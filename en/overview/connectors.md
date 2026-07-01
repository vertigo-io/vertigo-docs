# Vertigo-Connectors

Connectors are a special type of component. Their purpose is to provide other components with a pre-configured client/driver to a third-party product or library, simplifying its use for application developers.
The advantage of this approach is twofold:

- **Simplify** Vertigo's technological openness to include more innovation with controlled risk
- **Assist** developers in edge cases requiring advanced features from third-party products and libraries

While __extensions__ provide "high-level" usage-oriented APIs with strong stability, __connectors__ provide "low-level" access directly exposed to third-party solution evolutions.

!> The use of __connectors__ in an application must be deliberate, to minimize and centralize coupling to third-party products, thus facilitating application evolution.

?> The plugins included in Vertigo extensions use __connectors__ to access third-party products and libraries.

Within a project, it is very easy to add a new *Connector* when needed. This notably allows leveraging Vertigo application configuration mechanisms to parameterize the third-party library's client/driver.

Each third-party solution has a dedicated module and may offer multiple *Connectors* if several access methods are possible.

The __connectors__ included in Vertigo are:

## vertigo-redis-connector

> Access to the [Jedis](https://github.com/redis/jedis) client

## vertigo-elasticsearch-connector

> Access to the [elasticsearch](https://github.com/elastic/elasticsearch) client, and embedded ElasticSearch server startup

## vertigo-javalin-connector

> Starts a [Javalin](https://github.com/tipsy/javalin) server locally or in servlet Filter mode

## vertigo-influxdb-connector

> Access to the [influxdb-java](https://github.com/influxdata/influxdb-java) client

## vertigo-keycloak-connector

> Access to the [KeyCloak](https://github.com/keycloak/keycloak) Java client

## vertigo-ldap-connector

> Connects to an LDAP server via native Java APIs

## vertigo-mail-connector

> Provides a mail client via native Java APIs, either directly or through a JNDI resource

## vertigo-mongodb-connector

> Access to the [mongodb-driver-sync](https://github.com/mongodb/mongo-java-driver) Java client

## vertigo-mqtt-connector

> Access to the [Paho](https://github.com/eclipse/paho.mqtt.java) MQTT Java client

## vertigo-neo4j-connector

> Access to the [Neo4j](https://github.com/neo4j/neo4j-java-driver) Java bolt client
!> Local Neo4J server startup (GPLv3 license)

## vertigo-openstack-connector

> Access to the [openstack4j](https://github.com/openstack4j/openstack4j) Java client

## vertigo-spring-connector

> Enriches the Spring component space with Vertigo components to enable interoperability with [Spring](https://github.com/spring-projects/spring-framework) via the `@EnableVertigoSpringBridge` annotation

## vertigo-twitter-connector

> Access to the [Twitter4j](https://github.com/Twitter4J/Twitter4J) Java client

## vertigo-ifttt-connector

> Accesses certain IFTTT API functions via native code

## vertigo-azure-connector

> Access to the [MSAL4j](https://github.com/AzureAD/microsoft-authentication-library-for-java) client for Azure Active Directory authentication

## vertigo-httpclient-connector

> Access to the standard Java HTTP client [java.net.http.HttpClient](https://docs.oracle.com/en/java/javase/17/docs/api/java.net.http/java/net/http/HttpClient.html) with proxy, truststore, and cookie support

## vertigo-jsch-connector

> Access to the [JSch](https://github.com/mwiede/jsch) SSH client with private key authentication from a PKCS12 keystore

## vertigo-oidc-connector

> Access to the [Nimbus OIDC](https://github.com/connect2id/nimbus-oauth-openid-connect-sdk) client for OpenID Connect authentication

## vertigo-s3-connector

> Access to the [MinIO](https://github.com/minio/minio-java) client for S3-compatible storage

## vertigo-saml2-connector

> Access to the [OpenSAML](https://github.com/Jasig/OpenSAML) framework for SAML2 authentication with SP and IP key configuration
