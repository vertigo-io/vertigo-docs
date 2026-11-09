# Module planning

## Fonctionnalités

Le module planning de la plateforme Vertigo est un vertical fonctionnel, permettant la gestion, l'organisation d'agenda et la prise de rendez-vous.

Des administrateurs fonctionnels proposent des créneaux qui peuvent ensuite être réservés par des usagers.
La gestion des créneaux est conçue pour être ensembliste. Elle est simplifiée par une présentation sous forme d'un calendrier et manipule essentiellement des plages horaires.
Une plage horaire est une période définie de la journée, composée de tranches horaires d'une même durée (la dernière pouvant être plus courte), chacune offrant autant de créneaux que de guichets.
La gestion utilise un statut de publication simple pour proposer les créneaux à heure fixe.

Les usagers du FrontOffice peuvent consulter et choisir un créneau horaire parmi la liste des disponibilités.

L'intégration de ce module dans l'application métier permet de gérer différents cas d'usage variés :

- Gestion des rendez-vous ouverts par un service pour des démarches administratives.
- Gestion des rendez-vous ouverts par un agent aux usagers, la prise de rendez-vous peut être indifférenciée ou non.

## Atouts

Supporte une charge de consultation très importante, et une contention sur les réservations importante.
Utilisé sur un site avec une très forte affluence. Certains agendas disposent de peu de créneaux disponibles, lesquels sont réservés en quelques minutes.

## Principes

Le module manipule cinq objets :

| Objet | Rôle |
|---|---|
| `Agenda` | Le calendrier, nommé, auquel l'application rattache ses objets métier (un service, une démarche, une personne…) |
| `PlageHoraire` | Une période d'une journée d'un agenda (par exemple 9h-12h le 1er juillet), avec son nombre de guichets |
| `TrancheHoraire` | Un découpage de la plage, de durée fixe (par exemple 9h00-9h30) ; elle porte l'instant de publication |
| `Creneau` | Une place réservable d'une tranche : une par guichet |
| `ReservationCreneau` | La réservation d'un usager ou d'un agent (agenda, date, heures de début et de fin, instant de réservation), rattachée à un créneau ou non |
<!-- source : agenda_model.ksp:L4-108 (entités et associations) -->

Ce que l'usager voit comme un créneau horaire est, dans le modèle, une tranche ; chaque tranche offre autant de créneaux que de guichets.

Le guichet mesure la capacité d'une tranche : le nombre de rendez-vous qu'elle accepte en même temps. Deux organisations correspondent aux deux cas d'usage présentés plus haut :

- **un agenda de service** (mode guichet) : plusieurs agents reçoivent en parallèle sur un même agenda ; le nombre de guichets est saisi à la création de chaque plage ;
- **des agendas personnels**, un par agent, affichés fusionnés dans un même calendrier : la création d'une plage désigne l'agenda à alimenter, et le nombre de guichets est celui du formulaire initial fourni par le contrôleur.
<!-- source : agenda-create-plage.html (select-edit ageId si !modeGuichet, text-field nbGuichet si modeGuichet) ; AbstractAgendaController.java:L75-85 -->

Le cycle de vie suit trois étapes :

