# Orchestra

**Orchestra** est un module de la plateforme Vertigo permettant la gestion des jobs et des batchs : ce qu'on appelle couramment un job ou un batch s'appelle un **processus** dans Orchestra.

Il permet à la fois de programmer et lancer des processus avec une stratégie prédéfinie et de fournir une API pour les configurer et les superviser.

Il inclut de nombreuses fonctionnalités :

- Support natif du multi-nœud avec gestion de la charge
- Détection des nœuds morts
- Récupération des planifications ratées
- Logging (Fichier + DB) (Un humain peut facilement y accéder, y compris via une IHM)
- Délégation du traitement asynchrone à un autre serveur / une autre application

## Qu'est-ce qu'un processus dans Orchestra ?

- Un processus est une liste séquentielle d'activités
- Un processus peut être programmé dans le temps via diverses stratégies (une expression cron, une exécution ponctuelle)
- Chaque exécution prévue est une **planification** : elle est créée à l'avance, à partir du cron ou par un appel au planificateur (*scheduler*), et devient une exécution à son heure

## Donc qu'est-ce qu'une activité dans Orchestra ?

- Une activité est l'unité d'exécution. C'est elle qui contient le code qui doit être exécuté.
- Une activité gère la suite à donner au processus
- Toutes les activités d'un processus partagent un environnement commun d'exécution appelé **workspace** : des paramètres sous forme de clés et de valeurs, transmis d'une activité à la suivante

## Comment l'utiliser ?

Orchestra offre les fonctionnalités suivantes :
- Une API de gestion des processus
- Deux implémentations pour la gestion des exécutions
  - Base de données, avec gestion des logs, du monitoring et du multi-nœud
  - Mémoire
