# vertigo-basics

**vertigo-basics** is a utility library providing the foundational components for building `SmartType` and `Task` in a Vertigo application: formatters, validators, and SQL execution engines. No YAML declaration is required; integration is exclusively via Maven dependency.

The module exposes three packages:

| Package | Content |
|---|---|
| `io.vertigo.basics.formatter` | 9 formatting classes for BasicType |
| `io.vertigo.basics.constraint` | 12 validation classes (including `AbstractConstraintLength` and `ConstraintUtil`) |
| `io.vertigo.basics.task` | 9 TaskEngine SQL classes and preprocessors |

---

## Principle

Each SmartType can be annotated with a `Formatter` (for display/input conversion) and one or more `Constraint` (for validation). SmartTypes are then consumed by SQL TaskEngine, which execute relational queries by mapping parameters and results to domain types.

The full SQL execution flow integrates a chain of preprocessors for script transformation before JDBC execution:

```
Raw SQL Script
        ↓
ScriptPreProcessor  (<% %>, <%= %>)
        ↓
TrimPreProcessor   (newline cleanup)
        ↓
WhereInPreProcessor  (IN expansion, chunking 1000)
        ↓
AbstractTaskEngineSQL (transaction, manager injection)
        ↓
    doExecute (Select / Proc / Insert)
        ↓
    JDBC
        ↓
    DTO / DTC
```

---

## Activation

Add Maven dependencies:

```xml
<!-- Required: SmartType, DTO, Task definitions -->
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-datamodel</artifactId>
</dependency>

<!-- Optional: SQL TaskEngine (SELECT, INSERT, UPDATE, DELETE) -->
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-database</artifactId>
</dependency>
```

No YAML features, no additional configuration. Classes are detected by classpath.

---

## Formatters

Convert typed data to displayable strings and vice versa. Declared on a SmartType via `@Formatter(clazz = ..., arg = "...")`.

| Formatter | Inheritance | BasicType | Args |
|---|---|---|---|
| `FormatterString` | final | `String` | `BASIC`, `UPPER`, `LOWER`, `UPPER_FIRST` (via enum `FormatterString.Mode`) |
| `FormatterNumber` | inheritable | `BigDecimal`, `Double`, `Integer`, `Long` | `DecimalFormat` pattern (default: comma decimal, space thousands) |
| `FormatterNumberLocalized` | inheritable | Same as `FormatterNumber` | Locale extension: uses `LocaleManager`, caches `DecimalFormatSymbols` per locale |
| `FormatterId` | final | `Long` | — (separator-free conversion) |
| `FormatterDate` | final | `LocalDate`, `Instant` | `displayFormat;{inputFormats}` (default `dd/MM/yyyy`). Uses `LocaleManager` + `ZoneId` |
| `FormatterBoolean` | final | `Boolean` | `yesFormat;noFormat` (display text). Input accepts `true`/`false`/`1`/`0` |
| `FormatterDefault` | final | All | Dispatch facade by `BasicType`. Args via `ParamManager`: `FmtStringDefaultArgs`, `FmtLocalDateDefaultArgs`, `FmtInstantDefaultArgs`, `FmtBooleanDefaultArgs`, `FmtNumberDefaultArgs` |

Formatting errors use 4 i18n keys defined in `Resources` (package `formatter`).

### SmartType with FormatterDefault

```java
package com.monprojet.smarttypes;

import java.math.BigDecimal;

import io.vertigo.basics.formatter.FormatterDefault;
import io.vertigo.datamodel.smarttype.annotations.Formatter;
import io.vertigo.datamodel.smarttype.annotations.SmartTypeDefinition;
import io.vertigo.datamodel.smarttype.annotations.SmartTypeProperty;

public enum MonProjetSmartTypes {

	@SmartTypeDefinition(String.class)
	@Formatter(clazz = FormatterDefault.class)
	@SmartTypeProperty(property = "storeType", value = "TEXT")
	Label,

	@SmartTypeDefinition(Long.class)
	@Formatter(clazz = FormatterDefault.class)
	@SmartTypeProperty(property = "storeType", value = "NUMERIC")
	Id,
}
```

### FormatterDate with multiple input formats

```java
	@SmartTypeDefinition(LocalDate.class)
	@Formatter(clazz = FormatterDate.class, arg = "dd/MM/yyyy;yyyy-MM-dd;dd-MM-yyyy")
	@SmartTypeProperty(property = "storeType", value = "DATE")
	DateDebut,
```

