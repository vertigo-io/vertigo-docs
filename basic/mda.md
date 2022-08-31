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

Vertigo-Studio se configure avec un fichier de configuration YAML.

Dans ce fichier, on va pouvoir configurer :

- la liste des sources qui seront lues pour constituer le `Notebook`
- la configuration des generateurs de code (mda)

Exemple de fichier de configuration YAML

```yaml
resources: 
  - { type: kpr, path: src/main/resources/io/mars/application.kpr}
mdaConfig:
  projectPackageName: io.mars
  targetGenDir : src/main/
  properties: 
    vertigo.domain.java: true
    vertigo.domain.java.generateDtResources: false
    vertigo.domain.sql: true
    vertigo.domain.sql.targetSubDir: javagen/sqlgen
    vertigo.domain.sql.baseCible: H2
    vertigo.domain.sql.generateDrop: true
    vertigo.domain.sql.generateMasterData: true
    vertigo.task: true
    vertigo.search: true
    mermaid: true
```

!> Nous préconisons d'inclure au gestionnaire de source l'intégralité du code généré par vertigo-studio. En effet, ces fichiers constituent *de facto* une partie du code source de l'application et doivent donc être versionnés. La génération n'est qu'une aide au développeur pour le soulager de tâches ingrates et n'est donc pas à intégrer à la chaine CI/CD. 

## Utilisation

Studio peut-etre utilisé selon deux modalités :

- via une extension __VisualStudioCode__
- via une classe Main Java à lancer depuis son IDE favori

> Nous préconisons l'utilisation de l'extension VSCode par défaut. Reserver l'appel via une classe Java pour les cas aux limites et les usages très avancés.

## Extension VSCode

Ajouter l'extension [suivante](https://marketplace.visualstudio.com/items?itemName=vertigo-io.vertigo-vscode&ssr=false#overview) à votre installation de VisualStudioCode.

L'extension s'active automatiquement lorsqu'un fichier ksp est ouvert. 

?>En plus de mettre à disposition Vertigo-Studio l'extension VSCode aujoute le support des KSP (coloration syntaxique et language-server)

Procéder ainsi :

1. Placer le fichier `studio-config.yaml` à la racine du projet.
2. Créer Editer vos fichiers ksp pour concevoir votre projet
3. Dans VSCode : *Terminal* > *Run Task...* > *vertigo-sudio* > *clean-watch*

?> Il existe plusieurs types de tasks, les tasks de type `watch` permettent de suveiller les modifications des fichiers KSP pour générer le code en continu.

?> Pour que les modifications soient automatiquement détectées dans Eclipse pensez à activer les native hooks dans les préférences Eclipse.


## Via une classe Main Java

Studio est une application Java qui s'exécute en dehors du contexte d'exécution normal du projet. Son exécution est donc toujours à l'initiative du développeur.

Il est possible de lancer Studio via une classe Main Java directement depuis l'IDE utilisé par le développeur. Cette manière de procéder permet une configuration simplifiée et de ne pas lier cette étape du développement à des outils tiers (Ant, Maven etc..) bien qu'il soit techniquement possible de le faire. 

Ainsi, créons une classe  `my.project.mda.StudioGenerate.java`, contenant la méthode `main` qui sera exécutée.

```java

public class StudioGenerate {

	public static void main(final String[] args) {
		try {
			VertigoStudioMda.main(new String[] { "generate", Paths.get("studio-config.yaml").toUri().toURL().toExternalForm() });
		} catch (final MalformedURLException e) {
			throw WrappedException.wrap(e);
		}
	}
}

```
## Format de la configuration Yaml

### Généralité

