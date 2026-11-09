# Planning module

## Features

The Vertigo platform planning module is a functional vertical for managing, organizing calendars, and making appointments.

Functional administrators propose time slots that can then be booked by end users.
Time slot management is designed to be set-based. It is simplified by a calendar presentation and primarily manipulates time periods.
A time period is a defined period of the day, composed of time ranges of the same duration (the last one may be shorter), each offering as many slots as counters.
Management uses a simple publication status to propose fixed-time slots.

FrontOffice end users can view and choose a time slot from the list of available slots.

Integrating this module into the business application allows managing various use cases:

- Managing appointments opened by a service for administrative procedures.
- Managing appointments opened by an agent for end users; booking can be undifferentiated or not.

## Strengths

Supports very high consultation load and significant contention on reservations.
Used on a site with very high traffic. Some calendars have few available slots, which are booked within minutes.

## Principles

The module handles five objects:

| Object | Role |
|---|---|
| `Agenda` | The named calendar, to which the application links its business objects (a service, a procedure, a person…) |
| `PlageHoraire` | A time period of one day of an agenda (for example 9am-12pm on July 1st), with its number of counters |
| `TrancheHoraire` | A time range: a fixed-duration division of the time period (for example 9:00-9:30); it carries the publication instant |
| `Creneau` | A bookable slot of a time range: one per counter |
| `ReservationCreneau` | The reservation of an end user or an agent (agenda, date, start and end times, reservation instant), linked to a slot or not |
<!-- source : agenda_model.ksp:L4-108 (entités et associations) -->

What the end user sees as a time slot is, in the model, a time range; each time range offers as many slots as counters.

The counter measures the capacity of a time range: the number of appointments it accepts at the same time. Two organizations match the two use cases presented above:

- **a service agenda** (counter mode): several agents receive in parallel on the same agenda; the number of counters is entered when each time period is created;
- **personal agendas**, one per agent, displayed merged in a single calendar: creating a time period designates the agenda to fill, and the number of counters is the one of the initial form provided by the controller.
<!-- source : agenda-create-plage.html (select-edit ageId si !modeGuichet, text-field nbGuichet si modeGuichet) ; AbstractAgendaController.java:L75-85 -->

The life cycle follows three steps:

1. **Creation**: the administrator creates time periods; the module divides them into time ranges of the duration set by the application (`dureeCreneau` of the initial form), the last time range being truncated at the end of the period. No slot exists yet.
2. **Publication**: the administrator publishes a period, immediately or at a chosen date and time. The module creates the slots of the time ranges right away, as many as counters; only their visibility to end users waits for the publication instant.
3. **Reservation**: an end user (FrontOffice) or an agent (BackOffice) books a free slot of a time range.
<!-- source : PlanningServices.java:L119-197 (« On ne crée pas les créneaux : seulement à la publication », L194), L725-796 (publication et création immédiate des créneaux) ; agenda_tasks.ksp (instant_Publication <= #now# dans les requêtes de consultation) -->

An agent can also book a time range that has no free slot: a time range never published, or a full one if overbooking is allowed. The reservation is then an **unlinked reservation**: the next publication of the period links it to a free slot, if one remains (see [Publication](#publication)).

The module calls **off-schedule reservations** (orphans) the reservations that no longer match any time range, for example after their time period has been deleted.

## Installing the planning module

### Adding the module to pom.xml

```xml
<dependency>
   <groupId>io.vertigo</groupId>
   <artifactId>vertigo-planning</artifactId>
   <version>${vertigo.version}</version>
</dependency>
```

### Adding to Vertigo configuration

You need to add the `PlanningFeatures` (the model) and `AgendaFeatures` (the services) features. The `services.config` entry allows modifying the default configuration of the `PlanningServices` service (see [Services](#services)).

Slot consultation on the FrontOffice side goes through a `foConsultation` plugin, of which the application activates **a single** variant (in the example below, two variants made exclusive by a flag):

| Feature | Consultation storage | Usage |
|---|---|---|
| `foConsultation.db` | Direct database queries | Application without Redis |
| `foConsultation.redis2Unified` | Redis cache, fed from the database, compatible with Redis cluster | High traffic; optional parameter `distributedSynchro` (default: `false`) |
| `foConsultation.redis`, `foConsultation.redis2` | Redis cache (previous versions) | Deprecated: prefer `foConsultation.redis2Unified` |
<!-- source : AgendaFeatures.java:L37-71 ; FoPlanningServices.java:L38-39 (plugin unique, non optionnel) ; RedisFoConsultationPlanningPlugin.java:L56 et Redis2FoConsultationPlanningPlugin.java:L65 (@Deprecated) ; RedisUnifiedFoConsultationPlanningPlugin.java:L96-114 (distributedSynchro) -->

```yaml
io.vertigo.planning.PlanningFeatures:
io.vertigo.planning.agenda.AgendaFeatures:
    featuresConfig:
        - services.config:
        - foConsultation.db:
              __flags__: ["!redis"]
        - foConsultation.redis2Unified:
              __flags__: ["redis"]
```

The `redis` flag of this example is an application flag (see [Flags](/en/basic/configuration#flags)): it allows choosing the variant depending on the environment.

The Redis variants require a `RedisConnector` (see [vertigo-redis-connector](/en/overview/connectors#vertigo-redis-connector)). They keep in Redis the published time ranges and their number of free slots: a daemon, `DmnSynchroDbRedisCreneau`, resynchronizes them from the database every 60 seconds, and the events posted by the application update them between two synchronizations (see [Redis cache consistency](#redis-cache-consistency)).
<!-- source : RedisUnifiedFoConsultationPlanningPlugin.java:L249-331 (daemon 60 s) ; SynchroDbRedisCreneauHelper.java:L43-45, L119-137 -->

With `foConsultation.redis2Unified`, the resynchronization is shared among the application nodes. The node that obtains the synchronization lock in Redis prepares the list of agendas to process. By default, this list is processed, in batches of 5 agendas, by this node and by the nodes whose daemon runs at the same moment; the other nodes wait for the next cycle.

When the synchronization becomes long (many agendas), the `distributedSynchro` parameter hands the batches over to the [Stella](/en/extensions/stella) workers. The synchronization [WorkEngine](/en/extensions/stella#workengine) must then be declared in the Stella configuration:
<!-- source : RedisUnifiedFoConsultationPlanningPlugin.java:L77, L93, L107-111 (masterManager requis), L272-287 (mode distribué), L289-331 (mode local : traitement de la file si le verrou date de moins de 2 s) ; README.md:L41-72 -->

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

The application references the agenda from one of its business objects:

```
create Association AMyBusinessObjectAgenda {
   fkFieldName : "ageId"

   dtDefinitionA : DtMyBusinessObject
   type : "*>1"
   dtDefinitionB : DtAgenda

   labelB : "Agenda"
}
```

`DtAgenda` is provided by the module's KPR, which the Studio generation configuration declares.
Example in `studio-config.yaml`:

```yaml
resources:
   - { type: kpr, path: classpath:io/vertigo/planning/studio/agenda/export_agenda.kpr }
```

This KPR exposes `DtAgenda`, `DtAgendaDisplay` and `DtReservationCreneau` (to link a business reservation to its slot reservation). It uses the `DoId` and `DoLabel` domains, which the application must define.
<!-- source : export_agenda.kpr:L1 ; export_agenda_model.ksp:L3-14 -->

### Database

The module tables (`AGENDA`, `PLAGE_HORAIRE`, `TRANCHE_HORAIRE`, `CRENEAU`, `RESERVATION_CRENEAU`) and their sequences are created by the scripts shipped in the module (`io/vertigo/planning/sql/`), written for PostgreSQL, to be included in the application's migration scripts (for example Liquibase):

- [`planning_create_init_4.5.0.sql`](https://github.com/vertigo-io/vertigo-modules/blob/master/vertigo-planning/src/main/resources/io/vertigo/planning/sql/planning_create_init_4.5.0.sql): initial database creation, with its unique constraints (a reservation occupies a single slot; two time periods of an agenda never start at the same time) and its consultation indexes
- [`planning_update_4.5.0.sql`](https://github.com/vertigo-io/vertigo-modules/blob/master/vertigo-planning/src/main/resources/io/vertigo/planning/sql/planning_update_4.5.0.sql): update of an existing database to 4.5.0 (constraints and indexes); adding the constraints fails if the data already contains duplicates, which the queries commented in the script help find

!> The initial creation scripts start by dropping the module tables (`drop table IF EXISTS … cascade`): they only run at installation, never on a database that contains data.

Previous versions:

- `planning_create_init_4.3.0.sql`: initial database creation in 4.3.0
- `planning_create_init_4.2.0.sql`: initial database creation in 4.2.0
- `planning_update_4.2.0.1.sql`: update to 4.2.0.1 (length of the agenda name)
<!-- source : resources/io/vertigo/planning/sql/ (5 scripts) ; planning_update_4.2.0.1.sql:L1 ; planning_create_init_4.5.0.sql (contraintes A_RESERVATION_CRENEAU_CRENEAU_RESERVATION_CRENEAU_UNIQUE_FK, A_PLAGE_HORAIRE_UNIQUE, index IDX_*) ; planning_update_4.5.0.sql -->

### Adding resource messages

The application UI configuration adds the components resource to the `MessageSource`:

```java
public static MessageSource getMessageSource() {
    final ResourceBundleMessageSource customMessageSource = new ResourceBundleMessageSource();
    customMessageSource.addBasenames("io/vertigo/ui/components/planning/planning");
    return customMessageSource;
}
```

The labels and icons of the components (`planning.agendaWeek.*` keys) can be redefined in an application bundle declared before the module's one.

The module's time formatter (`FormatterMinutes`, input `HH:mm` or `HHhmm`, display `HH:mm`) uses an error message that the application registers in the `LocaleManager`, for example in an initializer:

```java
localeManager.add("io.vertigo.planning.Formatter", io.vertigo.planning.Resources.values());
```
<!-- source : planning.properties:L1-30 ; FormatterMinutes.java:L33, L53-117 ; Resources.java:L27-33 ; Formatter.properties:L5 -->

## Usage in pages

The module provides the BackOffice components. It provides no FrontOffice component: the application builds its appointment booking screens on `FoPlanningServices` (see [FrontOffice consultation](#frontoffice-consultation)).

### For BackOffice

__CSS additions__

```html
<head>
    ...
    <link th:href="@{/vertigo-ui/static/planning/css/vertigo-planning.css}" rel="stylesheet" type="text/css">
    <link th:href="@{/vertigo-ui/static/3rdParty/cdn.jsdelivr.net/npm/@quasar/quasar-ui-qcalendar@4.1.2/index.min.css}" rel="stylesheet" type="text/css">
</head>
```

?> The QCalendar stylesheet (Quasar, version 4.1.2) is required to display the calendar.

__JavaScript additions__

```html
<section layout:fragment="additional-librairies">
    <script th:src="@{/vertigo-ui/static/3rdParty/cdn.jsdelivr.net/npm/@quasar/quasar-ui-qcalendar@4.1.2/QCalendarDay.umd.min.js}"></script>
    <script th:src="@{/vertigo-ui/static/planning/js/vertigo-planning.js?t=__${appBuildTime}__}"></script>
</section>
```

#### VertigoUi Components

- `agenda-week`: Full calendar component, place it full page
  - `agenda_actions_slot`: Component buttons slot (default: create time period, duplicate day, duplicate week, publication)
  - `agenda_tranchesHoraire_slot`: Time ranges display slot (in time ranges mode)
  - `agenda_reservationOrphelines_slot`: Off-schedule (orphan) reservations display slot
  - `eventNameTwoLetters`: 2 letters in the time period (default: false)
  - `eventIconAgenda`: Icon in the time period (default: `event`)
  - `multiEventIconAgenda`: Multiple agenda icon in the time period (default: `calendar_month`)
  - `maxMultiEventShow`: Maximum number of agendas shown before list (default: 3)
  - `hasAuthzAdmin`: If agenda admin rights (default: true); without this right, the calendar no longer offers creating a time period on click, nor modifying or deleting time periods

- `agenda-create-plage`: Time period creation modal component
  - `plage_actions_slot`: Component buttons slot (default: creation button, depending on counter or personal agenda mode)

- `agenda-edit-plage`: Time period edition modal component; its confirmation reports the appointments already booked and the publication needed again

- `agenda-detail-plage`: Time period detail modal component
  - `plage_actions_slot`: Component buttons slot (default: none)

- `agenda-delete-plage`: Time period deletion confirmation modal component
  - `plage_actions_slot`: Component buttons slot (default: cancel, delete)

- `agenda-duplicate-day`: Modal component duplicating a day to other days
  - `plage_actions_slot`: Component buttons slot (default: duplicate the day)

- `agenda-duplicate-week`: Week duplication modal component
  - `plage_actions_slot`: Component buttons slot (default: duplicate the week)

- `agenda-publish-plage`: Time period publication modal component (scheduled or immediate publication)
  - `plage_actions_slot`: Component buttons slot (default: cancel, publish)
<!-- source : components/planning/agenda-week.html:L1-12, L187-188, L220 ; agenda-create-plage.html:L67-70 ; agenda-detail-plage.html:L19 ; agenda-delete-plage.html:L19-22 ; agenda-duplicate-day.html:L46-48 ; agenda-duplicate-week.html:L25-27 ; agenda-publish-plage.html:L45-46, L83-86 -->

`hasAuthzAdmin` does not hide the default buttons of `agenda_actions_slot`: for a read-only calendar, the application redefines this slot with its buttons conditioned by `vu:authz`, as in the example below, and secures the routes of its controller.

__Example__

```html
<vu:agenda-week eventIconAgenda="ri-folder-fill" hasAuthzAdmin="${authz.hasAuthorization('Demarche$agendaPersonnel')}">
    <vu:slot name="agenda_actions_slot">
        <vu:button icon="ri-add-line" label="#{projet.bo.projet.agenda.action.create-plage-horaire}" @click="onCreatePlageHoraireDefault" vu:authz="Projet$agendaPersonnel" />
        <vu:button icon="ri-file-copy-line" label="#{projet.bo.projet.agenda.action.duplicate-week}" @click="onDuplicateWeek" vu:authz="Projet$agendaPersonnel"/>
        <vu:button icon="ri-gallery-upload-line" label="#{projet.bo.projet.agenda.action.manage-publication}" @click="onPublishPlageHoraires" :disabled="Quasar.date.extractDate(vueData.agendaRange.lastDate, 'yyyy-MM-dd') < new Date()" vu:authz="Projet$agendaPersonnel"/>
    </vu:slot>
</vu:agenda-week>
<vu:agenda-create-plage/>
<vu:agenda-edit-plage/>
<vu:agenda-detail-plage>
    <vu:slot name="plage_actions_slot">
        <vu:include-data-primitive key="selectedProjetId" />
        <vu:include-data object="plageHoraireDetail" field="ageId" />
        <vu:button icon="edit_calendar" label="#{projet.bo.projet.agenda.plage-horaire.action.book-rdv}" v-if="vueData.canCreateReservation" vu:authz="Reservation$create"
            th:@click="|openModal('editModal', '@{/gestion/reservation/new?projetId=}'+vueData.selectedProjetId+'&ageId='+vueData.plageHoraireDetail.ageId+'&dateLocale='+vueData.plageHoraireDetail.dateLocale)|" />
    </vu:slot>
</vu:agenda-detail-plage>
<vu:agenda-delete-plage/>
<vu:agenda-publish-plage/>
<vu:agenda-duplicate-week/>

<vu:modal componentId="editModal" title="#{reservation.bo.modal.edit.title}" iframe_title="#{reservation.bo.modal.edit.title}" position="right" maximized width="min(1024px, 100vw)" height="calc(100vh - 57px)" @before-hide="refresh()" />
```

#### Page controller

The page controller extends `AbstractAgendaController`. It carries the security and the prefix of its routes, completes the context for the other elements of its page, and calls the parent's `initContext`, which initializes the context required by the module:

```java
initContext(viewContext, agendasDisplay, weekDaysNumber, creationPlageHoraireForm, duplicationSemaineForm, modeGuichet, modeTranchesHoraire);
```

- `agendasDisplay`: the displayed agendas, possibly several, merged in a single calendar (`AgendaDisplay`, whose name can be replaced by `overridedName`);
- `weekDaysNumber`: the number of days displayed per week (for example 5, Monday to Friday);
- `creationPlageHoraireForm`, `duplicationSemaineForm`: the initial values of the creation and duplication forms (including the duration of the time ranges and, outside counter mode, the number of counters);
- `modeGuichet`: in counter mode, creating a time period asks for a number of counters; otherwise, for the agenda to fill (see [Principles](#principles));
- `modeTranchesHoraire`: the calendar displays the time ranges rather than the time periods.

The controller can override `getInfoCalendrierForRange(viewContext, startDate, endDate)`, which provides the day header information (`InfoCalendrierDisplay`: label, tooltip, style); a day marked as closed (`siFerme`) is not filled by duplications. `getAgendaLabel()` provides the label of the agenda selection field, in the creation modal (default: "Agenda").

The controller routes receive the numeric identifiers of the objects (`plhId`, `trhId`); the module services take `UID`s, typed identifiers of the entities (for example `UID.of(PlageHoraire.class, plhId)`), and the list of `UID<Agenda>` authorized for the user.
<!-- source : AbstractAgendaController.java:L44, L75-85, L87-178, L188-199 ; AgendaControllerHelper.java:L140-183 ; agenda-create-plage.html:L63-64 ; agenda_ui_model.ksp:L12-23, L131-138 ; AgendaControllerHelper.java:L255-276 (jours fermés) -->

## Implementation

### Managing agendas and time periods

BackOffice operations are carried by the `PlanningServices` service:

- `createAgenda(name)`: creates an agenda, which the application links to its business object; `deleteEmptyAgenda(ageUid)` deletes it.
- `createPlageHoraire(form, authorizedAgeUids, maxWeekDaysNumber)`: creates a time period and divides it into time ranges of `dureeCreneau` minutes. Creation checks the `services.config` thresholds (duration, start and end times, number of counters, distance of the date), the day of the week, and the absence of overlap with the time periods of the authorized agendas. Errors are collected per form field and raised together (`ValidationUserException`). An unauthorized agenda raises a `VSecurityException`; the other business refusals are `VUserException`s whose message is intended for the user.
- `duplicateSemaine(…)`, `duplicateJour(…)`: reproduce the time periods of a week or a day on other dates, ignoring closed days and time periods that would overlap existing ones.
- `deletePlageHoraireCascade(ageUid, plhUid)`: deletes a time period, its time ranges and its slots. Reservations are kept: they become off-schedule.
- `updatePlageHoraire(plhUid, form, authorizedAgeUids, maxWeekDaysNumber)`: modifies a time period on the same date (times, number of counters, agenda). The time period is deleted and created again, with the creation checks; it is no longer published: the agent checks it, then publishes it, which links its reservations again. A change of date, or a modification that changes nothing, is refused.
- `closeTrancheHoraire(ageUid, trhUid)`: closes a time range: its number of counters drops to zero, its slots are deleted, and it is no longer offered.
- `checkAuthorizedAgenda(ageUid, authorizedAgeUids)`, `checkAuthorizedAgendaOfPlh(plhUid, authorizedAgeUids)`: check that the agenda concerned is among the agendas authorized for the user.

Creating, duplicating, modifying and deleting time periods, as well as closing a time range, lock the agenda row in the database (`readOneForUpdate`): two simultaneous actions on the same agenda do not create duplicate time periods. Publication does not set this lock.
<!-- source : PlanningServices.java:L90 (@Transactional), L110-197 (création, contrôles, verrou L167, conflits L169-179, UiErrorBuilder L128, L181), L235-312 (duplications, verrou L329), L403-431, L459-468 (jours fermés, conflits), L470-484 (verrous L474, L482), updatePlageHoraire (suppression puis création), L881-883, L895-907 ; agenda_tasks.ksp:L28-36 (fermeture d'une tranche) -->

!> SQL queries written by the application on the module tables do not benefit from these locks, nor from the reservation ones: prefer the service methods to modify time periods, time ranges and reservations.

### Publication

`publishPlageHorairesAndRelinkReservation(ageUids, publicationTrancheHoraireForm)` publishes the time ranges of the chosen period (`dateLocaleDebut` to `dateLocaleFin`). In the calendar, the period is prefilled from the first displayed day (or today if the week is in progress) to the last displayed day, as a scheduled publication. Publication is:

- **immediate** (`publishNow`): the time ranges become visible after a short delay (`publishNowDelaySecond`, default: 60 s);
- **scheduled**: `publicationDateLocale` and `publicationMinutesDebut`, in the `publicationZonCd` time zone (default: `Europe/Paris`).

In both cases, the slots are created as soon as the method is called, as many as counters of each time range; a closed time range (without counter) gets none. The publication instant carried by the time range only governs its visibility to end users. The unlinked reservations of the period are then linked to the slots that remain free.

`relinkReservationsToCreneaux(ageUids, dateDebut, dateFin)` performs this linking alone, for example after an import of reservations.

The calendar reports two situations for an agent to handle:

- reservations on time ranges not visible to end users, that is not published, scheduled or closed (`nbReserveNonPublie`);
- off-schedule (orphan) reservations, which no longer match any time range. `getReservationOrphelines(ageUids, firstDate, lastDate)` gives their number, grouped by half hour; the calendar displays them in the `agenda_reservationOrphelines_slot` slot.
<!-- source : PlanningServices.java:L725-796 (publication, création des créneaux L792-795), L807-821 (rattachement), L585-588 ; agenda_tasks.ksp:L455-471 (orphelines : not exists tranche_horaire, agrégation minuteAgg), L632-671 (publication, création des créneaux), L706-738 ; agenda_ui_model.ksp:L42-51 ; planning.properties:L22-23 (reserveNonPublie) -->

### FrontOffice consultation

The `FoPlanningServices` service carries the consultation of availabilities, delegated to the configured `foConsultation` plugin:

- `getTrancheHoraireDisponibles(critere)`: the published time ranges with at least one free slot;
- `getDateDePremiereDisponibilite(critere)`: the date of the first available time range between `premierJour` and `dateMax`;
- `getDateDeDernierePublication(ageUids)`: the last date of a time range visible to end users (within the coming year);
- `getPrecedentePublication(ageUids)`, `getProchainePublication(ageUids)`: the previous or next publication (`PublicationRange`: published period `dateMin` - `dateMax` and publication instant), to announce to the end user when the next slots open.

The `CritereTrancheHoraire` criterion carries the consulted agendas (`ageIds`), the first displayed day (`premierJour`), a floor (`dateMin`, `minutesMin`) below which time ranges are not offered (for example to impose a notice period), and the search limit date (`dateMax`). Available time ranges are searched over 7 days from `premierJour`.
<!-- source : FoPlanningServices.java:L35-57 ; FoConsultationPlanningPlugin.java:L32-43 ; CritereTrancheHoraire.java (ageIds, premierJour, dateMin, minutesMin, dateMax) ; DbFoConsultationPlanningPlugin.java:L49, L57 ; RedisUnifiedFoConsultationPlanningPlugin.java:L130 -->

### Reservation

- `reserverCreneau(trhUid)`: books a free slot of the time range. Slots are selected with `FOR UPDATE SKIP LOCKED`: two simultaneous reservations never take the same slot, and do not wait for each other. The result is empty if no free slot is available without waiting (all booked, or being booked). This method does not check the publication of the time range: on the FrontOffice side, the application only offers time ranges obtained through the consultation.
- `reserverCreneau(ageUids, startDate, endDate, startMinutes, endMinutes)`: books a free slot of a published time range among several agendas, over a period and a range of minutes.
- `reserverCreneauBO(trhUid, siSurbooking)`: reservation by an agent. It takes a free slot if one exists, including on a time range whose publication is scheduled. Otherwise (time range never published, or full), it locks the time range and creates an unlinked reservation; it is refused if the time range is full and overbooking is not allowed.
- `supprimerReservationCreneau(recUids)`: deletes reservations and frees their slots.

The slot reservation carries the agenda, the date, the start and end times and the reservation instant: the application links it to its own business reservation.
<!-- source : PlanningServices.java:L612-680 (reserverCreneauBO : getTrancheHoraireWithLock L665), L714-723, L823-831 ; agenda_tasks.ksp:L558-591 (FOR UPDATE SKIP LOCKED), L689-700, L740-749 ; agenda_model.ksp:L12-18 -->

### Redis cache consistency

With a Redis consultation, the number of free slots of each time range is kept in Redis. **The application reports the changes**, by posting a `TrancheHoraireEvent` on the [EventBus](/en/extensions/commons#eventbus); the module does not post it itself. The Redis plugins subscribe to it:

| Type | To post | Effect in Redis |
|---|---|---|
| `CONSOMME` | after a reservation by `reserverCreneau` | one free slot less |
| `LIBERE` | after a cancellation by `supprimerReservationCreneau` | one free slot more |
| `SUPPRIME` | when `reserverCreneau` returns empty for a time range offered to the end user | no free slot left, until the next resynchronization |

The event designates the time ranges concerned by their agenda, date and start time (`HoraireImpacte`). It is posted once the transaction is committed:

```java
transactionManager.getCurrentTransaction().addAfterCompletion(committed -> {
	if (committed) {
		eventBusManager.post(new TrancheHoraireEvent(TrancheHoraireEvent.Type.CONSOMME,
				List.of(new HoraireImpacte(ageId, dateLocale, minutesDebut))));
	}
});
```

BackOffice operations (publication, closing a time range, deleting a time period) have no event: the periodic resynchronization (60 s) carries them over to Redis. It rewrites the days that keep at least one available time range; a day left without availability disappears from Redis when its keys expire, at most 120 s after its last write. If the Redis data of a time range is missing or about to expire (less than 5 s), the event triggers a resynchronization from the database of the dates concerned.
<!-- source : TrancheHoraireEvent.java:L31-87 ; aucun post dans le module ; RedisUnifiedFoConsultationPlanningPlugin.java:L341-402 (@EventBusSubscribed, traitement par type, TTL < 5 s) ; VTransaction.java:L75 ; EventBusManager.java:L52 -->

### Purge

Agendas are fed over time: past data must be purged. `purgeAgendaOlderThan(date)` deletes the time periods, time ranges, slots and reservations prior to the date. The module provides the Orchestra activity `PurgeAgendaActivity`, to include in an application process, whose initial parameter `olderThanDays` sets the age of the purged data (see [Processes](/en/modules/orchestra#processes)).

The purge deletes the slot reservations: if the application links its business reservations to them through a foreign key, it purges or detaches its own reservations before the module's ones.
<!-- source : PlanningServices.java:L890-893 ; agenda_tasks.ksp:L779-801 ; PurgeAgendaActivity.java:L30-48 -->

## Content

### Data model

[`mermaid-io-vertigo-planning.html`](https://github.com/vertigo-io/vertigo-modules/blob/master/vertigo-planning/src/main/javagen/mermaid/mermaid-io-vertigo-planning.html): entities diagram, to open in a browser once downloaded.

**SQL**: see [Database](#database).

### Controllers

**AbstractAgendaController**

Includes the context elements necessary for module operation to display a calendar with one or several merged agendas.
Provides a context initialization method.
Provides standard actions:

- `POST ~/_reload(agendaRange,plageHoraireDetail)`: reloads the agenda data, and the detail of the selected time period if any
- `POST ~/_semainePrecedente(agendaRange)`: navigates one week earlier
- `POST ~/_semaineSuivante(agendaRange)`: navigates one week later
- `POST ~/_createPlage(agendaRange,creationPlageHoraireForm)`: creates a time period according to the submitted form
- `POST ~/_prepareDuplicateSemaine(agendaRange,duplicationSemaineForm)`: loads the initial data of the week duplication popin
- `POST ~/_duplicateSemaine(agendaRange,duplicationSemaineForm)`: duplicates the agenda week according to the submitted form
- `POST ~/_duplicateJour(agendaRange,duplicationJourForm,duplicationSemaineForm)`: duplicates a day to the chosen days
- `POST ~/_publishPlage(agendaRange,publicationTrancheHoraireForm)`: publishes the time ranges of the displayed agendas over the period of the form
- `POST ~/_deletePlage(agendaRange,plhId)`: deletes the identified time period
- `POST ~/_editPlage(agendaRange,plhId,creationPlageHoraireForm)`: modifies the identified time period according to the submitted form; it must be published again
- `POST ~/_loadPlageHoraireDetail(agendaRange,plhId)`: loads the data of the time period detail popin
- `POST ~/_deleteTrancheHoraire(agendaRange,plageHoraireDetail,trhId)`: closes the identified time range, and reloads the time period detail
<!-- source : AbstractAgendaController.java:L87-178 -->

### Services

**PlanningServices**

Provides a set of services for module integration,
part of the services is consumed by the controller,
the other part can be used by your business services (see [Implementation](#implementation)).

The thresholds used during validity checks are configurable via `AgendaFeatures - services.config`:

| Parameter | Role | Default |
|---|---|---|
| `createMinDureePlageMinute` | Minimum duration of a time period, in minutes | 60 |
| `createMaxDureePlageHeure` | Maximum duration of a time period, in hours | 10 |
| `createPlageHeureMin` | Minimum start time, in minutes since midnight | 450 (7:30am) |
| `createPlageHeureMax` | Maximum end time, in minutes since midnight | 1260 (9:00pm) |
| `createMaxNbGuichet` | Maximum number of counters of a time period (at most 12) | 9 |
| `createMaxDaysFromNow` | Maximum days in advance to create | 365 |
| `publishMaxDaysFromNow` | Maximum days in advance to publish | 365 |
| `publishMaxDaysPeriode` | Maximum days published at once | 62 |
| `publishNowDelaySecond` | Delay before effective publication, in seconds | 60 |
| `duplicateMaxDaysPeriode` | Maximum days to duplicate | 93 |
| `duplicateMaxDaysFromNow` | Maximum days in advance to duplicate | 365 |
<!-- source : PlanningServicesConfig.java:L65-100 ; PlanningSmartTypes.java:L81-85 (nombre de guichets 1..12) -->

## For Experts

### Services and configuration

| Service | Role |
|---|---|
| `PlanningServices` | BackOffice services: agendas, time periods, time ranges, publication, reservations, purge |
| `FoPlanningServices` | FrontOffice services: consultation of available slots |
| `PlanningServicesConfig` | Configuration of `PlanningServices` (11 thresholds) |

### FrontOffice plugins (slot consultation)

| Plugin | Enabled by | Description |
|---|---|---|
| `DbFoConsultationPlanningPlugin` | `foConsultation.db` | Direct consultation from the database |
| `RedisFoConsultationPlanningPlugin` | `foConsultation.redis` | Consultation from Redis (v1, deprecated) |
| `Redis2FoConsultationPlanningPlugin` | `foConsultation.redis2` | Consultation from Redis (v2, deprecated) |
| `RedisUnifiedFoConsultationPlanningPlugin` | `foConsultation.redis2Unified` | Unified Redis consultation, compatible with Redis cluster, distributed synchronization available |

### Synchronization from the database to Redis

| Class | Role |
|---|---|
| `SynchroDbRedisCreneauHelper` | Synchronization of slots from the database to Redis |
| `WorkEngineSynchroDbRedisCreneau` | Stella WorkEngine for distributed synchronization |

### Controller classes

| Class | Role |
|---|---|
| `AbstractAgendaController` | Parent controller with context initialization and standard actions |
| `AgendaControllerHelper` | Utilities for agenda controllers (built by `AbstractAgendaController`; it is not a component) |
<!-- source : AgendaControllerHelper.java:L55, L104-107 ; AbstractAgendaController.java:L44 -->

### DAOs

| DAO | Persisted object |
|---|---|
| `AgendaDAO` | `Agenda` |
| `PlageHoraireDAO` | `PlageHoraire` |
| `TrancheHoraireDAO` | `TrancheHoraire` |
| `CreneauDAO` | `Creneau` |
| `ReservationCreneauDAO` | `ReservationCreneau` |
| `AgendaPAO` | Cross-cutting queries of the module |

### Domain Model (DtObjects)

| DtObject | Description |
|---|---|
| `Agenda` | Named calendar (for example "Consultations") |
| `PlageHoraire` | Time period of one day, with its number of counters (for example 9am-12pm on July 1st) |
| `TrancheHoraire` | Division of the time period, of fixed duration (for example 9:00-9:30) |
| `Creneau` | Bookable slot of a time range (one per counter) |
| `ReservationCreneau` | Reservation of an end user or an agent, linked to a slot or not |

### Events

| Event | Types |
|---|---|
| `TrancheHoraireEvent` | SUPPRIME, CONSOMME, LIBERE (posted by the application, see [Redis cache consistency](#redis-cache-consistency)) |

### Formatters

| Formatter | Usage |
|---|---|
| `FormatterMinutes` | Formatting of minutes-since-midnight into readable time (HH:mm) |

### Orchestra activity

| Activity | Description |
|---|---|
| `PurgeAgendaActivity` | Purge of data older than `olderThanDays` days (extends `AbstractActivityEngine`) |

### Features (@Feature)

| Flag | Parameters | Components |
|---|---|---|
| `foConsultation.db` | — | `DbFoConsultationPlanningPlugin` |
| `foConsultation.redis` | — | `RedisFoConsultationPlanningPlugin` |
| `foConsultation.redis2` | — | `Redis2FoConsultationPlanningPlugin` |
| `foConsultation.redis2Unified` | `distributedSynchro` (optional, default: `false`) | `RedisUnifiedFoConsultationPlanningPlugin` |
| `services.config` | 11 optional parameters (validation thresholds) | `PlanningServicesConfig` |

The other components of the module (DAOs, PAO, `PlanningServices`, `FoPlanningServices`) are registered automatically by `AgendaFeatures`, which discovers the components of its package.
<!-- source : AgendaFeatures.java:L29-85 ; ModuleDiscoveryFeatures.java:L44-47 ; PlanningFeatures.java:L32-38 -->

### Configuration YAML

```yaml
io.vertigo.planning.PlanningFeatures:
io.vertigo.planning.agenda.AgendaFeatures:
    featuresConfig:
        - services.config:
              createMinDureePlageMinute: 60
              createMaxDureePlageHeure: 10
        - foConsultation.redis2Unified:
```

For `distributedSynchro`, see the example with Stella in [Adding to Vertigo configuration](#adding-to-vertigo-configuration).
