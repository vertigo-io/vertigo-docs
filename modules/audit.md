# Module audit

**Audit** est un module Vertigo offrant deux capacités couplées :

- **Audit Trail** : Traçage et archivage des événements métier dans un ou plusieurs stores.
- **Ledger Blockchain Ethereum** : Ancrage de données sur une blockchain Ethereum pour garantir l'intégrité et la non-répudiation.

Le module s'intègre dans une application de Gestion de Projet, où la traçabilité des actions et la preuve d'ancrage sont critiques.

## Installation

### Ajout de la dépendance

```xml
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-audit</artifactId>
    <version>4.3.2</version>
</dependency>
```

### Dépendances

| Dépendance | Type | Usage |
|---|---|---|
| vertigo-core | Obligatoire | — |
| vertigo-datamodel | Obligatoire | — |
| vertigo-datastore | Optionnelle | Requise par StoreTraceStorePlugin |
| web3j | Optionnelle (4.13.0) | Requise par EthereumLedgerPlugin |

## Activation

Le module s'active exclusivement via les annotations `@Feature` dans la configuration YAML de `AuditFeatures`. Aucune méthode Java DSL n'est disponible.

| Feature YAML | Composants activés |
|---|---|
| `trace` | `TraceManager`, `TraceManagerImpl`, définitions DT/SmartTypes |
| `trace.memory` | `MemoryTraceStorePlugin` |
| `trace.store` | `StoreTraceStorePlugin` |
| `trace.log` | `LogTraceStorePlugin` |
| `ledger` | `LedgerManager` + `LedgerManagerImpl` |
| `ledger.ethereum` | `EthereumLedgerPlugin` (+`Activeable`) |
| `ledger.fake` | `FakeLedgerPlugin` |

Exemple YAML :

```yaml
modules:
    io.vertigo.audit.AuditFeatures:
        features:
            - trace:
            - ledger:
        featuresConfig:
            - trace.store:
            - trace.log:
            - ledger.fake:
```

---

## Audit Trail

### Principe

Le système de traces enregistre des événements métier de manière structurée. Chaque trace possède une catégorie, un utilisateur, une date métier optionnelle, une date d'exécution automatique, un identifiant URN d'objet métier, un message et un contexte optionnel.

Les traces sont écrites sur TOUS les plugins de storage configurés. La lecture s'opère sur le PREMIER plugin dont `isReadSupported` vaut `true`.

### API

#### TraceManager

Interface de type Manager exposant :

- `void addTrace(Trace trace)` : Écrit une trace sur tous les plugins configurés.
- `DtList<Trace> findTrace(TraceCriteria criteria)` : Retourne les traces correspondant aux critères.
- `Trace getTrace(Long idAuditTrace)` : Retourne une trace par son identifiant numérique.

#### Trace

Entity finale avec 8 champs :

| Champ | Type | Description |
|---|---|---|
| traId | Long | Identifiant auto-généré |
| category | String (100c) | Catégorie de la trace |
| username | String (100c) | Utilisateur ayant généré la trace |
| businessDate | Instant | Date métier (optionnel) |
| executionDate | Instant | Date d'exécution (auto) |
| itemUrn | String (250c) | URN de l'objet métier concerné |
| message | String (TEXT) | Message descriptif |
| context | String (TEXT) | Contexte au format pipe-separated |

#### TraceBuilder

Construction d'une Trace :

```java
new TraceBuilder(String category, String user, String itemUrn, String message)
```

Méthodes de configuration :

- `withDateBusiness(Instant)` : Définit la date métier.
- `withContext(List<String>)` : Définit le contexte (liste de chaînes, assemblées avec séparateur pipe).
- `build() -> Trace` : Retourne l'objet Trace.

#### TraceCriteriaBuilder

Construction des critères de recherche :

```java
TraceCriteria.builder()
```

Méthodes de filtrage (toutes optionnelles, cumulables) :

- `withDateExecutionStart(Instant)` / `withDateExecutionEnd(Instant)`
- `withDateBusinessStart(Instant)` / `withDateBusinessEnd(Instant)`
- `withCategory(String)`
- `withUsername(String)`
- `withItemUrn(String)`
- `build() -> TraceCriteria`

### Plugins TraceStorePlugin

Trois implémentations du SPI `TraceStorePlugin` :

| Plugin | Stockage | Lecture | Usage |
|---|---|---|---|
| MemoryTraceStorePlugin | ConcurrentHashMap + AtomicLong | Oui | Développement, tests |
| StoreTraceStorePlugin | Base SQL via EntityStoreManager (transactionnel) | Oui | Production |
| LogTraceStorePlugin | Log4j (logger "audit") | Non | Archivage complémentaire |

