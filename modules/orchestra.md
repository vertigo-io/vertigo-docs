# Orchestra

**Orchestra** est un module de la plateforme Vertigo permettant la gestion des jobs et des batchs.

Il permet à la fois de programmer et lancer des processus avec une stratégie prédéfinie et de fournir une API pour les configurer et les superviser.

Il inclut de nombreuses fonctionnalités :

- Support natif du multi-nœud avec gestion de la charge
- Détection des nœuds morts
- Récupération des planifications ratées
- Logging (Fichier + DB) (Un humain peut facilement y accéder, y compris via une IHM)
- Délégation du traitement asynchrone à un autre serveur / une autre application

## Qu'est-ce qu'un processus dans Orchestra ?

- Un processus est une liste séquentielle d'activités
- Un processus peut être programmé dans le temps via diverses stratégies

## Donc qu'est-ce qu'une activité dans Orchestra ?

- Une activité est l'unité d'exécution. C'est elle qui contient le code qui doit être exécuté.
- Une activité gère la suite à donner au processus
- Toutes les activités d'un processus partagent un environnement commun d'exécution appelé workspace

## Comment l'utiliser ?

Orchestra offre les fonctionnalités suivantes :
- Une API de gestion des processus
- Deux implémentations pour la gestion des exécutions
  - Base de données avec gestion des logs, du monitoring et du multi-nœud (seul PostgreSQL est actuellement supporté)
  - Mémoire
- Une API REST pour gérer les processus, les exécutions, la planification et la supervision

Lorsque le module Orchestra est ajouté à votre application, il est possible de l'utiliser en mode intégré ou comme un nœud standalone dans une architecture micro-services.

La configuration YAML pour Orchestra en mode base de données est la suivante :

```yaml
io.vertigo.orchestra.OrchestraFeatures:
    features:
        - orchestra.database:
              nodeName: NODE_ID
              daemonPeriodSeconds: 30
              workersCount: 10
              forecastDurationSeconds: 60
        - orchestra.webapi:
```

Pour utiliser Orchestra en version base de données, il est nécessaire d'initialiser cette base (création des tables et insertion des données primaires).

## A quoi cela ressemble-t-il dans le code ?

### Ecrire un ActivityEngine

Nous avons vu qu'une activité contenait le code source à exécuter. Plus en détails, ce code est contenu dans un *ActivityEngine* qui est une interface que doivent implémenter les ActivityEngines.

La classe abstraite **AbstractActivityEngine** implémente *ActivityEngine* et ajoute le code nécessaire pour gérer les logs et d'autres services.

> Il est préférable d'étendre cette classe abstraite pour construire son *Engine*.

Votre premier *ActivityEngine* que nous nommerons *MyFirstActivityEngine* ressemblera à

```java
package io.vertigo.orchestra.execution.engine;

import io.vertigo.orchestra.impl.services.execution.AbstractActivityEngine;
import io.vertigo.orchestra.services.execution.ActivityExecutionWorkspace;

public class MyFirstActivityEngine extends AbstractActivityEngine {

	/** {@inheritDoc} */
	@Override
	public ActivityExecutionWorkspace execute(final ActivityExecutionWorkspace workspace) {
		return workspace;
	}

}
```

Pour gérer le statut de retour en fin d'activité, il suffit de modifier l'état du workspace avant de le retourner.
Par exemple, pour déclarer que l'activité se termine par un succès :

```java
/** {@inheritDoc} */
@Override
public ActivityExecutionWorkspace execute(final ActivityExecutionWorkspace workspace) {
    workspace.setSuccess();
	return workspace;
}
```

Si une activité se termine par un succès alors l'activité suivante du processus est lancée. Le workspace de sortie de la précédente activité est utilisé comme paramètre d'entrée de la nouvelle activité. Il s'agit du mécanisme permettant le partage de données entre activités.

> Lorsque vous écrivez une activité, gardez bien à l'esprit de la rendre réutilisable car un processus n'est ni plus ni moins qu'un arrangement d'activités.

Maintenant que nous avons un ActivityEngine, nous allons l'associer à notre premier processus.

### Définir un nouveau processus

Pour créer un nouveau processus, nous devons créer une nouvelle `ProcessDefinition`.
Pour construire une `ProcessDefinition`, il est nécessaire d'utiliser la classe `ProcessDefinitionBuilder`.

Voici notre première ProcessDefinition :

```java
final ProcessDefinition myFirstProcessDefinition = new ProcessDefinitionBuilder("MY_FIRST_ONE", "My first process")
				.addActivity("ACTIVITY", "First activity", MyFirstActivityEngine.class)
				.build();
```

On peut remarquer que notre premier processus possède une unique activité qui utilise l'engine *MyFirstActivityEngine*.

A l'aide du builder, il est très aisé de configurer son processus (pour les différentes options, voir la Javadoc).
Une des options importantes est la possibilité de planifier l'exécution d'un processus via une Expression Cron.

