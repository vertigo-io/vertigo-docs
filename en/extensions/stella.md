# Stella

Module **Stella** implements a distributed Master-Worker job engine.
It delegates execution of heavy tasks to worker nodes within a farm, via two interchangeable transports: Redis (peer-to-peer) or REST (centralized server).

The Master-Worker pattern separates the work submitter (Master) from the executor (Worker), each running on distinct Vertigo nodes. A single node can be both master and worker.

## Architecture

### Execution Flow

1. The **Master** submits a task via `MasterManager`. Work is encapsulated in a `WorkItem` identified by a UUID.
2. `WorkItem` is placed in the queue of the chosen transport.
3. A **Worker** retrieves the `WorkItem`, instantiates the corresponding `WorkEngine` via dependency injection, and executes `process(W work)`.
4. Result is stored in the transport, then consumed by the Master.

On the Master side, `MasterManagerImpl` uses a `Coordinator` to track in-progress work and results.

On the Worker side, `WorkersManagerImpl` creates a single execution pool (`workersCount` threads). Dispatchers (one per workType) poll the queue via the transport plugin, then delegate to `WorkEngine` via dependency injection. The master consumes results via `DistributedWorkResultWatcher`, polling finished results at the same `pollFrequencyMs` frequency.

### Transports

- **Redis**: peer-to-peer communication via `RedisMasterPlugin` and `RedisWorkersPlugin`. Atomic Redis queues (`lmove`), heartbeat via `SETEX`, namespace `vertigo:work:{workType}:{id}`. Serialization: Java + Base64.
- **REST**: communication via centralized server. `RestMasterPlugin`, `RestMasterWebService`, and `RestWorkersPlugin`. Endpoints: `GET /pollWork/{type}`, `POST /event/{start,success,failure}/{uuid}`. Serialization: Java + GZip + Base64 + JSON.

## API

### WorkEngine

`WorkEngine<W, R>` is the contract interface implemented by the developer.

```java
public interface WorkEngine<W, R> {
    R process(W work);
}
```

Implementation is not thread-safe: a new instance is created per call via dependency injection.

### MasterManager

```java
public interface MasterManager {
    <W, R> WorkPromise<R> process(W work, Class<? extends WorkEngine<W, R>> workEngineClass);
    <W, R> void schedule(W work, Class<? extends WorkEngine<W, R>> workEngineClass, WorkResultHandler<R> handler);
}
```

- `process()`: synchronous call. Returns `WorkPromise<R>`.
- `schedule()`: asynchronous call. Callback `WorkResultHandler<R>` receives events.

### WorkPromise

```java
public interface WorkPromise<R> {
    R join();
}
```

`join()` returns the result or throws a WrappedException on error.

### WorkResultHandler

```java
public interface WorkResultHandler<R> {
    void onStart();
    void onDone(R result, Throwable error);
}
```

A single `onDone` method receives both result AND error. If `error` is null, processing succeeded. If `result` is null, processing failed.

### WorkersManager

`WorkersManager` is a marker interface indicating the node is part of the worker farm.

## Configuration

### Activation

Stella is activated exclusively via `@Feature` annotations in YAML configuration of `StellaFeatures`. No Java DSL method is available — features are declared as follows:

| Feature YAML | Activated Components |
|---|---|
| `master` | `MasterManager` + `MasterManagerImpl` |
| `worker` | `WorkersManager` + `WorkersManagerImpl` |
| `master.redis` | `RedisMasterPlugin` |
| `worker.redis` | `RedisWorkersPlugin` |
| `master.rest` | `RestMasterPlugin`, `RestMasterWebService` |
| `worker.rest` | `RestWorkersPlugin` |

### Worker Parameters

- `workTypes` (required): format `Package.WorkEngineImpl^N;Another^M`. N defines the number of dispatcher threads per type (ScheduledExecutorService).
- `workersCount` (required): size of the single execution pool
- `pollFrequencyMs`: poll frequency, 5000ms default

