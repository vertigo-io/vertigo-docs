# Module planning

## Fonctionnalités

Le module planning de Vertigo est un vertical fonctionnel, permettant la gestion, l'organisation d'agenda et la prise de rendez vous.

Des administrateurs fonctionnels, proposent des créneaux qui peuvent ensuite être réservés par des utilisateurs.
La gestion des créneaux est conçue pour être ensembliste. Elle est simplifiée par une présentation sous forme d'un calendrier et manipule essentiellement des plages horaires. 
Une plage horaire est une période définie de la journée, composée de créneaux d'une durée identique, proposés par un nombre défini de guichets.
La gestion utilise un statut de publication simple pour proposer les créneaux à heure fixe.

Les utilisateurs du FrontOffice peuvent consulter et choisir un creneau horaire parmi la liste des disponibilités.

L'intégration de ce module dans l'application métier permet de géréer différents cas d'usage variés :
 
  - Gestion des rendez-vous ouvert par un service pour des démarches administratives.
  - Gestion des rendez-vous ouvert par un agent aux utilisateurs, la prise de rendez-vous peut-être indifférentiée ou non.

## Atouts
Supporte une charge de consultation très importante, et une contention sur les réservations importante.
Utilisé sur un site avec une très forte affluence. Certains agendas disposent de peu de créneaux disponibles, lesquels sont réservés en quelques minutes.


## Installation module planning

### Ajout du module dans le pom
```xml
<dependency>
   <groupId>io.vertigo</groupId>
   <artifactId>vertigo-planning</artifactId>
   <version>4.3.2</version>
</dependency>
```

## Ajout dans la conf vertigo

Il faut ajouter les features `PlanningFeatures` et `AgendaFeatures`.
L'entrée `services.config` permet de modifier le paramétrage par défaut du service `PlanningServices` (cf. plus bas).
Le plugin `foConsultation` utilisé coté FrontOffice existe en version : Base de Données et Redis.

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

> La configuration permet de proposer une synchronisation distribuée.
> Pour cela, il faut un WorkEngine dans Stella et ajouter la tache dans le redis2Unified :
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

## Ajout dans le model

Dans votre modelisation, il faut référencer l'agenda depuis un de vos objets métier.
```
create Association AMyBusinessObjectAgenda {
   fkFieldName : "ageId"

   dtDefinitionA : DtMyBusinessObject
   type : "*>1"
   dtDefinitionB : DtAgenda
    
   labelB : "Agenda"
}
```

Pour que le DtAgenda soit reconnu, il faut aussi l'ajouter le kpr du module lors de la génération de studio.
Exemple dans `studio-config.yaml` :
```yaml
resources:
  - { type: kpr, path: classpath:io/vertigo/planning/studio/agenda/export_agenda.kpr }
```

## Ajout des messages resource

Dans votre `XxxVSpringWebConfig`, on ajout la ressource au `MessageSource` Spring.
```Java
public static MessageSource getMessageSource() {
	final ResourceBundleMessageSource customMessageSource = new ResourceBundleMessageSource();
        ...
	customMessageSource.addBasenames("io/vertigo/ui/components/planning/planning");
	...
	return customMessageSource;
}
```

## Utilisation dans les pages

### Pour le BackOffice

__Compléments CSS__
```HTML
<head>
    ...
    <link th:href="@{/vertigo-ui/static/planning/css/vertigo-planning.css}" rel="stylesheet" type="text/css">
    <link th:href="@{/vertigo-ui/static/3rdParty/cdn.jsdelivr.net/npm/@quasar/quasar-ui-qcalendar@4.1.2/index.min.css}" rel="stylesheet" type="text/css">   
</head>	
```
___Note:___ _La css de quasar est nécessaire pour le calendrier_

