# vertigo-datafactory

**vertigo-datafactory** est le module de recherche et d'indexation de la plateforme Vertigo. Il expose deux mécanismes complémentaires : une recherche textuelle distribuée basée sur ElasticSearch et des collections in-mémoire utilisant Lucene. La configuration se fait via les Features (YAML ou API Java) et les paramètres décorés par `@ParamValue`.

Le module repose sur deux axes :

| Axe | Usage | Dépendance |
|---|---|---|
| **ElasticSearch** | Indexation automatique des KeyConcepts via EventBus, reindexation 3 stratégies, facettage + DSL PEG | `vertigo-elasticsearch-connector` (optionnel), ES 7.17.x |
| **Collections** | Facettage pur-Java + filtrage Lucene in-RAM sur DtList | Lucene 8.11.3 (bundlé) |

```
KeyConcept / DtList (données en mémoire ou persistées)
        ↓
    SearchLoader / IndexDtListFunctionBuilder
        ↓
  Index ElasticSearch ou Lucene RAM
        ↓
  SearchQuery / FacetedQuery (DSL, facettes, géo, boost)
        ↓
  FacetedQueryResult<I,S> (liste, compteurs, facettes, clusters, highlights)
```

---

## Activation

```xml
<!-- Obligatoire : TaskManager, VTransactionManager, CacheManager -->
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-datastore</artifactId>
</dependency>

<!-- Module principal -->
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-datafactory</artifactId>
</dependency>

<!-- Optionnel : client ElasticSearch 7.17.x -->
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-elasticsearch-connector</artifactId>
</dependency>
```

Le composant `CollectionsManager` est toujours actif (`buildFeatures()`). Les autres nécessitent une feature YAML (cf. §Pour les experts). Les paramètres se configurent via `@ParamValue`, par exemple :

- `@ParamValue("envIndexPrefix")` — préfixe des noms d'index
- `@ParamValue("rowsPerQuery")` — taille des lots de chargement
- `@ParamValue("connectorName")` — nom du connecteur ElasticSearch

---

## Architecture

Le module articule la recherche autour de trois concepts :

- **SearchIndexDefinition** (prefixe `Idx`) : lie un KeyConcept à un Index DTO, à un SearchLoader, et définit les champs copyTo pour la recherche multicritères.
- **SearchLoader** (Component) : loader personnalisé pour alimenter un index. L'abstraction `AbstractSqlSearchLoader` permet le chargement depuis une source SQL.
- **SearchQuery** + **FacetedQuery** : modèles de requête prenant en compte le DSL PEG, les facettes, la géolocalisation, le boost temporel et le facet clustering.

Les composants centraux sont :

| Composant | Type | Rôle |
|---|---|---|
| `SearchManager` | Manager | Reindexation (3 stratégies), requêtes ElasticSearch, opérations sur les metadata |
| `CollectionsManager` | Manager | Facettage pur-Java + filtrage Lucene in-RAM |
| `SearchServicesPlugin` | Plugin | Contract pour le moteur ElasticSearch |
| `IndexPlugin` | Plugin | Contract pour Lucene in-RAM |
| `ListFilterBuilder<C>` | Builder | Construit un `ListFilter` depuis un objet Criteria |
| `IndexDtListFunctionBuilder` | Builder | Builder chaînable pour trier/filtrer/pager une DtList via Lucene |
| `FacetedQueryResultMerger` | — | Fusion des résultats multi-index |

---

## ElasticSearch

### SearchIndexDefinition

La classe `SearchIndexDefinition` définit le lien entre un KeyConcept (objet métier), un DTO d'indexation, les champs copyTo pour la recherche multicritères, et l'identifiant du SearchLoader.

Le constructeur prend exactement 5 paramètres :

| Paramètre | Type | Description |
|---|---|---|
| `name` | `String` | Identifiant de la définition d'index |
| `keyConceptDataDefinition` | `DataDefinition` | Définition du KeyConcept métier (par exemple DtTache) |
| `indexDataDefinition` | `DataDefinition` | Définition du DTO d'indexation (par exemple DtTacheIndex) |
| `indexCopyFromFieldsMap` | `Map<DataField, List<DataField>>` | Mappage des champs source vers les champs copyTo cibles |
| `searchLoaderId` | `String` | Identifiant du Component SearchLoader associé |

