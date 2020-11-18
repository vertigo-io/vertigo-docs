# Configuration

La configuration d'une application permet de définir l'ensemble de ses éléments constitutifs :
- sa configuration globale
- ses différents modules constitués de :
  - composants et plugins
  - définitions 

La configuration de l'application peut s'effectuer selon deux modalités : sous forme de fichiers YAML ou via une API Java
Ces deux modalités ont pour but de construire un objet Java `NodeConfig` qui est utilisé afin de démarrer l'application.

## Configuration par features (API Java)

> La configuration par features via l'API Java est privilégiée pour les tests unitaires ou les applications Java en général.

Afin de créer une application Vertigo, il est nécessaire de créer un objet `NodeConfig`. Pour y parvenir, l'utilisation de la classe `NodeConfigBuilder` est nécessaire.

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

?> L'exemple de configuration ci-dessus permet la création d'une application fournissant un WebService REST 'HelloWorld' sur le port 8080.



L'API fluent de création de la configuration permet d'être guidé dans sa création. Par ce biais, il est possible de configurer les éléments suivants :

- **boot** : méthode `beginBoot` , `endBoot`

- **modules** : méthode `addModule`

  - ajout d'un **composant** :  méthode `addComponent`

  - ajout d'un **plugin** : méthode `addPlugin`

  - ajout d'un **definitionProvider** : méthode `addDefinitionProvider` 

    ajout d'un **aspect** : méthode `addAspect`

- **init** : `addInitializer`

