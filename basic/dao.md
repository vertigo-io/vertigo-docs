# DAO

Dans les projets Vertigo, les accès aux données sont matérialiés dans des objets DAO et reposent sur l'utilisation d'un Store et de tâches.

## Store

Dans les objets DAO générés lors du MDA, des méthodes d'accès aux données sont offertes. Elles permettent depuis une API Java les manipulations suivantes :

- création
- selection par la clé primaire
- mise à jour
- suppression
- selection par critère de recherche (utilisation de l'API [Criteria](#criteria))
- manipulation des relations de type N-N

Ces méthodes permettent une manipulation du stockage directement depuis une API Java et sont donc facilement utilisables par un développeur. Elles permettent de faire une grande partie des intéractions avec le stockage moyennant un effort très faible.

Voici un exemple d'utilisation de la méthode de selection par clé primaire :

```java
@Override
public Movie getMovieById(final Long movId) {
	Assertion.checkNotNull(movId);
	// ---
	return movieDAO.get(movId);
}
```


?> Les méthodes qui sont offertes sont limitées à la manipulation d'une seule entité métier car c'est l'assurance de bonnes performances. La maîtrise des performances étant primordiale pour un système opérationnel, nous conseillons l'utilisation du store dans les cas simples et d'utiliser une [tâche](#tâches) dédiée dans les cas plus complexes, notamment lorsque plusieurs entités sont concernées.

!> Il est important de toujours privilégier les manipulations de données ensemblistes (selection et modification) et d'éviter les appels unitaires multiples qui ont un coût en performances important et non-maitrisé. L'atelier DAO détaillé [ici](/guide/samples_dao) permet, au travers d'exercices, de maitriser l'accès aux données dans une application Vertigo.


## Criteria

L'API offre les fonctionnalités suivantes en proposant des recherches de type :

- Null/Non null (Null/Not null)
- Egal/Non égal (Equals/Not equals)
- Commence par (StartsWith)
- Supérieur/Supérieur ou égal/Inférieur/Inférieur ou égal (GreaterThan/LowerThan)
- Entre (Between)
- Parmi (In)

D'autre part, elle permet l’enchaînement de clauses *et* et *ou* de manière fluide.

Un "criteria" est construit de la manière suivante :

```java
final Criteria<Movie> criteria = Criterions.startsWith(MovieFields.name, title)
						  .and(Criterions.isEqualTo(MovieFields.year, year));
```

et s'utilise directement depuis un objet DAO :

```java
movieDAO.findAll(criteria, 500);
```


## Tâches

Lorsque les manipulations vers la base de données sont plus complexes, il est préférable de passer par une requête native au dispositif de stockage. Les tâches permettent de réaliser ces manipulations.

Une tâche (Task) permet d'abstraire le concept de manipulation des données quel que soit l'élément technique sous-jacent. Elle est définie par :

- un nom
- un moteur d'exécution :  `className`
- une requête : fournissant le traitement à effectuer
- des paramètres d'entrée
- un paramètre de sortie optionel

Une tâche est créée en la déclarant dans un fichier KSP.

### Moteur d'exécution

Vertigo embarque un certain nombre de moteurs d'exécution. De par la nature des applications construites avec Vertigo, ces moteurs sont concus pour l'ex&cution de requêtes SQL. En voici les principaux :

- `io.vertigo.basics.task.TaskEngineSelect`: permet de faire une selection de données dans une base de données relationelle en SQL (requête de type *select*)
- `io.vertigo.basics.task.TaskEngineProc`: permet de faire une manipulation de données dans une base de données relationelle en SQL (requêtes de type *update* et *delete*)
- `io.vertigo.basics.task.TaskEngineProcBatch`: permet de faire une requête de type batch avec un paramètre d'entrée de type `DtList`


### Paramètres

Les paramètres d'une tâche sont définis par :

- s'il s'agit d'un paramètre d'entrée ou de sortie
- un nom : utilisable dans la requête sous forme de paramètre bindé
- un domain : permet de préciser son type (au sens Vertigo). Pour les objets il existe le *domain* suivant Do*NomObjet*
- la cardinalité associée au paramètre (`1`, `?` ou `*`)

### Requête

La requête est un champ texte qui contient le traitement à effectuer.

Ce champ permet l'utilisation des paramètres d'entrées sous forme de paramètres bindés à l'aide de la syntaxe suivante : 

- *#nomParametrePrimitif#* : pour un paramètre primitif
- *#nomParametrePrimitif.rownum#* : pour un paramètre de type liste de primitif et utilisation d'un champ dans le cadre des requêtes de type batch 

- *#nomParametre.champ#* : pour un paramètre de type objet et utilisation d'un champ
- *#nomParametreList.index.champ#* : pour un paramètre de type liste d'objet et utilisation d'un champ (*à utiliser pour les clauses de type Where IN(...)*)
- *#nomParametreList.champ#* : pour un paramètre de type liste et utilisation d'un champ dans le cadre des requêtes de type batch 

D'autre part, il est également possible d'apporter du dynamisme dans les requêtes avec l'utilisation de la syntaxe `<%><%>` qui permet d'intercaler du code Java qui sera interprété à l'exécution. Ceci est notamment utilisé afin d'activer ou désactiver des parties de requêtes.

```
 create Task TkGetMoviesByCriteria {
    className : "io.vertigo.basics.task.TaskEngineSelect"
        request : "
        	select mov.*
        	from movie mov
        	where 
        	1=1
        	<%if(title != null) {%>
        	 and mov.NAME like concat(#title#, '%%')
        	<%}%>
        	<%if(year != null) {%>
        	 and mov.YEAR = #year#
        	<%}%>
			"
	in title	 	{domain : DoLabelLong 		cardinality:"1" 	}
	in year	 		{domain : DoYear 			cardinality:"1" 	}
	out movies		{domain : DoDtMovie	 		cardinality:"*" 	}
}
```


Pour plus de détails sur l'utilisation de ces syntaxes, un [atelier](/guide/samples_dao) complet est disponible.

### Exemple d'échappement

Pour échapper un caractère comme le `"`, vous pouvez utiliser `\`

Exemple souvant utilisé pour passer la clause de sécurité : 

`where ass.usr_Id = #usrId# and <%=securedAssignement.asSqlWhere(\"ass\", ctx)%>`


### Exemple de TaskEngineSelect
Voici un exemple de déclaration de tâche permettant de récupérer une liste d'acteurs ayant participé à un film. 

```
create Task TkGetActorsInMovie {
    className : "io.vertigo.basics.task.TaskEngineSelect"
        request : "
        	select act.*
        	from role rol
        	join actor act on act.ACT_ID = rol.ACT_ID
        	where rol.MOV_ID = #movId#
			"
	in 	movId		{domain : DoId 				cardinality:"1" 	}
	out actors		{domain : DoDtActor 		cardinality:"*"		}
}

```
Une fois cette tâche déclarée et le générateur executé, une nouvelle méthode est disponible dans le DAO associé. Les tâches sont placées dans le DAO de l'objet concerné par les paramètres (en sortie ou en entrée) lorsqu'il n'y a pas ambiguité ou dans un PAO (Package Access Object) dans le cas contraire.

```java
public io.vertigo.dynamo.domain.model.DtList<io.vertigo.samples.dao.domain.Actor> getActorsInMovie(final Long movId) {
		final Task task = createTaskBuilder("TkGetActorsInMovie")
				.addValue("movId", movId)
				.build();
		return getTaskManager()
				.execute(task)
				.getResult();
}
```
Cette tâche est dès lors appelable très simplement par un service métier par l'intermédiaire de ce DAO.

```java
@Override
public DtList<Actor> getActorsByMovie2(final Long movId) {
	return actorDAO.getActorsInMovie(movId);
}
```

### Exemple de TaskEngineProcBatch

Avec un taskEngine de type TaskEngineProcBatch, il est possible d'appliquer les champs des éléments de la liste ligne par ligne pour faire des mises à jour ensembliste.

Comme ceci :
```
create Task TkUpdateActorsNameBatch {
    className : "io.vertigo.basics.task.TaskEngineProcBatch"
        request : "
        	UPDATE actor
        	SET name = #actors.name#
            WHERE act_id = #actors.actId#;
			"
	int actors		{domain : DoDtActor 		cardinality:"*"		}
    out intSqlRowcount  {domain : DoNumber      cardinality: "1" }
}
```

Cet exemple est fictif, dans beaucoup de cas il est plus simple de passer par le DAO de l'entité et sa méthode `updateList(final DtList<E> entities)`.
