# DataStore

Module **DataStore** provides multi-backend storage abstraction organized around four managers: **EntityStore**, **FileStore**, **KVStore**, and **Cache**.

## EntityStore

`EntityStoreManager` offers generic CRUD persistence on business objects (`Entity`), with criteria support, caching, and reference data (`MasterData`).

### API

| Element | Role |
|---|---|
| `EntityStoreManager` | Main persistence interface |
| `EntityStorePlugin` | Persistence plugin (only integrated SQL plugin) |
| `EntityStoreConfig` / `EntityStoreConfigImpl` | Per-object configuration (cache, TTL) |
| `MasterDataConfig` / `MasterDataConfigImpl` | Reference data configuration |
| `BrokerNN` | N-N association management |
| `StoreEvent` | Persistence events (create, update, delete) |

### Criteria

`SqlCriteriaEncoder` dynamically builds SQL queries from criteria (`Criteria`, `Criterion`, `CriteriaExpression`), with filter and aggregate encoders.

### SQL Plugin

`SqlEntityStorePlugin` implements relational persistence. It uses `SqlCriteriaEncoder` to build SQL queries from criteria.

### Reference Data

`MasterData` and `StaticMasterData` are loaded via `AbstractMasterDataDefinitionProvider`. The API exposes `MasterDataDefinition` for reference definitions.

### Metrics

`EntityMetricsProvider` exposes the `entityCount` metric (access counter) per entity.

## FileStore

`FileStoreManager` manages file storage with MIME resolution and multi-backend support (filesystem, database, S3).

### Data Model

| Class | Role |
|---|---|
| `VFile` | Generic file representation |
| `FileInfo` | File metadata (name, size, MIME, date) |
| `FileInfoURI` | URI pointing to a file in the store |

### Storage Plugins

| Plugin | Feature | Description |
|---|---|---|
| `FsFileStorePlugin` | `filestore.filesystem` | Files on local filesystem |
| `FsFullFileStorePlugin` | `filestore.fullFilesystem` | Full filesystem access (free read/write) |
| `DbFileStorePlugin` | `filestore.db` | Files stored in database (1 table) |
| `S3FileStorePlugin` | `filestore.s3` | S3 / MinIO storage |

### MIME Resolution

| Plugin | Feature | Description |
|---|---|---|
| `TikaMimeTypeResolverPlugin` | `filestore.mimeType.tika` | MIME detection via Apache Tika (most accurate) |
| `SimpleMagicMimeTypeResolverPlugin` | `filestore.mimeType.simplemagic` | MIME detection via binary signatures (lighter) |

## KVStore

`KVStoreManager` provides key-value storage with 6 available backends. API exposes typed collections (`KVCollection`).

### Plugins

| Plugin | Feature | Description |
|---|---|---|
| `BerkeleyKVStorePlugin` | `kvStore.berkeley` | Berkeley DB Java Edition (LMDB-like files) |
| `RedisKVStorePlugin` | `kvStore.redis` | Redis (distributed, clustering support) |
| `SpeedbKVStorePlugin` | `kvStore.speedb` | Speedb (optimized RocksDB fork) |
| `H2KVStorePlugin` | `kvStore.h2` | Embedded H2 database |
| `EhCacheKVStorePlugin` | `kvStore.ehcache` | EhCache (distributed cache) |
| `DelayedMemoryKVStorePlugin` | `kvStore.delayedMemory` | Memory with delayed persistence |

## Cache

`CacheManager` provides abstraction to the caching solution for other components.

| Plugin | Feature | Description |
|---|---|---|
| `MemoryCachePlugin` | `cache.memory` | Local in-memory cache *(TTL eviction defined by the consuming module)* |
| `RedisCachePlugin` | `cache.redis` | Shared cache via Redis *(Requires Redis connector)* |
| `EhCachePlugin` | `cache.eh` | Cache via EhCache *(Requires configuration file `ehcache.xml`)* |

## For Experts

### Managers

| Manager | Impl | Feature |
|---|---|---|
| `EntityStoreManager` | `EntityStoreManagerImpl` | `entitystore` |
| `FileStoreManager` | `FileStoreManagerImpl` | `filestore` |
| `KVStoreManager` | `KVStoreManagerImpl` | `kvStore` |
| `CacheManager` | `CacheManagerImpl` | `cache` |

### Features

| Flag | Params | Added Components |
|---|---|---|
| `entitystore` | — | `EntityStoreManager` (`EntityStoreManagerImpl`) |
| `entitystore.sql` | `Param...` | `SqlEntityStorePlugin`, `SqlCriteriaEncoder` |
| `filestore` | `Param...` | `FileStoreManager` (`FileStoreManagerImpl`) |
| `filestore.filesystem` | `Param...` | `FsFileStorePlugin` |
| `filestore.fullFilesystem` | `Param...` | `FsFullFileStorePlugin` |
| `filestore.db` | `Param...` | `DbFileStorePlugin` |
| `filestore.s3` | `Param...` | `S3FileStorePlugin` |
| `filestore.mimeType.tika` | — | `TikaMimeTypeResolverPlugin` |
| `filestore.mimeType.simplemagic` | — | `SimpleMagicMimeTypeResolverPlugin` |
| `kvStore` | — | `KVStoreManager` (`KVStoreManagerImpl`) |
| `kvStore.berkeley` | `Param...` | `BerkeleyKVStorePlugin` |
| `kvStore.redis` | `Param...` | `RedisKVStorePlugin` |
| `kvStore.speedb` | `Param...` | `SpeedbKVStorePlugin` |
| `kvStore.h2` | `Param...` | `H2KVStorePlugin` |
| `kvStore.ehcache` | `Param...` | `EhCacheKVStorePlugin` |
| `kvStore.delayedMemory` | `Param...` | `DelayedMemoryKVStorePlugin` |
| `taskProxyMethod` | — | AmplifierMethod `TaskAmplifierMethod` |
| `entityMetrics` | — | `EntityMetricsProvider` |
| `cache` | — | `CacheManager` (`CacheManagerImpl`) |
| `cache.redis` | `Param...` | `RedisCachePlugin` |
| `cache.memory` | — | `MemoryCachePlugin` |
| `cache.eh` | — | `EhCachePlugin` |