Le paramètre `indexCopyFromFieldsMap` associe chaque champ source (`DataField`) à une liste de champs cibles, permettant de copier plusieurs champs dans un seul champ d'agrégation pour la recherche multicritères. Par exemple, copier `libelle`, `categorie` et `statut` vers un unique champ `rechercheGlobale`.

Pour définir un index, on crée une sous-classe avec le préfixe `Idx` par convention :

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

Le premier paramètre est de type `DataDefinition`, non `DtDefinition`. La map copyTo est de type `Map<DataField, List<DataField>>`, non `Map<String, String>`.

### SearchLoader SQL

Le `SearchLoader` est un Component chargé d'alimenter un index depuis une source de données. L'abstraction `AbstractSqlSearchLoader` fournit le squelette pour un chargement SQL batch.

Ce Component s'injecte via `@Component` et reçoit en paramètres `TaskManager` et `VTransactionManager`. La méthode `loadData(SearchChunk<K>)` est appelée avec un lot d'UIDs identifié par un curseur, et retourne une `List<SearchIndex<K, I>>` contenant les documents à indexer. La méthode `getSqlQueryFilter()` retourne le filtre SQL additionnel appliqué lors des reindexations incrémentales (Delta et Modified), typiquement une condition sur un champ timestamp du style `WHERE LAST_UPDATE > :lastDate`.

`AbstractSqlSearchLoader` est une classe abstraite paramétrée dont le constructeur injecte `TaskManager` et `VTransactionManager`. La classe implémentante doit surcharger :
- `loadData(SearchChunk<K>)` → `List<SearchIndex<K, I>>` : charge les données du chunk SQL et retourne les documents à indexer.
- `getSqlQueryFilter()` → `String` : retourne le filtre SQL pour les reindexations incrémentales (ex. `WHERE LAST_UPDATE > :lastDate`).

Le loader se déclare avec `@Component`. La méthode `loadData` retourne `List<SearchIndex<K, I>>`, non `void`. Le paramètre est `SearchChunk<K>` (type UID du KeyConcept), non `SearchChunk<String>`.

### Reindexation

`SearchManager` expose trois stratégies de reindexation. L'implémentation (`SearchManagerImpl`) utilise un mécanisme mark-as-dirty, file les tâches de reindexation avec un délai de 1 seconde, et écoute les `StoreEvent` via l'EventBus pour détecter automatiquement les KeyConcepts modifiés.

```java
// Reindexation complète — reconstruit l'intégralité de l'index
Future<Long> futureCount = searchManager.reindexAll(idxTache);
Long nombreIndexe = futureCount.get();
```

```java
// Reindexation des documents modifiés — utilise le champ timestamp
Future<Long> futureModified = searchManager.reindexAllModified(idxTache);
```

```java
// Reindexation incrémentale — ajoute/supprime depuis le dernier curseur
Future<Long> futureDelta = searchManager.reindexDelta(idxTache);
```

Chaque méthode retourne un `Future<Long>` indiquant le nombre de documents indexés à l'issue de l'opération.

### Plugins ElasticSearch

Le module fournit deux implémentations du contract `SearchServicesPlugin` :

| Plugin | Implémentation | Notes |
|---|---|---|
| `RestHLClientESSearchServicesPlugin` | RestHighLevelClient 7.17.x | Mode production, recommandé |
| `ClientESSearchServicesPlugin` | Transport legacy | Compatibilité ascendante |

Les classes internes du connecteur incluent `ESStatement`, `ESSearchRequestBuilder`, `ESDocumentCodec` (sérialisation base64 compressée) et `IndexType`.

---

## DSL de requête

Le moteur DSL utilise un parser PEG pour évaluer les expressions de filtrage. Dix-sept règles composent la grammaire (`Dsl*Rule`). Les opérateurs disponibles :

