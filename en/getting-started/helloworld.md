# Minimal application (how to start the engine...)

In this chapter we will see how a Vertigo application can be started.
To illustrate this, we will build an application exposing a Helloworld REST WebService.

## Creating the Maven project

To create this project you can either use an IDE assistant or any other method, the essential is to:

- Specify the Java version to use via Maven properties
- Add the dependency to __vertigo-vega__ (all necessary dependencies are transitive and thus retrieved automatically via maven)

Once created, your __pom.xml__ file should look like this:

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
	<modelVersion>4.0.0</modelVersion>
	<groupId>your.group.id</groupId>
	<artifactId>helloworld-vertigo</artifactId>
	<version>0.0.1-SNAPSHOT</version>
	<packaging>jar</packaging>
	
	<properties>
		<maven.compiler.source>11</maven.compiler.source>
		<maven.compiler.target>11</maven.compiler.target>
	</properties>
	
	<dependencies>
		<dependency>
			<groupId>io.vertigo</groupId>
			<artifactId>vertigo-vega</artifactId>
			<version>4.3.2</version>
		</dependency>
	</dependencies>
	
</project>
```

## Creating the WebService

Creating your webservice is simple:
- Create a class implementing the `io.vertigo.vega.webservice.WebServices` interface (Don't worry, it's just a marker...). For example, name it `io.vertigo.samples.hello.webservices.HelloWebServices`
- Add an annotated method that returns the string `"Hello World!"` on a `GET` call to the route `/hello/`

And here is the class:

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

> With Vertigo everything is secured by default. The `@AnonymousAccessAllowed` annotation bypasses this control for Helloworld purposes. Obviously, this should not be used in production.


## Creating the Main class

Create a Java Main class to start the helloworld. In the `main` method, we will:

- Start the application
- Wait for system input just to keep the application running while we check the result in a browser

Here is our Main class:

```java
/**
 * Start the main method.
 *
 * Call "http://localhost:8080/helloworld" with your web browser.
 * You may receive an "hello world" back.
 *
 */
public class HelloWorld {

	public static void main(final String[] args) throws IOException {
		
		// Create the nodeConfig
		final NodeConfig nodeConfig = NodeConfig.builder()
		        .addModule(new JavalinFeatures().withEmbeddedServer(Param.of("port", "8080")).build()) // we want to use javalin embedded
				.addModule(new DataModelFeatures().build()) // we want the support of DtObjects
				.addModule(new VegaFeatures() // we want to use Vega that offers simple REST WebServices management
						.withWebServices()
						.withJavalinWebServerPlugin()
						.build())
				//-----Declaration of a module named 'Hello' which contains a webservice component.
				.addModule(ModuleConfig.builder("Hello")
						.addComponent(HelloWebServices.class)
						.build())
				.build();

		try (AutoCloseableNode app = new AutoCloseableNode(nodeConfig)) { // start the app
			System.in.read(); // wait for connection (this is not real world code...)
		}

```

All that remains is to run this class however you choose, the simplest being via an IDE (in Eclipse: Right-click on the class > Run As > Java Application)

Then navigate to: http://localhost:8080/helloworld/ and admire the result.
You now know how to build a Vertigo application! To go further, consult the [Complete application (Real world Hello World !)](/en/getting-started/realworld_helloworld.md) chapter to build a mini real-life application...
