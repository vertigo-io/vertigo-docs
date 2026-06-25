# Database

Le module **vertigo-database** fournit la couche de persistance SQL, la gestion des séries temporelles et les migrations de schéma de base de données. Trois managers structurent le module : `SqlManager`, `TimeSeriesManager` et `MigrationManager`.

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

Chaque manager est activé par sa propre feature et fonctionne de manière indépendante. Le `SqlManager` est le composant central, utilisé par les extensions de plus haut niveau (EntityStore, DataFactory…) pour accéder aux bases relationnelles.

---

## SqlManager

Le `SqlManager` est le point d'entrée pour toutes les opérations SQL : requêtes, updates, batchs et gestion transactionnelle.

### Principe

Le manager expose une interface transactionnelle pour exécuter du SQL paramétré sur n'importe quel SGBD. L'exécution repose sur trois couches :

1. **`SqlStatement`** — requête SQL paramétrée avec placeholders nommés
2. **`SqlStatementDriver`** — bridge JDBC qui applique le `SqlDialect` du vendor détecté
3. **`SqlConnection`** — wrapper autour de `java.sql.Connection`, fourni par un `SqlConnectionProvider`

Le `SqlManagerImpl` orchestre le cycle de vie : obtention de la connexion, préparation de la requête, binding des paramètres, exécution, release de la connexion.

### Requêtes paramétrées

Le module expose un DSL pour construire des requêtes SQL de manière typée et sécurisée :

| Classe | Rôle |
|---|---|
| `SqlStatement` | Requête SQL paramétrée (immutable) |
| `SqlStatementBuilder` | Constructeur fluide de `SqlStatement` |
| `SqlParameter` | Paramètre positionnel typé avec direction (IN, OUT, INOUT) |
| `SqlNamedParam` | Paramètre identifié par un nom, pour les requêtes nommées |
| `SqlMapping` | Mapping Java → JDBC et JDBC → Java des types |

La démarche typique :

1. Construire un `SqlStatement` via `SqlStatementBuilder` en ajoutant les paramètres via `SqlParameter` ou `SqlNamedParam`
2. Exécuter le `SqlStatement` via `SqlManager` (`query`, `update`, `batch`)
3. Le `SqlStatementDriver` détecte le dialecte du vendor et applique les adaptations spécifiques

L'API distingue deux modes d'exécution :

- **Query** (`executeQuery`) — retourne des résultats (`List<O>`) à partir d'un `ResultSet` avec limitation optionnelle
- **Update** (`executeUpdate`, `executeUpdateWithGeneratedKey`) — retourne le nombre de lignes modifiées et les generated keys optionnels
- **Batch** (`executeBatch`, `executeBatchWithGeneratedKeys`) — exécution groupée avec retour des keys générées

### Connexion

La connexion à la base se fait via un `SqlConnectionProvider`, interface qui délègue à un plugin concret. Chaque `SqlConnection` encapsule un `java.sql.Connection` et gère le cycle de vie (ouverture, commit, rollback, fermeture).

Deux plugins de connexion sont disponibles :

| Plugin | Feature | Description |
|---|---|---|
| `C3p0ConnectionProviderPlugin` | `sql.c3p0` | Pool de connections C3P0 intégré. Paramètres : `driverClassName`, `jdbcUrl`, `userId`, `userPassword`, et paramètres de pool |
| `DataSourceConnectionProviderPlugin` | `sql.datasource` | Utilisation d'un `DataSource` injecté (JNDI, Spring, etc.) |

Le `SqlAdapterSupplierPlugin` complète la couche de connexion en fournissant les adaptateurs de types JDBC spécifiques au vendor.

L'interface `SqlDataBase` regroupe la base de données et son `SqlDialect` associé. L'interface `SqlConnectionProvider` est le contrat pour tous les plugins de connexion.

### Dialectes SQL

Le module supporte quatre familles de SGBD, chacune implémentant l'interface `SqlDialect` :

| SGBD | Classes Dialect | Version supportée |
|---|---|---|
| H2 | `H2SqlDialect` | Dev / Test |
| PostgreSQL | `PostgreSqlDialect` | Toute version récente |
| Oracle | `OracleDialect`, `Oracle11Dialect` | 11g et supérieur |
| SQL Server | `SqlServerDialect` | Toute version récente |

Chaque dialecte implémente la syntaxe spécifique du vendor : pagination, gestion des identifiants, fonctions natives, et mapping des types. L'interface `SqlExceptionHandler` traduit les codes erreur SQL du vendor vers des exceptions standardisées.

