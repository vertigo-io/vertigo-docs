# vertigo-datafactory

**vertigo-datafactory** is Vertigo's search and indexing module. It exposes two complementary mechanisms: distributed text search based on ElasticSearch and in-memory collections using Lucene. Configuration is done via Features (YAML or Java API) and parameters decorated with `@ParamValue`.

The module relies on two axes:

| Axis | Usage | Dependency |
|---|---|---|
| **ElasticSearch** | Automatic KeyConcept indexing via EventBus, 3 reindexing strategies, faceting + PEG DSL | `vertigo-elasticsearch-connector` (optional), ES 7.17.x |
| **Collections** | Pure-Java faceting + Lucene in-RAM filtering on DtList | Lucene 8.11.3 (bundled) |

```
KeyConcept / DtList (in-memory or persisted data)
        ↓
    SearchLoader / IndexDtListFunctionBuilder
        ↓
  ElasticSearch or Lucene RAM Index
        ↓
  SearchQuery / FacetedQuery (DSL, facets, geo, boost)
        ↓
  FacetedQueryResult<I,S> (list, counters, facets, clusters, highlights)
```

---

## Activation

```xml
<!-- Required: TaskManager, VTransactionManager, CacheManager -->
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-datastore</artifactId>
</dependency>

<!-- Main module -->
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-datafactory</artifactId>
</dependency>

<!-- Optional: ElasticSearch 7.17.x client -->
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-elasticsearch-connector</artifactId>
</dependency>
```

`CollectionsManager` is always active (`buildFeatures()`). Others require a YAML feature (see §For Experts). Parameters are configured via `@ParamValue`, for example:

- `@ParamValue("envIndexPrefix")` — index name prefix
- `@ParamValue("rowsPerQuery")` — batch load size
- `@ParamValue("connectorName")` — ElasticSearch connector name

---

## Architecture

The module organizes search around three concepts:

- **SearchIndexDefinition** (prefix `Idx`): links a KeyConcept to an Index DTO, a SearchLoader, and defines copyTo fields for multi-criteria search.
- **SearchLoader** (Component): custom loader to feed an index. Abstraction `AbstractSqlSearchLoader` enables loading from a SQL source.
- **SearchQuery** + **FacetedQuery**: query models accounting for PEG DSL, facets, geolocation, temporal boost, and facet clustering.

Central components:

| Component | Type | Role |
|---|---|---|
| `SearchManager` | Manager | Reindexing (3 strategies), ElasticSearch queries, metadata operations |
| `CollectionsManager` | Manager | Pure-Java faceting + Lucene in-RAM filtering |
| `SearchServicesPlugin` | Plugin | Contract for ElasticSearch engine |
| `IndexPlugin` | Plugin | Contract for Lucene in-RAM |
| `ListFilterBuilder<C>` | Builder | Builds a `ListFilter` from a Criteria object |
| `IndexDtListFunctionBuilder` | Builder | Chainable builder to sort/filter/page a DtList via Lucene |
| `FacetedQueryResultMerger` | — | Multi-index result merging |

---

## ElasticSearch

### SearchIndexDefinition

`SearchIndexDefinition` defines the link between a KeyConcept (business object), an indexing DTO, copyTo fields for multi-criteria search, and the SearchLoader identifier.

The constructor takes exactly 5 parameters:

| Parameter | Type | Description |
|---|---|---|
| `name` | `String` | Index definition identifier |
| `keyConceptDataDefinition` | `DataDefinition` | KeyConcept definition (e.g., DtTache) |
| `indexDataDefinition` | `DataDefinition` | Indexing DTO definition (e.g., DtTacheIndex) |
| `indexCopyFromFieldsMap` | `Map<DataField, List<DataField>>` | Source field to copyTo target mapping |
| `searchLoaderId` | `String` | Associated SearchLoader Component identifier |

`indexCopyFromFieldsMap` associates each source `DataField` to a list of target fields, enabling copying multiple fields into a single aggregation field for multi-criteria search. For example, copying `label`, `category`, and `status` into a single `globalSearch` field.

To define an index, create a subclass with the `Idx` prefix by convention:

```java
public final class IdxTache extends SearchIndexDefinition<IdxTache> {

    IdxTache(
            final String name,
            final DataDefinition keyConceptDataDefinition,
            final DataDefinition indexDataDefinition,
            final Map<DataField, List<DataField>> copyToMap,
            final String loaderId) {
        super(name, keyConceptDataDefinition, indexDataDefinition, copyToMap, loaderId);
    }
}
```