1. **La création** : l'administrateur crée des plages horaires ; le module les découpe en tranches de la durée fixée par l'application (`dureeCreneau` du formulaire initial), la dernière tranche étant tronquée à la fin de la plage. Aucun créneau n'existe encore.
2. **La publication** : l'administrateur publie une période, immédiatement ou à une date et une heure choisies. Le module crée aussitôt les créneaux des tranches, autant que de guichets ; seule leur visibilité par les usagers attend l'instant de publication.
3. **La réservation** : un usager (FrontOffice) ou un agent (BackOffice) réserve un créneau libre d'une tranche.
<!-- source : PlanningServices.java:L119-197 (« On ne crée pas les créneaux : seulement à la publication », L194), L725-796 (publication et création immédiate des créneaux) ; agenda_tasks.ksp (instant_Publication <= #now# dans les requêtes de consultation) -->

Un agent peut aussi réserver une tranche qui n'a pas de créneau libre : une tranche jamais publiée, ou complète si le surbooking est autorisé. La réservation est alors une **réservation non rattachée** : la publication suivante de la période la rattache à un créneau libre, s'il en reste un (voir [Publication](#publication)).

Le module appelle **réservations hors planning** (orphelines) les réservations qui ne correspondent plus à aucune tranche, par exemple après la suppression de leur plage.

## Installation du module planning

### Ajout du module dans le pom

```xml
<dependency>
   <groupId>io.vertigo</groupId>
   <artifactId>vertigo-planning</artifactId>
   <version>${vertigo.version}</version>
</dependency>
```

### Ajout dans la configuration Vertigo

Il faut ajouter les features `PlanningFeatures` (le modèle) et `AgendaFeatures` (les services). L'entrée `services.config` permet de modifier le paramétrage par défaut du service `PlanningServices` (voir [Services](#services)).

La consultation des créneaux côté FrontOffice passe par un plugin `foConsultation`, dont l'application active **une seule** variante (dans l'exemple ci-dessous, deux variantes rendues exclusives par un flag) :

| Feature | Stockage de la consultation | Usage |
|---|---|---|
| `foConsultation.db` | Requêtes directes en base | Application sans Redis |
| `foConsultation.redis2Unified` | Cache Redis, alimenté depuis la base, compatible avec Redis en cluster | Forte affluence ; paramètre optionnel `distributedSynchro` (défaut : `false`) |
| `foConsultation.redis`, `foConsultation.redis2` | Cache Redis (versions précédentes) | Dépréciées : préférer `foConsultation.redis2Unified` |
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

Le flag `redis` de cet exemple est un flag de l'application (voir [Flags](/basic/configuration#flags)) : il permet de choisir la variante selon l'environnement.

Les variantes Redis nécessitent un `RedisConnector` (voir [vertigo-redis-connector](/overview/connectors#vertigo-redis-connector)). Elles maintiennent dans Redis les tranches publiées et leur nombre de créneaux libres : un daemon, `DmnSynchroDbRedisCreneau`, les resynchronise depuis la base toutes les 60 secondes, et les événements publiés par l'application les mettent à jour entre deux synchronisations (voir [Cohérence du cache Redis](#cohérence-du-cache-redis)).
<!-- source : RedisUnifiedFoConsultationPlanningPlugin.java:L249-331 (daemon 60 s) ; SynchroDbRedisCreneauHelper.java:L43-45, L119-137 -->

Avec `foConsultation.redis2Unified`, la resynchronisation se répartit entre les nœuds de l'application. Le nœud qui obtient le verrou de synchronisation dans Redis prépare la liste des agendas à traiter. Par défaut, cette liste est traitée, par paquets de 5 agendas, par ce nœud et par les nœuds dont le daemon s'exécute au même moment ; les autres nœuds attendent le cycle suivant.

Quand la synchronisation devient longue (agendas nombreux), le paramètre `distributedSynchro` confie les paquets aux workers de [Stella](/extensions/stella). Il faut alors déclarer le [WorkEngine](/extensions/stella#workengine) de synchronisation dans la configuration Stella :
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

### Ajout dans le modèle

L'application référence l'agenda depuis un de ses objets métier :

```
create Association AMyBusinessObjectAgenda {
   fkFieldName : "ageId"

   dtDefinitionA : DtMyBusinessObject
   type : "*>1"
   dtDefinitionB : DtAgenda

   labelB : "Agenda"
}
```

`DtAgenda` est fourni par le KPR du module, que la configuration de génération du Studio déclare.
Exemple dans `studio-config.yaml` :

```yaml
resources:
   - { type: kpr, path: classpath:io/vertigo/planning/studio/agenda/export_agenda.kpr }
```

Ce KPR expose `DtAgenda`, `DtAgendaDisplay` et `DtReservationCreneau` (pour rattacher une réservation métier à sa réservation de créneau). Il utilise les domaines `DoId` et `DoLabel`, que l'application doit définir.
<!-- source : export_agenda.kpr:L1 ; export_agenda_model.ksp:L3-14 -->

### Base de données

Les tables du module (`AGENDA`, `PLAGE_HORAIRE`, `TRANCHE_HORAIRE`, `CRENEAU`, `RESERVATION_CRENEAU`) et leurs séquences sont créées par les scripts livrés dans le module (`io/vertigo/planning/sql/`), écrits pour PostgreSQL, à intégrer dans les scripts de migration de l'application (par exemple Liquibase) :

- [`planning_create_init_4.3.0.sql`](https://github.com/vertigo-io/vertigo-modules/blob/master/vertigo-planning/src/main/resources/io/vertigo/planning/sql/planning_create_init_4.3.0.sql) : création de la base de données initiale

!> Les scripts de création initiale commencent par supprimer les tables du module (`drop table IF EXISTS … cascade`) : ils ne s'exécutent qu'à l'installation, jamais sur une base qui contient des données.

Versions précédentes :

- `planning_create_init_4.2.0.sql` : création de la base de données initiale en 4.2.0
- `planning_update_4.2.0.1.sql` : mise à jour vers 4.2.0.1 (longueur du nom de l'agenda)
<!-- source : resources/io/vertigo/planning/sql/ (3 scripts) ; planning_update_4.2.0.1.sql:L1 -->

### Ajout des messages ressource

La configuration UI de l'application ajoute la ressource des composants au `MessageSource` :

```java
public static MessageSource getMessageSource() {
    final ResourceBundleMessageSource customMessageSource = new ResourceBundleMessageSource();
    customMessageSource.addBasenames("io/vertigo/ui/components/planning/planning");
    return customMessageSource;
}
```

Les libellés et les icônes des composants (clés `planning.agendaWeek.*`) peuvent être redéfinis dans un bundle de l'application déclaré avant celui du module.

Le formatter des heures du module (`FormatterMinutes`, saisie `HH:mm` ou `HHhmm`, affichage `HH:mm`) utilise un message d'erreur que l'application enregistre dans le `LocaleManager`, par exemple dans un initializer :

```java
localeManager.add("io.vertigo.planning.Formatter", io.vertigo.planning.Resources.values());
```
<!-- source : planning.properties:L1-30 ; FormatterMinutes.java:L33, L53-117 ; Resources.java:L27-33 ; Formatter.properties:L5 -->

## Utilisation dans les pages

Le module fournit les composants du BackOffice. Il ne fournit pas de composant FrontOffice : l'application construit ses écrans de prise de rendez-vous sur `FoPlanningServices` (voir [Consultation FrontOffice](#consultation-frontoffice)).

### Pour le BackOffice

__Compléments CSS__

```html
<head>
    ...
    <link th:href="@{/vertigo-ui/static/planning/css/vertigo-planning.css}" rel="stylesheet" type="text/css">
    <link th:href="@{/vertigo-ui/static/3rdParty/cdn.jsdelivr.net/npm/@quasar/quasar-ui-qcalendar@4.1.2/index.min.css}" rel="stylesheet" type="text/css">
</head>
```

?> La feuille de style de QCalendar (Quasar, version 4.1.2) est nécessaire à l'affichage du calendrier.

__Compléments JavaScript__

```html
<section layout:fragment="additional-librairies">
    <script th:src="@{/vertigo-ui/static/3rdParty/cdn.jsdelivr.net/npm/@quasar/quasar-ui-qcalendar@4.1.2/QCalendarDay.umd.min.js}"></script>
    <script th:src="@{/vertigo-ui/static/planning/js/vertigo-planning.js?t=__${appBuildTime}__}"></script>
</section>
```

#### Composants VertigoUi

- `agenda-week` : Composant calendrier complet, à poser pleine page
  - `agenda_actions_slot` : Slot des boutons du composant (défaut : création de plage, duplication de jour, duplication de semaine, publication)
  - `agenda_tranchesHoraire_slot` : Slot d'affichage des tranches horaires (en mode tranches horaires)
  - `agenda_reservationOrphelines_slot` : Slot d'affichage des réservations hors planning (orphelines)
  - `eventNameTwoLetters` : 2 lettres dans la plage (défaut : false)
  - `eventIconAgenda` : Icône dans la plage (défaut : `event`)
  - `multiEventIconAgenda` : Icône d'agenda multiple dans la plage (défaut : `calendar_month`)
  - `maxMultiEventShow` : Nombre maximum d'agendas présentés avant liste (défaut : 3)
  - `hasAuthzAdmin` : Si droit d'admin de l'agenda (défaut : true) ; sans ce droit, le calendrier ne propose plus la création d'une plage au clic, ni la modification ou la suppression des plages

- `agenda-create-plage` : Composant de modale création de plage horaire
  - `plage_actions_slot` : Slot des boutons du composant (défaut : bouton de création, selon le mode guichet ou agenda personnel)

- `agenda-detail-plage` : Composant de modale détail de plage horaire
  - `plage_actions_slot` : Slot des boutons du composant (défaut : aucun)

- `agenda-delete-plage` : Composant de modale de confirmation de suppression de plage horaire
  - `plage_actions_slot` : Slot des boutons du composant (défaut : annuler, supprimer)

- `agenda-duplicate-day` : Composant de modale de duplication d'un jour vers d'autres jours
  - `plage_actions_slot` : Slot des boutons du composant (défaut : dupliquer le jour)

- `agenda-duplicate-week` : Composant de modale de duplication de semaine
  - `plage_actions_slot` : Slot des boutons du composant (défaut : dupliquer la semaine)

- `agenda-publish-plage` : Composant de modale de publication de plage horaire (publication planifiée ou immédiate)
  - `plage_actions_slot` : Slot des boutons du composant (défaut : annuler, publier)
<!-- source : components/planning/agenda-week.html:L1-12, L187-188, L220 ; agenda-create-plage.html:L67-70 ; agenda-detail-plage.html:L19 ; agenda-delete-plage.html:L19-22 ; agenda-duplicate-day.html:L46-48 ; agenda-duplicate-week.html:L25-27 ; agenda-publish-plage.html:L45-46, L83-86 -->

`hasAuthzAdmin` ne masque pas les boutons par défaut d'`agenda_actions_slot` : pour un calendrier en consultation, l'application redéfinit ce slot en conditionnant ses boutons par `vu:authz`, comme dans l'exemple ci-dessous, et sécurise les routes de son contrôleur.

__Exemple__

```html
<vu:agenda-week eventIconAgenda="ri-folder-fill" hasAuthzAdmin="${authz.hasAuthorization('Demarche$agendaPersonnel')}">
    <vu:slot name="agenda_actions_slot">
        <vu:button icon="ri-add-line" label="#{projet.bo.projet.agenda.action.create-plage-horaire}" @click="onCreatePlageHoraireDefault" vu:authz="Projet$agendaPersonnel" />
        <vu:button icon="ri-file-copy-line" label="#{projet.bo.projet.agenda.action.duplicate-week}" @click="onDuplicateWeek" vu:authz="Projet$agendaPersonnel"/>
        <vu:button icon="ri-gallery-upload-line" label="#{projet.bo.projet.agenda.action.manage-publication}" @click="onPublishPlageHoraires" :disabled="Quasar.date.extractDate(vueData.agendaRange.lastDate, 'yyyy-MM-dd') < new Date()" vu:authz="Projet$agendaPersonnel"/>
    </vu:slot>
</vu:agenda-week>
<vu:agenda-create-plage/>
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

#### Contrôleur de la page

Le contrôleur de la page hérite d'`AbstractAgendaController`. Il porte la sécurité et le préfixe de ses routes, complète le contexte pour les autres éléments de sa page, et appelle le `initContext` du parent, qui initialise le contexte nécessaire au module :

```java
initContext(viewContext, agendasDisplay, weekDaysNumber, creationPlageHoraireForm, duplicationSemaineForm, modeGuichet, modeTranchesHoraire);
```

- `agendasDisplay` : les agendas affichés, éventuellement plusieurs, fusionnés dans un même calendrier (`AgendaDisplay`, dont le nom peut être remplacé par `overridedName`) ;
- `weekDaysNumber` : le nombre de jours affichés par semaine (par exemple 5, du lundi au vendredi) ;
- `creationPlageHoraireForm`, `duplicationSemaineForm` : les valeurs initiales des formulaires de création et de duplication (dont la durée des tranches et, hors mode guichet, le nombre de guichets) ;
- `modeGuichet` : en mode guichet, la création d'une plage demande un nombre de guichets ; sinon, l'agenda à alimenter (voir [Principes](#principes)) ;
- `modeTranchesHoraire` : le calendrier affiche les tranches horaires plutôt que les plages.

Le contrôleur peut redéfinir `getInfoCalendrierForRange(viewContext, startDate, endDate)`, qui fournit les informations d'en-tête des jours (`InfoCalendrierDisplay` : libellé, infobulle, style) ; un jour indiqué comme fermé (`siFerme`) n'est pas alimenté par les duplications. `getAgendaLabel()` fournit le libellé du champ de sélection de l'agenda, dans la modale de création (défaut : « Agenda »).

Les routes du contrôleur reçoivent les identifiants numériques des objets (`plhId`, `trhId`) ; les services du module prennent des `UID`, identifiants typés des entités (par exemple `UID.of(PlageHoraire.class, plhId)`), et la liste des `UID<Agenda>` autorisés pour l'utilisateur.
<!-- source : AbstractAgendaController.java:L44, L75-85, L87-178, L188-199 ; AgendaControllerHelper.java:L140-183 ; agenda-create-plage.html:L63-64 ; agenda_ui_model.ksp:L12-23, L131-138 ; AgendaControllerHelper.java:L255-276 (jours fermés) -->

## Mise en œuvre

### Gestion des agendas et des plages horaires

Les opérations de BackOffice sont portées par le service `PlanningServices` :

- `createAgenda(name)` : crée un agenda, que l'application rattache à son objet métier ; `deleteEmptyAgenda(ageUid)` le supprime.
- `createPlageHoraire(form, authorizedAgeUids, maxWeekDaysNumber)` : crée une plage et la découpe en tranches de `dureeCreneau` minutes. La création contrôle les seuils de `services.config` (durée, heures de début et de fin, nombre de guichets, éloignement de la date), le jour de la semaine, et l'absence de chevauchement avec les plages des agendas autorisés. Les erreurs sont collectées par champ du formulaire et levées ensemble (`ValidationUserException`). Un agenda non autorisé provoque une `VSecurityException` ; les autres refus métier sont des `VUserException` dont le message est destiné à l'utilisateur.
- `duplicateSemaine(…)`, `duplicateJour(…)` : reproduisent les plages d'une semaine ou d'un jour sur d'autres dates, en ignorant les jours fermés et les plages qui chevaucheraient l'existant.
- `deletePlageHoraireCascade(ageUid, plhUid)` : supprime une plage, ses tranches et ses créneaux. Les réservations sont conservées : elles deviennent hors planning.
- `closeTrancheHoraire(ageUid, trhUid)` : ferme une tranche : son nombre de guichets passe à zéro, ses créneaux sont supprimés, et elle n'est plus proposée.
- `checkAuthorizedAgenda(ageUid, authorizedAgeUids)`, `checkAuthorizedAgendaOfPlh(plhUid, authorizedAgeUids)` : vérifient que l'agenda concerné fait partie des agendas autorisés pour l'utilisateur.

La création, la duplication et la suppression de plages, ainsi que la fermeture d'une tranche, verrouillent la ligne de l'agenda en base (`readOneForUpdate`) : deux actions simultanées sur un même agenda ne créent pas de plages en double. La publication ne pose pas ce verrou.
<!-- source : PlanningServices.java:L90 (@Transactional), L110-197 (création, contrôles, verrou L167, conflits L169-179, UiErrorBuilder L128, L181), L235-312 (duplications, verrou L329), L403-431, L459-468 (jours fermés, conflits), L470-484 (verrous L474, L482), L881-883, L895-907 ; agenda_tasks.ksp:L28-36 (fermeture d'une tranche) -->

!> Les requêtes SQL écrites par l'application sur les tables du module ne bénéficient pas de ces verrous, ni de ceux de la réservation : préférer les méthodes du service pour modifier les plages, les tranches et les réservations.

### Publication

`publishPlageHorairesAndRelinkReservation(ageUids, publicationTrancheHoraireForm)` publie les tranches de la période choisie (`dateLocaleDebut` à `dateLocaleFin`). Dans le calendrier, la période est préremplie du premier jour affiché (ou d'aujourd'hui si la semaine est en cours) au dernier jour affiché, en publication planifiée. La publication est :

- **immédiate** (`publishNow`) : les tranches deviennent visibles après un court délai (`publishNowDelaySecond`, défaut : 60 s) ;
- **planifiée** : `publicationDateLocale` et `publicationMinutesDebut`, dans le fuseau `publicationZonCd` (défaut : `Europe/Paris`).

Dans les deux cas, les créneaux sont créés dès l'appel, autant que de guichets de chaque tranche ; une tranche fermée (sans guichet) n'en reçoit pas. L'instant de publication porté par la tranche ne règle que sa visibilité par les usagers. Les réservations non rattachées de la période sont ensuite rattachées aux créneaux restés libres.

`relinkReservationsToCreneaux(ageUids, dateDebut, dateFin)` effectue seul ce rattachement, par exemple après un import de réservations.

Le calendrier signale deux situations à reprendre par un agent :

- les réservations sur des tranches non visibles des usagers, c'est-à-dire non publiées, planifiées ou fermées (`nbReserveNonPublie`) ;
- les réservations hors planning (orphelines), qui ne correspondent plus à aucune tranche. `getReservationOrphelines(ageUids, firstDate, lastDate)` en donne le nombre, regroupé par demi-heure ; le calendrier les affiche dans le slot `agenda_reservationOrphelines_slot`.
<!-- source : PlanningServices.java:L725-796 (publication, création des créneaux L792-795), L807-821 (rattachement), L585-588 ; agenda_tasks.ksp:L455-471 (orphelines : not exists tranche_horaire, agrégation minuteAgg), L632-671 (publication, création des créneaux), L706-738 ; agenda_ui_model.ksp:L42-51 ; planning.properties:L22-23 (reserveNonPublie) -->

### Consultation FrontOffice

Le service `FoPlanningServices` porte la consultation des disponibilités, déléguée au plugin `foConsultation` configuré :

- `getTrancheHoraireDisponibles(critere)` : les tranches publiées ayant au moins un créneau libre ;
- `getDateDePremiereDisponibilite(critere)` : la date de la première tranche disponible entre `premierJour` et `dateMax` ;
- `getDateDeDernierePublication(ageUids)` : la dernière date de tranche visible des usagers (dans l'année à venir) ;
- `getPrecedentePublication(ageUids)`, `getProchainePublication(ageUids)` : la publication précédente ou suivante (`PublicationRange` : période publiée `dateMin` - `dateMax` et instant de publication), pour annoncer à l'usager l'ouverture des prochains créneaux.

Le critère `CritereTrancheHoraire` porte les agendas consultés (`ageIds`), le premier jour affiché (`premierJour`), un plancher (`dateMin`, `minutesMin`) en deçà duquel les tranches ne sont pas proposées (par exemple pour imposer un délai de prévenance), et la date limite de recherche (`dateMax`). Les tranches disponibles sont cherchées sur 7 jours à partir de `premierJour`.
<!-- source : FoPlanningServices.java:L35-57 ; FoConsultationPlanningPlugin.java:L32-43 ; CritereTrancheHoraire.java (ageIds, premierJour, dateMin, minutesMin, dateMax) ; DbFoConsultationPlanningPlugin.java:L49, L57 ; RedisUnifiedFoConsultationPlanningPlugin.java:L130 -->

### Réservation

- `reserverCreneau(trhUid)` : réserve un créneau libre de la tranche. Les créneaux sont sélectionnés avec `FOR UPDATE SKIP LOCKED` : deux réservations simultanées ne prennent jamais le même créneau, et ne s'attendent pas. Le résultat est vide si aucun créneau libre n'est disponible sans attente (tous réservés, ou en cours de réservation). Cette méthode ne contrôle pas la publication de la tranche : côté FrontOffice, l'application ne propose que des tranches obtenues par la consultation.
- `reserverCreneau(ageUids, startDate, endDate, startMinutes, endMinutes)` : réserve un créneau libre d'une tranche publiée parmi plusieurs agendas, sur une période et une plage de minutes.
- `reserverCreneauBO(trhUid, siSurbooking)` : réservation par un agent. Elle prend un créneau libre s'il en existe, y compris sur une tranche dont la publication est planifiée. Sinon (tranche jamais publiée, ou complète), elle verrouille la tranche et crée une réservation non rattachée ; elle est refusée si la tranche est complète et que le surbooking n'est pas autorisé.
- `supprimerReservationCreneau(recUids)` : supprime des réservations et libère leurs créneaux.

La réservation de créneau porte l'agenda, la date, les heures de début et de fin et l'instant de réservation : l'application la rattache à sa propre réservation métier.
<!-- source : PlanningServices.java:L612-680 (reserverCreneauBO : getTrancheHoraireWithLock L665), L714-723, L823-831 ; agenda_tasks.ksp:L558-591 (FOR UPDATE SKIP LOCKED), L689-700, L740-749 ; agenda_model.ksp:L12-18 -->

### Cohérence du cache Redis

Avec une consultation Redis, le nombre de créneaux libres de chaque tranche est maintenu dans Redis. **C'est l'application qui signale les changements**, en publiant un `TrancheHoraireEvent` sur l'[EventBus](/extensions/commons#eventbus) ; le module ne le publie pas lui-même. Les plugins Redis y sont abonnés :

| Type | À publier | Effet dans Redis |
|---|---|---|
| `CONSOMME` | après une réservation par `reserverCreneau` | un créneau libre de moins |
| `LIBERE` | après une annulation par `supprimerReservationCreneau` | un créneau libre de plus |
| `SUPPRIME` | quand `reserverCreneau` revient vide pour une tranche proposée à l'usager | plus aucun créneau libre, jusqu'à la resynchronisation suivante |

L'événement désigne les tranches concernées par leur agenda, leur date et leur heure de début (`HoraireImpacte`). Il se publie une fois la transaction validée :

```java
transactionManager.getCurrentTransaction().addAfterCompletion(committed -> {
	if (committed) {
		eventBusManager.post(new TrancheHoraireEvent(TrancheHoraireEvent.Type.CONSOMME,
				List.of(new HoraireImpacte(ageId, dateLocale, minutesDebut))));
	}
});
```

Les opérations de BackOffice (publication, fermeture d'une tranche, suppression d'une plage) n'ont pas d'événement : la resynchronisation périodique (60 s) les reporte dans Redis. Elle réécrit les jours qui gardent au moins une tranche disponible ; un jour devenu sans disponibilité disparaît de Redis à l'expiration de ses clés, au plus 120 s après sa dernière écriture. Si la donnée Redis d'une tranche est absente ou sur le point d'expirer (moins de 5 s), l'événement déclenche une resynchronisation depuis la base des dates concernées.
<!-- source : TrancheHoraireEvent.java:L31-87 ; aucun post dans le module ; RedisUnifiedFoConsultationPlanningPlugin.java:L341-402 (@EventBusSubscribed, traitement par type, TTL < 5 s) ; VTransaction.java:L75 ; EventBusManager.java:L52 -->

### Purge

Les agendas s'alimentent au fil du temps : les données passées doivent être purgées. `purgeAgendaOlderThan(date)` supprime les plages, tranches, créneaux et réservations antérieurs à la date. Le module fournit l'activité Orchestra `PurgeAgendaActivity`, à inclure dans un processus de l'application, dont le paramètre initial `olderThanDays` fixe l'ancienneté des données purgées (voir [Les processus](/modules/orchestra#les-processus)).

La purge supprime les réservations de créneau : si l'application y rattache ses réservations métier par une clé étrangère, elle purge ou détache ses propres réservations avant celles du module.
<!-- source : PlanningServices.java:L890-893 ; agenda_tasks.ksp:L779-801 ; PurgeAgendaActivity.java:L30-48 -->

## Contenu

### Modèle de données

[`mermaid-io-vertigo-planning.html`](https://github.com/vertigo-io/vertigo-modules/blob/master/vertigo-planning/src/main/javagen/mermaid/mermaid-io-vertigo-planning.html) : diagramme des entités, à ouvrir dans un navigateur une fois téléchargé.

**SQL** : voir [Base de données](#base-de-données).

### Contrôleurs

**AbstractAgendaController**

Inclut les éléments du contexte nécessaires au fonctionnement du module pour afficher un calendrier avec un ou plusieurs agendas fusionnés.
Propose une méthode d'initialisation du contexte.
Fournit les actions standards :

- `POST ~/_reload(agendaRange,plageHoraireDetail)` : recharge les données de l'agenda, et le détail de la plage horaire sélectionnée le cas échéant
- `POST ~/_semainePrecedente(agendaRange)` : navigue une semaine plus tôt
- `POST ~/_semaineSuivante(agendaRange)` : navigue une semaine plus tard
- `POST ~/_createPlage(agendaRange,creationPlageHoraireForm)` : crée une plage horaire en fonction du formulaire envoyé
- `POST ~/_prepareDuplicateSemaine(agendaRange,duplicationSemaineForm)` : charge les données initiales de la popin de duplication de semaine
- `POST ~/_duplicateSemaine(agendaRange,duplicationSemaineForm)` : duplique la semaine de l'agenda en fonction du formulaire envoyé
- `POST ~/_duplicateJour(agendaRange,duplicationJourForm,duplicationSemaineForm)` : duplique un jour vers les jours choisis
- `POST ~/_publishPlage(agendaRange,publicationTrancheHoraireForm)` : publie les tranches des agendas affichés sur la période du formulaire
- `POST ~/_deletePlage(agendaRange,plhId)` : supprime la plage horaire identifiée
- `POST ~/_loadPlageHoraireDetail(agendaRange,plhId)` : charge les données de la popin de détail de la plage horaire
- `POST ~/_deleteTrancheHoraire(agendaRange,plageHoraireDetail,trhId)` : ferme la tranche horaire identifiée, et recharge le détail de la plage
<!-- source : AbstractAgendaController.java:L87-178 -->

### Services

**PlanningServices**

Propose un ensemble de services pour l'intégration du module,
une partie des services est consommée par le contrôleur,
l'autre peut être utilisée par vos services métier (voir [Mise en œuvre](#mise-en-œuvre)).

Les seuils utilisés lors des contrôles de validité sont paramétrables via `AgendaFeatures - services.config` :

| Paramètre | Rôle | Défaut |
|---|---|---|
| `createMinDureePlageMinute` | Durée minimale d'une plage horaire, en minutes | 60 |
| `createMaxDureePlageHeure` | Durée maximale d'une plage horaire, en heures | 10 |
| `createPlageHeureMin` | Heure de début minimale, en minutes depuis minuit | 450 (7h30) |
| `createPlageHeureMax` | Heure de fin maximale, en minutes depuis minuit | 1260 (21h00) |
| `createMaxNbGuichet` | Nombre maximal de guichets d'une plage horaire (au plus 12) | 9 |
| `createMaxDaysFromNow` | Jours maximum à l'avance pour créer | 365 |
| `publishMaxDaysFromNow` | Jours maximum à l'avance pour publier | 365 |
| `publishMaxDaysPeriode` | Jours maximum publiés à la fois | 62 |
| `publishNowDelaySecond` | Délai avant publication effective, en secondes | 60 |
| `duplicateMaxDaysPeriode` | Jours maximum à dupliquer | 93 |
| `duplicateMaxDaysFromNow` | Jours maximum à l'avance pour dupliquer | 365 |
<!-- source : PlanningServicesConfig.java:L65-100 ; PlanningSmartTypes.java:L81-85 (nombre de guichets 1..12) -->

## Pour les experts

### Services et configuration

| Service | Rôle |
|---|---|
| `PlanningServices` | Services BackOffice : agendas, plages, tranches, publication, réservations, purge |
| `FoPlanningServices` | Services FrontOffice : consultation des créneaux disponibles |
| `PlanningServicesConfig` | Configuration de `PlanningServices` (11 seuils) |

### Plugins FrontOffice (consultation des créneaux)

| Plugin | Activé par | Description |
|---|---|---|
| `DbFoConsultationPlanningPlugin` | `foConsultation.db` | Consultation directe depuis la base |
| `RedisFoConsultationPlanningPlugin` | `foConsultation.redis` | Consultation depuis Redis (v1, dépréciée) |
| `Redis2FoConsultationPlanningPlugin` | `foConsultation.redis2` | Consultation depuis Redis (v2, dépréciée) |
| `RedisUnifiedFoConsultationPlanningPlugin` | `foConsultation.redis2Unified` | Consultation Redis unifiée, compatible avec Redis en cluster, synchronisation distribuée possible |

### Synchronisation de la base vers Redis

| Classe | Rôle |
|---|---|
| `SynchroDbRedisCreneauHelper` | Synchronisation des créneaux de la base vers Redis |
| `WorkEngineSynchroDbRedisCreneau` | WorkEngine Stella pour la synchro distribuée |

### Classes des contrôleurs

| Classe | Rôle |
|---|---|
| `AbstractAgendaController` | Contrôleur parent avec initialisation du contexte et actions standards |
| `AgendaControllerHelper` | Utilitaires pour les contrôleurs d'agenda (construit par `AbstractAgendaController` ; ce n'est pas un composant) |
<!-- source : AgendaControllerHelper.java:L55, L104-107 ; AbstractAgendaController.java:L44 -->

### DAOs

| DAO | Objet persisté |
|---|---|
| `AgendaDAO` | `Agenda` |
| `PlageHoraireDAO` | `PlageHoraire` |
| `TrancheHoraireDAO` | `TrancheHoraire` |
| `CreneauDAO` | `Creneau` |
| `ReservationCreneauDAO` | `ReservationCreneau` |
| `AgendaPAO` | Requêtes transverses du module |

### Modèle Domain (DtObjects)

| DtObject | Description |
|---|---|
| `Agenda` | Calendrier nommé (par exemple « Consultations ») |
| `PlageHoraire` | Période d'une journée, avec son nombre de guichets (par exemple 9h-12h le 1er juillet) |
| `TrancheHoraire` | Découpage de la plage, de durée fixe (par exemple 9h00-9h30) |
| `Creneau` | Place réservable d'une tranche (une par guichet) |
| `ReservationCreneau` | Réservation d'un usager ou d'un agent, rattachée à un créneau ou non |

### Événements

| Événement | Types |
|---|---|
| `TrancheHoraireEvent` | SUPPRIME, CONSOMME, LIBERE (publié par l'application, voir [Cohérence du cache Redis](#cohérence-du-cache-redis)) |

### Formatters

| Formatter | Usage |
|---|---|
| `FormatterMinutes` | Formatage des minutes-depuis-minuit en temps lisible (HH:mm) |

### Activité Orchestra

| Activité | Description |
|---|---|
| `PurgeAgendaActivity` | Purge des données antérieures à `olderThanDays` jours (extends `AbstractActivityEngine`, paramètre `olderThanDays`) |

### Features (@Feature)

| Flag | Paramètres | Composants |
|---|---|---|
| `foConsultation.db` | — | `DbFoConsultationPlanningPlugin` |
| `foConsultation.redis` | — | `RedisFoConsultationPlanningPlugin` |
| `foConsultation.redis2` | — | `Redis2FoConsultationPlanningPlugin` |
| `foConsultation.redis2Unified` | `distributedSynchro` (optionnel, défaut : `false`) | `RedisUnifiedFoConsultationPlanningPlugin` |
| `services.config` | 11 paramètres optionnels (seuils de validation) | `PlanningServicesConfig` |

Les autres composants du module (DAO, PAO, `PlanningServices`, `FoPlanningServices`) sont enregistrés automatiquement par `AgendaFeatures`, qui découvre les composants de son package.
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

Pour `distributedSynchro`, voir l'exemple avec Stella dans [Ajout dans la configuration Vertigo](#ajout-dans-la-configuration-vertigo).