LogTraceStorePlugin lève `UnsupportedOperationException` sur toute opération de lecture (`read`, `findByCriteria`).

### Exemples — domaine Gestion de Projet

#### Création d'une trace

```java
final Trace trace = new TraceBuilder(
        "PROJET", "dupont.j", "PROJ-001", "Projet 'Migration SI' créé")
    .withDateBusiness(Instant.now())
    .withContext(Arrays.asList("priority=HIGH", "department=IT"))
    .build();
traceManager.addTrace(trace);
```

#### Recherche de traces

```java
final TraceCriteria criteria = TraceCriteria.builder()
    .withCategory("PROJET")
    .withDateBusinessStart(Instant.parse("2025-01-01T00:00:00Z"))
    .withDateBusinessEnd(Instant.parse("2025-12-31T23:59:59Z"))
    .build();
final DtList<Trace> results = traceManager.findTrace(criteria);
```

#### Recherche par utilisateur et URN

```java
final TraceCriteria criteria = TraceCriteria.builder()
    .withUsername("dupont.j")
    .withItemUrn("PROJ-001")
    .build();
final DtList<Trace> results = traceManager.findTrace(criteria);
```

#### Lecture d'une trace par identifiant

```java
final Trace trace = traceManager.getTrace(12345L);
```

---

## Ledger Blockchain Ethereum

### Principe

Le Ledger permet d'ancrer des données sur une blockchain Ethereum pour en garantir l'intégrité et la non-répudiation. Les données sont transmises en tant que chaîne de caractères.

Deux modes :

- **Ethereum** : Ancrage réel via un nœud Ethereum (web3j, RPC HTTP).
- **Fake** : Simulation, aucune opération réelle, solde toujours à zéro.

### API

#### LedgerManager

Interface de type Manager exposant :

- `String sendData(String data)` : Envoi synchrone. Retourne le hash hexadécimal de la transaction.
- `void sendDataAsync(String data, Runnable callback)` : Envoi asynchrone. Les appels sont accumulés dans une `ConcurrentLinkedQueue` et exécutés par un thread daemon toutes les 10 secondes. Le callback est invoqué après traitement.
- `BigInteger getWalletBalance(LedgerAddress ledgerAddress)` : Solde d'un portefeuille identifié par son adresse.
- `BigInteger getMyWalletBalance()` : Solde du portefeuille configuré comme local.

#### LedgerTransaction

Objet final immuable représentant une transaction blockchain. Champs (tous BigInteger sauf hash, blockHash, from, to, message qui sont String) :

| Champ | Type | Description |
|---|---|---|
| hash | String | Hash de la transaction |
| nonce | BigInteger | Nonce |
| blockHash | String | Hash du bloc |
| blockNumber | BigInteger | Numéro du bloc |
| from | String | Adresse émettrice |
| to | String | Adresse destinataire |
| value | BigInteger | Valeur transférée (wei) |
| message | String | Message hexadécimal |
| transactionIndex | BigInteger | Index dans le bloc |

#### LedgerTransactionBuilder

Builder fluide pour construire des objets `LedgerTransaction`.

#### LedgerTransactionEvent

Evenement EventBus, émis à chaque transaction reçue. L'écoute se fait avec l'annotation `@EventBusSubscribed`.

#### LedgerTransactionPriorityEnum

Cinq niveaux de priorité avec leur valeur en pour-mille :

| Valeur | Priorité | Multiplicateur |
|---|---|---|
| 5 | VERYSLOW | gasBase * 5 / 1000 |
| 50 | SLOW | gasBase * 50 / 1000 |
| 500 | MEDIUM | gasBase * 500 / 1000 |
| 650 | FAST | gasBase * 650 / 1000 |
| 1000 | VERYFAST | gasBase * 1000 / 1000 |

La formule de calcul est : `gasPrice = gasBase * priority / 1000`.

#### LedgerCredential

Paire d'authentification : `LedgerCredential(password, walletPath)`.

#### LedgerAddress

Record : `LedgerAddress(accountName, publicAddress)`.

### Plugins LedgerPlugin

Deux implémentations du SPI `LedgerPlugin` :

| Plugin | Type | Description |
|---|---|---|
| EthereumLedgerPlugin | Activeable | Connexion RPC HTTP via web3j |
| FakeLedgerPlugin | — | No-op, balance à zéro |

#### EthereumLedgerPlugin — paramètres

| Paramètre | Description |
|---|---|
| urlRpcEthNode | URL du nœud Ethereum RPC |
| myAccountName | Nom du compte local |
| myPublicAddr | Adresse publique du compte local |
| defaultDestAccountName | Nom du compte destinataire par défaut |
| defaultDestPublicAddr | Adresse publique du destinataire par défaut |
| walletPassword | Mot de passe du portefeuille |
| walletPath | Chemin vers le fichier wallet |

