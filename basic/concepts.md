# Glossaire / Concepts Vertigo

Voici une liste des concepts clés, fondateurs, qui sont nécessaires à avoir en tête pour bien débuter avec **Vertigo**.


## Core

### Module *(concept)*

Les `Modules` représentent un concept de découpage du code applicatif ou technique. C'est un regroupement cohérent d'un ensemble de services, d'objets et d'implémentations autour d'une notion plus large qui fait sens.
Les `Modules` ont une granularité raisonnée pour une bonne maîtrise des dépendances, à la fois en matière de point d'entrée (dépendances entre API) qu'en matière d'orientation. 
Par exemple : `Dynamo` module autour de la gestion et le stockage de la données. `Vega` module autour de la gestion de WebService. `Studio` module autour de l'outilage projet de la gestion du developpement (dont le MDA).

### Extension *(concept)*

Les `Extensions` sont un concept de module particulier, clé en main et optionnel. Les `Extensions` ont vocation à proposer une fonctionalité complète en vertical (de l'IHM au stockage), ajoutable à l'application avec le minimum d'efforts.

### Component *(interface)*

Les `Components` au sens **Vertigo** représentent tous les objets gérés par l'injection de dépendances **Vertigo**. 
Les composants sont des singletons au niveau applicatif et ont donc vocation à rester sans état (*StateLess*). 
Il s'agit juste d'un marqueur déclaratif.

### Manager *(interface)*

Les `Managers` sont des `Components`. Ils représentent des facades de service de haut niveau pour des traitements transverses ou technique. 
C'est essentiellement des APIs avec une forte contrainte de **DX** (*Developpers Experience*) : simples à utiliser et à comprendre, centrées sur les cas d'usage métier.
Exemple : SearchManager, NotificationManager, ...

### Plugin *(interface)*

Les `Plugins` sont des `Components` également, ils ont vocaction à être liés et utilisés uniquement par un `Manager`. 
Ils représentent les options d'implémentation d'un besoin particulier, nécessaires pour rendre le service de leur `Manager`.
Ils permettent de systématiser le découplage entre le coeur applicatif et les dépendances tierces nécessaires. 
Ce principe assure le côté pérenne et stable des applications : l'évolution ou le remplacement d'une bibliothèque tierce est absorbé par le plugin concerné.

### Connector *(interface)*

Les `Connectors` sont des `Components` également, ils ont vocaction à être liés et utilisés  soit par des `Plugins` soit par d'autre composants. 
Ils permettent de configurer et d'accèder sans API intermédiaire aux clients de librairies / produits tiers.
Les `Plugins` natifs dans Vertigo utilisent des `Connectors` quand ils s'appuient sur une librairie ou un produit tiers. Ces connecteurs peuvent alors être reutilisés directement par le développeur de l'application en cas de besoin impératif.

### Definition *(interface)*

Les `Definitions` répresentent les porteurs d'informations. Là où les `Managers` portent les traitements, les `Definitions` portent la description des données.
De manière générale, tout élément qui sert à établir le modèle (*tout ce qui tourne autour des données*) est porté par une `Definition`.
Les `Definitions` servent **à modéliser** le métier. Elles sont uniques, chargées au démarrage du serveur et immuables. 

### BasicType *(concept)*

L'intégralité des modules Vertigo gère un nombre fini de type de données. Il s'agit de types primaires (basiques).
Il s'agit donc du dénominateur commun, ce qui permet d'assurer une **compatibilité totale** des types de données complets entre tous les modules Vertigo.

### VUserException, VSystemException, WrappedException *(class)*

Dans son approche *Opinionated Architecture*, **Vertigo** propose une gestion des exceptions dans les applications basée sur des exceptions `Un-checked` (Runtime et faiblement typées). 
Globalement, dans une application, les `Exceptions` n'ont jamais à être interceptées par le développeur, le socle s'occupe de tout, il inclut déjà les interceptions nécessaires aux endroits clés.

Trois types sont utilisés : 

- `VUserException` : Pour les exceptions correspondant à une règle métier (contrôle de surface, validation ou règle de gestion). L'exception est associée à un message et éventuellement un champ de l'écran et sera présentée à l'utilisateur en lui indiquant ce qui s'est passé.
- `VSystemException` : Pour les exceptions correspondant à une erreur système (Assertions, erreurs I/O, etc...) 
- `WrappedException` : Pour l'encapsulation d'exceptions techniques, permet d'encapsuler une erreur technique tierce afin de la laisser remonter jusqu'à l'interception Vertigo.  

## Data-Model

### SmartType *(concept)*

Les `SmartType` sont le permier niveau de déclaration du modèle et à ce titre sont des `Definitions`. 
Ils représentent un *super-type*, c'est un typage fort de la donnée, enrichi par des métadonnées pour décupler ses possibilités.
Globalement, un `SmartType` possède : un type Java, porte une validation (avec une liste de contraintes), un formatteur et des adapteurs, et des métadonnées complémentaires : le type de stockage SQL, la taille du champ d'affichage, l'unité pour les quantités, etc...

Les `SmartType` définissent des `Adapter` afin de transformer de manière bi-directionnelle la donnée vers un `BasicType` (exemple : un POJO avec différentes propriétés peut etre transformé vers le `BasicType` **String** via une serialisation JSON)

Dans `Vertigo` le `SmartType` remplace la notion de type Java dans les déclarations, ainsi la déclaration des entrées/sorties dans les `Tasks` (voir ci-dessous) utilise la notion de `SmartType`.
Toutefois, dans le code Java, c'est bien le type Java qui est utilisé (Par exemple une `String` pour un `Domain` *SIRET*).

### DtObject *(interface)*

Le `DtObject` est l'un des objets les plus importants de la gestion des données dans **Vertigo**. 
Il représente l'objet de transfert des données, est transverse à toutes les couches (de l'IHM à la base de données) et permet une simplification de l'application en évitant de nombreuses copies et conversions.
Les objets concrets implémentant `DtObject` sont des POJOs avec annotations et peuvent être créés à la main ou générés grâce au module `Studio`.

