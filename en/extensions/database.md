# Database

Module **vertigo-database** provides SQL persistence layer, time series management, and database schema migrations. Three managers structure the module: `SqlManager`, `TimeSeriesManager`, and `MigrationManager`.

```
Application / Component
        ↓
┌──────────────┬───────────────────┬──────────────────┐
│  SqlManager  │ TimeSeriesManager │ MigrationManager │
└──────┬───────┴────────┬──────────┴────────┬─────────┘
       ↓                ↓                   ↓
┌──────────────┐ ┌───────────────┐ ┌────────────────┐
│SqlManagerImpl││TimeSeriesMgrImpl││MigrationMgrImpl │
└──────┬───────┘ └──────┬────────┘ └───────┬────────┘
       ↓                ↓                   ↓
┌───────────┐ ┌──────────────┐  ┌──────────────────┐
│ JDBC +    │ │ TimeSeries   │  │ MigrationPlugin  │
│ SqlDialect│ │ Plugin active│  │ (Liquibase)      │
└───────────┘ └──────────────┘  └──────────────────┘
```

Each manager is activated by its own feature and operates independently. `SqlManager` is the central component, used by higher-level extensions (EntityStore, DataFactory…) to access relational databases.

---

## SqlManager

`SqlManager` is the entry point for all SQL operations: queries, updates, batches, and transaction management.

### Principle

The manager exposes a transactional interface for executing parameterized SQL on any RDBMS. Execution relies on three layers:

1. **`SqlStatement`** — parameterized SQL query with named placeholders
2. **`SqlStatementDriver`** — JDBC bridge applying the detected vendor's `SqlDialect`
3. **`SqlConnection`** — wrapper around `java.sql.Connection`, provided by a `SqlConnectionProvider`

`SqlManagerImpl` orchestrates the lifecycle: connection acquisition, query preparation, parameter binding, execution, connection release.

### Parameterized Queries

The module exposes a DSL for building SQL queries in a typed and secure way:

| Class | Role |
|---|---|
| `SqlStatement` | Parameterized SQL query (immutable) |
| `SqlStatementBuilder` | Fluent `SqlStatement` builder |
| `SqlParameter` | Typed parameter: record `(Class<O> dataType, O value)` — direction determined by type, no IN/OUT enum |
| `SqlMapping` | Mapping interface for Java → JDBC and JDBC → Java type conversions |

Typical approach:

1. Build a `SqlStatement` via `SqlStatementBuilder` adding parameters through `SqlParameter` or `SqlNamedParam`
2. Execute `SqlStatement` via `SqlManager` (`query`, `update`, `batch`)
3. `SqlStatementDriver` detects vendor dialect and applies specific adaptations

API distinguishes two execution modes:

- **Query** (`executeQuery`) — returns results (`List<O>`) from a `ResultSet` with optional limit
- **Update** (`executeUpdate`, `executeUpdateWithGeneratedKey`) — returns modified row count and optional generated keys
- **Batch** (`executeBatch`, `executeBatchWithGeneratedKeys`) — grouped execution with generated key return

### Connection

Database connection is done via `SqlConnectionProvider`, an interface delegating to a concrete plugin. Each `SqlConnection` encapsulates a `java.sql.Connection` and manages lifecycle (open, commit, rollback, close).

Two connection plugins are available:

| Plugin | Feature | Description |
|---|---|---|
| `C3p0ConnectionProviderPlugin` | `sql.c3p0` | Integrated C3P0 connection pool. Parameters: `dataBaseClass`, `jdbcDriver`, `jdbcUrl`, `minPoolSize`, `maxPoolSize`, `acquireIncrement`, `configName`, `name` |
| `DataSourceConnectionProviderPlugin` | `sql.datasource` | Uses an injected `DataSource` (JNDI, Spring, etc.) |

`SqlAdapterSupplierPlugin` complements the connection layer by providing vendor-specific JDBC type adapters.

Interface `SqlDataBase` groups the database and its associated `SqlDialect`. Interface `SqlConnectionProvider` is the contract for all connection plugins.

### SQL Dialects

The module supports four RDBMS families, each implementing `SqlDialect`:

| RDBMS | Dialect Classes | Supported Version |
|---|---|---|
| H2 | `H2SqlDialect` | Dev / Test |
| PostgreSQL | `PostgreSqlDialect` | Any recent version |
| Oracle | `OracleDialect`, `Oracle11Dialect` | 11g and above |
| SQL Server | `SqlServerDialect` | Any recent version |

Each dialect implements vendor-specific syntax: pagination, identifier handling, native functions, and type mapping. `SqlExceptionHandler` translates vendor SQL error codes to standardized exceptions.

Detection works automatically: when opening the first connection, `SqlStatementDriver` identifies the vendor from JDBC metadata and applies the corresponding `SqlDialect`.

`SqlMapping` interface defines Java-to-JDBC type correspondences for each dialect.

### Example

```java
// Parameterized query — the #name# syntax is converted to ? internally by SqlStatementBuilder
SqlStatement selectStatement = SqlStatement
    .builder("SELECT tacha_id, tacha_libelle, tacha_budget FROM TACHES WHERE tacha_statut = #statut#")
    .bind("statut", String.class, "IN_PROGRESS")
    .build();

List<DtTache> results = sqlManager.executeQuery(
    selectStatement, DtTache.class, basicTypeAdapters, null, sqlConnection);

// Update with generated key
SqlStatement insertStatement = SqlStatement
    .builder("INSERT INTO TACHES (tacha_libelle, tacha_budget) VALUES (#libelle#, #budget#)")
    .bind("libelle", String.class, "My task")
    .bind("budget", Integer.class, 5000)
    .build();

Tuple<Integer, Long> result = sqlManager.executeUpdateWithGeneratedKey(
    insertStatement, GenerationMode.GENERATED_KEYS, "tacha_id", Long.class,
    basicTypeAdapters, sqlConnection);
```

---

## TimeSeriesManager

`TimeSeriesManager` offers a generic API for storing and querying time series, independent of the chosen temporal backend.

### Principle

The manager acts as a facade over an active `TimeSeriesPlugin`. Implementation `TimeSeriesManagerImpl` delegates all calls to the registered plugin. This indirection allows changing backend (InfluxDB, memory for tests) without modifying business code.

### Data Model

The model relies on five fundamental concepts:

| Class | Role |
|---|---|
| `Measure` | Immutable record `(measurement, instant, fields:Map, tags:Map)` — via factory `Measure.builder()` |
| `DataFilter` | Immutable record `(measurement, filters:Map<String, String>)` — via factory `DataFilter.builder()` |
| `TimeFilter` | Immutable record `(from, to, dim)` — bounds as `String` — via factory `TimeFilter.builder()` |
| `TimedDatas` | Temporal aggregation result (time-series by interval) |
| `TabularDatas` | Table-formatted result (data rows) |

### Plugins

Two implementations of `TimeSeriesPlugin` contract are available:

| Plugin | Feature | Description |
|---|---|---|
| `FluxInfluxDbTimeSeriesPlugin` | `timeseries.influxdb` | InfluxDB backend via Flux client. Queries expressed in Flux language |
| `FakeTimeSeriesPlugin` | `timeseries.fake` | In-memory backend for tests. Stores and returns measures without persistence |

Only one `TimeSeriesPlugin` can be active at a time. If no plugin is registered, calls to `TimeSeriesManager` fail.

### Example

```java
// Store a measure
Measure measure = Measure.builder("temperature")
    .addField("value", 22.5)
    .tag("location", "office")
    .build();
timeSeriesManager.insertMeasure("my_metrics", measure);

// Query with filters
DataFilter dataFilter = DataFilter.builder("temperature")
    .addFilter("location", "office")
    .build();
TimeFilter timeFilter = TimeFilter
    .builder(Instant.now().minusHours(24).toString(), Instant.now().toString())
    .build();

TimedDatas result = timeSeriesManager.getTimeSeries(
    "my_metrics", Arrays.asList("temperature.*"), dataFilter, timeFilter);
```

---

## MigrationManager

`MigrationManager` orchestrates database schema migrations in a versioned and reproducible way.

### Principle

`MigrationManagerImpl` delegates migration execution to the registered `MigrationPlugin`. This model allows changing the migration engine without impacting calling code.

### Liquibase Plugin

`LiquibaseMigrationPlugin` implements `MigrationPlugin` using Liquibase as the migration engine. Supports changelog files in XML, SQL, or YAML format.

