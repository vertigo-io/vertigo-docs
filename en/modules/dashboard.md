# Dashboard module

**Dashboard** is a Vertigo module dedicated to application monitoring and observability.

In the Project Management domain, it allows visualizing the health status and performance of a project tracking application, with a retrospective history fed by InfluxDB.

The module exposes a REST API for monitoring data and a web interface based on FreeMarker, mounted directly on the application's Javalin server.

The architecture relies on three layers:

1. **DataProvider**: abstraction for real-time queries on time series, health checks, metrics, and tabular data
2. **Business controllers**: four sub-modules covering platform components
3. **DashboardRouter**: HTTP routes + FreeMarker mounted on Javalin

## Components

| Component | Type | Role |
|---|---|---|
| `DataProvider` | Interface | Contract for real-time queries (series, health, metrics, tabular) |
| `DataProviderImpl` | Implementation | Delegates to `TimeSeriesManager` (InfluxDB), isolated by `@ParamValue("appName")` |
| `DashboardDataProviderWebServices` | Vega WebServices | REST API under `/dashboard/data` |
| `DashboardUiManager` | Manager / Activeable | Mounts `DashboardRouter` on Javalin at startup |
| `DashboardRouter` | Class | HTTP routes + FreeMarker, hardcoded `/dashboard/` prefix |
| `AbstractDashboardModuleControler` | Abstract | Template method for sub-module controllers |

## Architecture

### DataProvider layer

The `DataProvider` interface defines the contract for data queries: time series, health checks, metrics, and tabular data.

`DataProviderImpl` delegates to `TimeSeriesManager` (vertigo-influxdb-connector) for time series queries. Data scope is isolated by application via `@ParamValue("appName")`, with default value `Node.getNode().getNodeConfig().appName()`.

### REST API

`DashboardDataProviderWebServices` exposes endpoints with `@PathPrefix("/dashboard/data")`.

All endpoints are annotated `@SessionLess`, `@AnonymousAccessAllowed`, and receive their parameters in JSON body via `@InnerBodyParam`.

| Endpoint | Annotation | Signature |
|----------|-----------|-----------|
| `/dashboard/data/series` | `@POST("/series")` | `getTimedDatas(measures, dataFilter, timeFilter) → TimedDatas` |
| `/dashboard/data/series/clustered` | `@POST("/series/clustered")` | `getClusteredTimedDatas(clusteredMeasure, dataFilter, timeFilter) → TimedDatas` |
| `/dashboard/data/tabular` | `@POST("/tabular")` | `getTabularDatas(measures, dataFilter, timeFilter, groupBy) → TabularDatas` |
| `/dashboard/data/tabular/tops` | `@POST("/tabular/tops")` | `getTops(measures, dataFilter, timeFilter, groupBy, maxRows) → TabularDatas` |

These endpoints are Vega web services. They are not accessible as injectable components via `appSpace.getComponent()`.

### Web interface

`DashboardUiManager` is a Manager implementing `Activeable`. At startup, it mounts `DashboardRouter` on the application's Javalin server.

`DashboardRouter` defines HTTP routes and the FreeMarker engine. Routes are hardcoded with the `/dashboard/...` prefix. This prefix is not configurable.

#### Template Method

Sub-module controllers extend `AbstractDashboardModuleControler`, which implements the Template Method pattern:

- `Map<String, Object> buildModel(Node node, String moduleName)` — builds and returns the FreeMarker context Map
- `void doBuildModel(Node node, Map<String, Object> model)` — method to override, returns **void**, populates the Map passed as parameter

Common initialization in `buildModel` prepares the Map with modules, localizations, features, and the `healthchecksByFeature` map of type `Map<String, List<HealthCheck>>`, then calls `doBuildModel` for sub-module-specific enrichment.

## Installation

### Maven dependency

```xml
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-dashboard</artifactId>
    <version>4.3.2</version>
</dependency>
```

Mandatory dependencies:

- `vertigo-vega`
- `vertigo-influxdb-connector`
- `vertigo-redis-connector`

Transitive dependencies used by code:

- `vertigo-core`
- `vertigo-commons`
- `vertigo-datastore`

### Configuration

Activate the dashboard via `DashboardFeatures.withAnalytics(appName)` in the application configuration:

```yaml
io.vertigo.dashboard.DashboardFeatures:
    withAnalytics:
        - project-management
```

