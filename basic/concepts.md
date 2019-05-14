# Glossaire / Concepts Vertigo

Voici une liste des concepts clés, fondateurs, qui sont nécessaires à avoir en tête pour bien débuter avec **Vertigo**.


## Core

### Module *(concept)*

Les `Modules` représentent un concept de découpage du code applicatif ou technique. C'est un regroupement cohérent d'un ensemble de services, d'objets et d'implémentations autour d'une notion plus large qui fait sens.
Les `Modules` ont une granularité raisonnées pour une bonne maitrise des dépendances, à la fois en terme de point d'entrée (dépendances entre API) qu'en terme d'orientation. 
Par exemple : `Dynamo` module autour de la gestion et le stockage de la données. `Vega` module autour de la gestion de WebService. `Studio` module autour de l'outilage projet de la gestion du developpement (dont le MDA).

### Extension *(concept)*

Les `Extensions` est un concept de module particulier, clé en main et optionnel. Les `Extensions` ont vocations à proposer une fonctionalité de complète en verticale (de l'IHM au stockage) ajoutable à l'application avec le minimum d'effort.

### Component *(interface)*

Les `Components` au sens **Vertigo** représentent tout les objets gérés par l'injection de dépendance **Vertigo**. 
Les composants sont des singletons au niveau applicatif, et on donc vocation à rester sans état (*StateLess*). 
C'est juste un marqueur déclaratif.

### Manager *(interface)*

Les `Managers` sont des `Components`. Ils représentent des facades de service de haut niveau pour des traitements transverses ou technique. 
C'est essentiellement des APIs avec une forte contrainte de **DX** (*Developpers Experience*) : simples à utiliser et à comprendre, centrées sur les cas d'usages métiers.
Exemple : SearchManager, NotificationManager, ...

### Plugin *(interface)*

Les `Plugin` sont des `Components` également, ils ont vocactions a être liés et utilisé uniquement par un `Manager`. 
Ils représentent les options d'implémentation d'un besoin particulier nécessaire pour rendre le service de leur `Manager`.
Ils permettent de systématiser le découplage entre le coeur applicatif et les dépendances tierces nécessaires. 
Ce principe assure le coté pérenne et stable des applications : l'évolution ou le remplacement d'une librairie tierce est absorbé par le plugin concerné.

### Definition *(interface)*

Les `Definitions` répresentent les porteurs d'informations. Là où les `Managers` portent les traitements, les `Definitions` portent la description des données.
De manière générale tout élément qui sert à établir le modèle (*tout ce qui tourne autour des données*) est porté par une `Definition`.
Les `Definitions` servent **à modéliser** le métier. Elles sont uniques, chargées aux démarrage du serveur et imutables. 

### VUserException, VSystemException, WrappedException *(class)*

Dans son approche *Opinionated Architecture* **Vertigo** la gestion des exceptions dans les applications **Vertigo** est basée sur des exceptions `Un-checked` (faiblement typées). 
Globalement dans une application les `Exceptions` n'ont jamais a être interceptées par le développeur, le socle s'occupe de tout.

Trois types sont utilisés : 

- `VUserException` : Pour les exceptions correspondant à une règle métier (contrôle de surface, validation ou règle de gestion). L'exception est associé à un message et éventuellement un champ de l'écran et sera présenté à l'utilisateur en lui indiquant se qui s'est passé.


## Dynamo

### DtObject *(interface)*

Les `DtObject` sont l'un des objets le plus important de la gestion des données dans **Vertigo**. 
Il représente l'objet de transfert des données, il est transverse à toutes les couches (de l'IHM à la base de données) et permet une simplification de l'application en évitant de nombreuses copies et conversions.
Les objets concrets implémentant `DtObject` sont des POJOs avec annotations et peuvent être crées à la main ou générés grace au module `Studio`.

### Entity *(interface)*

Les `Entity` sont des `DtObject` persistant. Ils possèdent un identifiant.

### KeyConcept *(interface)*

Les `KeyConcept` sont des `Entity` clés de l'application. Cette interface est un marqueur aidant à la compréhension et la maitrise de l'application sur la durée en identifiant les objets métiers principaux. 
Les APIs **Vertigo** utilisent cette notion pour guider les développeurs.

