# Commons

**vertigo-commons** regroupe les composants transverses de la plateforme : gestion des codecs, bus d'événements, découverte de topologie, exécution de scripts, système de commandes, gestion transactionnelle et moteur de parsing PEG.

Les composants sont orthogonaux et sont généralement consommés par des modules de plus haut niveau. L'activation se fait par features YAML ou par l'API Java.

Cinq composants sont démarrés automatiquement : CodecManager, EventBusManager, AppManager, VTransactionManager et VTransactionAspect. Les autres nécessitent une déclaration de feature.

---

## Codec

Le `CodecManager` centralise treize encodeurs/décodeurs thread-safe et sans état.

### Principe

Deux interfaces structurent le codec :
- `Codec<S,T>` — transformation bijective (encode + decode)
- `Encoder<S,T>` — transformation unidirectionnelle (encode)

Chaque codec est instancié une seule fois, puis réutilisé sans contention. Les codecs gèrent automatiquement les valeurs null via le décorateur `NullCodec`.

### Codecs disponibles

| Catégorie | Codecs |
|---|---|
| **Encodage Texte** | HTML, Base64 URL-safe, Base64 Legacy |
| **Crypto** | TripleDES, AES-128 |
| **Hachage** | MD5, SHA-1, SHA-256 |
| **Format** | Hex, CSV |
| **Sérialisation** | Serialization, CompressedSerialization |
| **Compression** | Compression (GZIP) |

### Activation

Aucune déclaration requise. Le composant est activé automatiquement au démarrage du module.

---

## EventBus

Le `EventBusManager` implémente un bus d'événements synchrone, intra-machine, sur le modèle pub/sub.

### Principe

Le flux est le suivant :
1. Un événement implémente l'interface marqueur `Event`
2. Un subscriber annote une méthode `void onXxx(MonEvenement e)` avec `@EventBusSubscribed`
3. L'annotation déclenche l'enregistrement automatique au démarrage
4. `post()` dispatche l'événement de manière synchrone à tous les subscribers
5. Si aucun subscriber n'est trouvé, l'événement est routé vers le gestionnaire `registerDead`

### Annotations

|Annotation|Cible|Rôle|
|---|---|---|
|`@EventBusSubscribed`|Méthode|Enregistre automatiquement la méthode comme subscriber. La signature doit être `void(MonEvent)`|

### Activation

Aucune déclaration requise. Le composant est activé automatiquement au démarrage du module.

---

## App

L'`AppManager` gère la topologie des nœuds d'exécution dans un environnement multi-nœuds.

### Principe

Chaque nœud est représenté par un `AppNode` (id, nom d'application, dernier statut, dernier contact, date de démarrage, point d'entrée, compétences). Un heartbeat de 60 secondes est émis périodiquement. Un nœud est considéré mort après deux heartbeats manqués (soit 120 secondes).

La découverte repose sur deux chaînes de plugins extensibles :
- **Registry** — registre des nœuds (stocke la liste des nœuds actifs)
- **Infos** — source d'informations détaillées par nœud

### Plugins Registry

| Plugin | Topologie | Rôle |
|---|---|---|
| `SingleAppNodeRegistryPlugin` | Activé par défaut | Registre local en mémoire (mononœud) |
| `DbAppNodeRegistryPlugin` | Feature `app.dbRegistry` | Registre partagé via JDBC (pool C3P0, table `V_NODE`) |
| `RedisAppNodeRegistryPlugin` | Feature `app.redisRegistry` | Registre partagé via Redis (dépend `RedisConnector`) |

### Plugins Infos

| Plugin | Feature | Rôle |
|---|---|---|
| `HttpAppNodeInfosPlugin` | `app.httpInfos` | Récupération des nœuds distants via REST HTTP (timeout 500 ms) |

### Plugin personnalisé

L'API Java expose deux méthodes sur `CommonsFeatures` pour injecter des plugins sans feature YAML :
- `withNodeRegistryPlugin(Class<? extends AppNodeRegistryPlugin>, Param...)`
- `withNodeInfosPlugin(Class<? extends AppNodeInfosPlugin>, Param...)`

### Activation

Aucune déclaration requise pour le registre local. Les fonctionnalités `app.dbRegistry`, `app.redisRegistry` et `app.httpInfos` nécessitent une feature.

Le plugin `DbAppNodeRegistryPlugin` nécessite le paramétrage du driver JDBC et de l'URL de connexion. Le plugin `RedisAppNodeRegistryPlugin` nécessite un `RedisConnector` actif.

---

## Command

Le `CommandManager` gère l'exécution de **commandes applicatives** — des opérations métier exposées comme des entrées de commande.

