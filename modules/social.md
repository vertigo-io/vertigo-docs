# Social

**Social** est un module de la plateforme Vertigo proposant des fonctions sociales.

Il ajoute des fonctions collaboratives à votre application pour améliorer la communication avec et entre vos utilisateurs.

Il inclut plusieurs sous-systèmes :

- **Notification** : Envoyer des notifications à vos utilisateurs sans recourir à des services tiers.
- **Comment** : Des espaces de partage d'informations non structurés pour améliorer l'efficacité opérationnelle de l'application.
- **Mail** : Envoyer des emails simplement.
- **Handle** : (Fonction en beta) Associer aux entités de votre application des handles significatifs permettant un référencement simplifié à l'extérieur de l'application ainsi qu'une meilleure navigation.

## Configuration

Pour utiliser les fonctionnalités de **Social**, il est nécessaire d'ajouter ce module à la configuration de l'application.
Pour plus de détails, voir le chapitre dédié à la [configuration](/basic/configuration) de l'application.

Le module **Account** est nécessaire pour utiliser ce module.

Voici une configuration typique d'une application utilisant le module Social :

```yaml
modules:
   io.vertigo.connectors.mail.MailFeatures:
       features:
           - javax.native:
                 storeProtocol: smtp
                 host: smtp.vertigo.io
   io.vertigo.social.SocialFeatures:
       features:
           - mail:
           - notifications:
           - comments:
           - webapi:
       featuresConfig:
           - mail.javax:
                 connectorName: 'default'
                 developmentMode: true
                 developmentMailTo: team@vertigo.io
                 charset: "UTF8"
           - notifications.redis:
           - comments.redis:
```

### Features disponibles

- **notifications** : Active les fonctionnalités de notification
- **comments** : Active les fonctionnalités de commentaire
- **mail** : Active les fonctionnalités d'envoi de mail
- **handles** : Active les fonctionnalités de Handle (**beta — non prod-ready**)

### Paramètres des Features

#### Notifications

- **notifications.redis** : Stockage des Notifications dans Redis via le RedisConnector
  - connectorName *(optionnel)* : Nom du connecteur utilisé (par défaut `main`)
- **notifications.memory** : Stockage des Notifications en mémoire

#### Comments

- **comments.redis** : Stockage des Commentaires dans Redis via le RedisConnector
  - connectorName *(optionnel)* : Nom du connecteur utilisé (par défaut `main`)
- **comments.memory** : Stockage des Commentaires en mémoire (**Attention** : Dev Only — pas de purge, ni API de suppression)

#### Mail

- **mail.javax** : Envoi de mail via l'API Javax.mail via des MailSessionConnector
  - connectorName *(optionnel)* : Nom du connecteur utilisé (par défaut `main`)
  - developmentMode : Booléen activant le mode développement (dans ce mode le destinataire est surchargé)
  - developmentMailTo : Email du destinataire des mails en développement
  - charset *(optionnel)* : Nom du charset utilisé (par défaut `ISO 8859-1`)

#### MailSessionConnector

La feature *Mail* requiert un connecteur MailSessionConnector. Voici les connecteurs proposés :

- `JndiMailSessionConnector` : Connecteur d'accès au serveur mail utilisant une ressource JNDI.
  - connectorName *(optionnel)* : Nom du connecteur utilisé (par défaut `main`)
  - mail.session : Nom JNDI de la ressource mail (doit commencer par `java:comp/env`)
- `NativeMailSessionConnector` : Connecteur d'accès au serveur mail utilisant l'implémentation du JDK.
  - connectorName *(optionnel)* : Nom du connecteur utilisé (par défaut `main`)
  - storeProtocol : Protocole utilisé (ex: `smtp`)
  - host : Nom du serveur mail (DNS ou IP)
  - port *(optionnel)* : Port réseau
  - login *(optionnel)* : Login d'accès au serveur mail
  - pwd *(optionnel)* : Mot de passe d'accès au serveur mail

## Notification

### Principe