Une fois la définition créée, il faut l'enregistrer. Pour ce faire, il suffit d'appeler la méthode adéquate du composant `OrchestraDefinitionManager` (vous pouvez l'injecter dans votre composant pour le récupérer).

```java
orchestraDefinitionManager.createOrUpdateDefinition(myFirstProcessDefinition);
```

La définition enregistrée, il est dès lors possible de l'utiliser via les services offerts par la classe `OrchestraServices` :
- Superviser les exécutions
- Planifier de nouvelles exécutions

!> L'exécution est toujours lancée via le *scheduler*. Si vous souhaitez lancer une exécution de manière immédiate, il suffit d'utiliser la méthode `scheduleAt` du `ProcessScheduler` avec comme date `Instant.now()`

Par exemple :

```java
orchestraServices.getScheduler().scheduleAt(myFirstProcessDefinition, Instant.now(), Collections.emptyMap());
orchestraServices.getReport().getSummaryByDate(myFirstProcessDefinition,
		LocalDate.of(2017, 1, 1), LocalDate.of(2017, 12, 31));
```

## Cas des évolutions des processus

Le principe général est qu'une définition de processus Orchestra est liée à du code : une activité, un service, etc. Ces définitions sont donc par nature stables dans le temps et ne changent pas à chaque démarrage.
Par défaut, la définition est conservée en base de données. Lorsqu'il est nécessaire de mettre à jour une nouvelle version du processus, on doit inclure dans la procédure de déploiement une mise à jour de la définition dans la base de données
avec needUpdate=true (en général, cela est réalisé par un script liquibase). Avec ce paramètre, au démarrage le système mettra à jour la définition dans la base à partir de la définition dans le code.

Pour une modification du paramétrage du déclenchement, ce n'est pas directement dans la définition mais dans la "ProcessTriggeringStrategy".
Ces informations sont modifiables avec l'API (updateProcessProperties), et certaines IHM proposent de modifier le cron directement par l'interface utilisateur.

## Pour les experts

### Managers

| Manager | Rôle | Activé par |
|---|---|---|
| `ONodeManager` | Gestion des nœuds Orchestra (détection nœuds morts, charge) | `orchestra.database` |
| `OrchestraDefinitionManager` | Gestion des définitions de processus | Toujours actif (`buildFeatures`) |
| `OrchestraServices` | Services principaux : exécution, planification, reporting, logging | Toujours actif (`buildFeatures`) |

### Services

| Service | Interface | Description |
|---|---|---|
| `ProcessExecutor` | `ProcessExecutor` | Exécution des processus (séquentielle, workspace partagé) |
| `ProcessScheduler` | `ProcessScheduler` | Planification Cron et exécutions ponctuelles |
| `ProcessReport` | `ProcessReport` | Rapports d'exécution (historique, statistiques) |
| `ProcessLogger` | `ProcessLogger` | Journalisation des exécutions et activités |

### Plugins

| Plugin Interface | Implémentations | Activé par |
|---|---|---|
| `ProcessDefinitionStorePlugin` | `DbProcessDefinitionStorePlugin`, `MemoryProcessDefinitionStorePlugin` | `orchestra.database` / `orchestra.memory` |
| `ProcessExecutorPlugin` | `DbProcessExecutorPlugin`, `MemoryProcessExecutorPlugin` | `orchestra.database` / `orchestra.memory` |
| `ProcessSchedulerPlugin` | `DbProcessSchedulerPlugin`, `MemoryProcessSchedulerPlugin` | `orchestra.database` / `orchestra.memory` |
| `ProcessReportPlugin` | `DbProcessReportPlugin` | `orchestra.database` |
| `ProcessLoggerPlugin` | `DbProcessLoggerPlugin` | `orchestra.database` |

### Scheduler Internals

| Classe | Rôle |
|---|---|
| `CronExpression` | Parsing et évaluation d'expressions Cron |
| `BasicTimerTask` | Tâche timer basique pour planification |
| `ReschedulerTimerTask` | Tâche timer avec re-planification automatique |

### WebServices API (REST)

| WebService | Description |
|---|---|
| `WsDefinition` | CRUD des définitions de processus |
| `WsExecution` | Lancement et suivi des exécutions |
| `WsExecutionControl` | Contrôle des exécutions (stop, restart) |
| `WsInfos` | Informations de supervision / monitoring |

### Modèle Domain (DtObjects)

| DtObject | Description |
|---|---|
| `OProcess` | Définition du processus |
| `OActivity` | Définition d'une activité |
| `OProcessExecution` | Instance d'exécution de processus |
| `OActivityExecution` | Instance d'exécution d'activité |
| `OActivityLog` | Log d'activité |
| `OActivityWorkspace` | Espace de travail partagé entre activités |
| `ONode` | Nœud Orchestra |
| `OProcessPlanification` | Planification de processus |
| `OExecutionState` | État d'exécution |
| `OSchedulerState` | État du scheduler |
| `OProcessType` | Type de processus (SUPERVISED, UNSUPERVISED) |
| `OUser` | Utilisateur Orchestra |

### Features (@Feature)

| Flag | Paramètres | Composants ajoutés |
|---|---|---|
| `orchestra.database` | `nodeName`, `daemonPeriodSeconds`, `workersCount`, `forecastDurationSeconds` | ONodeManager, 8 DAOs, 6 PAOs, 5 plugins DB, ModelDefinitionProvider |
| `orchestra.memory` | `workersCount` | 3 plugins mémoire (store, scheduler, executor) |
| `orchestra.webapi` | — | WsDefinition, WsExecution, WsExecutionControl, WsInfos |

### Configuration YAML

```yaml
io.vertigo.orchestra.OrchestraFeatures:
    features:
        - orchestra.database:
              nodeName: NODE_ID
              daemonPeriodSeconds: 30
              workersCount: 10
              forecastDurationSeconds: 60
        - orchestra.webapi:
```