__Compléments javascript__
```Javascript
<section layout:fragment="additional-librairies" >
	<script th:src="@{/vertigo-ui/static/3rdParty/cdn.jsdelivr.net/npm/@quasar/quasar-ui-qcalendar@4.1.2/QCalendarDay.umd.min.js}"></script>
	<script th:src="@{/vertigo-ui/static/planning/js/vertigo-planning.js?t=__${appBuildTime}__}"></script>
</section>	
```

Composants VertigoUi 
- `agenda-week` : Composant calendrier complet, à poser pleine page
  - `agenda_actions_slot` : Slot des boutons du composant (défaut: creation de plage, duplication de semaine, publication)
  - `eventNameTwoLetters` : 2 lettre dans la plage (défaut : false)
  - `eventIconAgenda` : Icon dans la plage (défaut : `event`)
  - `multiEventIconAgenda` : Icon d'agenda multiple dans la plage (défaut : `calendar_month`)
  - `maxMultiEventShow` : Nombre maximum d'agenda présenté avant liste (défaut : 3)
  - `hasAuthzAdmin` : Si droit d'admin de l'agenda (défaut : true)

- `agenda-create-plage` : Composant de modale création de plage horaire
  - `plage_actions_slot` : Slot des boutons du composant (défaut: creation si guichet, creation si agenda personnel)
  
- `agenda-detail-plage` : Composant de modale détail de plage horaire
  - `plage_actions_slot` : Slot des boutons du composant (défaut: aucun)

- `agenda-delete-plage` : Composant de modale de confirmation de suppression de plage horaire
  - `plage_actions_slot` : Slot des boutons du composant (défaut: annuler, deletePlageHoraire)

- `agenda-duplicate-week` : Composant de modale de duplication de semaine
  - `plage_actions_slot` : Slot des boutons du composant (défaut: dupliquer semaine)

- `agenda-publish-plage` : Composant de modale de publication de plage horaire
  - `plage_actions_slot` : Slot des boutons du composant (défaut: annuler, publishPlageHoraires)

Exemple
```HTML
<vu:agenda-week eventIconAgenda="ri-folder-fill" hasAuthzAdmin="${authz.hasAuthorization('Demarche$agendaPersonel')}">
	<vu:slot name="agenda_actions_slot">
		<vu:button icon="ri-add-line" label="#{demarche.bo.demarche.agenda.action.create-plage-horaire}" @click="onCreatePlageHoraireDefault" vu:authz="Demarche$agendaPersonel" /> 
		<vu:button icon="ri-file-copy-line" label="#{demarche.bo.demarche.agenda.action.duplicate-week}" @click="onDuplicateWeek" vu:authz="Demarche$agendaPersonel"/>
		<vu:button icon="ri-gallery-upload-line" label="#{demarche.bo.demarche.agenda.action.manage-publication}" @click="onPublishPlageHoraires" :disabled="Quasar.date.extractDate(vueData.agendaRange.lastDate, 'yyyy-MM-dd') < new Date()" vu:authz="Demarche$agendaPersonel"/>
	</vu:slot>
</vu:agenda-week>
<vu:agenda-create-plage/>
<vu:agenda-detail-plage>
	<vu:slot name="plage_actions_slot">
		<vu:include-data-primitive key="selectedDemarcheId" />
		<vu:include-data object="plageHoraireDetail" field="ageId" />                        
		<vu:button icon="edit_calendar" label="#{demarche.bo.demarche.agenda.plage-horaire.action.book-rdv}" v-if="vueData.canCreateReservation" vu:authz="Reservation$create" 
			th:@click="|openModal('editModal', '@{/gestion/reservation/new?demId=}'+vueData.selectedDemarcheId+'&ageId='+vueData.plageHoraireDetail.ageId+'&dateLocale='+vueData.plageHoraireDetail.dateLocale)|" />                 
	</vu:slot>
</vu:agenda-detail-plage>
<vu:agenda-delete-plage/>
<vu:agenda-publish-plage/>
<vu:agenda-duplicate-week/>
		
<vu:modal componentId="editModal" title="#{reservation.bo.modal.edit.title}" iframe_title="#{reservation.bo.modal.edit.title}" position="right" maximized width="min(1024px, 100vw)" height="calc(100vh - 57px)" @before-hide="refresh()" />		
```

