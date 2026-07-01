# Configuration

Application configuration defines all its constituent elements:
- its global configuration
- its various modules composed of:
  - components and plugins
  - definitions

Application configuration can be done in two ways: via YAML files or through a Java API.
Both approaches aim to build a Java `NodeConfig` object, which is used to start the application.

## Features Configuration (Java API)

> Features-based configuration via the Java API is preferred for unit tests or Java applications in general.

To create a Vertigo application, you must create a `NodeConfig` object. To do this, you need the `NodeConfigBuilder` class.

```java
final NodeConfig nodeConfig = NodeConfig.builder()
	.addModule(new CommonsFeatures().build())
	.addModule(new VegaFeatures().withEmbeddedServer(8080).build())
	//-----Declaration of a module named 'Hello' which contains a webservice component.
	.addModule(ModuleConfig.builder("Hello")
		.addComponent(HelloWebServices.class)
		.build())
	.build();
```

?> The configuration example above creates an application providing a REST WebService 'HelloWorld' on port 8080.



The fluent API for configuration creation guides you through the process. Through it, you can configure the following elements:

- **modules**: `addModule` method

  - add a **component**: `addComponent` method

  - add a **plugin**: `addPlugin` method

  - add a **definitionProvider**: `addDefinitionProvider` method

    add an **aspect**: `addAspect` method

- **init**: `addInitializer`

- **appName**: `withAppName` method (use for multi-node applications)

- **endPoint**: `withEndPoint` method (use for multi-node applications)

- **nodeId**: `withNodeId` method (use for multi-node applications)

> When intermediate objects are required (for example `DefinitionProviderConfig`), there is always an associated builder (`DefinitionProviderConfig.builder()`)

To help build modules, each Vertigo module or extension contains a Java class named *ModuleName*__Features__ located at the root of the module's package.
This class simplifies module configuration by abstracting the choice of components and plugins into feature activation/disactivation.

In the example, the **EmbeddedServer** feature (an embedded web server) can be activated by simply calling a method and providing the port.

> You can create as many Features classes as needed. Application business module configuration can follow the same procedure.

Once this NodeConfig object is created, the application can be started:

```java
try (AutoCloseableNode app = new AutoCloseableNode(nodeConfig)) {
	//do whatever you want
}
```



## YAML Configuration

> YAML file configuration is preferred for web application configuration.

YAML file configuration ultimately relies on the Java configuration described above. It allows configuring the various application modules through a text file by activating desired features and parameterizing them according to each project's needs.
_Note: Internally, the YAML file is mapped to the `io.vertigo.core.node.config.yaml.YamlAppConfig` object_

### General Rules

For Vertigo configuration, the important points are:
> - YAML format uses indentation to convey meaning; be careful with it.
> - Indentation with `-` is only used to declare lists. i.e., for active plugin names (first level under `features:` and `featuresConfig:`), for custom plugins (first level under `plugins:`), and initializers (first level under `initializers:`)
> - Indentation alone, without `-`, is used for attributes and maps. Notably Features under `modules:` and parameters in general (plugin, feature, ...)
> - Values can come from external parameters with `${ }`. _Those from `boot` come from limited sources and must be prefixed with `boot.`_
!> - Vertigo supports the special attribute `__flags__:` placed under any element; it conditions the inclusion of the element in the configuration based on activeFlags (application startup parameter: command line, web.xml, etc.). _The flag can be included: `__flags__: ["redis"]` or excluded: `__flags__: ["!redis"]`

