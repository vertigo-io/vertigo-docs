# Planning module

## Features

The Vertigo platform planning module is a functional vertical for managing, organizing calendars, and making appointments.

Functional administrators propose time slots that can then be booked by users.
Time slot management is designed to be set-based. It is simplified by a calendar presentation and primarily manipulates time periods.
A time period is a defined period of the day, composed of time slots of identical duration, offered by a defined number of counters.
Management uses a simple publication status to propose fixed-time slots.

FrontOffice users can view and choose a time slot from the list of available slots.

Integrating this module into the business application allows managing various use cases:

- Managing appointments opened by a service for administrative procedures.
- Managing appointments opened by an agent for users; booking can be undifferentiated or not.

## Strengths

Supports very high consultation load and significant contention on reservations.
Used on a site with very high traffic. Some calendars have few available slots, which are booked within minutes.

## Installing the planning module

### Adding the module to pom.xml

```xml
<dependency>
   <groupId>io.vertigo</groupId>
   <artifactId>vertigo-planning</artifactId>
   <version>4.3.2</version>
</dependency>
```

## Adding to Vertigo configuration

You need to add `PlanningFeatures` and `AgendaFeatures` features.
The `services.config` entry allows modifying the default configuration of the `PlanningServices` service (see below).
The `foConsultation` plugin used on the FrontOffice side exists in database and Redis versions.

```yaml
io.vertigo.planning.PlanningFeatures:
io.vertigo.planning.agenda.AgendaFeatures:
    featuresConfig:
        - services.config:
        - foConsultation.db:
              __flags__: ["!redis"]
        - foConsultation.redis2Unified:
            __flags__: ["redis && redisCluster"]
```

> The configuration allows distributed synchronization.
> For this, you need a WorkEngine in Stella and add the task to redis2Unified:

```yaml
io.vertigo.stella.StellaFeatures:
    __flags__: ["redis"]
    features:
        - master:
              nodeId: ${STELLA_NODE_NAME}
        - worker:
              workersCount: 1
              nodeId: ${STELLA_NODE_NAME}
              workTypes: io.vertigo.planning.agenda.services.fo.plugin.WorkEngineSynchroDbRedisCreneau^1
    featuresConfig:
        - master.redis:
        - worker.redis:
io.vertigo.planning.PlanningFeatures:
io.vertigo.planning.agenda.AgendaFeatures:
    featuresConfig:
        - foConsultation.redis2Unified:
              distributedSynchro: true
```

### Adding to the model

In your modeling, you need to reference the agenda from one of your business objects.

```
create Association AMyBusinessObjectAgenda {
   fkFieldName : "ageId"

   dtDefinitionA : DtMyBusinessObject
   type : "*>1"
   dtDefinitionB : DtAgenda

   labelB : "Agenda"
}
```

For DtAgenda to be recognized, you also need to add it to the module's KPR during Studio generation.
Example in `studio-config.yaml`:

```yaml
resources:
   - { type: kpr, path: classpath:io/vertigo/planning/studio/agenda/export_agenda.kpr }
```

### Adding resource messages

In your UI configuration, add the resource to the `MessageSource`:

```java
public static MessageSource getMessageSource() {
    final ResourceBundleMessageSource customMessageSource = new ResourceBundleMessageSource();
    customMessageSource.addBasenames("io/vertigo/ui/components/planning/planning");
    return customMessageSource;
}
```

## Usage in pages

### For BackOffice

__CSS additions__

```html
<head>
    ...
    <link th:href="@{/vertigo-ui/static/planning/css/vertigo-planning.css}" rel="stylesheet" type="text/css">
    <link th:href="@{/vertigo-ui/static/3rdParty/cdn.jsdelivr.net/npm/@quasar/quasar-ui-qcalendar@4.1.2/index.min.css}" rel="stylesheet" type="text/css">
</head>
```

__Note:__ Quasar CSS is required for the calendar.

__JavaScript additions__

```javascript
<section layout:fragment="additional-librairies">
    <script th:src="@{/vertigo-ui/static/3rdParty/cdn.jsdelivr.net/npm/@quasar/quasar-ui-qcalendar@4.1.2/QCalendarDay.umd.min.js}"></script>
    <script th:src="@{/vertigo-ui/static/planning/js/vertigo-planning.js?t=__${appBuildTime}__}"></script>
</section>
```

#### VertigoUi Components

- `agenda-week`: Full calendar component, place it full page
  - `agenda_actions_slot`: Component buttons slot (default: create period, duplicate week, publication)
  - `eventNameTwoLetters`: 2 letters in the period (default: false)
  - `eventIconAgenda`: Icon in the period (default: `event`)
  - `multiEventIconAgenda`: Multiple agenda icon in the period (default: `calendar_month`)
  - `maxMultiEventShow`: Maximum number of agendas shown before list (default: 3)
  - `hasAuthzAdmin`: If agenda admin rights (default: true)