Execution happens at application startup: the plugin detects unapplied migrations and executes them sequentially. Migration history is tracked in a dedicated table managed by Liquibase.

### Example

```java
// Manual migration execution
migrationManager.update(SqlManager.MAIN_CONNECTION_PROVIDER_NAME);

// Consistency check node↔DB
migrationManager.check(SqlManager.MAIN_CONNECTION_PROVIDER_NAME);
```

---

## Activation

```xml
<!-- Database Module -->
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-database</artifactId>
</dependency>

<!-- Optional: JDBC driver (e.g., PostgreSQL) -->
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
</dependency>
```

No component is activated by default. Each manager and plugin require explicit feature declaration.

A typical configuration activates `sql` with a C3P0 pool and `timeseries` with InfluxDB:

```yaml
modules:
  io.vertigo.database.DatabaseFeatures:
    features:
      - sql:
      - timeseries:
      - migration:
    featuresConfig:
      - sql.c3p0:
          dataBaseClass: org.postgresql.PGDatabase
          jdbcDriver: org.postgresql.Driver
          jdbcUrl: jdbc:postgresql://localhost:5432/mydb
      - timeseries.influxdb:
          connectorName: main
          dbNames: my_metrics
      - migration.liquibase:
          masterFile: db/changelog/changelog-master.xml
```

Each connection feature `sql.*` (`sql.c3p0`, `sql.datasource`) is mutually exclusive: only one `SqlConnectionProvider` plugin can be active. Similarly, only one `TimeSeriesPlugin` and one `MigrationPlugin` can be active simultaneously.

---

## Notes

- **Single connection plugin**: `sql.c3p0` and `sql.datasource` are mutually exclusive. Declaring both causes a startup error.
- **Automatic dialect**: `SqlDialect` is auto-detected from JDBC connection. No manual dialect configuration is required. Detection order: PostgreSQL, Oracle, SQL Server, H2.
- **Generated keys**: `executeBatchWithGeneratedKeys` is only supported on RDBMS exposing `getGeneratedKeys()`. Verify JDBC driver compatibility.
- **Oracle11Dialect**: specialized for Oracle 11g and versions prior to 12c. For Oracle 12c+, use `OracleDialect`.
- **TimeSeries without plugin**: if feature `timeseries` is enabled but no `TimeSeriesPlugin` is registered, all manager operations will fail. Always activate at least one plugin feature (`timeseries.influxdb` or `timeseries.fake`).
- **InfluxDB and Flux**: InfluxDB plugin uses Flux language for queries. Flux syntax differs from Line Protocol used for writes.
- **Liquibase at startup**: Liquibase plugin automatically executes migrations at startup. Do not configure manual parallel execution to avoid locking conflicts.
- **SqlMapping and types**: Java→SQL mapping is defined by `SqlMapping`. For uncovered Java types (e.g., `Mail`), use `BasicTypeAdapter` to convert to a supported primitive type (via `basicTypeAdapters` parameter of execution methods).
- **C3P0 connection pool**: Pool parameters (min/max size, timeout) are configurable via `Param` of `sql.c3p0` feature. Without configuration, C3P0 defaults apply (min 3, max 15).

---

## For Experts

### Managers

| Manager | Impl | Feature |
|---|---|---|
| `SqlManager` | `SqlManagerImpl` (final) | `sql` |
| `TimeSeriesManager` | `TimeSeriesManagerImpl` | `timeseries` |
| `MigrationManager` | `MigrationManagerImpl` (final) | `migration` |

### Impl — SqlManager

`SqlManagerImpl` implements five execution methods:

| Method | Role |
|---|---|
| `executeQuery` | SELECT execution, returns `List<O>` with optional limit |
| `executeUpdate` | INSERT/UPDATE/DELETE execution, returns `int` (modified rows) |
| `executeUpdateWithGeneratedKey` | Same + primary key retrieval, returns `Tuple<Integer, O>` |
| `executeBatch` | Grouped SQL statement execution, returns `OptionalInt` |
| `executeBatchWithGeneratedKeys` | Batch with generated primary key retrieval, returns `Tuple<Integer, List<O>>` |

Method `getConnectionProvider(String)` accesses named providers (default `MAIN_CONNECTION_PROVIDER_NAME` = `"main"`).