| Règle | Syntaxe | Exemple |
|---|---|---|
| Terme | `field:value` | `categorie:dev` |
| Range | `field:[min TO max]` | `budget:[1000 TO 50000]` |
| Multi-champs | `(f1:value f2:value)` | `(categorie:dev statut:actif)` |
| Booléen AND | `AND` | `categorie:dev AND statut:actif` |
| Booléen OR | `OR` | `categorie:dev OR categorie:test` |
| Booléen positif | `+` | `+statut:actif` |
| Booléen negatif | `-` | `-statut:archive` |
| Géo distance | voir `withGeoSearchQuery()` | via API programmatique |
| Géo bounding box | via API programmatique | — |
| Géo point | via API programmatique | — |

**Important** : les fonctions `geo_distance()`, `decay()` et `cluster()` ne sont **pas** disponibles inline dans le DSL. Elles se configurent via l'API programmatique de `SearchQueryBuilder`.

### ListFilterBuilder

`ListFilterBuilder<C>` est l'interface pour construire un `ListFilter` depuis un objet Criteria. `DslListFilterBuilder` est l'implémentation par défaut.

La construction suit un pattern de builder instance chaînable (pas de méthode statique `.build()`). La démarche typique :

1. Créer une instance de `DslListFilterBuilder`
2. Appeler `withListFilterQuery(String)` pour définir l'expression DSL
3. Appeler `withCriteria(C)` de manière optionnelle pour associer un objet Criteria de pré-filtrage
4. Appeler `build()` sur l'instance pour obtenir le `ListFilter` final

Il existe deux formes de construction de filtre : une expression DSL pure (chaîne de caractères parsée par le moteur PEG) et un filtrage par field, où l'on spécifie un `DataField` cible et une valeur.

### SearchQuery et SearchQueryBuilder

`SearchQuery` est le modèle regroupant les critères de recherche : DSL filter, géolocalisation, sécurité, boost récent, et facet clustering. `SearchQueryBuilder` est le builder fluide associé.

Méthodes confirmées de `SearchQueryBuilder` :

| Méthode | Signature | Usage |
|---|---|---|
| `withGeoSearchQuery` | `(String)` | Ajoute un critère géolocalisé (distance, bbox, point) |
| `withDateBoost` | `(DataField, int, int)` | Booste les documents récents via le champ temporel et les facteurs de decay |
| `withFacetClustering` | `(FacetDefinition)` | Active le facet clustering sur une facette donnée |
| `build` | `()` | Retourne le SearchQuery construit |

La méthode `withGeoSearchQuery` prend une chaîne d'expression géographique, non un objet typé. La méthode `withDateBoost` prend un `DataField` pour le champ date et deux entiers pour les paramètres de boost et de période de decay.

### Exécution avec SearchManager

La méthode `SearchManager.loadList()` prend en paramètres la définition d'index, le `SearchQuery` construit, et un `DtListState` pour la pagination, et retourne un `FacetedQueryResult` contenant la liste paginée, le compteur total, et les facettes calculées.

```java
// Chargement d'une liste facettée depuis un index
FacetedQueryResult result = searchManager.loadList(idxTache, query, dtListState);
```

---

## Modèles de résultat

### FacetedQueryResult<I,S>

Résultat d'une requête facettée, paramétrée par le type d'index DTO `<I>` et le type de metadata `<S>`.

```java
// Compteur total des Documents correspondants
long total = result.getCount();

// Liste des Documents paginée
DtList<I> liste = result.getDtList();

// Facettes calculées
List<Facet> facettes = result.getFacets();
```

Le résultat peut également contenir des clusters et des highlights selon la configuration de la requête.

### Facet

```java
for (Facet facet : facettes) {
    String nomFacette = facet.getDefinition().getName();
    // getFacetValues() retourne Map<FacetValue, Long>
    Map<FacetValue, Long> valeurs = facet.getFacetValues();
    for (Map.Entry<FacetValue, Long> entry : valeurs.entrySet()) {
        FacetValue fv = entry.getKey();
        Long count = entry.getValue();
        System.out.println(fv.code() + " : " + count);
    }
}
```

`FacetValue` est un record à trois champs :

| Champ | Type | Description |
|---|---|---|
| `code` | String | Valeur brute de la facette |
| `listFilter` | ListFilter | Filtre associé pour raffiner la recherche |
| `label` | LocaleMessageText | Libellé affiché (accès texte via `fv.label().getDisplay()`) |

Aucune méthode `getKey()` ou `getCount()` n'existe sur `FacetValue`. Le code s'accède via `fv.code()`, le count via la valeur de la Map.