The call `withAnalytics(appName)` activates the DataProvider and associated web services. There is no parameter to modify the `/dashboard/` route prefix, nor `featuresConfig` for the web interface.

## Examples

### Activating the dashboard

In a Project Management application:

```java
DashboardFeatures.withAnalytics("project-management");
```

### REST access

```http
POST /dashboard/data/series
Content-Type: application/json

{
  "measures": ["taskExecutionCount"],
  "dataFilter": {"appName": "project-management"},
  "timeFilter": {"startTime": -86400000, "endTime": 0}
}
```

### UI access

Pages are accessible from `/dashboard/`. No prefix customization is possible.

### UI sub-modules

Each sub-module has a dedicated controller:

| Module | Controller | Exposed data |
|---|---|---|
| vertigo-commons | `CommonsDashboardControler` | Daemons (`DaemonModel`, `isLastExecSuccess()`), EventBus (`EventBusModel`), Caches (`CacheModel`, TTL, capacity, health green/yellow/red) |
| vertigo-datamodel | `DynamoDashboardControler` | Entities (`EntityModel`), SmartTypes (`SmartTypeModel`, `isOrphan()`), Tasks (`TaskModel`, `medianDuration` over 24h) |
| vertigo-vega | `VegaDashboardControler` | Web service locations (`getTagValues("webservices", "location")`) |
| vertigo-ui | `VUiDashboardControler` | Page locations (`getTagValues("page", "location")`) |

## Retrospective health checks

The module reconstructs health checks for the last five weeks from time series stored in InfluxDB. Aggregation is done by feature.

Each `HealthCheck` is composed of: `name`, `checker`, `module`, `feature`, `time`, and `HealthMeasure`.

`HealthMeasure` contains the status and associated message.

The `healthchecksByFeature` map produces a `Map<String, List<HealthCheck>>` accessible in the FreeMarker model.

## Templates and assets

### FreeMarker

- `page.ftl`: base template, HTML structure and static asset inclusion
- `home.ftl`: home page, maps the four sub-modules
- `module_macros.ftl`: common macros for data display
- `vertigo-commons.ftl`, `vertigo-dynamo.ftl`, `vertigo-vega.ftl`, `vertigo-ui.ftl` (in `templates/` without subdirectories)

### Static assets

- `dashboard.css`: interface styles
- `dashboard.js`: client-side logic
- `dashboard.datatable.js`: data table management
- `dashboard.chartjs.js`: Chart.js integration for charts

## Cautions

- Routes `/dashboard/...` are hardcoded in `DashboardRouter`. No `prefix` parameter exists for customization.
- `doBuildModel()` returns `void`. It's `buildModel()` that returns `Map<String, Object>`.
- Web services `DashboardDataProviderWebServices` are Vega endpoints. They are not injectable via `appSpace.getComponent()`.

## For Experts

### Managers
| Manager | Role | Activated by |
|---|---|---|
| `DataProvider` | Real-time query on time series, health checks, metrics, and tabular data | `analytics` |
| `DashboardUiManager` | Mounts `DashboardRouter` on Javalin server | Always active (buildFeatures) |

### Internal components
| Component | Role |
|---|---|
| `DataProviderImpl` | Implementation delegating to `TimeSeriesManager` (InfluxDB) |
| `DashboardDataProviderWebServices` | REST API under `/dashboard/data` (4 endpoints) |
| `DashboardRouter` | HTTP routes + FreeMarker, hardcoded `/dashboard/` prefix |
| `AbstractDashboardModuleControler` | Template Method for sub-module controllers |
| `CommonsDashboardControler` | vertigo-commons sub-module (Daemons, EventBus, Caches) |
| `DynamoDashboardControler` | vertigo-dynamo sub-module (Entities, SmartTypes, Tasks) |
| `VegaDashboardControler` | vertigo-vega sub-module (Web service locations) |
| `VUiDashboardControler` | vertigo-ui sub-module (Page locations) |

### Features (@Feature)
| Flag | Components |
|---|---|
| `analytics` | `DataProvider` + `DataProviderImpl`, `DashboardDataProviderWebServices` |

### Plugins
No plugins. Components are internal to the module.

### Configuration YAML
```yaml
modules:
    io.vertigo.dashboard.DashboardFeatures:
        features:
            - analytics:
                appName: "project-management"
```