### Principe

Une commande applicative est une méthode annotée `@Command(handle, description, questions)` qui :
1. Accepte des paramètres de type `String` ou `GenericUID<O>`
2. Retourne un `CommandResponse<P>` construisant le statut (OK/KO), le texte d'affichage, une charge utile optionnelle, et une URL cible

Le `CommandManagerImpl` découvre automatiquement les méthodes annotées, assemble leur définition (`CommandDefinition` avec le préfixe `Cmd`), et les exécute avec validation des paramètres. Le builder `CommandResponseBuilder<P>` simplifie la construction du résultat.

### Annotations

| Annotation | Cible | Rôle |
|---|---|---|
| `@Command` | Méthode | Déclare une méthode comme commande applicative. Attributs : `handle` (identifiant), `description`, `questions` (paramètres attendus) |

### Types

| Type | Rôle |
|---|---|
| `CommandResponse<P>` | Record : `status` (enum OK/KO), `display`, `payload`, `targetUrl` |
| `CommandResponseStatus` | Enum : OK, KO |
| `CommandResponseBuilder<P>` | Constructeur fluide pour `CommandResponse` |
| `GenericUID<O>` | Identifiant absolu de ressource (URN, type, identifiant sérialisable) |
| `CommandParam` | Record décrivant un paramètre de commande (type reflété) |
| `CommandDefinition` | Définition d'une commande (`@DefinitionPrefix("Cmd")`) |

### Activation

Feature `command` requise.

---

## Script

Le `ScriptManager` permet d'évaluer des scripts textuels mélangeant du code Java et des données, avec injection de paramètres fortement typés.

### Principe

Un script est un texte contenant des balises délimitées. Le `ScriptParser` analyse le texte séquence par séquence et délègue chaque segment code à l'implémentation sélectionnée :
1. Les séparateurs sont configurables via `SeparatorType` (XML `<% %>`, CLASSIC, XML_CODE `<# #>`)
2. Le parser appelle un `ScriptParserHandler` par bloc d'expression et par bloc textuel
3. `ScriptEvaluator` coordonne Parser → Handler → Compilateur runtime
4. Le compilateur implémente `ExpressionEvaluatorPlugin` (interface `evaluate(expression, params, type)`)

Les paramètres sont injectés via `ExpressionParameter` (nom, type, valeur).

### Annotations

Aucune annotation. L'intégration repose sur le plugin `ExpressionEvaluatorPlugin`.

### Activation

Feature `script` requise. La feature `script.janino` ajoute l'implémentation Janino (seule implémentation fournie).

---

## Transaction

Le `VTransactionManager` orchestre les transactions applicatives avec propagation REQUIRED, hooks de cycle de vie et gestion de ressources priorisées.

### Principe

Le modèle supporte :
- Les transactions thread-local avec support du nesting
- La propagation REQUIRED via `@Transactional`
- L'enregistrement de ressources (`VTransactionResource`) avec priorité TOP ou NORMAL
- Des hooks `beforeCommit` et `afterCompletion` (committed ou rollback)
- Une journalisation via `VTransactionListener` (implémentation `VTransactionListenerImpl` avec log4j trace)

La machine d'état interne distingue les états ALIVE et CLOSED.

### Interfaces

| Interface | Rôle |
|---|---|
| `VTransactionManager` | Crée, récupère et vérifie les transactions courantes (`createCurrentTransaction`, `createAutonomousTransaction`, `getCurrentTransaction`, `hasCurrentTransaction`) |
| `VTransaction` | Transaction en lecture : `addResource`, `getResource`, `addBeforeCommit`, `addAfterCompletion` |
| `VTransactionWritable` | Extend `VTransaction` pour écrire : `commit`, `rollback`, `close` |
| `VTransactionResource` | Ressource inscrite à une transaction : `commit`, `rollback`, `close` |
| `VTransactionResourceId<R>` | Identifiant de ressource avec `Priority` (TOP > NORMAL) |
| `VTransactionAfterCompletionFunction` | Fonction `@FunctionalInterface` : `afterCompletion(boolean committed)` |

### Annotations

| Annotation | Cible | Rôle |
|---|---|---|
| `@Transactional` | Méthode ou classe | Aspect `@AspectAnnotation` activant la propagation REQUIRED sur méthode ou classe entière. Appliqué par `VTransactionAspect` |

### Activation

Aucune déclaration requise. `VTransactionManager` et `VTransactionAspect` sont activés automatiquement au démarrage du module. L'aspect `VTransactionAspect` est nécessaire pour que `@Transactional` prenne effet.

---

## PEG Parser

