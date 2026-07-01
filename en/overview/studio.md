# vertigo-studio

Vertigo-Studio is a dedicated design tool for business applications to improve efficiency and consistency.

It is usable by designers and project managers, but especially by developers.

This provides a common language while also enabling all project stakeholders to work on a neutral, editable medium.

Vertigo currently covers the following aspects of application design:

- business entity modeling
- security rules (authorization/operations)
- data operations
- web service APIs

The core concept of Vertigo-Studio is the __notebook__.
It is essentially the application's notebook, describing its operation—at least its main outlines.
A __notebook__ contains a set of __sketches__ for each type of object designed within Studio (DtSketch, TaskSketch, FacetedQuerySketch).

Studio operates as follows:

1. Build a __notebook__
2. Use that __notebook__ to deliver high-value services

The strategy for building a notebook consists of reading multiple source files through specialized `Reader` instances.
Each `Reader` reads the source files it handles and enriches the __notebook__ with numerous __sketches__.

Currently, the main types of usable sources are:

- ksp/kpr
- oom
- xmi (EnterpriseArchitect)
- json files
- Java classes

Among the high-value services available from the notebook:

- Java class generation (Entities, DAO, Search...)
- SQL script generation
- JavaScript file generation
- TypeScript file generation
- Model visualization generation

## KSP

To model a business application effectively and use a medium accessible to all project stakeholders, we created a grammar dedicated to this purpose.
It is specifically designed to be:

- concise
- unambiguous
- intuitive

Furthermore, the use of "text" files makes them natively supported by source control tools. Differences between versions can be viewed easily, collaboration is improved, etc.

To facilitate adoption, the format is close to JSON but streamlined and improved for our needs.

KSP stands for Domain Specific Language—a language adapted to a specific challenge: the design of business applications.

To support this DSL and simplify its use, we created an ecosystem of tools for integration with market-leading IDEs:

- an **Eclipse plugin** available on the Eclipse marketplace [here](https://marketplace.eclipse.org/content/vertigo-3-dsl-plugin)
- a **Visual Studio Code extension** available [here](https://marketplace.visualstudio.com/items?itemName=vertigo-io.vertigo-vscode)
- a **language-server** for integration into other IDEs

These tools provide:

- **syntax highlighting**
- **autocompletion** and **syntax verification**
- **grammatical** verification
