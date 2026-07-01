# Glossary / Vertigo Concepts

Here is a list of key, foundational concepts that are essential to keep in mind when getting started with **Vertigo**.


## Core

### Module *(concept)*

`Modules` represent a concept for partitioning application or technical code. They are a coherent grouping of a set of services, objects, and implementations around a broader concept that makes sense.
`Modules` have a reasonable granularity for proper dependency management, both in terms of entry points (inter-API dependencies) and orientation.
For example: `Dynamo` module around data management and storage. `Vega` module around WebService management. `Studio` module around project tooling and development management (including MDA).

### Extension *(concept)*

`Extensions` are a particular type of module: out-of-the-box and optional. `Extensions` aim to deliver a complete vertical functionality (from the UI to storage), addable to the application with minimal effort.

### Component *(interface)*

`Components` in the **Vertigo** sense represent all objects managed by **Vertigo** dependency injection.
Components are application-level singletons and should therefore remain stateless.
This is simply a declarative marker.

### Manager *(interface)*

`Managers` are `Components`. They represent high-level service facades for cross-cutting or technical processing.
They are essentially APIs with a strong **DX** (*Developer Experience*) constraint: simple to use and understand, focused on business use cases.
Example: SearchManager, NotificationManager, ...

### Plugin *(interface)*

`Plugins` are also `Components`, they are intended to be linked to and used exclusively by a `Manager`.
They represent implementation options for a specific need, required to deliver their `Manager`'s service.
They systematize the decoupling between the application core and required third-party dependencies.
This principle ensures the longevity and stability of applications: the evolution or replacement of a third-party library is absorbed by the affected plugin.

### Connector *(interface)*

`Connectors` are also `Components`, they are intended to be linked to and used either by `Plugins` or by other components.
They allow configuration and direct access to third-party library/product clients without an intermediary API.
The native `Plugins` in Vertigo use `Connectors` when they rely on a third-party library or product. These connectors can then be reused directly by the application developer when strictly needed.

### Definition *(interface)*

`Definitions` represent information carriers. Where `Managers` carry processing logic, `Definitions` carry data descriptions.
Generally, any element used to establish the model (everything related to data) is carried by a `Definition`.
`Definitions` are used **to model** the business domain. They are unique, loaded at server startup, and immutable.

### BasicType *(concept)*

All Vertigo modules handle a finite set of data types. These are primary types (basic types).
They represent the common denominator, ensuring **full compatibility** of complete data types across all Vertigo modules.

### VUserException, VSystemException, WrappedException *(class)*

With its *Opinionated Architecture* approach, **Vertigo** proposes exception handling in applications based on `Un-checked` exceptions (Runtime and loosely typed).
Overall, in an application, `Exceptions` never need to be caught by the developer; the framework handles everything, already including the necessary interceptions at key locations.

Three types are used:

- `VUserException`: For exceptions corresponding to a business rule (screen validation, validation, or business rule). The exception is associated with a message and possibly a screen field and will be presented to the user indicating what happened.
- `VSystemException`: For exceptions corresponding to a system error (Assertions, I/O errors, etc.)
- `WrappedException`: For wrapping technical exceptions, allows encapsulating a third-party technical error to let it bubble up to Vertigo's interception.

## Data-Model

### SmartType *(concept)*

`SmartType`s are the first level of model declaration and as such are `Definitions`.
They represent a *super-type*, a strong data typing enriched with metadata to multiply its capabilities.
Generally, a `SmartType` has: a Java type, carries validation (with a list of constraints), a formatter and adapters, and complementary metadata: SQL storage type, display field size, unit for quantities, etc.

`SmartType`s define `Adapter`s to bi-directionally transform data into a `BasicType` (example: a POJO with various properties can be transformed into the **String** `BasicType` via JSON serialization)

In `Vertigo`, the `SmartType` replaces the notion of Java type in declarations, so the declaration of inputs/outputs in `Tasks` (see below) uses the `SmartType` notion.
However, in Java code, it is the Java type that is used (for example a `String` for a *SIRET* `Domain`).