### Redis Parameters

- `deadWorkTypeTimeoutSeconds`: 60s (master side), timeout before abandoning a workType with no worker
- `timeoutSeconds`: 60s (worker side), TTL of cores
- `connectorName`: Redis connector name, "main" default

### REST Parameters

- `serverUrl`: required on worker side, REST server URL

## REST Transport

`RestMasterWebService` exposes endpoints under prefix `/backend/workQueue` for polling and work event reporting.

## Resilience

### Automatic Retry

On `WorkItem` failure, the system automatically retries up to 3 executions (`MAX_WORK_RETRY_COUNT = 3`) before giving up and propagating the error to the master.

### Dead-node detection

A scheduled daemon (`@DaemonScheduled`, 20s period) detects dead nodes:
- **Master side**: scans workTypes with no active worker heartbeat. In-progress `WorkItem`s are reinjected into the Todo queue.
- **Worker side**: heartbeat published (`SETEX` Redis / REST timestamp). If heartbeat exceeds `timeoutSeconds` (60s default), the node is considered dead.

### Graceful shutdown

Master and worker nodes implement two-phase shutdown:
1. `shutdown()` — stops accepting new work
2. `awaitTermination(60s)` — lets in-progress work complete
3. `shutdownNow()` — forces remaining task termination

### Inactive workType

If no worker handles a `workType`, pending work beyond `deadWorkTypeTimeoutSeconds` is abandoned. The master throws an exception on `.join()` resumption or via `onDone(null, error)`.

## Analytics Tracing

Stella emits events via `AnalyticsManager`, category `distributedwork`.

## Examples

Domain: Project Management.

### 1. Define a WorkEngine

Project statistics calculation:

```java
public final class ProjectStatsWorkEngine implements WorkEngine<Long, ProjectStats> {

    @Inject
    private ProjectServices projectServices;

    @Override
    public ProjectStats process(final Long projectId) {
        return projectServices.calcStats(projectId);
    }
}
```

### 2. WorkEngine with side effects

Project backlog PDF export:

```java
public final class ExportPdfWorkEngine implements WorkEngine<ExportCriteria, String> {

    @Inject
    private BacklogServices backlogServices;

    @Override
    public String process(final ExportCriteria criteria) {
        DtList<TacheDto> backlog = backlogServices.getBacklog(criteria.getProjectId());
        return PdfGenerator.generatePath("backlog_" + criteria.getProjectId(), backlog);
    }
}
```

### 3. Synchronous call

```java
@Inject
private MasterManager masterManager;

public ProjectStats getProjectStats(final Long projectId) {
    WorkPromise<ProjectStats> promise = masterManager.process(projectId, ProjectStatsWorkEngine.class);
    return promise.join();
}
```

Calling thread blocks on `.join()` until result is available. If worker crashes, `join()` throws WrappedException.

### 4. Asynchronous call

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
                Logger.info("Export launched for project " + criteria.getProjectId());
            }

            @Override
            public void onDone(final String result, final Throwable error) {
                if (error != null) {
                    Logger.error("Export failed", error);
                } else {
                    Logger.info("Export available: " + result);
                }
            }
        }
    );
}
```

`onDone()` is called exactly once with either the result or the error.

### 5. Worker node configuration (Redis)

Configuration is done exclusively via YAML:

```yaml
modules:
    io.vertigo.stella.StellaFeatures:
        features:
            - worker:
                workTypes: "my.app.task.ProjectStatsWorkEngine^3;my.app.task.ExportPdfWorkEngine^2"
                workersCount: 5
                pollFrequencyMs: 5000
        featuresConfig:
            - worker.redis:
                  connectorName: "main"
                  timeoutSeconds: 60
