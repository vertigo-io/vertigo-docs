# Database

Le module **Database** fournit la couche de persistance SQL, la gestion des séries temporelles et les migrations de schéma de base de données. Trois managers principaux structurent le module : `SqlManager`, `TimeSeriesManager` et `MigrationManager`.

## SqlManager

Le `SqlManager` est le point d'entrée pour toutes les opérations SQL. Il fournit des connections gérées et un DSL de construction de requêtes.

### Connexion

La connexion à la base se fait via un `SqlConnectionProvider` qui délègue à un `SqlConnectionProviderPlugin`. Deux implémentations sont disponibles :

| Plugin | Feature | Description |
|---|---|---|
| `DataSourceConnectionProviderPlugin` | `sql.datasource` | Utilise un `javax.sql.DataSource` configuré extérieurement (ex : Tomcat JNDI) |
| `C3p0ConnectionProviderPlugin` | `sql.c3p0` | Gère un pool de connections C3P0 intégré |

Chaque connection (`SqlConnection`) encapsule un `java.sql.Connection` et gère le cycle de vie (ouverture, commit, rollback, fermeture).

### Requetes paramétrées

Le module expose un DSL pour construire safely des requêtes paramétrées :

- `SqlStatement` : Requête SQL avec placeholders nommés
- `SqlStatementBuilder` : Constructeur fluide de requêtes
- `SqlParameter` : Paramètre typé avec direction (IN, OUT, INOUT)
- `SqlNamedParam` : Paramètre identifié par un nom

L'exécution se fait via `SqlStatementDriver` qui gère les mappings JDBC via `SqlMapping` et `SqlDialect`.

### Dialectes SQL

Chaque SGBD dispose d'un `SqlDialect` pour les spécificités de syntaxe, d'un `SqlMapping` pour le mapping des types JDBC, et d'un `SqlExceptionHandler` pour la traduction des codes erreur.

| SGBD | Classes | Feature |
|---|---|---|
| H2 | `H2DataBase`, `H2SqlDialect`, `H2SqlExceptionHandler` | inclus |
| PostgreSQL | `PostgreSqlDataBase`, `PostgreSqlDialect`, `PostgreSqlExceptionHandler` | inclus |
| SQL Server | `SqlServerDataBase`, `SqlServerDialect`, `SqlServerExceptionHandler` | inclus |
| Oracle | `OracleDataBase`, `OracleDialect`, `OracleExceptionHandler` | inclus |
| Oracle 11 | `Oracle11DataBase`, `Oracle11Dialect` | inclus |

Le `SqlVendorMapping` détecte automatiquement le vendor depuis la connection JDBC et retourne le `SqlDialect` correspondant. Les exceptions sont standardisées via `SqlOffLimitsException` pour les erreurs de droits et `AbstractSqlExceptionHandler` pour la traduction.

## TimeSeriesManager

Le `TimeSeriesManager` expose une API générique pour stocker et interroger des séries temporelles, indépendamment du backend.

### Modèle de données

| Classe | Rôle |
|---|---|
| `Measure` / `MeasureBuilder` | Mesure individuelle (timestamp + valeur) |
| `DataFilter` / `DataFilterBuilder` | Filtre sur les séries (par nom, tags) |
| `TimeFilter` / `TimeFilterBuilder` | Filtre temporel (par période) |
| `TimedDatas` | Résultat d'agrégation temporelle |
| `TimedDataSerie` | Série temporelle (valeurs par intervalle) |
| `TabularDatas` | Résultat au format tableau de données |
| `TabularDataSerie` | Série tabulaire (lignes de données) |
| `ClusteredMeasure` | Regroupement de mesures par cluster de tags |

### Plugins

| Plugin | Feature | Description |
|---|---|---|
| `FluxInfluxDbTimeSeriesPlugin` | `timeseries.influxdb` | Backend InfluxDB via requêtes Flux |
| `FakeTimeSeriesPlugin` | `timeseries.fake` | Backend en mémoire pour les tests |

## MigrationManager

Le `MigrationManager` orchestre les migrations de schéma de base de données de manière versionnée et reproductible.

### Plugins

| Plugin | Feature | Description |
|---|---|---|
| `LiquibaseMigrationPlugin` | `migration.liquibase` | Migrateur basé sur Liquibase, avec support des changelog XML/SQL/YAML |

## Pour les experts

### Managers

| Manager | Impl | Feature |
|---|---|---|
| `SqlManager` | `SqlManagerImpl` | `sql` |
| `TimeSeriesManager` | `TimeSeriesManagerImpl` | `timeseries` |
| `MigrationManager` | `MigrationManagerImpl` | `migration` |

### Features

| Flag | Params | Composants ajoutés |
|---|---|---|
| `sql` | — | `SqlManager` (`SqlManagerImpl`) |
| `timeseries` | — | `TimeSeriesManager` (`TimeSeriesManagerImpl`) |
| `migration` | `Param...` | `MigrationManager` (`MigrationManagerImpl`) |
| `timeseries.influxdb` | `Param...` | `FluxInfluxDbTimeSeriesPlugin` |
| `timeseries.fake` | — | `FakeTimeSeriesPlugin` |
| `sql.datasource` | `Param...` | `DataSourceConnectionProviderPlugin` |
| `sql.c3p0` | `Param...` | `C3p0ConnectionProviderPlugin` |
| `migration.liquibase` | `Param...` | `LiquibaseMigrationPlugin` |

### Plugins

**Connexion SQL**
- `DataSourceConnectionProviderPlugin` — utilise un `DataSource` externe
- `C3p0ConnectionProviderPlugin` — pool C3P0 intégré
- `AbstractSqlConnectionProviderPlugin` — base commune

**Time Series**
- `FluxInfluxDbTimeSeriesPlugin` — backend InfluxDB (requêtes Flux)
- `FakeTimeSeriesPlugin` — backend en mémoire pour les tests

**Migration**
- `LiquibaseMigrationPlugin` — migrations versionnées via Liquibase

### Configuration

Aucun composant n'est activé par défaut (`buildFeatures()` vide). L'utilisateur doit déclarer explicitement les features nécessaires :

```yaml
modules:
  io.vertigo.database.DatabaseFeatures:
    features:
      - sql:
    featuresConfig:
      - sql.c3p0:
          driverClassName: org.postgresql.Driver
          jdbcUrl: jdbc:postgresql://localhost:5432/mydb
          userId: user
          userPassword: secret
```
