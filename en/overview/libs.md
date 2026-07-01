# Vertigo Extensions: Libs and Modules

Vertigo follows modular programming paradigms. It is therefore divided into modules, each with a clear purpose.

The underlying principle is: 1 recurring business application challenge = 1 Vertigo module

Naturally, when challenges are closely related, they are encapsulated within the same module.

The modules listed here are those that form the central core of Vertigo. They are designed to be used together, providing a cohesive whole for creating Java applications.
These modules are extensions because they enrich a Vertigo application and provide solutions to one or more business application challenges.
We classify these extensions into two groups: *libs* and *modules*.
*Libs* are primarily components aimed at solving technical challenges, while *modules* are akin to functional modules and aim to solve a business challenge as a whole.
*Modules* generally provide a service API, a data model, and sometimes a UI [Module overview](/en/overview/modules).

Below is the list of *Libs* along with a brief description of their contents.


## vertigo-commons
> A collection of technical utilities.

* __codec__: transform objects with codecs (built-in codecs: HTML, MD5, SHA1, SHA256, Base64, Compress, Serialize...)
* __eventbus__: a synchronous event bus for simple event-driven handling within the application
* __app__: multi-node management for clustered applications (topology, health, configuration)
* __peg__: a parser for writing your own [DSL](http://en.wikipedia.org/wiki/Domain-specific_language)
* __script__: transforms simple character strings into executable scripts from your source code (because sometimes mixing code and data is the right approach)
* __transaction__: adds transaction management to your application

[Access the documentation](/en/extensions/commons)

## vertigo-database

> Access databases with a concept-based unified API.

* __sql__: with native support for the following RDBMS: Oracle, MSSql, Postgresql, H2
* __timeseries__: with native support for the InfluxDB time-series database

[Access the documentation](/en/extensions/database)

## vertigo-datamodel

> Efficiently model a business application.

* __smarttype__: Management of enhanced Java types for cross-cutting concerns: constraints, formatting rules, impedance adaptation with the external world
* __structure__: End-to-end management of Java POJOs (from UI to storage) to simplify communication between layers
* __criteria__: a unified API for building filters independent of their usage (Java predicates, SQL...)
* __task__: create and execute various tasks (e.g., direct access to relational databases)

[Access the documentation](/en/extensions/datamodel)

## vertigo-datastore

> Simplified storage management through a standardized API

* __entityStore__: simplified access to multiple storage spaces via a unified API (includes: routing business entities to the correct storage system, CRUD operations, NN operations, cache management)
* __kvstore__: key/value storage space
* __fileStore__: file storage management via a unified API

[Access the documentation](/en/extensions/datastore)

## vertigo-datafactory

> High-value services for efficient data processing.

* __search__: enables use of a search engine within your application—from indexing and updates to consumption via complex faceted queries
* __collections__: tools for manipulating object collections (includes: full-text indexing, faceting, filtering)

[Access the documentation](/en/extensions/datafactory)

## vertigo-basics

> Collections of ready-to-use Formatters, Constraints, and TaskEngine to create all your SmartType and Task instances instantly.

* __formatter__: Text, number, date, etc. formatters
* __constraint__: Text, number, date, etc. constraints
* __task__: SQL TaskEngine for manipulating data in relational databases

[Access the documentation](/en/extensions/basics)


## vertigo-vega
> Publish your application to the outside world.

* __rest__: Adds a REST web service layer to your application. These services are suited for both Machine2Machine exchanges and Single Page Application construction, with dedicated features (security management, rate limiting, token handling...)

[Access the documentation](/en/extensions/vega)

## vertigo-ui

> Create stunning Web interfaces securely and efficiently with the Vertigo-UI extension, leveraging the best of VueJS and Quasar with a highly effective and ergonomic Design System

[Access the documentation](/en/extensions/ui)

## vertigo-account
> Manage your application's users, not just from a technical perspective.

* __authentication__: provides a variety of connectors for managing user application authentication
* __authorization__: provides a security model that associates users with both global rights and fine-grained data rights (Role Based and Attribute Based)
* __identity__: a mechanism to store and retrieve user identities from authoritative sources

[Access the documentation](/en/extensions/account)

## vertigo-stella

> Distribute processing across dedicated nodes

- __rest__: Communication between nodes is performed via HTTP
- __redis__: Tasks to execute are centralized in a REDIS database

[Access the documentation](/en/extensions/stella)
