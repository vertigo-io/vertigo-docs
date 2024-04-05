# Vertigo Extensions
Vertigo follows the paradigms of modular programming. Therefore, it is divided into modules, each with a clear vocation.

The underlying idea is as follows: 1 recurring issue of business applications = 1 vertigo module

Of course, when issues are very close, they are encapsulated in the same module.

The modules listed here are those that are part of the central core of Vertigo. They are intended to be used together to provide a coherent whole to create a Java application. 
These modules are called *extensions* because they enrich a Vertigo application and provide solutions to one or more issues related to a business application.

Here is the list of modules along with a brief description of their content

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

## vertigo-social

> Adds collaborative functions to your application to improve communication with and between your users.

* __notification__: Send notifications to your users without resorting to third-party services
* __comment__: Spaces for sharing unstructured information to improve the operational efficiency of the application 
* __mail__: Send emails very simply
* __handle__: (Function in beta): Associate 'meaningful handles' with the entities of your application for simplified referencing outside the application and better navigation within the application.

[Access the documentation](/extensions/social)

## vertigo-orchestra

> A control tower and execution of long and scheduled processes (commonly called batches), allowing the supervision of the application by a technical-functional administrator.

* __definition__: defines the managed processes
* __schedule__: schedules recurring executions or delegates this treatment to third-party solutions
* __execute__: executes the processes according to different strategies while minimizing the impact on the host application

[Access the documentation](/extensions/orchestra)

## vertigo-quarto

> Allows the management of publications and editions of documents with data merging.

- __publisher__: Simple and lightweight publishing tool. Allows to produce documents from user document model and application data. The models are very simple to modify because they are ODT or DOCX documents with markers.
- __converter__: Allows to convert a document format into another (the existing plugins support: ODT, DOC, DOCX, RTF, TXT to PDF)
- __export__: Allows to export collections or business objects to utility formats (the existing plugins support: CSV, PDF, RTF, XLS)

[Access the documentation](/extensions/quarto)

## vertigo-audit

> Allows to record critical actions in an application to create audit trails

- __ledger__: Uses the mechanisms of BlockChain to securely trace important information (Supports Ethereum blockchain, public and/or private, and/or sidechain)
- __trace__: Traces actions according to various strategies (log, db, etc...)

[Access the documentation](/extensions/audit)

## vertigo-dashboard

> Provides a turnkey dashboard to monitor the performance and health of an application without depending on a third-party product.

This module is likely to be heavily reworked/moved in the near future.

[Access the documentation](/extensions/dashboard)

## vertigo-geo

> Add a geographical dimension to your business entities and your application 

* __geocoder__: Transform positions into addresses and vice versa, via different services (GoogleMaps and BAN included)
* __geosearch__: Use cartographic functions to search for business entities in a geographical area (ElasticSearch included)

[Access the documentation](/extensions/geo)

## vertigo-stella

> Distributes treatments on dedicated nodes

- __rest__: Communication between nodes is carried out via the http protocol
- __redis__: The tasks to be performed are centralized in a REDIS database

[Access the documentation](/extensions/stella)
