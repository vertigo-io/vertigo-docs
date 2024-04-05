# vertigo-studio

Vertigo-Studio is a design tool dedicated to business applications to gain efficiency and consistency.

It can be used by both designers, project managers, and especially developers.

This allows both to have a common language and also to work on a neutral support editable by all project stakeholders.

Vertigo currently covers the following aspects of application design:

- modeling of business entities
- security rules (authorization/operations)
- data manipulations
- webservices APIs

The main concept of Vertigo-Studio is the __notebook__.
It is somewhat the notebook of the application, which describes its operation, or at least its main lines.
A __notebook__ contains a set of __sketch__ (or sketches) for each type of object designed within Studio (DtSketch, TaskSketch, FacetedQuerySketch)

The operation of Studio is therefore as follows:

1. Constitute a __notebook__
2. Use this __notebook__ to provide value-added services

The strategy of constituting a notebook is done by reading multiple source files by specialized `Readers`.
Each `Reader` will read the source files it supports and enrich the __notebook__ with numerous __sketches__.

To date, here are the main types of usable sources:

- ksp/kpr
- oom
- xmi (EnterpriseArchitect)
- json file
- java classes


Among the value-added services available from the notebook:
 
- generation of Java classes (Entities, DAO, Search...)
- generation of SQL script
- generation of JavaScript files
- generation of TypeScript files
- generation of model visualization

## KSP

To effectively model a business application and use a support usable by the different project stakeholders, we have created a grammar dedicated to this problem.
It is specially designed to be both:

- concise
- unambiguous
- intuitive

On the other hand, the use of "text" file makes its native support in source management tools. It is then possible to simply visualize the differences between several versions, collaborate better with several, etc...

To facilitate its adaptation it is quite close to a JSON format but purified and improved for our needs.

KSP is therefore indeed a DSL for Domain Specific Language, that is to say a language adapted to a specific problem: the design of business applications.

To accompany this DSL and simplify its use we have created an ecosystem of tools to integrate it into the IDE market:

- an **Eclipse plugin** available on the eclipse marketplace [here](https://marketplace.eclipse.org/content/vertigo-3-dsl-plugin)
- a **Visual Studio Code extension** available [here](https://marketplace.visualstudio.com/items?itemName=vertigo-io.vertigo-vscode)
- a **language-server** for integration into other IDEs

These tools provide:

- **syntax coloring**
- **autocompletion** and **syntax verification**
- **grammatical** verification