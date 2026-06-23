# Stella

Le module **Stella** implémente un moteur de travail distribué de type Master-Worker.
Il permet de déléguer l'exécution de tâches lourdes à des nœuds workers au sein d'une ferme, via deux transports interchangeables : Redis (pair-à-pair) ou REST (serveur centralisé).

Le pattern Master-Worker sépare l'émetteur de travail (Master) de l'exécutant (Worker), chacun pouvant vivre sur des nœuds Vertigo distincts. Un même nœud peut être à la fois master et worker.

## Architecture

### Flux d'exécution

1. Le **Master** soumet une tâche via `MasterManager`. Le travail est encapsulé dans un `WorkItem` identifié par un UUID.
2. Le `WorkItem` est placé dans la file d'attente du transport choisi.
3. Un **Worker** récupère le `WorkItem`, instancie le `WorkEngine` correspondant via l'injection de dépendances, et exécute `process(W work)`.
4. Le résultat est stocké dans le transport, puis consommé par le Master.

Côté Master, `MasterManagerImpl` délègue à `MasterCoordinator`. Un thread `DistributedWorkResultWatcher` (basé sur `ScheduledExecutorService`) poll les résultats en arrière-plan. Le daemon `DmnWorkerDeadNodeDetector` tourne toutes les 20s pour détecter les nœuds workers inactifs et remettre en file les travaux en cours.

Côté Worker, `WorkersManagerImpl` crée un pool d'exécution par workType. Les dispatchers pollent la file via le plugin de transport, puis délèguent à `WorkersCoordinator` qui exécute dans un `FixedThreadPool`. La classe `Worker<R,W>` instancie le `WorkEngine` via DI et nettoie les ThreadLocals après exécution.

### Transports

- **Redis** : communication pair-à-pair via `RedisMasterPlugin` et `RedisWorkersPlugin`, utilisant RedisDB (Jedis). Les clés préfixées `vertigo:work:` utilisent des transactions atomiques. Le hash tag `{workType}` garantit la compatibilité cluster.
- **REST** : communication via un serveur centralisé. `RestMasterPlugin` (@PathPrefix "/backend/workQueue"), `RestMasterWebService` (endpoints JAX-RS), `RestWorkersPlugin` (client Jersey avec synchronisation par workType et backoff de 2s), et `RestQueueServer` (LinkedBlockingQueue par workType). Le heartbeat REST `heartBeat()` n'est pas implémenté (TODO).

## API

### WorkEngine

`WorkEngine<W, R>` est l'interface contractuelle implémentée par le développeur.

```java
public interface WorkEngine<W, R> {
    R process(W work);
}
```

L'implémentation n'est pas thread-safe : une nouvelle instance est créée par l'injection de dépendances à chaque appel.

### MasterManager

```java
public interface MasterManager {
    <W, R> WorkPromise<R> process(W work, Class<? extends WorkEngine<W, R>> workEngineClass);
    <W, R> void schedule(W work, Class<? extends WorkEngine<W, R>> workEngineClass, WorkResultHandler<R> handler);
}
```

- `process()` : appel synchrone. Retourne un `WorkPromise<R>`.
- `schedule()` : appel asynchrone. Le callback `WorkResultHandler<R>` reçoit les événements.

### WorkPromise

```java
public interface WorkPromise<R> {
    R join();
}
```

`join()` retourne le résultat ou lance une WrappedException en cas d'erreur.

### WorkResultHandler

```java
public interface WorkResultHandler<R> {
    void onStart();
    void onDone(R result, Throwable error);
}
```

Une seule méthode `onDone` reçoit le résultat ET l'erreur. Si `error` est null, le traitement a réussi. Si `result` est null, le traitement a échoué.

### WorkersManager

`WorkersManager` est une interface marqueur indiquant que le nœud fait partie de la ferme de workers.

## Configuration

### Activation

Stella s'active via le DSL `StellaFeatures` :

- `StellaFeatures.withMaster()` : active `MasterManager` seul
- `StellaFeatures.withWorker()` : active `WorkersManager` seul
- `StellaFeatures.withRedisMasterPlugin()` : plugin Redis côté master
- `StellaFeatures.withRedisWorkerPlugin()` : plugin Redis côté worker
- `StellaFeatures.withRestMasterPlugin()` : plugin REST côté master
- `StellaFeatures.withRestWorkerPlugin()` : plugin REST côté worker

Un nœud peut combiner master et worker :

```java
StellaFeatures.withMaster();
StellaFeatures.withWorker();
StellaFeatures.withRedisMasterPlugin();
StellaFeatures.withRedisWorkerPlugin();
```

### Paramètres Worker