### SearchIndex et SearchChunk

- `SearchIndex<K,I>` : enveloppe un UID de type `<K>` et un DTO d'indexation de type `<I>` pour l'indexation ElasticSearch.
- `SearchChunk<K>` : lot d'UIDs de type `<K>` avec curseur, utilisé par les SearchLoaders pour le chargement par batch.

### SelectedFacetValues

`SelectedFacetValues` permet de connaître les valeurs de facette sélectionnées par l'utilisateur. La méthode pour récupérer les valeurs est `getFacetValues(String facetName)`, non `getSelectedFacetValues()`.

```java
// Récupérer les valeurs sélectionnées pour une facette donnée
List<FacetValue> values = selectedFacetValues.getFacetValues("facetCategorie");
```

### FacetedQuery

`FacetedQuery` est un objet immutable à deux paramètres : la définition et les valeurs de facette sélectionnées.

```
FacetedQuery(FacetedQueryDefinition definition, SelectedFacetValues selectedValues)
```

### FacetDefinition

La classe `FacetDefinition` est **finale** (non subclassable). Les facettes se créent exclusivement via l'API fluide `FacetFactory` :

| Factory | Type | Paramètres |
|---|---|---|
| `FacetFactory.createFacetDefinitionByTerm()` | Terme | `name`, `dtField`, `label`, `multiSelectable`, `order` |
| `FacetFactory.createFacetDefinitionByRange()` | Range | `name`, `dtField`, `label`, `facetValues`, `multiSelectable`, `order` |
| `FacetFactory.createCustomFacetDefinition()` | Custom | `name`, `dtField`, `label`, `customParams` (Map&lt;String, String&gt;), `order` |

