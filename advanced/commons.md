# Commons

Le module **Commons** est un module d'utilitaire. 
Il met a disposition des fonctions techniques transverses adaptés aux besoins spécifiques.
Il respecte le principe de modularité, et met en oeuvre le design pattern **Strategy** comme les autres modules Vertigo.

**Commons** propose plusieurs composants transverses sur les thèmes suivant :
- **Analytics** : Permet de suivre l'état du système, santé, métriques via le suivi des appels de process en activité, performance et erreur 
- **Cache** : Propose une abstraction vers la solution de cache pour les autres composants
- **Codec** : Transforme un objet en un autre (built-in codecs : HTML, SHA1, Base64, Compress, Serialize)
- **Daemon** : Permet de gérer les démons de l'application (au sens tache récurrente technique) : enregistrement simplifié, statistiques d'utilisation, protection de l'exécution
- **Eventbus** : Propose un Bus d'évenement simple, pour gérer les évenements dans l'application (ex : les évenements de mise à jour de données)
- **Node** : Permet une gestion simple de noeud d'exécution pour les applications en cluster (topologie, santé, config)
- **Config** : Abstrait l'accès à la configuration pour vos applications, et permet : surcharges, externalisation, aggrège plusieurs sources deconfiguration
- **Peg** : Signifie *Parsing Expression Grammars*, c'est un parser simple pour vos DSL (*Domain Specific Langage*)
- **Script** : Abstrait la solution d'execution de script au sein de l'application : transforme une String en code exécutable (parceque parfois, il faut mixer code et données)
- **Transaction** : Propose une gestion simple des transactions applicatives (pas forcément Base de Données) 

## Configuration

Les composants sont orthogonaux, habituellement ils sont utilisé par d'autres composants de plus haut niveau dans votre application.
Afin d'utiliser les fonctionnalités de **Commons** il est nécessaire d'ajouter ce module à la configuration de l'application.
Pour plus de détails, vous pouvez vous rapporter au chapitre dédié à la [configuration](/basic/configuration) de l'application.

Les composants suivants sont automatiquements démarrés avec le module Commons et possèdent un paramétrage par défaut qui peut être surchargé si besoin :
- **Analytics**
- **Codec**
- **Daemon**
- **EventBus**
- **Node**
- **Transaction**

Voici une configuration typique d'une application utilisant le module Account

```yaml
modules:
  io.vertigo.commons.CommonsFeatures:
    features:
      - script:
      - cache:
      - redis:
          host: ${redisHost}
          port: 6379
          database: 0
    featuresConfig:
      - script.janino:
      - cache.memory:
      - analytics.socketLoggerConnector:
          appName: mars-analytics
          hostName: ${analyticsHost}
```


### Features disponibles :
- **script**
- **cache**
- **redis**
  - `host` : Server redis
  - `port` : port du redis
  - `database` : nom de la database redis
  - `password` *Optionel* : mot de passe de connection

### Paramètres des Features 

- **script.janino** : Utilise la librairie Janino pour ce composant. *(Actuellement seule implémentation disponible)*
- **cache.redis** : Utilise le `RedisConnector` pour mettre en place un cache partagé *(Nécessite le composant Redis)*
- **cache.memory** : Utilise la mémoire locale comme implémentation du cache *(comme les autres implé, l'éviction en TTL définit par le module consommateur)*
- **cache.eh** : Utilise la librairie EhCache *(Necessite le fichier de paramétrage `ehcache.xml`)*
- **analytics.socketLoggerConnector** : Les données d'analytics sont envoyés en utilisant le connecteur log4j/log4j2 SocketAppender
  - `appName` *Optionel* : Nom de l'application
  - `hostName` *Optionel* : Serveur de collecte
  - `port` *Optionel* : Port de collecte (par défaut 4562 pour log4j2, mettre 4650 si vous utilisez log4j)
- **analytics.smartLoggerConnector** : Connecteur qui analyse le process d'execution et calcul les temps passés et les nombres d'appels
  - `aggregatedBy` *Optionel* : Définit la catégorie des sous-process à aggreger
  - `durationThreshold` (ms) *Optionel* : Seuil au delà duquel l'appel est loggué en erreur *(par défaut 1000ms)*
- **app.dbRegistry** : Utilise la base de données pour gérer les Nodes *(En interne, utilise un pool de connection C3P0)*
  - `driverClassName` : Nom du driver base de données (**Attention** : doit être dans le classpath)
  - `jdbcUrl` : Url de connection Jdbc
- **app.redisRegistry** : Utilise le `RedisConnector` pour gérer les Nodes *(Nécessite le composant Redis)*
- **app.httpInfos** : Permet de récupérer les informations des Nodes en HTTP *(via des Webservices REST)*

