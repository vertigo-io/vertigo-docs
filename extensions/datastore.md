# DataStore

Le module **DataStore** propose une abstraction de stockage multi-backend organisée autour de quatre managers : **EntityStore**, **FileStore**, **KVStore** et **Cache**.

## EntityStore

L'`EntityStoreManager` offre une persistance CRUD générique sur les objets métier (`Entity`), avec support du critère, du caching et des données de référence (`MasterData`).

### API

| Élément | Rôle |
|---|---|
| `EntityStoreManager` | Interface principale de persistance |
| `EntityStorePlugin` | Plugin de persistance (seul plugin SQL intégré) |
| `EntityStoreConfig` / `EntityStoreConfigImpl` | Configuration par objet (cache, TTL) |
| `MasterDataConfig` / `MasterDataConfigImpl` | Configuration des données de référence |
| `BrokerNN` | Gestion des associations N-N |
| `StoreEvent` | Événements de persistance (création, modification, suppression) |

### Critères

Le `SqlCriteriaEncoder` permet de construire dynamiquement des requêtes SQL à partir de critères (`Criteria`, `Criterion`, `CriteriaExpression`), avec encodeur de filtrage et d'agrégation.

### Plugin SQL

Le `SqlEntityStorePlugin` implémente la persistance relationnelle. Il utilise `SqlCriteriaEncoder` pour construire les requêtes SQL à partir des critères.

### Données de référence

Les `MasterData` et `StaticMasterData` sont chargés via `AbstractMasterDataDefinitionProvider`. L'API expose `MasterDataDefinition` pour la définition des références.

### Métriques

L'`EntityMetricsProvider` expose la métrique `entityCount` (compteur d'accès) pour chaque entité.

## FileStore

Le `FileStoreManager` gère le stockage de fichiers avec résolution MIME et support multi-backend (filesystem, base de données, S3).

### Modèle de données

| Classe | Rôle |
|---|---|
| `VFile` | Représentation générique d'un fichier |
| `FileInfo` | Métadonnées du fichier (nom, taille, MIME, date) |
| `FileInfoURI` | URI pointant vers un fichier dans le store |

### Plugins de stockage

| Plugin | Feature | Description |
|---|---|---|
| `FsFileStorePlugin` | `filestore.filesystem` | Fichiers sur le système de fichiers local |
| `FsFullFileStorePlugin` | `filestore.fullFilesystem` | Accès complet au système de fichiers (lecture/écriture libre) |
| `DbFileStorePlugin` | `filestore.db` | Fichiers stockés en base de données (1 table) |
| `S3FileStorePlugin` | `filestore.s3` | Stockage S3 / MinIO |

### Résolution MIME

| Plugin | Feature | Description |
|---|---|---|
| `TikaMimeTypeResolverPlugin` | `filestore.mimeType.tika` | Détection MIME via Apache Tika (plus précis). Optionnel : paramètre `tikaConfigResource` pour config Tika personnalisée |
| `SimpleMagicMimeTypeResolverPlugin` | `filestore.mimeType.simplemagic` | Détection MIME via signatures binaires (plus léger, `.toLowerCase()`) |

Les tâches de count ajoutent le suffixe `ByCriteria` uniquement si `criteria ≠ alwaysTrue`.

## KVStore

Le `KVStoreManager` offre un stockage clé-valeur avec 6 backends disponibles. L'API expose des collections (`KVCollection`) typées.

### Plugins

| Plugin | Feature | Description |
|---|---|---|
| `BerkeleyKVStorePlugin` | `kvStore.berkeley` | Berkeley DB Java Edition (stockage local, RocksDB-like) |
| `RedisKVStorePlugin` | `kvStore.redis` | Redis (nécessite le connecteur Redis) |
| `SpeedbKVStorePlugin` | `kvStore.speedb` | Speedb (fork optimisé de RocksDB / TtlDB, LZ4_COMPRESSION, multi-collection) |
| `H2KVStorePlugin` | `kvStore.h2` | Base H2 intégrée (MVStore/collection, purge daemon 30s, multi-collection) |
| `EhCacheKVStorePlugin` | `kvStore.ehcache` | EhCache |
| `DelayedMemoryKVStorePlugin` | `kvStore.delayedMemory` | Mémoire avec persistance retardée |