The first parameter is of type `DataDefinition`, not `DtDefinition`. The copyTo map is `Map<DataField, List<DataField>>`, not `Map<String, String>`.

### SQL SearchLoader

`SearchLoader` is a Component responsible for feeding an index from a data source. `AbstractSqlSearchLoader` provides the skeleton for batch SQL loading.

This Component is injected via `@Component` and receives `TaskManager` and `VTransactionManager` as parameters. Method `loadData(SearchChunk<K>)` is called with a batch of UIDs identified by a cursor, and returns a `List<SearchIndex<K, I>>` containing documents to index. `getSqlQueryFilter()` returns the additional SQL filter applied during incremental reindexing (Delta and Modified), typically a timestamp condition like `WHERE LAST_UPDATE > :lastDate`.

`AbstractSqlSearchLoader` is a parameterized abstract class whose constructor injects `TaskManager` and `VTransactionManager`. The implementing class must override:
- `loadData(SearchChunk<K>)` → `List<SearchIndex<K, I>>`: loads chunk SQL data and returns documents to index.
- `getSqlQueryFilter()` → `String`: returns SQL filter for incremental reindexing (e.g., `WHERE LAST_UPDATE > :lastDate`).

The loader is declared with `@Component`. `loadData` returns `List<SearchIndex<K, I>>`, not `void`. The parameter is `SearchChunk<K>` (UID type of the KeyConcept), not `SearchChunk<String>`.

### Reindexing

`SearchManager` exposes three reindexing strategies. Implementation (`SearchManagerImpl`) uses a mark-as-dirty mechanism, queues reindexing tasks with a 1-second delay, and listens to `StoreEvent` via EventBus to auto-detect modified KeyConcepts.

```java
// Full reindexing — rebuilds the entire index
Future<Long> futureCount = searchManager.reindexAll(idxTache);
Long nombreIndexe = futureCount.get();
```

```java
// Reindex modified documents — uses the timestamp field
Future<Long> futureModified = searchManager.reindexAllModified(idxTache);
```

```java
// Incremental reindexing — add/remove from last cursor
Future<Long> futureDelta = searchManager.reindexDelta(idxTache);
```

Each method returns a `Future<Long>` indicating the number of indexed documents upon completion.

### ElasticSearch Plugins

The module provides two implementations of `SearchServicesPlugin` contract:

| Plugin | Implementation | Notes |
|---|---|---|
| `RestHLClientESSearchServicesPlugin` | RestHighLevelClient 7.17.x | Production mode, recommended |
| `ClientESSearchServicesPlugin` | Transport legacy | Backward compatibility |

Internal connector classes include `ESStatement`, `ESSearchRequestBuilder`, `ESDocumentCodec` (compressed base64 serialization), and `IndexType`.

---

## Query DSL

The DSL engine uses a PEG parser to evaluate filter expressions. Seventeen rules compose the grammar (`Dsl*Rule`). Available operators:

| Rule | Syntax | Example |
|---|---|---|
| Term | `field:value` | `categorie:dev` |
| Range | `field:[min TO max]` | `budget:[1000 TO 50000]` |
| Multi-field | `(f1:value f2:value)` | `(categorie:dev statut:active)` |
| Boolean AND | `AND` | `categorie:dev AND statut:active` |
| Boolean OR | `OR` | `categorie:dev OR categorie:test` |
| Boolean positive | `+` | `+statut:active` |
| Boolean negative | `-` | `-statut:archived` |
| Geo distance | see `withGeoSearchQuery()` | via programmatic API |
| Geo bounding box | via programmatic API | — |
| Geo point | via programmatic API | — |

**Important**: functions `geo_distance()`, `decay()`, and `cluster()` are **not** available inline in DSL. They are configured via `SearchQueryBuilder` programmatic API.

### ListFilterBuilder

`ListFilterBuilder<C>` is the interface for building a `ListFilter` from a Criteria object. `DslListFilterBuilder` is the default implementation.

Construction follows a chainable instance builder pattern (no static `.build()` method). Typical approach:

1. Create a `DslListFilterBuilder` instance
2. Call `withListFilterQuery(String)` to define the DSL expression
3. Optionally call `withCriteria(C)` to associate a pre-filtering Criteria object
4. Call `build()` on the instance to get the final `ListFilter`

Two filter construction forms exist: a pure DSL expression (string parsed by the PEG engine) and field-based filtering, where you specify a target `DataField` and a value.

### SearchQuery and SearchQueryBuilder

`SearchQuery` is the model grouping search criteria: DSL filter, geolocation, security, recent boost, and facet clustering. `SearchQueryBuilder` is the associated fluent builder.

Confirmed `SearchQueryBuilder` methods:

| Method | Signature | Usage |
|---|---|---|
| `withGeoSearchQuery` | `(String)` | Adds geolocation criteria (distance, bbox, point) |
| `withDateBoost` | `(DataField, int, int)` | Boosts recent documents via temporal field and decay factors |
| `withFacetClustering` | `(FacetDefinition)` | Activates facet clustering on a given facet |
| `build` | `()` | Returns the built SearchQuery |

`withGeoSearchQuery` takes a geographic expression string, not a typed object. `withDateBoost` takes a `DataField` for the date field and two integers for boost and decay period parameters.

### Execution with SearchManager

`SearchManager.loadList()` takes the index definition, the built `SearchQuery`, and a `DtListState` for pagination, and returns a `FacetedQueryResult` containing the paginated list, total counter, and computed facets.

```java
// Loading a faceted list from an index
FacetedQueryResult result = searchManager.loadList(idxTache, query, dtListState);
```

---

## Result Models

### FacetedQueryResult<I,S>

Result of a faceted query, parameterized by index DTO type `<I>` and metadata type `<S>`.

```java
// Total matching document count
long total = result.getCount();

// Paginated document list
DtList<I> list = result.getDtList();

// Computed facets
List<Facet> facets = result.getFacets();
```

The result can also contain clusters and highlights depending on query configuration.

### Facet

```java
for (Facet facet : facets) {
    String facetName = facet.getDefinition().getName();
    // getFacetValues() returns Map<FacetValue, Long>
    Map<FacetValue, Long> values = facet.getFacetValues();
    for (Map.Entry<FacetValue, Long> entry : values.entrySet()) {
        FacetValue fv = entry.getKey();
        Long count = entry.getValue();
        System.out.println(fv.code() + " : " + count);
    }
}
```

`FacetValue` is a record with three fields:

| Field | Type | Description |
|---|---|---|
| `code` | String | Raw facet value |
| `listFilter` | ListFilter | Associated filter to refine search |
| `label` | LocaleMessageText | Display label (text access via `fv.label().getDisplay()`) |

No `getKey()` or `getCount()` method exists on `FacetValue`. Code is accessed via `fv.code()`, count via the Map value.

### SearchIndex and SearchChunk

- `SearchIndex<K,I>`: wraps a `<K>` UID and a `<I>` indexing DTO for ElasticSearch indexing.
- `SearchChunk<K>`: batch of `<K>` UIDs with cursor, used by SearchLoaders for batch loading.

### SelectedFacetValues

`SelectedFacetValues` provides user-selected facet values. The method to retrieve values is `getFacetValues(String facetName)`, not `getSelectedFacetValues()`.

```java
// Get selected values for a given facet
List<FacetValue> values = selectedFacetValues.getFacetValues("facetCategory");
```

### FacetedQuery

`FacetedQuery` is an immutable object with two parameters: definition and selected facet values.

```
FacetedQuery(FacetedQueryDefinition definition, SelectedFacetValues selectedValues)
```

### FacetDefinition

`FacetDefinition` is **final** (non-subclassable). Facets are created exclusively via `FacetFactory` fluent API:

| Factory | Type | Parameters |
|---|---|---|
| `FacetFactory.createFacetDefinitionByTerm()` | Term | `name`, `dtField`, `label`, `multiSelectable`, `order` |
| `FacetFactory.createFacetDefinitionByRange()` | Range | `name`, `dtField`, `label`, `facetValues`, `multiSelectable`, `order` |
| `FacetFactory.createCustomFacetDefinition()` | Custom | `name`, `dtField`, `label`, `customParams` (Map&lt;String, String&gt;), `order` |

Declarative construction uses `FacetTermDefinitionSupplier`, `FacetRangeDefinitionSupplier`, and `FacetCustomDefinitionSupplier`. Facet type is determined by the called factory, not by `FacetType` enum (does not exist).

