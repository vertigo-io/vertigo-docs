# Coding rules and conventions

Vertigo's [philosophy](/en/intro/philosophie) sets the course: simple, modular, fast. These principles only matter if they show up in the code, line by line. This page describes the concrete rules applied throughout the framework — and that we recommend applying in the applications built with it.

## Ban null

Vertigo applies *design by contract* as formalized by Bertrand Meyer (the Eiffel language): every method states a contract — what it requires from its arguments, what it guarantees in return — and checks it **at runtime, as early as possible**.

The tool is the `Assertion` class (`io.vertigo.core.lang`), a fluent API placed at the top of every public method:

```java
public MovieDisplay getMovieDisplay(final Long movieId, final String locale) {
	Assertion.check()
			.isNotNull(movieId, "Movie id is mandatory")
			.isNotBlank(locale, "Locale {0} must be provided", locale);
	// ---
	final Movie movie = movieDAO.get(movieId);
	return toDisplay(movie, locale);
}
```

The associated rules:

- **The assertion block opens the method**, separated from the body by a `// ---` marker. When reading a method, the contract is visible at a glance; everything after the separator can assume the contract is fulfilled.
- **Distinguish contract from state**: `isNotNull` / `isNotBlank` check the *arguments* (the contract towards the caller), `isTrue` / `isFalse` check a *condition* — typically the object's internal state. The thrown exceptions follow this distinction (`NullPointerException` / `IllegalArgumentException` for the contract, `IllegalStateException` for the state).

```java
public void start() {
	Assertion.check()
			.isFalse(started, "Component is already started");
	// ---
	started = true;
}
```

- **A public API never returns null**: an optional result is an `Optional<T>`. The caller is forced to handle the absence; the compiler works for you.
- **A collection is never null**: at worst it is empty. `for` and `stream()` then work without any guard.

The benefit is twofold: the error blows up **as close as possible to its cause** (an invalid argument is detected at the method's entry point, not three layers below in an anonymous `NullPointerException`), and method bodies are free of the defensive `if (x != null)` checks that inflate cyclomatic complexity without guaranteeing anything.

## Favor immutability

An immutable object can never be observed in an inconsistent state: once built, it is final. The rules:

- state is **injected through the constructor** (and validated with assertions);
- **no setters**;
- classes and fields declared **`final`**;
- exposed collections are wrapped with `Collections.unmodifiableList` / `unmodifiableMap`...

```java
public final class MovieInfo {
	private final String title;
	private final List<String> tags;

	public MovieInfo(final String title, final List<String> tags) {
		Assertion.check()
				.isNotBlank(title)
				.isNotNull(tags);
		// ---
		this.title = title;
		this.tags = Collections.unmodifiableList(new ArrayList<>(tags));
	}

	public String getTitle() {
		return title;
	}

	public List<String> getTags() {
		return tags;
	}
}
```

The benefit: **thread-safety by construction** (no synchronization to write, no shared mutable state) and **local reasoning** — the value of an immutable object depends neither on the moment nor on the path through which it reaches you.

## Builders and fluent style

Immutability and option-rich objects are reconciled through the **Builder** pattern: the builder is mutable and guides the construction, the built object is immutable. Vertigo formalizes it with the `io.vertigo.core.lang.Builder<T>` interface, ubiquitous in the framework (`NodeConfig`, `ModuleConfig`, `SearchQuery`...):

```java
public interface Builder<T> {
	T build();
}
```

A real example, the configuration of a node (see [Configuration](/en/basic/configuration)):

```java
final NodeConfig nodeConfig = NodeConfig.builder()
	.addModule(new CommonsFeatures().build())
	.addModule(new VegaFeatures()
		.withWebServices()
		.build())
	.addModule(ModuleConfig.builder("Hello")
		.addComponent(HelloWebServices.class)
		.build())
	.build();
```

The naming conventions carry the meaning:

- **`with...`**: the element is set **at most once** (an embedded server, an application name...);
- **`add...`**: the call is **repeatable**, each call adds an element (a module, a component...).

The `build()` method validates the consistency of the whole (with assertions) and returns the final object. Configuration code then reads like a description, not like a sequence of assignments.

## Util vs Helper

Two families of classes support the code, not to be confused:

- **Util**: a **static, stateless** class, therefore threadsafe by nature. Examples in `io.vertigo.core.util`: `StringUtil` (message formatting, camelCase/CONST_CASE conversions), `ClassUtil` (introspection), `BeanUtil` (property access).

```java
final String columnName = StringUtil.camelToConstCase("movieTitle"); // MOVIE_TITLE
```

- **Helper**: a **stateful** class whose constructor takes the object to manipulate; its methods then work on that object. A helper is instantiated as close as possible to its use and is not shared between threads.

```java
final MovieHelper movieHelper = new MovieHelper(movie);
movieHelper.applyDefaultRating();
```

If a `Util` class keeps accumulating parameters passed on every call, it's a sign a `Helper` is a better fit — and conversely, a stateless helper has no reason to be instantiated.

?> Note: `DateUtil` is now only used for parsing **relative date expressions** (`parseToLocalDate` / `parseToInstant`, e.g. `"now+8d"`), used in particular by search range facets. For everything else, `java.time` covers the need.

## Loggers

The default rule: **one logger named after the class**, following the structure of the code.

```java
private static final Logger LOG = LogManager.getLogger(MovieServices.class);
```

In addition, Vertigo uses **category loggers** to extract a cross-cutting stream, independently of the classes producing it: `sql` (SQL queries), `tasks` (Task execution), `health`, `metric`. Both approaches coexist: the class to locate the code, the category to follow one kind of event end to end. The log4j2 configuration drives each stream separately:

```xml
<Logger name="sql" level="info" additivity="false">
	<AppenderRef ref="sqlAppender" />
</Logger>
```

Finally, the **SmartLogger** of the analytics module (`SmartLoggerAnalyticsConnectorPlugin`) logs processes **by category** with a duration threshold `durationThreshold` (1000 ms by default): below the threshold a process is logged as INFO, above it switches to **ERROR** — abnormally slow processes stand out in the logs by themselves.