Le package `io.vertigo.commons.peg` fournit un moteur de *Parsing Expression Grammars* combinatoire pour construire des parsers de DSL. Il s'agit d'une bibliothèque utilitaire — aucun composant n'y est inscrit en tant que feature Vertigo.

### Principe

Le PEG Parser repose sur une composition de règles via la factory statique `PegRules` :
- **Règles atomiques** : `term()`, `word()`, `blanks()`, `skipBlanks()`
- **Règles compositionnelles** : `named()`, `optional()`, `sequence()`, `choice()`, `zeroOrMore()`, `oneOrMore()`
- **Règles différées** : `delayedOperation()`, `delayedComparison()`, `delayedOperationAndComparison()` (évaluation Shunting Yard)
- **Utils** : `parseAll()` pour un parsing complet, `namedRulesAsHtml()` pour le rendu HTML d'une grammaire

Chaque `PegRule<R>` expose `getExpression()` pour la représentation textuelle et `parse(text, start)` pour l'exécution. Le résultat est un `PegResult<R>` (index final, valeur parse, meilleure règle incomplète en cas d'erreur).

Les erreurs génèrent `PegNoMatchFoundException` avec le contexte et une pile d'erreurs inversée. Le debugging se fait via `PegLogger` (désactivé par défaut, `DISABLED = true`).

### Termes et opérateurs

L'interface `PegTerm` (méthode `getStrValues()`) est implémentée par six énumérations prédéfinies :

| Enum | Valeurs | Rôle |
|---|---|---|
| `PegCompareTerm` | LTE, GTE, NEQ, EQ, LT, GT | Opérateurs de comparaison |
| `PegBracketsTerm` | OPEN `(`, CLOSE `)` | Parenthèses |
| `PegBoolOperatorTerm` | OR (prio 1), AND (prio 2) | Opérateurs booléens |
| `PegArithmeticsOperatorTerm` | PLUS/MINUS, MULTIPLY/DIVIDE | Opérateurs arithmétiques |

L'interface `PegOperatorTerm<T>` décrit un opérateur binaire avec priorité et méthode `apply(left, right)`.

Le helper `PegEnumRuleHelper` simplifie la construction de règles sur les enums `PegTerm`.

### Solver

`PegSolver<S,I,R>` (interface fonctionnelle) encapsule une transformation raw → qualified via `PegSolver.PegSolverFunction<S,I>` qui expose `identity()` comme fonction identité.

### Types

| Type | Rôle |
|---|---|
| `PegRule<R>` | Règle : `getExpression()`, `parse(text, start)` |
| `PegRule.Dummy` | Singleton pour les règles sans résultat |
| `PegAbstractRule<R,M>` | Wrapper déléguant à une règle principale |
| `PegRules` | Factory statique (constructeur privé) avec 18+ méthodes de construction |
| `PegResult<R>` | Résultat : index, valeur, meilleure règle incomplète |
| `PegChoice` | Résultat de choix : index + valeur |
| `PegNoMatchFoundException` | Exception avec contexte et pile d'erreurs |
| `PegParsingValueException` | Exception de valeur non parsable |

### Règles PEG détaillées

| Règle | Signature | Rôle |
|---|---|---|
| `PegRules.named()` | `(name, rule)` | Étiquette une règle, retourne une `PegGrammarRule` |
| `PegRules.optional()` | `(rule)` | Match 0 ou 1 occurrence |
| `PegRules.term()` | `(terms)` | Match un `PegTerm` |
| `PegRules.sequence()` | `(rules...)` | Chaînage séquentiel |
| `PegRules.choice()` | `(rules...)` | Match la première règle réussie, retourne un `PegChoice` |
| `PegRules.zeroOrMore()` | `(rule, untilEnd)` | Match 0 ou plus (`*`) |
| `PegRules.oneOrMore()` | `(rule, untilEnd)` | Match 1 ou plus (`+`) |
| `PegRules.parseAll()` | `(rule)` | Vérifie que tout le texte est consommé |
| `PegRules.word()` | `(chars, mode)` | Chaîne de caractères reconnue (`PegWordRuleMode`) |
| `PegRules.blanks()` | `(blanks)` | Blancs (espace, tabulation ; par défaut " \t") |
| `PegRules.skipBlanks()` | `(blanks)` | Blancs et retours chariot (par défaut " \t\n\r") |
| `PegRules.operation()` | `(operators, term)` | Expressions avec opérateurs (évaluation immédiate) |
| `PegRules.delayedOperation()` | `(operators, term)` | Expressions avec opérateurs (évaluation différée) |
| `PegRules.delayedOperationAndComparison()` | — | Expressions arithmétiques + comparaisons combinées |
| `PegRules.comparison()` | — | Comparaison immédiate |
| `PegRules.delayedComparison()` | — | Comparaison différée |
| `PegRules.namedRulesAsHtml()` | `(rules...)` | Rendu HTML d'une grammaire |