### DtObject *(interface)*

The `DtObject` is one of the most important objects for data management in **Vertigo**.
It represents the data transfer object, spans all layers (from UI to database), and simplifies the application by avoiding numerous copies and conversions.
Concrete objects implementing `DtObject` are annotated POJOs and can be created manually or generated through the `Studio` module.

### Entity *(interface)*

`Entity`s are persistent `DtObject`s. They possess an identifier.

### KeyConcept *(interface)*

`KeyConcept`s are key `Entity`s of the application. This interface is a marker that helps understanding and maintaining the application over time by identifying main business objects.
**Vertigo** APIs use this notion to guide developers.

### DtList *(interface)*

`DtList`s are **typed lists** of `DtObject`s. This interface compensates for the absence of strongly typed lists in Java and makes lists span from UI to storage.



### Constraint *(interface)*

`Constraints` represent the validations associated with a `SmartType`. `Vertigo` provides many standard `Constraints` out of the box, and it is very simple to add more. Standard `Constraints` can have parameters to adapt their behavior or change the error message.
`Constraints` are applied and validated automatically when user-entered data is integrated into the system (i.e., on entered data). It is possible to force constraint validation.
Generally, a constraint violation generates a user exception.


### Formatter *(interface)*

`Formatters` are converters associated with a `SmartType`. They allow transforming data from its typed manipulation format in Java services to a string handled by the user. `Formatters` are bidirectional and are often more permissive when translating user input to the technical type (a date can be entered as 10/01/2019 or 10/01/19 or 10/1/19 or 10 01 19).
Overall, they are used (*automatically*) during communication with the UI or in data exports.


### Task *(concept)*

`Task`s are definitions; they represent access points to a data source. They consist of input and output parameters, a query, and an execution engine.
By default, the most commonly used engine is the one for executing SQL queries.
This is the most common use case for `Tasks`; they are used to declare specific SQL queries used in the application.
Through this mechanism, **Vertigo** promotes efficient and controlled database access: simple accesses (i.e., without operational risk, typically CRUD with or without criteria) are automated, complex accesses (with joins or specific behaviors) are externalized to a resource file in native SQL syntax for full behavioral control.


### @Transactional *(annotation)*

`@Transactional` is one of the annotations provided by **Vertigo**. It is presented here because it is crucial in business applications.
As its name suggests, it adds transactional behavior to a method (through an *AOP* principle).
It is intended to be placed on service facades and behaves as **REQUIRED**, meaning the annotation ensures a transaction is present: if none exists, one is created; if one already exists, it is reused.

## Studio

### MDA: Model Driven Architecture *(concept)*

The notion of `MDA` (for *Model Driven Architecture*) describes the practice of using data declarations as the supporting structure of the application.
**Vertigo** guides development toward this type of approach, where the declarative structure of the **Model** (everything related to data) supports the rest of the application: the separation into modules (functional partitioning) and layers (technical partitioning).
**Vertigo** provides a code generation module that allows this principle to be put into practice quickly, consistently, and reproducibly: generated code is not modified by the developer, it is always kept consistent with the model declaration.

### Domain *(concept)*

Domains allow declaring data types usable in an application within Studio.
There are two types of `Domain`: those based on a `BasicType` and those using any other Java class (preferably a *ValueObject* type class).
`Domain`s also have other useful properties to complete their definition.

### KSP *(file)*

KSP files are text files that allow developers to design their application and declare the **Model** definition. These files are self-sufficient, but the data model can also be supplemented with files from third-party modeling tools (OOM or XMI).
KSP files use a syntax close to JSON to remain readable and flexible, even for someone external to the project or a non-developer such as a project manager or a DBA.
Overall, they allow declaring all Vertigo definitions.

The **Model** elements most commonly declared in *KSP* files are:

- Domain
- DtObject: non-persisted objects such as UI objects; the others are usually in the data model (OOM or XMI)
- Task: SQL queries thus remain outside the code, properly indented and readable.

### KPR *(file)*

KPR files are text files that allow referencing other KPR or KSP files. These control the partitioning of KSP files.