Le mécanisme de détection fonctionne automatiquement : au moment de l'ouverture de la première connexion, le `SqlStatementDriver` identifie le vendor depuis la métadonnée JDBC et applique le `SqlDialect` correspondant.

La classe `SqlMapping` définit les correspondances entre les types Java et les types JDBC pour chaque dialecte.

### Exemple

```java
// Requête paramétrée
SqlStatement selectStatement = new SqlStatementBuilder()
    .withSql("SELECT tacha_id, tacha_libelle, tacha_budget FROM TACHES WHERE tacha_statut = ?")
    .withParam(SqlParameter.of(SqlMapping.STRING, "EN_COURS"))
    .build();

List<DtTache> resultats = sqlManager.executeQuery(
        selectStatement, DtTache.class, basicTypeAdapters, null, sqlConnection);

// Update avec generated key
SqlStatement insertStatement = new SqlStatementBuilder()
    .withSql("INSERT INTO TACHES (tacha_libelle, tacha_budget) VALUES (?, ?)")
    .withParam(SqlParameter.of(SqlMapping.STRING, "Ma tâche"))
    .withParam(SqlParameter.of(SqlMapping.INTEGER, 5000))
    .build();

Tuple<Integer, Long> result = sqlManager.executeUpdateWithGeneratedKey(
        insertStatement, GenerationMode.GENERATED_KEYS, "tacha_id", Long.class,
        basicTypeAdapters, sqlConnection);
```

---

## TimeSeriesManager

Le `TimeSeriesManager` offre une API générique pour stocker et interroger des séries temporelles, indépendamment du backend temporel choisi.

### Principe

Le manager agit comme une façade au-dessus d'un `TimeSeriesPlugin` actif. L'implémentation `TimeSeriesManagerImpl` délègue toutes ses appels au plugin enregistré. Cette indirection permet de changer de backend (InfluxDB, mémoire pour les tests) sans modifier le code métier.

### Modèle de données

Le modèle repose sur cinq concepts fondamentaux :

| Classe | Rôle |
|---|---|
| `Measure` | Mesure individuelle (timestamp, nom de série, valeur, tags) |
| `MeasureBuilder` | Constructeur de `Measure` |
| `DataFilter` / `DataFilterBuilder` | Filtre sur les séries par nom, tags, et valeurs |
| `TimeFilter` / `TimeFilterBuilder` | Filtre temporel par période (début/fin) |
| `TimedDatas` | Résultat d'agrégation temporelle (séries par intervalle) |
| `TabularDatas` | Résultat au format tableau (lignes de données) |

### Plugins

Deux implémentations du contract `TimeSeriesPlugin` sont disponibles :

| Plugin | Feature | Description |
|---|---|---|
| `FluxInfluxDbTimeSeriesPlugin` | `timeseries.influxdb` | Backend InfluxDB via client Flux. Les requêtes sont exprimées en langage Flux |
| `FakeTimeSeriesPlugin` | `timeseries.fake` | Backend en mémoire pour les tests. Stocke et restitue les mesures sans persistance |

Un seul plugin `TimeSeriesPlugin` peut être actif à la fois. Si aucun plugin n'est enregistré, les appels au `TimeSeriesManager` échouent.

### Exemple

```java
// Stocker une mesure
Measure measure = new MeasureBuilder()
    .withSeriesName("temperature.salle1")
    .withValue(22.5)
    .withTag("localisation", "bureau")
    .build();
timeSeriesManager.insertMeasure("my_metrics", measure);

// Requêter avec filtres
DataFilter dataFilter = new DataFilterBuilder()
    .withSeriesName("temperature.*")
    .build();
TimeFilter timeFilter = new TimeFilterBuilder()
    .withStart(Instant.now().minusHours(24))
    .build();

TimedDatas result = timeSeriesManager.getTimeSeries(
        "my_metrics", Arrays.asList("temperature.*"), dataFilter, timeFilter);
```

---

## MigrationManager

Le `MigrationManager` orchestre les migrations de schéma de base de données de manière versionnée et reproductible.

### Principe

Le `MigrationManagerImpl` délègue l'exécution des migrations au `MigrationPlugin` enregistré. Ce modèle permet de changer de moteur de migration sans impact sur le code appelant.

### Plugin Liquibase

Le plugin `LiquibaseMigrationPlugin` implémente `MigrationPlugin` en utilisant Liquibase comme moteur de migration. Il supporte les fichiers changelog au format XML, SQL ou YAML.

L'exécution se fait au démarrage de l'application : le plugin détecte les migrations non appliquées et les exécute séquentiellement. L'historique des migrations est tracé dans une table dédiée gérée par Liquibase.

### Exemple