## Cache

Le `CacheManager` propose une abstraction vers la solution de cache pour les autres composants.

| Plugin | Feature | Description |
|---|---|---|
| `MemoryCachePlugin` | `cache.memory` | Cache en mémoire locale *(l'éviction en TTL est définie par le module consommateur)* |
| `RedisCachePlugin` | `cache.redis` | Cache partagé via Redis *(Nécessite le connecteur Redis)* |
| `EhCachePlugin` | `cache.eh` | Cache via EhCache *(Nécessite le fichier de paramétrage `ehcache.xml`)* |

## RedisConnector

Le `RedisConnector` remplace le connecteur Redis antérieur et supporte trois modes de connexion via la feature `jedis`.

### Modes de connexion

| Mode | Paramètres YAML | Description |
|---|---|---|
| Single | `host`, `port`, `database`, `username`, `password`, `ssl`, `trustStoreUrl`, `trustStorePassword`, `maxTotal`, `minIdle` | Connexion à un nœud Redis unique |
| Cluster | `clusterNodes`, `password`, `ssl`, `trustStoreUrl`, `trustStorePassword`, `maxTotal`, `minIdle` | Cluster Redis natif |
| Sentinel | `mastername`, `sentinels`, `database`, `username`, `password`, `ssl`, `trustStoreUrl`, `trustStorePassword`, `maxTotal`, `minIdle` | Via Sentinel (méthode `withJedis`) |

| Paramètre | Single | Cluster | Sentinel |
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

### RedisSingleConnector (déprécié)

Le `RedisSingleConnector` est **déprécié** (`@Deprecated`) et jettera une `UnsupportedOperationException` si utilisé avec un mode Sentinel.

**Migration** : remplacer par `RedisConnector` avec le mode single (paramètres `host`/`port`) ou Sentinel (paramètres `mastername`/`sentinels`).

## Database

### LiquibaseMigrationPlugin

Exécute les migrations de schéma Liquibase au démarrage du module.

| Paramètre | Description |
|---|---|
| `masterFile` | Chemin vers le fichier `changelog-master.xml` |
| `connectionName` | Nom de la connexion JDBI à utiliser |
| `contexts` | Contextes Liquibase à activer |

### InfluxDB

Connecteur InfluxDB pour le stockage de métriques temporelles.

| Paramètre | Description |
|---|---|
| `host` | URL du serveur InfluxDB |
| `token` | Jeton d'authentification |
| `org` | Organisation InfluxDB |

Les filtres vides sont ignorés (correctif). Les mesures multiples en union utilisent `toFloat()` / `toString()` avec valeurs par défaut `0.0` / `""`.

## Pour les experts

### Managers

| Manager | Impl | Feature |
|---|---|---|
| `EntityStoreManager` | `EntityStoreManagerImpl` | `entitystore` |
| `FileStoreManager` | `FileStoreManagerImpl` | `filestore` |
| `KVStoreManager` | `KVStoreManagerImpl` | `kvStore` |
| `CacheManager` | `CacheManagerImpl` | `cache` |

### Features

| Flag | Params | Composants ajoutés |
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

> Les features `jedis`, `jedisSingle`, `jedisCluster`, `jedisSentineled` sont fournies par le module **redis-connector** (connecteur Redis).

### Configuration

Aucun composant n'est activé par défaut (`buildFeatures()` vide). Exemple de configuration :

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

Configuration du connecteur Redis (mode single) :

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

Configuration du connecteur Redis (mode cluster) :

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

Configuration du connecteur Redis (mode Sentinel) :

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

## Vigilance

- **KVStore multi-collections** : H2 et Speedb supportent les collections multiples. Chaque collection utilise un store dédié (`MVStore` pour H2, `SpeedbDB` séparé pour Speedb). Sur H2, le daemon de purge TTL s'exécute toutes les 30s. Sur Speedb, le cleanup se fait via `forceRemoveTooOldElements()` (à appeler manuellement si besoin).
- **Tika config** : `TikaMimeTypeResolverPlugin` accepte un paramètre `tikaConfigResource` optionnel pour une config Tika personnalisée (fichier TikaConfig dans le classpath).
