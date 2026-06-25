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

Côté Master, `MasterManagerImpl` utilise un `Coordinator` pour suivre les travaux en cours et les résultats.

Côté Worker, `WorkersManagerImpl` crée un pool d'exécution unique (`workersCount` threads). Les dispatchers (un par workType) pollent la file via le plugin de transport, puis délèguent à `WorkEngine` via l'injection de dépendances. Le master consomme les résultats via `DistributedWorkResultWatcher` qui poll les résultats finis à la même fréquence `pollFrequencyMs`.

### Transports

- **Redis** : communication pair-à-pair via `RedisMasterPlugin` et `RedisWorkersPlugin`. Files atomiques Redis (`lmove`), heartbeat via `SETEX`, namespace `vertigo:work:{workType}:{id}`. Sérialisation : Java + Base64.
- **REST** : communication via un serveur centralisé. `RestMasterPlugin`, `RestMasterWebService`, et `RestWorkersPlugin`. Endpoints : `GET /pollWork/{type}`, `POST /event/{start,success,failure}/{uuid}`. Sérialisation : Java + GZip + Base64 + JSON.

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

Stella s'active exclusivement via les annotations `@Feature` dans la configuration YAML du module `StellaFeatures`. Aucune méthode Java DSL n'est disponible — les features sont déclarées comme suit :

| Feature YAML | Composants activés |
|---|---|
| `master` | `MasterManager` + `MasterManagerImpl` |
| `worker` | `WorkersManager` + `WorkersManagerImpl` |
| `master.redis` | `RedisMasterPlugin` |
| `worker.redis` | `RedisWorkersPlugin` |
| `master.rest` | `RestMasterPlugin`, `RestMasterWebService` |
| `worker.rest` | `RestWorkersPlugin` |

### Paramètres Worker

- `workTypes` (requis) : au format `Package.WorkEngineImpl^N;Another^M`. N définit le nombre de dispatcher threads par type (ScheduledExecutorService).
- `workersCount` (requis) : taille du pool d'exécution unique
- `pollFrequencyMs` : fréquence de poll, 5000ms par défaut

### Paramètres Redis

- `deadWorkTypeTimeoutSeconds` : 60s (côté master), délai avant abandon d'un workType sans worker
- `timeoutSeconds` : 60s (côté worker), TTL des cœurs
- `connectorName` : nom du connecteur Redis, "main" par défaut

### Paramètres REST

- `serverUrl` : requis côté worker, URL du serveur REST

## Transport REST

`RestMasterWebService` expose des endpoints sous le préfixe `/backend/workQueue` pour le polling et le signalement des événements de travail.

## Résilience

### Retry automatique

En cas d'échec d'un `WorkItem`, le système tente automatiquement jusqu'à 3 exécutions (`MAX_WORK_RETRY_COUNT = 3`) avant d'abandonner et de propager l'erreur au master.

### Dead-node detection

Un daemon planifié (`@DaemonScheduled`, période 20s) détecte les nœuds morts :
- **Côté master** : scan des workTypes sans heartbeat worker actif. Les `WorkItem` en cours sont réinjectés dans la file Todo.
- **Côté worker** : heartbeat publié (`SETEX` Redis / timestamp REST). Si le heartbeat dépasse `timeoutSeconds` (60s par défaut), le nœud est considéré mort.

### Graceful shutdown

Les nœuds master et worker implémentent un arrêt en deux phases :
1. `shutdown()` — arrête l'acceptation de nouveaux travaux
2. `awaitTermination(60s)` — laisse les travaux en cours se terminer
3. `shutdownNow()` — force l'arrêt des tâches restantes

### workType inactif

Si aucun worker ne traite un `workType`, les travaux en attente au-delà de `deadWorkTypeTimeoutSeconds` sont abandonnés. Le master lève une exception à la reprise du `.join()` ou via `onDone(null, error)`.

## Tracing Analytics

Stella émet des événements via `AnalyticsManager`, catégorie `distributedwork`.

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

La configuration se fait exclusivement via YAML :

```yaml
modules:
    io.vertigo.stella.StellaFeatures:
        features:
            - worker:
                workTypes: "ma.app.task.ProjetStatsWorkEngine^3;ma.app.task.ExportPdfWorkEngine^2"
                workersCount: 5
                pollFrequencyMs: 5000
        featuresConfig:
            - worker.redis:
                  connectorName: "main"
                  timeoutSeconds: 60
```

La séparation en pools par workType évite qu'un export PDF long bloque le calcul de statistiques.

### 6. Configuration d'un nœud worker (REST)

