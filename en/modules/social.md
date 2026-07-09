# Social

**Social** is a Vertigo platform module providing social functions.

It adds collaborative functions to your application to improve communication with and between your users.

It includes several sub-systems:

- **Notification**: Send notifications to your users without relying on third-party services.
- **Comment**: Unstructured information sharing spaces to improve the operational efficiency of the application.
- **Mail**: Send emails simply.
- **Handle**: (Beta feature) Associate meaningful handles with your application entities, enabling simplified external referencing and better navigation.

## Configuration

To use **Social** features, you must add this module to the application configuration.
For more details, see the chapter dedicated to application [configuration](/en/basic/configuration).

The **Account** module is required to use this module.

Here is a typical configuration of an application using the Social module:

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

### Available features

- **notifications**: Activates notification features
- **comments**: Activates comment features
- **mail**: Activates email sending features
- **handles**: Activates Handle features (**beta — not prod-ready**)

### Feature parameters

#### Notifications

- **notifications.redis**: Stores Notifications in Redis via the RedisConnector
  - connectorName *(optional)*: Name of the connector used (default `main`)
- **notifications.memory**: Stores Notifications in memory

#### Comments

- **comments.redis**: Stores Comments in Redis via the RedisConnector
  - connectorName *(optional)*: Name of the connector used (default `main`)
- **comments.memory**: Stores Comments in memory (**Warning**: Dev Only — no purge, no deletion API)

#### Mail

- **mail.javax**: Sends mail via the Javax.mail API through MailSessionConnector
  - connectorName *(optional)*: Name of the connector used (default `main`)
  - developmentMode: Boolean activating development mode (in this mode the recipient is overridden)
  - developmentMailTo: Email of the recipient for development mails
  - charset *(optional)*: Name of the charset used (default `ISO 8859-1`)

#### MailSessionConnector

The *Mail* feature requires a MailSessionConnector connector. Here are the proposed connectors:

- `JndiMailSessionConnector`: Connector for accessing the mail server using a JNDI resource.
  - connectorName *(optional)*: Name of the connector used (default `main`)
  - mail.session: JNDI name of the mail resource (must start with `java:comp/env`)
- `NativeMailSessionConnector`: Connector for accessing the mail server using the JDK implementation.
  - connectorName *(optional)*: Name of the connector used (default `main`)
  - storeProtocol: Protocol used (e.g.: `smtp`)
  - host: Mail server name (DNS or IP)
  - port *(optional)*: Network port
  - login *(optional)*: Login for mail server access
  - pwd *(optional)*: Password for mail server access

## Notification

### Principle

Notifications in a business application are used to:

- Quickly signal information (action by another user, return from asynchronous processing, …)
- Provide a shortcut to a business screen

!> It is important not to neglect notification design: what types exist, what URLs they target, what processes create them, what processes delete them, to whom they are sent, etc.
You must particularly consider the targetUrl which serves as functional identifier (you can complement the URL with # if needed).

?> It is possible to send Notifications from one SI to another (this is the benefit of shared Redis storage).

?> Notifications are global to users, but it is possible to keep per-user meta-data (such as read/unread status or to pin them).
Some projects have already implemented a daily summary mechanism to send an email recap of unread notifications.

### Usage

Using Notifications is simple:

- In a business process, a Notification is generated. Among its properties, the type determines the notification rendering (icon), and the targetUrl gives the URL that will be used to provide more information to the user (it also serves as functional identifier for deletion).
- The notification is sent to a list of users (via `void send(final Notification notification, final Set<UID<Account>> accountURIs)`).
- On the UI side, in Vertigo UI the `<v-notification>` component displays the notification list. Alternatively, a specific UI or Focus (under React) can use the `NotificationWebServices` WebApi.
- When a functional viewpoint indicates that the notification is no longer valid (case processed, item read, etc.), it can be removed for all users via `void removeAll(String type, String targetUrl)`.

!> Notifications should be treated as temporary elements. They have a lifetime (TTL: Time To Live): it is primarily a shortcut and a way to be quickly notified, but it is not a persistent signal. If it is lost, data must be accessible through another means.

#### API

##### NotificationManager

- **send(Notification, Set\<UID\<Account\>\>)**: Sends a notification to a set of users
- **getCurrentNotifications(UID\<Account\>)**: Retrieves a user's notifications
- **remove(UID\<Account\>, notificationUUID)**: Removes a notification for a user (does not affect other users)
- **removeAll(type, targetUrl)**: Removes all notifications by type and targetUrl
- **updateUserContent(UID\<Account\>, notificationUUID, userContent)**: Allows modifying (cancels and replaces) per-user information on a notification (tags or flags notion)

##### Notification

- **UUID uuid**: Unique identifier
- **String sender**: Sender label
- **String type**: Notification type (affects rendering)
- **String title**: Notification title
- **String content**: Notification content
- **int ttlInSeconds**: Notification lifetime (>&nbsp;0 or -1 for indefinite)
- **String targetUrl**: Target URL, for clicking the notification (can use #)
- **Instant creationDate**: Creation date (optional, default Instant.now)
- **Optional\<String\> userContentOpt**: Per-user specific content

Example of creating and sending a notification:

```java
final Notification notification = Notification.builder()
    .withSender("System") //we could keep the user who did this update
    .withTitle("Base updated")
    .withContent("Base " + base.getCode() + " information updated")
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

## For Experts

### Managers

| Manager | Role | Activated by |
|---|---|---|
| `NotificationManager` | User notification sending and reading | `notifications` |
| `CommentManager` | Comment space management | `comments` |
| `HandleManager` | Association of meaningful handles with entities | `handles` |
| `MailManager` | Email sending | `mail` |
| `SmsManager` | SMS sending | `sms` |

### Features (@Feature)

| Flag | Components |
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

| Plugin | Role | Feature |
|---|---|---|
| `RedisNotificationPlugin` | Notification storage in Redis | `notifications.redis` |
| `MemoryNotificationPlugin` | In-memory notification storage | `notifications.memory` |
| `RedisCommentPlugin` | Comment storage in Redis | `comments.redis` |
| `MemoryCommentPlugin` | In-memory comment storage | `comments.memory` |
| `RedisHandlePlugin` | Handle storage in Redis | `handles.redis` |
| `MemoryHandlePlugin` | In-memory handle storage | `handles.memory` |
| `JavaxMailPlugin` | Email sending via Javax.mail API | `mail.javax` |
| `OvhSmsSendPlugin` | SMS sending via OVH API | `sms.ovh` |
| `LinkMobilitySmsSendPlugin` | SMS sending via LinkMobility API | `sms.linkmobility` |

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
                  serviceName: "MyApp"
                  whitelistPrefixes: "..."
                  creditLeftThreshold: 10
            - sms.ovh.requestSpecializer:
                  appKey: "..."
                  appSecret: "..."
                  consumerKey: "..."
            - sms.linkmobility:
                  whitelistPrefixes: "..."
                  maxSmsPerMinute: 10
            - sms.linkmobility.requestSpecializer:
                  username: "..."
                  password: "..."
```