Les notifications dans une application métier sont utilisées pour :

- Signaler rapidement une information (action d'un autre utilisateur, retour d'un traitement asynchrone, …)
- Proposer un raccourci vers un écran métier

!> Il est important de ne pas négliger la conception des notifications : quels types existent, quelles URL ciblent, quels processus les créent, quels processus les suppriment, à qui sont-elles envoyées, etc.
Il faut notamment réfléchir au targetUrl qui sert d'identifiant fonctionnel (on peut compléter l'URL avec des # si besoin).

?> Il est possible d'envoyer des Notifications d'un SI à un autre (c'est l'intérêt du stockage partagé Redis).

?> Les Notifications sont globales aux utilisateurs, mais il est possible de conserver des méta-données par utilisateur (comme un état lu/non lu ou pour les épingler).
Des projets ont déjà implémenté un mécanisme de résumé quotidien pour envoyer un récapitulatif par mail des notifications non lues.

### Utilisation

L'utilisation des Notifications est simple :

- Dans un traitement métier, on génère une Notification. Parmi ses propriétés, le type détermine le rendu de la notification (icône), et la targetUrl donne l'URL qui sera utilisée pour donner plus d'informations à l'utilisateur (elle servira aussi d'identifiant fonctionnel pour la suppression).
- La notification est envoyée à une liste d'utilisateurs (via `void send(final Notification notification, final Set<UID<Account>> accountURIs)`).
- Côté IHM, dans Vertigo UI le composant `<v-notification>` permet d'afficher la liste des notifications. Sinon une IHM spécifique ou Focus (sous React) peuvent utiliser la WebApi `NotificationWebServices`.
- Lorsqu'un point de vue fonctionnel indique que la notification n'est plus valide (dossier traité, élément lu, etc.), il est possible de la retirer pour tous les utilisateurs via `void removeAll(String type, String targetUrl)`.

!> Les notifications doivent être traitées comme des éléments temporaires. Elles possèdent une durée de vie (TTL : Time To Live) : c'est avant tout un raccourci et un moyen d'être rapidement notifié, mais ce n'est pas un signal persistant. Si elle est perdue, l'accès aux données doit être possible via un autre biais.

#### API

##### NotificationManager