The first format is used for display. Subsequent formats are tried during input.

### Custom FormatterBoolean

```java
	@SmartTypeDefinition(Boolean.class)
	@Formatter(clazz = FormatterBoolean.class, arg = "Active;Inactive")
	@SmartTypeProperty(property = "storeType", value = "BOOLEAN")
	IsActive,
```

---

## Constraints

Validate data according to SmartType rules. Declared via `@Constraint(clazz = ..., arg = "...")`. Error message can be overridden via the optional `msg` parameter of the annotation.

Length constraints (`StringLength`, `IntegerLength`, `LongLength`, `DoubleLength`, `BigDecimalLength`) share a common implementation via `AbstractConstraintLength`, handling `maxLength` and `DtProperty.MAX_LENGTH`. Constraint errors use 8 i18n keys defined in `Resources` (package `constraint`).

| Constraint | Inheritance | Args | Role |
|---|---|---|---|
| `ConstraintStringLength` | final | integer (maxLength) | `String.length()` ≤ maxLength |
| `ConstraintRegex` | final | pattern | `Pattern.matches()` match |
| `ConstraintNumberMinimum` | final | double | `Number.doubleValue()` ≥ minValue |
| `ConstraintNumberMaximum` | final | double | `Number.doubleValue()` ≤ maxValue |
| `ConstraintLongLength` | final (via Abstract) | integer (< 19) | `Long` ∈ ]-10^n, 10^n[ |
| `ConstraintIntegerLength` | final (via Abstract) | integer (< 10) | `Integer` ∈ ]-10^n, 10^n[ |
| `ConstraintDoubleLength` | final (via Abstract) | integer (n) | `Double` ∈ ]-10^n, 10^n[ |
| `ConstraintBigDecimalLength` | final (via Abstract) | integer (n) | `BigDecimal` ∈ ]-10^n, 10^n[ |
| `ConstraintBigDecimal` | final | `M,D` | Decimal(M,D): M total digits, D decimal places. Applies `stripTrailingZeros()` |

Utility class `ConstraintUtil` (final, private constructor, static methods) groups helper methods for building error messages via `LocaleMessageText`.

### SmartType with composed constraints

```java
package com.monprojet.smarttypes;

import java.math.BigDecimal;

import io.vertigo.basics.constraint.ConstraintBigDecimal;
import io.vertigo.basics.constraint.ConstraintNumberMaximum;
import io.vertigo.basics.constraint.ConstraintNumberMinimum;
import io.vertigo.basics.constraint.ConstraintRegex;
import io.vertigo.basics.constraint.ConstraintStringLength;
import io.vertigo.datamodel.smarttype.annotations.Constraint;
import io.vertigo.datamodel.smarttype.annotations.SmartTypeDefinition;
import io.vertigo.datamodel.smarttype.annotations.SmartTypeProperty;

public enum MonProjetSmartTypes {

	// Budget: max 10 digits, 2 decimals
	@SmartTypeDefinition(BigDecimal.class)
	@Constraint(clazz = ConstraintBigDecimal.class, arg = "10,2")
	@SmartTypeProperty(property = "storeType", value = "NUMERIC")
	Budget,

	// Progress percentage: between 0 and 100
	@SmartTypeDefinition(BigDecimal.class)
	@Constraint(clazz = ConstraintBigDecimal.class, arg = "5,2")
	@Constraint(clazz = ConstraintNumberMinimum.class, arg = "0")
	@Constraint(clazz = ConstraintNumberMaximum.class, arg = "100")
	@SmartTypeProperty(property = "storeType", value = "NUMERIC")
	TaskProgress,

	// Internal task code: 3 letters then 4 digits
	@SmartTypeDefinition(String.class)
	@Constraint(clazz = ConstraintRegex.class, arg = "^[A-Z]{3}-\\d{4}$")
	@SmartTypeProperty(property = "storeType", value = "TEXT")
	InternalCode,

	// Short label: max 50 characters
	@SmartTypeDefinition(String.class)
	@Constraint(clazz = ConstraintStringLength.class, arg = "50")
	@SmartTypeProperty(property = "storeType", value = "TEXT")
	TaskLabel;
}
```

Multiple `@Constraint` can stack on the same SmartType. All constraints are evaluated on each validation.

---

## SQL TaskEngine

SQL TaskEngine are organized around `AbstractTaskEngineSQL`, an abstract class providing common infrastructure: SQL preprocessor chain, transaction management, and injection of 5 managers (`SqlManager`, `ScriptManager`, `VTransactionManager`, `SmartTypeManager`, `AnalyticsManager`). Each subclass implements the abstract method `doExecute`.

Constants `SQL_MAIN_RESOURCE_ID` and `SQL_ROWCOUNT` are defined in `AbstractTaskEngineSQL`.

| TaskEngine | Inheritance | Role |
|---|---|---|
| `TaskEngineSelect` | inheritable | SELECT queries. Auto-dispatch between `DtList` (multi-row) and singleton (single row). |
| `TaskEngineProc` | inheritable | INSERT/UPDATE/DELETE queries. Returns execution rowcount. |
| `TaskEngineInsert` | inheritable | INSERT with generated key injection via `DataAccessor`. Used by `SqlEntityStorePlugin` and available to developers. |
| `TaskEngineProcBatch` | final | Batch SQL execution. A hasMany IN attribute. |
| `TaskEngineInsertBatch` | final | Batch insertion with generated key return. |

### SQL Preprocessors

`AbstractTaskEngineSQL` automatically applies a chain of three preprocessors to each SQL script before execution:

1. **ScriptPreProcessor** — JSP-like SQL syntax: `<% %>` for conditional blocks, `<%= %>` for expression interpolation.
2. **TrimPreProcessor** — Cleans redundant newlines to produce compact SQL.
3. **WhereInPreProcessor** — Expands `IN` clauses: automatic chunking by batches of 1000 elements. Empty collections resolve to `1=1` (SELECT) or `1=2` (DML).

Preprocessors are package-private and not intended for direct use from application projects. For more information on SQL TaskEngine, see [database.md](database.md).

---

## Notes

- **Format vs Input**: `FormatterDate` takes a display format and input formats separated by `;`. Do not confuse the order: the first format is **always** display. Formats can include time (e.g., `dd/MM/yyyy HH:mm`) for `Instant`.
- **Stacked Constraints**: multiple `@Constraint` on the same SmartType are all evaluated. Declaration order determines validation order. Default error message can be overridden via `msg`.
- **FormatterDefault**: delegates to simple formatters by reading application-level config parameters via `ParamManager`. If no parameter is defined, default behavior depends on BasicType (`toString()` for uncovered cases).
- **FormatterNumber vs FormatterNumberLocalized**: `FormatterNumber` applies fixed formatting (decimal comma, space thousands). `FormatterNumberLocalized` adapts formatting to the user's locale via `LocaleManager`.
- **Package-private Preprocessors**: `ScriptPreProcessor`, `TrimPreProcessor`, and `WhereInPreProcessor` are only accessible internally. Do not attempt to instantiate them directly from application code.
- **IN Chunking (1000)**: `WhereInPreProcessor` splits collections over 1000 elements into multiple `IN` clauses to respect RDBMS limits. Empty collections produce `1=1` in selection and `1=2` in modification.

---

## For Experts

### Managers
None.

### Features
No `*Features.java` class — vertigo-basics declares no features. Integration is exclusively via Maven dependency.

### Plugins
None.

### Composition

| Category | Classes | Key File |
|---|---|---|
| **Formatters** | `FormatterString`, `FormatterNumber`, `FormatterNumberLocalized`, `FormatterId`, `FormatterDate`, `FormatterBoolean`, `FormatterDefault`, `FormatterString.Mode`, `Resources` | `io/vertigo/basics/formatter/FormatterString.java` |
| **Constraints** | `AbstractConstraintLength`, `ConstraintStringLength`, `ConstraintRegex`, `ConstraintNumberMinimum`, `ConstraintNumberMaximum`, `ConstraintLongLength`, `ConstraintIntegerLength`, `ConstraintDoubleLength`, `ConstraintBigDecimalLength`, `ConstraintBigDecimal`, `ConstraintUtil`, `Resources` | `io/vertigo/basics/constraint/AbstractConstraintLength.java` |
| **Task Engines** | `AbstractTaskEngineSQL`, `TaskEngineSelect`, `TaskEngineProc`, `TaskEngineInsert`, `TaskEngineProcBatch`, `TaskEngineInsertBatch` | `io/vertigo/basics/task/AbstractTaskEngineSQL.java` |
| **Preprocessors** | `ScriptPreProcessor`, `TrimPreProcessor`, `WhereInPreProcessor` | `io/vertigo/basics/task/ScriptPreProcessor.java` |