### Configuration

No component is activated by default (`buildFeatures()` is empty). Configuration example:

```yaml
modules:
  io.vertigo.datastore.DataStoreFeatures:
    features:
      - entitystore:
      - cache:
      - filestore:
      - kvStore:
    featuresConfig:
      - entitystore.sql:
      - cache.redis:
      - filestore.filesystem:
      - kvStore.h2:
      - kvStore.speedb:
```

Redis connector configuration (single mode):

```yaml
modules:
  io.vertigo.services.redis.RedisFeatures:
    featuresConfig:
      - jedis:
          host: localhost
          port: 6379
          database: 0
          password:
          ssl: false
          maxTotal: 8
          minIdle: 1
```

Redis connector configuration (cluster mode):

```yaml
modules:
  io.vertigo.services.redis.RedisFeatures:
    featuresConfig:
      - jedis:
          clusterNodes: "redis-node1:6379;redis-node2:6379;redis-node3:6379"
          password:
          ssl: false
          maxTotal: 8
          minIdle: 1
```

Redis connector configuration (Sentinel mode):

```yaml
modules:
  io.vertigo.services.redis.RedisFeatures:
    featuresConfig:
      - jedis:
          mastername: mymaster
          sentinels: "sentinel1:26379;sentinel2:26379;sentinel3:26379"
          database: 0
          password:
          ssl: false
          maxTotal: 8
          minIdle: 1
```

## RedisConnector

`RedisConnector` replaces the previous Redis connector and supports three connection modes via the `jedis` feature.

### Connection Modes

| Mode | YAML Parameters | Description |
|---|---|---|
| Single | `host`, `port`, `database`, `username`, `password`, `ssl`, `trustStoreUrl`, `trustStorePassword`, `maxTotal`, `minIdle` | Single Redis node connection |
| Cluster | `clusterNodes`, `password`, `ssl`, `trustStoreUrl`, `trustStorePassword`, `maxTotal`, `minIdle` | Native Redis cluster |
| Sentinel | `mastername`, `sentinels`, `database`, `username`, `password`, `ssl`, `trustStoreUrl`, `trustStorePassword`, `maxTotal`, `minIdle` | Via Sentinel (method `withJedis`) |

| Parameter | Single | Cluster | Sentinel |
|---|:---:|:---:|:---:|
| `host` | ✅ | | |
| `port` | ✅ | | |
| `database` | ✅ | | ✅ |
| `username` | ✅ | ✅ | ✅ |
| `password` | ✅ | ✅ | ✅ |
| `ssl` | ✅ | ✅ | ✅ |
| `trustStoreUrl` | ✅ | ✅ | ✅ |
| `trustStorePassword` | ✅ | ✅ | ✅ |
| `maxTotal` | ✅ | ✅ | ✅ |
| `minIdle` | ✅ | ✅ | ✅ |
| `clusterNodes` | | ✅ | |
| `mastername` | | | ✅ |
| `sentinels` | | | ✅ |

### RedisSingleConnector (deprecated)

`RedisSingleConnector` is **deprecated** (`@Deprecated`) and will throw an `UnsupportedOperationException` if used in Sentinel mode.

**Migration**: replace with `RedisConnector` using single mode (`host`/`port` parameters) or Sentinel mode (`mastername`/`sentinels` parameters).

## Database

### LiquibaseMigrationPlugin

Executes Liquibase schema migrations at module startup.

| Parameter | Description |
|---|---|
| `masterFile` | Path to `changelog-master.xml` file |
| `connectionName` | JDBI connection name to use |
| `contexts` | Liquibase contexts to activate |

### InfluxDB

InfluxDB connector for time-series metric storage.

| Parameter | Description |
|---|---|
| `host` | InfluxDB server URL |
| `token` | Authentication token |
| `org` | InfluxDB organization |

Empty filters are ignored (fix). Multiple measures in union use `toFloat()`/`toString()` with default values `0.0`/`""`.

## Vigilance

- **KVStore multi-collections**: H2 and Speedb support multiple collections. Each collection uses a dedicated store (`MVStore` for H2, separate `SpeedbDB` for Speedb). On H2, the TTL purge daemon runs every 30s. On Speedb, cleanup is done via `forceRemoveTooOldElements()` (call manually if needed).
- **Tika config**: `TikaMimeTypeResolverPlugin` accepts an optional `tikaConfigResource` parameter for custom Tika configuration (TikaConfig file in classpath).
