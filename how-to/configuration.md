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