Example for Project Management domain:
- `FctTacheCategorie`: term facet on field category — filter by task type (development, test, documentation)
- `FctTacheBudget`: range facet on field budget — ranges 0-5000, 5000-20000, 20000-50000, 50000+

The `label` argument expected by factory methods is `LocaleMessageText` (not raw String). Enum `FacetOrder` exposes three lowercase values: `alpha`, `count`, `definition`.

### FacetedQueryDefinition

`FacetedQueryDefinition` (prefix `Qry`) gathers facets, DSL, and the definition associated with the KeyConcept. Constructor takes six parameters: name, list of `FacetDefinition`, `SmartTypeDefinition`, `ListFilterBuilder` class, default DSL query, and geo field.

**Note**: no method `DtClassKey.of()` exists in the module.

---

## In-Memory Collections

In-memory collections use Lucene to index `DtList` directly in RAM. Typical usage is filtering and faceting of already-loaded data lists.

### CollectionsManager

`CollectionsManager` is the central component. Its main method is:

```
facetList(DtList, FacetedQuery, Optional<FacetDefinition>) → FacetedQueryResult
```

Lucene filtering is delegated to `IndexPlugin` (`LuceneIndexPlugin`). Internal implementations use `RamLuceneIndex`, `RamLuceneQueryFactory`, and `DefaultAnalyzer`.

To use `CollectionsManager`, retrieve the instance via `ApplicationManager`, build `FacetedQuery` from a `FacetedQueryDefinition` and `SelectedFacetValues`, then call `facetList` with the target `DtList`. `FacetedQuery` is built with the definition (instance of `QryTache`) and selected facet values, not with a class.

```java
CollectionsManager collectionsManager = ApplicationManager.get()
    .getModules()
    .getInstance(CollectionsManager.class);

FacetedQuery facetedQuery = new FacetedQuery(
    qryTache,                // FacetedQueryDefinition instance
    selectedFacetValues      // selected values
);

FacetedQueryResult result =
    collectionsManager.facetList(taskList, facetedQuery, Optional.empty());
```

### IndexDtListFunctionBuilder

`IndexDtListFunctionBuilder` is a utility to filter and facet a `DtList` via Lucene. A Lucene index is created by calling the creation method with the list and faceted query definition, then executing the operation to get the result.

The method rebuilds the Lucene index on each call against provided data; usage is suited for moderately-sized lists already loaded in memory.

---

## Comparison: ElasticSearch vs Collections

| Criterion | ElasticSearch | Lucene Collections |
|---|---|---|
| Support | Remote server, cluster, persistence | RAM, Java process, ephemeral |
| Volume | Millions of documents | Few thousands DTOs |
| Latency | Network (ms) | Memory (µs) |
| Full-text | ES Analyzer, tokenizer, synonyms | Basic Lucene DefaultAnalyzer |
| Facets | ES Aggregates | Pure-Java in-process counting |
| Reindexing | Full / Modified / Delta via SearchManager | Index rebuilt on each call |
| Auto-indexing | EventBus StoreEvent on KeyConcept | Manual, on provided DtList |
| Dependency | `vertigo-elasticsearch-connector`, ES 7.17.x | Lucene 8.11.3 (bundled) |
| Typical usage | Catalog, application search, shared index | UI filters, data tables, reports |

---

## Complete Example: datafactory flow A to Z

Full flow walk-through in the Project Management domain, from index definition to faceted query execution, without uncertain API snippets.

### Step 1 — DTO Declaration

The project first defines business data structures. `DtTache` represents the business object (the KeyConcept) with its fields: label, category, status, budget, creationDate, responsible, etc. `DtTacheIndex` is the indexing DTO, containing only fields useful for search and faceting. Both DTOs are declared via standard Vertigo mechanisms (`DataDefinition`).

### Step 2 — Index Definition

Create `IdxTache`, subclass of `SearchIndexDefinition`, linking `DtTache` (KeyConcept) to `DtTacheIndex` (indexing DTO). Constructor receives 5 parameters: index name, KeyConcept `DataDefinition`, indexing DTO `DataDefinition`, `Map<DataField, List<DataField>>` for copyTo fields, and SearchLoader identifier.