Pour la configuration Vertigo, les éléments important sont :
> - Le format Yaml utilise les indentations pour donner du sens, il faut y faire attention.
> - L'indentation avec `-` n'est utilisée que pour déclarer les listes. ie. pour le nom des plugins actives (1er niveau sous `features:` et `featuresConfig:`), pour les plugins custom (1er niveau sous `plugins:`) et les initialisers (1er niveau sous `initializers:`)
> - L'indentation seule, sans `-` est utilisée pour les attributs et les maps. Notament les Features sous `modules:` et les paramètres en général (de plugin, feature, ...)
> - Des valeurs peuvent venir de paramètres extérieur avec `${ }`. _Ceux du `boot` viennent de sources limitée et doivent être préfixé par `boot.`_
!> - Vertigo support l'attribut particulier `__flags__:` placé sous n'importe quels éléments il permet de conditionner l'inclusion de l'élément dans la configuration en fonction des activeFlags (paramètre de démarrage de l'application : ligne de commande, web.xml, etc...). _le flag peut être inclus : `__flags__: ["redis"]` ou exclus : `__flags__: ["!redis"]`

_Note : En interne, le fichier Yaml est mappé sur l'objet `io.vertigo.core.node.config.yaml.YamlAppConfig`_

Extrait de [Wikipedia](https://fr.wikipedia.org/wiki/YAML) : 
- Les commentaires sont signalés par le signe dièse `#` et se prolongent sur toute la ligne. Si par contre le dièse apparait dans une chaine, il signifie alors un nombre littéral.
- Une valeur nulle s'écrit avec le caractère tilde `~`
- Il est possible d'inclure une syntaxe JSON dans une syntaxe YAML.
- Les éléments de listes sont dénotés par le tiret `-`, suivi d'une espace, à raison d'un élément par ligne.
- Les tableaux sont de la forme `clé: valeur`, à raison d'un couple par ligne.
- Les scalaires peuvent être entourés de guillemets doubles `"`, ou simples `'`, sachant qu'un guillemet s'échappe avec un antislash `\`, alors qu'une apostrophe s'échappe avec une autre apostrophe5. Ils peuvent de plus être représentés par un bloc indenté avec des modificateurs facultatifs pour conserver `|` ou éliminer `>` les retours à la ligne.
- Plusieurs documents rassemblés dans un seul fichier sont séparés par trois traits d'union `---` ; trois points `...` optionnels marquent la fin d'un document dans un fichier.
- Les nœuds répétés sont initialement signalés par une esperluette `&` puis sont référencés avec un astérisque `*` ; JSON, un langage concurrent de YAML, est compatible avec la syntaxe de JavaScript mais ne supporte pas cette notion de référence.
- L'indentation, par des espaces, manifeste une arborescence.


### boot
Le fichier est composée d'une première partie déclarant le comportement de la phase de démarrage du système :

- `boot` la balise déclare le début de cette configuration. Cela inclus les Managers par défaut : LocaleManager, ResourceManager, ParamManager, DaemonManager, AnalyticsManager
- > `params` déclare les paramètres des Managers par défaut
- > `plugins` déclare les plugins des Managers par défaut


Exemple :
```yaml
boot:
  params:
    locales: fr_FR
  plugins:
    - io.vertigo.core.plugins.resource.classpath.ClassPathResourceResolverPlugin: {}
    - io.vertigo.core.plugins.resource.url.URLResourceResolverPlugin: {}
    - io.vertigo.core.plugins.param.properties.PropertiesParamPlugin:
       url : file:./src/test/java/fr/gouv/interieur/rdvpref/support/env-test.properties
    - io.vertigo.core.plugins.param.env.EnvParamPlugin: {}
```

### modules
Le fichier est composée d'une seconde partie déclarant les modules de l'application :

- `modules` la balise déclare le début de cette configuration. Il faut ensuite déclarer les Features à appliquer.
- > `xx.xxx.XxxFeatures` le chemin complet de la class déclarant la feature
- > `features` déclare les features optionnelles (et leurs paramètres) effectivement activées _les features possibles sont déclarées avec `@Feature` sur la classe de Features_
- > `featuresConfig` déclare les plugins (et leurs paramètres) des features _les features doivent avoir été activées_
- > `plugins` _(optionel)_ il est possible de déclarer des plugins complémentaires non prévus dans la Feature

!> L'ordre de déclaration des modules est important, les modules ne peuvent dépendre que des modules _'au dessus'_ d'eux

Typiquement, on déclare les Modules Vertigo utilisés, puis ceux de l'application.
```
   <Connectors> JavalinFeatures
   CommonsFeatures
   DatabaseFeatures
   DataModelFeatures
   DataStoreFeatures
   DataFactoryFeatures
   AccountFeatures
   VegaFeatures
   <modules de l'application> io.mars.support.SupportFeatures
   <modules de l'application> io.mars.basemanagement.BasemanagementFeatures
```

Exemple :
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

### Initializers

La configuration se termine par la déclaration des Initializers.
Ceux ci enrichissent les composants après leur démarrage.

Habituellement on déclare des Initialiers tel que : 
```yaml
  - io.mars.support.boot.InitialDataInitializer:
  - io.mars.support.boot.I18nResourcesInitializer:
  - io.mars.support.boot.SearchInitializer:
  - io.mars.support.boot.OrchestraInitializer:
```

## Annexes

Pour que vous puissiez lancer Studio à l'issue de la lecture de ce chapitre, voici des fichiers qui vont seront nécessaires. 

> Il s'agit évidemment d'exemples qu'il est tout à fait possible de modifier pour vous familiariser avec les concepts.

Voici le contenu du fichier *studio-config.yaml*
```yaml
resources: 
  - { type: kpr, path: src/main/resources/my/project/generation.kpr}
mdaConfig:
  projectPackageName: my.project
  targetGenDir : src/main/
  properties: 
    vertigo.domain.java: true
    vertigo.domain.java.generateDtResources: false
    vertigo.domain.sql: true
    vertigo.domain.sql.targetSubDir: javagen/sqlgen
    vertigo.domain.sql.baseCible: H2
    vertigo.domain.sql.generateDrop: true
    vertigo.domain.sql.generateMasterData: true
    vertigo.task: true
    vertigo.search: true
    mermaid: true
```


Voici le contenu du fichier *generation.kpr* à placer dans *src/main/resources/my/project/generation.kpr*

```
model.ksp
```

Voici le contenu du fichier *model.ksp* (référencé par le fichier kpr ci-dessus) à placer dans *src/main/resources/my/project/model.ksp*

```json
package my.project.domain

create Domain DoId {
	dataType : Long
}

create Domain DoLabel {
	dataType : String
}

create DtDefinition DtCountry {
  id couId   {domain:DoId     label:"Id"           }
  field name {domain:DoLabel  label:"Nom du pays"  cardinality:"?"}
}


```







