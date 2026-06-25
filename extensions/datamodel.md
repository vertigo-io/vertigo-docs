# DataModel

**DataModel** est un module central des extensions Vertigo permettant de partager des concepts communs de Data Transfert Object et de ce qui tourne autour.

Ce module est fortement basé sur des définitions qui ont vocation à être transverse.

Il inclut :

- de nombreuses définitions liées à la couche domaine :
 	- `DtDefinition`
	- Contraintes, Formatters
	- Associations N-N, 1-N
 	- `TaskDefinition`, `TaskAttribute`
- des concepts/API transverses :
	- `UID`, `Entity`, `DataObject`, `VAccessor`
	- `DtList`, `DtListState`, `DtListURI`
 	- `DtMasterData`, `DtStaticMasterData`, `KeyConcept`, `Fragment`
 	- `SmartTypeDefinition`, `Formatter`, `Constraint`
	- `Criteria`, `Criterion`, `CriteriaExpression`
- les managers `SmartTypeManager` et `TaskManager`, toujours actifs

## Utilisation via Studio

Une majorité des concepts de ce module peuvent être générés via l'outil Studio.
Les générateurs suivants sont liés à ce module :

- `vertigo.domain.java`: génère les classes Java des DtObject
- `vertigo.domain.java.targetSubDir`: précise le répertoire de génération (par défaut *~/javagen*)
- `vertigo.domain.java.generateDtResources`: génère les fichiers .properties pour le i18n des libellés des champs
- `vertigo.domain.sql`: génère le fichier crebase.sql pour régénérer la structure de la base
- `vertigo.domain.sql.targetSubDir`: précise le répertoire de génération du SQL
- `vertigo.domain.sql.baseCible`: Type de la base *(pour les syntaxes spécifiques)*
- `vertigo.domain.sql.generateDrop`: génère les DROP dans crebase.sql
- `vertigo.domain.sql.generateMasterData`: génère les scripts de remplissage des données de référence
- `vertigo.task`: génère les classes Java des tâches d'accès aux données
- `mermaid`: génère un fichier HTML pour visualiser le modèle graphiquement

### Syntaxe KSP

__Généralités__

```ksp
create <<type>> <<nom>> {
    <<corps de la déclaration>>
}
```
Permet de déclarer une nouvelle définition.

```ksp
alter <<type>> <<nom>> {
    <<corps de la déclaration>>
}
```
Permet de modifier/compléter une définition existante.

__DtDefinition__

```ksp
create DtDefinition DtUsager {
    id usaId {domain: DoId label:"Id" cardinality:"1"}
    field email {domain: DoEmail label:"E-mail"}
}
```

- `field` : déclare un champ de l'objet
	- `domain` : SmartType du champ
	- `label` : libellé du champ
	- `cardinality` : `?` (0-1), `1` (obligatoire), `*` (multiple)
- `id` : désigne l'entité persistante et sa clé primaire *(pas de PK multiple, sauf tables d'association N-N)*

__StereoType__

```ksp
create DtDefinition DtReservation {
    stereotype: "KeyConcept"
	...
}
```

- `stereotype` : tag de l'objet. Valeurs possibles : `ValueObject` *(défaut)*, `MasterData`, `StaticMasterData`, `KeyConcept`, `Entity`, `Fragment`

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

Les StaticMasterData sont des listes de référence figées. L'id est de type String.

__SmartTypes__

```ksp
create Domain DoVisitCount {
    dataType: Integer
	storeType : "NUMERIC"
}
```

- `dataType` : Type Java de la donnée
- `storeType` : Type de stockage SQL *(dépend de la BDD)*

__SmartTypes : ValueObject__

```ksp
create Domain DoFormulaire {
	dataType : ValueObject
	type : "com.monde.ECommerce.models.CoinType"
	storeType : "JSONB"
}
```

- `dataType: ValueObject` : Objet converti par des `Adapter` selon le contexte *(SQL, UI…)*
- `type` : Classe Java de la donnée

