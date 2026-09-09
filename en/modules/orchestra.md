# Orchestra

**Orchestra** is a Vertigo platform module for job and batch management.

It allows scheduling and launching processes with a predefined strategy, and provides an API to configure and monitor them.

It includes many features:

- Native multi-node support with load management
- Dead node detection
- Recovery of missed schedules
- Logging (File + DB) (Accessible by humans, including via a UI)
- Delegation of asynchronous processing to another server / another application

## What is a process in Orchestra?

- A process is a sequential list of activities
- A process can be scheduled over time using various strategies

## So what is an activity in Orchestra?

- An activity is the execution unit. It contains the code to be executed.
- An activity manages the next step of the process
- All activities in a process share a common execution environment called workspace

## How to use it?

Orchestra provides the following features:
- A process management API
- Two implementations for execution management
  - Database with logging, monitoring, and multi-node management (only PostgreSQL is currently supported)
  - Memory
- A REST API to manage processes, executions, scheduling, and monitoring

When the Orchestra module is added to your application, it can be used in embedded mode or as a standalone node in a micro-services architecture (see the vertigo-orchestra-demo project).

> An embedded Vue.js UI exists (4 views, i18n fr/en, Vite build) but is not prod-ready.

The YAML configuration for Orchestra in database mode is as follows:

```yaml
io.vertigo.orchestra.OrchestraFeatures:
    features:
        - orchestra.database:
              nodeName: NODE_ID
              daemonPeriodSeconds: 30
              workersCount: 10
              forecastDurationSeconds: 60
        - orchestra.webapi:
```

