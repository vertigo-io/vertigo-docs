# Recherche

Dans les projets Vertigo, l'intégration d'un moteur de recherche puissant est simplifiée et pérénisée par l'utilisation du module **Dynamo-search**.

## Principe général

L'intégration d'un moteur de recherche est devenu un standard dans les projets car son apport de valeur est indéniable.

Le module de recherche Vertigo permet : 

- d'apporter une fonctionnalité de recherche riche et performante (facettes, recherche plein texte, phonétique, compteurs de résultats, tri par pertinence, etc..., tout ça avec des performances de qques millisecondes : incomparables avec des requetes SQL)
- de placer la recherche au centre : toutes les entités clés peuvent être indéxées et recherchées par les utilisateurs. C'est un point d'accès privilégié : on entre par la recherche, on navige par la recherche. Les critères restent simples et l'on affine par les facettes.
- de rendre accéssible l'accès à l'information, l'utilisateur est soit un néophyte soit auto-formé. La recherche proposée reprend les standards actuels du net, et permet une prise en main rapide. 
- au développeur de paramétrer le mécanisme de recherche. La paramétrage ouvre les posibilités, tout en outillant et stabilisant les composants techniques sous jacents.
- de générer lors du MDA les facades d'appels aux recherches paramétrées, l'usage du moteur de recherche est donc décorélé du paramtrage des recherches mis à disposition.

Le module de recherche Vertigo supporte les trois cas d'usage principaux :

- recherche d'**un élément** à partir d'**informations connues**
- recherche d'**un élément** **sans information** connu précisément
- constitution d'**un ensemble** d'élément pour une action globale **par étapes** successives

!> La recherche est un filtre : plus l'utilisateur donne d'informations plus on réduit le champ des résultats.

!> La recherche la plus courante est dite plain-text, ce qui signifie : "cherche un document qui contient un mot qui commence par", *ca ne signifie par "contient"* 
!> Les performances du moteur sont assurées par un index des mots des documents (comme dans un livre), il faut donc toujours le début du mot pour s'y retrouver dans l'index : pas de recherche `*oitur`*  

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

> Les champs ayant l'attribut `sortable`, sont automatiquement doublés avec une version 'keyword' du champ.
> Ce pseudo permet de trier correctement le champ. Vertigo l'utilise de manière transparente pour les tris et les facettes.
> Il peut être utilisé dans les requetes : 
> **Exemple :**
> ``field1.keyword:#query#``


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

**Propriétés**
- `keyConcept`* : Nom du Dt KeyConcept, utilisé pour suivre les modifications et déclencher les réindexations
- `dtIndex`* : Nom du Dt représentant le document, à la fois les champs recherchés et les champs retournés
- `searchLoader`* : Nom d'un composant Vertigo utilisé pour recharger les documents à partir d'une liste d'Ids (doit implémenter l'interface SearchLoader<keyConcept, dtIndex>)
- `indexCopyTo` : Ajoute un champ aggrégeant une liste de champ du document, utilise la fonction de copy optimisée du moteur (le champ doit préexister dans le DtIndex)
  - `from` : liste des champs séparés par une virgule

```javascript
create IndexDefinition IdxEquipment {  
  keyConcept : DtEquipment
  dtIndex : DtEquipmentIndex 
  loaderId : "EquipmentSearchLoader"
  indexCopyTo allText { from: "name,code,description,tags,equipmentTypeName,equipmentCategoryName" }
}
```
> L'attribut `loaderId` pointe sur un Composant Vertigo qui implémente l'interface `SearchLoader<? extends DtObject>` adaptée pour l'objet d'index


#### **FacetDefinition**

La **FacetDefinition** représente une définition de facette. Il en existe deux types : 

**Propriétés**
- `dtDefinition`* : Nom du Dt d'index
- `fieldName`* : Nom du champ portant la facette
- `label`* : Label de la facette
- `order` : Change le mode de tri de la facette : alpha, count (par défaut pour les terms), definition (pour les ranges)
- `multiSelectable` : Boolean indiquant que les valeurs de facettes sont multi-selectionnables (false par défaut) 
- `range` : Ajoute une valeur de facette (pour les facettes **range**), le nom est utilisé comme code
  - `filter`* : filtre de recherche pour cette valeur. Reprend la syntaxe du moteur de recherche utilisé (ici ElasticSearch).
  - `label`* : label de cette valeur

!> Attention : les facettes multiSelectable impactent les performances 
  
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

#### **FacetedQueryDefinition**

La **FacetedQueryDefinition** représente une définition de requête de recherche. Associée à un KeyConcept elle précise également :

