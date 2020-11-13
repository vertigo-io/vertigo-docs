# Vertigo-Connectors

Les *Connector* sont des composants un peu particulier. Leur raison d"être est de fournir aux autres composants un client/driver pré-configuré vers un produit ou une librairie tierce pour simplifier son usage pour le développeur de l'application.
L'avantage d'une telle démarche est double :

- **Simplifier** l'ouverture technologique de Vertigo pour y inclure plus d'innovation avec un risque maîtrisé
- **Aider** le développeur dans les cas aux limites qui nécessitent l'utilisation de fonctions avancées des produits et librairies tiers

Alors que les __extensions__ propose des API de "haut-niveau" orienté usage et donc d'une grande stabilité, les __connectors__ founissent un accès "bas-niveau" directement soumis aux évolutions des solutions tierce.

!> L'usage des __connectors__ dans une application doit être raisoné afin de minimiser et de centraliser les adhérences aux produits tiers et ainsi faciliter l'évolutivité de l'application.

?> Les plugins inclus dans les extensions Vertigo, utilisent les __connectors__ pour accéder aux produits et librairies tiers.

Dans le cadre d'un projet il est très simple d'ajouter un nouveau *Connector* en cas de besoin. Cela permet notament de profiter des mécanismes de configuration d'une application Vertigo afin de paramétrer le client/driver de la librairie tierces

Chaque solution tierce possède un module dédié et propose éventuellement plusieurs *Connector* si plusieurs modalités d'accès sont possibles.

Les __connectors__ inclus dans vertigo sont les suivants

## vertigo-redis-connector

> Accès au client [Jedis](https://github.com/redis/jedis)

## vertigo-elasticsearch-connector

> Accès au client [elasticsearch](https://github.com/elastic/elasticsearch), et démarrage d'un serveur ElasticSearch embarqué

## vertigo-javalin-connector

> Démarre un serveur [Javalin](https://github.com/tipsy/javalin) local ou en mode Filtre de servlet

## vertigo-influxdb-connector

> Accès au client [influxdb-java](https://github.com/influxdata/influxdb-java)

## vertigo-keycloak-connector

> Accès au client java [KeyCloak](https://github.com/keycloak/keycloak)

## vertigo-ldap-connector

> Accède à un serveur ldap via les API natives Java

## vertigo-mail-connector

> Fournit un client mail via les API natives Java soit directement soit une resource JNDI

## vertigo-mongodb-connector

> Accès au client java [mongodb-driver-sync](https://github.com/mongodb/mongo-java-driver)

## vertigo-mqtt-connector

> Accès au client MQTT Java [Paho](https://github.com/eclipse/paho.mqtt.java)

## vertigo-neo4j-connector

> Accès au client java bolt de [Neo4j](https://github.com/neo4j/neo4j-java-driver)
!> Démarrage d'un serveur local Neo4J (GPLv3 licence)

## vertigo-openstack-connector

> Accès au client Java [openstack4j](https://github.com/openstack4j/openstack4j)

## vertigo-spring-connector

> Enrichit l'espace des composants de spring avec les composants de Vertigo pour permettre l'interopérabilité avec [Spring](https://github.com/spring-projects/spring-framework) via l'annotation `@EnableVertigoSpringBridge`

## vertigo-twitter-connector

> Accès au client java [Twitter4j](https://github.com/Twitter4J/Twitter4J)

## vertigo-iftt-connector

> Accède à certaines fonctions de l'API IFFT via du code natif