- **send(Notification, Set\<UID\<Account\>\>)** : Envoie une notification à un ensemble d'utilisateurs
- **getCurrentNotifications(UID\<Account\>)** : Récupère les notifications d'un utilisateur
- **remove(UID\<Account\>, notificationUUID)** : Supprime une notification pour un utilisateur (n'affecte pas les autres utilisateurs)
- **removeAll(type, targetUrl)** : Supprime toutes les notifications par type et targetUrl
- **updateUserContent(UID\<Account\>, notificationUUID, userContent)** : Permet de modifier (annule et remplace) l'information par utilisateur sur une notification (notion de tags ou de flags)

##### Notification

- **UUID uuid** : Identifiant unique
- **String sender** : Libellé de l'émetteur
- **String type** : Type de la notification (affecte le rendu)
- **String title** : Titre de la notification
- **String content** : Contenu de la notification
- **int ttlInSeconds** : Durée de vie de la notification (>&nbsp;0 ou -1 pour indéfinie)
- **String targetUrl** : URL cible, pour le clic sur la notification (possibilité d'utiliser #)
- **Instant creationDate** : Date de création (optionnel, par défaut Instant.now)
- **Optional\<String\> userContentOpt** : Contenu spécifique par utilisateur

Exemple de création et envoi d'une notification :

```java
final Notification notification = Notification.builder()
    .withSender("System") //we could keep the user who did this update
    .withTitle("Base updated")
    .withContent("Base " + base.getCode() + " informations updated")
    .withTTLInSeconds(600)
    .withType("MARS-BASE") //should prefix by app, in case of multi-apps notifications
    .withTargetUrl("/mars/basemanagement/base/information/" + base.getBaseId()) //we may use a parameter to reference the good url
    .build();

//sendNotificationToAll(notification); //use with care, in a true app we should use security rules to get the users list
final Set<UID<Account>> accountUIDs = personServices.getPersons(DtListState.of(null))
    .stream()
    .map((person) -> UID.of(Account.class, String.valueOf(person.getPersonId())))
    .collect(Collectors.toSet());
notificationManager.send(notification, accountUIDs);
```

## Pour les experts

### Managers

| Manager | Rôle | Activé par |
|---|---|---|
| `NotificationManager` | Envoi et lecture de notifications utilisateur | `notifications` |
| `CommentManager` | Gestion des espaces de commentaires | `comments` |
| `HandleManager` | Association de handles significatifs aux entités | `handles` |
| `MailManager` | Envoi d'emails | `mail` |
| `SmsManager` | Envoi de SMS | `sms` |

### Features (@Feature)

| Flag | Composants |
|---|---|
| `notifications` | `NotificationManager` |
| `notifications.redis` | `RedisNotificationPlugin` |
| `notifications.memory` | `MemoryNotificationPlugin` |
| `comments` | `CommentManager` |
| `comments.redis` | `RedisCommentPlugin` |
| `comments.memory` | `MemoryCommentPlugin` |
| `handles` | `HandleManager` |
| `handles.redis` | `RedisHandlePlugin` |
| `handles.memory` | `MemoryHandlePlugin` |
| `mail` | `MailManager` |
| `mail.javax` | `JavaxMailPlugin` |
| `sms` | `SmsManager` |
| `sms.ovh` | `OvhSmsSendPlugin` + `OvhSmsWebServiceClient` |
| `sms.ovh.requestSpecializer` | `OvhRequestSpecializer` |
| `sms.linkmobility` | `LinkMobilitySmsSendPlugin` + `LinkMobilitySmsWebServiceClient` |
| `sms.linkmobility.requestSpecializer` | `LinkMobilityRequestSpecializer` |
| `webapi` | `AccountWebServices`, `NotificationWebServices`, `CommentWebServices`, `HandleWebServices` |

### Plugins

| Plugin | Rôle | Feature |
|---|---|---|
| `RedisNotificationPlugin` | Stockage des notifications dans Redis | `notifications.redis` |
| `MemoryNotificationPlugin` | Stockage des notifications en mémoire | `notifications.memory` |
| `RedisCommentPlugin` | Stockage des commentaires dans Redis | `comments.redis` |
| `MemoryCommentPlugin` | Stockage des commentaires en mémoire | `comments.memory` |
| `RedisHandlePlugin` | Stockage des handles dans Redis | `handles.redis` |
| `MemoryHandlePlugin` | Stockage des handles en mémoire | `handles.memory` |
| `JavaxMailPlugin` | Envoi de mail via API Javax.mail | `mail.javax` |
| `OvhSmsSendPlugin` | Envoi de SMS via l'API OVH | `sms.ovh` |
| `LinkMobilitySmsSendPlugin` | Envoi de SMS via l'API LinkMobility | `sms.linkmobility` |

### Configuration YAML

```yaml
modules:
   io.vertigo.social.SocialFeatures:
       features:
           - notifications:
           - comments:
           - handles:
           - mail:
           - sms:
           - webapi:
       featuresConfig:
           - notifications.redis:
                 connectorName: "main"
           - comments.redis:
                 connectorName: "main"
           - handles.redis:
                 connectorName: "main"
           - mail.javax:
                 connectorName: "default"
                 developmentMode: true
                 developmentMailTo: "team@vertigo.io"
                 charset: "UTF-8"
            - sms.ovh:
                  appKey: "..."
                  appSecret: "..."
                  consumerKey: "..."
                  serviceName: "MonApp"
                  whitelistPrefixes: "..."
                  creditLeftThreshold: 10
            - sms.linkmobility:
                  username: "..."
                  password: "..."
                  smsSender: "MonApp"
                  whitelistPrefixes: "..."
                  maxSmsPerMinute: 10
```