- `agenda-create-plage`: Time period creation modal component
  - `plage_actions_slot`: Component buttons slot (default: create if counter, create if personal agenda)

- `agenda-detail-plage`: Time period detail modal component
  - `plage_actions_slot`: Component buttons slot (default: none)

- `agenda-delete-plage`: Time period deletion confirmation modal component
  - `plage_actions_slot`: Component buttons slot (default: cancel, deletePlageHoraire)

- `agenda-duplicate-week`: Week duplication modal component
  - `plage_actions_slot`: Component buttons slot (default: duplicate week)

- `agenda-publish-plage`: Time period publication modal component
  - `plage_actions_slot`: Component buttons slot (default: cancel, publishPlageHoraires)

__Example__

```html
<vu:agenda-week eventIconAgenda="ri-folder-fill" hasAuthzAdmin="${authz.hasAuthorization('Project$personalAgenda')}">
    <vu:slot name="agenda_actions_slot">
        <vu:button icon="ri-add-line" label="#{project.bo.project.agenda.action.create-time-period}" @click="onCreateTimePeriodDefault" vu:authz="Project$personalAgenda" />
        <vu:button icon="ri-file-copy-line" label="#{project.bo.project.agenda.action.duplicate-week}" @click="onDuplicateWeek" vu:authz="Project$personalAgenda"/>
        <vu:button icon="ri-gallery-upload-line" label="#{project.bo.project.agenda.action.manage-publication}" @click="onPublishTimePeriods" :disabled="Quasar.date.extractDate(vueData.agendaRange.lastDate, 'yyyy-MM-dd') < new Date()" vu:authz="Project$personalAgenda"/>
    </vu:slot>
</vu:agenda-week>
<vu:agenda-create-plage/>
<vu:agenda-detail-plage>
    <vu:slot name="plage_actions_slot">
        <vu:include-data-primitive key="selectedProjectId" />
        <vu:include-data object="timePeriodDetail" field="ageId" />
        <vu:button icon="edit_calendar" label="#{project.bo.project.agenda.time-period.action.book-appointment}" v-if="vueData.canCreateReservation" vu:authz="Reservation$create"
            th:@click="|openModal('editModal', '@{/management/reservation/new?projectId=}'+vueData.selectedProjectId+'&ageId='+vueData.timePeriodDetail.ageId+'&dateLocale='+vueData.timePeriodDetail.dateLocale)|" />
    </vu:slot>
</vu:agenda-detail-plage>
<vu:agenda-delete-plage/>
<vu:agenda-publish-plage/>
<vu:agenda-duplicate-week/>

<vu:modal componentId="editModal" title="#{reservation.bo.modal.edit.title}" iframe_title="#{reservation.bo.modal.edit.title}" position="right" maximized width="min(1024px, 100vw)" height="calc(100vh - 57px)" @before-hide="refresh()" />
```

__Controller__

Your controller extends `AbstractAgendaController`.
You must set security and route prefix for your page.
You can complete the context for other elements of your page, and call the parent's `initContext` to initialize the context required by the module.

## Content

### Data model

