# Core

Vertigo-core is the mini framework that allows a Vertigo application to function. It is very light, very robust but has everything of a large one, its design being the fruit of several decades of efforts.

Its missions for a Vertigo application are:

- **Configure**: describes what it does and how it does it
- **Run**: starts the application and stops it
- **Monitor**: collects statistics to assess its state at any time

To do this, an application consists of two distinct spaces:

- **ComponentSpace**: the space of components, which corresponds to treatments (pure and stateless mathematical functions)
- **DefinitionSpace**: the space of definitions, which corresponds to immutable information that describes the elements manipulated by the application.

The startup cycle therefore aims to fill these two spaces. Once the application is started, these two spaces are locked (they can no longer be modified), the state of the application can no longer be altered. The result is a robust application, whose behavior is reproducible, without side effects, in a word **reliable**.

## Configuration

In the concept of configuration, we have chosen to differentiate the **structural** configuration of an application (what it does) from its settings (which influence how it operates). Thus, the configuration of a Vertigo application is done via two very different means:

- the configuration: which lists the modules of the application and for each module the activated features (according to two modalities: YAML file or Java API)
- the settings: which provide values of named parameters used by the components. (the provision of parameter values can be done by as many modalities as necessary via dedicated plugins)

The configuration of the application is therefore by nature immutable, which is not the case for parameters that can have their own strategy.

An application is made up of modules, each bringing both its **definitions** and its **components**.

## Run

Starting from the configuration and settings of an application, it is then possible to create an execution node (Node). The startup cycle is as follows:

1. Creation of all components: module by module and using an inversion of control mechanism to resolve dependencies between components
2. Locking of the component space (no new component can be registered)
3. Registration of all definitions: module by module via the DefinitionProvider, the components themselves can be DefinitionProvider
4. Locking of the definition space (no new definition can be registered)
5. Starting of all components: call of the start() method of the activatable components, they then have access to the definition space 
(5.bis Creation of ephemeral *Initializer* components for certain needs)
6. Execution of pre-activation functions registered during the startup of the components.
7. At the end of this startup cycle, the *Node* is ready, and all of its functionalities are usable via its components.

When stopping the application node, all components are stopped in the reverse order of their startup.

On the other hand, Vertigo-Core provides an execution environment dedicated to daemons, in the sense of a recurring technical task, through the `DaemonManager`. To register a new daemon, simply create a `DaemonDefinition`. A simplified way is to add the `@DaemonScheduled` annotation on a public method of a component registered in the `ComponentSpace`.


## Monitor

Once an application is started, it is important to monitor its activity and performance. A native analytics module is present in Vertigo to allow fine tracking of the treatments that are performed. It allows to follow three types of indicators:

- **HealthStatus**: Allows to indicate a health status (red, orange, green) for a specific function
- **AProcess**: Allows to trace complete executions within the application by passing through different checkpoints. This allows in particular to count the nature and duration of the different processes.
- **Metric**: Allows to collect metrics at regular time intervals to follow the evolution over time of a characteristic of an application.

Probes are placed at strategic locations of the treatments in the different Vertigo extensions. Each additional project/module can add new checkpoints for each type of indicator.

## Plugin API

- **analytics.socketLoggerConnector**: Analytics data is sent using the log4j/log4j2 SocketAppender connector
  - `appName` *Optional*: Application name
  - `hostName` *Optional*: Collection server
  - `port` *Optional*: Collection port (default 4562 for log4j2, set to 4650 if you are using log4j)
- **analytics.smartLoggerConnector**: Connector that analyzes the execution process and calculates the elapsed times and the number of calls
  - `aggregatedBy` *Optional*: Defines the category of sub-processes to aggregate
  - `durationThreshold` (ms) *Optional*: Threshold beyond which the call is logged as an error *(default 1000ms)*