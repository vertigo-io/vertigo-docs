# Module dashboard

**Dashboard** est un module Vertigo dédié au monitoring et à l'observabilité des applications.

Dans le domaine de la Gestion de Projet, il permet de visualiser l'état de santé et les performances d'une application de suivi de projets, avec un historique rétrospectif alimenté par InfluxDB.

Le module expose une API REST pour les données de monitoring et une interface web basée sur FreeMarker, montée directement sur le serveur Javalin de l'application.

L'architecture repose sur trois couches :

1. **DataProvider** : abstraction de requête temps réel sur les séries temporelles, health checks, métriques et données tabulaires
2. **Contrôleurs métier** : quatre sous-modules couvrant les composants du framework
3. **DashboardRouter** : routes HTTP + FreeMarker montées sur Javalin

## Composants

| Composant | Type | Rôle |
|---|---|---|
| `DataProvider` | Interface | Contrat pour les requêtes temps réel (séries, health, métriques, tabulaires) |
| `DataProviderImpl` | Implémentation | Délègue à `TimeSeriesManager` (InfluxDB), isolé par `@ParamValue("appName")` |
| `DashboardDataProviderWebServices` | WebServices Vega | API REST sous `/dashboard/data` |
| `DashboardUiManager` | Manager / Activeable | Monte `DashboardRouter` sur Javalin au démarrage |
| `DashboardRouter` | Class | Routes HTTP + FreeMarker, préfixe `/dashboard/` en dur |
| `AbstractDashboardModuleControler` | Abstract | Template method pour les contrôleurs de sous-module |

## Architecture

### Couche DataProvider

L'interface `DataProvider` définit le contrat pour les requêtes de données : séries temporelles, health checks, métriques et données tabulaires.

`DataProviderImpl` délègue à `TimeSeriesManager` (vertigo-influxdb-connector) pour les requêtes séries temporelles. Le scope des données est isolé par application via `@ParamValue("appName")`, avec la valeur par défaut `Node.getNode().getNodeConfig().appName()`.

### API REST

`DashboardDataProviderWebServices` expose les endpoints avec `@PathPrefix("/dashboard/data")`.

Tous les endpoints sont annotés `@SessionLess`, `@AnonymousAccessAllowed`, et reçoivent leurs paramètres en corps JSON via `@InnerBodyParam`.

| Endpoint | Annotation | Signature |
|----------|-----------|-----------|
| `/dashboard/data/series` | `@POST("/series")` | `getTimedDatas(measures, dataFilter, timeFilter) → TimedDatas` |
| `/dashboard/data/series/clustered` | `@POST("/series/clustered")` | `getClusteredTimedDatas(clusteredMeasure, dataFilter, timeFilter) → TimedDatas` |
| `/dashboard/data/tabular` | `@POST("/tabular")` | `getTabularDatas(measures, dataFilter, timeFilter, groupBy) → TabularDatas` |
| `/dashboard/data/tabular/tops` | `@POST("/tabular/tops")` | `getTops(measures, dataFilter, timeFilter, groupBy, maxRows) → TabularDatas` |

Ces endpoints sont des web services Vega. Ils ne sont pas accessibles comme composants injectables via `appSpace.getComponent()`.

### Interface web

`DashboardUiManager` est un Manager implémentant `Activeable`. Au démarrage, il monte `DashboardRouter` sur le serveur Javalin de l'application.

`DashboardRouter` définit les routes HTTP et le moteur FreeMarker. Les routes sont codées en dur avec le préfixe `/dashboard/...`. Ce préfixe n'est pas paramétrable.

#### Template Method

Les contrôleurs de sous-module héritent de `AbstractDashboardModuleControler`, qui implémente le patron Template Method :

- `Map<String, Object> buildModel(Node node, String moduleName)` — construit et retourne la Map du contexte FreeMarker
- `void doBuildModel(Node node, Map<String, Object> model)` — méthode à surcharger, retourne **void**, peuple la Map passée en paramètre

