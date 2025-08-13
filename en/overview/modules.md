# Vertigo Extensions: Libs and Modules

Vertigo follows the paradigms of modular programming. It is therefore split into modules, each with a clear purpose.

The underlying idea is as follows: **1 recurring business application challenge = 1 Vertigo module**.

Of course, when issues are closely related, they are encapsulated within the same module.

The modules listed here are those that are part of the Vertigo core. They are intended to be used together to provide a coherent whole for building a Java application.
These modules are considered extensions because they enhance a Vertigo application and provide solutions to one or more business application challenges.

We classify these extensions into two groups: *libs* and *modules*.

* **Libs** are more like components designed to solve a specific technical problem  [Libs Overview](/en/overview/libs).
* **Modules** are closer to functional modules and aim to address a complete business problem. Modules generally offer a service API, a data model, and sometimes a UI.

Below is the list of *Modules* along with a brief description of their contents.

## vertigo-social

> Adds collaborative functions to your application to improve communication with and between your users.

* __notification__: Send notifications to your users without resorting to third-party services
* __comment__: Spaces for sharing unstructured information to improve the operational efficiency of the application 
* __mail__: Send emails very simply
* __handle__: (Function in beta): Associate 'meaningful handles' with the entities of your application for simplified referencing outside the application and better navigation within the application.

[Access the documentation](/modules/social)

## vertigo-orchestra

> A control tower and execution of long and scheduled processes (commonly called batches), allowing the supervision of the application by a technical-functional administrator.

* __definition__: defines the managed processes
* __schedule__: schedules recurring executions or delegates this treatment to third-party solutions
* __execute__: executes the processes according to different strategies while minimizing the impact on the host application

[Access the documentation](/modules/orchestra)

## vertigo-quarto

> Allows the management of publications and editions of documents with data merging.

- __publisher__: Simple and lightweight publishing tool. Allows to produce documents from user document model and application data. The models are very simple to modify because they are ODT or DOCX documents with markers.
- __converter__: Allows to convert a document format into another (the existing plugins support: ODT, DOC, DOCX, RTF, TXT to PDF)
- __export__: Allows to export collections or business objects to utility formats (the existing plugins support: CSV, PDF, RTF, XLS)

[Access the documentation](/modules/quarto)

## vertigo-audit

> Allows to record critical actions in an application to create audit trails

- __ledger__: Uses the mechanisms of BlockChain to securely trace important information (Supports Ethereum blockchain, public and/or private, and/or sidechain)
- __trace__: Traces actions according to various strategies (log, db, etc...)

[Access the documentation](/modules/audit)

## vertigo-dashboard

> Provides a turnkey dashboard to monitor the performance and health of an application without depending on a third-party product.

This module is likely to be heavily reworked/moved in the near future.

[Access the documentation](/modules/dashboard)

## vertigo-geo

> Add a geographical dimension to your business entities and your application 

* __geocoder__: Transform positions into addresses and vice versa, via different services (GoogleMaps and BAN included)
* __geosearch__: Use cartographic functions to search for business entities in a geographical area (ElasticSearch included)

[Access the documentation](/modules/geo)

## vertigo-easyforms

> Adds a dynamic form tool to your application. This module is designed to allow functional administrators to adapt forms that require flexibility.
> This module provides a UI built with VertigoUi.

[Access the documentation](/modules/easyforms)

## vertigo-planning

> Adds a scheduling management tool to your application. This module provides both slot planning (BackOffice side) and slot selection (FrontOffice side).
> This module provides a UI built with VertigoUi.

[Access the documentation](/modules/planning)