- **appName** : méthode `withAppName` (à utiliser en cas d'application multi-noeud)

- **endPoint** : méthode `withEndPoint` (à utiliser en cas d'application multi-noeud)

- **nodeId** : méthode `withNodeId` (à utiliser en cas d'application multi-noeud)

> Lorsque des objets intermédiaires sont requis (par exemple `DefinitionProviderConfig`) il existe toujours un builder associé (`DefinitionProviderConfig.builder()`)

Afin d'aider à la construction des modules, chaque module ou extension de Vertigo contient une classe Java nommée *NomDuModule*__Features__ située à la racine du package dudit module.
Cette classe permet une configuration plus aisée d'un module en abstrayant le choix des composants et des plugins par une activation / desactivation de fonctionalités.

Dans l'exemple, il est possible d'activer la fonctionalité **EmbeddedServer** (donc un serveur web embarqué) uniquement en appelant une méthode et en fournissant le port.

> Il est possible de créer autant de classes de Features que souhaité. La configuration des modules métier des applications peut être réalisée selon la même procédure.

Une fois cet objet AppConfig créé, il est possible de démarrer l'application : 

```java
try (AutoCloseableApp app = new AutoCloseableApp(nodeConfig)) {
	//do whatever you want
}
```



## Configuration YAML

> La configuration sous forme de fichiers YAML est privilégiée pour la configuration d'applications web.

La configuration par fichier YAML s'appuie *in fine* sur la configuration Java présentée ci-dessus. Elle permet via un fichier texte de configurer les différents modules de l'application en activant les fonctionnalités souhaitées et en les paramétrant selon les besoins de chaque projet.

La structure des fichiers YAML de configuration est la suivante : 

```yaml
---
node: // optionel : uniquement requis dans un système consitué de plusieurs noeuds
	appName : // le nom de l'application dont fait partie le noeud
	nodeId : // optionnel : l'id du noeud courant. En général, il s'agit d'un paramètre évalué de type ${nomDuParamètre}. Par défaut, un UUID est généré. L'id doit être unique au sein du cluster
	endPoint : // optionnel : spécifie l'url racine permettant d'interroger le noeud sur ses capacités et sa configuration
boot:
  params:
 	// paramètres du boot
  plugins:
    // liste de plugins identifiés par leur nom complet de classe
    - my.boot.Plugin: 
    	// paramètres d'un plugin
    	paramName : paramValue
modules:
  // map des modules identifiés par leurs classes de manifest
  my.module.MyModuleFeatures:
    features:
      // liste des fonctionalités activées. Une fonctionnalité est identifiée par son nom
      - myFeature:
      	// paramètres d'une fonctionnalité
    featuresConfig:
    	// liste des configurations des fonctionalités activées. Une configuration est identifiée par son nom composé du nom de la fonctionnalité et de la solution technique retenue
      - myFeature.mySolution:
        // paramètres d'une configuration de fonctionnalités
    plugins:
      // liste de plugins additionnels identifiés par leur nom complet de classe
      - my.additional.Plugin: 
        // paramètres d'un plugin
        paramName : paramValue
initializers:
  // liste d'initializers identifiés par leur nom complet de classe 
  - my.module.Initializer:

```



Un fichier de configuration est donc constitué des sections suivantes :

- **node** : permet de spécifier la configuration d'un nœud en cas d'application multi-nœuds
- **boot** : permet de lister l'ensemble des plugins utilisables par les composants du noyau (LocaleManager, ResourceManager)
- **modules** listant les différents modules présents dans l'application. Ces modules offrent des fonctionnalités (Managers) et différentes manières de les mettre en œuvre (Plugin).
  Il faut ainsi définir pour chaque module :
  - **features** : indiquant la liste des fonctionnalités activées
  - **featuresConfig** : indiquant les choix de mise en œuvre
- **initializers** : listant des composants ephémères d'initialisation

!> L'ordre de déclaration des modules est important car les composants sont résolus dynamiquement au cours du démarrage de l'application. L'ordre de déclaration dans un module n'a en revanche pas d'importance.



### Flags

Avec la configuration YAML, il est possible de positionner des *flags* sur les différents éléments de la configuration. Ces *flags* permettent de spécifier les conditions à remplir pour qu'un élément de configuration soit pris en compte.

A l'aide d'un flag il est possible d'activer ou de désactiver :  

- Un module complet 
- Une fonctionnalité (**attention** : il faut dans ce cas s'assurer de la cohérence des pré-requis entre fonctionnalités)
- Un paramétrage de fonctionnalité
- Un plugin additionnel
- Un initializer

Au démarrage de l'application, la liste des flags actifs doit être fournie via l'intermédiaire du paramètre *boot.activeFlags*, qui est une liste de chaînes de caractères séparées par des `;`

Au sein de la configuration YAML, les flags sont associés aux éléments de configuration via intermédiaire d'un paramètre spécial *\_\_flags\_\_* qui est un tableau de chaines de caractères. L'opérateur **ou** s'applique entre les différents éléments de la liste des flags. Si le paramètre spécial *\_\_flags\_\_* n'est pas positionné, l'élément de configuration sera toujours activé. 

Les flags s'intègrent comme suit dans la configuration et permettent par exemple

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

Dans l'exemple ci-dessus :

- Le plugin *my.boot.Plugin* est activé lorsque le *flag1* **ou** le *flag2* est positionné
- Le module MyModule dont la classe de Manifest est *my.module.MyModuleFeatures* est activé lorsque le *flag3* est positionné
- La fonctionnalité *myFeature* utilise la solution *mySolution1* lorsque le *flag1* est positionné
- La fonctionnalité *myFeature* utilise la solution *mySolution2* lorsque le *flag2* est positionné
- Le plugin additionnel *my.additional.Plugin* est ajouté lorsque le *flag4* est positionné
- L'initializer *my.module.Initializer* est exécuté au démarrage de l'application lorsque le *flag5* est positionné



Il est alors possible de changer la configuration par l'intermédiaire d'un fichier de paramètrage.

> La configuration par fichier xml est également décrite par un fichier XSD disponible [ici](https://github.com/KleeGroup/vertigo/blob/master/vertigo-core/src/main/java/io/vertigo/app/config/xml/vertigo_1_0.xsd)

### Utilisation

Dans le cadre des applications Web, un *listener* doit être paramétré sur la servlet.

```xml
<listener>
	<listener-class>io.vertigo.vega.impl.webservice.servlet.AppServletContextListener</listener-class>
</listener>
```
Ce listener permet la création de l'application Vertigo. Ce dernier lit la configuration de l'application par l'intermédiaire des fichiers de configuration spécifiés à l'aide du paramètre *boot.applicationConfiguration*  de la servlet.

```xml
<context-param>
	<param-name>boot.applicationConfiguration</param-name>
	<param-value>/META-INF/configuration.yaml</param-value>
</context-param>
```
Il est possible de spécifier plusieurs fichiers en les séparant par des `;`. Les fichiers sont lus séquentiellement pour créer une unique application.

Les flags actifs peuvent être fournis à l'aide du paramètre *boot.activeFlags*  de la servlet.

```xml
<context-param>
	<param-name>boot.activeFlags</param-name>
	<param-value>flag1;flag3</param-value>
</context-param>
```



### Exemple

Voici un exemple de configuration de l'application blanche de Vertigo : [configuration.yaml](https://github.com/KleeGroup/vertigo-university/blob/develop/mars/src/main/resources/boot/mars.yaml) qui met en œuvre un grand nombre de modules et extensions.

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
        url: ${user.home}\mars\marsconf\marsApiKeys.properties
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