L'initialisation commune dans `buildModel` prépare la Map avec les modules, localisations, features et la carte `healthchecksByFeature` de type `Map<String, List<HealthCheck>>`, puis appelle `doBuildModel` pour l'enrichissement spécifique à chaque sous-module.

## Installation

### Dépendance Maven

```xml
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-dashboard</artifactId>
    <version>4.3.2</version>
</dependency>
```

Dépendances obligatoires :

- `vertigo-vega`
- `vertigo-influxdb-connector`
- `vertigo-redis-connector`

Dépendances transitives utilisées par le code :

- `vertigo-core`
- `vertigo-commons`
- `vertigo-datastore`
- `vertigo-dynamo`

### Configuration

Activer le dashboard via `DashboardFeatures.withAnalytics(appName)` dans la configuration de l'application :

```yaml
io.vertigo.dashboard.DashboardFeatures:
    withAnalytics:
        - gestion-projet
```

L'appel `withAnalytics(appName)` active le DataProvider et les web services associés. Il n'existe pas de paramètre pour modifier le préfixe `/dashboard/` des routes, ni de configuration `featuresConfig` pour l'interface web.

## Exemples

### Activation du dashboard

Dans une application de Gestion de Projet :

```java
DashboardFeatures.withAnalytics("gestion-projet");
```

### Accès REST

```http
POST /dashboard/data/series
Content-Type: application/json

{
  "measures": ["taskExecutionCount"],
  "dataFilter": {"appName": "gestion-projet"},
  "timeFilter": {"startTime": -86400000, "endTime": 0}
}
```

### Accès UI

Les pages sont accessibles à partir de `/dashboard/`. Aucune customisation du préfixe n'est possible.

### Sous-modules UI

Chaque sous-module a un contrôleur dédié :

| Module | Contrôleur | Données exposées |
|---|---|---|
| vertigo-commons | `CommonsDashboardControler` | Daemons (`DaemonModel`, `isLastExecSuccess()`), EventBus (`EventBusModel`), Caches (`CacheModel`, TTL, capacité, health vert/yellow/red) |
| vertigo-dynamo | `DynamoDashboardControler` | Entities (`EntityModel`), SmartTypes (`SmartTypeModel`, `isOrphan()`), Tasks (`TaskModel`, `medianDuration` sur 24h) |
| vertigo-vega | `VegaDashboardControler` | Locations webservices (`getTagValues("webservices", "location")`) |
| vertigo-ui | `VUiDashboardControler` | Locations pages (`getTagValues("page", "location")`) |

## Health checks rétrospectifs

Le module reconstruit les health checks des cinq dernières semaines à partir des séries temporelles stockées dans InfluxDB. L'agrégation se fait par feature.

Chaque `HealthCheck` est composé de : `name`, `checker`, `module`, `feature`, `time`, et `HealthMeasure`.

`HealthMeasure` contient le statut et le message associé.

La carte `healthchecksByFeature` produit un `Map<String, List<HealthCheck>>` accessible dans le modèle FreeMarker.

## Templates et assets

### FreeMarker

- `page.ftl` : template de base, structure HTML et inclusion des assets statiques
- `home.ftl` : page d'accueil, mappe les quatre sous-modules
- `module_macros.ftl` : macros communes pour l'affichage des données
- `vertigo-commons.ftl`, `vertigo-dynamo.ftl`, `vertigo-vega.ftl`, `vertigo-ui.ftl` (dans `templates/` sans sous-répertoires)

### Assets statiques

- `dashboard.css` : styles de l'interface
- `dashboard.js` : logique côté client
- `dashboard.datatable.js` : gestion des tableaux de données
- `dashboard.chartjs.js` : intégration Chart.js pour les graphiques

## Vigilance

- Les routes `/dashboard/...` sont codées en dur dans `DashboardRouter`. Aucun paramètre `prefix` n'existe pour les personnaliser.
- `doBuildModel()` retourne `void`. C'est `buildModel()` qui retourne `Map<String, Object>`.
- Les web services `DashboardDataProviderWebServices` sont des endpoints Vega. Ils ne sont pas injectables via `appSpace.getComponent()`.