Calcul du gas : `gasPrice = gasBase * priority / 1000`. Une marge de 10% est ajoutée au gasLimit, sur le coût de stockage uniquement.

Le plugin écoute le flux `transactionFlowable` du nœud et publie les transactions sur l'EventBus via `LedgerTransactionEvent`.

### Exemples — domaine Gestion de Projet

#### Envoi synchrone

```java
final String hash = ledgerManager.sendData(
    "PROJET_CREATE:PROJ-001:Migration SI");
```

#### Envoi asynchrone avec callback

```java
ledgerManager.sendDataAsync(
    "PROJET_UPDATE:PROJ-001:etat=termine",
    () -> {
        // Action post-confirmation
        projetServices.updateProjetStatus(projetProjet, StatusEnum.TERMINE);
    }
);
```

#### Lecture de solde

```java
final BigInteger balance = ledgerManager.getMyWalletBalance();
final LedgerAddress archiveAddress = new LedgerAddress("archive", "0xDef456...");
final BigInteger partnerBalance = ledgerManager.getWalletBalance(archiveAddress);
```

#### Ecoute des transactions via EventBus

```java
@EventBusSubscribed
public void onLedgerTransaction(final LedgerTransactionEvent event) {
    final String message = event.getLedgerTransaction().getMessage();
    logger.info("Transaction confirmee : " + message);
}
```

---

## Configuration combinée

Scénario production : traces persistantes en base + archivage log + ledger Ethereum.

```yaml
modules:
    io.vertigo.audit.AuditFeatures:
        features:
            - trace:
            - ledger:
        featuresConfig:
            - trace.store:
            - trace.log:
            - ledger.ethereum:
                  ethereumRPCUrl: "http://eth-node:8545"
                  contractName: "gestion-projet"
                  contractAddress: "0xAbC123..."
                  ledgerName: "archive"
                  walletAddress: "0xDeF456..."
                  walletPassword: "secret"
                  walletPath: "/wallet/gestion-projet.p12"
```

Ce scénario trace chaque action dans la base de données, archive un journal log parallèle, et ancre les événements critiques sur la blockchain Ethereum.

Scénario développement : traces mémoire + ledger simulé.

```yaml
modules:
    io.vertigo.audit.AuditFeatures:
        features:
            - trace:
            - ledger:
        featuresConfig:
            - trace.memory:
            - ledger.fake:
```

## Pour les experts

### Managers
| Manager | Rôle | Activé par |
|---|---|---|
| `TraceManager` | Écriture et lecture de traces d'audit (audit trail) | `trace` |
| `LedgerManager` | Ancrage de données sur blockchain Ethereum (ou simulation) | `ledger` |

### Features (@Feature)
| Flag | Composants |
|---|---|
| `trace` | `TraceManager`, `TraceManagerImpl`, définitions DT/SmartTypes |
| `trace.memory` | `MemoryTraceStorePlugin` |
| `trace.store` | `StoreTraceStorePlugin` |
| `trace.log` | `LogTraceStorePlugin` |
| `ledger` | `LedgerManager` + `LedgerManagerImpl` |
| `ledger.ethereum` | `EthereumLedgerPlugin` (+`Activeable`) |
| `ledger.fake` | `FakeLedgerPlugin` |

### Plugins
| Plugin | Rôle | Feature |
|---|---|---|
| `MemoryTraceStorePlugin` | Stockage des traces en mémoire (dev/tests) | `trace.memory` |
| `StoreTraceStorePlugin` | Persistance transactionnelle via EntityStoreManager | `trace.store` |
| `LogTraceStorePlugin` | Archivage complémentaire via logger "audit" (écriture seule) | `trace.log` |
| `EthereumLedgerPlugin` | Ancrage réel via RPC HTTP web3j (Activeable) | `ledger.ethereum` |
| `FakeLedgerPlugin` | Simulation ledger, balance à zéro (dev/tests) | `ledger.fake` |

### Configuration YAML
```yaml
modules:
    io.vertigo.audit.AuditFeatures:
        features:
            - trace:
            - ledger:
        featuresConfig:
            - trace.store:
            - trace.log:
            - ledger.ethereum:
                  urlRpcEthNode: "http://eth-node:8545"
                  myAccountName: "gestion-projet"
                  myPublicAddr: "0xAbC123..."
                  defaultDestAccountName: "archive"
                  defaultDestPublicAddr: "0xDeF456..."
                  walletPassword: "..."
                  walletPath: "/path/to/wallet"
            - ledger.fake:
```
