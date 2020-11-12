# Core

Vertigo-core est le mini framework qui permet de faire fonctionner une application Vertigo.
Il est très léger, très robuste mais a tout d'un grand, sa conception étant le fruit de plusieurs décennies d'efforts.

Ses missions pour une application Vertigo sont :

- **Configure** : décrit ce qu'elle fait et comment elle le fait
- **Run** : démarre l'application et l'arrête
- **Monitor** : recueille des statistiques permettant d'évaluer son état à tout instant

Pour faire cela une application est consituée de deux espaces distincts :
- **ComponentSpace** : l'espace des composants, ce qui correspond aux traitements (des fonctions mathématiques pures et sans état)
- **DefinitionSpace** : l'espace des définitions, ce qui correspond aux informations immuables qui décrivent les éléments manipulés par l'application.

Le cycle de démarrage a donc pour but de remplir ces deux espaces. Une fois l'application démarrée ces deux espaces sont vérouillés (ils ne peuvent plus être modifiés), l'état de l'application ne peut plus altéré.
Il en resulte une application robuste, dont le comportement est reproductible, sans effet de bord, en un mot __fiable__.

## Configuration

Dans le concept de configuration nous avons fait le choix de différentier la configuration __structurelle__ d'une application (ce qu'elle fait) de son paramètrage (qui influence comment elle fonctionne).
Ainsi la configuration d'une application Vertigo se fait via deux moyens très différents :

- la configuration : qui liste les modules de l'application et pour chaque modules les fonctionnalités activées (selon deux modalités : fichier YAML ou API Java)
- le parametrage : qui fournit des valeurs de paramètres nommés utilisés par les composants. (la fourniture des valeurs de paramètre peut se faire par autant de modalités que nésessaire via des plugins dédiés)

La configuration de l'application est donc par nature immuable, ce qui n'est pas le cas des paramètres qui peuvent avoir leur propre stratégie.

Une application est constituée de modules, chacun apportant à la fois ses __définitions__ et ses __composants__.

## Run

En partant de la configuration et du paramètrage d'une application il est dès lors possible de créer un noeud d'éxecution (Node).
Le cycle de démarrage est le suivant :

1. Création de l'ensemble des composants : module par module et en utilisant un mécanisme d'inversion du contrôle pour résoudre les dépendances entre composants
2. Vérouillage de l'espace des composants (aucun nouveau composant ne peut etre enregistré)
3. Enregistrerment de l'ensemble des définitions : module par module via les DefinitionProvider, les composants eux-même pouvant être des DefinitionProvider
4. Vérouillage de l'espace des définitions (aucune nouvelle définition ne peut être enregistrée)
5. Démarrage de l'ensemble des composants : appel de la méthode start() des composants activables, ils ont alors accès à l'espace des définitions
(5.bis Création des composants éphémères _Initializer_ pour certains besoins)
6. Executions de fonctions de pré-activation enregistrées pendant le démarrage des composants.

A l'issue de ce cycle de démarrage le _Node_ est prêt, et l'ensemble de ses fonctionnalités sont utilisables via ses composants.

Lors de l'arret du noeud de l'application, l'ensemble des composants sont arretés dans l'ordre inverse de leur démarrage.

D'autre part Vertigo-Core fournit un environnement d'execution dédié aux démons (Daemons en anglais), au sens tache récurrente technique, par le biais du DaemonManager. Pour enregistrer un nouveau démon il suffit de créer la une `DaemonDefinition`.
Une manière simplifiée consiste à ajouter l'annotation `@DaemonScheduled` sur une méthode publique d'un composant enregistré dans le ComponentSpace.

## Monitor

Une fois une application démarée il important de suivre son activité et ses performances.
Un module d'analytics est nativement présent dans Vertigo pour permettre un suivi fin des traitements qui son effectués.
Il permet de suivre trois types d'indicateurs :

- **HealthStatus** : Permet d'indiquer un état de santé (rouge, orange, vert) pour une fonction précise
- **AProcess** : Permet de tracer des executions complètes au sein de l'application en passant par différents point de contrôle. Cela permet notament de compter la nature et la durée des différents processus?
- **Metric** : Permet de relever des métriques a interval de temps régulier pour suivre l'évolution dans le temps d'une caractéristique d'une application.

Des sondes sont placés aux endroits stratégiques des traitements dans les différentes extensions Vertigo. Chaque projet / module complémentaire peut ajouter des nouveaux points de contrôle pour chaque type d'indicateurs.


## API des plugins

- **analytics.socketLoggerConnector** : Les données d'analytics sont envoyés en utilisant le connecteur log4j/log4j2 SocketAppender
  - `appName` *Optionel* : Nom de l'application
  - `hostName` *Optionel* : Serveur de collecte
  - `port` *Optionel* : Port de collecte (par défaut 4562 pour log4j2, mettre 4650 si vous utilisez log4j)
- **analytics.smartLoggerConnector** : Connecteur qui analyse le process d'execution et calcul les temps passés et les nombres d'appels
  - `aggregatedBy` *Optionel* : Définit la catégorie des sous-process à aggreger
  - `durationThreshold` (ms) *Optionel* : Seuil au delà duquel l'appel est loggué en erreur *(par défaut 1000ms)*