# Bien démarrer avec Vertigo

Dans ce guide, nous vous aidons à créer votre première application Vertigo, en deux étapes :
* Comment créer une application minimale et la démarrer
* Comment créer une véritable application, avec un exemple d'écran

## Prérequis

Pour suivre ce guide, vous aurez besoin :
* D'un __éditeur__ de texte ou mieux, d'un __IDE Java__ (nous préconisons l'IDE Eclipse qui sera d'ailleurs utlisé dans ce guide)
* Du Java Development Kit correctement installé - Version : __JDK 1.8 ou supérieur__
* De __Gradle (version 4 ou supérieure)__  ou __Maven (version 3 ou supérieure)__ - ce dernier sera utilisé pour ce guide)

# Application minimale (comment démarrer le moteur...)
# Application complète (Real world Hello World !)

## Création du projet dans l'IDE

Nous utiliserons ici Eclipse. A l'heure de la rédaction de ce guide, la version utilisée est la 2018-09.

1. Création du projet Java (méthode 1 : sans archétype Maven)

Cliquer sur __File > New > Project__. Dans la boîte de dialogue, choisir __Maven > Maven Project__ et cliquer sur __Next__.

Dans l'écran "Select project name and location", cocher l'option _Create a simple project (skip archetype selection)_ et cliquer sur __Next__.

Dans "Configure project", renseigner les champs suivants :
* Group ID : your.group.id (ou autre chose de plus signifiant pour vous !)
* Artifact ID : getting-started-vertigo
* Packaging : War

Cliquer sur __Finish__.

2. Configuration du fichier pom du projet

Ouvrir le fichier __pom.xml__ à la racine du projet.

Rajouter les propriétés permettant de spécifier la version de Java (ici 1.8)

Rajouter les dépendances suivantes dans le fichier pom.xml : 
* Module vertigo-ui (cette dépendance tirera l'ensemble des modules Vertigo requis pour l'application)
* Module vertigo-studio (celui-ci nous simplifie la tâche en générant des parties de code sans valeur ajoutée)
* Les dépendances externes vers des outils nécessaires : 
	* Une base de donnée H2 (il s'agit d'une base mémoire, faile à utiliser à des fins de tests)
	* Le gestionnaire de pool de connexions C3P0 pour la connexion à la base de données

Rajouter l'indication que le répertoire contenant les fichiers générés (src/main/javagen) doit faire partie du "Build Path" d'Eclipse.
	
Le fichier pom.xml devrait maintenant ressembler à ceci : 

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>your.group.id</groupId>
  <artifactId>getting-started-vertigo</artifactId>
  <version>0.0.1-SNAPSHOT</version>
  <packaging>war</packaging>
  
  <properties>
  	<maven.compiler.source>1.8</maven.compiler.source>
	<maven.compiler.target>1.8</maven.compiler.target>
  </properties>
  
  <dependencies>
	  <dependency>
	  	<groupId>io.vertigo</groupId>
	  	<artifactId>vertigo-ui</artifactId>
	  	<version>2.0.0-SNAPSHOT</version>
	  </dependency>
	  <dependency>
	  	<groupId>com.h2database</groupId>
	  	<artifactId>h2</artifactId>
	  	<version>1.4.199</version>
	  </dependency>
	  <dependency>
	  	<groupId>com.mchange</groupId>
	  	<artifactId>c3p0</artifactId>
	  	<version>0.9.5.3</version>
	  </dependency>
  </dependencies>
  
  
  <build>
  	<resources>
  		<resource>
  			<directory>src/main/javagen</directory>
  		</resource>
  	</resources>
  </build>
</project>
```

Une fois le fichier pom.xml complété, cliquer avec le bouton de droite sur le projet getting-started-vertigo puis sur __Maven > Update Projet__.
Dans la boîte de dialogue, vérifier que les éléments suivants sont cochés :
* Update project configuration from pom.xml
* Refresh workspace resources from local filesystem
* Clean projects

Cliquer sur __OK__.


3. Création de la structure du projet

Créer l'arborescence de packages et de répertoires suivante :

XXXXXX SCREENSHOT XXXXXXXX

## Phase de modélisation

Nous allons ici créer la description des entités métier de l'application. Cette description sera utilisée par l'outil _vertigo-studio_ pour créer les classes Java correspondantes ainsi que les classes d'accès aux données.

1. Créer un fichier __modele.ksp__ dans le répertoire __/src/main/resources/your/group/id/gs/modulemetier1/mda__

Dans ce fichier, insérer les éléments suivants:

```json
package your.group.id.modulemetier1.domain 