- `workTypes` (requis) : au format `Package.WorkEngineImpl^N;Another^M`. N définit le nombre de dispatcher threads par type (ScheduledExecutorService). Parse par `WorkDispatcherConfUtil`.
- `workersCount` (requis) : taille du pool d'exécution unique `FixedThreadPool` dans `WorkersCoordinator`
- `pollFrequencyMs` : fréquence de poll, 5000ms par défaut, entre 100ms et 300s

### Paramètres Redis

- `deadWorkTypeTimeoutSeconds` : 60s (côté master), délai avant abandon d'un workType sans worker
- `timeoutSeconds` : 60s (côté worker), TTL des cœurs
- `connectorName` : nom du connecteur Redis, "main" par défaut

### Paramètres REST

- `serverUrl` : requis côté worker, URL du serveur REST

## Transport Redis

### Clés Redis

Les clés utilisent le préfixe `vertigo:work:` :

| Clé | Type | Usage |
|-----|------|-------|
| `vertigo:works:todo:{workType}` | List | File FIFO des travaux en attente |
| `vertigo:works:in progress:{nodeId}{workType}` | List | Travaux en cours par nœud |
| `vertigo:works:done:{callerNodeId}{workType}` | List | Résultats destinés au caller |
| `vertigo:work:{workType}:{workId}` | Hash | Données du travail : work, result, error, status |
| `vertigo:workers:node:{nodeId}` | String (SETEX) | Heartbeat du nœud (TTL = timeoutSeconds) |
| `vertigo:workers:{workType}` | Set | Workers actifs pour ce workType |
| `vertigo:works:timeout:{workType}` | String | Timestamp d'un workType déclaré mort |

### Mécanisme

Le worker utilise `SETEX` sur `vertigo:workers:node:{nodeId}` avec un TTL égal à `timeoutSeconds`. Le master détecte les nœuds morts quand la clé expire. Les transactions atomiques (HMSET + LPUSH) garantissent la cohérence. Le hash tag `{workType}` dans les clés Redis permet le routing cluster-safe.

## Transport REST

### Endpoints

Préfixe : `/backend/workQueue`

| Méthode | Path | Description |
|---------|------|-------------|
| GET | `pollWork/{workType}?nodeUID=uid` | Retourne `"[uuid, base64]"` ou bloque |
| POST | `event/start/{uuid}` | Signale le début du traitement |
| POST | `event/success/{uuid}` | Retourne le résultat en base64 |
| POST | `event/failure/{uuid}` | Retourne l'exception en base64 |
| GET | `version` | Retourne `"1.0.0"` |

### Mécanisme

`RestWorkersPlugin` utilise un client Jersey avec synchronisation par workType. En cas d'erreur de connexion, le worker applique un backoff exponentiel de 2s. `RestQueueServer` maintient une `LinkedBlockingQueue` par workType. Le heartbeat REST via `heartBeat()` n'est pas implémenté (TODO).

## Résilience

### Heartbeat

Chaque worker envoie un heartbeat toutes les 20s :
- Redis : `SETEX` sur `vertigo:workers:node:{nodeId}`, TTL = `timeoutSeconds`
- REST : heartbeat non implémenté (TODO dans `RestQueueClient.heartBeat()`). Détection via expiration au polling.

### Détection de nœud mort

`DmnWorkerDeadNodeDetector` (20s) vérifie l'état des nœuds. Lorsqu'un worker est considéré mort, les `WorkItem` en cours sur ce nœud sont remis en file pour retry. La constante `MAX_WORK_RETRY_COUNT = 3` existe mais n'est pas utilisée pour limiter les retries réelles dans `RedisDB.checkDeadNodes()`.

### workType inactif

Si aucun worker ne traite un `workType`, les `WorkItem` en attente au-delà de `deadWorkTypeTimeoutSeconds` sont abandonnés. Le master lève une exception à la reprise du `.join()` ou via `onDone(null, error)`.

## Tracing Analytics

Stella émet des événements via `AnalyticsManager`, catégorie `distributedwork` :

1. **workSubmit** : soumission du travail par le master (tags: workType)
2. **workerProcess** : traitement par un worker (measures: `workerPendingDuration`, `workerProcessDuration`)
3. **workResultHandler.onDone** : résultat disponible (measures: success)
4. **distributedWorkResultWatcher** : polling des résultats (measures: `pollResult`, `missingWorkProcessingInfos`)
5. **deadNodeDetector** : détection nodes morts (measures: `retriedWorks`, `abandonnedWorkIds`)

## Exemples

Domaine : Gestion de Projet.

### 1. Définir un WorkEngine

Calcul des statistiques d'un projet :

```java
public final class ProjetStatsWorkEngine implements WorkEngine<Long, ProjetStats> {

    @Inject
    private ProjetServices projetServices;

    @Override
    public ProjetStats process(final Long projetId) {
        return projetServices.calcStats(projetId);
    }
}
```