__Controlleur__

Votre controlleur hérite du AbstractAgendaController.
Vous devez positionner la sécurité et le préfix des routes de votre page.
Vous pouvez compléter le context pour les autres éléments de votre page, et appeller le initContext du parent pour initialiser le context nécessaire au module.

	
## Contenu 
 
### Modèle de données

### Sql
 - planning_create_init_4.3.0.sql : pour la création de la base de données initiale
 
_ previous version _
Si besoin :
 - planning_create_init_4.2.0.sql : pour la création de la base de données initiale en 4.2.0
 - planning_update_4.2.0.1.sql : pour la mise à jour vers 4.2.0.1
 
### Controlleurs

**AbstractAgendaController**
Inclus les éléments du context nécessaire au fonctionnement du module pour afficher un calendrier avec un ou plusieurs agenda fusionés
Propose une méthode d'initalisation du context
Fournit les actions standards :
 - `POST ~/_reload(agendaRange,plageHoraireDetail)` : recharge les données de l'agenda, et le détail de la plage horaire sélectionnée le cas échéant
 - `POST ~/_semainePrecedente(agendaRange)` : navigue une semaine plus tot
 - `POST ~/_semaineSuivante(agendaRange)` : navigue une semaine plus 
 - `POST ~/_createPlage(agendaRange,creationPlageHoraireForm)` : Crée une plage horaire en fonction du formulaire envoyé
 - `POST ~/_prepareDuplicateSemaine(agendaRange,duplicationSemaineForm)` : Charge les données initiales de la popin de duplication de semaine
 - `POST ~/_duplicateSemaine(agendaRange,duplicationSemaineForm)` : Duplique la semaine de l'agenda en fonction du formulaire envoyé
 - `POST ~/_publishPlage(agendaRange,publicationTrancheHoraireForm)` : Publie les plages horaires des agendas la semaine de l'agenda en fonction du formulaire envoyé
 - `POST ~/_deletePlage(agendaRange,plhId)` : Supprime la plage horaire identifiée
 - `POST ~/_loadPlageHoraireDetail(agendaRange,plhId)` : Charge les données de la popin de détail de la plage horaire
 - `POST ~/_deleteTrancheHoraire(agendaRange,trhId)` : Supprime la tranche horaire identifiée
	 

### services

**PlanningServices**
Propose un ensemble de service pour l'intégration du module, 
une partie des services sont consommés par le controller, 
une autre peut-être utilisé par vos services métiers.
https://github.com/vertigo-io/vertigo-modules/blob/master/vertigo-planning/src/main/java/io/vertigo/planning/agenda/services/PlanningServices.java

Les seuils utilisés lors des controles de validité sont paramétrable via `AgendaFeature -services.config` :
- `createMinDureePlageMinute` : la durée minimale d'une plage horaire en minutes (60 min)
- `createMaxDureePlageHeure` : la durée maximale d'une plage horaire en heures (10 h)
- `createPlageHeureMin` : heure de début minimale en minutes depuis minuit (450 = 7:30)
- `createPlageHeureMax` : heure de fin maximale en minutes depuis minuit (1260 = 21:00)
- `createMaxNbGuichet` : nombre maximal de guichets pour une plage horaire (9)
- `createMaxDaysFromNow` : jours maximum à l'avance pour créer (365)
- `publishMaxDaysFromNow` : jours maximum à l'avance pour publier (365)
- `publishMaxDaysPeriode` : jours maximum publiés à la fois (60)
- `publishNowDelaySecond` : délai avant publication effective (60 s)
- `duplicateMaxDaysPeriode` : jours maximum à dupliquer (90)
- `duplicateMaxDaysFromNow` : jours maximum à l'avance pour dupliquer (365)