The copyTo map copies fields `label`, `category`, and `status` into a single `globalSearch` field, enabling multi-criteria search on one aggregated field.

### Step 3 — Loader Implementation

Loader `TacheSearchLoader` extends `AbstractSqlSearchLoader` and is declared as `@Component`. It injects `TaskManager` and `VTransactionManager` to access relational data.

`loadData(SearchChunk<K>)` receives a batch of UIDs (identified by a cursor) and returns `List<SearchIndex<K, I>>`: for each chunk UID, load task data, map to `DtTacheIndex`, and return the list of documents to index.

`getSqlQueryFilter()` returns the dynamic SQL filter used for incremental reindexing. For example, `WHERE LAST_UPDATE > :lastDate` only reindexes tasks modified since the last reindex.

### Step 4 — Facet Definition

Facets are created via static factory methods of `FacetDefinition`:
- `FctTacheCategorie`: `createFacetDefinitionByTerm()` on field category, filtering by task type (development, test, documentation, etc.)
- `FctTacheBudget`: `createFacetDefinitionByRange()` on field budget, with predefined ranges (0-5000, 5000-20000, 20000-50000, 50000+)
- `FctTacheStatut`: `createFacetDefinitionByTerm()` on field status (in progress, completed, pending, canceled)

No `FacetType` enum is used. Facet type is determined by constructor parameters.

### Step 5 — Faceted Query Definition

`QryTache`, subclass of `FacetedQueryDefinition`, groups the index definition, available facets (FctTacheCategorie, FctTacheBudget, FctTacheStatut), and associated search configurations.

### Step 6 — Initial Indexing

On deployment, a full reindex is triggered via `searchManager.reindexAll(idxTache)`. Method returns `Future<Long>` indicating the indexed document count. Loader loads tasks in batches from the relational database and indexes them in ElasticSearch.

In production, reindexing is automatic: `SearchManagerImpl` listens to `StoreEvent` on EventBus to detect task modifications and queues a `ReindexTask` with a 1-second delay to avoid multiple calls.

### Step 7 — Search Query Execution

To filter tasks of category "dev" with budget between 5000 and 50000:

1. Build DSL filter via `DslListFilterBuilder`: expression `"categorie:dev AND budget:[5000 TO 50000]"`, optionally associated with a Criteria.
2. Build `SearchQuery` via `SearchQueryBuilder`: apply filter, add temporal boost on field `dateCreation` via `withDateBoost(DataField, int, int)`, activate faceting on category via `withFacetClustering(facetDefinitionInstance)`.
3. Execute via `SearchManager.loadList()`: pass index, query, and `DtListState` for pagination. Result is `FacetedQueryResult` with task list, total counter, and computed facets.
4. Read facets: for each `Facet`, iterate `getFacetValues()` returning `Map<FacetValue, Long>`. Each `FacetValue` exposes `code()`, `label()`, and `listFilter`.

### Step 8 — In-Memory Faceting on DtList

When data is already loaded in memory (e.g., a filtered view of up to 2000 tasks):

1. Retrieve `CollectionsManager` via `ApplicationManager`.
2. Build `FacetedQuery` with `QryTache` instance (FacetedQueryDefinition) and selected facet values via `SelectedFacetValues.getFacetValues(String)`.
3. Call `collectionsManager.facetList(taskList, facetedQuery, Optional.empty())` returning `FacetedQueryResult` with filtered list, counters, and facets computed by Lucene in RAM.

Lucene index is rebuilt on each call against the provided `DtList`, so this axis is suited for moderate datasets and interactive UI filtering contexts.

---

## Notes

