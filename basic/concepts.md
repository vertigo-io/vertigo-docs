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

### Domain *(class)*

Les `Domain` sont le permier niveau de déclaration du modèle, a ce titre ils sont des `Definitions`. 
Ils représentent un *super-type*, c'est un typage fort de la donnée enrichit par des méta-données pour découpler ses possibilités.
Globalement un `Domain` a un type Java simple, porte une validation (avec une liste de contraintes), un formatteur et des méta-données complémentaires : le type de stockage SQL, la taille du champs d'affichage, l'unité pour les quantités, etc...

Dans `Vertigo` le `Domain` remplace la notion de type Java dans les déclarations, ainsi la déclaration des entrées/sorties dans les `Tasks` (voir ci-dessous) utilise la notion de `Domain`.
Toutefois dans le code Java, c'est bien le type Java qui est utilisé (Par exemple une `String` pour un `Domain` *SIRET*)

### Constraint

### Formatter

### Task

## Autres concepts 

### MDA : Model Driven Architecture
