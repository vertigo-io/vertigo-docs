# Commons

**vertigo-commons** groups the platform's cross-cutting components: codec management, event bus, topology discovery, script execution, command system, transaction management, and PEG parsing engine.

The module follows the modularity principle and implements the Strategy design pattern like other Vertigo modules.

Components are orthogonal and are typically consumed by higher-level modules. Activation is done via YAML features or the Java API. For more details, refer to the [configuration](/en/basic/configuration) chapter.

Five components start automatically: CodecManager, EventBusManager, AppManager, VTransactionManager, and VTransactionAspect. Others require a feature declaration.

---

## Codec

`CodecManager` centralizes thirteen thread-safe, stateless encoders/decoders.

### Principle

Two interfaces structure the codec:
- `Codec<S,T>` — bijective transformation (encode + decode)
- `Encoder<S,T>` — unidirectional transformation (encode)

Each codec is instantiated once, then reused without contention. Codecs automatically handle null values via the `NullCodec` decorator.

### Available Codecs

| Category | Codecs |
|---|---|
| **Text Encoding** | HTML, Base64 URL-safe, Base64 Legacy |
| **Crypto** | TripleDES, AES-128 |
| **Hashing** | MD5, SHA-1, SHA-256 |
| **Format** | Hex, CSV |
| **Serialization** | Serialization, CompressedSerialization |
| **Compression** | Compression (GZIP) |

### Activation

No declaration required. The component activates automatically at module startup.

---

## EventBus

`EventBusManager` implements a synchronous, intra-machine event bus using the pub/sub pattern.

### Principle

Flow:
1. An event implements the marker interface `Event`
2. A subscriber annotates a method `void onXxx(MyEvent e)` with `@EventBusSubscribed`
3. The annotation triggers automatic registration at startup
4. `post()` dispatches the event synchronously to all subscribers
5. If no subscriber is found, the event routes to the `registerDead` handler

### Annotations

| Annotation | Target | Role |
|---|---|---|
| `@EventBusSubscribed` | Method | Automatically registers the method as a subscriber. Signature must be `void(MyEvent)` |

### Activation

No declaration required. The component activates automatically at module startup.

---

## App

`AppManager` manages execution node topology in a multi-node environment.

### Principle

Each node is represented by an `AppNode` (id, app name, last status, last contact, start date, entry point, skills). A 60-second heartbeat is emitted periodically. A node is considered dead after two missed heartbeats (120 seconds).

Discovery relies on two extensible plugin chains:
- **Registry** — node registry (stores the list of active nodes)
- **Infos** — per-node detailed information source

### Registry Plugins

| Plugin | Topology | Role |
|---|---|---|
| `SingleAppNodeRegistryPlugin` | Default | Local in-memory registry (single-node) |
| `DbAppNodeRegistryPlugin` | Feature `app.dbRegistry` | Shared registry via JDBC (C3P0 pool, table `V_NODE`) |
| `RedisAppNodeRegistryPlugin` | Feature `app.redisRegistry` | Shared registry via Redis (depends on `RedisConnector`) |

### Infos Plugins

| Plugin | Feature | Role |
|---|---|---|
| `HttpAppNodeInfosPlugin` | `app.httpInfos` | Remote node retrieval via REST HTTP (500 ms timeout) |

### Custom Plugin

The Java API exposes two methods on `CommonsFeatures` to inject plugins without YAML features:
- `withNodeRegistryPlugin(Class<? extends AppNodeRegistryPlugin>, Param...)`
- `withNodeInfosPlugin(Class<? extends AppNodeInfosPlugin>, Param...)`

### Activation

No declaration required for the local registry. Features `app.dbRegistry`, `app.redisRegistry`, and `app.httpInfos` require a feature.

`DbAppNodeRegistryPlugin` requires JDBC driver and connection URL configuration. `RedisAppNodeRegistryPlugin` requires an active `RedisConnector`.

---

## Command

`CommandManager` handles **application command** execution — business operations exposed as command endpoints.

### Principle