- **SearchIndexDefinition constructor**: takes exactly 5 parameters: name, keyConceptDataDefinition (`DataDefinition`), indexDataDefinition (`DataDefinition`), indexCopyFromFieldsMap (`Map<DataField, List<DataField>>`), searchLoaderId. No fluent builder `SearchIndexDefinitionBuilder` exists. Do not confuse `DataDefinition` with `DtDefinition`; do not use `Map<String, String>` for the copyTo map.
- **Automatic reindexing**: `SearchManagerImpl` listens to `StoreEvent` on EventBus to mark KeyConcepts as dirty, then queues a `ReindexTask` with 1-second delay to avoid multiple calls.
- **Delta reindexing**: `getSqlQueryFilter()` in SearchLoader must return a SQL filter with a timestamp parameter. Deleted documents are detected by KeyConcept disappearance.
- **Ranges in DSL**: `[min TO max]` includes bounds. Use `*` for open infinite bounds: `[0 TO *]`.
- **Geo**: Geographic expressions are not inline in DSL. Configure via `SearchQueryBuilder.withGeoSearchQuery(String)`.
- **Boost and clustering**: `decay()` and `cluster()` are not inline. Use `withDateBoost(DataField, int, int)` and `withFacetClustering(FacetDefinition)` on the builder.
- **FacetValue**: record `(code, listFilter, label)`. Access via `fv.code()`, `fv.listFilter()`, `fv.label()`. No `getKey()` or `getCount()` methods. Count is the value of `Map<FacetValue, Long>` returned by `facet.getFacetValues()`.
- **SelectedFacetValues**: use `getFacetValues(String facetName)`, not `getSelectedFacetValues()`.
- **FacetedQuery immutable**: built with `(FacetedQueryDefinition, SelectedFacetValues)`. No `setFilter()` or `execute()` on the object.
- **Collection vs Index**: `collectionsManager.facetList()` recreates the Lucene index on each call against the provided `DtList`. For intensive usage, minimize repeated calls on the same list.
- **Range facet size**: Ranges are defined statically in `FacetDefinition`. A document outside all ranges appears in no range facet. Include a catch-all range at the end.
- **SearchLoader loadData**: `loadData(SearchChunk<K>)` returns `List<SearchIndex<K, I>>`, not `void`. Do not use `SearchChunk<String>`.
- **ListFilterBuilder**: no static `.build()` method. Use instance builder pattern: `withListFilterQuery()` → `withCriteria()` → `build()`.
- **ESDocumentCodec**: handles ElasticSearch document encoding/decoding. Serialization goes through base64 and possibly compression. This impacts direct document readability in the ES interface.

## For Experts

### Managers
| Manager | Role | Activated by |
|---|---|---|
| `CollectionsManager` | Pure-Java faceting + Lucene in-RAM filtering | Always (`buildFeatures`) |
| `SearchManager` | Reindexing (3 strategies), ElasticSearch queries | `search` |

### Features (@Feature)
| Flag | Components |
|---|---|
| `search` | `SearchManager` + `SearchManagerImpl` |
| `search.elasticsearch.client` | `ClientESSearchServicesPlugin` (Transport legacy) |
| `search.elasticsearch.restHL` | `RestHLClientESSearchServicesPlugin` (RestHighLevelClient 7.17.x) |
| `collections.luceneIndex` | `LuceneIndexPlugin` |

### Fluent API (Suppliers)
| Supplier | Role |
|---|---|
| `SearchIndexDefinitionSupplier` | Fluent `SearchIndexDefinition` build |
| `FacetedQueryDefinitionSupplier` | Fluent `FacetedQueryDefinition` build |
| `FacetTermDefinitionSupplier` | Fluent term `FacetDefinition` build |
| `FacetRangeDefinitionSupplier` | Fluent range `FacetDefinition` build |
| `FacetCustomDefinitionSupplier` | Fluent custom `FacetDefinition` build |

### Utils & Pattern Filters
| Class | Role |
|---|---|
| `FacetFactory` | Facet factory (term/range/custom) and clusters |
| `IndexFilterFunction<D>` | Lucene indexed filtering (keywords, sort, pagination) |
| `DtListPatternFilter<D>` | Runtime pattern: `FIELD:VALUE` or `FIELD:[MIN TO MAX]` |
| `DtListPatternFilterUtil` | Regex parser: BasicType conversion, ranges, terms |

### Plugins
| Plugin | Role | Feature |
|---|---|---|
| `LuceneIndexPlugin` | In-RAM Lucene index for in-memory faceting | `collections.luceneIndex` |
| `ClientESSearchServicesPlugin` | Transport legacy ElasticSearch client | `search.elasticsearch.client` |
| `RestHLClientESSearchServicesPlugin` | REST High Level ElasticSearch client 7.17.x | `search.elasticsearch.restHL` |

### YAML Configuration
```yaml
modules:
    io.vertigo.datafactory.DataFactoryFeatures:
        features:
            - search:
            - collections.luceneIndex:
        featuresConfig:
            - search.elasticsearch.restHL:
                  envIndexPrefix: "prod_"
                  connectorName: "main"
```