### Entity *(interface)*

Les `Entity` sont des `DtObject` persistants. Elless possèdent un identifiant.

### KeyConcept *(interface)*

Les `KeyConcept` sont des `Entity` clés de l'application. Cette interface est un marqueur aidant à la compréhension et à la maitrise de l'application sur la durée, en identifiant les objets métier principaux.
Les APIs **Vertigo** utilisent cette notion pour guider les développeurs.

### DtList *(interface)*

Les `DtList` sont des **listes typées** de `DtObject`. Cette interface permet de compenser l'absence de liste fortement typée en Java. 



### Constraint *(interface)*

Les `Constraints` représentent les contrôles associés à un `SmartType`. `Vertigo` propose de base de nombreuses `Constraints` standard et il est très simple d'en ajouter. Les `Contraints` standards peuvent posséder des paramètres pour adapter leur comportement ou changer le message d'erreur.
Les `Constraints` sont appliquées et validées automatiquement lorsque des données saisies par les utilisateurs sont intégrées dans le système (ie : sur les données saisies). Il est possible de forcer une validation des contraintes.
En général, une violation de contrainte génère une exception utilisateur.


### Formatter *(interface)*

Les `Formatters` sont des convertisseurs associés à un `SmartType`. Ils permettent de transformer une donnée depuis son format typé de manipulation dans les services Java en chaîne de caractères manipulée par l'utilisateur. Les `Formatters` sont biderectionnels et sont souvent plus permissifs lors de la traduction de la saisie utilisateur vers le type technique (une date peut être saisie 10/01/2019 ou 10/01/19 ou 10/1/19 ou 10 01 19).
Dans l'ensemble, ils sont utilisés (*automatiquement*) lors des communications avec l'IHM ou dans les exports de données.


### Task *(concept)*

Les `Task` sont des définitions, elles représentent les points d'accès à une source de données. Elles sont constituées de paramètres d'entrée et de sortie, d'une requete et d'un moteur d'exécution.
De base, le moteur le plus souvent utilisé est celui permettant d'exécuter des requètes SQL. 
C'est le cas d'usage le plus courant des `Tasks`, elles sont utilisées pour déclarer des requêtes SQL spécifiques utilisées dans l'application.
Par ce mecanisme, **Vertigo** favorise une utilisation efficace et maîtrisée des accès à la base de données : les accès simples (c'est-à-dire sans risque opérationnel, typiquement CRUD avec ou sans critères) sont automatisés, les accès complexes (avec jointures, ou comportement spécifiques) sont externalisés dans un fichier de resource en syntaxe SQL native pour une maîtrise complète du comportement.


### @Transactional *(annotation)*

`@Transactional` est l'une des annotations proposées par **Vertigo**. Elle est présentée ici car elle est d'une importance capitale dans les applications de gestion. 
Comme son nom l'indique, elle ajoute le caractère transactionel sur une méthode (par un principe d'*AOP*).
Elle a vocation a être positionnée sur les façades de services et se comporte comme étant **REQUIRES_NEW**, c'est à dire que l'annotation s'assure qu'une transaction est présente : s'il n'y en a pas encore, on en crée une, s'il y en a déjà une, on la réutilise.

## Studio 

### MDA : Model Driven Architecture *(concept)*

La notion de `MDA' (pour *Model Driven Architecture*) décrit le fait de partir de la déclaration des données comme structure portante de l'application. 
**Vertigo** guide les développements vers une approche de ce type, la structure déclarative du **Model** (ce qui touche aux données) soutient le reste de l'application : la séparation en modules (découpage fonctionnel) et en couches (découpage technique).
**Vertigo** propose un module de génération de code qui permet de mettre en pratique ce principe de manière rapide, homogène et reproductible : le code généré n'est pas modifié par le développeur, il est toujours maintenu cohérent avec la déclaration du modèle. 

### Domain *(concept)*

Les domains permettent dans Studio de déclarer les types de données utilisables dans une application.
Il existe deux types de `Domain` ceux s'appuyant sur un `BasicType` et ceux utilisant toute autre classe Java (préférablement une classe de type *ValueObject*)
Les `Domain` possèdent également d'autre propriétés utiles pour compléter sa définition.

### KSP *(fichier)*

Les fichiers KSP sont des fichiers texte permettant aux développeurs de concevoir son application et d'y déclarer la définition du **Model**. Ces fichiers sont auto-suffisants mais le modèle de donnée peut également être complété par des fichiers issus d'outils de modélisation tiers (OOM ou XMI).
Les fichiers KSP reprennent une syntaxe proche du Json afin de rester lisible et flexible, y compris par quelqu'un d'externe au projet ou non développeur comme le chef de projet, ou un DBA.
Globalement ils permettent de déclarer toutes les définitions de Vertigo.

Les éléments du **Modèle** le plus souvant déclarés en fichier *KSP* sont :

- Domain
- DtObject : les objets non persistés comme les objets d'IHM, les autres sont plutôt dans le modèle de données (OOM ou XMI)
- Task : Les requêtes SQL restent ainsi hors du code, indentées correctement et lisibles.

### KPR *(fichier)*

Les fichiers KPR sont des fichiers texte permettant de référencer d'autres fichiers KPR ou KSP. Ceux-ci permettent de maitriser le découpage des fichiers KSP.