[Planning Entities Diagram](https://github.com/vertigo-io/vertigo-modules/blob/master/vertigo-planning/src/main/javagen/mermaid/mermaid-io-vertigo-planning.html)

**SQL**:

- `planning_create_init_4.3.0.sql`: for initial database creation

Previous versions:

- `planning_create_init_4.2.0.sql`: for initial database creation in 4.2.0
- `planning_update_4.2.0.1.sql`: for update to 4.2.0.1

### Controllers

**AbstractAgendaController**

Includes context elements necessary for module operation to display a calendar with one or multiple merged agendas.
Provides a context initialization method.
Provides standard actions:

- `POST ~/_reload(agendaRange,timePeriodDetail)`: reloads agenda data and selected time period details if applicable
- `POST ~/_semainePrecedente(agendaRange)`: navigates one week earlier
- `POST ~/_semaineSuivante(agendaRange)`: navigates one week later
- `POST ~/_createPlage(agendaRange,creationPlageHoraireForm)`: creates a time period based on the submitted form
- `POST ~/_prepareDuplicateSemaine(agendaRange,duplicationSemaineForm)`: loads initial data for the week duplication popin
- `POST ~/_duplicateSemaine(agendaRange,duplicationSemaineForm)`: duplicates the agenda's week based on the submitted form
- `POST ~/_publishPlage(agendaRange,publicationTrancheHoraireForm)`: publishes time periods of the agenda's week based on the submitted form
- `POST ~/_deletePlage(agendaRange,plhId)`: deletes the identified time period
- `POST ~/_loadPlageHoraireDetail(agendaRange,plhId)`: loads data for the time period detail popin
- `POST ~/_deleteTrancheHoraire(agendaRange,trhId)`: deletes the identified time slice

### Services

**PlanningServices**

Provides a set of services for module integration,
part of the services are consumed by the controller,
the other part can be used by your business services.

Thresholds used during validity checks are configurable via `AgendaFeatures - services.config`:

- `createMinDureePlageMinute`: minimum duration of a time period in minutes (60 min)
- `createMaxDureePlageHeure`: maximum duration of a time period in hours (10 h)
- `createPlageHeureMin`: minimum start time in minutes since midnight (450 = 7:30)
- `createPlageHeureMax`: maximum end time in minutes since midnight (1260 = 21:00)
- `createMaxNbGuichet`: maximum number of counters per time period (9)
- `createMaxDaysFromNow`: maximum days in advance to create (365)
- `publishMaxDaysFromNow`: maximum days in advance to publish (365)
- `publishMaxDaysPeriode`: maximum days published at once (62 = 31*2)
- `publishNowDelaySecond`: delay before effective publication (60 s)
- `duplicateMaxDaysPeriode`: maximum days to duplicate (93)
- `duplicateMaxDaysFromNow`: maximum days in advance to duplicate (365)

## For Experts

### Services

| Service | Role |
|---|---|
| `PlanningServices` | BackOffice services: agenda CRUD, periods, slices, reservations |
| `FoPlanningServices` | FrontOffice services: consultation of available time slots |
| `PlanningServicesConfig` | Configuration of thresholds (11 parameters) |

### FO Plugins (time slot consultation)

| Plugin | Activated by | Description |
|---|---|---|
| `DbFoConsultationPlanningPlugin` | `foConsultation.db` | Direct consultation from database |
| `RedisFoConsultationPlanningPlugin` | `foConsultation.redis` | Consultation from Redis (v1) |
| `Redis2FoConsultationPlanningPlugin` | `foConsultation.redis2` | Consultation from Redis (v2) |
| `RedisUnifiedFoConsultationPlanningPlugin` | `foConsultation.redis2Unified` | Unified Redis consultation (cluster + distributed synchro) |

### DB↔Redis synchronization helpers

| Class | Role |
|---|---|
| `SynchroDbRedisCreneauHelper` | Time slot synchronization between DB and Redis |
| `WorkEngineSynchroDbRedisCreneau` | Stella WorkEngine for distributed synchronization |

### Controllers

| Class | Role |
|---|---|
| `AbstractAgendaController` | Parent controller with context initialization and standard actions |
| `AgendaControllerHelper` | Utilities for agenda controllers |

### DAOs

| DAO | Persisted object |
|---|---|
| `AgendaDAO` | `Agenda` |
| `PlageHoraireDAO` | `PlageHoraire` |
| `TrancheHoraireDAO` | `TrancheHoraire` |
| `CreneauDAO` | `Creneau` |
| `ReservationCreneauDAO` | `ReservationCreneau` |

### Domain Model (DtObjects)

| DtObject | Description |
|---|---|
| `Agenda` | Named calendar (e.g.: "Consultations") |
| `PlageHoraire` | Time window on a date (e.g.: 9am-12pm on 07/01) |
| `TrancheHoraire` | Time slot within a period (e.g.: 9:00-9:30am) |
| `Creneau` | Bookable resource within a slice (counter N°) |
| `ReservationCreneau` | Reservation made by a user |

### Events

| Event | Types |
|---|---|
| `TrancheHoraireEvent` | DELETED, CONSUMED, RELEASED |

### Formatters

| Formatter | Usage |
|---|---|
| `FormatterMinutes` | Formats minutes-since-midnight to readable time (HH:mm) |

### Orchestra Jobs

| Job | Description |
|---|---|
| `PurgeAgendaActivity` | Purge of expired agendas (extends `AbstractActivityEngine`) |

### Features (@Feature)

| Flag | Parameters | Components |
|---|---|---|
| `foConsultation.db` | params… | `DbFoConsultationPlanningPlugin` |
| `foConsultation.redis` | params… | `RedisFoConsultationPlanningPlugin` |
| `foConsultation.redis2` | params… | `Redis2FoConsultationPlanningPlugin` |
| `foConsultation.redis2Unified` | params… | `RedisUnifiedFoConsultationPlanningPlugin` |
| `services.config` | 11 params (validation thresholds) | `PlanningServicesConfig` |

### Configuration YAML

```yaml
io.vertigo.planning.PlanningFeatures:
    # Always active: TraceAspect, ModelDefinitionProvider
io.vertigo.planning.agenda.AgendaFeatures:
    featuresConfig:
        - services.config:
              createMinDureePlageMinute: 60
              createMaxDureePlageHeure: 10
        - foConsultation.redis2Unified:
              distributedSynchro: true
```