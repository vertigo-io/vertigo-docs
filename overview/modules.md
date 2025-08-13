# Extensions de Vertigo : Libs et Modules
Vertigo suit les paradigmes de la programmation modulaire. Il est donc découpé en modules qui ont chacun une vocation claire.

L'idée sous-jacente est la suivante : 1 enjeu récurrent des applications métier = 1 module vertigo

Evidemment, lorsque des problématiques sont très proches, celles-ci sont encapsulées dans un même module.

Les modules listés ici sont ceux qui font partie du noyau central de Vertigo. Ils ont vocation à être utilisés ensemble pour fournir un tout cohérent permettant créer une application Java. 
Ces modules sont des extensions car ils permettent d'enrichir une application Vertigo et fournissent des solutions à un ou plusieurs enjeux liés à une application métier.
Nous classons ces extensions en deux groups *libs* et *modules*.
Les *libs* sont plutôt des composants qui visent à résoudre une problèmatique techniques, et les *modules* s'apparentent aux modules fonctionnels et visent à résoudre une problématique métier dans son ensemble [Présentation des libs](/overview/libs).
Les *modules* proposent en général une API de services, un modèle de données et parfois une IHM.

Voici la liste des *Modules* ainsi qu'une description succincte de leur contenu


## vertigo-social

> Ajoute des fonctions collaboratives à votre application pour améliorer la communication avec et entre vos utilisateurs.

* __notification__ : Envoyer des notifications à vos utilisateurs sans recourir à des services tiers
* __comment__ : Des espaces de partage d'informations non structurés pour améliorer l'efficacité opérationnelle de l'application 
* __mail__ : Envoyer des emails très simplement
* __sms__ : Envoyer des SMS
* __handle__ : (Fonction en beta) : Associer aux entités de votre application des 'handle' signifiants permettant un référencement simplifié à l'exterieur de l'application ainsi qu'une meilleure navigation au sein de l'application.

[Accéder à la documentation](/modules/social)

## vertigo-orchestra

> Une tour de controle et d'execution de processus longs et programmés (regulièrement appelés batchs), permettant la supervision de l'application par un administrateur technico-fonctionnel.
> Ce module propose une IHM de base en VueJs.

* __definition__ : définit les processus gérés
* __schedule__ : planifie les executions récurrentes ou délègue ce traitement à une solutions tierces
* __execute__ : execute les processus selon différentes stratégie tout en minimisant l'impact sur l'application hôte

[Accéder à la documentation](/modules/orchestra)

## vertigo-quarto

> Permet la gestion des publications et des éditions de documents avec fusion de données.

- __publisher__ : Outil d'éditique simple et léger. Permet de produire des documents à partir de modèle de document utilisateur et des données de l'application. Les modèles sont très simples à modifier car ils sont des documents ODT ou DOCX avec des marqueurs.
- __converter__ : Permet de convertir un format de document dans un autre (les plugins existants supportent : ODT, DOC, DOCX, RTF, TXT vers PDF)
- __export__ : Permet d'exporter des collections ou des objets métiers vers des formats utilitaires (les plugins existants supportent : CSV, PDF, RTF, XLS)

[Accéder à la documentation](/modules/quarto)

## vertigo-audit

> Permet d'enregister les actions critiques dans une application pour créer des pistes d'audit

- __ledger__ : Utilise les méchanismes de BlockChain pour tracer de manière sécurisé des informations importantes (Support de la blockchain Ethereum, publique et/ou privée, et/ou sidechain)
- __trace__ : Trace selon diverses stratégies les actions (log, db, etc...)

[Accéder à la documentation](/modules/audit)

## vertigo-dashboard

> Fournir un tableau de bord clé en main pour suivre les performances et la santé d'une application sans dépendre d'un produit tiers.

Ce module est susceptible d'être fortement remanié / déplacé dans un avenir proche.

[Accéder à la documentation](/modules/dashboard)

## vertigo-geo

> Ajoute une dimension géographique à vos entités métiers et à votre application 

* __geocoder__ : Transformer des positions en adresses et inversement, via différents services (GoogleMaps et BAN inclus)
* __geosearch__ : Utiliser les fonctions cartographiques pour rechercher des entités métiers dans une zone geographique (ElasticSearch inclus)

[Accéder à la documentation](/modules/geo)


## vertigo-easyforms

> Ajoute un outil de formulaire dynamique dans votre application. Ce module est conçu pour permettre aux administrateurs fonctionnels d'adapater les formulaires qui ont besoin de flexibilité.
> Ce module propose une IHM en VertigoUi.

[Accéder à la documentation](/modules/easyforms)


## vertigo-planning

> Ajoute un outil de gestion de planning dans votre application. Ce module propose à la fois la plannification de créneau (cot BackOffice) et la sélection de créneau (coté FrontOffice).
> Ce module propose une IHM en VertigoUi.

[Accéder à la documentation](/modules/planning)
