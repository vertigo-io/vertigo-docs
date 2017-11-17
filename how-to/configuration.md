# Configuration

La configuration d'une application permet de définir l'ensemble de ses éléments constitutifs :
- sa configuration globale
- ses différents modules constitués de :
  - composants et plugins
  - définitions 

La configuration de l'application peut s'effectuer selon deux modalités : sous forme de fichiers XML ou via une API Java
Ces deux modalités ont pour but de construire un objet Java `AppConfig`.

## Configuration XML

> La configuration sous forme de fichiers XML est privilégiée pour la configuration d'applications webs.

La structure des fichiers XML de configuration est la suivante : 

```xml
<?xml version =	'1.0' encoding = 'UTF-8'?>
<config>
  <boot>
    <plugin class="" />
    ...	
  </boot>
  <module name="">
    <component class="" >
      <plugin class="" />
      ...
    </component>
    <definitions>
          <provider class="" />
          ...
    </definitions>
  </module>
  ...
  <init>
      <initializer class=""/>
  </init>
</config>
```



Un fichier de configuration est donc consitué des sections suivantes :

- **app** : permet de spécifier la configuration d'un noeud en cas d'application multi-noeuds
- **boot** : permet de lister l'ensemble des plugins utilisables par les composants du noyaux (LocaleManager, ResourceManager)
- une **liste de modules** listant chacun :
  - le définitions
  - les composants 
  - les plugins
  - les aspects
- **init** : listant des composants ephémères d'initialisation

!> L'ordre de déclaration des modules est important car les composants sont resolus dynamiquement au cours du démarrage de l'application. L'ordre de déclaration dans un module n'a en revanche pas d'importance.

### Api

*`boot`*

| attribut | obligatoire | description                              |
| :------: | :---------: | ---------------------------------------- |
|  locale  |     non     | spécifie les différentes locales prisent en charge par l'application |

*`module`*

| attribut | obligatoire | description      |
| :------: | :---------: | ---------------- |
|   name   |     oui     | le nom du module |

*`composant`*

| attribut | obligatoire | description                              |
| :------: | :---------: | ---------------------------------------- |
|   api    |     non     | le nom du composant utilisé pour l'injection de dépendance |
|  class   |     oui     | le nom complet de la classe d'implémentation du composant |

*`plugin`*

| attribut | obligatoire | description                              |
| :------: | :---------: | ---------------------------------------- |
|  class   |     oui     | le nom complet de la classe d'implémentation du composant |

*`aspect`*

| attribut | obligatoire | description                              |
| :------: | :---------: | ---------------------------------------- |
|  class   |     oui     | le nom complet de la classe d'implémentation de l'aspect |

*`definitionProvider`*

| attribut | obligatoire | description                              |
| :------: | :---------: | ---------------------------------------- |
|  class   |     oui     | le nom complet de la classe fournissant les définitions |

*`param`*

| attribut | obligatoire | description            |
| :------: | :---------: | ---------------------- |
|   name   |     oui     | le nom du paramètre    |
|  value   |     oui     | la valeur du paramètre |

En cas de besoin la valeurs des paramètres peut être modifiée par paramètrage à l'aide de la syntaxe suivante `${}`. Il est donc possible d'avoir la configuration suivante permettant une modification par l'intermédiaire d'une fichier de paramétrage.

```xml
<plugin class="io.vertigo.core.plugins.param.xml.XmlParamPlugin">
	<param name="url" value="${boot.configXmlInterne}" />
</plugin>
```
Il est alors possible de changer le paramètre par l'intermédiaire d'un fichier de paramètrage.