```yaml
modules:
    io.vertigo.stella.StellaFeatures:
        features:
            - worker:
                workTypes: "ma.app.task.ProjetStatsWorkEngine^3;ma.app.task.ExportPdfWorkEngine^2"
                workersCount: 5
        featuresConfig:
            - worker.rest:
                  serverUrl: "http://stella-server:8080"
```

### 7. Configuration d'un nœud master + worker (Redis)

Un nœud peut être à la fois émetteur et exécutant :

```yaml
modules:
    io.vertigo.stella.StellaFeatures:
        features:
            - master:
            - worker:
                workTypes: "ma.app.task.ProjetStatsWorkEngine^3;ma.app.task.ExportPdfWorkEngine^2"
                workersCount: 5
        featuresConfig:
            - master.redis:
                  connectorName: "main"
                  deadWorkTypeTimeoutSeconds: 60
            - worker.redis:
                  connectorName: "main"
                  timeoutSeconds: 60
```

### 8. Configuration master seul

`MasterManager` seul nécessite un plugin de transport (Redis ou REST). Il n'existe **pas** d'exécution locale sans plugin : `MasterManagerImpl` exige un `MasterPlugin` injecté. Utile quand le master délègue à d'autres nœuds workers, sans faire tourner de workers locaux.

## Dépendances

- **Obligatoire** : `vertigo-datamodel`
- **Optionnel Redis** : `vertigo-redis-connector`
- **Optionnel REST** : `vertigo-vega`

## Vigilance

- `WorkEngine` n'est pas thread-safe. Une instance est créée par appel via l'injection de dépendances. Ne pas partager d'état mutable entre les appels.
- `WorkEngine` et ses paramètres (work et result) **doivent implémenter `Serializable`** (sérialisation Java nécessaire pour le transport Redis et REST).
- `WorkPromise.join()` bloque le thread appelant. Utiliser `schedule()` avec `WorkResultHandler` pour les appels non bloquants.
- En cas d'erreur durant le traitement, l'exception est relayée par `join()`. Le handler `onDone()` reçoit l'erreur en second paramètre.
- Retry automatique : chaque `WorkItem` échoué est réessayé jusqu'à 3 fois avant abandon.
- Les travaux orphelins (node mort) sont réinjectés dans la file Todo par le daemon de détection de nœuds morts (période 20s).

## Références

- [vertigo-stella](https://github.com/vertigo-io/vertigo-libs/tree/master/vertigo-stella) sur GitHub

## Pour les experts

### Managers
| Manager | Rôle | Activé par |
|---|---|---|
| `MasterManager` | Soumission de tâches (synchrone/asynchrone) vers les workers | `master` |
| `WorkersManager` | Exécution des tâches reçues du master | `worker` |

### Composants internes
| Composant | Rôle |
|---|---|
| `WorkEngine<W,R>` | Interface contractuelle implémentée par le développeur |
| `WorkPromise<R>` | Future bloquante (`join()`) pour l'appel synchrone |
| `WorkResultHandler<R>` | Callback asynchrone (`onStart`, `onDone`) |
| `Coordinator` | Interface commune de soumission asynchrone de travaux (implémentée séparément par `MasterCoordinator` et `WorkersCoordinator`) |
| `WorkListener` | Interfaces d'écoute des événements de travail |

### Features (@Feature)
| Flag | Composants |
|---|---|
| `master` | `MasterManager` + `MasterManagerImpl` |
| `master.redis` | `RedisMasterPlugin` |
| `master.rest` | `RestMasterPlugin`, `RestMasterWebService` |
| `worker` | `WorkersManager` + `WorkersManagerImpl` |
| `worker.redis` | `RedisWorkersPlugin` |
| `worker.rest` | `RestWorkersPlugin` |

### Plugins
| Plugin | Rôle | Feature |
|---|---|---|
| `RedisMasterPlugin` | Coordination master via Redis (pair-à-pair) | `master.redis` |
| `RestMasterPlugin` | Coordination master via serveur REST centralisé | `master.rest` |
| `RestMasterWebService` | Endpoints REST du serveur (`/backend/workQueue`) | `master.rest` |
| `RedisWorkersPlugin` | Workers connectés via Redis (pair-à-pair) | `worker.redis` |
| `RestWorkersPlugin` | Workers connectés via client REST | `worker.rest` |

### Configuration YAML
```yaml
modules:
    io.vertigo.stella.StellaFeatures:
        features:
            - master:
            - worker:
        featuresConfig:
            - master.redis:
                  connectorName: "main"
                  deadWorkTypeTimeoutSeconds: 60
            - worker.redis:
                  connectorName: "main"
                  timeoutSeconds: 60
            - worker:
                  workTypes: "ma.app.task.ProjetStatsWorkEngine^3;ma.app.task.ExportPdfWorkEngine^2"
                  workersCount: 5
                  pollFrequencyMs: 5000
```
