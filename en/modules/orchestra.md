# Orchestra

**Orchestra** is a module of the Vertigo platform for managing jobs and batches: what is commonly called a job or a batch is called a **process** in Orchestra.

It allows both scheduling and launching processes with a predefined strategy, and provides an API to configure and supervise them.

It includes many features:

- Native multi-node support with load management
- Dead node detection
- Recovery of missed schedules
- Logging (File + DB) (A human can easily access it, including through a UI)
- Delegation of asynchronous processing to another server / another application

## What is a process in Orchestra?

- A process is a sequential list of activities
- A process can be scheduled over time through various strategies (a cron expression, a one-off execution)
- Each planned execution is a **planification**: it is created in advance, from the cron or by a call to the *scheduler*, and becomes an execution when its time comes

## So what is an activity in Orchestra?

- An activity is the unit of execution. It contains the code to be executed.
- An activity manages what happens next in the process
- All activities of a process share a common execution environment called the **workspace**: parameters as keys and values, passed from one activity to the next

## How to use it?

Orchestra offers the following features:
- A process management API
- Two implementations for managing executions
  - Database, with logs, monitoring and multi-node management
  - Memory
- A REST API to manage processes, executions, scheduling and supervision
- An embedded Vue.js UI (see [Embedded UI](#embedded-ui))

When the Orchestra module is added to your application, it can be used in integrated mode or as a standalone node in a micro-services architecture. The [Mars](https://github.com/vertigo-io/vertigo-mars) demo application uses it in integrated mode.

### Adding the module to the pom

```xml
<dependency>
	<groupId>io.vertigo</groupId>
	<artifactId>vertigo-orchestra</artifactId>
	<version>${vertigo.version}</version>
</dependency>
```

### Database mode and memory mode

Each process definition has a **type**, which designates the mode that manages it:

| Type (`ProcessType`) | Mode | Feature |
|---|---|---|
| `SUPERVISED` (default) | Database: definitions kept, execution monitoring, logs, multi-node | `orchestra.database` |
| `UNSUPERVISED` | Memory: nothing is kept from one startup to the next, no execution monitoring | `orchestra.memory` (mandatory parameter: `workersCount`) |

Both features can be enabled together. In memory mode only, definitions must be built with `withProcessType(ProcessType.UNSUPERVISED)` (see [Processes](#processes)). Unless stated otherwise, the rest of this page describes the database mode.
<!-- source : ProcessDefinitionBuilder.java:L78, L174-176 (SUPERVISED par défaut) ; MemoryProcessDefinitionStorePlugin.java:L81-82, MemoryProcessExecutorPlugin.java:L161-162 (UNSUPERVISED) ; OrchestraDefinitionManagerImpl.java:L86-87 ; OrchestraFeatures.java:L144-154 -->

### Database mode configuration

The YAML configuration of Orchestra in database mode, as in Mars:

```yaml
io.vertigo.orchestra.OrchestraFeatures:
  featuresConfig:
    - orchestra.database:
        nodeName: MARS1
        daemonPeriodSeconds: 30
        workersCount: 10
        forecastDurationSeconds: 60
    - orchestra.webapi:
```

| Parameter | Role |
|---|---|
| `nodeName` | Name of the node: it must be specific to each node of the application (in multi-node, it usually comes from an environment variable, for example `${ORCHESTRA_NODE_NAME}`) |
| `daemonPeriodSeconds` | Period, in seconds, of the two Orchestra daemons: the one that schedules executions and the one that runs them |
| `workersCount` | Number of activities the node runs at the same time (the size of its worker pool) |
| `forecastDurationSeconds` | Duration, in seconds, over which the next executions of scheduled processes are planned in advance |

These four parameters are mandatory. The `orchestra.webapi` feature publishes the REST API (see [Driving Orchestra through webservices](#driving-orchestra-through-webservices)); it requires the application's webservices (see [WebServices](/en/basic/webservices)).
<!-- source : OrchestraFeatures.java:L77-85 (findParamByName), L95-112 (daemonPeriodSeconds -> planningPeriodSeconds et executionPeriodSeconds) ; DbProcessExecutorPlugin.java:L144 (pool de workers) ; DbProcessSchedulerPlugin.java:L124, L308 (durée de prévision) ; mars.yaml:L212-219 (master) -->

The whole Orchestra model is declared in `@DataSpace("orchestra")`: the application therefore declares an SQL store for this dataSpace. Its accesses go through the connection designated by the `connectionName` parameter of this store (by default, the main connection). It is recommended to give it a dedicated connection, to isolate Orchestra from the application pool, and to size it consistently with the `workersCount` parameter (see [Multiple connections and dataSpace](/en/extensions/database#multiple-connections-and-dataspace)).

```yaml
io.vertigo.datastore.DataStoreFeatures:
  features:
    - entitystore:
  featuresConfig:
    - entitystore.sql:          # the application store
    - entitystore.sql:          # the Orchestra store
        dataSpace: orchestra
```
<!-- source : domain/*/O*.java (@DataSpace("orchestra")) ; SqlEntityStorePlugin.java:L118-130 (connectionName, défaut main) ; mars.yaml:L136-138 (master) -->

To use Orchestra in database mode, this database must be initialized (table creation and insertion of primary data) with the [`orchestra_create_init_v1.0.0.sql`](https://github.com/vertigo-io/vertigo-modules/blob/master/vertigo-orchestra/src/main/database/scripts/install/orchestra_create_init_v1.0.0.sql) script, written for PostgreSQL.

?> In development, this script and the Orchestra queries also work with H2 (2.x) in PostgreSQL compatibility mode (`MODE=PostgreSQL` in the JDBC URL), as in the local configuration of Mars.
<!-- source : orchestra_create_init_v1.0.0.sql exécuté entièrement avec H2 2.2.224 en MODE=PostgreSQL ; FOR UPDATE et extract('epoch' from …) acceptés ; mars.yaml:L114 (master) -->

### Memory mode configuration

```yaml
io.vertigo.orchestra.OrchestraFeatures:
  featuresConfig:
    - orchestra.memory:
        workersCount: 10
```

## Implementation

### Activities

The code of an activity is carried by an **ActivityEngine**: an interface whose `execute` method receives the workspace of the activity and returns it, completed with its **status**. The abstract class **AbstractActivityEngine** provides its base implementation: a log (`getLogger()`), post-processing after success and after error, and putting the activity on hold for a delegated processing (`setActivityPending`). An activity normally extends this class.

```java
public class MyActivityEngine extends AbstractActivityEngine {

	/** {@inheritDoc} */
	@Override
	public ActivityExecutionWorkspace execute(final ActivityExecutionWorkspace workspace) {
		getLogger().info("Processing");
		// … the processing of the activity
		workspace.setSuccess();
		return workspace;
	}

}
```

The status given to the workspace determines what happens next in the process:

| Workspace method | What happens next |
|---|---|
| `setSuccess()` | Done (`DONE`) |
| `setFinished()` | Done, and the process ends (`DONE`) without running the following activities |
| `setFailure()` | In error (`ERROR`): the process stops |
| `setActivityPending(workspace)` (`AbstractActivityEngine` method) | Waiting for the end of a delegated processing (see [Delegating a processing](#delegating-a-processing)); do not call `workspace.setPending()` directly |

An activity that gives no status, or that throws an exception, ends in error.

?> In memory mode, `setFinished()` does not interrupt the process and delegation is not available.
<!-- source : ActivityEngine.java ; ActivityExecutionWorkspace.java:L204-225 ; AbstractActivityEngine.java:L43-70 ; DbProcessExecutorPlugin.java:L368-382 (statut obligatoire, exception -> échec), L397-419 (putResult : DONE, finishProcessExecution, pending, ERROR), L628-633 ; MemoryProcessExecutorPlugin.java:L113-116, L166-176 -->

**The workspace** carries the parameters of the activity, as keys and values. When an activity ends successfully, its output workspace becomes the input workspace of the next activity: this is the mechanism for sharing data between activities (`workspace.setValue(key, value)`, then `workspace.getValue(key)`).

**The log** of the activity (`getLogger().info(…)`, `warn(…)`, `error(…)`) is saved with its execution, and can be consulted through the API or the UI; in memory mode, it only goes to the application logs.

**The attached file**: an activity can produce a file (a report, an export). It writes it under the directory given by the `orchestra.root.directory` application parameter (read by the `ParamManager`, see [Configuration](/en/basic/configuration)), and indicates its path relative to this directory with `workspace.setAttachment(path)`. The file can then be downloaded through the API.
<!-- source : ActivityExecutionWorkspace.java:L59-81, L181 ; ActivityLogger.java:L54-88 ; DbProcessExecutorPlugin.java:L510-527 (workspace transmis à l'activité suivante), L647-648, L665-681 (saveActivityLogs, journal et pièce jointe) ; DbProcessLoggerPlugin.java:L48, L90-101 (orchestra.root.directory) -->

**Instantiation**: Orchestra creates a new instance of the ActivityEngine for each execution of an activity, and injects the components it needs (`@Inject`). An ActivityEngine is therefore not registered as a component, and keeps no state from one execution to the next.
<!-- source : DbProcessExecutorPlugin.java:L354, MemoryProcessExecutorPlugin.java:L126 (InjectorUtil.newInstance) -->

> A process is only a sequence of activities: an activity should be reusable, so that it can serve several processes.

### Processes

A process is described by a **ProcessDefinition**: its name, its label, the ordered list of its activities and its triggering strategy. It is built with the `ProcessDefinition.builder(name, label)` factory (the `ProcessDefinitionBuilder` constructor is not public).

```java
final ProcessDefinition processDefinition = ProcessDefinition.builder("ProMyProcess", "My process")
		.withCronExpression("0 0 2 * * ?") // every day at 2 am
		.addActivity("EXTRACT", "Extraction", ExtractActivityEngine.class)
		.addActivity("REPORT", "Report", ReportActivityEngine.class)
		.build();
```

!> A `ProcessDefinition` is a Vertigo definition: its name must start with the `Pro` prefix, followed by letters or digits, the first one in upper case (`ProMyProcess`, no `_`), 61 characters at most in total. The name of an activity is free (not empty).
<!-- source : ProcessDefinition.java:L33-35 (@DefinitionPrefix "Pro"), L92-94 (builder) ; DefinitionId.java:L53, L64-67 ; ActivityDefinition.java:L38-41 -->

The builder options:

| Builder method | Effect |
|---|---|
| `addActivity(name, label, engineClass)` | Adds an activity, after the previous ones |
| `withCronExpression(cron)` | Schedules the process. The cron expression uses the Quartz format, with 6 or 7 fields (the year is optional), the first one being the second (Mars: `"0 0/1 * ? * * *"`, every minute) |
| `addInitialParam(name, value)`, `addInitialParams(map)` | Initial parameters, placed in the workspace of the first activity |
| `withMultiExecution()` | Allows several simultaneous executions of the same process |
| `withRescuePeriod(rescuePeriod)` | Period during which a missed planification (the node was stopped) is still caught up |
| `inactive()` | Creates the process deactivated: in database mode, it is not scheduled by its cron |
| `withProcessType(type)` | Process type: `SUPERVISED` (default) or `UNSUPERVISED` (see [Database mode and memory mode](#database-mode-and-memory-mode)) |
| `withMetadatas(map)` | Free metadata associated with the process |
| `withNeedUpdate()` | The code prevails at each startup (see [Process evolution cases](#process-evolution-cases)) |
<!-- source : ProcessDefinitionBuilder.java:L68-172 ; CronExpression.java:L465-470 (année facultative) ; DbProcessSchedulerPlugin.java:L321 (processus actifs), L357-368 (rattrapage) ; mars OrchestraInitializer.java (cron) -->

The definition is registered with the `OrchestraDefinitionManager` manager:

```java
orchestraDefinitionManager.createOrUpdateDefinition(processDefinition);
```

In database mode, it is then kept in the database, which prevails at the following startups (see [Process evolution cases](#process-evolution-cases)).

### Declaring processes in a project

Definitions are registered at application startup. Two practices exist.

**An initializer**, listed in the `initializers` section of the YAML file, which registers all the processes of the application. This is the choice of Mars ([`OrchestraInitializer`](https://github.com/vertigo-io/vertigo-mars/blob/master/src/main/java/io/mars/support/boot/OrchestraInitializer.java)):

```java
public class OrchestraInitializer implements ComponentInitializer {

	@Inject
	private OrchestraDefinitionManager orchestraDefinitionManager;

	/** {@inheritDoc} */
	@Override
	public void init() {
		final ProcessDefinition processDefinition = ProcessDefinition.builder("ProEquipmentDecommissioning", "Equipment decommissioning")
				.withCronExpression("0 0/1 * ? * * *")
				.addActivity("DECOMMISSION", "Decommission equipmenents", DecommissionEquipmentActivityEngine.class)
				.addActivity("REPORT", "Produce a file report of the decommisioned equipments", DecommissioningReportActivityEngine.class)
				.build();
		orchestraDefinitionManager.createOrUpdateDefinition(processDefinition);
		// … the other processes of the application
	}
}
```
It is declared in the YAML file of the application:

```yaml
initializers:
  - io.mars.support.boot.OrchestraInitializer:
```
<!-- source : vertigo-mars OrchestraInitializer.java:L20-35 ; mars.yaml:L319 (master) -->

**One component per process**, registered in the `Features` class of its module: it registers its definition at startup, in its `start()` method (`Activeable`), and can receive its settings from the configuration (`@ParamValue`). For example, a purge whose number of days is a parameter, registered with `.addComponent(PurgeJob.class, Param.of("olderThanDays", "30"))`:

```java
public class PurgeJob implements Component, Activeable {

	private final OrchestraDefinitionManager orchestraDefinitionManager;
	private final Integer olderThanDays;

	@Inject
	public PurgeJob(final OrchestraDefinitionManager orchestraDefinitionManager, @ParamValue("olderThanDays") final Integer olderThanDays) {
		this.orchestraDefinitionManager = orchestraDefinitionManager;
		this.olderThanDays = olderThanDays;
	}

	@Override
	public void start() {
		orchestraDefinitionManager.createOrUpdateDefinition(ProcessDefinition.builder("ProPurge", "Purge of old data")
				.withCronExpression("0 30 5 1/1 * ? *") // every day at 5:30 am
				.addInitialParam("olderThanDays", olderThanDays.toString())
				.addActivity("PURGE", "Purge", PurgeActivityEngine.class)
				.build());
	}

	@Override
	public void stop() {
		// nothing to do
	}
}
```
<!-- source : vertigo-core Activeable (start/stop), ParamValue, Param.java:L80 (Param.of), ModuleConfigBuilder.java:L141 (addComponent avec paramètres) -->

!> In database mode, a definition already registered is not replaced at the next startup: changing the cron, the activities or an initial parameter (here `olderThanDays`) in the code or in the configuration has no effect until the definition is updated (see [Process evolution cases](#process-evolution-cases)).
<!-- source : DbProcessDefinitionStorePlugin.java:L199-218 -->

### Launching an execution

Once the definition is registered, it can be used through the `OrchestraServices` component:
- Schedule new executions (`getScheduler()`)
- Supervise executions (`getReport()`, see [Finding a process and its executions](#finding-a-process-and-its-executions))

The recommended usage is to go through the *scheduler*, which enforces the execution rules of the process: for example, it does not launch a new execution of a process already running, unless it allows multiple execution. The executor (`orchestraServices.getExecutor().execute(…)`) launches an execution directly, without these checks. For an immediate execution, use the `scheduleAt` method of the `ProcessScheduler` with `Instant.now()` as the date:

```java
orchestraServices.getScheduler().scheduleAt(processDefinition, Instant.now(), Map.of());
```

?> In database mode, the execution starts at the next run of the Orchestra daemons (see the `daemonPeriodSeconds` parameter), not at the exact moment of the call.
<!-- source : DbProcessSchedulerPlugin.java:L130, L270-277, L280-288 (exécution multiple) ; DbProcessExecutorPlugin.java:L149, L212-222, L307-321 ; ProcessExecutor.java:L30 -->

!> Each call to `scheduleAt` **adds** a planification: there is no API to cancel a planification already set (see [Process evolution cases](#process-evolution-cases) for the purge of future planifications).

With the `orchestra.webapi` feature, triggering and monitoring are also possible through the REST API: see [Driving Orchestra through webservices](#driving-orchestra-through-webservices).

### Passing parameters to an execution

The third argument of `scheduleAt` is a `Map<String, String>` of initial parameters: it is added to the initial parameters of the definition to form the workspace (`ActivityExecutionWorkspace`) of the first activity of the process.

```java
orchestraServices.getScheduler().scheduleAt(processDefinition, Instant.now(), Map.of("dossierId", "1234"));
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
	final Long preId = workspace.getProcessExecutionId(); // id of the current execution (database mode)
	workspace.setSuccess();
	return workspace;
}
```
<!-- source : ProcessScheduler.java:L38 ; DbProcessExecutorPlugin.java:L461-472 ; ActivityExecutionWorkspace.java:L142 -->

### Delegating a processing

In database mode, an activity can hand its processing over to another server or another application. It calls `setActivityPending(workspace)` (`AbstractActivityEngine` method) and passes to the remote processing the identifier of the activity execution (`workspace.getActivityExecutionId()`) and its token (`workspace.getToken()`): the activity goes into the `PENDING` state. At the end of its processing, the remote server reports it through the [Orchestra REST API](#driving-orchestra-through-webservices), with this identifier and this token: `onSuccess` on success, `onError` (with a message) on error.
<!-- source : AbstractActivityEngine.java:L66-70 ; ActivityExecutionWorkspace.java:L126, L174 ; WsExecutionControl.java:L58-87 ; DbProcessExecutorPlugin.java:L234-243 -->

## Finding a process and its executions

A process execution is identified by its `preId`, and each activity execution by its `aceId`.

- Definitions: `orchestraDefinitionManager.getProcessDefinition(processName)`, or `getAllProcessDefinitions()`.
- Executions, through the report `orchestraServices.getReport()` (database mode only): `getProcessExecutions(processDefinition, status, limit, offset)`, `getProcessExecution(preId)`, `getActivityExecutionsByProcessExecution(preId)`, and the summaries `getSummaryByDate(processDefinition, minDate, maxDate)` and `getSummariesByDate(minDate, maxDate, status)`.
- In the database: `O_PROCESS` (the definitions, one row per version; the version in force has `ACTIVE_VERSION` set to true), `O_PROCESS_EXECUTION` (the executions), `O_ACTIVITY_EXECUTION` (the executions of each activity) and `O_ACTIVITY_LOG` (their logs).
- Through the REST API, or the [embedded UI](#embedded-ui).
<!-- source : OrchestraDefinitionManager.java:L42-49 ; ProcessReport.java:L36-75 ; OrchestraServicesImpl.java:L94-96, OrchestraFeatures.java:L113 (rapport en mode base de données) ; orchestra_create_init_v1.0.0.sql (tables) -->

### Execution lifecycle

A **process** execution starts in the `RUNNING` state, then ends in `DONE`, `ERROR` or `ABORTED`. Each **activity** execution goes through the states of the `ExecutionState` enum:

| State | Description |
|---|---|
| `WAITING` | Waiting for an available worker |
| `RESERVED` | Reserved by a node |
| `SUBMITTED` | Submitted to the worker pool of the node |
| `RUNNING` | Running |
| `DONE` | Ended successfully |
| `ERROR` | Ended in error |
| `ABORTED` | Abandoned: its node was declared dead, or restarted |
| `PENDING` | Waiting for the end of a delegated processing |

?> An activity that stays in `WAITING` for a long time is waiting for a free worker: size the `workersCount` parameter according to the expected parallelism. Not to be confused with a waiting planification, which is simply waiting for its time.
<!-- source : ExecutionState.java ; DbProcessExecutorPlugin.java:L438 (processus RUNNING), L487, L317 ; activityExecutionDAO.ksp:L39-45 ; coreDAO.ksp:L17-58 (ABORTED) ; DbProcessSchedulerPlugin.java:L227 -->

## Process evolution cases

The general principle is that an Orchestra process definition is linked to code: an activity, a service, etc. These definitions are therefore by nature stable over time and do not change at each startup.

In database mode, **the definition stored in the database prevails**. At startup, `createOrUpdateDefinition` replaces an existing definition only if the one **in the database** has the `NEED_UPDATE` flag set to true; otherwise, it keeps the one in the database, with its cron, its activities and its parameters.

!> Common pitfall: changing the cron (or the activities) in the code and redeploying changes nothing.

Three ways to evolve a process:

- **The code prevails at each startup**: build the definition with `withNeedUpdate()`. The flag is stored in the database with the definition: at each startup, the definition from the code replaces the one in the database. In return, a change made through the API or the UI is lost at the next startup.
- **A one-off update, at deployment**: set `NEED_UPDATE` to true in the database, on the row of the version in force of the process (the one whose `ACTIVE_VERSION` is true), usually through a Liquibase script of the delivery. At the next startup, the definition from the code replaces the one in the database, then the flag takes back the value from the code.
- **Only the triggering or the parameters**: the triggering of a process is not carried directly by the definition, but by its `ProcessTriggeringStrategy` (the cron, multiple execution, the rescue period, the initial parameters). It is changed without redeployment with `orchestraDefinitionManager.updateProcessDefinitionProperties(processName, cronExpression, multiExecution, rescuePeriod, active)` (`cronExpression` is an `Optional<String>`: when empty, it removes the cron scheduling), and the initial parameters with `orchestraDefinitionManager.updateProcessDefinitionInitialParams(processName, initialParams)`; or through the REST API, or the UI.

When a definition is replaced, the old version is deactivated (`ACTIVE_VERSION` set to false): its execution history is kept. Replacing the definition, like `updateProcessDefinitionProperties`, purges the future planifications of the process.

There is no deletion of a process: so that it is no longer scheduled, it is deactivated: `active` set to false with `updateProcessDefinitionProperties`, or a definition built with `inactive()`, which only applies to an already registered process through `withNeedUpdate()` or `NEED_UPDATE` (see above). A manual launch remains possible.

?> In memory mode, the definition from the code always replaces the previous one, and it cannot be modified afterwards: `updateProcessDefinitionProperties` and `updateProcessDefinitionInitialParams` are not available.
<!-- source : DbProcessDefinitionStorePlugin.java:L86 (NEED_UPDATE enregistré), L199-218 (drapeau lu sur la définition existante), L221-228 (désactivation, purge), L253 (purge par updateProcessDefinitionProperties) ; processDAO.ksp:L10-11 (version en vigueur), L52-63 ; OrchestraDefinitionManager.java:L78-86 ; MemoryProcessDefinitionStorePlugin.java:L43, L72, L77 -->

## Driving Orchestra through webservices

The `orchestra.webapi` feature publishes the Orchestra REST API, under the prefix of the application's webservices (the `apiPrefix` parameter of `webservices.javalin`, for example `/api`). The API neither creates nor deletes definitions: definitions come from the code.

| Route | Role |
|---|---|
| `GET /orchestra/definitions/{processName}` | Read a definition |
| `POST /orchestra/definitions/_search` (body: `criteria`) | Search definitions by label |
| `PUT /orchestra/definitions/{processName}/properties` (body: `cronExpression`, `multiExecution`, `rescuePeriod`, `active`) | Change the triggering |
| `PUT /orchestra/definitions/{processName}/params` (body: `initialParams`) | Change the initial parameters |
| `GET /orchestra/executions/?processName=&status=&limit=&offset=` | List the executions of a process |
| `GET /orchestra/executions/{preId}` | Read an execution |
| `GET /orchestra/executions/{preId}/activities` | List the activity executions of an execution |
| `GET /orchestra/executions/{preId}/activities/{aceId}` | Read an activity execution |
| `GET /orchestra/executions/{preId}/logFile` | Download the attached file of an execution (the one of the last ended activity) |
| `GET /orchestra/executions/{preId}/activities/{aceId}/attachment` | Download the attached file of an activity |
| `GET /orchestra/executions/{preId}/activities/{aceId}/logFile` | Download the log of an activity |
| `GET /orchestra/executions/summaries/{processName}` | Week summary of a process |
| `GET /orchestra/executions/summaries?weekOffset=&status=` | Week summaries of all processes |
| `POST /orchestra/executionsControl/executeNow` (body: `processName`) | Launch an immediate execution |
| `POST /orchestra/executionsControl/execute` (body: `processName`, `initialParams`) | Launch an immediate execution, with parameters |
| `POST /orchestra/executionsControl/onSuccess` (body: `aceId`, `token`) | Report the successful end of a delegated processing (see [Delegating a processing](#delegating-a-processing)) |
| `POST /orchestra/executionsControl/onError` (body: `aceId`, `token`, `errorMessage`) | Report the end in error of a delegated processing |
| `GET /orchestra/infos/status`, `GET /orchestra/infos/help` | Status and help of the module |

For example, to launch the `ProMyProcess` process:

```http
POST /api/orchestra/executionsControl/executeNow
Content-Type: application/json

{ "processName": "ProMyProcess" }
```
<!-- source : WsDefinition.java:L41-102 ; WsExecution.java:L47-170 ; WsExecutionControl.java:L44-116 ; WsInfos.java:L34-81 ; JavalinWebServerPlugin.java (apiPrefix) ; DbProcessLoggerPlugin.java:L60-101 ; processExecutionDAO.ksp:L25-26 -->

!> This API allows launching and modifying processes: it is reserved for the administration of the application and must be protected, for example with the [`AuthorizationWebFilter`](/en/basic/webservices#servlet-filters-vs-handlerchain) filter on `/api/orchestra/*`, restricted to an administration authorization. If the application delegates processing, the `onSuccess` and `onError` callbacks of the remote server must remain accessible: exclude them from the filter (`url-exclude-pattern` parameter).
<!-- source : AuthorizationWebFilter.java ; AbstractFilter.java:L51 -->

## Embedded UI

The module embeds a Vue.js UI (4 views, labels in French and English), to be integrated into a [Vertigo-UI](/en/extensions/ui) page: a controller and its view, in the layout of the application (see the « Controller: SpringMVC » and « Layout Engine: Thymeleaf Layout » sections of that page). It relies on the REST API: the `orchestra.webapi` feature must be enabled.

- Its files are in the jar, under `io/vertigo/orchestra/static/`: `js/vertigo-orchestra-ui.umd.js` (the components), `js/vertigo-orchestra-ui.js` (which installs them in the Vertigo-UI application, on the `vui-before-plugins` event) and `css/vertigo-orchestra-ui.css`. Vertigo-UI only serves its own resources (`/vertigo-ui/static/`): the application must make these files accessible, for example by copying them into the static resources of its webapp. The example below assumes the JavaScript files copied into `static/js/orchestra/` and the stylesheet into `static/css/orchestra/`.
- The `vui-orchestra` component displays the list of processes, then the detail of a process: its executions, its activities and their logs, its settings, and the launch of an execution. It receives `api-url`, the address of the Orchestra API (the webservices prefix followed by `/orchestra`), and `read-only`.

```html
<head>
	<link rel="stylesheet" th:href="@{/static/css/orchestra/vertigo-orchestra-ui.css}">
	<script th:src="@{/static/js/orchestra/vertigo-orchestra-ui.js}"></script>
	<script th:src="@{/static/js/orchestra/vertigo-orchestra-ui.umd.js}"></script>
</head>
<body>
	<section layout:fragment="content">
		<vui-orchestra th:api-url="@{/api/orchestra}" :read-only="false"></vui-orchestra>
	</section>
</body>
```

!> `read-only` only hides the modification and launch buttons: the webservices remain callable. If the UI is used in production, access to the page and to the API must be protected on the server side (see [Driving Orchestra through webservices](#driving-orchestra-through-webservices)).
<!-- source : vertigo-orchestra/src/main/vuejs/src/main.js (composants), src/views/ (4 vues), src/lang/ (fr, en) ; views/VuOApp.vue:L16 (props apiUrl, readOnly) ; views/VuOProcess.vue:L58 (orchestraUiReadOnly) ; resources/io/vertigo/orchestra/static/ ; vuejs/README.md (« If used in production, you must protect access ») ; VSpringWebConfig.java:L341 -->

Another option, chosen by Mars: building its own process monitoring screens (the [`job`](https://github.com/vertigo-io/vertigo-mars/tree/master/src/main/java/io/mars/job) module: list of processes, detail, executions), with Vertigo-UI, on top of the Orchestra monitoring queries (the PAOs of the `io.vertigo.orchestra.monitoring` package).
<!-- source : vertigo-mars io/mars/job (JobServices, Job*Controller), views/job/*.html -->

## For Experts

### Managers and components

| Component | Nature | Role | Enabled by |
|---|---|---|---|
| `ONodeManager` | Manager | Registration of Orchestra nodes and update of their heartbeat | `orchestra.database` |
| `OrchestraDefinitionManager` | Manager | Management of process definitions | Always active (`buildFeatures`) |
| `OrchestraServices` | Component | Main services: execution, scheduling, reporting, logging | Always active (`buildFeatures`) |
<!-- source : ONodeManager.java:L28, OrchestraDefinitionManager.java:L32 (extends Manager) ; OrchestraServices.java:L32 (extends Component) -->

### Services

| Service | Access | Description |
|---|---|---|
| `ProcessExecutor` | `orchestraServices.getExecutor()` | Execution of processes (sequential, shared workspace) |
| `ProcessScheduler` | `orchestraServices.getScheduler()` | Cron scheduling and one-off executions |
| `ProcessReport` | `orchestraServices.getReport()` | Execution reports (history, statistics) |
| `ProcessLogger` | `orchestraServices.getLogger()` | Access to the logs and attached files of executions |
<!-- source : OrchestraServices.java:L37-54 -->

### Plugins

| Plugin Interface | Implementations | Enabled by |
|---|---|---|
| `ProcessDefinitionStorePlugin` | `DbProcessDefinitionStorePlugin`, `MemoryProcessDefinitionStorePlugin` | `orchestra.database` / `orchestra.memory` |
| `ProcessExecutorPlugin` | `DbProcessExecutorPlugin`, `MemoryProcessExecutorPlugin` | `orchestra.database` / `orchestra.memory` |
| `ProcessSchedulerPlugin` | `DbProcessSchedulerPlugin`, `MemoryProcessSchedulerPlugin` | `orchestra.database` / `orchestra.memory` |
| `ProcessReportPlugin` | `DbProcessReportPlugin` | `orchestra.database` |
| `ProcessLoggerPlugin` | `DbProcessLoggerPlugin` | `orchestra.database` |

### Orchestra Daemon

?> The `DmnODbProcessExecutorDaemon` daemon (period: `daemonPeriodSeconds`) updates the heartbeat of the Orchestra nodes, that is the signal by which each node indicates that it is alive. A node whose heartbeat has not been updated for more than 2 × `daemonPeriodSeconds` is declared dead. This daemon runs in the daemon pool of the platform, shared with the other daemons of the application: if long daemons occupy all the threads of this pool, the heartbeat can be delayed and cause a dead node detection. Check the execution duration of your daemons through the analytics dashboard. Some Orchestra logs give the node identifier, the activity execution identifier and the state; the health checks of the daemon pool (`poolUtilization` and `daemonsAlive`, from version 4.5.0) also help with diagnosis.
<!-- source : DbProcessExecutorPlugin.java:L149, L171, L506-507, L694 ; DaemonManagerImpl.java:L53, L193, L204 -->

### Scheduler: internal classes

| Class | Role |
|---|---|
| `CronExpression` | Parsing and evaluation of Cron expressions |
| `BasicTimerTask` | Basic timer task for scheduling (memory mode) |
| `ReschedulerTimerTask` | Timer task with automatic rescheduling (memory mode) |

### Domain Model (DtObjects)

| DtObject | Description |
|---|---|
| `OProcess` | Process definition |
| `OActivity` | Activity definition |
| `OProcessExecution` | Process execution instance |
| `OActivityExecution` | Activity execution instance |
| `OActivityLog` | Activity log |
| `OActivityWorkspace` | Input or output workspace of an activity execution |
| `ONode` | Orchestra node |
| `OProcessPlanification` | Process planification |
| `OExecutionState` | Execution state |
| `OSchedulerState` | Scheduler state |
| `OProcessType` | Technical table, used as a lock when registering definitions (the type of a process is the Java enum `ProcessType`) |
| `OUser` | Orchestra user |
<!-- source : orchestra_create_init_v1.0.0.sql (o_process_type : 'DUMB') ; processDAO.ksp:L19-26 (TkLockProcessesForInsert) ; ProcessType.java -->

### Features (@Feature)

| Flag | Parameters (mandatory) | Added components |
|---|---|---|
| `orchestra.database` | `nodeName`, `daemonPeriodSeconds`, `workersCount`, `forecastDurationSeconds` | ONodeManager, 8 DAOs, 6 PAOs, 5 DB plugins, ModelDefinitionProvider |
| `orchestra.memory` | `workersCount` | 3 memory plugins (store, scheduler, executor) |
| `orchestra.webapi` | — | WsDefinition, WsExecution, WsExecutionControl, WsInfos |