> La configuration par fichier xml est également décrite par un fichier XSD disponible [ici](https://github.com/KleeGroup/vertigo/blob/master/vertigo-core/src/main/java/io/vertigo/app/config/xml/vertigo_1_0.xsd)


### Utilisation

Ces fichiers de configurations sont spécifiés à l'aide du paramètre *boot.applicationConfiguration*  de la servlet

```xml
<context-param>
	<param-name>boot.applicationConfiguration</param-name>
	<param-value>/META-INF/managers.xml;/META-INF/demo-services.xml</param-value>
</context-param>
```
Il est possible de spécifier plusieurs fichiers en les séparant par des `;`. Les fichiers sont lus séquentiellement. 

### Exemple

Voici un exemple de configuration des composants Vertigo. [managers.xml](https://github.com/KleeGroup/vertigo-university/blob/master/vertigo-demo-struts2/src/main/resources/META-INF/managers.xml)

```xml
<?xml version =	'1.0' encoding = 'ISO-8859-1'?>
<!-- Utilisation -->
<config>
	<boot locales="fr_FR">
		<plugin class="io.vertigo.core.plugins.resource.classpath.ClassPathResourceResolverPlugin" />
		<plugin class="io.vertigo.vega.plugins.webservice.servlet.ServletResourceResolverPlugin" />
		<plugin class="io.vertigo.core.plugins.param.xml.XmlParamPlugin">
			<param name="url" value="${boot.configXmlInterne}" />
		</plugin>
		<plugin class="io.vertigo.vega.plugins.webservice.servlet.WebAppContextParamPlugin" />
	</boot>
	
	<module name="commons">
		<component api="ScriptManager" class="io.vertigo.commons.impl.script.ScriptManagerImpl">
			<plugin class="io.vertigo.commons.plugins.script.janino.JaninoExpressionEvaluatorPlugin" />
		</component>
		<component api="AnalyticsManager" class="io.vertigo.commons.impl.analytics.AnalyticsManagerImpl" />
		<component api="CodecManager" class="io.vertigo.commons.impl.codec.CodecManagerImpl" />
		<component api="CacheManager" class="io.vertigo.commons.impl.cache.CacheManagerImpl">
			<plugin class="io.vertigo.commons.plugins.cache.memory.MemoryCachePlugin">
			</plugin>
		</component>
		<component api="VTransactionManager" class="io.vertigo.commons.impl.transaction.VTransactionManagerImpl" />
		<component api="EventBusManager" class="io.vertigo.commons.impl.eventbus.EventBusManagerImpl" />
		<component api="DaemonManager" class="io.vertigo.commons.impl.daemon.DaemonManagerImpl" />
	</module>
	<module name="database">
		<component api="SqlDataBaseManager" class="io.vertigo.database.impl.sql.SqlDataBaseManagerImpl">
			<plugin class="io.vertigo.database.plugins.sql.connection.datasource.DataSourceConnectionProviderPlugin">
				<param name="source" value="java:/comp/env/jdbc/DataSource" />
				<param name="classname" value="io.vertigo.database.impl.sql.vendor.h2.H2DataBase" />
			</plugin>
		</component>
	</module>
	<module name="dynamo">
		<component api="TaskManager" class="io.vertigo.dynamo.impl.task.TaskManagerImpl" />
		<component api="KVStoreManager" class="io.vertigo.dynamo.impl.kvstore.KVStoreManagerImpl">
			<plugin class="io.vertigo.dynamo.plugins.kvstore.berkeley.BerkeleyKVStorePlugin">
				<param name="collections" value="VActionContext;TTL=43200" /> <!-- 12h -->
				<param name="dbFilePath" value="${java.io.tmpdir}/ehcache/DemoVActionContext" />
			</plugin>
		</component>
		<component api="StoreManager" class="io.vertigo.dynamo.impl.store.StoreManagerImpl">
			<plugin class="io.vertigo.dynamo.plugins.store.datastore.sql.SqlDataStorePlugin">
				<param name="sequencePrefix" value="SEQ_" />
			</plugin>
			<plugin class="io.vertigo.demo.services.util.TutoMasterDataStoreStatic"/>
			<plugin class="io.vertigo.demo.services.util.CommuneStorePlugin"/>
			
			<plugin class="io.vertigo.dynamo.plugins.store.filestore.db.DbFileStorePlugin">
				<param name="storeDtName" value="DT_KX_FILE_INFO" />
			</plugin>
		</component>
		<component api="FileManager" class="io.vertigo.dynamo.impl.file.FileManagerImpl" /> 
		<component api="CollectionsManager" class="io.vertigo.dynamo.impl.collections.CollectionsManagerImpl">
			<plugin class="io.vertigo.dynamo.plugins.collections.lucene.LuceneIndexPlugin" />
		</component>
	</module>
	<module name="account">
		<component api="VSecurityManager" class="io.vertigo.persona.impl.security.VSecurityManagerImpl">
			<param name="userSessionClassName" value="io.vertigo.demo.services.DemoUserSession" />
		</component>
	</module>
	<module name="struts2">
	</module>
	<module name="orchestra">
		<definitions>
			<provider class="io.vertigo.dynamo.plugins.environment.DynamoDefinitionProvider" >
				<resource type ="kpr" path="io/vertigo/orchestra/execution.kpr"/>
			    <resource type="classes" path="io.vertigo.orchestra.domain.DtDefinitions" />  
		    </provider>
		</definitions>   
		<component api="OrchestraDefinitionManager" class="io.vertigo.orchestra.impl.definitions.OrchestraDefinitionManagerImpl">
			<plugin class="io.vertigo.orchestra.plugins.definitions.memory.MemoryProcessDefinitionStorePlugin"/>
		</component>
		<component api="OrchestraServices" class="io.vertigo.orchestra.impl.services.OrchestraServicesImpl">
			<plugin class="io.vertigo.orchestra.plugins.services.schedule.memory.MemoryProcessSchedulerPlugin"/>
			<plugin class="io.vertigo.orchestra.plugins.services.execution.memory.MemoryProcessExecutorPlugin" >
				<param name="workersCount" value="5" />
			</plugin>
		</component>
	</module>
</config>
```

Voici un exemple de configuration des composants d'une application. [demo-services.xml](https://github.com/KleeGroup/vertigo-university/blob/master/vertigo-demo-struts2/src/main/resources/META-INF/demo-services.xml)

```xml
<?xml version =	'1.0' encoding = 'ISO-8859-1'?>
<!-- Utilisation -->
<config>
	<!-- Aspects declaration -->
	<module name="aspects" >
		<aspect class="io.vertigo.commons.impl.transaction.VTransactionAspect"/>
	</module>
	
	<!-- Demo App-->
	<module name="Demo">
		<definitions>
			<provider class="io.vertigo.dynamo.plugins.environment.DynamoDefinitionProvider" >
				<param name='encoding' value='utf8' />
				<resource type="classes" path="io.vertigo.demo.domain.DtDefinitions" />
				<resource type="kpr" path="io/vertigo/demo/execution.kpr" />
			</provider>
			<provider class="io.vertigo.persona.plugins.security.loaders.SecurityDefinitionProvider" >
				<resource type="security" path="/META-INF/demo-auth-config.xml" />
			</provider>
		</definitions>
		<!-- dao -->
		<component class="io.vertigo.demo.dao.administration.utilisateur.LoginDAO" />
	    <component class="io.vertigo.demo.dao.administration.utilisateur.RoleDAO" />
	    <component class="io.vertigo.demo.dao.administration.utilisateur.UtilisateurDAO" />
	    <component class="io.vertigo.demo.dao.produit.ProduitDAO" />
	    <!-- services -->
	    <component api="UtilisateurServices" class="io.vertigo.demo.services.administration.utilisateur.UtilisateurServicesImpl" />
	    <component api="ProduitServices" class="io.vertigo.demo.services.produit.ProduitServicesImpl" />
	    <component api="ReferentielServices" class="io.vertigo.demo.services.referentiel.ReferentielServicesImpl" />
	</module>
	<init>
		<initializer class="io.vertigo.demo.boot.initializer.LocaleManagerInitializer"/>
		<initializer class="io.vertigo.demo.boot.initializer.PersistenceManagerInitializer"/>
		<initializer class="io.vertigo.demo.boot.initializer.JobManagerInitializer"/>
		<initializer class="io.vertigo.demo.boot.initializer.SecurityManagerInitializer"/>
	</init>
 </config>
```


## Configuration par features (API Java)

> La configuration par features via l'API Java est privilégiée pour les tests unitaires ou les applications Java en général.

Afin de créer une application Vertigo il est nécessaire de créer un objet `AppConfig`. Pour y parvenir l'utilisation de la classe `AppConfigBuilder` est nécessaire.

```java
final AppConfig appConfig = AppConfig.builder()
	.addModule(new CommonsFeatures().build())
	.addModule(new VegaFeatures().withEmbeddedServer(8080).build())
	//-----Declaration of a module named 'Hello' which contains a webservice component.
	.addModule(ModuleConfig.builder("Hello")
		.addComponent(HelloWebServices.class)
		.build())
	.build();
```

?> L'exemple de configuration ci-dessous permet la création d'une application fournissant un WebServices   REST 'HelloWorld' sur le port 8080.



L'API fluent de création de la configuration permet d'être guidé dans sa création. Par ce biais il est possible de configurer les éléments suivants :

- **boot** : méthodes `beginBoot` , `endBoot`
- **modules** : méthode `addModule`
  - ajout d'un **composant** :  méthode `addComponent`

  - ajout d'un **plugin** : méthode `addPlugin`

  - ajout d'un **definitionProvider** : méthode `addDefinitionProvider` 

    ajout d'un **aspect** : méthode `addAspect`
- **init** : `addInitializer`

> Lorsque des objets intermédiaires sont requis (par exemple `DefinitionProviderConfig`) il existe toujours un builder associé (`DefinitionProviderConfig.builder()`)

Afin d'aider à la construction des modules, chaque module ou extension de Vertigo contient une classe Java nommée *NomDuModule*__Features__ située à la racine du package du dit module.
Cette classe permet une configuration plus aisée d'un module en abstrayant le choix des composants et des plugins par une activation/desactivation de fonctionalités.

Dans l'exemple il est possible d'activer la fonctionalité **EmbeddedServer** donc un serveur web embarqué uniquement en appelant une méthode et en fournissant le port.

> Il est possible de créer autant de classe de Features que souhaité. La configuration des modules métiers des applications peut-être réalisée selon la même procédure.

Une fois cet objet AppConfig créé il est possible de démarrer l'application : 

```java
try (AutoCloseableApp app = new AutoCloseableApp(appConfig)) {
	//do whatever you want
}
```