### DtList *(interface)*

Les `KeyConcept` sont des **listes typées** de `DtObject`. Permet de compenser l'absence de liste fortement typée en Java. 

### Domain *(concept)*

Les `Domain` sont le permier niveau de déclaration du modèle, a ce titre ils sont des `Definitions`. 
Ils représentent un *super-type*, c'est un typage fort de la donnée enrichit par des méta-données pour découpler ses possibilités.
Globalement un `Domain` a un type Java simple, porte une validation (avec une liste de contraintes), un formatteur et des méta-données complémentaires : le type de stockage SQL, la taille du champs d'affichage, l'unité pour les quantités, etc...

Dans `Vertigo` le `Domain` remplace la notion de type Java dans les déclarations, ainsi la déclaration des entrées/sorties dans les `Tasks` (voir ci-dessous) utilise la notion de `Domain`.
Toutefois dans le code Java, c'est bien le type Java qui est utilisé (Par exemple une `String` pour un `Domain` *SIRET*)

### Constraint *(interface)*

Les `Constraints` représentent les contrôles associés à un `Domain`. `Vertigo` propose de base de nombreuses `Constraints` standard et il est très simple d'en ajouter. Les `Contraints` standards peuvent des paramètres pour adapter leur comportements ou changer le message d'erreur.
Les `Constraints` sont appliqués et validés automatiquement lorsque des données saisies par les utilisateurs sont intégrés dans le système (ie : sur les données saisies). Il est possible de forcer une validation des contraintes.
En général, une violation de contrainte génère une exception utilisateur.


### Formatter *(interface)*

Les `Formatters` sont des convertisseurs associés à un `Domain`. Ils permettent de transformer une donnée de son format typé de manipulation dans les services Java en chaine de caractère utilisée par l'utilisateur. Les `Formatters` sont biderectionnels et sont souvant plus permissif lors de la traduction de la saisie utilisateur vers le type technique (une date peut être saisie 10/01/2019 ou 10/01/19 ou 10/1/19 ou 10 01 19).
Dans l'ensemble ils sont utilisés (*automatiquement*) lors des communications avec l'IHM ou dans les exports de données.


### Task *(concept)*

Les `Task` sont des définitions, elles représentent les points d'accès à une source de données. Elles sont constitués de paramètres d'entrées et de sorties, d'une requete et d'un moteur d'exécution. 
De base, le moteur le plus souvant utilisé est celui permettant d'exécuter des requètes SQL. 
C'est le cas d'usage le plus courant des `Tasks`, elles sont utilisées pour déclarer des requêtes SQL spécifiques utilisées dans l'application.
Par ce mecanisme **Vertigo** pousse une utilisation efficace et maitrisée des accès à la base de données : les accès simples (c-a-d sans risques opérationnels, typiquement CRUD avec ou sans critères) sont automatisées, les accès complexes (avec jointures, ou comportement spécifiques) sont externalisés dans un fichier de resource en syntaxe SQL native pour une maitrise complète du comportement. 


### @Transactional *(annotation)*

`@Transactional` est l'une des annotations proposées par **Vertigo**, elle est présentée ici car elle est d'une importance capitale dans les applications de gestion. 
Comme son nom l'indique est ajoute le caractère transactionel sur une méthode (par un principe d'*AOP*).
Elle a vocation a être positionnée sur les facades de services, elle se comporte comme étant **REQUIRES_NEW**, c'est à dire l'annotation assure qu'une transaction est présente, s'il n'y a pas on en crée une, s'il y en a déjà une on la réutilise.

## Studio 

### MDA : Model Driven Architecture *(concept)*

La notion de `MDA' (pour *Model Driven Architecture*) décrit le fait de partir de la déclaration données comme structure portante de l'application. 
**Vertigo** guide le développement vers une approche de ce type, la structure déclarative du **Model** (ce qui touche aux données) supporte le reste de l'application : la séparation en modules (découpage fonctionnel) et en couches (découpage technique).
**Vertigo** propose un module de génération de code qui permet de mettre en pratique ce principe de manière rapide, homogène et reproductible : le code généré n'est pas modifié par le développeur, il est toujours maintenu cohérent avec la déclaration du modèle. 
