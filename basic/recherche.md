# Recherche

Dans les projets Vertigo, l'intégration d'un moteur de recherche puissant est simplifiée et pérénisée par l'utilisation du module **Dynamo-search**.

## Principe général

L'intégration d'un moteur de recherche est devenu un standard dans les projets car son apport de valeur est indéniable.

Le module de recherche Vertigo permet : 

- d'apporter une fonctionnalité de recherche riche et performante (facettes, recherche plein texte, phonétique, compteurs de résultats, tri par pertinence, etc..., tout ca avec des performances de qques millisecondes : incomparables avec des requetes SQL..)
- de placer la recherche au centre : toutes les entités clés peuvent être indéxées et recherchées par les utilisateurs. C'est un point d'accès privilégié : on entre par la recherche, on navige par la recherche. Les critères restent simples et l'on affine par les facettes.
- de rendre accéssible l'accès à l'information, l'utilisateur est soit un néophyte soit auto-formé. La recherche proposée reprend les standards actuels du net, et permet une prise en main rapide. 
- au développeur de paramétrer le mécanisme de recherche. La paramétrage ouvre les posibilités, tout en outillant et stabilisant les composants techniques sous jacents.
- de générer lors du MDA les facades d'appels aux recherches paramétrées, l'usage du moteur de recherche est donc décorélé du paramtrage des recherches mis à disposition.

Le module de recherche Vertigo supporte les trois cas d'usage principaux :

- recherche d'**un élément** à partir d'**informations connues**
- recherche d'**un élément** **sans information** connu précisément
- constitution d'**un ensemble** d'élément pour une action globale **par étapes** successives

!> La recherche est un filtre : plus l'utilisateur donne d'informations plus on réduit le champ des résultats.