La construction déclarative utilise `FacetTermDefinitionSupplier`, `FacetRangeDefinitionSupplier` et `FacetCustomDefinitionSupplier`. Le type de facette est déterminé par la factory appelée, pas par une énumération `FacetType` (n'existe pas).

Exemple narratif pour le domaine Gestion de Projet :
- `FctTacheCategorie` : facette terme sur le champ categorie — filtre par type de tâche (développement, test, documentation)
- `FctTacheBudget` : facette range sur le champ budget — intervalles 0-5000, 5000-20000, 20000-50000, 50000+

L'argument `label` attendu par les factory methods est de type `LocaleMessageText` (pas String brut). L'enum `FacetOrder` expose trois valeurs en minuscules : `alpha`, `count`, `definition`.

### FacetedQueryDefinition

La `FacetedQueryDefinition` (préfixe `Qry`) rassemble les facettes, le DSL, et la définition associée au KeyConcept. Le constructeur prend six paramètres : nom, liste des `FacetDefinition`, `SmartTypeDefinition`, classe de `ListFilterBuilder`, requête DSL par défaut, et champ géo.

**Attention** : aucune méthode `DtClassKey.of()` n'existe dans le module.

---

## Collections in-mémoire

Les collections in-mémoire utilisent Lucene pour indexer des `DtList` directement en RAM. L'usage typique est le filtrage et le facettage de listes de données déjà chargées.

### CollectionsManager

`CollectionsManager` est le composant central. Sa méthode principale est :

```
facetList(DtList, FacetedQuery, Optional<FacetDefinition>) → FacetedQueryResult
```

Le filtrage Lucene est délégué à `IndexPlugin` (`LuceneIndexPlugin`). Les implémentations internes utilisent `RamLuceneIndex`, `RamLuceneQueryFactory` et `DefaultAnalyzer`.

Pour utiliser `CollectionsManager`, on récupère l'instance via `ApplicationManager`, on construit la `FacetedQuery` à partir d'une `FacetedQueryDefinition` et d'un objet `SelectedFacetValues`, puis on appelle `facetList` avec la `DtList` cible. La `FacetedQuery` est construite avec la définition (instance de `QryTache`) et les valeurs de facette sélectionnées, non avec une classe.

```java
CollectionsManager collectionsManager = ApplicationManager.get()
    .getModules()
    .getInstance(CollectionsManager.class);

FacetedQuery facetedQuery = new FacetedQuery(
    qryTache,                // instance de FacetedQueryDefinition
    selectedFacetValues      // valeurs sélectionnées
);

FacetedQueryResult result =
    collectionsManager.facetList(listeTaches, facetedQuery, Optional.empty());
```

### IndexDtListFunctionBuilder

`IndexDtListFunctionBuilder` est un utilitaire permettant de filtrer et facetter une `DtList` via Lucene. La création d'un index Lucene se fait en appelant la méthode de création avec la liste et la définition de requête facettée, puis en exécutant l'opération pour obtenir le résultat.

La méthode reconstruit l'index Lucene à chaque appel sur les données fournies, l'usage est adapté pour des listes de taille modérée déjà chargées en mémoire.

---

## Comparaison : ElasticSearch vs Collections

| Critère | ElasticSearch | Collections Lucene |
|---|---|---|
| Support | Serveur distant, cluster, persistance | RAM, process Java, éphémère |
| Volume | Millions de documents | Quelques milliers de DTO |
| Latence | Réseau (ms) | Mémoire (µs) |
| Plein texte | Analyzer ES, tokenizer, synonymes | DefaultAnalyzer Lucene basique |
| Facettes | Agrégats ES | Comptage pur-Java in-process |
| Reindexation | Full / Modified / Delta via SearchManager | Index rebuilt à chaque appel |
| Indexation auto | EventBus StoreEvent sur KeyConcept | Manuel, sur DtList fournie |
| Dépendance | `vertigo-elasticsearch-connector`, ES 7.17.x | Lucene 8.11.3 (bundlé) |
| Usage typique | Catalogue, recherche applicative, index partagé | Filtres UI, tables de données, rapports |

---

## Exemple complet : flux datafactory de A à Z

Parcours du flux complet dans le domaine de la gestion de projet, de la définition de l'index à l'exécution d'une requête facettée, sans snippets APIs incertains.

### Étape 1 — Déclaration des DTO

Le projet définit d'abord les structures de données métier. `DtTache` représente l'objet métier (le KeyConcept) avec ses fields : libelle, categorie, statut, budget, dateCreation, responsable, etc. `DtTacheIndex` est le DTO d'indexation, contenant uniquement les champs utiles pour la recherche et le facettage. Ces deux DTO sont déclarés via les mécanismes standards Vertigo (`DataDefinition`).

### Étape 2 — Définition de l'index

On crée `IdxTache`, sous-classe de `SearchIndexDefinition`, qui lie `DtTache` (KeyConcept) à `DtTacheIndex` (DTO d'indexation). Le constructeur reçoit 5 paramètres : le nom de l'index, la `DataDefinition` du KeyConcept, la `DataDefinition` du DTO d'indexation, une `Map<DataField, List<DataField>>` pour les champs copyTo, et l'identifiant du SearchLoader.

La map copyTo copie les champs `libelle`, `categorie` et `statut` vers un champ unique `rechercheGlobale`, permettant une recherche multicritères sur un seul champ agrégé.

### Étape 3 — Implémentation du loader

Le loader `TacheSearchLoader` étend `AbstractSqlSearchLoader` et est déclaré comme `@Component`. Il injecte `TaskManager` et `VTransactionManager` pour accéder aux données relationnelles.

La méthode `loadData(SearchChunk<K>)` reçoit un lot d'UIDs (identifiés par un curseur) et retourne `List<SearchIndex<K, I>>` : pour chaque UID du chunk, on charge les données de la tâche, on mappe vers `DtTacheIndex`, et on retourne la liste des documents à indexer.

La méthode `getSqlQueryFilter()` retourne le filtre SQL dynamique utilisé pour les reindexations incrémentales. Par exemple, une clause `WHERE LAST_UPDATE > :lastDate` permet de ne réindexer que les tâches modifiées depuis la dernière reindexation.

### Étape 4 — Définition des facettes

Les facettes sont créées via les méthodes factory statiques de `FacetDefinition` :
- `FctTacheCategorie` : `createFacetDefinitionByTerm()` sur le champ categorie, permettant de filtrer par type de tâche (développement, test, documentation, etc.)
- `FctTacheBudget` : `createFacetDefinitionByRange()` sur le champ budget, avec des plages prédéfinies (0-5000, 5000-20000, 20000-50000, 50000+)
- `FctTacheStatut` : `createFacetDefinitionByTerm()` sur le champ statut (en cours, terminé, en attente, annulé)

Aucune énumération `FacetType` n'est utilisée. Le type de facette est déterminé par les paramètres du constructeur.

### Étape 5 — Définition de la requête facettée

`QryTache`, sous-classe de `FacetedQueryDefinition`, regroupe la définition de l'index, les facettes disponibles (FctTacheCategorie, FctTacheBudget, FctTacheStatut), et les configurations de recherche associées.

### Étape 6 — Indexation initiale

Lors du déploiement, une reindexation complète est lancée via `searchManager.reindexAll(idxTache)`. La méthode retourne un `Future<Long>` indiquant le nombre de documents indexés. Le loader charge les tâches par batch depuis la base relationnelle et les indexe dans ElasticSearch.

En production, la reindexation se fait automatiquement : `SearchManagerImpl` écoute les `StoreEvent` sur l'EventBus pour détecter les modifications de tâches, et file un `ReindexTask` avec un délai de 1 seconde pour éviter les appels multiples.

### Étape 7 — Exécution d'une requête de recherche

Pour filtrer les tâches de catégorie "dev" avec un budget entre 5000 et 50000 :

1. Construction du filtre DSL via `DslListFilterBuilder` : expression `"categorie:dev AND budget:[5000 TO 50000]"`, associée à un Criteria optionnel.
2. Construction de la `SearchQuery` via `SearchQueryBuilder` : application du filtre, ajout d'un boost temporel sur le champ `dateCreation` via `withDateBoost(DataField, int, int)`, activation du faceting sur la catégorie via `withFacetClustering(facetDefinitionInstance)`.
3. Exécution via `SearchManager.loadList()` : passage de l'index, de la requête, et d'un `DtListState` pour la pagination. Le résultat est un `FacetedQueryResult` contenant la liste des tâches, le compteur total, et les facettes calculées.
4. Lecture des facettes : pour chaque `Facet`, on parcourt `getFacetValues()` qui retourne `Map<FacetValue, Long>`. Chaque `FacetValue` expose `code()`, `label()`, et `listFilter`.

### Étape 8 — Facettage in-mémoire sur DtList

Quand les données sont déjà chargées en mémoire (par exemple une vue filtrée de 2000 tâches au plus) :

1. Récupération de `CollectionsManager` via `ApplicationManager`.
2. Construction de `FacetedQuery` avec l'instance de `QryTache` (FacetedQueryDefinition) et les valeurs de facette sélectionnées via `SelectedFacetValues.getFacetValues(String)`.
3. Appel de `collectionsManager.facetList(listeTaches, facetedQuery, Optional.empty())` qui retourne un `FacetedQueryResult` avec la liste filtrée, les compteurs, et les facettes calculées par Lucene en RAM.

L'index Lucene est reconstruit à chaque appel sur la `DtList` fournie, donc cet axe est adapté pour des jeux de données modérés et des contextes de filtrage UI interactif.

---

## Vigilance

- **Constructeur SearchIndexDefinition** : le constructeur prend exactement 5 paramètres : name, keyConceptDataDefinition (`DataDefinition`), indexDataDefinition (`DataDefinition`), indexCopyFromFieldsMap (`Map<DataField, List<DataField>>`), searchLoaderId. Aucun builder fluide de type `SearchIndexDefinitionBuilder` n'existe. Ne pas confondre `DataDefinition` avec `DtDefinition` ; ne pas utiliser `Map<String, String>` pour la map copyTo.
- **Reindexation automatique** : `SearchManagerImpl` écoute les `StoreEvent` sur l'EventBus pour marquer les KeyConcepts comme dirty, puis file un `ReindexTask` avec un délai de 1 seconde pour éviter les appels multiples.
- **Reindexation Delta** : la méthode `getSqlQueryFilter()` du SearchLoader doit retourner un filtre SQL avec un paramètre timestamp. Les documents supprimés sont détectés par disparition du KeyConcept.
- **Ranges dans le DSL** : `[min TO max]` inclut les bornes. Utiliser `*` pour les bornes ouvertes infinies : `[0 TO *]`.
- **Géo** : les expressions géographiques ne sont pas inline dans le DSL. Elles se configurent via `SearchQueryBuilder.withGeoSearchQuery(String)`.
- **Boost et clustering** : `decay()` et `cluster()` ne sont pas inline. Utiliser `withDateBoost(DataField, int, int)` et `withFacetClustering(FacetDefinition)` sur le builder.
- **FacetValue** : c'est un record `(code, listFilter, label)`. Accès via `fv.code()`, `fv.listFilter()`, `fv.label()`. Pas de méthodes `getKey()` ni `getCount()`. Le count est la valeur de la `Map<FacetValue, Long>` retournée par `facet.getFacetValues()`.
- **SelectedFacetValues** : utiliser `getFacetValues(String facetName)`, pas `getSelectedFacetValues()`.
- **FacetedQuery immutable** : construit avec `(FacetedQueryDefinition, SelectedFacetValues)`. Pas de méthode `setFilter()` ou `execute()` sur l'objet.
- **Collection vs Index** : `collectionsManager.facetList()` recrée l'index Lucene à chaque appel sur la `DtList` fournie. Pour un usage intensif, minimiser les appels répétés sur la même liste.
- **Taille des facettes range** : les plages sont définies statiquement dans la `FacetDefinition`. Un document hors de toutes les plages n'apparaît dans aucune facette range. Inclure une plage catch-all en dernière position.
- **LoadData du SearchLoader** : `loadData(SearchChunk<K>)` retourne `List<SearchIndex<K, I>>`, pas `void`. Ne pas utiliser `SearchChunk<String>`.
- **ListFilterBuilder** : pas de méthode statique `.build()`. Utiliser le pattern de builder instance : `withListFilterQuery()` → `withCriteria()` → `build()`.
- **ESDocumentCodec** : `ESDocumentCodec` gère l'encodage/décodage des documents ElasticSearch. La sérialisation passe par base64 et éventuellement compression (à confirmer par source). Cela impacte la lisibilité directe des documents dans l'interface ES.

## Pour les experts

### Managers
| Manager | Rôle | Activé par |
|---|---|---|
| `CollectionsManager` | Facettage pur-Java + filtrage Lucene in-RAM | Always (`buildFeatures`) |
| `SearchManager` | Reindexation (3 stratégies), requêtes ElasticSearch | `search` |

### Features (@Feature)
| Flag | Composants |
|---|---|
| `search` | `SearchManager` + `SearchManagerImpl` |
| `search.elasticsearch.client` | `ClientESSearchServicesPlugin` (Transport legacy) |
| `search.elasticsearch.restHL` | `RestHLClientESSearchServicesPlugin` (RestHighLevelClient 7.17.x) |
| `collections.luceneIndex` | `LuceneIndexPlugin` |

### API fluide (Suppliers)
| Supplier | Rôle |
|---|---|
| `SearchIndexDefinitionSupplier` | Construction fluide de `SearchIndexDefinition` |
| `FacetedQueryDefinitionSupplier` | Construction fluide de `FacetedQueryDefinition` |
| `FacetTermDefinitionSupplier` | Construction fluide d'une `FacetDefinition` terme |
| `FacetRangeDefinitionSupplier` | Construction fluide d'une `FacetDefinition` range |
| `FacetCustomDefinitionSupplier` | Construction fluide d'une `FacetDefinition` custom |

### Utils & Pattern Filters
| Classe | Rôle |
|---|---|
| `FacetFactory` | Factory de facettes (term/range/custom) et clusters |
| `IndexFilterFunction<D>` | Filtrage indexé Lucene (keywords, sort, pagination) |
| `DtListPatternFilter<D>` | Pattern runtime : `FIELD:VALUE` ou `FIELD:[MIN TO MAX]` |
| `DtListPatternFilterUtil` | Parser regex : conversion BasicType, ranges, termes |

### Plugins
| Plugin | Rôle | Feature |
|---|---|---|
| `LuceneIndexPlugin` | Index Lucene en RAM pour le facettage in-mémoire | `collections.luceneIndex` |
| `ClientESSearchServicesPlugin` | Client Transport legacy ElasticSearch | `search.elasticsearch.client` |
| `RestHLClientESSearchServicesPlugin` | Client REST High Level ElasticSearch 7.17.x | `search.elasticsearch.restHL` |

### Configuration YAML
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
