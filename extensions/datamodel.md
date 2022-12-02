# DataModel

**DataModel** est un module central des extensions Vertigo permettant de partager des concepts communs de Data Transfert Object et de ce qui tourne autour.

Ce module est fortement basés sur des définitions qui ont vocation à être transverse.

Il inclut :

- de nombreuses définitions liés à la couche domain :
	- DtDefinition
	- Contraint
	- Formatter
	- Association
	- Task

- des concepts/API transverses :
	- UID
	- DtObject, DtList
	- MasterData, StaticMasterData
	- KeyConcept, Fragment
	- SmartType, Adapter
	- Criteria


## Utilisation via Studio

Une majorité des concepts de ce module peuvent être généré via l'outil Studio.
Les générateurts suivant sont liés à ce module :

- `vertigo.domain.java`: génère les class Java des DtObject
- `vertigo.domain.java.targetSubDir`: présise le répertoire de génération (par défaut *~/javagen*)
- `vertigo.domain.java.generateDtResources`: génère les fichiers .properties pour utiliser le i18n avec les libellés des champs des DtObjects
- `vertigo.domain.sql`: génère le fichier crebase.sql qui permet de regénérer la structure de la base
- `vertigo.domain.sql.targetSubDir`: présise le répertoire de génération du fichier sql
- `vertigo.domain.sql.baseCible`: Type de la base *(pour les syntaxes spécifiques)*
- `vertigo.domain.sql.generateDrop`: génère les drop dans le script crebase.sql
- `vertigo.domain.sql.generateMasterData`: génère les scripts de remplissage des données de référence par défaut
- `vertigo.task`: génère les class Java des tâchs d'accçs au données..
- `mermaid`: génère un fichier HTML permettant de visualiser le modèle de données graphiquement *(lib mermaid)*


### Syntaxe KSP

__Généralités__
```json
create <<type>> <<nom>> {
    <<corps de la déclaration>>
```
Permet de déclarer une nouvelle définition.


```json
alter <<type>> <<nom>> {
    <<corps de la déclaration>>
```
Permet de modifier/compléter une nouvelle définition.


__DtDefinition__
```json
create DtDefinition DtUsager {
    id usaId {domain: DoId label:"Id" cardinality:"1"}
    field email {domain: DoEmail label:"E-mail" }
}
```
- `field` : déclare le champ de l'objet.
	- `domain` : indique le `Domain` du champ. Ce domain pointe sur un SmartType du projet.
	- `label` : indique le libellé par défaut du champ.
	- `cardinality` : indique la cardinalité du champ (`?`:0-1, `1`: obligatoire, `*`:multiple)
- `id` : précise que l'objet est une entité (persistante), et que ce champ correspond à la PK *(Note: dans Vertigo, il n'y a pas de PK multiple, sauf les tables d'association NN)*

__StereoType__
```json
create DtDefinition DtReservation {
    stereotype: "KeyConcept"
	...
}
```
- `stereotype` : précise que l'objet est taggé spécifiquement. Valeurs possible : 
  -	`ValueObject`: //By default
  - `MasterData` : Liste de référence
  - `StaticMasterData` : Liste de référence static
  - `KeyConcept` : Concept clé
  - `Entity` : Entité (élément persistant)
  - `Fragment` : Sous partie extraite d'une entité

__StaticMasterData__
```json
create DtDefinition DtBaseType {
	stereotype : "StaticMasterData"
	id baseTypeId {domain: DoCode label:"Id"}
	field label {domain: DoLabel label:"Base Type Label" }	
	values : `{ "hydro" : 		{ "baseTypeId" : "HYDRO",  		"label" : "Hydroponic"},
				"mine" : 		{ "baseTypeId" : "MINE", 		"label" : "Mining Complex" },
        		"dwelling" : 	{ "baseTypeId" : "DWELLING", 	"label" : "Dwelling Complex"} }`
}
```
Les StaticMasterData sont un cas particulier de liste de référence, ou les valeurs sont figées.
Le générateur propose alors un script sql d'insertion des données en BDD, et une enum listant les valeurs.

*Note* : L'id d'une StaticMasterData est forcément de type String. En effet les StaticMasterData ont vocation a être utilisable directement dans les requetes sans faire de jointure, il faut alors que le code (qu'on retrouve dans les FK) soient "à peu près" signifiant.
Par exemple les dossiers encours : 
```sql select * from dossier dos where dos.ETA_CD = 'ENCOU'```


__SmartTypes__
```json
create Domain DoVisitCount {
    dataType: Integer
	storeType : "NUMERIC"
}
```
- `dataType` : Type Java de la donnée
- `storeType` : Type de stockage SQL de la donnée *(dépend de la BDD)*

Pour assurer la cohérence des déclarations, il est nécessaire de déclarer les smartTypes utilisés par les DtDefinition et les Task.
Cette déclaration n'entraine pas de génération, les SmartTypes doivent être aussi déclarés en Java avec l'ensemble des informations portées par le SmartType, dans le KSP on ne met que ce qui est nécessaire à la génération des autres objets.


**Note** : le terme Domain et le préfix Do sont historiques et font référence à une ancienne notion des bases de données. Dans le reste de Vertigo cette notion a été renommée en SmartType, mais comme vous le voyez il reste des traces du passé ici où là :)

__SmartTypes : ValueObjet__
```json
create Domain DoFormulaire {
	dataType : ValueObject
	type : "fr.gouv.interieur.rdvpref.support.smarttypes.FormulaireDemarche"
	storeType : "JSONB"
}
```
- `dataType: ValueObject` : Indique que la donnée représente un Objet, il sera convertit en type primitif par des `Adapater` correspondant aux différents cas d'usages (sql, ui, ...)
- `type` : Objet Java de la donnée
- `storeType` : Type de stockage SQL de la donnée *(dépend de la BDD)*





