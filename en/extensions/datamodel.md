# DataModel

**DataModel** is a central module in Vertigo extensions for sharing common Data Transfer Object concepts and related functionality.

This module is heavily based on definitions that are designed to be cross-cutting.

It includes:

- numerous definitions related to the domain layer:
  - `DtDefinition`
  - Constraints, Formatters
  - N-N, 1-N Associations
  - `TaskDefinition`, `TaskAttribute`
- cross-cutting concepts/API:
  - `UID`, `Entity`, `DataObject`, `VAccessor`
  - `DtList`, `DtListState`, `DtListURI`
  - `DtMasterData`, `DtStaticMasterData`, `KeyConcept`, `Fragment`
  - `SmartTypeDefinition`, `Formatter`, `Constraint`
  - `Criteria`, `Criterion`, `CriteriaExpression`
- managers `SmartTypeManager` and `TaskManager`, always active

## Usage via Studio

Most concepts in this module can be generated via Studio.
The following generators are related to this module:

- `vertigo.domain.java`: generates Java classes for DtObject
- `vertigo.domain.java.targetSubDir`: specifies generation directory (default *~/javagen*)
- `vertigo.domain.java.generateDtResources`: generates .properties files for field label i18n
- `vertigo.domain.sql`: generates crebase.sql to regenerate database structure
- `vertigo.domain.sql.targetSubDir`: specifies SQL generation directory
- `vertigo.domain.sql.baseCible`: Database type *(for specific syntaxes)*
- `vertigo.domain.sql.generateDrop`: generates DROP statements in crebase.sql
- `vertigo.domain.sql.generateMasterData`: generates reference data population scripts
- `vertigo.task`: generates Java classes for data access tasks
- `mermaid`: generates an HTML file for graphical model visualization

### KSP Syntax

__General__

```ksp
create <<type>> <<name>> {
    <<declaration body>>
}
```
Declares a new definition.

```ksp
alter <<type>> <<name>> {
    <<declaration body>>
}
```
Modifies/completes an existing definition.

__DtDefinition__

```ksp
create DtDefinition DtUser {
    id usrId {domain: DoId label:"Id" cardinality:"1"}
    field email {domain: DoEmail label:"E-mail"}
}
```

- `field`: declares an object field
  - `domain`: SmartType of the field
  - `label`: field label
  - `cardinality`: `?` (0-1), `1` (required), `*` (multiple)
- `id`: designates the persistent entity and its primary key *(no multiple PK, except N-N association tables)*

__Stereotype__

```ksp
create DtDefinition DtReservation {
    stereotype: "KeyConcept"
	...
}
```

- `stereotype`: object tag. Possible values: `ValueObject` *(default)*, `MasterData`, `StaticMasterData`, `KeyConcept`, `Entity`, `Fragment`

__StaticMasterData__

```ksp
create DtDefinition DtBaseType {
	stereotype : "StaticMasterData"
	id baseTypeId {domain: DoCode label:"Id"}
	field label {domain: DoLabel label:"Base Type Label"}
	values : `{ "hydro": {"baseTypeId":"HYDRO","label":"Hydroponic"},
	          "mine": {"baseTypeId":"MINE","label":"Mining Complex"} }`
}
```

StaticMasterData are fixed reference lists. Id is of type String.

__SmartTypes__

```ksp
create Domain DoVisitCount {
    dataType: Integer
	storeType : "NUMERIC"
}
```

- `dataType`: Java type of the data
- `storeType`: SQL storage type *(depends on the database)*

__SmartTypes: ValueObject__

```ksp
create Domain DoFormulaire {
	dataType : ValueObject
	type : "com.monde.ECommerce.models.CoinType"
	storeType : "JSONB"
}
```

- `dataType: ValueObject`: Object converted by `Adapter` according to context *(SQL, UI…)*
- `type`: Java class of the data

**Note**: `Domain` and the `Do` prefix are historical. Elsewhere in Vertigo, this concept is `SmartType`.

## TaskManager

`TaskManager` handles execution of tasks defined in KSP. It exposes `TaskDefinition`, `TaskBuilder`, `TaskResult` for task programming, and an annotation-based proxy system.

### Proxy Annotations

| Annotation | Role |
|---|---|
| `@TaskAnnotation` | Declares a method as a task proxy |
| `@TaskProxyAnnotation` | Task proxy interface |
| `@TaskInput` | Task input parameter |
| `@TaskOutput` | Task output result |
| `@TaskContextProperty` / `@TaskContextProperties` | Execution context property |

Implementation `TaskAmplifierMethod` links proxy annotations to actual `TaskDefinition`.

## SmartType Annotations

SmartTypes can be defined in Java with annotations, as an alternative to KSP + classic enum:

| Annotation | Role |
|---|---|
| `@SmartTypeDefinition` | Defines a SmartType for a BasicType |
| `@SmartTypeProperty` / `@SmartTypeProperties` | SmartType properties (storeType, etc.) |
| `@Formatter` | Associated formatter |
| `@Constraint` / `@Constraints` | Validation constraints |
| `@Adapter` / `@Adapters` | Conversion adapters |

## Stereotype Annotations

For DtObject, Java annotations are an alternative to KSP:

| Annotation | Role |
|---|---|
| `@DataSpace` | Data space |
| `@Field` | DtObject field |
| `@DisplayField` | Display field |
| `@SortField` | Sort field |
| `@KeyField` | Key field |
| `@ForeignKey` | Foreign key |
| `@Association` | 1-N Association |
| `@AssociationNN` | N-N Association |
| `@Fragment` | Entity fragment |

## Criteria API

The Criteria API builds dynamic queries:

- `Criteria` / `Criterion`: Criteria expressions
- `CriteriaEncoder` / `CriterionOperator` / `CriteriaLogicalOperator`: Encoding and operators
- `CriteriaExpression` / `CriteriaCtx`: Expression and context
- `CriterionLimit` / `Criterions` / `CriteriaUtil`: Construction utilities

## Associations

Associations between objects are defined by:

| Class | Role |
|---|---|
| `AssociationDefinition` | Defines an association |
| `AssociationSimpleDefinition` | 1-N Association |
| `AssociationNNDefinition` | N-N Association |
| `AssociationNode` | Association node |
| `DtListURIForAssociation` | URI to association list |
| `DtListURIForSimpleAssociation` | URI simple association |
| `DtListURIForNNAssociation` | URI N-N association |

## For Experts

### Managers

| Manager | Impl | Activation |
|---|---|---|
| `SmartTypeManager` | `SmartTypeManagerImpl` | Always active (`buildFeatures()`) |
| `TaskManager` | `TaskManagerImpl` | Always active (`buildFeatures()`) |

### Internal Components (always active)

| Component | Role |
|---|---|
| `DataModelFeatures` | Features class activating managers via `buildFeatures()` |
| `DataMetricsProvider` | Data access metrics |
| `TaskMetricsProvider` | Task execution metrics |
| `SmartTypesLoader` | SmartType loading |
| `DtObjectsLoader` | DtObject loading |
| `TaskAmplifierMethod` | Task Proxy → DI |

### Composition

| Category | Classes |
|---|---|
| **SmartType** | `SmartTypeDefinition`, `SmartTypeDefinitionBuilder`, `Properties`, `Property`, `PropertiesBuilder`, `DtProperty`, `FormatterConfig`, `ConstraintConfig`, `SmarttypeResources` |
| **SmartType Annotations** | `@SmartTypeDefinition`, `@SmartTypeProperty`, `@SmartTypeProperties`, `@Formatter`, `@Constraint`, `@Constraints`, `@Adapter`, `@Adapters` |
| **SmartType Implementations** | `Formatter`, `FormatterException`, `Constraint`, `ConstraintException` |
| **Data Definitions** | `DataDefinition`, `DataDefinitionBuilder`, `DataField`, `DataFieldName`, `DataStereotype`, `DataDescriptor`, `DataAccessor` |
| **Data Stereotype Annotations** | `@DataSpace`, `@Field`, `@DisplayField`, `@SortField`, `@KeyField`, `@ForeignKey`, `@Association`, `@AssociationNN`, `@Fragment` |
| **Data Model** | `Entity`, `DataObject`, `VAccessor`, `ListVAccessor`, `UID`, `DtList`, `DtListState`, `DtListURI`, `DtListURIForMasterData`, `Fragment`, `MasterDataEnum`, `DtMasterData`, `DtStaticMasterData`, `KeyConcept` |
| **Associations** | `AssociationDefinition`, `AssociationSimpleDefinition`, `AssociationNNDefinition`, `AssociationNode`, `DtListURIForAssociation`, `DtListURIForSimpleAssociation`, `DtListURIForNNAssociation` |
| **Task Definitions** | `TaskDefinition`, `TaskDefinitionBuilder`, `TaskAttribute`, `TaskEngine` |
| **Task Model** | `Task`, `TaskBuilder`, `TaskResult` |
| **Task Proxy** | `@TaskAnnotation`, `@TaskProxyAnnotation`, `@TaskInput`, `@TaskOutput`, `@TaskContextProperty`, `@TaskContextProperties` |
| **Criteria** | `Criteria`, `Criterion`, `CriteriaEncoder`, `CriterionOperator`, `CriteriaLogicalOperator`, `CriteriaExpression`, `CriteriaCtx`, `CriterionLimit`, `Criterions`, `CriteriaUtil` |
| **Data Util** | `DataModelUtil`, `AssociationUtil`, `VCollectors` |
| **Impl/Loaders** | `Loader`, `DynamicDefinition`, `DynamicDefinitionSolver`, `SmartTypesLoader`, `DtObjectsLoader`, `TaskAmplifierMethod` |