/* Formatteur de données par défaut */
create Formatter FmtDefault {
	className: "io.vertigo.dynamox.domain.formatter.FormatterDefault"
}

/* Domaines représentant les types de données utilisables dans les entités */
create Domain DoId {
	dataType: Long
	formatter: FmtDefault
	storeType: "NUMERIC"
}

create Domain DoLabel {
	dataType:String
	formatter: FmtDefault
	storeType: "TEXT"
}

/* Description d'une entité métier représentant un film et son titre */
create DtDefinition DtMovie {
	id movId {domain: DoId label: "ID"}
	field title {domain: DoLabel label: "Titre" required: "true"  }
}
```

2. Créer un fichier __mda.kpr__ dans le répertoire __src/main/resources/your/group/id/gs/modulemetier1/__

Ce fichier contient la ligne suivante, indiquant que le fichier à utiliser pour la génération des classes est le fichier ksp créé ci-dessus

```json
mda/modele.ksp
```

3. Créer une classe nommée __Studio__ dans le package __your/group/id/gs/mda/__

Cette classe comprend l'ensemble des instructions permettant de générer les classes Java et les DAO correspondant aux entités métier à partir des fichiers KSP pointés par le fichier KPR.

Copier le code suivant dans la classe Studio : 

```java
package your.group.id.gs.mda;

import io.vertigo.app.AutoCloseableApp;
import io.vertigo.app.config.DefinitionProviderConfig;
import io.vertigo.app.config.ModuleConfig;
import io.vertigo.app.config.NodeConfig;
import io.vertigo.commons.CommonsFeatures;
import io.vertigo.core.param.Param;
import io.vertigo.core.plugins.resource.classpath.ClassPathResourceResolverPlugin;
import io.vertigo.dynamo.DynamoFeatures;
import io.vertigo.dynamo.plugins.environment.DynamoDefinitionProvider;
import io.vertigo.studio.StudioFeatures;
import io.vertigo.studio.mda.MdaManager;

public class Studio {

	// Méthode d'initialisation de la configuration de Studio
	private static NodeConfig buildNodeConfig() {
		return NodeConfig.builder() 									// Création d'un conteneur pour la configuration
				.beginBoot() 											// lancement du moteur Studio
				.addPlugin(ClassPathResourceResolverPlugin.class)		// Initialisation du resolveur de ressources
				.endBoot()												// Le démarrage de vertigo-studio est terminé
				.addModule(new CommonsFeatures().build())				// Configuration des fonctions communes de Vertigo
				.addModule(new DynamoFeatures().build())				// Configuration des fonctions d'accès aux données
				//----Definitions
				.addModule(ModuleConfig.builder("ressources")			// Ajout des ressources pour la génération des classes Java
						.addDefinitionProvider(DefinitionProviderConfig.builder(DynamoDefinitionProvider.class)
								.addDefinitionResource("kpr", "your/group/id/gs/modulemetier1/mda.kpr")
								.build())
						.build())
				// ---StudioFeature
				.addModule(new StudioFeatures()							// Configuration du moteur vertigo-Studio
						.withMasterData()
						.withMda(Param.of("projectPackageName", "your.group.id"))
						.withJavaDomainGenerator(Param.of("generateDtResources", "false"))
						.withTaskGenerator()
						.withSqlDomainGenerator(
								Param.of("targetSubDir", "javagen/sqlgen"),
								Param.of("baseCible", "H2"), 
								Param.of("generateDrop", "true"),
								Param.of("generateMasterData", "true"))
						.build())
				.build();

	}

	
	// Méthode main à lancer pour générer les éléments du projet à partir du modèle 
	public static void main(String[] args) {
		try (final AutoCloseableApp app = new AutoCloseableApp(buildNodeConfig())) {	// Création de l'application vertigo-studio avec la configuration ci-dessus
			final MdaManager mdaManager = app.getComponentSpace().resolve(MdaManager.class);
			//-----
			mdaManager.clean();											// Nettoyage des générations précédentes
			mdaManager.generate().displayResultMessage(System.out);		// Lancement de la génération
		}
	}

}
```
Sauvegarder, cliquer avec le bouton de droite sur le fichier __Studio.java__ puis sur __Run as > Java Application__.

La génération des fichiers est lancée et les entités générées apparaissent dans le répertoire __src/main/javagen/your/group/id__.
Ces éléments sont maintenant utilisables pour créer des services puis des écrans.


