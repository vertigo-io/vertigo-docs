# Core

Vertigo-core is the lightweight foundation that powers a Vertigo application.
It is very light, very robust, yet features a full-featured design born from several decades of effort.

Its responsibilities for a Vertigo application are:

- **Configure**: describes what the application does and how it does it
- **Run**: starts and stops the application
- **Monitor**: collects statistics to evaluate application state at any moment

To accomplish this, an application consists of two distinct spaces:
- **ComponentSpace**: the component space, corresponding to processing logic (pure, stateless functions)
- **DefinitionSpace**: the definition space, corresponding to immutable information describing the elements manipulated by the application.

The startup cycle therefore aims to populate these two spaces. Once the application has started, both spaces are locked (they can no longer be modified), and the application state cannot be altered.
This results in a robust application with reproducible behavior, no side effects—in short, __reliable__.

## Configuration

Within the configuration concept, we chose to differentiate the __structural__ configuration of an application (what it does) from its parameters (which influence how it operates).
Thus, a Vertigo application is configured through two very distinct mechanisms:

- configuration: lists the application's modules and, for each module, the activated features (via two methods: YAML file or Java API)
- parameters: provides values for named parameters used by components. (parameter values can be supplied through as many methods as needed via dedicated plugins)

The application configuration is therefore inherently immutable, which is not the case for parameters, which can follow their own strategy.

An application consists of modules, each contributing both its __definitions__ and its __components__.

## Run

Starting from the application configuration and parameters, it is then possible to create an execution node (Node).
The startup cycle is as follows:

1. Creation of all components: module by module, using a control inversion mechanism to resolve component dependencies
2. Locking of the component space (no new component can be registered)
3. Registration of all definitions: module by module via DefinitionProvider, with components themselves potentially serving as DefinitionProvider
4. Locking of the definition space (no new definition can be registered)
5. Startup of all components: invoking the start() method on activatable components, which now have access to the definition space
(5.bis Creation of ephemeral _Initializer_ components for certain needs)
6. Execution of pre-activation functions registered during component startup.

At the end of this startup cycle, the _Node_ is ready, and all its features are available via its components.

When the application node stops, all components are shut down in reverse order of their startup.

Additionally, Vertigo-Core provides a dedicated execution environment for daemons (recurring technical tasks) through the DaemonManager. To register a new daemon, simply create a `DaemonDefinition`.
A simplified approach is to add the `@DaemonScheduled` annotation to a public method of a component registered in the ComponentSpace.

## Monitor

Once an application has started, it is important to monitor its activity and performance.
An analytics module is natively included in Vertigo to provide fine-grained tracking of executed processes.
It supports three types of indicators:

- **HealthStatus**: indicates a health state (red, orange, green) for a specific function
- **Trace**: traces complete executions within the application via nestable `TraceSpan`. Each span represents a control point and measures the nature and duration of processes.
- **Metric**: records metrics at regular time intervals to track the evolution of an application characteristic over time.

Probes are placed at strategic points within processing logic across various Vertigo extensions. Each project / supplementary module can add new control points for each indicator type.


## Plugin API

- **analytics.socketLoggerConnector**: Analytics data is sent using the log4j/log4j2 SocketAppender connector
  - `appName` *Optional*: Application name
  - `hostName` *Optional*: Collection server
  - `port` *Optional*: Collection port (default 4562 for log4j2, use 4650 if you are using log4j)
- **analytics.smartLoggerConnector**: Connector that analyzes the execution process and calculates elapsed times and call counts
  - `aggregatedBy` *Optional*: defines the category of sub-processes to aggregate
  - `durationThreshold` (ms) *Optional*: threshold beyond which the call is logged as an error *(default 1000ms)*