An application command is a method annotated with `@Command(handle, description, questions)` that:
1. Accepts parameters of type `String` or `GenericUID<O>`
2. Returns `CommandResponse<P>` building the status (OK/KO), display text, optional payload, and target URL

`CommandManagerImpl` auto-discovers annotated methods, assembles their definition (`CommandDefinition` with prefix `Cmd`), and executes them with parameter validation. `CommandResponseBuilder<P>` simplifies result construction.

### Annotations

| Annotation | Target | Role |
|---|---|---|
| `@Command` | Method | Declares a method as an application command. Attributes: `handle` (identifier), `description`, `questions` (expected parameters) |

### Types

| Type | Role |
|---|---|
| `CommandResponse<P>` | Record: `status` (enum OK/KO), `display`, `payload`, `targetUrl` |
| `CommandResponseStatus` | Enum: OK, KO |
| `CommandResponseBuilder<P>` | Fluent builder for `CommandResponse` |
| `GenericUID<O>` | Absolute resource identifier (URN, type, serializable identifier) |
| `CommandParam` | Record describing a command parameter (reflected type) |
| `CommandDefinition` | Command definition (`@DefinitionPrefix("Cmd")`) |

### Activation

Feature `command` required.

---

## Script

`ScriptManager` evaluates textual scripts mixing Java code and data, with strongly-typed parameter injection.

### Principle

A script is text containing delimited tags. `ScriptParser` parses text sequence by sequence and delegates each code segment to the selected implementation:
1. Separators are configurable via `SeparatorType` (XML `<% %>`, CLASSIC, XML_CODE `<# #>`)
2. Parser calls a `ScriptParserHandler` per expression block and per text block
3. `ScriptEvaluator` coordinates Parser → Handler → Runtime compiler
4. The compiler implements `ExpressionEvaluatorPlugin` (interface `evaluate(expression, params, type)`)

Parameters are injected via `ExpressionParameter` (name, type, value).

### Annotations

None. Integration relies on the `ExpressionEvaluatorPlugin` plugin.

### Activation

Feature `script` required. Feature `script.janino` adds the Janino implementation (only provided implementation).

---

## Transaction

`VTransactionManager` orchestrates application transactions with REQUIRED propagation, lifecycle hooks, and prioritized resource management.

### Principle

The model supports:
- Thread-local transactions with nesting support
- REQUIRED propagation via `@Transactional`
- Resource registration (`VTransactionResource`) with TOP or NORMAL priority
- Hooks `beforeCommit` and `afterCompletion` (committed or rollback)
- Logging via `VTransactionListener` (`VTransactionListenerImpl` with log4j trace)

The internal state machine distinguishes ALIVE and CLOSED states.

### Interfaces

| Interface | Role |
|---|---|
| `VTransactionManager` | Creates, retrieves, and verifies current transactions (`createCurrentTransaction`, `createAutonomousTransaction`, `getCurrentTransaction`, `hasCurrentTransaction`) |
| `VTransaction` | Read transaction: `addResource`, `getResource`, `addBeforeCommit`, `addAfterCompletion` |
| `VTransactionWritable` | Extends `VTransaction` for write: `commit`, `rollback`, `close` |
| `VTransactionResource` | Resource registered to a transaction: `commit`, `rollback`, `close` |
| `VTransactionResourceId<R>` | Resource identifier with `Priority` (TOP > NORMAL) |
| `VTransactionAfterCompletionFunction` | `@FunctionalInterface` function: `afterCompletion(boolean committed)` |

### Annotations

| Annotation | Target | Role |
|---|---|---|
| `@Transactional` | Method or class | `@AspectAnnotation` aspect activating REQUIRED propagation on method or entire class. Applied by `VTransactionAspect` |

### Activation

No declaration required. `VTransactionManager` and `VTransactionAspect` activate automatically at module startup. `VTransactionAspect` is required for `@Transactional` to take effect.

---

## PEG Parser

Package `io.vertigo.commons.peg` provides a *Parsing Expression Grammar* combinator engine for building DSL parsers. This is a utility library — no component is registered as a Vertigo feature.

### Principle

