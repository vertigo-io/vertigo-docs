# Extensions de Vertigo : Libs et Modules
Vertigo suit les paradigmes de la programmation modulaire. Il est donc découpé en modules qui ont chacun une vocation claire.

L'idée sous-jacente est la suivante : 1 enjeu récurrent des applications métier = 1 module vertigo

Evidemment, lorsque des problématiques sont très proches, celles-ci sont encapsulées dans un même module.

Les modules listés ici sont ceux qui font partie du noyau central de Vertigo. Ils ont vocation à être utilisés ensemble pour fournir un tout cohérent permettant créer une application Java. 
Ces modules sont des extensions car ils permettent d'enrichir une application Vertigo et fournissent des solutions à un ou plusieurs enjeux liés à une application métier.
Nous classons ces extensions en deux groups *libs* et *modules*.
Les *libs* sont plutôt des composants qui visent à résoudre une problèmatique techniques, et les *modules* s'apparentent aux modules fonctionnels et visent à résoudre une problématique métier dans son ensemble.
Les *modules* proposent en général une API de services, un modèle de données et parfois une IHM [Présentation des modules](/overview/modules).

Voici la liste des *Libs* ainsi qu'une description succincte de leur contenu


## vertigo-commons
> Une collection d'utilitaires techniques.

* __codec__ : transformer les objets avec des codecs (codecs intégrés : HTML, MD5, SHA1, SHA256, Base64, Compress, Serialize...) 
* __eventbus__ :  un bus d'évènements synchrone pour une gestion évènementielle simple dans l'application
* __app__ :  gestion du multi-nœud dans le cadre d'applications constituées d'un cluster (topologie, santé, configuration)
* __peg__ : un parseur pour écrire vos propres [DSL](http://en.wikipedia.org/wiki/Domain-specific_language)
* __script__ : permet de transformer de simples chaines de caractère en scripts exécutables depuis votre code source (car parfois mélanger code et données est la bonne solution)
* __transaction__ : ajoute une gestion transactionnelle à votre application 

[Accéder à la documentation](/extensions/commons)

## vertigo-database

>  Accéder à des bases de données avec une API unifiée par concept.

* __sql__ : avec le support natif des SGBD suivants : Oracle, MSSql, Postgresql, H2
* __timeseries__ : avec le support natif de la base de données InfluxDB

[Accéder à la documentation](/extensions/database)

## vertigo-datamodel

> Modéliser efficacement une application métier.

* __smarttype__ : Gestion de super types Java pour gérér de manière transverses : les contraintes, les règles de formattages, les adaptations d'impédance avec le monde extérieur
* __structure__ : Gestion de POJO Java de bout en bout (de L'IHM au stockage) pour simplifier la communication entre les couches
* __criteria__ : une API unique pour construire des filtres indépendamment de leur utilisation (prédicats Java, sql...)
* __task__ : créer et exécuter des tâches diverses (par exemple, un accès direct aux bases de données relationnelles)

[Accéder à la documentation](/extensions/datamodel)

## vertigo-datastore

> Gestion du stockage simplifié via une API standardisée

* __entityStore__ : accès simplifié à vos multiples espaces de stockage via une API unifiée (inclus : routage des entités métier vers le bon système de stockage, opérations CRUD, opérations NN, gestion du cache)
* __kvstore__ : espace de stockage clés / valeurs
* __fileStore__ : gestion du stockage des fichiers via une API unifiée

[Accéder à la documentation](/extensions/datastore)

## vertigo-datafactory

> Des services à forte valeur ajoutée pour traiter les données efficacement.

* __search__ : permet l'utilisation d'un moteur de recherche dans le votre application de manière simple, depuis l'indexation, la mise à jour jusqu'à la consommation via des recherches complexes à facettes
* __collections__ : des outils pour manipuler les collections d'objets (sont intégrés : indexation fulltext, facettage, filtrage)

[Accéder à la documentation](/extensions/datafactory)

## vertigo-basics

> Des collections de Formatters, Contraintes, TaskEngine prêt à l'emploi pour créer tous vos SmartType et Task en un éclair.

* __formatter__ : Formatter de texte, de nombres, de dates, ect...
* __constraint__ : Contraintes de texte, de nombres, de dates, ect...
* __task__ : TaskEngine SQL pour manipuler des données sur des bases de données relationnelles

[Accéder à la documentation](/extensions/basics)


## vertigo-vega
> Publier son application à destination du reste du monde.

* __rest__ : Ajoute une couche webservice REST à votre application. Ces services sont à la fois adaptés aux échanges Machine2Machine et à la construction de Single Page Applications via des fonctionnalités dédiées (gestion de la sécurité, rate limiting, gestion de tokens...)

[Accéder à la documentation](/extensions/vega)

## vertigo-ui

> Créer de superbes interfaces Web en tout sécurité et très efficacement avec l'extension Vertigo-UI qui tire le meilleur parti de VueJS et de Quasar avec un Design System ultra efficace et ergonomique

[Accéder à la documentation](/extensions/ui)

## vertigo-account
> Gestion des utilisateurs de votre application, et pas uniquement d'un point de vue technique.

* __authentication__ : fournit une variété de connecteurs pour gérer l'authentification de vos utilisateurs à l'application
* __authorization__ : fournit un modèle de sécurité qui permet d'associer aux utilisateurs aussi bien des droits globaux que des droits fins liés aux données (Role Based et Attribute Based)   
* __identity__ : un moyen de stocker et récupérer depuis les points de vérité les identités de vos utilisateurs

[Accéder à la documentation](/extensions/account)

## vertigo-stella

> Distribue les traitements sur des noeud dédiés

- __rest__ : La communication entre les noeuds est réalisée via le protocole http
- __redis__ : Les taches à effectuer sont centralise dans une base de données REDIS

[Accéder à la documentation](/extensions/stella)
