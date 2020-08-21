# MDA

MDA signifie Model Driven Architecture qui est une démarche de développement où la modélisation possède une place centrale.

Vertigo propose un outillage permettant de profiter des avantages de cette méthode, tout en accélérant les développements. Cet outillage est le module **vertigo-studio**. 

vertigo-studio permet d'utiliser la modélisation du projet pour générer du code source nécessaire au développement mais qui découle directement d'une autre source de données déjà écrite par le développeur. 

Ce générateur apporte donc les bénéfices suivants en plus de l'approche MDA : 

- évite une double saisie du développeur et lui fait gagner du temps
- fiabilise le code source en supprimant les erreurs humaines
- améliore la lisibilité du code source en standardisant des pratiques (nommages, arborescence de dossiers et packages, etc...)

Les éléments qui peuvent être générés via vertigo-studio sont :

- les entités JAVA (POJO) issues de la modélisation
- les scripts de création de bases de données (SQL notamment)
- les DAO (Data Access Object) qui offrent un accès simplifié au stockage via un composant dédié par entité métier (cf [ici](/basic/dao) pour plus de détails)
- les entités JavaScript et TypeScript pour les Single Page Applications



## Configuration

Studio est une application Java qui s'exécute en dehors du contexte d'exécution normal du projet. Son exécution est donc toujours à l'initiative du développeur.

Nous proposons d'exécuter Studio via une classe Main Java directement depuis l'IDE utilisé par le développeur. Cette manière de procéder permet une configuration simplifiée et de ne pas lier cette étape du développement à des outils tiers (Ant, Maven etc..) bien qu'il soit techniquement possible de le faire. 

Ainsi, créons une classe  `my.project.mda.Studio.java`, contenant la méthode `main` qui sera exécutée.

```java
public class Studio {

	private static NodeConfig buildNodeConfig() {
		return AppConfig.builder()
				.beginBoot()
				.withLocales("fr_FR")
				.addPlugin(ClassPathResourceResolverPlugin.class)
				.endBoot()
				.addModule(new CommonsFeatures().build()) // requirement
				.addModule(new DynamoFeatures().build()) // requirement
				// ---StudioFeature
				.addModule(new StudioFeatures()
						.withMasterData()
						.withMda(
								Param.of("projectPackageName", "my.project"))
						.withJavaDomainGenerator(
								Param.of("generateDtResources", "false"))
						.withTaskGenerator()
						.withFileGenerator()
						.withSqlDomainGenerator(
								Param.of("baseCible", "PostgreSQL"),
								Param.of("generateDrop", "false"),
								Param.of("generateMasterData", "true"))
						.build())
            	//----Definitions
            	.addModule(ModuleConfig.builder("myAppModel")
.addDefinitionProvider(DefinitionProviderConfig.builder(DynamoDefinitionProvider.class)
								.addParam(Param.of("encoding", "UTF-8"))
								.addDefinitionResource("kpr", "my/project/generation.kpr")
								.build())
						.build())
				.build();

	}

	@Inject
	private MdaManager mdaManager;

	public static void main(final String[] args) {
		try (final AutoCloseableApp app = new AutoCloseableApp(buildNodeConfig())) {
			final Studio studio = new Studio();
			DIInjector.injectMembers(studio, app.getComponentSpace());
			//-----
			studio.cleanGenerate();
		}
	}

	void cleanGenerate() {
		mdaManager.clean();
		mdaManager.generate().displayResultMessage(System.out);
	}
```

Dans cette classe nous pouvons observer dans la méthode `buildNodeConfig` qui permet de spécifier la configuration de la "mini-application vertigo" qui va permettre de lancer la génération de code en partant du modèle.

Dans cette configuration, nous pouvons donc retrouver le module Studio qui est à configurer en fonction des besoins. Pour le détail des options disponibles dans vertigo-studio, vous pouvez vous rapporter à ce [chapitre](/advanced/studio).

On retrouve également un module, dénommé ici "myAppModel", qui permet de charger le modèle de l'application. Pour ce faire, nous utilisons le chargeur de définitions fourni par vertigo-dynamo : `DynamoDefinitionProvider`  qui permet de charger le modèle depuis de multiples sources :

- fichiers kpr : permet une modélisation depuis le DSL de Vertigo via des fichiers texte
- fichiers oom : fichier de modélisation issu du logiciel PowerAmcDesigner
- fichiers xmi : fichier de modélisation issu du logiciel EnterpriseArchitect

Cette classe Studio.java contient une méthode main qui crée la "mini-application vertigo" (`new AutoCloseableApp(buildNodeConfig()) `), puis lance la génération via le `mdaManager`

Pour lancer la génération, il ne reste plus qu'à lancer cette classe Studio par le moyen de votre choix.

!> Nous préconisons d'inclure au gestionnaire de source l'intégralité du code généré par vertigo-studio. En effet, ces fichiers constituent *de facto* une partie du code source de l'application et doivent donc être versionnés. La génération n'est qu'une aide au développeur pour le soulager de tâches ingrates et n'est donc pas à intégrer à la chaine CI/CD. 

## Annexes

Pour que vous puissiez lancer Studio à l'issue de la lecture de ce chapitre, voici des fichiers qui vont seront nécessaires. 

> Il s'agit évidemment d'exemples qu'il est tout à fait possible de modifier pour vous familiariser avec les concepts.

Voici le contenu du fichier *generation.kpr* à placer dans *src/main/resources/my/project/generation.kpr*

```
model.ksp
```

Voici le contenu du fichier *model.ksp* (référencé par le fichier kpr ci-dessus) à placer dans *src/main/resources/my/project/model.ksp*

```json
package my.project.domain

create DtDefinition DtCountry {
  id couId   {domain:DoId     label:"Id"           required:"true"}
  field name {domain:DoLabel  label:"Nom du pays"  required:"false"}
}

create Domain DoId {
	dataType : Long
	formatter : FmtDefault
}

create Domain DoLabel {
	dataType : String
	formatter : FmtDefault
}

create Formatter FmtDefault{
	className : "io.vertigo.dynamox.domain.formatter.FormatterDefault"
}
```