```

Separation into pools per workType prevents a long PDF export from blocking statistics calculation.

### 6. Worker node configuration (REST)

```yaml
modules:
    io.vertigo.stella.StellaFeatures:
        features:
            - worker:
                workTypes: "my.app.task.ProjectStatsWorkEngine^3;my.app.task.ExportPdfWorkEngine^2"
                workersCount: 5
        featuresConfig:
            - worker.rest:
                  serverUrl: "http://stella-server:8080"
```

### 7. Master + Worker node configuration (Redis)

A node can be both submitter and executor:

```yaml
modules:
    io.vertigo.stella.StellaFeatures:
        features:
            - master:
            - worker:
                workTypes: "my.app.task.ProjectStatsWorkEngine^3;my.app.task.ExportPdfWorkEngine^2"
                workersCount: 5
        featuresConfig:
            - master.redis:
                  connectorName: "main"
                  deadWorkTypeTimeoutSeconds: 60
            - worker.redis:
                  connectorName: "main"
                  timeoutSeconds: 60
```

### 8. Master-only configuration

`MasterManager` alone requires a transport plugin (Redis or REST). There is **no** local-only execution: `MasterManagerImpl` requires an injected `MasterPlugin`. Useful when the master delegates to other worker nodes without running local workers.

## Dependencies

- **Required**: `vertigo-datamodel`
- **Optional Redis**: `vertigo-redis-connector`
- **Optional REST**: `vertigo-vega`

## Notes

- `WorkEngine` is not thread-safe. An instance is created per call via dependency injection. Do not share mutable state between calls.
- `WorkEngine` parameters (work and result) **must implement `Serializable`** (Java serialization required for Redis and REST transport).
- `WorkPromise.join()` blocks the calling thread. Use `schedule()` with `WorkResultHandler` for non-blocking calls.
- On processing error, the exception is relayed by `join()`. Handler `onDone()` receives the error as the second parameter.
- Automatic retry: each failed `WorkItem` is retried up to 3 times before abandonment.
- Orphaned work (dead node) is reinjected into the Todo queue by the dead-node detection daemon (20s period).

## References

- [vertigo-stella](https://github.com/vertigo-io/vertigo-libs/tree/master/vertigo-stella) on GitHub

## For Experts

### Managers
| Manager | Role | Activated by |
|---|---|---|
| `MasterManager` | Task submission (sync/async) to workers | `master` |
| `WorkersManager` | Execution of tasks received from master | `worker` |

### Internal Components
| Component | Role |
|---|---|
| `WorkEngine<W,R>` | Contract interface implemented by developer |
| `WorkPromise<R>` | Blocking future (`join()`) for synchronous calls |
| `WorkResultHandler<R>` | Async callback (`onStart`, `onDone`) |
| `Coordinator` | Common async work submission interface (implemented separately by `MasterCoordinator` and `WorkersCoordinator`) |
| `WorkListener` | Work event listener interfaces |

### Features (@Feature)
| Flag | Components |
|---|---|
| `master` | `MasterManager` + `MasterManagerImpl` |
| `master.redis` | `RedisMasterPlugin` |
| `master.rest` | `RestMasterPlugin`, `RestMasterWebService` |
| `worker` | `WorkersManager` + `WorkersManagerImpl` |
| `worker.redis` | `RedisWorkersPlugin` |
| `worker.rest` | `RestWorkersPlugin` |

### Plugins
| Plugin | Role | Feature |
|---|---|---|
| `RedisMasterPlugin` | Master coordination via Redis (peer-to-peer) | `master.redis` |
| `RestMasterPlugin` | Master coordination via centralized REST server | `master.rest` |
| `RestMasterWebService` | Server REST endpoints (`/backend/workQueue`) | `master.rest` |
| `RedisWorkersPlugin` | Workers connected via Redis (peer-to-peer) | `worker.redis` |
| `RestWorkersPlugin` | Workers connected via REST client | `worker.rest` |

### YAML Configuration
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
                  workTypes: "my.app.task.ProjectStatsWorkEngine^3;my.app.task.ExportPdfWorkEngine^2"
                  workersCount: 5
                  pollFrequencyMs: 5000
```
