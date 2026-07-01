# Vertigo Extensions: Libs and Modules

Vertigo follows modular programming paradigms. It is therefore divided into modules, each with a clear purpose.

The underlying principle is: 1 recurring business application challenge = 1 Vertigo module

Naturally, when challenges are closely related, they are encapsulated within the same module.

The modules listed here are those that form the central core of Vertigo. They are designed to be used together, providing a cohesive whole for creating Java applications.
These modules are extensions because they enrich a Vertigo application and provide solutions to one or more business application challenges.
We classify these extensions into two groups: *libs* and *modules*.
*Libs* are primarily components aimed at solving technical challenges, while *modules* are akin to functional modules and aim to solve a business challenge as a whole [Libs overview](overview/libs).
*Modules* generally provide a service API, a data model, and sometimes a UI.

Below is the list of *Modules* along with a brief description of their contents.


## vertigo-social

> Adds collaborative features to your application to improve communication with and among your users.

* __notification__: Send notifications to your users without relying on third-party services
* __comment__: Information sharing spaces for unstructured content to improve the operational efficiency of the application
* __mail__: Send emails with ease
* __sms__: Send SMS messages
* __handle__: (Beta feature): Associate meaningful 'handles' with your application's entities, enabling simplified external referencing and improved application navigation.

[Access the documentation](modules/social)

## vertigo-orchestra

> A control tower and scheduler for long and scheduled processes (commonly called batches), enabling application supervision by a technical-functional administrator.
> This module provides a base VueJS UI.

* __definition__: defines the managed processes
* __schedule__: schedules recurring executions or delegates this processing to third-party solutions
* __execute__: executes processes using various strategies while minimizing impact on the host application

[Access the documentation](modules/orchestra)

## vertigo-quarto

> Manages publications and document generation with data merge.

- __publisher__: Simple and lightweight publishing tool. Produces documents from user-defined document templates and application data. Templates are easy to modify as they are ODT or DOCX documents with markers.
- __converter__: Converts documents between formats (existing plugins support: ODT, DOC, DOCX, RTF, TXT to PDF)
- __export__: Exports collections or business objects to utility formats (existing plugins support: CSV, PDF, RTF, XLS)

[Access the documentation](modules/quarto)

## vertigo-audit

> Records critical actions within an application to create audit trails

- __ledger__: Uses Blockchain mechanisms to securely trace important information (supports Ethereum blockchain, public and/or private, and/or sidechain)
- __trace__: Traces actions using various strategies (log, db, etc.)

[Access the documentation](modules/audit)

## vertigo-dashboard

> Provides an out-of-the-box dashboard for monitoring application performance and health without depending on a third-party product.

This module is likely to be significantly reworked / relocated in the near future.

[Access the documentation](modules/dashboard)

## vertigo-geo

> Adds a geographic dimension to your business entities and your application

* __geocoder__: Convert positions to addresses and vice versa, via various services (GoogleMaps and BAN included)
* __geosearch__: Use mapping functions to search for business entities within a geographic zone (ElasticSearch included)

[Access the documentation](modules/geo)


## vertigo-easyforms

> Adds a dynamic form tool to your application. This module is designed to allow functional administrators to adapt forms that require flexibility.
> This module provides a VertigoUi-based UI.

[Access the documentation](modules/easyforms)


## vertigo-planning

> Adds a scheduling tool to your application. This module offers both slot planning (BackOffice side) and slot selection (FrontOffice side).
> This module provides a VertigoUi-based UI.

[Access the documentation](modules/planning)