### Activation

Aucune feature — les classes PEG sont directement utilisables via import. L'intégration se fait par dépendance Maven du module vertigo-commons.

---

## Configuration

Les composants sont orthogonaux. Voici une configuration typique activant les features optionnelles :

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

La feature `script.janino` nécessite la feature parente `script`. La feature `app.dbRegistry` nécessite un driver JDBC sur le classpath. La feature `app.redisRegistry` nécessite un `RedisConnector` déclaré en amont.

---

## Vigilance

- **`@Transactional` sans aspect** : L'annotation seule n'a aucun effet. Le composant `VTransactionAspect` doit être actif (ce qui est le cas par défaut). Ne pas le supprimer de la configuration.
- **PegLogger désactivé par défaut** : Le debugging PEG est désactivé (`DISABLED = true`). L'activer en production a un coût de performance significatif.
- **Commands applicatives ≠ commandes système** : `@Command` déclare des opérations métier, pas des exécutions shell. Le `CommandManager` ne lance aucun processus OS.
- **Priorité des ressources transactionnelles** : Lors du commit, les ressources TOP sont validées avant les ressources NORMAL. Lors du rollback, l'ordre est inversé.
- **Base64 URL-safe vs Legacy** : Le module expose deux codecs Base64 : URL-safe et Legacy (compatible RFC 2045). Ne pas les mélanger dans une même chaîne d'échange.
- **Registry mono par nœud** : Un seul plugin registry est actif par nœud. `SingleAppNodeRegistryPlugin` est actif par défaut et suffit pour les applications mononœud. Les plugins DB et Redis sont destinés aux topologies multi-nœuds.
- **Janino — implémentation unique** : Actuellement, `JaninoExpressionEvaluatorPlugin` est le seul implémentant `ExpressionEvaluatorPlugin`. Toute personnalisation du moteur d'évaluation nécessite de développer un plugin dédié.

---

## Pour les experts

### Managers

| Manager | Impl | Activation |
|---|---|---|
| `AppManager` | `AppManagerImpl` | Automatique (`buildFeatures()`) |
| `CodecManager` | `CodecManagerImpl` | Automatique (`buildFeatures()`) |
| `CommandManager` | `CommandManagerImpl` | Feature `command` |
| `EventBusManager` | `EventBusManagerImpl` | Automatique (`buildFeatures()`) |
| `ScriptManager` | `ScriptManagerImpl` | Feature `script` |
| `VTransactionManager` | `VTransactionManagerImpl` | Automatique (`buildFeatures()`) |

### Features

| Flag | Params | Composants ajoutés |
|---|---|---|
| *(buildFeatures) | — | `CodecManager`, `EventBusManager`, `AppManager`, `VTransactionManager`, `VTransactionAspect` |
| `script` | — | `ScriptManager`, `ScriptManagerImpl` |
| `script.janino` | — | `JaninoExpressionEvaluatorPlugin` |
| `command` | — | `CommandManager`, `CommandManagerImpl` |
| `app.dbRegistry` | `driverClassName`, `jdbcUrl` | `DbAppNodeRegistryPlugin` |
| `app.redisRegistry` | — | `RedisAppNodeRegistryPlugin` |
| `app.httpInfos` | — | `HttpAppNodeInfosPlugin` |

### Plugins

**App Topology**
- `SingleAppNodeRegistryPlugin` — registre local en mémoire (défaut)
- `DbAppNodeRegistryPlugin` — registre partagé via JDBC (pool C3P0)
- `RedisAppNodeRegistryPlugin` — registre partagé via Redis
- `HttpAppNodeInfosPlugin` — découverte de nœuds par REST HTTP (500 ms)

**Script**
- `JaninoExpressionEvaluatorPlugin` — évaluation d'expressions Java runtime via Janino

**Codec**
- `NullCodec<S,T>` — décorateur null-safe autour de tout `Codec`
- 13 codecs : HTML, Base64 URL/Legacy, TripleDES, AES-128, Compression, Serialization, CompressedSerialization, CSV, MD5, SHA-1, SHA-256, Hex

### Annotations

| Annotation | Cible | Module concerné |
|---|---|---|
| `@Command` | Méthode | Command |
| `@EventBusSubscribed` | Méthode | EventBus |
| `@Transactional` | Méthode | Transaction |

---