The PEG Parser relies on rule composition via static factory `PegRules`:
- **Atomic rules**: `term()`, `word()`, `blanks()`, `skipBlanks()`
- **Compositional rules**: `named()`, `optional()`, `sequence()`, `choice()`, `zeroOrMore()`, `oneOrMore()`
- **Deferred rules**: `delayedOperation()`, `delayedComparison()`, `delayedOperationAndComparison()` (Shunting Yard evaluation)
- **Utils**: `parseAll()` for full parsing, `namedRulesAsHtml()` for HTML rendering of a grammar

Each `PegRule<R>` exposes `getExpression()` for textual representation and `parse(text, start)` for execution. Result is `PegResult<R>` (final index, parse value, best incomplete rule on error).

Errors generate `PegNoMatchFoundException` with context and inverted error stack. Debugging is done via `PegLogger` (disabled by default, `DISABLED = true`).

### Terms and operators

Interface `PegTerm` (method `getStrValues()`) is implemented by six predefined enumerations:

| Enum | Values | Role |
|---|---|---|
| `PegCompareTerm` | LTE, GTE, NEQ, EQ, LT, GT | Comparison operators |
| `PegBracketsTerm` | OPEN `(`, CLOSE `)` | Parentheses |
| `PegBoolOperatorTerm` | OR (prio 1), AND (prio 2) | Boolean operators |
| `PegArithmeticsOperatorTerm` | PLUS/MINUS, MULTIPLY/DIVIDE | Arithmetic operators |

Interface `PegOperatorTerm<T>` describes a binary operator with priority and `apply(left, right)` method.

Helper `PegEnumRuleHelper` simplifies building rules on `PegTerm` enums.

### Solver

`PegSolver<S,I,R>` (functional interface) encapsulates a raw → qualified transformation via `PegSolver.PegSolverFunction<S,I>` which exposes `identity()` as the identity function.

### Types

| Type | Role |
|---|---|
| `PegRule<R>` | Rule: `getExpression()`, `parse(text, start)` |
| `PegRule.Dummy` | Singleton for rules without result |
| `PegAbstractRule<R,M>` | Wrapper delegating to a main rule |
| `PegRules` | Static factory (private constructor) with 18+ build methods |
| `PegResult<R>` | Result: index, value, best incomplete rule |
| `PegChoice` | Choice result: index + value |
| `PegNoMatchFoundException` | Exception with context and error stack |
| `PegParsingValueException` | Exception for unparseable value |

### Detailed PEG Rules

| Rule | Signature | Role |
|---|---|---|
| `PegRules.named()` | `(name, rule)` | Labels a rule, returns a `PegGrammarRule` |
| `PegRules.optional()` | `(rule)` | Matches 0 or 1 occurrence |
| `PegRules.term()` | `(terms)` | Matches a `PegTerm` |
| `PegRules.sequence()` | `(rules...)` | Sequential chaining |
| `PegRules.choice()` | `(rules...)` | Matches first successful rule, returns `PegChoice` |
| `PegRules.zeroOrMore()` | `(rule, untilEnd)` | Matches 0 or more (`*`) |
| `PegRules.oneOrMore()` | `(rule, untilEnd)` | Matches 1 or more (`+`) |
| `PegRules.parseAll()` | `(rule)` | Verifies all text is consumed |
| `PegRules.word()` | `(chars, mode)` | Recognized character string (`PegWordRuleMode`) |
| `PegRules.blanks()` | `(blanks)` | Whitespace (space, tab; default " \t") |
| `PegRules.skipBlanks()` | `(blanks)` | Whitespace and newlines (default " \t\n\r") |
| `PegRules.operation()` | `(operators, term)` | Expressions with operators (immediate evaluation) |
| `PegRules.delayedOperation()` | `(operators, term)` | Expressions with operators (deferred evaluation) |
| `PegRules.delayedOperationAndComparison()` | — | Arithmetic expressions + combined comparisons |
| `PegRules.comparison()` | — | Immediate comparison |
| `PegRules.delayedComparison()` | — | Deferred comparison |
| `PegRules.namedRulesAsHtml()` | `(rules...)` | HTML rendering of a grammar |

### Activation

No feature — PEG classes are directly usable via import. Integration is via Maven dependency on vertigo-commons module.

