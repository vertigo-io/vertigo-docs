# Vertigo : Boost your apps

?> Boost your apps, or how to create value in your projects, better and faster

[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

**Vertigo** is a Java platform for building modern, complete, maintainable, and scalable business applications or information systems.

It is designed to maximize value delivery:
- simple things are done simply,
- more complex things are added via *plug-ins* while minimizing their impact,
- several high-value building blocks are provided *out-of-the-box*: modern UI, search, security, analytics, dataviz...

The automotive industry popularized the concept of "platform", enabling different models—sedan, compact, SUV...—to be rapidly created from a common base.
A series of options and customizations are layered on top, offering a wide range of choices while sharing costs, minimizing industrial risks, and maximizing customer value.

**Vertigo**, the application of this principle to information systems and digital services, consists of a core application engine guaranteeing robustness, quality, and development efficiency.
Innovative options can be plugged onto this core and activated based on business objectives.
**Vertigo** is an **Opinionated** platform (i.e. an *Opinionated Software Development Framework*—a framework that takes clear stances on architecture and best practices).
This approach maximizes development efficiency for "management applications"—highly effective in its domain while still allowing you to go beyond it. Where other general-purpose frameworks offer average efficiency across a very broad (*too broad?*) range of application scenarios.

**Vertigo**, as the application core of the platform, natively includes all components essential to a modern application: search, security, mobility, analytics, dataviz...

## Architectural choices

Because an *Opinionated* platform stands by its convictions, Vertigo rests on five technical pillars that protect your projects from the typical pitfalls of business applications. Each choice eliminates a source of complexity, bugs, or rework.

- **MDA Architecture (Model Driven)**: Your model declarations are the single source of truth. Code, interfaces, web services, and storage are auto-generated—synchronization guaranteed, no divergences.
- **Strong typing (SmartTypes, BasicTypes)**: A price stays a price, a date stays a date. Validated upon entry into the system, they preserve data integrity everywhere (UI, database, JSON) and eliminate formatting errors.
- **No checked exceptions (Runtime only)**: Business logic should not be polluted by mandatory technical exception handling. Vertigo manages errors in a centralized manner, for cleaner code and faster development.
- **ComponentSpace / DefinitionSpace separation**: Fixed structure at startup, immutable and non-corruptible at runtime. Result: maximum robustness, predictable behavior, and enhanced production security.
- **Hybrid Server-Side / Client-Side UI**: The platform combines the reliability of server-side rendering for structure with the fluidity of VueJS for interaction. The best of both worlds, without the complexity of a pure SPA.

Vertigo is composed of:

- [**Vertigo-Core**](/en/overview/core): An ultra-powerful and super-light Java engine
- [**Vertigo-Libs**](/en/overview/libs): A collection of extension modules addressing all key challenges of business applications, enabling rapid development
- [**Vertigo-Connectors**](/en/overview/connectors): A collection of low-level connectors to third-party libraries and products, simplifying edge-case development
- [**Vertigo-Studio**](/en/overview/studio): A dedicated design tool for business applications to gain efficiency and consistency
