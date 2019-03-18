# Modules de Vertigo
Vertigo suit les paradigmes de la programmation modulaire, il est donc découpé en modules qui ont chacun une vocation claire.

L'idée sous-jacente est la suivante : 1 enjeu récurrent des applications métier = 1 module vertigo

Evidemment lorsque des problématiques sont très proches celles-ci sont encapsulées dans un même module.

Les modules listés ici sont ceux qui font partie du noyau central de Vertigo. Ils ont vocations à être utilisés ensemble pour fournir une ensemble cohérent pour créer une application Java. Il s'agit des éléments minimum à mettre en œuvre dans une **vraie** application métier.

> Il existe une dépendance linéaire maîtrisée entre ces modules pour une évolutivité aisée.
> **core** <--(uses)-- **commons** <--(uses)-- **database** <--(uses)-- **dynamo** <--(uses)-- **vega** <--(uses)-- **studio** 

Chaque module apportent donc des solutions à un ou plusieurs enjeux liés à une application métier.

Voici la liste des modules ainsi qu'une description succincte de son contenu

## vertigo-core
> L'ensemble des outils pour créer et configurer une application modulaire et fiable.

* __app__ : le nécessaire pour configurer l'application, via une configuration par API Java ou via fichier Yaml
* __component__ : tout ce qui concerne les composants de votre application : un mécanisme d'injection de dépendance, simple, rapide et léger à extrême, une gestion de la programmation par aspects AOP, une gestion de la programmation déclarative via des proxys
* __locale__ : gestion de l'internationalisation dans votre application (messages, etc...)
* __param__ : gestion de la configuration de votre application, qu'elle soit technique ou fonctionnel et aussi bien interne qu'externe
* __definitions__ : gestion des définitions de votre applications. Les définitions constituent les éléments immuables de votre application depuis le démarrage jusqu'à arrêt
* __resource__ : gestion de l'accès aux ressources de votre application (nativement integré : recherche dans le classpath, la webapp, le filesystem avec des chemins absolus et relatifs)
* __lang__ : une liste d'éléments aussi utiles qu'indispensables pour agrémenter le langage Java (ex: Assertions)


## vertigo-commons
> Une collection d'utilitaires techniques.

* __analytics__ : collecte les données d'utilisation de l'application pour comprendre son fonctionnement en détail
* __cache__ : permet de garder certains éléments en mémoire pour gagner en performance
* __codec__ : transformer les objets avec des codecs (codecs intégrés : HTML, SHA1, Base64, Compress, Serialize) 
* __daemon__ : gestion des démons (tâches techniques en arrière plan) de votre application, depuis leur enregistrement jusqu'à l'établissement de statistiques d'utilisation en passant par leur exécution
* __eventbus__ :  un bus évènement synchrone pour une gestion évènementielle simple dans l'application
* __node__ :  gestion du multi-noeud dans le cadre d'application constitués d'un cluster (topologie, santé, configuration)
* __peg__ : un parser pour écrire vos propres [DSL](http://en.wikipedia.org/wiki/Domain-specific_language)
* __script__ : permet de transformer de simples chaines de caractère en scripts executable depuis votre code source (car des fois mélanger code et données est la bonne solution)
* __transaction__ : ajoute une gestion transactionnelle à votre application 

## vertigo-database
### A simple data access to your databases

>  Accèder à des bases de données avec une API unifiée par concept.

* __sql__ : avec le support native des SGBD suivants : Oracle, MSSql, Postgresql, H2
* __timeseries__ : avec le support natif de base de donnée InfluxDB

## vertigo-dynamo
> Une manière simple de modéliser votre application tout en fournissant des services utiles via des API claires, telle que le stockage, la recherche etc...

* __collections__ : des outils pour manipuler les collections d'objets (sont intégrés : indexation fulltext, facettage, filtrage)
* __criteria__ : une API unique pour construire des filtres indépendamment de leur utilisation(predicats Java, sql...)
* __domain__ : Gestion de POJO Java de bout en bout (de L'IHM au stockage) pour simplifier la communication entre les couches
* __environment__ : permet la création des définitions d'objets métiers depuis des sources distinctes tout en initialize your components from different sources (built-in : powerdesigner, DSL, Java annotations)
* __file__ : manage file creation
* __kvstore__ : key/value datastore
* __store__ : accès simplifié à vos multiples espaces de stockage via une API unifiée (inlcus : routages des entités métiers vers le bon système de stoclage, opérations  CRUD, opérations NN, gestion du cache)
* __search__ : permet l'utilisation d'un moteur de recherche dans le votre application de manière simple, depuis l'indexation, la mise à jour jusqu'à la consommation via des recherches complexe à facettes
* __task__ : créer et exexution des tâches diverses (par exemple un accès direct aux bases de données relationnelles)


## vertigo-account
> Gestion des utilisateurs de votre application, et pas uniquement d'un point de vue technique.

* __authentication__ : fournit une variété de connecteurs pour gérer l'authentification de vos utilisateurs à l'application
* __authorization__ : fournit un modèle de sécurité qui permet d'associer aux utilisateurs aussi bien des droits globaux que des droits fin liés aux données (Role Based et attribute based)   
* __identity__ : un moyen de stocker et récuperer depuis les points de vérités les identités de vos utilisateurs


## vertigo-vega
> Publier son application au reste du monde.

* __rest__ : Ajoute une couche webservice REST à votre application. Ces services sont à la fois adaptés aux échanges Machine2Machine et à la construction de Single Pages Applications via des fonctionnalités dédiées (gestion de la sécurité, rate limiting, gestion de tokens...)


## vertigo-studio
>  Une collection  d'outils pour aider le développeur dans son travail.

* __mda__ : Model Driven Architecture outils pour générer le code source sans valeur ajoutée (java, sql, js, ts), fichier de propriétés multilingues...
* __ui__ : more to come

