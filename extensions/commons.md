# Commons

Le module **Commons** est un module d'utilitaire.
Il met a disposition des fonctions techniques transverses adaptés aux besoins spécifiques.
Il respecte le principe de modularité, et met en oeuvre le design pattern **Strategy** comme les autres modules Vertigo.

**Commons** propose plusieurs composants transverses sur les thèmes suivant :

- **Codec** : Transforme un objet en un autre via `CodecManager`, avec encodeurs/décodeurs parametrables (`Encoder<S,T>`, `Codec<S,T>`)
- **EventBus** : Propose un Bus d'événement simple pour gérer les événements dans l'application *(ex : les événements de mise à jour de données, pub/synchro)*
- **App** : Permet une gestion simple des nœuds d'exécution pour les applications en cluster *(topologie, santé, config)*
- **Command** : Exécution de commandes système via `CommandManager`
- **Peg** : Signifie *Parsing Expression Grammars*, c'est un parser simple pour vos DSL (*Domain Specific Langage*) avec `PegSolver`, `PegTerm`, `PegOperatorTerm`, `PegRule`, `PegAbstractRule`
- **Script** : Abstrait la solution d'exécution de script au sein de l'application : transforme une String en code exécutable *(parceque parfois, il faut mixer code et données)*
- **Transaction** : Propose une gestion simple des transactions applicatives *(pas forcément Base de Données)* via `VTransactionManager` et `VTransactionAspect`

## Configuration

Les composants sont orthogonaux, habituellement ils sont utilisés par d'autres composants de plus haut niveau dans votre application.
Afin d'utiliser les fonctionnalités de **Commons** il est nécessaire d'ajouter ce module à la configuration de l'application.
Pour plus de détails, vous pouvez vous rapporter au chapitre dédié à la [configuration](/basic/configuration) de l'application.

Les composants suivants sont automatiquement démarrés avec le module Commons et possèdent un paramétrage par défaut qui peut être surchargé si besoin :

- **Codec**
- **EventBus**
- **App**
- **Transaction**

Voici une configuration typique d'une application utilisant le module Commons :

```yaml
modules:
  io.vertigo.commons.CommonsFeatures:
    features:
      - script:
      - command:
    featuresConfig:
      - script.janino:
      - app.dbRegistry:
          driverClassName: org.postgresql.Driver
          jdbcUrl: jdbc:postgresql://localhost:5432/mydb
```

### Features disponibles :

- **script** : Active le `ScriptManager` pour l'exécution de scripts
- **command** : Active le `CommandManager` pour l'exécution de commandes système

### Paramètres des Features

- **script.janino** : Utilise la librairie Janino pour l'évaluation d'expressions *(Actuellement seule implémentation disponible)*
- **app.dbRegistry** : Utilise la base de données pour gérer les Nodes d'application *(En interne, utilise un pool de connection C3P0)*
  - `driverClassName` : Nom du driver base de données (**Attention** : doit être dans le classpath)
  - `jdbcUrl` : Url de connection Jdbc
- **app.redisRegistry** : Utilise le `RedisConnector` pour gérer les Nodes d'application *(Nécessite le composant Redis)*
- **app.httpInfos** : Permet de récupérer les informations des Nodes en HTTP *(via des WebServices REST)*

## Pour les experts

### Managers

| Manager | Impl | Activation |
|---|---|---|
| `AppManager` | `AppManagerImpl` | Toujours actif (`buildFeatures()`) |
| `CodecManager` | `CodecManagerImpl` | Toujours actif (`buildFeatures()`) |
| `CommandManager` | `CommandManagerImpl` | Feature `command` |
| `EventBusManager` | `EventBusManagerImpl` | Toujours actif (`buildFeatures()`) |
| `ScriptManager` | `ScriptManagerImpl` | Feature `script` |
| `VTransactionManager` | `VTransactionManagerImpl` | Toujours actif (`buildFeatures()`) |

### Features

| Flag | Params | Composants ajoutés |
|---|---|---|
| `script` | — | `ScriptManager` + `ScriptManagerImpl` |
| `script.janino` | — | `JaninoExpressionEvaluatorPlugin` |
| `app.dbRegistry` | `Param... params` | `DbAppNodeRegistryPlugin` |
| `app.redisRegistry` | — | `RedisAppNodeRegistryPlugin` |
| `app.httpInfos` | — | `HttpAppNodeInfosPlugin` |
| `command` | — | `CommandManager` + `CommandManagerImpl` |

### Plugins

**App Topology**
- `SingleAppNodeRegistryPlugin` — Registre local (toujours actif)
- `DbAppNodeRegistryPlugin` — Registre partagé en base de données
- `RedisAppNodeRegistryPlugin` — Registre partagé via Redis
- `HttpAppNodeInfosPlugin` — Découverte HTTP des nœuds

**Script**
- `JaninoExpressionEvaluatorPlugin` — Évaluateur d'expressions Janino

**PEG Parser**
- `PegSolver<S,I,R>` — ResolvingPEG expression grammar
- `PegRule<R>` / `PegAbstractRule<R,M>` — Règles de grammaire
- `PegTerm` / `PegOperatorTerm<T>` — Termes et opérateurs

### Configuration

Les composants de `buildFeatures()` sont toujours actifs : `CodecManager`, `EventBusManager`, `AppManager`, `VTransactionManager`, `VTransactionAspect`. Les autres composés sont activés par feature.
