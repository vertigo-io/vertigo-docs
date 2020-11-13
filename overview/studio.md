# vertigo-studio

Vertigo-Studio est un outil de conception dédié aux applications métiers pour gagner en efficacité et en cohérence.

Il est utilisable à la fois par les concepteurs, chef de projets mais aussi et surtout pour les développeurs.

Cela permet à la fois d'avoir un langage commun mais également de travailler sur un support neutre éditable par tous les acteurs du projet.

Vertigo couvre à ce jour les aspects suivants de la conception d'une application :

- la modélisation des entités métiers
- les règles de sécurité (authorization/opérations)
- les manipulations de données
- les apis de webservices

Le concept principal de Vertigo-Studio est le __notebook__.
C'est en quelque sorte le cahier de notes de l'application, qui décrit son fonctionnement, ou tout du moins ses grandes lignes.
Un __notebook__ contient un ensemble de __sketch__ (ou des croquis) pour chaque type d'objet concu au sein de Studio (DtSketch, TaskSketch, FacetedQuerySkecth)

Le fonctionnement de Studio est donc le suivant :

1. Constituer un __notebook__ 
2. Utiliser ce __notebook__ pour fournir des services à valeur ajoutée

La stratégie de constitution d'un notebook se fait par lecture de multiples fichiers sources par des `Reader` spécialisés.
Chaque `Reader` va lire les fichiers sources qu'il prend en charge et enrichir le __notebook__ de nombreux __sketchs__.

A ce jour voici les principaux type de sources utilisables : 

- ksp/kpr
- oom
- xmi (EntrepriseArchitect)
- fichier json
- classes java


Parmi les services à valeurs ajoutée disponibles à partir du notebook :
 
- génération de classes Java (Entités, DAO, Search...)
- génération de script SQL
- génération de fichiers JavaScript
- génération de fichiers TypeScript
- génération de visualisation du modèle

## KSP

Pour modéliser de manière efficace une application métier et utiliser un support utilisable par les différents acteurs du projet nous avons créé une grammaire dédiée à cette problématique.
Elle est spécialement étudiée pour être à la fois :

- concise
- non ambigüe
- intuitive

D'autre part l'utilisation de fichier "texte" rend sa prise en charge native dans les outils de gestion de source. Il est alors possible de visualiser simplement les différences entre plusieurs versions, mieux collaborer à plusieurs, etc...

Afin de faciliter son adaption il est assez proche d'un format JSON mais épuré et amélioré pour nos besoins.

KSP est donc bel et bien un DSL pour Domain Specific Language, c'est à dire un langage adapté à une problématique précise : la conception des applications métiers.

Pour accompagner ce DSL et simplifier son usage nous avons créé un ecosystème d'outils pour l'intégrer aux IDE du marché :

- un **plugin Eclipse** disponible sur le marketplace eclipse [ici](https://marketplace.eclipse.org/content/vertigo-3-dsl-plugin)
- une **extension Visual Studio Code** disponible [ici](https://marketplace.visualstudio.com/items?itemName=vertigo-io.vertigo-vscode)
- un **langage-server** pour intégration dans d'autre IDE

Ces outils fournissent : 

- de la **coloration syntaxique**
- de l'**autocomplétion** et de la **verification syntaxique**
- de la vérification **grammaticale**

