# Vertigo : Boost your apps

?> Boost your apps, ou comment créer de la valeur dans vos projets, mieux et plus vite

[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

**Vertigo** est une plateforme Java pour construire des applications ou systèmes d'information métier modernes, complets, maintenables et évolutifs.

Elle est conçue pour maximiser l'ajout de valeur :
- les choses simples se font simplement,
- les choses plus compliquées sont ajoutées par des *plug-in* en minimisant leurs impacts,
- plusieurs briques à forte valeur ajoutée sont fournies *out-of-the-box* : IHM moderne, recherche, sécurité, analytics, dataviz...

L'industrie automobile a vu la généralisation du concept de "plateforme", permettant de créer rapidement, à partir d'une même base, différents modèles : berline, compacte, SUV...
A cette base s'ajoutent une série d'options et de personnalisations qui apportent un large éventail de choix, tout en mutualisant les coûts, minimisant les risques industriels et en maximisant la valeur pour le client.

**Vertigo**, transposition de ce principe dans la création de systèmes d'information et de services numériques, se traduit par un cœur applicatif garantissant la robustesse, la qualité et l'efficacité des développements.
Sur ce cœur se greffent des options innovantes, activables en fonction des objectifs métier.
**Vertigo** se présente comme une plateforme **Opinionated** (c'est-à-dire un *Opinionated Software Development Framework* — un framework qui prend des positions claires sur l'architecture et les bonnes pratiques).
Ce principe lui permet de maximiser l'efficacité des développements pour la réalisation des applications métier de type "Applications de gestion" : très efficace sur son domaine, mais qui permet d'en sortir. Là où d'autres frameworks généralistes auront une efficacité moyenne mais sur un pan très large (*trop ?*) de cas d'application.

**Vertigo**, en cœur applicatif de la plateforme, embarque nativement l'ensemble des composants indispensables à une application moderne : recherche, sécurité, mobilité, analytics, dataviz...

## Choix architecturaux

Parce qu'une plateforme *Opinionated* assume ses convictions, Vertigo s'appuie sur cinq piliers techniques qui protègent vos projets des dérives classiques des applications métier. Chaque choix élimine une source de complexité, de bugs ou de rework.

- **Architecture MDA (Model Driven)** : La déclaration de vos modèles est l'unique source de vérité. Code, interfaces, webservices et stockage sont générés automatiquement — synchronisation garantie, plus de divergences.
- **Typage fort (SmartTypes, BasicTypes)** : Un prix reste un prix, une date reste une date. Validés dès l'entrée dans le système, ils préservent l'intégrité de la donnée partout (IHM, base, JSON) et suppriment les erreurs de formatage.
- **Aucune exception checked (Runtime only)** : La logique métier ne doit pas être polluée par la capture systématique d'exceptions techniques. Vertigo gère les erreurs de manière centralisée, pour un code plus lisible et un développement accéléré.
- **Séparation ComponentSpace / DefinitionSpace** : Structure figée au démarrage, immuable et non corruptible à chaud. Résultat : une robustesse maximale, un comportement prévisible et une sécurité renforcée en production.
- **UI hybride Server-Side / Client-Side** : La plateforme combine la solidité du rendu serveur pour la structure et la fluidité de VueJS pour l'interaction. Le meilleur des deux mondes, sans la complexité d'une SPA pure.

Vertigo est composé de :

- [**Vertigo-Core**](/overview/core) : Un moteur Java ultra puissant et super léger
- [**Vertigo-Libs**](/overview/libs) : Une collection de modules d'extensions permettant de gérer toutes les problématiques principales des applications métier, et donc de les créer en un temps record
- [**Vertigo-Connectors**](/overview/connectors) : Une collection de connecteurs "bas-niveau" vers des librairies et produits tiers pour faciliter la vie du développeur dans les cas aux limites
- [**Vertigo-Studio**](/overview/studio) : Un outil de conception dédié aux applications métier pour gagner en efficacité et en cohérence