- Une API REST pour gérer les processus, les exécutions, la planification et la supervision
- Une IHM Vue.js embarquée (voir [IHM embarquée](#ihm-embarquée))

Lorsque le module Orchestra est ajouté à votre application, il est possible de l'utiliser en mode intégré ou comme un nœud standalone dans une architecture micro-services. L'application de démonstration [Mars](https://github.com/vertigo-io/vertigo-mars) l'utilise en mode intégré.

### Ajout du module dans le pom

```xml
<dependency>
	<groupId>io.vertigo</groupId>
	<artifactId>vertigo-orchestra</artifactId>
	<version>${vertigo.version}</version>
</dependency>
```

### Mode base de données et mode mémoire

Chaque définition de processus a un **type**, qui désigne le mode qui la gère :

| Type (`ProcessType`) | Mode | Feature |
|---|---|---|
| `SUPERVISED` (par défaut) | Base de données : définitions conservées, suivi des exécutions, journaux, multi-nœud | `orchestra.database` |
| `UNSUPERVISED` | Mémoire : rien n'est conservé d'un démarrage à l'autre, pas de suivi des exécutions | `orchestra.memory` (paramètre obligatoire : `workersCount`) |

Les deux features peuvent être activées ensemble. En mode mémoire seul, les définitions doivent être construites avec `withProcessType(ProcessType.UNSUPERVISED)` (voir [Les processus](#les-processus)). Sauf mention contraire, la suite de cette page décrit le mode base de données.
<!-- source : ProcessDefinitionBuilder.java:L78, L174-176 (SUPERVISED par défaut) ; MemoryProcessDefinitionStorePlugin.java:L81-82, MemoryProcessExecutorPlugin.java:L161-162 (UNSUPERVISED) ; OrchestraDefinitionManagerImpl.java:L86-87 ; OrchestraFeatures.java:L144-154 -->

### Configuration en mode base de données

La configuration YAML d'Orchestra en mode base de données, telle que dans Mars :

```yaml
io.vertigo.orchestra.OrchestraFeatures:
  featuresConfig:
    - orchestra.database:
        nodeName: MARS1
        daemonPeriodSeconds: 30
        workersCount: 10
        forecastDurationSeconds: 60
    - orchestra.webapi:
```

| Paramètre | Rôle |
|---|---|
| `nodeName` | Nom du nœud : il doit être propre à chaque nœud de l'application (en multi-nœud, il vient en général d'une variable d'environnement, par exemple `${ORCHESTRA_NODE_NAME}`) |
| `daemonPeriodSeconds` | Période, en secondes, des deux daemons d'Orchestra : celui qui planifie les exécutions et celui qui les exécute |
| `workersCount` | Nombre d'activités que le nœud exécute en même temps (la taille de son pool de workers) |
| `forecastDurationSeconds` | Durée, en secondes, sur laquelle les prochaines exécutions des processus planifiés sont prévues à l'avance |

Ces quatre paramètres sont obligatoires. La feature `orchestra.webapi` publie l'API REST (voir [Piloter Orchestra par webservices](#piloter-orchestra-par-webservices)) ; elle nécessite les webservices de l'application (voir [WebServices](/basic/webservices)).
<!-- source : OrchestraFeatures.java:L77-85 (findParamByName), L95-112 (daemonPeriodSeconds -> planningPeriodSeconds et executionPeriodSeconds) ; DbProcessExecutorPlugin.java:L144 (pool de workers) ; DbProcessSchedulerPlugin.java:L124, L308 (durée de prévision) ; mars.yaml:L212-219 (master) -->

Tout le modèle Orchestra est déclaré en `@DataSpace("orchestra")` : l'application déclare donc un store SQL pour ce dataSpace. Ses accès passent par la connexion désignée par le paramètre `connectionName` de ce store (par défaut, la connexion principale). Il est recommandé de lui donner une connexion dédiée, afin d'isoler Orchestra du pool applicatif, et de la dimensionner en cohérence avec le paramètre `workersCount` (voir [Connexions multiples et dataSpace](/extensions/database#connexions-multiples-et-dataspace)).

```yaml
io.vertigo.datastore.DataStoreFeatures:
  features:
    - entitystore:
  featuresConfig:
    - entitystore.sql:          # le store de l'application
    - entitystore.sql:          # le store d'Orchestra
        dataSpace: orchestra
```
<!-- source : domain/*/O*.java (@DataSpace("orchestra")) ; SqlEntityStorePlugin.java:L118-130 (connectionName, défaut main) ; mars.yaml:L136-138 (master) -->

Pour utiliser Orchestra en version base de données, il est nécessaire d'initialiser cette base (création des tables et insertion des données primaires) à l'aide du script [`orchestra_create_init_v1.0.0.sql`](https://github.com/vertigo-io/vertigo-modules/blob/master/vertigo-orchestra/src/main/database/scripts/install/orchestra_create_init_v1.0.0.sql), écrit pour PostgreSQL.

?> En développement, ce script et les requêtes d'Orchestra fonctionnent aussi avec H2 (2.x) en mode de compatibilité PostgreSQL (`MODE=PostgreSQL` dans l'URL JDBC), comme dans la configuration locale de Mars.
<!-- source : orchestra_create_init_v1.0.0.sql exécuté entièrement avec H2 2.2.224 en MODE=PostgreSQL ; FOR UPDATE et extract('epoch' from …) acceptés ; mars.yaml:L114 (master) -->

### Configuration en mode mémoire

```yaml
io.vertigo.orchestra.OrchestraFeatures:
  featuresConfig:
    - orchestra.memory:
        workersCount: 10
```

## Mise en œuvre

### Les activités

Le code d'une activité est porté par un **ActivityEngine** : une interface dont la méthode `execute` reçoit le workspace de l'activité et le renvoie, complété de son **statut**. La classe abstraite **AbstractActivityEngine** en fournit l'implémentation de base : un journal (`getLogger()`), des traitements après succès et après erreur, et la mise en attente pour un traitement délégué (`setActivityPending`). Une activité étend en principe cette classe.

```java
public class MyActivityEngine extends AbstractActivityEngine {

	/** {@inheritDoc} */
	@Override
	public ActivityExecutionWorkspace execute(final ActivityExecutionWorkspace workspace) {
		getLogger().info("Traitement en cours");
		// … le traitement de l'activité
		workspace.setSuccess();
		return workspace;
	}

}
```

Le statut donné au workspace détermine la suite du processus :

| Méthode du workspace | Suite donnée au processus |
|---|---|
| `setSuccess()` | Terminée (`DONE`) |
| `setFinished()` | Terminée, et le processus se termine (`DONE`) sans exécuter les activités suivantes |
| `setFailure()` | En erreur (`ERROR`) : le processus s'arrête |
| `setActivityPending(workspace)` (méthode d'`AbstractActivityEngine`) | En attente de la fin d'un traitement délégué (voir [Déléguer un traitement](#déléguer-un-traitement)) ; n'appelez pas directement `workspace.setPending()` |

Une activité qui ne donne pas de statut, ou qui lève une exception, se termine en erreur.

?> En mode mémoire, `setFinished()` n'interrompt pas le processus et la délégation n'est pas disponible.
<!-- source : ActivityEngine.java ; ActivityExecutionWorkspace.java:L204-225 ; AbstractActivityEngine.java:L43-70 ; DbProcessExecutorPlugin.java:L368-382 (statut obligatoire, exception -> échec), L397-419 (putResult : DONE, finishProcessExecution, pending, ERROR), L628-633 ; MemoryProcessExecutorPlugin.java:L113-116, L166-176 -->

**Le workspace** porte les paramètres de l'activité, sous forme de clés et de valeurs. Lorsqu'une activité se termine avec succès, son workspace de sortie devient le workspace d'entrée de l'activité suivante : c'est le mécanisme de partage de données entre activités (`workspace.setValue(clé, valeur)`, puis `workspace.getValue(clé)`).

**Le journal** de l'activité (`getLogger().info(…)`, `warn(…)`, `error(…)`) est enregistré avec son exécution, et consultable par l'API ou par l'IHM ; en mode mémoire, il va seulement dans les logs de l'application.

**Le fichier joint** : une activité peut produire un fichier (un rapport, un export). Elle l'écrit sous le répertoire donné par le paramètre d'application `orchestra.root.directory` (lu par le `ParamManager`, voir [Configuration](/basic/configuration)), et indique son chemin relatif à ce répertoire par `workspace.setAttachment(chemin)`. Le fichier est ensuite téléchargeable par l'API.
<!-- source : ActivityExecutionWorkspace.java:L59-81, L181 ; ActivityLogger.java:L54-88 ; DbProcessExecutorPlugin.java:L510-527 (workspace transmis à l'activité suivante), L647-648, L665-681 (saveActivityLogs, journal et pièce jointe) ; DbProcessLoggerPlugin.java:L48, L90-101 (orchestra.root.directory) -->

**L'instanciation** : Orchestra crée une nouvelle instance de l'ActivityEngine à chaque exécution d'une activité, et y injecte les composants dont elle a besoin (`@Inject`). Un ActivityEngine n'est donc pas enregistré comme composant, et ne conserve aucun état d'une exécution à l'autre.
<!-- source : DbProcessExecutorPlugin.java:L354, MemoryProcessExecutorPlugin.java:L126 (InjectorUtil.newInstance) -->

> Un processus n'est qu'un enchaînement d'activités : une activité gagne à être réutilisable, pour servir à plusieurs processus.

### Les processus

Un processus est décrit par une **ProcessDefinition** : son nom, son libellé, la liste ordonnée de ses activités et sa stratégie de déclenchement. Elle se construit par la factory `ProcessDefinition.builder(name, label)` (le constructeur de `ProcessDefinitionBuilder` n'est pas public).

```java
final ProcessDefinition processDefinition = ProcessDefinition.builder("ProMyProcess", "Mon processus")
		.withCronExpression("0 0 2 * * ?") // tous les jours à 2h
		.addActivity("EXTRACT", "Extraction", ExtractActivityEngine.class)
		.addActivity("REPORT", "Rapport", ReportActivityEngine.class)
		.build();
```

!> Une `ProcessDefinition` est une définition Vertigo : son nom commence obligatoirement par le préfixe `Pro`, suivi de lettres ou de chiffres, le premier en majuscule (`ProMyProcess`, sans `_`), 61 caractères au plus au total. Le nom d'une activité, lui, est libre (non vide).
<!-- source : ProcessDefinition.java:L33-35 (@DefinitionPrefix "Pro"), L92-94 (builder) ; DefinitionId.java:L53, L64-67 ; ActivityDefinition.java:L38-41 -->

Les options du builder :

| Méthode du builder | Effet |
|---|---|
| `addActivity(name, label, engineClass)` | Ajoute une activité, à la suite des précédentes |
| `withCronExpression(cron)` | Planifie le processus. L'expression cron est au format Quartz, en 6 ou 7 champs (l'année est facultative), dont le premier est la seconde (Mars : `"0 0/1 * ? * * *"`, toutes les minutes) |
| `addInitialParam(name, value)`, `addInitialParams(map)` | Paramètres initiaux, placés dans le workspace de la première activité |
| `withMultiExecution()` | Autorise plusieurs exécutions simultanées du même processus |
| `withRescuePeriod(rescuePeriod)` | Période pendant laquelle une planification ratée (le nœud était arrêté) est encore rattrapée |
| `inactive()` | Crée le processus désactivé : en mode base de données, il n'est pas planifié par son cron |
| `withProcessType(type)` | Type du processus : `SUPERVISED` (par défaut) ou `UNSUPERVISED` (voir [Mode base de données et mode mémoire](#mode-base-de-données-et-mode-mémoire)) |
| `withMetadatas(map)` | Métadonnées libres associées au processus |
| `withNeedUpdate()` | Le code fait foi à chaque démarrage (voir [Cas des évolutions des processus](#cas-des-évolutions-des-processus)) |
<!-- source : ProcessDefinitionBuilder.java:L68-172 ; CronExpression.java:L465-470 (année facultative) ; DbProcessSchedulerPlugin.java:L321 (processus actifs), L357-368 (rattrapage) ; mars OrchestraInitializer.java (cron) -->

La définition est enregistrée par le manager `OrchestraDefinitionManager` :

```java
orchestraDefinitionManager.createOrUpdateDefinition(processDefinition);
```

En mode base de données, elle est alors conservée en base, qui fait foi aux démarrages suivants (voir [Cas des évolutions des processus](#cas-des-évolutions-des-processus)).

### Déclarer ses processus dans un projet

Les définitions s'enregistrent au démarrage de l'application. Deux pratiques existent.

**Un initializer**, cité dans la section `initializers` du fichier YAML, qui enregistre tous les processus de l'application. C'est le choix de Mars ([`OrchestraInitializer`](https://github.com/vertigo-io/vertigo-mars/blob/master/src/main/java/io/mars/support/boot/OrchestraInitializer.java)) :

```java
public class OrchestraInitializer implements ComponentInitializer {

	@Inject
	private OrchestraDefinitionManager orchestraDefinitionManager;

	/** {@inheritDoc} */
	@Override
	public void init() {
		final ProcessDefinition processDefinition = ProcessDefinition.builder("ProEquipmentDecommissioning", "Equipment decommissioning")
				.withCronExpression("0 0/1 * ? * * *")
				.addActivity("DECOMMISSION", "Decommission equipmenents", DecommissionEquipmentActivityEngine.class)
				.addActivity("REPORT", "Produce a file report of the decommisioned equipments", DecommissioningReportActivityEngine.class)
				.build();
		orchestraDefinitionManager.createOrUpdateDefinition(processDefinition);
		// … les autres processus de l'application
	}
}
```
Il est déclaré dans le fichier YAML de l'application :

```yaml
initializers:
  - io.mars.support.boot.OrchestraInitializer:
```
<!-- source : vertigo-mars OrchestraInitializer.java:L20-35 ; mars.yaml:L319 (master) -->

**Un composant par processus**, rangé dans le package de son module : comme les autres composants du module, il est découvert par sa classe `Features` (voir [Configuration](/basic/configuration#configuration-par-features-api-java)). Il enregistre sa définition au démarrage, dans sa méthode `start()` (`Activeable`), et lit ses réglages dans le `ParamManager`, qui les cherche dans les paramètres de l'application : variables d'environnement, fichier de propriétés… (voir [Paramètres](/basic/configuration#parametres)). Par exemple, une purge dont le nombre de jours se règle par environnement :

```java
public class PurgeJob implements Component, Activeable {

	@Inject
	private OrchestraDefinitionManager orchestraDefinitionManager;
	@Inject
	private ParamManager paramManager;

	@Override
	public void start() {
		final int olderThanDays = paramManager.getOptionalParam("PURGE_OLDER_THAN_DAYS")
				.map(Param::getValueAsInt)
				.orElse(30);
		orchestraDefinitionManager.createOrUpdateDefinition(ProcessDefinition.builder("ProPurge", "Purge des données anciennes")
				.withCronExpression("0 30 5 1/1 * ? *") // tous les jours à 5h30
				.addInitialParam("olderThanDays", String.valueOf(olderThanDays))
				.addActivity("PURGE", "Purge", PurgeActivityEngine.class)
				.build());
	}

	@Override
	public void stop() {
		// rien à faire
	}
}
```
<!-- source : vertigo-core ComponentDiscovery.java (découverte du package), ParamManager.java:L67 (getOptionalParam), Param.java:L128 (getValueAsInt), Activeable (start/stop) -->

Un job qu'un environnement doit pouvoir désactiver (par exemple sur les nœuds qui n'exécutent pas de traitements) est au contraire exclu de la découverte par `@NotDiscoverable`, et déclaré par une feature de son module, que le fichier YAML active, ici sous un flag :

```java
@Feature("purge.job")
public MyModuleFeatures withPurgeJob() {
	getModuleConfigBuilder().addComponent(PurgeJob.class);
	return this;
}
```

```yaml
modules:
  com.mycompany.myapp.mymodule.MyModuleFeatures:
    features:
      - purge.job:
          __flags__: ["jobs"]
```
<!-- source : ComponentDiscovery.java:L64 (NotDiscoverable), YamlNodeConfigBuilder.java:L223-240 (features, __flags__) -->

!> En mode base de données, une définition déjà enregistrée n'est pas remplacée au démarrage suivant : changer le cron, les activités ou un paramètre initial (ici `olderThanDays`) dans le code ou dans la configuration n'a pas d'effet tant que la définition n'est pas mise à jour (voir [Cas des évolutions des processus](#cas-des-évolutions-des-processus)).
<!-- source : DbProcessDefinitionStorePlugin.java:L199-218 -->

### Lancer une exécution

Une fois la définition enregistrée, il est dès lors possible de l'utiliser via le composant `OrchestraServices` :
- Planifier de nouvelles exécutions (`getScheduler()`)
- Superviser les exécutions (`getReport()`, voir [Retrouver un processus et ses exécutions](#retrouver-un-processus-et-ses-exécutions))

L'usage recommandé est de passer par le *scheduler*, qui respecte les règles d'exécution du processus : par exemple, il ne lance pas une nouvelle exécution d'un processus déjà en cours, sauf s'il autorise l'exécution multiple. L'exécuteur (`orchestraServices.getExecutor().execute(…)`) lance une exécution directement, sans ces contrôles. Pour une exécution immédiate, utilisez la méthode `scheduleAt` du `ProcessScheduler` avec comme date `Instant.now()` :

```java
orchestraServices.getScheduler().scheduleAt(processDefinition, Instant.now(), Map.of());
```

?> En mode base de données, l'exécution démarre au passage suivant des daemons d'Orchestra (voir le paramètre `daemonPeriodSeconds`), et non à l'instant exact de l'appel.
<!-- source : DbProcessSchedulerPlugin.java:L130, L270-277, L280-288 (exécution multiple) ; DbProcessExecutorPlugin.java:L149, L212-222, L307-321 ; ProcessExecutor.java:L30 -->

!> Chaque appel à `scheduleAt` **ajoute** une planification : il n'existe pas d'API d'annulation d'une planification déjà posée (voir [Cas des évolutions des processus](#cas-des-évolutions-des-processus) pour la purge des planifications futures).

Avec la feature `orchestra.webapi`, le déclenchement et le suivi sont aussi possibles par l'API REST : voir [Piloter Orchestra par webservices](#piloter-orchestra-par-webservices).

### Passer des paramètres à une exécution

Le troisième argument de `scheduleAt` est une `Map<String, String>` de paramètres initiaux : elle s'ajoute aux paramètres initiaux de la définition pour former le workspace (`ActivityExecutionWorkspace`) de la première activité du processus.

```java
orchestraServices.getScheduler().scheduleAt(processDefinition, Instant.now(), Map.of("dossierId", "1234"));
```

Côté `ActivityEngine`, le workspace donne accès à ces paramètres :

```java
/** {@inheritDoc} */
@Override
public ActivityExecutionWorkspace execute(final ActivityExecutionWorkspace workspace) {
	if (workspace.containsKey("dossierId")) {
		final String dossierId = workspace.getValue("dossierId");
		// ...
	}
	final Long preId = workspace.getProcessExecutionId(); // id de l'exécution en cours (mode base de données)
	workspace.setSuccess();
	return workspace;
}
```
<!-- source : ProcessScheduler.java:L38 ; DbProcessExecutorPlugin.java:L461-472 ; ActivityExecutionWorkspace.java:L142 -->

### Déléguer un traitement

En mode base de données, une activité peut confier son traitement à un autre serveur ou une autre application. Elle appelle `setActivityPending(workspace)` (méthode d'`AbstractActivityEngine`) et transmet au traitement distant l'identifiant de l'exécution de l'activité (`workspace.getActivityExecutionId()`) et son jeton (`workspace.getToken()`) : l'activité passe dans l'état `PENDING`. À la fin de son traitement, le serveur distant le signale par l'[API REST d'Orchestra](#piloter-orchestra-par-webservices), avec cet identifiant et ce jeton : `onSuccess` en cas de succès, `onError` (avec un message) en cas d'erreur.
<!-- source : AbstractActivityEngine.java:L66-70 ; ActivityExecutionWorkspace.java:L126, L174 ; WsExecutionControl.java:L58-87 ; DbProcessExecutorPlugin.java:L234-243 -->

## Retrouver un processus et ses exécutions

Une exécution de processus est identifiée par son `preId`, et chaque exécution d'activité par son `aceId`.

- Les définitions : `orchestraDefinitionManager.getProcessDefinition(processName)`, ou `getAllProcessDefinitions()`.
- Les exécutions, par le rapport `orchestraServices.getReport()` (en mode base de données seulement) : `getProcessExecutions(processDefinition, status, limit, offset)`, `getProcessExecution(preId)`, `getActivityExecutionsByProcessExecution(preId)`, et les résumés `getSummaryByDate(processDefinition, minDate, maxDate)` et `getSummariesByDate(minDate, maxDate, status)`.
- En base : `O_PROCESS` (les définitions, une ligne par version ; la version en vigueur a `ACTIVE_VERSION` à vrai), `O_PROCESS_EXECUTION` (les exécutions), `O_ACTIVITY_EXECUTION` (les exécutions de chaque activité) et `O_ACTIVITY_LOG` (leurs journaux).
- Par l'API REST, ou par l'[IHM embarquée](#ihm-embarquée).
<!-- source : OrchestraDefinitionManager.java:L42-49 ; ProcessReport.java:L36-75 ; OrchestraServicesImpl.java:L94-96, OrchestraFeatures.java:L113 (rapport en mode base de données) ; orchestra_create_init_v1.0.0.sql (tables) -->

### Cycle de vie d'une exécution

Une exécution de **processus** démarre dans l'état `RUNNING`, puis se termine en `DONE`, `ERROR` ou `ABORTED`. Chaque exécution d'**activité** passe par les états de l'enum `ExecutionState` :

| État | Description |
|---|---|
| `WAITING` | En attente d'un worker disponible |
| `RESERVED` | Réservée par un nœud |
| `SUBMITTED` | Soumise au pool de workers du nœud |
| `RUNNING` | En cours d'exécution |
| `DONE` | Terminée avec succès |
| `ERROR` | Terminée en erreur |
| `ABORTED` | Abandonnée : son nœud a été déclaré mort, ou a redémarré |
| `PENDING` | En attente de la fin d'un traitement délégué |

?> Une activité qui reste durablement en `WAITING` attend un worker libre : dimensionnez le paramètre `workersCount` selon le parallélisme attendu. À ne pas confondre avec une planification en attente, qui attend simplement son heure.
<!-- source : ExecutionState.java ; DbProcessExecutorPlugin.java:L438 (processus RUNNING), L487, L317 ; activityExecutionDAO.ksp:L39-45 ; coreDAO.ksp:L17-58 (ABORTED) ; DbProcessSchedulerPlugin.java:L227 -->

## Cas des évolutions des processus

Le principe général est qu'une définition de processus Orchestra est liée à du code : une activité, un service, etc. Ces définitions sont donc par nature stables dans le temps et ne changent pas à chaque démarrage.

En mode base de données, **c'est la définition enregistrée en base qui fait foi**. Au démarrage, `createOrUpdateDefinition` ne remplace une définition existante que si celle **de la base** a le drapeau `NEED_UPDATE` à vrai ; sinon, elle conserve celle de la base, avec son cron, ses activités et ses paramètres.

!> Piège courant : changer le cron (ou les activités) dans le code et redéployer ne change rien.

Trois façons de faire évoluer un processus :

- **Le code fait foi à chaque démarrage** : construire la définition avec `withNeedUpdate()`. Le drapeau est enregistré en base avec la définition : à chaque démarrage, la définition du code remplace celle de la base. En contrepartie, une modification faite par l'API ou par l'IHM est perdue au démarrage suivant.
- **Une mise à jour ponctuelle, au déploiement** : passer `NEED_UPDATE` à vrai en base, sur la ligne de la version en vigueur du processus (celle dont `ACTIVE_VERSION` est à vrai), en général par un script Liquibase de la livraison. Au démarrage suivant, la définition du code remplace celle de la base, puis le drapeau reprend la valeur du code.
- **Seulement le déclenchement ou les paramètres** : le déclenchement d'un processus n'est pas porté directement par la définition, mais par sa `ProcessTriggeringStrategy` (le cron, l'exécution multiple, la période de rattrapage, les paramètres initiaux). Il se modifie sans redéploiement par `orchestraDefinitionManager.updateProcessDefinitionProperties(processName, cronExpression, multiExecution, rescuePeriod, active)` (`cronExpression` est un `Optional<String>` : vide, il retire la planification par cron), et les paramètres initiaux par `orchestraDefinitionManager.updateProcessDefinitionInitialParams(processName, initialParams)` ; ou par l'API REST, ou par l'IHM.

Lorsqu'une définition est remplacée, l'ancienne version est désactivée (`ACTIVE_VERSION` à faux) : son historique d'exécutions est conservé. Le remplacement de la définition, comme `updateProcessDefinitionProperties`, purge les planifications futures du processus.

Il n'existe pas de suppression d'un processus : pour qu'il ne soit plus planifié, on le désactive : `active` à faux par `updateProcessDefinitionProperties`, ou une définition construite avec `inactive()`, qui ne s'applique à un processus déjà enregistré que par `withNeedUpdate()` ou `NEED_UPDATE` (voir plus haut). Un lancement manuel reste possible.

?> En mode mémoire, la définition du code remplace toujours la précédente, et elle ne peut pas être modifiée ensuite : `updateProcessDefinitionProperties` et `updateProcessDefinitionInitialParams` ne sont pas disponibles.
<!-- source : DbProcessDefinitionStorePlugin.java:L86 (NEED_UPDATE enregistré), L199-218 (drapeau lu sur la définition existante), L221-228 (désactivation, purge), L253 (purge par updateProcessDefinitionProperties) ; processDAO.ksp:L10-11 (version en vigueur), L52-63 ; OrchestraDefinitionManager.java:L78-86 ; MemoryProcessDefinitionStorePlugin.java:L43, L72, L77 -->

## Piloter Orchestra par webservices

La feature `orchestra.webapi` publie l'API REST d'Orchestra, sous le préfixe des webservices de l'application (le paramètre `apiPrefix` de `webservices.javalin`, par exemple `/api`). L'API ne crée ni ne supprime de définition : les définitions viennent du code.

| Route | Rôle |
|---|---|
| `GET /orchestra/definitions/{processName}` | Lire une définition |
| `POST /orchestra/definitions/_search` (corps : `criteria`) | Chercher des définitions par libellé |
| `PUT /orchestra/definitions/{processName}/properties` (corps : `cronExpression`, `multiExecution`, `rescuePeriod`, `active`) | Modifier le déclenchement |
| `PUT /orchestra/definitions/{processName}/params` (corps : `initialParams`) | Modifier les paramètres initiaux |
| `GET /orchestra/executions/?processName=&status=&limit=&offset=` | Lister les exécutions d'un processus |
| `GET /orchestra/executions/{preId}` | Lire une exécution |
| `GET /orchestra/executions/{preId}/activities` | Lister les exécutions des activités d'une exécution |
| `GET /orchestra/executions/{preId}/activities/{aceId}` | Lire l'exécution d'une activité |
| `GET /orchestra/executions/{preId}/logFile` | Télécharger le fichier joint d'une exécution (celui de l'activité terminée en dernier) |
| `GET /orchestra/executions/{preId}/activities/{aceId}/attachment` | Télécharger le fichier joint d'une activité |
| `GET /orchestra/executions/{preId}/activities/{aceId}/logFile` | Télécharger le journal d'une activité |
| `GET /orchestra/executions/summaries/{processName}` | Résumé de la semaine d'un processus |
| `GET /orchestra/executions/summaries?weekOffset=&status=` | Résumés de la semaine de tous les processus |
| `POST /orchestra/executionsControl/executeNow` (corps : `processName`) | Lancer une exécution immédiate |
| `POST /orchestra/executionsControl/execute` (corps : `processName`, `initialParams`) | Lancer une exécution immédiate, avec des paramètres |
| `POST /orchestra/executionsControl/onSuccess` (corps : `aceId`, `token`) | Signaler la fin, en succès, d'un traitement délégué (voir [Déléguer un traitement](#déléguer-un-traitement)) |
| `POST /orchestra/executionsControl/onError` (corps : `aceId`, `token`, `errorMessage`) | Signaler la fin, en erreur, d'un traitement délégué |
| `GET /orchestra/infos/status`, `GET /orchestra/infos/help` | Statut et aide du module |

Par exemple, pour lancer le processus `ProMyProcess` :

```http
POST /api/orchestra/executionsControl/executeNow
Content-Type: application/json

{ "processName": "ProMyProcess" }
```
<!-- source : WsDefinition.java:L41-102 ; WsExecution.java:L47-170 ; WsExecutionControl.java:L44-116 ; WsInfos.java:L34-81 ; JavalinWebServerPlugin.java (apiPrefix) ; DbProcessLoggerPlugin.java:L60-101 ; processExecutionDAO.ksp:L25-26 -->

!> Cette API permet de lancer et de modifier les processus : elle est réservée à l'administration de l'application et doit être protégée, par exemple avec le filtre [`AuthorizationWebFilter`](/basic/webservices#servlet-filters-vs-handlerchain) sur `/api/orchestra/*`, réservé à une autorisation d'administration. Si l'application délègue des traitements, les rappels `onSuccess` et `onError` du serveur distant doivent rester accessibles : excluez-les du filtre (paramètre `url-exclude-pattern`).
<!-- source : AuthorizationWebFilter.java ; AbstractFilter.java:L51 -->

## IHM embarquée

Le module embarque une IHM Vue.js (4 vues, libellés en français et en anglais), à intégrer dans une page [Vertigo-UI](/extensions/ui) : un controller et sa vue, dans le layout de l'application (voir dans cette page les sections « Controller : SpringMVC » et « Moteur de layout : Thymeleaf Layout »). Elle s'appuie sur l'API REST : la feature `orchestra.webapi` doit être active.

- Ses fichiers sont dans le jar, sous `io/vertigo/orchestra/static/` : `js/vertigo-orchestra-ui.umd.js` (les composants), `js/vertigo-orchestra-ui.js` (qui les installe dans l'application Vertigo-UI, à l'événement `vui-before-plugins`) et `css/vertigo-orchestra-ui.css`. Vertigo-UI ne sert que ses propres ressources (`/vertigo-ui/static/`) : l'application doit rendre ces fichiers accessibles, par exemple en les copiant dans les ressources statiques de sa webapp. L'exemple ci-dessous suppose les fichiers JavaScript copiés dans `static/js/orchestra/` et la feuille de style dans `static/css/orchestra/`.
- Le composant `vui-orchestra` affiche la liste des processus, puis le détail d'un processus : ses exécutions, ses activités et leurs journaux, ses réglages, et le lancement d'une exécution. Il reçoit `api-url`, l'adresse de l'API d'Orchestra (le préfixe des webservices suivi de `/orchestra`), et `read-only`.

```html
<head>
	<link rel="stylesheet" th:href="@{/static/css/orchestra/vertigo-orchestra-ui.css}">
	<script th:src="@{/static/js/orchestra/vertigo-orchestra-ui.js}"></script>
	<script th:src="@{/static/js/orchestra/vertigo-orchestra-ui.umd.js}"></script>
</head>
<body>
	<section layout:fragment="content">
		<vui-orchestra th:api-url="@{/api/orchestra}" :read-only="false"></vui-orchestra>
	</section>
</body>
```

!> `read-only` masque seulement les boutons de modification et de lancement : les webservices restent appelables. Si l'IHM est utilisée en production, l'accès à la page et à l'API doit être protégé côté serveur (voir [Piloter Orchestra par webservices](#piloter-orchestra-par-webservices)).
<!-- source : vertigo-orchestra/src/main/vuejs/src/main.js (composants), src/views/ (4 vues), src/lang/ (fr, en) ; views/VuOApp.vue:L16 (props apiUrl, readOnly) ; views/VuOProcess.vue:L58 (orchestraUiReadOnly) ; resources/io/vertigo/orchestra/static/ ; vuejs/README.md (« If used in production, you must protect access ») ; VSpringWebConfig.java:L341 -->

Autre option, retenue par Mars : construire ses propres écrans de suivi des processus (le module [`job`](https://github.com/vertigo-io/vertigo-mars/tree/master/src/main/java/io/mars/job) : liste des processus, détail, exécutions), avec Vertigo-UI, sur les requêtes de suivi d'Orchestra (les PAO du package `io.vertigo.orchestra.monitoring`).
<!-- source : vertigo-mars io/mars/job (JobServices, Job*Controller), views/job/*.html -->

## Pour les experts

### Managers et composants

| Composant | Nature | Rôle | Activé par |
|---|---|---|---|
| `ONodeManager` | Manager | Enregistrement des nœuds Orchestra et mise à jour de leur heartbeat | `orchestra.database` |
| `OrchestraDefinitionManager` | Manager | Gestion des définitions de processus | Toujours actif (`buildFeatures`) |
| `OrchestraServices` | Composant | Services principaux : exécution, planification, reporting, logging | Toujours actif (`buildFeatures`) |
<!-- source : ONodeManager.java:L28, OrchestraDefinitionManager.java:L32 (extends Manager) ; OrchestraServices.java:L32 (extends Component) -->

### Services

| Service | Accès | Description |
|---|---|---|
| `ProcessExecutor` | `orchestraServices.getExecutor()` | Exécution des processus (séquentielle, workspace partagé) |
| `ProcessScheduler` | `orchestraServices.getScheduler()` | Planification Cron et exécutions ponctuelles |
| `ProcessReport` | `orchestraServices.getReport()` | Rapports d'exécution (historique, statistiques) |
| `ProcessLogger` | `orchestraServices.getLogger()` | Accès aux journaux et aux fichiers joints des exécutions |
<!-- source : OrchestraServices.java:L37-54 -->

### Plugins

| Plugin Interface | Implémentations | Activé par |
|---|---|---|
| `ProcessDefinitionStorePlugin` | `DbProcessDefinitionStorePlugin`, `MemoryProcessDefinitionStorePlugin` | `orchestra.database` / `orchestra.memory` |
| `ProcessExecutorPlugin` | `DbProcessExecutorPlugin`, `MemoryProcessExecutorPlugin` | `orchestra.database` / `orchestra.memory` |
| `ProcessSchedulerPlugin` | `DbProcessSchedulerPlugin`, `MemoryProcessSchedulerPlugin` | `orchestra.database` / `orchestra.memory` |
| `ProcessReportPlugin` | `DbProcessReportPlugin` | `orchestra.database` |
| `ProcessLoggerPlugin` | `DbProcessLoggerPlugin` | `orchestra.database` |

### Daemon Orchestra

?> Le daemon `DmnODbProcessExecutorDaemon` (période : `daemonPeriodSeconds`) met à jour le heartbeat des nœuds Orchestra, c'est-à-dire le signal par lequel chaque nœud indique qu'il est vivant. Un nœud dont le heartbeat n'a pas été mis à jour depuis plus de 2 × `daemonPeriodSeconds` est déclaré mort. Ce daemon s'exécute dans le pool de daemons de la plateforme, partagé avec les autres daemons de l'application : si des daemons longs occupent tous les threads de ce pool, le heartbeat peut être retardé et provoquer une détection de nœud mort. Vérifiez la durée d'exécution de vos daemons via le dashboard analytics. Certains logs Orchestra précisent l'identifiant du nœud, celui de l'exécution d'activité et l'état.
<!-- source : DbProcessExecutorPlugin.java:L149, L171, L506-507, L694 ; DaemonManagerImpl.java:L53, L193, L204 -->

### Planificateur : classes internes

| Classe | Rôle |
|---|---|
| `CronExpression` | Parsing et évaluation d'expressions Cron |
| `BasicTimerTask` | Tâche timer basique pour planification (mode mémoire) |
| `ReschedulerTimerTask` | Tâche timer avec re-planification automatique (mode mémoire) |

### Modèle Domain (DtObjects)

| DtObject | Description |
|---|---|
| `OProcess` | Définition du processus |
| `OActivity` | Définition d'une activité |
| `OProcessExecution` | Instance d'exécution de processus |
| `OActivityExecution` | Instance d'exécution d'activité |
| `OActivityLog` | Log d'activité |
| `OActivityWorkspace` | Workspace d'entrée ou de sortie d'une exécution d'activité |
| `ONode` | Nœud Orchestra |
| `OProcessPlanification` | Planification de processus |
| `OExecutionState` | État d'exécution |
| `OSchedulerState` | État du scheduler |
| `OProcessType` | Table technique, qui sert de verrou lors de l'enregistrement des définitions (le type d'un processus est l'enum Java `ProcessType`) |
| `OUser` | Utilisateur Orchestra |
<!-- source : orchestra_create_init_v1.0.0.sql (o_process_type : 'DUMB') ; processDAO.ksp:L19-26 (TkLockProcessesForInsert) ; ProcessType.java -->

### Features (@Feature)

| Flag | Paramètres (obligatoires) | Composants ajoutés |
|---|---|---|
| `orchestra.database` | `nodeName`, `daemonPeriodSeconds`, `workersCount`, `forecastDurationSeconds` | ONodeManager, 8 DAOs, 6 PAOs, 5 plugins DB, ModelDefinitionProvider |
| `orchestra.memory` | `workersCount` | 3 plugins mémoire (store, scheduler, executor) |
| `orchestra.webapi` | — | WsDefinition, WsExecution, WsExecutionControl, WsInfos |