* Les facettes utilisées
* Le type de critère d'entrée (par son **domain**) 
* La class de construction de la requête envoyée au moteur de recherche
* Le pattern de la requête du moteur de recherche

**Propriétés**
- `keyConcept`* : Nom du Dt du KeyConcept
- `domainCriteria`* : Nom du domain du critère d'entrée.
- `facets`* : Liste des facettes activées dans cette recherche
- `listFilterBuilderClass`* : Nom du moteur permettant la traduction de la query (*io.vertigo.dynamox.search.DslListFilterBuilder* préconisé)
- `listFilterBuilderQuery`* : Requête de la recherche (voir syntaxe [VertigoSearchDSL])
  

```javascript
create FacetedQueryDefinition QryEquipment {
   keyConcept : DtEquipment
   facets : [FctEquipmentEquipmentTypeName, FctEquipmentPurchaseDate ]
   domainCriteria : DoLabel
   listFilterBuilderClass : "io.vertigo.dynamox.search.DslListFilterBuilder"  
   listFilterBuilderQuery : "allText:#+query*#"
}
```

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
   request : "   select    equ.EQUIPMENT_ID,
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


## Syntaxe VertigoSearchDSL

Le DslListFilterBuilder vise à construire la requete Lucene de la manière la plus intuitive pour le développeur :
Voir [Lucene QueryParser](https://lucene.apache.org/core/8_0_0/queryparser/org/apache/lucene/queryparser/classic/package-summary.html#package.description)

* L'expression subit le moins de modification possible
* Les critères sont posés en les encapsulant dans des # (Ex: #query#)
* Avec les critères de valeur null soit l'expression complète est retirée, soit le critère est remplacé par la valeur par défaut déclarée.
* Les opérateurs placés à l'intérieur des # seront reproduit pour chaque mots.
* Les critères et mots sont en `Optionel` par défaut (il faut donc préciser le caractère obligatoire des critères/mots avec le préfix `+`)
* L'utilisateur (avancé) peut surcharger le champs de recherche, rajouter des parenthèses ou changer les opérateurs (OR, AND, +, -, ...)

### Syntaxe de base

Une spécifité forte de la syntaxe de recherche est que les critères sont indépendant : il n'y a pas de notion de OR et AND comme en SQL, le principe chaque critère porte son caractère Obligatoire ou Optionel.
Ce principe est bien mieux, puisqu'il simplifie la syntaxe (surtout quand la requète est manipulée dynamiquement) et empêche l'altération des critéres système la requete par l'utilisateur.

#### Fields
* `#query#` : criteria.toString() *(A utiliser quand criteria est directement la chaine de saisie utilisateur)*
* `#myField#` : criteria.myField
* `#myField#!(myDefault)` : criteria.myField!=null?criteria.myField:myDefault

*Exemples*

* `field1:#query#` : le champ `field1` doit contenir un des mots de la query, en OR avec les autres critères
* `+field1:#query#` : idem mais ce critère est obligatoire
* `-field1:#query#` : idem mais ce critère est interdit
* `field1:#query#!(inactif)` : si le critère est null, on recherche les documents ou `field1` contient inactif<br/><br/>
* `field1:"#query#"` : le champ `field1` doit contenir la saisie exacte de la query
* `field1:#+query#` : le champ `field1` doit contenir tous les mots de la query
* `field1:#-query#` : aucun mots de la query ne doit être dans le champ `field1` de l'index 
* `+field1:(#+nom# #+prenom#)` : le champ `field1` doit contenir tous les mots du critère `NOM` et du critère `PRENOM`
* `field1:#query*#` : le champ `field1` doit avoir un mot qui commence par un des préfixes de la query
* `field1:#query#^2` : le champ `field1` à un poids de 2
* `field1:#query~2#` : le champ `field1` doit contenir un des mots de la query avec une distance de levenshtein de 2 (2 max). **Attention peu performant**.<br/><br/>
* `+field1:(#+nom*# #+prenom*#)` : le champ `field1` doit contenir des mots avec tous les préfixes du critère `NOM` et ceux du critère `PRENOM`

#### Modes d'échappements de la saisie utilisateur

Par défaut la saisie utilisateur est très échappée. Il est même permis à l'utilisateur de faire une recherche avancée en utilisant lui même la syntaxe Lucene.
Il peut ajouter des poids ou du fuzzy, faire une recherche exacte avec " ", ajouter une recherche en OR (ou AND) entre deux termes et même chercher dans un autre champ de l'index avec myOtherField:(mes mots clés).
Cette fonctionnalité est autorisée car elle ne s'adresse qu'aux utilisateurs avancés et ne permet pas de sortir du périmètre autorisée par la sécurité.

Dans tout les cas une syntaxe imcomplète saisie par l'utilisateur sera échapée : les ( ), { } ou [ ] mal fermées, ou les AND OR mal utilisés.

Le développeur peut toutefois agir sur le mode d'échappement lors de l'écriture de la requete, par l'emploi d'un suffix sur la déclaration du champ :

* `removeReserved` : Les caractères réservés sont simplement retirés (syntaxe : myField1:#+query*#removeReserved )
* `escapeReserved` : Les caractères réservés sont échappés (syntaxe : myField1:#+query*#escapeReserved )

Ceci peut être utile quand les valeurs recherchées contiennent des caractères réservés (par exemple une recherche par IP : 192.168.0.456)

> Les caractères réservés sont : 
> `+ - = & | > < ! ( ) { } [ ] ^\" ~ * ? : / OR AND`

#### Range

Les critères de type **range** reprennent la syntaxe Lucene.
Les bornes utilisent les caractères [ ou { pour indiquer le caractère inclusif.
L'étoile ``* représente l'infini
Les dates supportent le mot cléf `now` et des opérations + ou - des délais

`+date_creation:[#critDateDebut# to #critDateFin#]`: date de création comprise entre deux dates. Si un critère est null il sera remplacé par *

`+date_debut:[* to #critDateFin#} +date_fin:{#critDateDebut# to *]` : Un document avec une période d'activité est recherché sur l'intersection avec la période du critère. Dans notre exemple les bornes sont exclues

`+date_creation:[now-6M to *]`: date de création de moins de 6 mois

> Les formats de date acceptés sont : dd/MM/yyyy||strict_date_optional_time||epoch_second

#### Poids des champs :
`+(title:#query#^2 content:#query#)` : Recherche dans le titre et dans le contenu. Le titre à un poids de 2 par rapport au contenu vis à vis de la pertinence.

#### Recherche multi-mode :
`+(content:#query#^4 content:#query*#^2 contentPhonetic:#query#)` : on cherche le maximum de mot dans content avec des poids plus ou moins fort selon le cas.

#### Recherche multi-champs :
La préconisation Lucène est de créer un champs qui concatène toutes données à recherche (par exemple `nomPrenom`, `codePostalComune`, etc ...)
La propriété `indexCopyTo` de l'IndexDefinition est utilisée pour ça.

* `+_all:#+query*#` : on recherche dans tous les champs. C'est la préconsiation Lucene : on crée un champs qui concatène les champs de recherche. Ce champs est paramétrable . 
* `+[codePostal,commune]:#+query*#` : on recherche les critères dans code postal et commune.
* `+[field1,field2]:#+query*#` : Tous les prefixes de la query doivent être présent soit dans `field1` soit dans `field2`
* `+[field1^2,field2]:#+query*#` : Idem, mais le `field1` à un poids de 2

!> La recherche multichamp [field1, field2] est moins performante et inadaptée si il y a beaucoup de mots saisi par l'utilisateur (ils sont multipliés par le nombre de champ)


## Bien construire sa recherche

Une recherche utilisateur est basé sur l'assemblage entre des critères utilisateurs, **des critères systèmes de filtrage contextuel et un filtre de sécurité**

Pour avoir une meilleur accessibilité, il est préférable de proposer un comportement similaire aux recherches des sites internet grand publique (au hasard Google)
En partant du constat que :
* La recherche est un filtre, plus on donne d'infos, plus on réduit le champs des résultats. 
* Le KeyConcept indexé peut-être éclaté en plusieurs champs.
* Les mots clés fournit par l'utilisateur ne sont pas forcément dans le même champs.

### Problématique

Globalement, la recherche multifield correspond à ce qui est attendu par l'utilisateur, il veut trouver son entité quelque soit les choix de structure de l'index dont il n'a même pas connaissance.

Le problème est expliqué sur le site d'ElasticSearch [ICI](https://www.elastic.co/guide/en/elasticsearch/guide/master/multi-field-search.html)

Les techniques les plus intuitives ne donnent pas de bon résultat: 

La recherche sur différent champs, avec les mots saisis en OU :
`+(field1:#query*# field2:#query*#)` <br/>
**KO** : les mots sont en `Optionel` et des mots saisis peuvent être absent des résultats.

La recherche sur différent champs, avec les mots saisies en ET :
`+(field1:#+query*# field2:#+query*#)` <br/>
**KO** : les mots sont en `Obligatoire` et tous les mots saisis doivent être présent dans le même champs.

### Solution

#### copyTo champ custom

> Cette solution est celle préconisée

ElasticSearch propose des champs custom qui sont l'assemblage de plusieurs champs de l'index. Par exemple le champ `_all` est natif et contient tous les champs tokenizés.
Il s'agit de la préconisation Lucène en créant des champs qui concatènent toutes données à rechercher (par exemple `nomPrenom`, `codePostalCommune`, etc ...)

ElasticSearch ajoute la possibilité de configurer les champs de ce type par la fonctionalité `copy_to`. (doc ElasticSearch [ici](https://www.elastic.co/guide/en/elasticsearch/guide/master/custom-all.html))

Dans Vertigo vous devez déclarer les instructions `indexCopyTo` dans la définition de l'index. Vous indiquez que l'un des champs de l'index est la copy de un ou plusieurs autres champs de l'index. 
Cette copie est effectuée coté ElasticSearch et est plus efficace qu'une copie Java ou SQL.

Exemple de KSP : 

```Json
create IndexDefinition IdxCar {
    keyConcept : DtCar
    dtIndex : DtCar
    indexCopyTo allText { from: "make,model,description,year,kilo,price,motorType" },
    indexCopyTo modelPhonetic { from: "model" },
    loaderId : "CarSearchLoader"
}
```

Cette fonction permet de crée des champs de recherche multichamps, mais peut aussi être utilisée pour peupler des champs proposant un autre analyzer que le champ principal (pour du tri, ou du phonétique par exemple).

Pour utiliser les champs ``copy_to``, il faut que le champ existe dans le Dt de l'index et que les champs copiés dedans aient tous un indexType.
Pour cela nous préconisons d'ajouter des champs computed :
```Json
computed modelPhonetic { domain:DoPhonetic label:"model sort" expression:"throw new io.vertigo.lang.VSystemException(\"Can't use index copyTo field\");"}
computed allText { domain:DoFullText label:"index all" expression:"throw new io.vertigo.lang.VSystemException(\"Can't use index copyTo field\");"}
```

Pour l'indexType des types primitifs, nous préconisons de définir l'indexType standard : 

```Json
create Domain DoVisitCount {
    dataType: Integer
    formatter: FmtDefault
    indexType: "standard:integer"
}
```

#### Recherche multi-champs :

> Cette solution ne convient pas à tout les cas, en revanche elle peut être utilisée pour tester des évolutions de la recherche avant l'ajout d'un custom field

Le DslListFilterBuilder permet de faire une recherche sur plusieurs champs : 
`+[codePostal,commune]:#+query*#` : on recherche les critères dans code postal et commune.

Cette syntaxe est résolue par Vertigo et reproduit le mécanisme du cross-field d'ElasticSearch (mais ne l'utilise pas). En couplant ce mécanisme avec les custom field présenté ci-dessus il est possible de limiter la complexité des requêtes obtenues.

Par rapport au custom field, cette syntaxe permet un comportement différent par champs : tokenizer utilisé et poids différent.

*Exemple:*
`+[commune,annee,titre^5]:#+query*#` : L'année est bien un nombre et le titre à un poids de 5 par rapport aux autres.

!> Attention: Utiliser cette syntaxe sur une nombre limité de champs, car comme son nom l'indique elle effectue un cross-join des champs avec les mots saisies. ElasticSearch est très performant avec ce type de recherche, mais il est inutile de le pousser aux limites.

*Exemple:*  
`+[codePostal,commune]:#+query*#` 
avec les mots clés ==92350 Le plessis robinson== devient : 
```
+( +(codePostal:92350* commune:92350*) 
   +(codePostal:Le* commune:Le*) 
   +(codePostal:plessis* commune:plessis*) 
   +(codePostal:robinson* commune:robinson*) )
```

#### Recherche multi-champs (==plus simple, mais à tester==) :

Une solution à envisager est le mix des deux solutions présentées ci-dessus :
On vérifie d'abord la présence des mots clés saisies par l'utilisateur dans `_all` puis on affect le poids à certain champs en OU.

```Json
+_all:#+query*# //_all en obligatoire contient tous les mots saisis par l'utilisateur
+titre:#query*#^5 //le titre est boosté avec les mots en Optionel; il n'est pas obliger de contenir tous les termes
```


## Filtre de sécurité

Le filtre de sécurité a vocation a être conservé en session et être ajouté à chaque recherche. 
Le module de sécurité de Vertigo permet de générer le filtre dans différent langage (et notament Lucene) à partir d'une déclaration unifiée des règles de sécurité.

Il se positionne avec le code suivant :
```Java
searchQueryBuilder.withSecurityFilter(session.getSearchSecurityFilter())
```

Il correspond à une expression de recherche qui sera directement ajouté à la recherche en mode obligatoire. (avec `+()`)
La saisie utilisateur ne peut pas désactiver ce filtre : non seulement il y a des échapements, mais de plus elle est cloisonnée dans une autre sous requête.