Excerpt from [Wikipedia](https://fr.wikipedia.org/wiki/YAML):
- Comments are marked by the hash sign `#` and extend to the end of the line. If the hash appears within a string, it means a literal number.
- A null value is written with the tilde character `~`
- JSON syntax can be included within YAML syntax.
- List items are denoted by a dash `-`, followed by a space, with one item per line.
- Maps are in the form `key: value`, with one pair per line.
- Scalars can be enclosed in double `"`, or single `'`, quotes, knowing that a quote is escaped with a backslash `\`, while an apostrophe is escaped with another apostrophe. They can additionally be represented as an indented block with optional modifiers to preserve `|` or eliminate `>` line breaks.
- Multiple documents in a single file are separated by three dashes `---`; three dots `...` optionally mark the end of a document in a file.
- Repeated nodes are initially marked by an ampersand `&` and then referenced with an asterisk `*`; JSON, a competing language to YAML, is compatible with JavaScript syntax but does not support this notion of reference.
- Indentation, using spaces, shows hierarchy.

### YAML Configuration Structure

The structure of YAML configuration files is as follows:

```yaml
---
node: // optional: required only in a multi-node system
  appName : // the name of the application to which this node belongs
  nodeId : // optional: the ID of the current node. Usually, this is a ${paramName} type evaluated parameter. By default, a UUID is generated. The ID must be unique within the cluster
  endPoint : // optional: specifies the root URL to query the node for its capabilities and configuration
boot:
  params:
    // boot parameters
  plugins:
    // list of plugins identified by their full class name
    - my.boot.Plugin:
        // plugin parameters
        paramName : paramValue
modules:
  // map of modules identified by their manifest classes
  my.module.MyModuleFeatures:
    features:
      // list of enabled features. A feature is identified by its name
      - myFeature:
          // feature parameters
    featuresConfig:
      // list of configurations for enabled features. A configuration is identified by a name composed of the feature name and the chosen technical solution
      - myFeature.mySolution:
        // feature configuration parameters
    plugins:
      // list of additional plugins identified by their full class name
      - my.additional.Plugin:
        // plugin parameters
        paramName : paramValue
initializers:
  // list of initializers identified by their full class name
  - my.module.Initializer:

```

### Sections

A configuration file therefore consists of the following sections:

- **node**: specifies the configuration of a node in a multi-node application
- **boot**: lists all plugins usable by core components (LocaleManager, ResourceManager)
- **modules** listing the various modules present in the application. These modules offer features (Managers) and various ways to implement them (Plugin).
  For each module, you must define:
  - **features**: listing the enabled features
  - **featuresConfig**: specifying the implementation choices
- **initializers**: listing ephemeral initialization components

!> The order of module declaration is important because components are resolved dynamically during application startup (modules can only depend on modules listed *'above'* them). The declaration order within a module does not matter.

#### boot
This section declares the behavior of the system startup phase:
- `boot` the tag declares the start of this configuration. This includes default Managers: LocaleManager, ResourceManager, ParamManager, DaemonManager, AnalyticsManager
- > `params` declares parameters for default Managers
- > `plugins` declares plugins for default Managers

Example:
```yaml
boot:
  params:
    locales: fr_FR
  plugins:
    - io.vertigo.core.plugins.resource.classpath.ClassPathResourceResolverPlugin: {}
    - io.vertigo.core.plugins.resource.url.URLResourceResolverPlugin: {}
    - io.vertigo.core.plugins.param.properties.PropertiesParamPlugin:
        url : file:./src/test/java/com/example/gestionprojet/support/env-test.properties
    - io.vertigo.core.plugins.param.env.EnvParamPlugin: {}
```

#### modules
This section declares the application's modules:

- `modules` the tag declares the start of this configuration. Then declare the Features to apply.
- > `xx.xxx.XxxFeatures` the full path of the class declaring the feature
- > `features` declares optional features (and their parameters) that are actually activated _possible features are declared with `@Feature` on the Features class_
- > `featuresConfig` declares features' plugins (and their parameters) _features must have been activated_
- > `plugins` _(optional)_ it is possible to declare additional complementary plugins not planned in the Feature

Typically, Vertigo Modules are declared first, then application modules.
```
    <Connectors> JavalinFeatures
    CommonsFeatures
    DatabaseFeatures
    DataModelFeatures
    DataStoreFeatures
    DataFactoryFeatures
    AccountFeatures
    VegaFeatures
    <application modules> io.mars.support.SupportFeatures
    <application modules> io.mars.basemanagement.BasemanagementFeatures
```

Example of a module:
```yaml
modules:
  io.vertigo.database.DatabaseFeatures:
    features:
      - sql:
      - migration:
          mode: update
    featuresConfig:
      - sql.datasource:
          __flags__: ["klee"]
          classname: io.vertigo.database.impl.sql.vendor.postgresql.PostgreSqlDataBase
          source: java:/comp/env/jdbc/DataSource
      - sql.datasource:
          __flags__: ["home"]
          classname: io.vertigo.database.impl.sql.vendor.h2.H2DataBase
          source: java:/comp/env/jdbc/DataSourceHome
      - migration.liquibase:
          masterFile: /liquibase/master.xml
```

#### Initializers
This last section allows enriching components after their startup.

Typically, Initializers are declared as:
```yaml
  - io.mars.support.boot.InitialDataInitializer:
  - io.mars.support.boot.I18nResourcesInitializer:
  - io.mars.support.boot.SearchInitializer:
  - io.mars.support.boot.OrchestraInitializer:
```


## Flags

With YAML configuration, you can set *flags* on various configuration elements. These *flags* specify conditions that must be met for a configuration element to be taken into account.

Using a flag, you can enable or disable:

- A complete module
- A feature (**warning**: you must ensure consistency of prerequisites between features)
- A feature configuration
- An additional plugin
- An initializer

At application startup, the list of active flags must be provided via the *boot.activeFlags* parameter, which is a list of strings separated by `;`

Within the YAML configuration, flags are associated with configuration elements through a special parameter *\_\_flags\_\_* which is an array of strings. The **OR** operator applies between the different elements of the flag list. If the special parameter *\_\_flags\_\_* is not set, the configuration element will always be activated.

Flags integrate into the configuration as follows:

```yaml
---
node:
boot:
  params:
  plugins:
    - my.boot.Plugin:
        __flags__ : ["flag1", "flag2"]
        paramName : paramValue
modules:
  my.module.MyModuleFeatures:
    __flags__ : ["flag3"]
    features:
      - myFeature:
    featuresConfig:
      - myFeature.mySolution1:
          __flags__ : ["flag1"]
      - myFeature.mySolution2:
          __flags__ : ["flag2"]
    plugins:
      - my.additional.Plugin:
        __flags__ : ["flag4"]
        paramName : paramValue
initializers:
  - my.module.Initializer:
    __flags__ : ["flag5"]

```

In the above example:

- The plugin *my.boot.Plugin* is activated when either *flag1* **or** *flag2* is set
- The module MyModule whose Manifest class is *my.module.MyModuleFeatures* is activated when *flag3* is set
- The feature *myFeature* uses *mySolution1* when *flag1* is set
- The feature *myFeature* uses *mySolution2* when *flag2* is set
- The additional plugin *my.additional.Plugin* is added when *flag4* is set
- The initializer *my.module.Initializer* is executed at application startup when *flag5* is set



The configuration can then be changed through a parameter file.

> XML file configuration is also described by an XSD file available [here](https://github.com/vertigo-io/vertigo/blob/master/vertigo-core/src/main/java/io/vertigo/app/config/xml/vertigo_1_0.xsd)

# Usage

?> This section describes legacy Servlet/Tomcat configuration. With standalone Javalin, these configurations are no longer necessary.

For web applications, a *listener* must be configured on the servlet.

```xml
<listener>
	<listener-class>io.vertigo.vega.impl.webservice.servlet.AppServletContextListener</listener-class>
</listener>
```
This listener creates the Vertigo application. It reads the application configuration through configuration files specified via the *boot.applicationConfiguration* servlet parameter.

```xml
<context-param>
	<param-name>boot.applicationConfiguration</param-name>
	<param-value>/META-INF/configuration.yaml</param-value>
</context-param>
```
Multiple files can be specified by separating them with `;`. Files are read sequentially to create a single application.

Active flags can be provided via the *boot.activeFlags* servlet parameter.

```xml
<context-param>
	<param-name>boot.activeFlags</param-name>
	<param-value>flag1;flag3</param-value>
</context-param>
```

For environments that require it, active flags can be passed via an environment variable: `VERTIGO_BOOT_ACTIVE_FLAGS`.

Example:
```xml
VERTIGO_BOOT_ACTIVE_FLAGS=devPages;redis;kvSpeedb;searchES;analytics;cspReportWs
```

## Example

Here is a configuration example of Vertigo's white application: [configuration.yaml](https://github.com/vertigo-io/vertigo-mars/blob/master/src/main/resources/mars.yaml) which implements a large number of modules and extensions.

```yaml
---
boot:
  params:
    locales: fr_FR, en_US
  plugins:
    - io.vertigo.core.plugins.resource.classpath.ClassPathResourceResolverPlugin: {}
    - io.vertigo.core.plugins.resource.local.LocalResourceResolverPlugin: {}
    - io.vertigo.core.plugins.resource.url.URLResourceResolverPlugin: {}
    - io.vertigo.core.plugins.param.properties.PropertiesParamPlugin:
        __flags__: ["ethereum"]
        url: "${boot.walletParamsUrl}"
    - io.vertigo.core.plugins.param.properties.PropertiesParamPlugin:
        __flags__: ["klee"]
        url: "${boot.apiKeysUrl}"
    - io.vertigo.core.plugins.param.properties.PropertiesParamPlugin:
        __flags__: ["home"]
        url: "${user.home}/mars/marsconf/marsApiKeys.properties"
    - io.vertigo.vega.plugins.webservice.servlet.WebAppContextParamPlugin: {}
    - io.vertigo.core.plugins.analytics.log.SocketLoggerAnalyticsConnectorPlugin:
        __flags__: ["klee"]
        appName: mars-analytics
        hostName: ${boot.analyticsHost}
modules:
  io.vertigo.connectors.redis.RedisFeatures:
    __flags__: ["klee"]
    features:
      - jedis:
          host: ${redisHost}
          port: 6379
          database: 0
  io.vertigo.connectors.influxdb.InfluxDbFeatures:
    __flags__: ["klee"]
    features:
      - influxdb:
          host: ${influxdbHost}
          user: user
          password: password
  io.vertigo.connectors.elasticsearch.ElasticSearchFeatures:
    features:
      - embeddedServer:
          __flags__: ["home"]
          home: search/
      - restHL:
          __flags__: ["home"]
          servers.names: "localhost:9200"
      - restHL:
          __flags__: ["klee"]
          servers.names: ${esHost}
  io.vertigo.connectors.mqtt.MqttFeatures:
    __flags__: ["klee"]
    features:
      - mosquitto:
          name: Subscriber
          host: ${mosquittoHost}
      - mosquitto:
          name: Publisher
          host: ${mosquittoHost}
  io.vertigo.connectors.keycloak.KeycloakFeatures:
    __flags__: ["keycloak"]
    features:
      - deployment:
          configUrl: ${keycloakConfigUrl}
  io.vertigo.connectors.javalin.JavalinFeatures:
    features:
      - standalone:
  io.vertigo.commons.CommonsFeatures:
    features:
      - script:
      - command:
    featuresConfig:
      - script.janino:
  io.vertigo.database.DatabaseFeatures:
    features:
      - sql:
      - timeseries:
      - migration:
          mode: update
    featuresConfig:
      - timeseries.influxdb:
          __flags__: ["klee"]
          dbNames: mars-test;*
      - timeseries.fake:
          __flags__: ["home"]
      - sql.datasource:
          __flags__: ["klee"]
          classname: io.vertigo.database.impl.sql.vendor.postgresql.PostgreSqlDataBase
          source: java:/comp/env/jdbc/DataSource
      - sql.datasource:
          __flags__: ["home"]
          classname: io.vertigo.database.impl.sql.vendor.h2.H2DataBase
          source: java:/comp/env/jdbc/DataSourceHome
      - migration.liquibase:
          masterFile: /liquibase/master.xml
  io.vertigo.datamodel.DataModelFeatures:
  io.vertigo.datastore.DataStoreFeatures:
    features:
      - entitystore:
      - filestore:
      - kvStore:
      - cache:
    featuresConfig:
      - entitystore.sql:
      - entitystore.sql:
          dataSpace: orchestra
      - filestore.db:
          __flags__: ["klee"]
          storeDtName: DtMediaFileInfo
          fileInfoClass: io.mars.support.fileinfo.FileInfoStd
      - filestore.filesystem:
          __flags__: ["home"]
          storeDtName: DtMediaFileInfo
          path: ${user.home}/marsFiles/
          fileInfoClass: io.mars.support.fileinfo.FileInfoStd
      - filestore.fullFilesystem:
          name: temp
          path: ${java.io.tmpdir}/marsFiles/
          purgeDelayMinutes: 30
          fileInfoClass: io.mars.support.fileinfo.FileInfoTmp
      - kvStore.delayedMemory:
          collections: protected-value
          timeToLiveSeconds: 3600
      - kvStore.berkeley:
          collections: VViewContext;TTL=43200
          dbFilePath: ${java.io.tmpdir}/vertigo-ui/MarsVViewContext
      - cache.memory:
  io.vertigo.datafactory.DataFactoryFeatures:
    features:
      - search:
    featuresConfig:
      - collections.luceneIndex:
      - search.elasticsearch.restHL:
          envIndexPrefix: mars
          rowsPerQuery: 50
          config.file: search/elasticsearch.yml
  io.vertigo.account.AccountFeatures:
    features:
      - security:
          userSessionClassName: io.mars.support.MarsUserSession
      - account:
      - authentication:
      - authorization:
    featuresConfig:
      - account.store.store:
          userIdentityEntity: DtPerson
          groupIdentityEntity: DtGroups
          userAuthField: email
          photoFileInfo: FiFileInfoStd
          userToAccountMapping: 'id:personId, displayName:lastName, email:email, authToken:email, photo: picturefileId'
          groupToGroupAccountMapping: 'id:groupId, displayName:name'
      - authentication.store:
          __flags__: ["keycloak"]
          userCredentialEntity: DtPerson
          userLoginField: email
          userPasswordField: notused
          userTokenIdField: email
      - authentication.text:
          __flags__: ["!keycloak"]
          filePath: /io/mars/support/userAccounts.txt
  io.vertigo.vega.VegaFeatures:
    features:
        - webservices:
    featuresConfig:
        - webservices.javalin:
            apiPrefix: /api
        - webservices.token:
            tokens: mars-api
        - webservices.rateLimiting:
        - webservices.security:
        - webservices.swagger:
  io.vertigo.orchestra.OrchestraFeatures:
    featuresConfig:
      - orchestra.database:
          nodeName: MARS1
          daemonPeriodSeconds: 30
          workersCount: 10
          forecastDurationSeconds: 60
      - orchestra.webapi:
  io.vertigo.social.SocialFeatures:
    features:
      - notifications:
      - comments:
      - handles:
      - webapi:
    featuresConfig:
      - notifications.redis:
          __flags__: ["klee"]
      - notifications.memory:
          __flags__: ["home"]
      - comments.redis:
          __flags__: ["klee"]
      - comments.memory:
          __flags__: ["home"]
      - handles.redis:
          __flags__: ["klee"]
      - handles.memory:
          __flags__: ["home"]
  io.vertigo.geo.GeoFeatures:
    features:
      - geosearch:
    featuresConfig:
      - geosearch.es:
          envIndexPrefix: mars
  io.vertigo.dashboard.DashboardFeatures:
    features:
      - analytics:
          appName: mars-analytics
  io.vertigo.audit.AuditFeatures:
    features:
      - ledger:
    featuresConfig:
      - ledger.ethereum:
          __flags__: ["ethereum"]
          urlRpcEthNode: ${ledgerHost}
          myAccountName: ${myAccountName}
          myPublicAddr: ${myPublicAddr}
          defaultDestAccountName: ${myAccountName}
          defaultDestPublicAddr: ${myPublicAddr}
          walletPassword: ${walletPassword}
          walletPath: ${walletPath}
      - ledger.fake:
          __flags__: ["!ethereum"]
  io.vertigo.connectors.ifttt.IftttFeatures:
    features:
      - ifttt:
          baseUrl: ${iftttApiUrl}
          apiKey: ${iftttApiKey}
  io.mars.support.SupportFeatures:
  io.mars.catalog.CatalogFeatures:
  io.mars.hr.HrFeatures:
  io.mars.basemanagement.BasemanagementFeatures:
    features:
      - mqtt:
          __flags__: ["klee"]
  io.mars.maintenance.MaintenanceFeatures:
  io.mars.opendata.OpendataFeatures:
  io.mars.job.JobFeatures:
  io.mars.datageneration.DataGenerationFeatures:
    features:
      - datageneration:
          initialEquipmentUnits: 1500
  io.mars.home.HomeFeatures:
  io.mars.command.CommandFeatures:
initializers:
  - io.mars.support.boot.InitialDataInitializer:
      __flags__: ["initialData"]
  - io.mars.support.boot.I18nResourcesInitializer:
  - io.mars.support.boot.SearchInitializer:
  - io.mars.support.boot.OrchestraInitializer:

```
---

## Focus on YAML Format

A YAML (Yet Another Markup Language) file is a human-readable format, widely used for configuration and data exchange.
Working with YAML requires particular attention to readability, indentation, and consistency. Regular validation and clear structuring practices will help you avoid frustrating and hard-to-diagnose errors.
Here are some principles, best practices, common pitfalls, and tips for working effectively with YAML:

### **Basic Principles**
1. **Readable format**: YAML is designed to be easy to read. Use explicit names for keys and avoid cluttering your files with complex configurations if they can be simplified.
2. **Strict indentation**: YAML relies on indentation to structure data. Use **spaces (2 or 4)** for indentation and **avoid tabs**, which are not recognized.
3. **No ambiguity in types**: YAML automatically detects types (strings, integers, booleans, etc.), but this can cause surprises. Use quotes for ambiguous strings (like `"true"`, `"123"`).

### **Important Syntaxes**
#### **Keys and values**
```yaml
simple_key: value
name: "Jean Dupont"
age: 30
active: true
```

#### **Nested structures**
- **Objects (map)**:
```yaml
user:
  name: "Alice"
  role: "Admin"
```

- **Lists**:
```yaml
animals:
  - cat
  - dog
  - bird
```

- **List of objects**:
```yaml
people:
  - name: "Alice"
    age: 25
  - name: "Bob"
    age: 30
```

### **Practical Tips**
1. **Validate your YAML files**: Use online validators or tools like `yamllint` to detect indentation or syntax errors.
2. **Use comments**: Add comments to explain complex sections.
   ```yaml
   # This file configures the production system
   environment: production
   ```
3. **Respect case sensitivity**: YAML is case-sensitive (`name` and `Name` are different).
4. **Avoid duplicate keys**: Each key at a given level must be unique. Otherwise, only the last one will be taken into account.
   ```yaml
   # Common mistake
   key: value1
   key: value2  # value1 will be ignored
   ```


### **Common Pitfalls**
1. **Bad indentation**:
   - Wrong:
     ```yaml
     user:
       name: "Alice"
       age: 25
         role: "Admin"  # Too many spaces
       ^^
     ```
   - Correct:
     ```yaml
     user:
       name: "Alice"
       age: 25
       role: "Admin"
     ```

3. **Incorrect list usage**:
   - Wrong:
     ```yaml
     animals:
       - "cat"
       - dog
         - bird  # Wrong indentation level
       ^^
     ```

   - Correct:
     ```yaml
     animals:
       - "cat"
       - "dog"
       - "bird"
     ```

4. **Special characters: use quotes**:
   - Example:
     ```yaml
     password: "1234$abcd"
     ```

5. **Advanced types (to avoid)**:
   - Certain types like timestamps (`2024-11-28`) may be interpreted as dates. Enclose them in quotes if they should be text.

