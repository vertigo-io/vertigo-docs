# Components

Components are objects that provide services.
They must at minimum implement the `io.vertigo.core.node.component.Component` interface, which is nothing more than a simple marker, or implement a business interface that formalizes the services offered.

!> Components are singletons, they must therefore have **threadsafe** behavior. A simple way to ensure this is to make them completely **stateless** objects.

Here are the main types of components used in a Vertigo project:
- **Managers** which are Vertigo's internal components and offer essential features (e.g.: `StoreManager`, `AuthorizationManager`, etc.)
- **DAOs** which encapsulate data access. These components are generally generated (see MDA)
- **Services** which contain the project's business logic and therefore offer high-level services. Vertigo extensions also provide high-level services.
- **WebServices** which generally consume business services and expose them as REST webservices


## Construction

Components are instantiated by the injection engine and are usable by other components through this same dependency injection mechanism.

To be created, a component must have either:

- no constructor (so the default constructor will be used)
- one (and only one) declared public constructor. When a constructor is declared, it must carry the `@Inject` annotation.


It is possible to inject into a component, either as instance variables or as constructor parameters, the following elements:

- a primitive type parameter carrying the `@ParamValue` annotation to specify its name
- a component
- a plugin
- a list of plugins of the same type


```java
@Inject
public Calculator3(@ParamValue("offset") final Optional<Integer> offset) {
	this.offset = offset.orElse(0);
}
```

?> Parameter injection allows handling `Optional`s when they can be null


```java
@Inject
public Calculator6(final List<OperationPlugin> operationPlugins) {
	operationDispatcher = new HashMap<>();
	for (final OperationPlugin operationPlugin : operationPlugins) {
		operationDispatcher.put(operationPlugin.getOperator(), operationPlugin);
	}
}
```

```java
@Inject
private OperationPlugin operationPlugin;
```

```java
@Inject
@ParamValue("log")
private boolean log;
```

## Usage

To be used by a process, a component must be retrieved within the object that requires the use of this component.

This object is often itself a component, and in that case dependency injection must be used to retrieve the instance and thus call the methods offered by the component.

> The class that must be used during injection (Calculator1 in the example below) is the interface when the component implements an interface, or its implementation class otherwise.

```java
@Inject
private Calculator1 calculator1;
```

?> This mechanism is available across all classes handled by the developer. It should be preferred.

> This is the case for DAOs used by business services, or business services themselves used by webservices.

When the object is not itself a component and therefore not created by the injection engine, it is possible to manually activate dependency injection:
- either during instance creation:
```java
DIInjector.newInstance(Samples.class, Node.getNode().getComponentSpace())
```
- or afterward:
```java
final Samples sample = new Samples();
DIInjector.injectMembers(sample, Node.getNode().getComponentSpace());
```

## Direct Access to Component Registry

It is also possible to retrieve the component directly from the component space.

```java
final Calculator2 calculator2 = Node.getNode().getComponentSpace().resolve(Calculator2.class)
```
!> Warning: this practice should only be used in very specific (and extremely rare) cases where injection is not available.

The services offered by this component can then be used

```java
calculator1.sum(1, 2, 3, 4);
```

## Behavior

The following behaviors can be added to components:
- `Activeable`: allows having entry points at component startup and shutdown

```java
@Override
public void start() {
}

@Override
public void stop() {
}
```

- `DefinitionProvider` and `SimpleDefinitionProvider`: allows enriching the definition space
```java
@Override
public List<Definition> provideDefinitions(final DefinitionSpace definitionSpace) {
	return Collections.emptyList();
}
```

## Example

Here is an example of a business service that can be implemented with Vertigo. It uses another DAO component as well as a `@Transactional` aspect to manage the transactionality of service methods.

```java
@Transactional
public class MovieServicesImpl implements MovieServices {

	@Inject
	private MovieDAO movieDAO;

	@Override
	public Movie getMovieById(final Long movId) {
		Assertion.checkNotNull(movId);
		// ---
		return movieDAO.get(movId);
	}

}
```