Execution goes through `SqlStatementDriver`, bridging JDBC calls to the vendor's `SqlDialect`. Driver manages parameter binding, type adaptation via `SqlMapping`, and exception translation via `SqlExceptionHandler`.

### Features

| Flag | Params | Added Components |
|---|---|---|
| `sql` | — | `SqlManager` (`SqlManagerImpl`) |
| `sql.c3p0` | `name`, `dataBaseClass`, `jdbcDriver`, `jdbcUrl`, `minPoolSize`, `maxPoolSize`, `acquireIncrement`, `configName` | `C3p0ConnectionProviderPlugin` |
| `sql.datasource` | DataSource params | `DataSourceConnectionProviderPlugin` |
| `timeseries` | — | `TimeSeriesManager` (`TimeSeriesManagerImpl`) |
| `timeseries.influxdb` | `connectorName`, `dbNames` (requires: `InfluxDbConnector`) | `FluxInfluxDbTimeSeriesPlugin` |
| `timeseries.fake` | — | `FakeTimeSeriesPlugin` |
| `migration` | `Param...` | `MigrationManager` (`MigrationManagerImpl`) |
| `migration.liquibase` | `masterFile`, `connectionName`, `contexts` | `LiquibaseMigrationPlugin` |

### Plugins

**SQL Connection**
- `C3p0ConnectionProviderPlugin` — integrated C3P0 pool with full configuration (driver, URL, credentials, pool params)
- `DataSourceConnectionProviderPlugin` — wrapper around external `DataSource` (JNDI, Spring, etc.)
- `SqlAdapterSupplierPlugin` (interface) — vendor-specific JDBC type adaptation

**TimeSeries**
- `FluxInfluxDbTimeSeriesPlugin` — InfluxDB backend with Flux queries and Line Protocol writes
- `FakeTimeSeriesPlugin` — in-memory backend for unit and integration tests

**Migration**
- `LiquibaseMigrationPlugin` — Liquibase engine for versioned SQL schema migrations

**SQL Dialects**
- `H2SqlDialect` — H2 dialect for dev and test
- `PostgreSqlDialect` — PostgreSQL dialect
- `OracleDialect` — Oracle 12c+ dialect
- `Oracle11Dialect` — Oracle 11g dialect (extends `OracleDialect`)
- `SqlServerDialect` — SQL Server dialect

### Key Interfaces

| Interface | Annotation | Role |
|---|---|---|
| `SqlManager` | `@Manager` | SQL CRUD, query/batch/generatedKey, transactional |
| `TimeSeriesManager` | `@Manager` | Temporal metric storage and querying |
| `MigrationManager` | `@Manager` | Versioned SQL schema migrations |
| `SqlConnectionProvider` | — | JDBC connection provider |
| `SqlDialect` | — | Vendor-specific SQL dialect |
| `SqlDataBase` | — | Database + associated dialect |
| `SqlExceptionHandler` | — | Vendor SQL error translation to standard |
| `TimeSeriesPlugin` | `@Plugin` | Temporal storage backend |
| `MigrationPlugin` | `@Plugin` | Schema migration engine |

### Composition

| Category | Classes |
|---|---|
| **SQL Statement** | `SqlStatement`, `SqlStatementBuilder`, `SqlParameter`, `SqlNamedParam` |
| **SQL Connection** | `SqlConnection`, `SqlConnectionProvider`, `SqlConnectionProviderPlugin`, `SqlAdapterSupplierPlugin` |
| **SQL Dialect** | `SqlDialect`, `SqlDataBase`, `SqlExceptionHandler`, `SqlMapping`, `SqlStatementDriver` |
| **TimeSeries Model** | `Measure`, `MeasureBuilder`, `DataFilter`, `DataFilterBuilder`, `TimeFilter`, `TimeFilterBuilder`, `TimedDatas`, `TabularDatas` |
| **TimeSeries Plugins** | `TimeSeriesPlugin`, `FluxInfluxDbTimeSeriesPlugin`, `FakeTimeSeriesPlugin` |
| **Migration Plugins** | `MigrationPlugin`, `LiquibaseMigrationPlugin` |
| **Connection Plugins** | `SqlConnectionProviderPlugin` (interface), `C3p0ConnectionProviderPlugin`, `DataSourceConnectionProviderPlugin` |

### YAML Configuration

See [Activation](#activation) section for complete YAML block.