---

## Configuration

Components are orthogonal. Here is a typical configuration enabling optional features:

```yaml
modules:
  io.vertigo.commons.CommonsFeatures:
    features:
      - script:
      - command:
    featuresConfig:
      - script.janino:
      - app.dbRegistry:
          driverClassName: org.postgresql.Driver
          jdbcUrl: jdbc:postgresql://localhost:5432/mydb
```

Feature `script.janino` requires parent feature `script`. Feature `app.dbRegistry` requires a JDBC driver on the classpath. Feature `app.redisRegistry` requires a `RedisConnector` declared upstream.

---

## Notes

- **`@Transactional` without aspect**: The annotation alone has no effect. `VTransactionAspect` must be active (which is the default). Do not remove it from configuration.
- **PegLogger disabled by default**: PEG debugging is disabled (`DISABLED = true`). Enabling it in production has a significant performance cost.
- **Application Commands ≠ system commands**: `@Command` declares business operations, not shell executions. `CommandManager` launches no OS processes.
- **Transactional resource priority**: On commit, TOP resources are committed before NORMAL resources. On rollback, the order is reversed.
- **Base64 URL-safe vs Legacy**: The module exposes two Base64 codecs: URL-safe and Legacy (RFC 2045 compatible). Do not mix them in the same exchange chain.
- **Single Registry per node**: Only one registry plugin is active per node. `SingleAppNodeRegistryPlugin` is active by default and sufficient for single-node applications. DB and Redis plugins are for multi-node topologies.
- **Janino — single implementation**: Currently, `JaninoExpressionEvaluatorPlugin` is the only implementation of `ExpressionEvaluatorPlugin`. Any custom evaluation engine requires developing a dedicated plugin.

---

## For Experts

### Managers

| Manager | Impl | Activation |
|---|---|---|
| `AppManager` | `AppManagerImpl` | Automatic (`buildFeatures()`) |
| `CodecManager` | `CodecManagerImpl` | Automatic (`buildFeatures()`) |
| `CommandManager` | `CommandManagerImpl` | Feature `command` |
| `EventBusManager` | `EventBusManagerImpl` | Automatic (`buildFeatures()`) |
| `ScriptManager` | `ScriptManagerImpl` | Feature `script` |
| `VTransactionManager` | `VTransactionManagerImpl` | Automatic (`buildFeatures()`) |

### Features

| Flag | Params | Added Components |
|---|---|---|
| *(buildFeatures) | — | `CodecManager`, `EventBusManager`, `AppManager`, `VTransactionManager`, `VTransactionAspect` |
| `script` | — | `ScriptManager`, `ScriptManagerImpl` |
| `script.janino` | — | `JaninoExpressionEvaluatorPlugin` |
| `command` | — | `CommandManager`, `CommandManagerImpl` |
| `app.dbRegistry` | `driverClassName`, `jdbcUrl` | `DbAppNodeRegistryPlugin` |
| `app.redisRegistry` | — | `RedisAppNodeRegistryPlugin` |
| `app.httpInfos` | — | `HttpAppNodeInfosPlugin` |

### Plugins

**App Topology**
- `SingleAppNodeRegistryPlugin` — local in-memory registry (default)
- `DbAppNodeRegistryPlugin` — shared registry via JDBC (C3P0 pool)
- `RedisAppNodeRegistryPlugin` — shared registry via Redis
- `HttpAppNodeInfosPlugin` — node discovery via REST HTTP (500 ms)

**Script**
- `JaninoExpressionEvaluatorPlugin` — runtime Java expression evaluation via Janino

**Codec**
- `NullCodec<S,T>` — null-safe decorator around any `Codec`
- 13 codecs: HTML, Base64 URL/Legacy, TripleDES, AES-128, Compression, Serialization, CompressedSerialization, CSV, MD5, SHA-1, SHA-256, Hex

### Annotations

| Annotation | Target | Affected Module |
|---|---|---|
| `@Command` | Method | Command |
| `@EventBusSubscribed` | Method | EventBus |
| `@Transactional` | Method | Transaction |

---