```java
// Exécution manuelle d'une migration
migrationManager.update(SqlManager.MAIN_CONNECTION_PROVIDER_NAME);

// Vérification de cohérence node↔DB
migrationManager.check(SqlManager.MAIN_CONNECTION_PROVIDER_NAME);
```

---

## Activation

```xml
<!-- Module Database -->
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-database</artifactId>
</dependency>

<!-- Optionnel : driver JDBC (ex : PostgreSQL) -->
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
</dependency>
```

Aucun composant n'est activé par défaut. Chaque manager et chaque plugin nécessitent une déclaration de feature explicite.

Une configuration typique active `sql` avec un pool C3P0 et `timeseries` avec InfluxDB :

```yaml
modules:
  io.vertigo.database.DatabaseFeatures:
    features:
      - sql:
      - timeseries:
      - migration:
    featuresConfig:
      - sql.c3p0:
          driverClassName: org.postgresql.Driver
          jdbcUrl: jdbc:postgresql://localhost:5432/mydb
          userId: user
          userPassword: secret
      - timeseries.influxdb:
          host: localhost
          port: 8086
          database: my_metrics
      - migration.liquibase:
          changeLogFile: db/changelog/changelog-master.xml
```

Chaque feature `sql.*` de connexion (`sql.c3p0`, `sql.datasource`) est incompatible avec les autres : un seul plugin de connexion `SqlConnectionProvider` peut être actif. De même, un seul `TimeSeriesPlugin` et un seul `MigrationPlugin` peuvent être actifs simultanément.

---

## Vigilance

