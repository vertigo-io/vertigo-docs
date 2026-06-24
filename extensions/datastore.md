# DataStore

Le module **DataStore** est le successeur de l'ancien module `vertigo-dynamo`. Il propose une abstraction de stockage multi-backend organisée autour de quatre managers : **EntityStore**, **FileStore**, **KVStore** et **Cache**.

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

L'`EntityMetricsProvider` expose les statistiques d'accès (temps, hits, misses) pour chaque entité.

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
| `TwoTablesDbFileStorePlugin` | — | Fichiers stockés en base de données (2 tables : infos + contenu) |
| `S3FileStorePlugin` | `filestore.s3` | Stockage S3 / MinIO |

### Résolution MIME

| Plugin | Feature | Description |
|---|---|---|
| `TikaMimeTypeResolverPlugin` | `filestore.mimeType.tika` | Détection MIME via Apache Tika (plus précis) |
| `SimpleMagicMimeTypeResolverPlugin` | `filestore.mimeType.simplemagic` | Détection MIME via signatures binaires (plus léger) |

## KVStore

Le `KVStoreManager` offre un stockage clé-valeur avec 6 backends disponibles. L'API expose des collections (`KVCollection`) typées.

### Plugins

| Plugin | Feature | Description |
|---|---|---|
| `BerkeleyKVStorePlugin` | `kvStore.berkeley` | Berkeley DB Java Edition (fichiers LMDB-like) |
| `RedisKVStorePlugin` | `kvStore.redis` | Redis (distribué, support clustering) |
| `SpeedbKVStorePlugin` | `kvStore.speedb` | Speedb (fork optimisé de RocksDB) |
| `H2KVStorePlugin` | `kvStore.h2` | Base H2 intégrée |
| `EhCacheKVStorePlugin` | `kvStore.ehcache` | EhCache (cache distribué) |
| `DelayedMemoryKVStorePlugin` | `kvStore.delayedMemory` | Mémoire avec persistance retardée |

## Cache

Le `CacheManager` propose une abstraction vers la solution de cache pour les autres composants.

| Plugin | Feature | Description |
|---|---|---|
| `MemoryCachePlugin` | `cache.memory` | Cache en mémoire locale *(l'éviction en TTL est définie par le module consommateur)* |
| `RedisCachePlugin` | `cache.redis` | Cache partagé via Redis *(Nécessite le connecteur Redis)* |
| `EhCachePlugin` | `cache.eh` | Cache via EhCache *(Nécessite le fichier de paramétrage `ehcache.xml`)* |

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

### Configuration

Aucun composant n'est activé par défaut (`buildFeatures()` vide). Exemple de configuration :

```yaml
modules:
  io.vertigo.datastore.DataStoreFeatures:
    features:
      - entitystore:
      - cache:
    featuresConfig:
      - entitystore.sql:
      - cache.redis:
          host: localhost
          port: 6379
```
