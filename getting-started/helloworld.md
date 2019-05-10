# Application minimale (comment démarrer le moteur...)

Dans ce chapitre nous allons voir comment une application Vertigo peut-être démarrée.
Pour illustrer ce propos nous allons construire une application mettant à disposition un WebService REST Helloworld.

## Création du projet Maven

Pour créer ce projet vous pouvez soit utiliser l'assitant de d'un IDE pour vous assister ou via tout autre méthode, l'essentiel est de :

- Spécifier la version de Java a utiliser via les propriétés Maven
- Ajouter la dépendance vers __vertigo-vega__ (l'ensemble des dépendances nécessaires sont transitives et donc récupérer automatiquement via maven)

A l'issu de cette création votre fichier __pom.xml__ doit ressembler à ça :

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>your.group.id</groupId>
  <artifactId>helloworld-vertigo</artifactId>
  <version>0.0.1-SNAPSHOT</version>
  <packaging>jar</packaging>
  
  <properties>
  	<maven.compiler.source>1.8</maven.compiler.source>
	<maven.compiler.target>1.8</maven.compiler.target>
  </properties>
  
  <dependencies>
	<dependency>
	  <groupId>io.vertigo</groupId>
	  <artifactId>vertigo-vega</artifactId>
	  <version>2.0.0-SNAPSHOT</version>
	</dependency>
  </dependencies>
 
</project>
```

## Création du WebService

Pour créer votre webservice rien de plus simple :
- Créer une classe implémentant l'interface `io.vertigo.vega.webservice.WebServices` (Pas d'inquiétude il s'agit uniquement d'un marqueur...). Par exemple nommez la `io.vertigo.samples.hello.webservices.HelloWebServices`
- Ajouter une méthode annotée qui renvoit sur un appel `GET` sur la route `/hello/` la chaine de caractère `"Hello World!"`

Et voici la classe en question : 

```java
package io.vertigo.samples.hello.webservices;

import io.vertigo.vega.webservice.WebServices;
import io.vertigo.vega.webservice.stereotype.AnonymousAccessAllowed;
import io.vertigo.vega.webservice.stereotype.GET;
import io.vertigo.vega.webservice.stereotype.PathPrefix;

@PathPrefix("/helloworld")
public class HelloWebServices implements WebServices {

	@AnonymousAccessAllowed
	@GET("/")
	public String hello() {
		return "Hello World!";
	}

}
```

> Avec Vertigo tout est sécurisé par défaut. L'annotation `@AnonymousAccessAllowed` permet de s'affranchir de ce contrôle pour les besoins du Helloworld. Ce n'est évidement par à utiliser en production.


## Création de la classe Main

Créer une classe Main Java afin de démarrer le helloworld. Dans la méthode `main` nous allons :

- Démarrer l'application 
- Attendre une entrée système juste pour maintenir l'application allumée le temps d'aller voir le resulat dans un navigateur

Voici notre classe Main :

```java
/***
 * Start the main method.
 *
 * Call "http://localhost:8080/hello" with your web browser.
 * You may receive an "hello world" back.
 *
 */
public class HelloWorld {

	public static void main(final String[] args) throws IOException {
		
		// Create the nodeConfig
		final NodeConfig nodeConfig = NodeConfig.builder()
				.addModule(new CommonsFeatures().build())
				.addModule(new VegaFeatures() // we want to use Vega that offers simple REST WebServices management
						.withWebServices()
						.withWebServicesEmbeddedServer(Param.of("port", "8080"))
						.build())
				//-----Declaration of a module named 'Hello' which contains a webservice component.
				.addModule(ModuleConfig.builder("Hello")
						.addComponent(HelloWebServices.class)
						.build())
				.build();

		try (AutoCloseableApp app = new AutoCloseableApp(nodeConfig)) { // start the app
			System.in.read(); // wait for connection (this is not real world code...)
		}

```

Il ne reste plus qu'à exécuter cette classe par le biais de votre choix, le plus simple étant de le faire via un IDE (dans Eclipse : Clic-droit sur la classe > Run As > Java Application )

Il ne reste plus qu'à vous rendre à l'adresse suivante : http://localhost:8080/hello/ et admirer le résultat. 
Vous savez maintenant faire une application Vertigo! Pour aller plus loin consultez le chapitre [Application complète (Real world Hello World !)](getting-started/realworld_helloworld.md) qui vous permettra de faire une mini-application de la vraie vie...