**Moteur utilisé**
[ElasticSearch](https://www.elastic.co/products/elasticsearch) & [Lucene](https://lucene.apache.org/). 
Le mécanisme de recherche est le [QueryStringQuery](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html)

ElasticSearch est un moteur de recherche basé sur la librairie Java Lucene.
Ce moteur est supporté par la société Elastic et est activement et régulièrement mis à jour, la conséquence principale de cette activité est une certaine volativité de l'API (il y a régulièrement des breaking-changes). 
C'est l'un des intérets du module Vertigo : une bonne partie des modifications peuvent être absorbées par le module, ce qui simplifie la montée de version pour les projets.
Vertigo maintient deux versions du plugin ElasticSearch : la version courante et la version précédente. 


## Configuration

### Activer le module

Pour commencer il faut activer le module **Dynamo-Search**.
Le module propose deux modes de fonctionnement : 
- le mode standard utilisant un serveur ElasticSearch distant
- le mode embedded utilisant un serveur ElasticSearch local démarré en même temps de l'application (utile pour les tests) 

!> Le mode embedded est déprécié par ElasticSearch depuis la version 5.

Exemple pour le mode Standard :
```yaml
modules
  io.vertigo.commons.CommonsFeatures:
  io.vertigo.dynamo.DynamoFeatures:
    features:
      - search
    featuresConfig:
      - search.elasticsearchTransport:
          servers.names: ${esHost}
          envIndex: mars
          cluster.name: mars
          rowsPerQuery: 50
          config.file: search/elasticsearch.yml
```

Exemple pour le mode Embedded :
```yaml
modules
  io.vertigo.commons.CommonsFeatures:
  io.vertigo.dynamo.DynamoFeatures:
    features:
      - search
    featuresConfig:
      - search.elasticsearchEmbedded:
          home: search/
          envIndex: mars
          rowsPerQuery: 50
          config.file: search/elasticsearch.yml
```

> Notez que le paramètre `envIndex` permet d'indiquer un préfix des index pour un environement applicatif, ainsi un même serveur ElasticSearch peut être utilisé pour différents environnements.
> Les nouvelles versions d'ElasticSearch impose un seul type de document par index.

### Configuration ElasticSearch

Le fichier elasticsearch.yml donne la configuration de l'index ElasticSearch, il permet de configurer les types d'analyzers utilisés par l'application et rattachés aux Domaines du modèle.
Cette configuration est envoyée par l'application au serveur ElasticSearch au démarrage.

Exemple de configuration d'analyser, cette configuration conviendra à la plus part des projets :
```yaml
index :
    analysis :
        normalizer :
            code :
                type : custom
            sortable :
                type : custom
                filter : [lowercase, asciifolding]  
        analyzer :
            multiple_code :
                tokenizer : piped_keywords
                filter : [standard]
            text_fr :
                tokenizer : standard
                filter : [standard, lowercase, asciifolding, snowball, elision]
        tokenizer :
            piped_keywords :
                type : pattern
                pattern : '([|,] *)'
        filter :
            snowball:
                type : snowball
                language: French
            elision:
                type : elision
                articles: [l, m, t, qu, n, s, j, d]
```


### Identifier vos **KeyConcept** (*entités métiers clés*)
Soit dans vos fichiers **KSP**: 
```javascript
alter DtDefinition DT_MOVIE {
  stereotype : "KeyConcept"
}
```

Soit dans votre fichier **OOM** : 
Sur vos classes indiquer le **Stereotype**: `KeyConcept`

### Ajout un DtObject réprésentant vos données d'index

Les indexes sont très puissants et gère des données **documentaire**. Il n'y pas de relationnel, il faut donc convertir votre grappe d'objet partant de votre **KeyConcept** en **Document**.
Très simplement, il s'agit de créer un DtObject mettant les données à plat.
```javascript
create DtDefinition DtEquipmentIndex {
	field equipmentId {domain: DoId label:"Id" required:"true"}
	field name {domain: DoLabel label: "Name" required:"false"}
	field code {domain: DoCode label: "Code" required:"false"}
	field purchaseDate {domain: DoLocaldate label: "Date of purchase" required:"false"}
	field description {domain: DoDescription label: "Description" required:"false"}
	field tags {domain: DoTags label: "Tags" required:"false"}
	field equipmentTypeName {domain: DoLabel label:"Type" required:"false"}
	field equipmentCategoryName {domain: DoLabel label:"Category" required:"false"}
}
```

Il est possible de préciser comment la donnée est indexée par la propriété **indexType** du domaine. 
Cette propriété permet la conversion du simple **Domain Vertigo** , vers le type ElasticSearch plus complexe.
Sa syntaxe est la suivante :
`` indexType : "myAnalyzer{:myDataType}{:stored|notStored}{:sortable|notSortable}{:facetable|notFacetable}" ``

Exemple de domain :

```javascript
create Domain DoCode {
	dataType : String
	formatter : FmtDefault
	indexType : "code:keyword"
}

create Domain DoLabel {
	dataType : String
	formatter : FmtDefault
	indexType : "text_fr:sortable"
}

create Domain DoDescription {
	dataType : String
	formatter : FmtDefault
	indexType : "text_fr"
}

create Domain DoTags {
	dataType : String
	formatter : FmtTags
	indexType : "multiple_code:facetable"
}
```


### Définition des indexes

Les indexes sont déclarés comme des **Definitions** Vertigo. Il est possible de le faire en Java ou en DSL.
Le plus simple est via le DSL, c'est cette méthode qui est décrite ici.

#### **IndexDefinition**

L'**IndexDefinition** représente un Index. Il n'en faut qu'un seul par KeyConcept. 
*Il est donc parfois nécessaire de créer des KeyConcept agrégeant d'autres KeyConcept.*
```javascript
create IndexDefinition IdxEquipment {  
  keyConcept : DtEquipment
  dtIndex : DtEquipmentIndex 
  loaderId : "EquipmentSearchLoader"
}
```
> L'attribut `loaderId` pointe sur un Composant Vertigo qui implémente l'interface `SearchLoader<? extends DtObject>` adaptée pour l'objet d'index


#### **FacetDefinition**

La **FacetDefinition** représente une définition de facette. Il en existe deux types : 

* les facettes **term** dont les valeurs sont tirées dynamiquement des données de l'index, 

```javascript
create FacetDefinition FctEquipmentEquipmentTypeName {
	dtDefinition:DtEquipmentIndex, fieldName:"equipmentTypeName", label:"Equipment Type"
}
```

* les facettes **range** qui sont prédéfinies et rassemblent un ensemble de valeurs dans chaque facette.
```javascript
create FacetDefinition FctEquipmentPurchaseDate {
	dtDefinition:DtEquipmentIndex, fieldName:"purchaseDate", label:"Purchase Date"
	range r1 { filter:"purchaseDate:[01/01/2008 TO 01/01/2012]", label:"2008-2012"},
	range r2 { filter:"purchaseDate:[01/01/2012 TO 01/01/2016]", label:"2012-2016"},
	range r3 { filter:"purchaseDate:[01/01/2016 TO *]", label:"after 2016"}
}
```
> Le **filter** de la facette **range** reprend la syntaxe du moteur de recherche utilisé (ici ElasticSearch).

#### **FacetedQueryDefinition**

La **FacetedQueryDefinition** représente une définition de requête de recherche. Associée à un KeyConcept elle précise également :

* Les facettes utilisées
* Le type de critère d'entrée (par son **domain**) 
* La class de construction de la requête envoyée au moteur de recherche
* Le pattern de la requête du moteur de recherche
```javascript
create FacetedQueryDefinition QryEquipment {
	keyConcept : DtEquipment
	facets : [FctEquipmentEquipmentTypeName, FctEquipmentPurchaseDate ]
	domainCriteria : DoLabel
	listFilterBuilderClass : "io.vertigo.dynamox.search.DslListFilterBuilder"  
	listFilterBuilderQuery : "allText:#+query*#"
}
```
Le **DslListFilterBuilder** de Vertigo est préconisé. Il propose de nombreuses fonctionnalités. Consulter la documentation avancée pour plus d'informations ([DslListFilterBuilder]).


#### **Code généré**

Le module MDA de Vertigo (*Vertigo-Studio*) utilise ces informations pour générer une méthode pour chaque FacetedQueryDefinition dans le DAO du KeyConcept associé.

### Service de chargement des données

Vertigo effectue automatiquement les mises à jour de l'index lorsque les données sont modifiées.
Pour cela, Vertigo surveille les modifications d'objet qui passent par le DAO de votre KeyConcept, si vous effectuer une mise à jour hors de ce DAO ou sur un autre object que le KeyConcept de l'index, vous devez l'indiquer en utilisant le readOneForUpdate **au début** du service effectuant la modification *(cela pose un lock)*.

Pour cette opération Vertigo à besoin du service de chargement des données de l'index :

```java
/**
 * Specific SearchIndex loader.
 * @param <K> KeyConcept
 * @param <I> Indexed data's type
 * @author npiedeloup, pchretien
 */
public interface SearchLoader<K extends KeyConcept, I extends DtObject> extends Component {
	/**
	 * Load all data from a list of keyConcepts.
	 * @param searchChunk the chunk
	 * @return List of searchIndex
	 */
	List<SearchIndex<K, I>> loadData(SearchChunk<K> searchChunk);

	/**
	 * Create a chunk iterator for crawl all keyConcept data.
	 * @param keyConceptClass keyConcept class
	 * @return Iterator of chunk
	 */
	Iterable<SearchChunk<K>> chunk(final Class<K> keyConceptClass);
}
```

Pour les cas standard, Vertigo propose un `AbstractSqlSearchLoader` a étendre. Il suffit d'implémenter le chargement de la liste des SearchIndex à partir d'une liste d'id.
Exemple :
```java
public final class EquipmentSearchLoader extends AbstractSqlSearchLoader<Long, Equipment, EquipmentIndex> {

	private final EquipmentServices myEquipmentServices;

	@Inject
	public EquipmentSearchLoader(final TaskManager taskManager, final VTransactionManager transactionManager, final EquipmentServices equipmentServices) {
		super(taskManager, transactionManager);
		myEquipmentServices = equipmentServices;
	}

	@Override
	public List<SearchIndex<Equipment, EquipmentIndex>> loadData(final SearchChunk<Equipment> searchChunk) {
		final SearchIndexDefinition indexDefinition = Home.getApp().getDefinitionSpace().resolve("IdxEquipment", SearchIndexDefinition.class);
		final List<Long> equipmentIds = new ArrayList<>();
		for (final UID<Equipment> uid : searchChunk.getAllUIDs()) {
			equipmentIds.add((Long) uid.getId());
		}
		final DtList<EquipmentIndex> equipmentIndexes = basemanagementPAO.loadEquipmentIndex(equipmentIds);
		final List<SearchIndex<Equipment, EquipmentIndex>> equipmentSearchIndexes = new ArrayList<>(searchChunk.getAllUIDs().size());
		for (final EquipmentIndex equipmentIndex : equipmentIndexes) {
			equipmentSearchIndexes.add(SearchIndex.<Equipment, EquipmentIndex> createIndex(indexDefinition,
					UID.of(indexDefinition.getKeyConceptDtDefinition(), equipmentIndex.getEquipmentId()), equipmentIndex));
		}
		return equipmentSearchIndexes;
	}
}
```


Il possible de filtrer la liste des KeyConcept à indexer en surchargeant la méthode `getSqlQueryFilter` pour préciser un filtre SQL :
```java
  /** {@inheritDoc} */
  @Override
  protected String getSqlQueryFilter() {
    //only index equipement with a purchaseDate
    return "PURCHASE_DATE is not null";
  }
```

### Récupération de l'objet à indexer

Une tache SQL de récupération de l'objet à indexer doit être déclarée :
```json
create Task TkLoadEquipmentIndex {
	className : "io.vertigo.dynamox.task.TaskEngineSelect",
	request : "	select 	equ.EQUIPMENT_ID,
						equ.NAME, 
						equ.CODE, 
						equ.PURCHASE_DATE, 
						equ.TAGS, 
						equipmentType.LABEL as EQUIPMENT_TYPE_NAME,
						equipmentCategory.LABEL as EQUIPMENT_CATEGORY_NAME
				from EQUIPMENT equ
				join EQUIPMENT_TYPE equipmentType on equipmentType.equipment_type_id = equ.equipment_type_id
				join EQUIPMENT_CATEGORY equipmentCategory on equipmentCategory.equipment_category_id = equipmentType.equipment_category_id
				where EQUIPMENT_ID in (#equipmentIds.rownum#);"
	attribute equipmentIds {domain : DoLongs, required:"true", inOut :"in",} 
	attribute dtcIndex {domain : DoDtEquipmentIndexDtc, required:"true", inOut :"out",} 
}
    
```

### Lancer l'indexation

Maintenant que tout est configuré, il faut lancer la première indexation.
Rien de plus simple, il suffit de créer un service qui appel la méthode `reindexAll` de `SearchManager` 

Exemple :
```java
  /** {@inheritDoc} */
  @Override
  public void reindexAllEquipements() {
    searchManager.reindexAll(searchManager.findFirstIndexDefinitionByKeyConcept(Equipement.class));
  }
```

### Lancer une recherche

Pour lancer une recherche Vertigo a générer du code dans le DAO du KeyConcept associé à l'index. Il faut d'abord créer une SearchQuery et la faire éxécuter par le DAO.

Exemple :
```java
  	public FacetedQueryResult<EquipmentIndex, SearchQuery> searchEquipments(final String criteria, final SelectedFacetValues selectedFacetValues, final DtListState dtListState) {
		final SearchQuery searchQuery = equipmentSearchClient.createSearchQueryBuilderEquipment(criteria, selectedFacetValues).build();
		return equipmentSearchClient.loadList(searchQuery, dtListState);
	}
```

L'object de résultat `FacetedQueryResult` fournit de nombreuses informations utiles pour l'affichage :

* liste
* facettes (et pour chaque facette le nombre de document par valeur de facette)
* highlights (si activé)
* la searchQuery source de la requête

### Ajouter la sélection d'une facette

La méthode générée dans le DAO du KeyConcept prend en paramètre un `SelectedFacetValues`.
Vertigo propose un pont entre cet Objet et les IHMs utilisées (WebServices, SpringMVC ou Struts2)




