# Commons

Le module **Commons** est un module d'utilitaire. 
Il met a disposition des fonctions techniques transverses adaptés aux besoins spécifiques.
Il respecte le principe de modularité, et met en oeuvre le design pattern **Strategy** comme les autres modules Vertigo.

**Commons** propose plusieurs composants transverses sur les thèmes suivant :
- **Codec** : Transforme un objet en un autre (built-in codecs : HTML, SHA1, Base64, Compress, Serialize)
- **Eventbus** : Propose un Bus d'évenement simple, pour gérer les évenements dans l'application (ex : les évenements de mise à jour de données)
- **App** : Permet une gestion simple de noeud d'exécution pour les applications en cluster (topologie, santé, config)
- **Peg** : Signifie *Parsing Expression Grammars*, c'est un parser simple pour vos DSL (*Domain Specific Langage*)
- **Script** : Abstrait la solution d'execution de script au sein de l'application : transforme une String en code exécutable (parceque parfois, il faut mixer code et données)
- **Transaction** : Propose une gestion simple des transactions applicatives (pas forcément Base de Données) 

## Configuration

Les composants sont orthogonaux, habituellement ils sont utilisé par d'autres composants de plus haut niveau dans votre application.
Afin d'utiliser les fonctionnalités de **Commons** il est nécessaire d'ajouter ce module à la configuration de l'application.
Pour plus de détails, vous pouvez vous rapporter au chapitre dédié à la [configuration](/basic/configuration) de l'application.

Les composants suivants sont automatiquements démarrés avec le module Commons et possèdent un paramétrage par défaut qui peut être surchargé si besoin :
- **Codec**
- **EventBus**
- **App**
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


### Paramètres des Features 

- **script.janino** : Utilise la librairie Janino pour ce composant. *(Actuellement seule implémentation disponible)*

- **app.dbRegistry** : Utilise la base de données pour gérer les Nodes *(En interne, utilise un pool de connection C3P0)*
  - `driverClassName` : Nom du driver base de données (**Attention** : doit être dans le classpath)
  - `jdbcUrl` : Url de connection Jdbc
- **app.redisRegistry** : Utilise le `RedisConnector` pour gérer les Nodes *(Nécessite le composant Redis)*
- **app.httpInfos** : Permet de récupérer les informations des Nodes en HTTP *(via des Webservices REST)*