- **Un seul plugin de connexion** : `sql.c3p0` et `sql.datasource` sont mutuellement exclusifs. Déclarer les deux provoque une erreur de démarrage.
- **Dialecte automatique** : le `SqlDialect` est détecté automatiquement depuis la connexion JDBC. Aucune configuration manuelle du dialecte n'est requise. L'ordre de détection est : PostgreSQL, Oracle, SQL Server, H2.
- **Generated keys** : la méthode `executeBatchWithGeneratedKeys` n'est supportée que sur les SGBD exposant `getGeneratedKeys()`. Vérifier la compatibilité du driver JDBC.
- **Oracle11Dialect** : ce dialecte est spécialisé pour Oracle 11g et versions antérieures à 12c. Pour Oracle 12c+, utiliser `OracleDialect`.
- **TimeSeries sans plugin** : si la feature `timeseries` est activée mais qu'aucun `TimeSeriesPlugin` n'est enregistré, toute opération sur le manager échouera. Toujours activer au moins une feature de plugin (`timeseries.influxdb` ou `timeseries.fake`).
- **InfluxDB et Flux** : le plugin InfluxDB utilise le langage Flux pour les requêtes. La syntaxe Flux diffère du langage Line Protocol utilisé pour les écritures.
- **Liquibase au démarrage** : le plugin Liquibase exécute les migrations automatiquement au démarrage. Ne pas configurer d'exécution manuelle en parallèle pour éviter les conflits de verrouillage.
- **SqlMapping et les types** : le mapping Java→SQL est défini par `SqlMapping`. Pour les types Java non couverts (ex : `Mail`), utiliser `BasicTypeAdapter` pour convertir vers un type primitif supporté (via le paramètre `basicTypeAdapters` des méthodes d'exécution).
- **Connection pool C3P0** : les paramètres de pool (taille minimale, maximale, timeout) sont configurables via les `Param` de la feature `sql.c3p0`. En l'absence de configuration, les valeurs par défaut C3P0 s'appliquent (pool min 3, max 15).

---

## Pour les experts

### Managers

| Manager | Impl | Feature |
|---|---|---|
| `SqlManager` | `SqlManagerImpl` (final) | `sql` |
| `TimeSeriesManager` | `TimeSeriesManagerImpl` (final) | `timeseries` |
| `MigrationManager` | `MigrationManagerImpl` (final) | `migration` |

### Impl — SqlManager

`SqlManagerImpl` implémente cinq méthodes d'exécution :

| Méthode | Rôle |
|---|---|
| `executeQuery` | Exécution de requête SELECT, retourne `List<O>` avec limitation optionnelle |
| `executeUpdate` | Exécution de requête INSERT/UPDATE/DELETE, retourne `int` (lignes modifiées) |
| `executeUpdateWithGeneratedKey` | Idem + récupération clé primaire, retourne `Tuple<Integer, O>` |
| `executeBatch` | Exécution groupée de plusieurs statements SQL, retourne `OptionalInt` |
| `executeBatchWithGeneratedKeys` | Batch avec récupération des clés primaires générées, retourne `Tuple<Integer, List<O>>` |

Une méthode `getConnectionProvider(String)` permet d'accéder aux providers nommés (par défaut `MAIN_CONNECTION_PROVIDER_NAME` = `"main"`).

L'exécution passe par `SqlStatementDriver`, classe qui bridge les appels JDBC vers le `SqlDialect` du vendor. Le driver gère le binding des paramètres, l'adaptation des types via `SqlMapping`, et la traduction des exceptions via `SqlExceptionHandler`.

### Features

| Flag | Params | Composants ajoutés |
|---|---|---|
| `sql` | — | `SqlManager` (`SqlManagerImpl`) |
| `sql.c3p0` | `driverClassName`, `jdbcUrl`, `userId`, `userPassword`, params pool | `C3p0ConnectionProviderPlugin` |
| `sql.datasource` | params DataSource | `DataSourceConnectionProviderPlugin` |
| `timeseries` | — | `TimeSeriesManager` (`TimeSeriesManagerImpl`) |
| `timeseries.influxdb` | `host`, `port`, `database`, params connexion | `FluxInfluxDbTimeSeriesPlugin` |
| `timeseries.fake` | — | `FakeTimeSeriesPlugin` |
| `migration` | `Param...` | `MigrationManager` (`MigrationManagerImpl`) |
| `migration.liquibase` | `Param...` | `LiquibaseMigrationPlugin` |

### Plugins

**Connexion SQL**
- `C3p0ConnectionProviderPlugin` — pool de connections C3P0 intégré avec configuration complète (driver, URL, credentials, pool params)
- `DataSourceConnectionProviderPlugin` — wrapper autour d'un `DataSource` externe (JNDI, Spring, etc.)
- `SqlAdapterSupplierPlugin` — adaptation des types JDBC spécifiques au vendor

**TimeSeries**
- `FluxInfluxDbTimeSeriesPlugin` — backend InfluxDB avec requêtes Flux et écritures Line Protocol
- `FakeTimeSeriesPlugin` — backend en mémoire pour les tests unitaires et d'intégration

**Migration**
- `LiquibaseMigrationPlugin` — moteur Liquibase pour les migrations versionnées du schéma SQL

**Dialectes SQL**
- `H2SqlDialect` — dialecte H2 pour dev et test
- `PostgreSqlDialect` — dialecte PostgreSQL
- `OracleDialect` — dialecte Oracle 12c+
- `Oracle11Dialect` — dialecte Oracle 11g (sous-classe de `OracleDialect`)
- `SqlServerDialect` — dialecte SQL Server

### Interfaces clés

| Interface | Annotation | Rôle |
|---|---|---|
| `SqlManager` | `@Manager` | CRUD SQL, query/batch/generatedKey, transactionnel |
| `TimeSeriesManager` | `@Manager` | Stockage et requête de métriques temporelles |
| `MigrationManager` | `@Manager` | Migrations de schéma SQL versionnées |
| `SqlConnectionProvider` | — | Fournisseur de connexions JDBC |
| `SqlDialect` | — | Dialecte SQL spécifique au vendor |
| `SqlDataBase` | — | Base de données + dialecte associé |
| `SqlExceptionHandler` | — | Traduction des erreurs SQL du vendor vers le standard |
| `TimeSeriesPlugin` | `@Plugin` | Backend de stockage temporel |
| `MigrationPlugin` | `@Plugin` | Moteur de migration de schéma |

### Composition

| Catégorie | Classes |
|---|---|
| **SQL Statement** | `SqlStatement`, `SqlStatementBuilder`, `SqlParameter`, `SqlNamedParam` |
| **SQL Connection** | `SqlConnection`, `SqlConnectionProvider`, `SqlConnectionProviderPlugin`, `SqlAdapterSupplierPlugin` |
| **SQL Dialect** | `SqlDialect`, `SqlDataBase`, `SqlExceptionHandler`, `SqlMapping`, `SqlStatementDriver` |
| **TimeSeries Model** | `Measure`, `MeasureBuilder`, `DataFilter`, `DataFilterBuilder`, `TimeFilter`, `TimeFilterBuilder`, `TimedDatas`, `TabularDatas` |
| **TimeSeries Plugins** | `TimeSeriesPlugin`, `FluxInfluxDbTimeSeriesPlugin`, `FakeTimeSeriesPlugin` |
| **Migration Plugins** | `MigrationPlugin`, `LiquibaseMigrationPlugin` |
| **Connexion Plugins** | `SqlConnectionProviderPlugin` (abstract), `C3p0ConnectionProviderPlugin`, `DataSourceConnectionProviderPlugin` |

### Configuration YAML

Voir section [Activation](#activation) pour le bloc YAML complet.