To use Orchestra in database mode, you must initialize the database (table creation and primary data insertion) using [this](https://github.com/vertigo-io/vertigo-modules/blob/master/vertigo-orchestra/src/main/database/scripts/install/orchestra_create_init_v1.0.0.sql) SQL file.

?> The whole Orchestra model is declared with `@DataSpace("orchestra")`: its SQL accesses go through the connection named `orchestra`. It is recommended to declare a dedicated connection pool under this name, to isolate Orchestra from the application pool, and to size it consistently with the `workersCount` parameter.

## What does it look like in code?

### Writing an ActivityEngine

We've seen that an activity contains the source code to execute. More specifically, this code is contained in an *ActivityEngine* which is an interface that ActivityEngines must implement.

The abstract class **AbstractActivityEngine** implements *ActivityEngine* and adds the code necessary to manage logs and other services.

> It is recommended to extend this abstract class to build your *Engine*.

Your first *ActivityEngine*, which we'll call *MyFirstActivityEngine*, will look like

```java
package io.vertigo.orchestra.execution.engine;

import io.vertigo.orchestra.impl.services.execution.AbstractActivityEngine;
import io.vertigo.orchestra.services.execution.ActivityExecutionWorkspace;

public class MyFirstActivityEngine extends AbstractActivityEngine {

	/** {@inheritDoc} */
	@Override
	public ActivityExecutionWorkspace execute(final ActivityExecutionWorkspace workspace) {
		return workspace;
	}

}
```

To manage the return status at the end of an activity, simply modify the workspace state before returning it.
For example, to declare that the activity ends with success:

```java
/** {@inheritDoc} */
@Override
public ActivityExecutionWorkspace execute(final ActivityExecutionWorkspace workspace) {
    workspace.setSuccess();
	return workspace;
}
```

If an activity ends with success, the next activity of the process is launched. The output workspace of the previous activity is used as input for the new activity. This is the mechanism that enables data sharing between activities.

> When writing an activity, keep in mind making it reusable because a process is nothing more than an arrangement of activities.

Now that we have an ActivityEngine, let's associate it with our first process.

### Defining a new process

To create a new process, we need to create a new `ProcessDefinition`.
To build a `ProcessDefinition`, it is necessary to use the static factory `ProcessDefinition.builder()` (the `ProcessDefinitionBuilder` constructor is package-private).

Here is our first ProcessDefinition:

```java
final ProcessDefinition myFirstProcessDefinition = ProcessDefinition.builder("MY_FIRST_ONE", "My first process")
			.addActivity("ACTIVITY", "First activity", MyFirstActivityEngine.class)
			.build();
```

Note that our first process has a single activity using the *MyFirstActivityEngine* engine.

Using the builder, it is very easy to configure your process (for the different options, see the Javadoc).
One important option is the ability to schedule a process execution via a Cron Expression.

Once the definition is created, it must be registered. To do this, simply call the appropriate method on the `OrchestraDefinitionManager` Component (you can inject it into your Component to retrieve it).

```java
orchestraDefinitionManager.createOrUpdateDefinition(myFirstProcessDefinition);
```

Once the definition is registered, it can then be used via the services offered by the `OrchestraServices` class:
- Monitor executions
- Schedule new executions

!> Execution is always launched via the *scheduler*. If you want to launch an execution immediately, simply use the `scheduleAt` method of `ProcessScheduler` with date `Instant.now()`

For example:

```java
orchestraServices.getScheduler().scheduleAt(myFirstProcessDefinition, Instant.now(), Collections.emptyMap());
orchestraServices.getReport().getSummaryByDate(myFirstProcessDefinition,
	Instant.parse("2017-01-01T00:00:00Z"), Instant.parse("2017-12-31T23:59:59Z"));
```

!> Each call to `scheduleAt` **adds** a scheduling entry: there is no API to cancel an already placed scheduling (see [Process evolution cases](#process-evolution-cases) for the purge of future schedulings).

### Passing parameters to an execution

The third argument of `scheduleAt` is a `Map<String, String>` of initial parameters: it initializes the workspace (`ActivityExecutionWorkspace`) of the first activity of the process.

```java
orchestraServices.getScheduler().scheduleAt(myFirstProcessDefinition, Instant.now(), Map.of("dossierId", "1234"));
```

On the `ActivityEngine` side, the workspace gives access to these parameters:

```java
/** {@inheritDoc} */
@Override
public ActivityExecutionWorkspace execute(final ActivityExecutionWorkspace workspace) {
    if (workspace.containsKey("dossierId")) {
        final String dossierId = workspace.getValue("dossierId");
        // ...
    }
    final Long preId = workspace.getProcessExecutionId(); // id of the current execution
    workspace.setSuccess();
    return workspace;
}
```

With the `orchestra.webapi` feature, tracking and triggering are also available via the REST API:
- `GET /orchestra/executions/?processName=&status=&limit=&offset=`: lists the executions of a process (`WsExecution`)
- `GET /orchestra/executions/{preId}/activities`: details of the activities of an execution
- `POST /orchestra/executionsControl/execute` and `POST /orchestra/executionsControl/executeNow`: triggers an execution (`WsExecutionControl`)

### Execution lifecycle

The state of an execution is carried by the `ExecutionState` enum:

| State | Description |
|---|---|
| `WAITING` | Waiting for an available worker |
| `RESERVED` | Reserved by a node (multi-node) |
| `SUBMITTED` | Submitted to the node's worker pool |
| `RUNNING` | Currently running |
| `DONE` | Completed successfully |
| `ERROR` | Ended in error |
| `ABORTED` | Aborted |
| `PENDING` | Waiting for the end of a delegated (asynchronous) processing |

?> `WAITING` is the nominal state of a scheduled execution: it is simply waiting for a worker to become available. If executions stay in `WAITING` for a long time, size the `workersCount` parameter (default 10) according to the expected parallelism.

## Process evolution cases

The general principle is that an Orchestra process definition is tied to code: an activity, a service, etc. These definitions are therefore naturally stable over time and do not change at each startup.
By default, the definition is stored in the database. When it is necessary to update a new version of the process, you must include in the deployment procedure an update of the definition in the database
with needUpdate=true (typically, this is done via a liquibase script). With this parameter, at startup the system will update the definition in the database from the definition in the code.

For a change to the triggering configuration, this is not directly in the definition but in the "ProcessTriggeringStrategy".
This information can be modified via the API (updateProcessDefinitionProperties), and some UIs allow modifying the cron directly from the user interface.

!> `createOrUpdateDefinition` only purges future schedulings if the definition was built with `withNeedUpdate()`: without this flag, already placed schedulings are kept. `updateProcessDefinitionProperties` also purges future schedulings.

## For Experts

### Managers

| Manager | Role | Activated by |
|---|---|---|
| `ONodeManager` | Orchestra node management (dead node detection, load) | `orchestra.database` |
| `OrchestraDefinitionManager` | Process definition management | Always active (`buildFeatures`) |
| `OrchestraServices` | Main services: execution, scheduling, reporting, logging | Always active (`buildFeatures`) |

### Services

| Service | Interface | Description |
|---|---|---|
| `ProcessExecutor` | `ProcessExecutor` | Process execution (sequential, shared workspace) |
| `ProcessScheduler` | `ProcessScheduler` | Cron scheduling and one-shot executions |
| `ProcessReport` | `ProcessReport` | Execution reports (history, statistics) |
| `ProcessLogger` | `ProcessLogger` | Execution and activity logging |

### Plugins

| Plugin Interface | Implementations | Activated by |
|---|---|---|
| `ProcessDefinitionStorePlugin` | `DbProcessDefinitionStorePlugin`, `MemoryProcessDefinitionStorePlugin` | `orchestra.database` / `orchestra.memory` |
| `ProcessExecutorPlugin` | `DbProcessExecutorPlugin`, `MemoryProcessExecutorPlugin` | `orchestra.database` / `orchestra.memory` |
| `ProcessSchedulerPlugin` | `DbProcessSchedulerPlugin`, `MemoryProcessSchedulerPlugin` | `orchestra.database` / `orchestra.memory` |
| `ProcessReportPlugin` | `DbProcessReportPlugin` | `orchestra.database` |
| `ProcessLoggerPlugin` | `DbProcessLoggerPlugin` | `orchestra.database` |

### Orchestra Daemon

**Note**: The `DmnODbProcessExecutorDaemon` daemon (`daemonPeriodSeconds`, default 30s) updates orchestra node heartbeats. Another long-running daemon (>60s) executing simultaneously in the shared pool can prevent this heartbeat and trigger a dead node detection. Check your daemon execution duration via the analytics dashboard. Orchestra logs include node id, activityExecution id, and state; the daemon pool `poolUtilization` healthcheck also helps with diagnosis.

### Scheduler Internals

| Class | Role |
|---|---|
| `CronExpression` | Parsing and evaluation of Cron expressions |
| `BasicTimerTask` | Basic timer task for scheduling |
| `ReschedulerTimerTask` | Timer task with automatic rescheduling |

### WebServices API (REST)

| WebService | Description |
|---|---|
| `WsDefinition` | CRUD of process definitions |
| `WsExecution` | Launching and tracking executions |
| `WsExecutionControl` | Execution control (stop, restart) |
| `WsInfos` | Monitoring / supervision information |

### Domain Model (DtObjects)

| DtObject | Description |
|---|---|
| `OProcess` | Process definition |
| `OActivity` | Activity definition |
| `OProcessExecution` | Process execution instance |
| `OActivityExecution` | Activity execution instance |
| `OActivityLog` | Activity log |
| `OActivityWorkspace` | Workspace shared between activities |
| `ONode` | Orchestra node |
| `OProcessPlanification` | Process scheduling |
| `OExecutionState` | Execution state |
| `OSchedulerState` | Scheduler state |
| `OProcessType` | Process type (SUPERVISED, UNSUPERVISED) |
| `OUser` | Orchestra user |

### Features (@Feature)

| Flag | Parameters | Components added |
|---|---|---|
| `orchestra.database` | `nodeName`, `daemonPeriodSeconds`, `workersCount`, `forecastDurationSeconds` | ONodeManager, 8 DAOs, 6 PAOs, 5 DB plugins, ModelDefinitionProvider |
| `orchestra.memory` | `workersCount` | 3 memory plugins (store, scheduler, executor) |
| `orchestra.webapi` | — | WsDefinition, WsExecution, WsExecutionControl, WsInfos |

### Configuration YAML

```yaml
io.vertigo.orchestra.OrchestraFeatures:
    features:
        - orchestra.database:
              nodeName: NODE_ID
              daemonPeriodSeconds: 30
              workersCount: 10
              forecastDurationSeconds: 60
        - orchestra.webapi:
```