**Note** : `Domain` et le préfixe `Do` sont historiques. Dans le reste de Vertigo, cette notion est `SmartType`.

## TaskManager

Le `TaskManager` gère l'exécution des tâches définies dans le KSP. Il expose `TaskDefinition`, `TaskBuilder`, `TaskResult` pour la programmation des tâches, et un système de proxy basé sur les annotations.

### Proxy Annotations

| Annotation | Rôle |
|---|---|
| `@TaskAnnotation` | Déclare une méthode comme proxy de tâche |
| `@TaskProxyAnnotation` | Interface de proxy de tâche |
| `@TaskInput` | Paramètre d'entrée de la tâche |
| `@TaskOutput` | Résultat de sortie de la tâche |
| `@TaskContextProperty` / `@TaskContextProperties` | Propriété du contexte d'exécution |

L'implémentation `TaskAmplifierMethod` relie les annotations proxy aux `TaskDefinition` réelles.

## SmartType Annotations

Les SmartTypes peuvent être définis en Java avec des annotations, alternativement au KSP + enum classique :

| Annotation | Rôle |
|---|---|
| `@SmartTypeDefinition` | Définit un SmartType pour un BasicType |
| `@SmartTypeProperty` / `@SmartTypeProperties` | Propriétés du SmartType (storeType, etc.) |
| `@Formatter` | Formateur associé |
| `@Constraint` / `@Constraints` | Contraintes de validation |
| `@Adapter` / `@Adapters` | Adaptateurs de conversion |

## Stereotype Annotations

Pour les DtObject, les annotations Java sont alternatives au KSP :

| Annotation | Rôle |
|---|---|
| `@DataSpace` | Espace de données |
| `@Field` | Champ d'un DtObject |
| `@DisplayField` | Champ d'affichage |
| `@SortField` | Champ de tri |
| `@KeyField` | Champ de clé |
| `@ForeignKey` | Clé étrangère |
| `@Association` | Association 1-N |
| `@AssociationNN` | Association N-N |
| `@Fragment` | Fragment d'entité |

## Criteria API

L'API Criteria permet de construire des requêtes dynamiques :

- `Criteria` / `Criterion` : Expressions de critère
- `CriteriaEncoder` / `CriterionOperator` / `CriteriaLogicalOperator` : Codage et opérateurs
- `CriteriaExpression` / `CriteriaCtx` : Expression et contexte
- `CriterionLimit` / `Criterions` / `CriteriaUtil` : Utilitaires de construction

## Associations

Les associations entre objets sont définies par :

| Classe | Rôle |
|---|---|
| `AssociationDefinition` | Définit une association |
| `AssociationSimpleDefinition` | Association 1-N |
| `AssociationNNDefinition` | Association N-N |
| `AssociationNode` | Nœud d'association |
| `DtListURIForAssociation` | URI vers liste d'association |
| `DtListURIForSimpleAssociation` | URI association simple |
| `DtListURIForNNAssociation` | URI association N-N |

## Pour les experts

### Managers

| Manager | Impl | Activation |
|---|---|---|
| `SmartTypeManager` | `SmartTypeManagerImpl` | Toujours actif (`buildFeatures()`) |
| `TaskManager` | `TaskManagerImpl` | Toujours actif (`buildFeatures()`) |

### Composants internes (toujours actifs)

| Composant | Rôle |
|---|---|
| `DataModelFeatures` | Classe `@Feature` qui active les managers via `buildFeatures()` |
| `DataMetricsProvider` | Métriques d'accès aux données |
| `TaskMetricsProvider` | Métriques d'exécution des tâches |
| `SmartTypesLoader` | Chargement des SmartTypes |
| `DtObjectsLoader` | Chargement des DtObjects |
| `TaskAmplifierMethod` | Proxy Task → DI |

### Composition

| Catégorie | Classes |
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
