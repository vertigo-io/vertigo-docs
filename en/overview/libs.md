# Vertigo Extensions: Libs and Modules

Vertigo follows the paradigms of modular programming. It is therefore split into modules, each with a clear purpose.

The underlying idea is as follows: **1 recurring business application challenge = 1 Vertigo module**.

Of course, when issues are closely related, they are encapsulated within the same module.

The modules listed here are those that are part of the Vertigo core. They are intended to be used together to provide a coherent whole for building a Java application.
These modules are considered extensions because they enhance a Vertigo application and provide solutions to one or more business application challenges.

We classify these extensions into two groups: *libs* and *modules*.

* **Libs** are more like components designed to solve a specific technical problem.
* **Modules** are closer to functional modules and aim to address a complete business problem. Modules generally offer a service API, a data model, and sometimes a UI. [Module Overview](/en/overview/modules)

Below is the list of *Libs* along with a brief description of their contents.


## vertigo-commons
> A collection of technical utilities.

* __codec__: transform objects with codecs (integrated codecs: HTML, MD5, SHA1, SHA256, Base64, Compress, Serialize...) 
* __eventbus__: a synchronous event bus for simple event management in the application
* __app__: multi-node management in the context of applications consisting of a cluster (topology, health, configuration)
* __peg__: a parser to write your own [DSL](http://en.wikipedia.org/wiki/Domain-specific_language)
* __script__: allows to transform simple strings into executable scripts from your source code (because sometimes mixing code and data is the right solution)
* __transaction__: adds transactional management to your application 

[Access the documentation](/extensions/commons)

## vertigo-database

> Access databases with a unified API by concept.

* __sql__: with native support for the following DBMS: Oracle, MSSql, Postgresql, H2
* __timeseries__: with native support for the InfluxDB database

[Access the documentation](/extensions/database)

## vertigo-datamodel

> Effectively model a business application.

* __smarttype__: Management of Java super types to manage transversely: constraints, formatting rules, impedance adaptations with the outside world
* __structure__: Management of Java POJO end-to-end (from the UI to storage) to simplify communication between layers
* __criteria__: a unique API to build filters regardless of their use (Java predicates, sql...)
* __task__: create and execute various tasks (for example, direct access to relational databases)

[Access the documentation](/extensions/datamodel)

## vertigo-datastore

> Simplified storage management via a standardized API

* __entityStore__: simplified access to your multiple storage spaces via a unified API (included: routing of business entities to the right storage system, CRUD operations, NN operations, cache management)
* __kvstore__: key / value storage space
* __fileStore__: management of file storage via a unified API

[Access the documentation](/extensions/datastore)

## vertigo-datafactory

> High value-added services to efficiently process data.

* __search__: allows the use of a search engine in your application in a simple way, from indexing, updating to consumption via complex faceted searches
* __collections__: tools to manipulate collections of objects (are integrated: fulltext indexing, faceting, filtering)

[Access the documentation](/extensions/datafactory)

## vertigo-basics

> Collections of ready-to-use Formatters, Constraints, TaskEngine to create all your SmartType and Task in a flash.

* __formatter__: Text, numbers, dates formatter, etc...
* __constraint__: Text, numbers, dates constraints, etc...
* __task__: SQL TaskEngine for manipulating data on relational databases

[Access the documentation](/extensions/basics)

## vertigo-account
> Management of the users of your application, and not only from a technical point of view.

* __authentication__: provides a variety of connectors to manage the authentication of your users to the application
* __authorization__: provides a security model that allows associating both global rights and fine rights related to data (Role Based and Attribute Based) with users  
* __identity__: a way to store and retrieve the identities of your users from the points of truth

[Access the documentation](/extensions/account)

## vertigo-vega
> Publish your application for the rest of the world.

* __rest__: Adds a REST webservice layer to your application. These services are both adapted to Machine2Machine exchanges and to the construction of Single Page Applications via dedicated features (security management, rate limiting, token management...)

[Access the documentation](/extensions/vega)

## vertigo-ui

> Create beautiful web interfaces safely and very efficiently with the Vertigo-UI extension which takes full advantage of VueJS and Quasar with an ultra efficient and ergonomic Design System

[Access the documentation](/extensions/ui)

## vertigo-stella

> Distributes treatments on dedicated nodes

- __rest__: Communication between nodes is carried out via the http protocol
- __redis__: The tasks to be performed are centralized in a REDIS database

[Access the documentation](/extensions/stella)