### 2. WorkEngine avec effet de bord

Export PDF du backlog d'un projet :

```java
public final class ExportPdfWorkEngine implements WorkEngine<ExportCriteria, String> {

    @Inject
    private BacklogServices backlogServices;

    @Override
    public String process(final ExportCriteria criteria) {
        DtList<TacheDto> backlog = backlogServices.getBacklog(criteria.getProjetId());
        return PdfGenerator.generatePath("backlog_" + criteria.getProjetId(), backlog);
    }
}
```

### 3. Appel synchrone

```java
@Inject
private MasterManager masterManager;

public ProjetStats getProjetStats(final Long projetId) {
    WorkPromise<ProjetStats> promise = masterManager.process(projetId, ProjetStatsWorkEngine.class);
    return promise.join();
}
```

Le thread appelant est bloqué sur `.join()` jusqu'à disponibilité du résultat. Si le worker plante, `join()` lève une WrappedException.

### 4. Appel asynchrone

```java
@Inject
private MasterManager masterManager;

public void exportBacklogAsync(final ExportCriteria criteria) {
    masterManager.schedule(
        criteria,
        ExportPdfWorkEngine.class,
        new WorkResultHandler<String>() {
            @Override
            public void onStart() {
                Logger.info("Export lancé pour le projet " + criteria.getProjetId());
            }

            @Override
            public void onDone(final String result, final Throwable error) {
                if (error != null) {
                    Logger.error("Export échoué", error);
                } else {
                    Logger.info("Export disponible : " + result);
                }
            }
        }
    );
}
```

`onDone()` est appelé une seule fois avec soit le résultat, soit l'erreur.

### 5. Configuration d'un nœud worker (Redis)

```java
StellaFeatures.withWorker();
StellaFeatures.withRedisWorkerPlugin();
```

Puis configurez :
- `workTypes` : `"ma.app.task.ProjetStatsWorkEngine^3;ma.app.task.ExportPdfWorkEngine^2"` — 3 threads pour les stats, 2 pour les exports
- `workersCount` : `5`
- `pollFrequencyMs` : `5000`
- `timeoutSeconds` : `60`

La séparation en pools par workType évite qu'un export PDF long bloque le calcul de statistiques.

### 6. Configuration d'un nœud worker (REST)

```java
StellaFeatures.withWorker();
StellaFeatures.withRestWorkerPlugin();
```

Puis configurez :
- `workTypes` : `"ma.app.task.ProjetStatsWorkEngine^3;ma.app.task.ExportPdfWorkEngine^2"`
- `workersCount` : `5`
- `serverUrl` : `"http://stella-server:8080"`

### 7. Configuration d'un nœud master + worker (Redis)

Un nœud peut être à la fois émetteur et exécutant :

```java
StellaFeatures.withMaster();
StellaFeatures.withWorker();
StellaFeatures.withRedisMasterPlugin();
StellaFeatures.withRedisWorkerPlugin();
```

Puis configurez :
- `deadWorkTypeTimeoutSeconds` : `60`
- `workTypes` : `"ma.app.task.ProjetStatsWorkEngine^3;ma.app.task.ExportPdfWorkEngine^2"`
- `workersCount` : `5`
- `connectorName` : `"main"`

### 8. Configuration master seul

```java
StellaFeatures.withMaster();
```

`MasterManager` seul nécessite un plugin de transport (Redis ou REST). Il n'existe **pas** d'exécution locale sans plugin : `MasterManagerImpl` exige un `MasterPlugin` injecté. Utile quand le master délègue à d'autres nodes worker, sans faire tourner de workers locaux.

## Dépendances

- **Obligatoire** : `vertigo-datamodel`
- **Optionnel Redis** : `vertigo-redis-connector`, `jedis`
- **Optionnel REST** : `vertigo-vega` (annotations JAX-RS), `jersey-client`

## Vigilance

- `WorkEngine` n'est pas thread-safe. Une instance est créée par appel via l'injection de dépendances. Ne pas partager d'état mutable entre les appels.
- Le heartbeat REST `heartBeat()` n'est pas implémenté (TODO). Privilégier Redis dans les déploiements exigeant une détection de défaillance fiable.
- `WorkPromise.join()` bloque le thread appelant. Utiliser `schedule()` avec `WorkResultHandler` pour les appels non bloquants.
- En cas d'erreur durant le traitement, `WrappedException` est levée par `join()`. Le handler `onDone()` reçoit l'erreur en second paramètre.

## Références

- [vertigo-stella](https://github.com/vertigo-io/vertigo-libs/tree/master/vertigo-stella) sur GitHub