## Pour les experts

### Services

| Service | Rôle |
|---|---|
| `PlanningServices` | Services BackOffice : CRUD agenda, plages, tranches, réservations |
| `FoPlanningServices` | Services FrontOffice : consultation des créneaux disponibles |
| `PlanningServicesConfig` | Configuration des seuils (11 paramètres)` |

### Plugins FO (consultation créneaux)

| Plugin | Activé par | Description |
|---|---|---|
| `DbFoConsultationPlanningPlugin` | `foConsultation.db` | Consultation directe depuis la base |
| `RedisFoConsultationPlanningPlugin` | `foConsultation.redis` | Consultation depuis Redis (v1) |
| `Redis2FoConsultationPlanningPlugin` | `foConsultation.redis2` | Consultation depuis Redis (v2) |
| `RedisUnifiedFoConsultationPlanningPlugin` | `foConsultation.redis2Unified` | Consultation Redis unifiée (cluster + synchro distribuée) |

### Helpers de synchronisation DB↔Redis

| Classe | Rôle |
|---|---|
| `SynchroDbRedisCreneauHelper` | Synchronisation des créneaux entre DB et Redis |
| `WorkEngineSynchroDbRedisCreneau` | WorkEngine Stella pour la synchro distribuée |

### Contrôleurs

| Classe | Rôle |
|---|---|
| `AbstractAgendaController` | Controller parent avec initialisation du contexte et actions standards |
| `AgendaControllerHelper` | Utilitaires pour les contrôleurs d'agenda |

### DAOs

| DAO | Objet persisté |
|---|---|
| `AgendaDAO` | `Agenda` |
| `PlageHoraireDAO` | `PlageHoraire` |
| `TrancheHoraireDAO` | `TrancheHoraire` |
| `CreneauDAO` | `Creneau` |
| `ReservationCreneauDAO` | `ReservationCreneau` |

### Modèle Domain (DtObjects)

| DtObject | Description |
|---|---|
| `Agenda` | Calendrier nommé (ex: "Consultations") |
| `PlageHoraire` | Fenêtre temporelle sur une date (ex: 9h-12h le 01/07) |
| `TrancheHoraire` | Creneau horaire dans une plage (ex: 9h00-9h30) |
| `Creneau` | Resource reservable dans une tranche (guichet N°) |
| `ReservationCreneau` | Reservation effectuee par un utilisateur |

### Events

| Event | Types |
|---|---|
| `TrancheHoraireEvent` | SUPPRIME, CONSOMME, LIBERE |

### Formatters

| Formatter | Usage |
|---|---|
| `FormatterMinutes` | Formatage des minutes-depuis-minuit en temps lisible (HH:mm) |

### Jobs Orchestra

| Job | Description |
|---|---|
| `PurgeAgendaActivity` | Purge des agendas expires (extends `AbstractActivityEngine`) |

### Features (@Feature)

| Flag | Paramètres | Composants |
|---|---|---|
| `foConsultation.db` | params… | `DbFoConsultationPlanningPlugin` |
| `foConsultation.redis` | params… | `RedisFoConsultationPlanningPlugin` |
| `foConsultation.redis2` | params… | `Redis2FoConsultationPlanningPlugin` |
| `foConsultation.redis2Unified` | params… | `RedisUnifiedFoConsultationPlanningPlugin` |
| `services.config` | 11 params (seuils de validation) | `PlanningServicesConfig` |

### Configuration YAML

```yaml
modules:
    io.vertigo.planning.PlanningFeatures:
        # Toujours actif : TraceAspect, ModelDefinitionProvider
    io.vertigo.planning.agenda.AgendaFeatures:
        featuresConfig:
            - services.config:
                  createMinDureePlageMinute: 60
                  createMaxDureePlageHeure: 10
            - foConsultation.redis2Unified:
                  __flags__: ["redis && redisCluster"]
                  distributedSynchro: true
```
