# Social

**Social** est une extension Vertigo proposant des fonctions sociales.

Elle ajoute des fonctions collaboratives à votre application pour améliorer la communication avec et entre vos utilisateurs.

Elle inclut plusieurs modules :

- **Notification** : Envoyer des notifications à vos utilisateurs sans recourir à des services tiers.
- **Comment** : Des espaces de partage d'informations non structurés pour améliorer l'efficacité opérationnelle de l'application
- **Mail** : Envoyer des emails très simplement
- **Handle** : (Fonction en beta) : Associer aux entités de votre application des 'handle' signifiants permettant un référencement simplifié à l'exterieur de l'application ainsi qu'une meilleure navigation au sein de l'application.

## Configuration

Afin d'utiliser les fonctionnalités de **Social** il est nécessaire d'ajouter ce module à la configuration de l'application.
Pour plus de détails, vous pouvez vous rapporter au chapitre dédié à la [configuration](/basic/configuration) de l'application.

Le module **Account** est nécessaire pour utiliser ce module.

Voici une configuration typique d'une application utilisant le module Social

```yaml
modules
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

### Features disponibles :
- **notifications** : Active les fonctionnalités de notification
- **comments** : Active les fonctionnalités de commentaire
- **mail** : Active les fonctionnalités d'envoi de mail
- **handles** : Active les fonctionnalités de Handle (**beta** : *non prod-ready*)

### Paramètres des Features 

#### Notifications
- **notifications.redis** : Stockage des *Notification* dans Redis via le *RedisConnector*
  - connectorName *(optionel)* : Nom du connecteur utilisé (par défaut `main`)
- **notifications.memory** : Stockage des *Notification* en mémoire

#### Comments
- **comments.redis** : Stockage des *Commentaires* dans Redis via le *RedisConnector*
  - connectorName *(optionel)* : Nom du connecteur utilisé (par défaut `main`)
- **comments.memory** : Stockage des *Commentaires* en mémoire (**Attention** : Dev Only : pas de purge, ni api de suppression)

#### Mail
- **mail.javax** : Envoie de mail via l'api Javax.mail via des *MailSessionConnector*
  - connectorName *(optionel)* : Nom du connecteur utilisé (par défaut `main`)
  - developmentMode : Booleen activant le mode développement (dans ce mode le destinataire est surchargé)
  - developmentMailTo  : EMail du destinataire des mails en développement
  - charset *(optionel)* : Nom du charset utilisé (par défaut `ISO 8859-1`)

#### MailSessionConnector

La feature *Mail* requière un connecteur MailSessionConnector, voici les connecteurs proposés : 

- `JndiMailSessionConnector` : Connecteur d'accès au serveur mail utilisant une resource Jndi.
  - connectorName *(optionel)* : Nom du connecteur utilisé (par défaut `main`)
  - mail.session : Nom JNDI de la resource mail (doit commencer par `java:comp/env`)
- `NativeMailSessionConnector` : Connecteur d'accès au serveur mail utilisant l'implémentation du Jdk.
  - connectorName *(optionel)* : Nom du connecteur utilisé (par défaut `main`)
  - storeProtocol : Protocol utilisé (ex : `smtp`)
  - host : Nom du serveur mail (dns ou ip)
  - port *(optionel)* : Port réseau
  - login *(optionel)* : Login d'accès au serveur mail
  - pwd *(optionel)* : Password d'accès au serveur mail
  
  
## Notification

### Principe

Les notifications dans une application métier sont utilisées pour :
- signaler rapidement une information (action d'un autre utilisateur, retour d'un traitement asynchrone, ...)
- proposer un racourci vers un écran métier

!> Il est important de ne pas négliger la conception des notifications : quels types existent, quels url en cible, quels process les crées, quels process les supprimes, à qui sont-elles envoyées, ...
   Il faut notament réfléchir au targetUrl qui sert d'id fonctionnel (on peut compléter l'url avec des # si besoin)

?> Il est possible d'envoyer des Notifications d'un SI à un autre (c'est l'interet du stockage partagé Redis)

?> Les Notifications sont globales aux utilisateurs, mais il est possible de conserver des méta-données par utilisateurs (comme un état *lue/non lue* ou pour l'*épingler*)
   Des projets ont déjà implémentés un mecanisme de résumer quotidien pour envoyer un récapitulatif par mail des notifications non lues


### Utilisation

L'utilisation des Notifications est assez simple : 
- Dans un traitement métier, on génère une Notification. Parmi ces propriétés, le type détermine le rendu de la notification (icone), et la targetUrl donne l'url qui sera utilisée pour donner plus d'info à l'utilisateur (elle servira aussi d'identifiant fonctionnel pour la suppression, cf ci dessous)
- La notification est envoyée à une liste d'utilisateur (via `void send(final Notification notification, final Set<UID<Account>> accountURIs);`)
- Coté IHM, dans Vertigo-ui le composant <v-notification> permet d'afficher la liste des notifications, sinon une IHM spécifique ou Focus (sous react) peuvent utiliser la WebApi `NotificationWebServices`
- Lorsque d'un point de vue fonctionnelle la notification n'est plus valide (dossier traité, élément lu, etc..), il est possible de la retirer pour tous les utilisateurs via `void removeAll(String type, String targetUrl);`
	
!> Les notifications doivent être traitées comme des notifications temporaires, elles possèdent une durée de vie (TTL : Time To Live) : c'est avant tout un raccourci et un moyen d'être rapidement notifié, mais ce n'est pas un signal persistant, si elle est perdue l'accès aux données doit être possible via un autre bias.

#### API

##### NotificationManager
- **send(Notification, Set<UID<Account>>)** : Envoi une notification à un ensemble d'utilisateur
- **getCurrentNotifications(UID<Account>)** : Récupère les notifications d'un utilisateur
- **remove(UID<Account>,notificationUUID)** : Supprime une notification pour un utilisateur (n'affecte pas les autres utilisateurs)
- **removeAll(type, targetUrl)** : Supprime toutes les notifications par type et targetUrl
- **updateUserContent(UID<Account>,notificationUUID,userContent)** : Permet de modifier (annule et remplace) l'information par utilisateur sur une notification (notion de tags ou de flags)

##### Notification
- **UUID uuid** : Identifiant unique
- **String sender** : Libellé de l'émetteur 
- **String type** : Type de la notification (affecte le rendu)
- **String title** : Titre de la notification
- **String content** : Contenu de la notification
- **int ttlInSeconds** : Durée de vie de la notification ( >0 ou -1 pour indéfinie)
- **String targetUrl** : Url cible, pour le click sur la notif (possibilité d'utiliser #)
- **Instant creationDate** : Date de création (optionnel par défaut Instant.now)
- **Optional<String> userContentOpt** : Contenu spécifique par utilisateur

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
