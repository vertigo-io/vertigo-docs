# Modules de Vertigo
Vertigo suit les paradigmes de la programmation modulaire. Il est donc découpé en modules qui ont chacun une vocation claire.

L'idée sous-jacente est la suivante : 1 enjeu récurrent des applications métier = 1 module vertigo

Evidemment, lorsque des problématiques sont très proches, celles-ci sont encapsulées dans un même module.

Les modules listés ici sont ceux qui font partie du noyau central de Vertigo. Ils ont vocation à être utilisés ensemble pour fournir un tout cohérent permettant créer une application Java. Il s'agit des éléments minimum à mettre en œuvre dans une **vraie** application métier.

> Il existe une dépendance linéaire maîtrisée entre ces modules pour une évolutivité aisée.
> 
> **core** <--(uses)-- **commons** <--(uses)-- **database** <--(uses)-- **dynamo** <--(uses)-- **vega** <--(uses)-- **studio** 

Chaque module apporte donc des solutions à un ou plusieurs enjeux liés à une application métier.

Voici la liste des modules ainsi qu'une description succincte de leur contenu

## vertigo-core
> L'ensemble des outils pour créer et configurer une application modulaire et fiable.

* __app__ : le nécessaire pour configurer l'application, via une configuration par API Java ou via fichier Yaml
* __component__ : tout ce qui concerne les composants de votre application : un mécanisme d'injection de dépendances, simple, rapide et léger à l'extrême, une gestion de la programmation par aspects (AOP), une gestion de la programmation déclarative via des proxys
* __locale__ : gestion de l'internationalisation dans votre application (messages, etc...)
* __param__ : gestion de la configuration de votre application, qu'elle soit technique ou fonctionnelle et aussi bien interne qu'externe
* __definitions__ : gestion des définitions de votre application. Les définitions constituent les éléments immuables de votre application depuis le démarrage jusqu'à l'arrêt
* __resource__ : gestion de l'accès aux ressources de votre application (nativement intégrés : recherche dans le classpath, la webapp, le file system avec des chemins absolus et relatifs)
* __lang__ : une liste d'éléments aussi utiles qu'indispensables pour agrémenter le langage Java (ex: Assertions)


## vertigo-commons
> Une collection d'utilitaires techniques.

* __analytics__ : collecte les données d'utilisation de l'application pour comprendre son fonctionnement en détails
* __cache__ : permet de garder certains éléments en mémoire pour gagner en performances
* __codec__ : transformer les objets avec des codecs (codecs intégrés : HTML, MD5, SHA1, SHA256, Base64, Compress, Serialize...) 
* __daemon__ : gestion des démons (tâches techniques en arrière-plan) de votre application, depuis leur enregistrement jusqu'à l'établissement de statistiques d'utilisation en passant par leur exécution
* __eventbus__ :  un bus d'évènements synchrone pour une gestion évènementielle simple dans l'application
* __node__ :  gestion du multi-nœud dans le cadre d'applications constituées d'un cluster (topologie, santé, configuration)
* __peg__ : un parseur pour écrire vos propres [DSL](http://en.wikipedia.org/wiki/Domain-specific_language)
* __script__ : permet de transformer de simples chaines de caractère en scripts exécutables depuis votre code source (car parfois mélanger code et données est la bonne solution)
* __transaction__ : ajoute une gestion transactionnelle à votre application 

## vertigo-database
### Accédez simplement à vos bases de données

>  Accéder à des bases de données avec une API unifiée par concept.

* __sql__ : avec le support natif des SGBD suivants : Oracle, MSSql, Postgresql, H2
* __timeseries__ : avec le support natif de la base de données InfluxDB

## vertigo-dynamo
> Une manière simple de modéliser votre application tout en fournissant des services utiles via des API claires, telles que le stockage, la recherche etc...

* __collections__ : des outils pour manipuler les collections d'objets (sont intégrés : indexation fulltext, facettage, filtrage)
* __criteria__ : une API unique pour construire des filtres indépendamment de leur utilisation (prédicats Java, sql...)
* __domain__ : Gestion de POJO Java de bout en bout (de L'IHM au stockage) pour simplifier la communication entre les couches
* __environment__ : permet la création des définitions d'objets métier depuis des sources distinctes tout en initialisant vos composants à partir de différentes sources  (intégrés en standard : powerdesigner, DSL, Java annotations)
* __file__ : manipuler des fichiers
* __kvstore__ : espace de stockage clés / valeurs
* __store__ : accès simplifié à vos multiples espaces de stockage via une API unifiée (inclus : routage des entités métier vers le bon système de stockage, opérations CRUD, opérations NN, gestion du cache)
* __search__ : permet l'utilisation d'un moteur de recherche dans le votre application de manière simple, depuis l'indexation, la mise à jour jusqu'à la consommation via des recherches complexes à facettes
* __task__ : créer et exécuter des tâches diverses (par exemple, un accès direct aux bases de données relationnelles)


## vertigo-account
> Gestion des utilisateurs de votre application, et pas uniquement d'un point de vue technique.

* __authentication__ : fournit une variété de connecteurs pour gérer l'authentification de vos utilisateurs à l'application
* __authorization__ : fournit un modèle de sécurité qui permet d'associer aux utilisateurs aussi bien des droits globaux que des droits fins liés aux données (Role Based et Attribute Based)   
* __identity__ : un moyen de stocker et récupérer depuis les points de vérité les identités de vos utilisateurs


## vertigo-vega
> Publier son application à destination du reste du monde.

* __rest__ : Ajoute une couche webservice REST à votre application. Ces services sont à la fois adaptés aux échanges Machine2Machine et à la construction de Single Page Applications via des fonctionnalités dédiées (gestion de la sécurité, rate limiting, gestion de tokens...)


## vertigo-studio
>  Une collection d'outils pour aider le développeur dans son travail.

* __mda__ : Model Driven Architecture, outils pour générer le code source sans valeur ajoutée (java, sql, js, ts), fichiers de propriétés multilingues...
* __ui__ : more to come !

