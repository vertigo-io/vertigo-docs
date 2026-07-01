# Audit module

**Audit** is a Vertigo module offering two coupled capabilities:

- **Audit Trail**: Tracing and archiving of business events in one or more stores.
- **Ethereum Blockchain Ledger**: Anchoring data on an Ethereum blockchain to guarantee integrity and non-repudiation.

The module integrates into a Project Management application, where action traceability and anchoring proof are critical.

## Installation

### Adding the dependency

```xml
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-audit</artifactId>
    <version>4.3.2</version>
</dependency>
```

### Dependencies

| Dependency | Type | Usage |
|---|---|---|
| vertigo-core | Mandatory | — |
| vertigo-datamodel | Mandatory | — |
| vertigo-datastore | Optional | Required by StoreTraceStorePlugin |
| web3j | Optional (4.13.0) | Required by EthereumLedgerPlugin |

## Activation

The module is activated via `@Feature` annotations in the YAML configuration of `AuditFeatures`. Java DSL methods also exist (`withTrace()`, `withLedger()`, `withEthereumBlockChain(Param...)`, etc.) but are not recommended: prefer YAML.

| Feature YAML | Components activated |
|---|---|
| `trace` | `TraceManager`, `TraceManagerImpl`, DT/SmartType definitions |
| `trace.memory` | `MemoryTraceStorePlugin` |
| `trace.store` | `StoreTraceStorePlugin` |
| `trace.log` | `LogTraceStorePlugin` |
| `ledger` | `LedgerManager` + `LedgerManagerImpl` |
| `ledger.ethereum` | `EthereumLedgerPlugin` (+`Activeable`) |
| `ledger.fake` | `FakeLedgerPlugin` |

Example YAML:

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

### Principle

The trace system records business events in a structured manner. Each trace has a category, a user, an optional business date, an automatic execution date, a business object URN identifier, a message, and an optional context.

Traces are written to ALL configured storage plugins. Reading occurs from the FIRST plugin whose `isReadSupported` is `true`.

### API

#### TraceManager

Manager-type interface exposing:

- `void addTrace(Trace trace)`: Writes a trace to all configured plugins.
- `DtList<Trace> findTrace(TraceCriteria criteria)`: Returns traces matching the criteria.
- `Trace getTrace(Long idAuditTrace)`: Returns a trace by its numeric identifier.

#### Trace

Final entity with 8 fields:

| Field | Type | Description |
|---|---|---|
| traId | Long | Auto-generated identifier |
| category | String (100c) | Trace category |
| username | String (100c) | User who generated the trace |
| businessDate | Instant | Business date (optional) |
| executionDate | Instant | Execution date (auto) |
| itemUrn | String (250c) | URN of the concerned business object |
| message | String (TEXT) | Descriptive message |
| context | String (TEXT) | Context in pipe-separated format |

#### TraceBuilder

Construction of a Trace:

```java
new TraceBuilder(String category, String user, String itemUrn, String message)
```

Configuration methods:

- `withDateBusiness(Instant)`: Sets the business date.
- `withContext(List<String>)`: Sets the context (list of strings, assembled with pipe separator).
- `build() -> Trace`: Returns the Trace object.

#### TraceCriteriaBuilder

Construction of search criteria:

```java
TraceCriteria.builder()
```

Filtering methods (all optional, cumulative):

- `withDateExecutionStart(Instant)` / `withDateExecutionEnd(Instant)`
- `withDateBusinessStart(Instant)` / `withDateBusinessEnd(Instant)`
- `withCategory(String)`
- `withUsername(String)`
- `withItemUrn(String)`
- `build() -> TraceCriteria`

### TraceStorePlugin Plugins

Three implementations of `TraceStorePlugin` SPI:

| Plugin | Storage | Read | Usage |
|---|---|---|---|
| MemoryTraceStorePlugin | ConcurrentHashMap + AtomicLong | Yes | Development, tests |
| StoreTraceStorePlugin | SQL database via EntityStoreManager (transactional) | Yes | Production |
| LogTraceStorePlugin | Log4j ("audit" logger) | No | Complementary archiving |

LogTraceStorePlugin throws `UnsupportedOperationException` on any read operation (`read`, `findByCriteria`).

### Examples — Project Management domain

#### Creating a trace

```java
final Trace trace = new TraceBuilder(
        "PROJECT", "dupont.j", "PROJ-001", "Project 'SI Migration' created")
    .withDateBusiness(Instant.now())
    .withContext(Arrays.asList("priority=HIGH", "department=IT"))
    .build();
traceManager.addTrace(trace);
```

#### Searching traces

```java
final TraceCriteria criteria = TraceCriteria.builder()
    .withCategory("PROJECT")
    .withDateBusinessStart(Instant.parse("2025-01-01T00:00:00Z"))
    .withDateBusinessEnd(Instant.parse("2025-12-31T23:59:59Z"))
    .build();
final DtList<Trace> results = traceManager.findTrace(criteria);
```

#### Searching by user and URN

```java
final TraceCriteria criteria = TraceCriteria.builder()
    .withUsername("dupont.j")
    .withItemUrn("PROJ-001")
    .build();
final DtList<Trace> results = traceManager.findTrace(criteria);
```

#### Reading a trace by identifier

```java
final Trace trace = traceManager.getTrace(12345L);
```

---

## Ethereum Blockchain Ledger

### Principle

The Ledger allows anchoring data on an Ethereum blockchain to guarantee its integrity and non-repudiation. Data is transmitted as a string.

Two modes:

- **Ethereum**: Real anchoring via an Ethereum node (web3j, HTTP RPC).
- **Fake**: Simulation, no real operation, balance always zero.

### API

#### LedgerManager

Manager-type interface exposing:

- `String sendData(String data)`: Synchronous send. Returns the hexadecimal hash of the transaction.
- `void sendDataAsync(String data, Runnable callback)`: Asynchronous send. Calls are accumulated in a `ConcurrentLinkedQueue` and executed by a daemon thread every 10 seconds. The callback is invoked after processing.
- `BigInteger getWalletBalance(LedgerAddress ledgerAddress)`: Balance of a wallet identified by its address.
- `BigInteger getMyWalletBalance()`: Balance of the wallet configured as local.

#### LedgerTransaction

Immutable final object representing a blockchain transaction. Fields (all BigInteger except hash, blockHash, from, to, message which are String):

| Field | Type | Description |
|---|---|---|
| hash | String | Transaction hash |
| nonce | BigInteger | Nonce |
| blockHash | String | Block hash |
| blockNumber | BigInteger | Block number |
| from | String | Sender address |
| to | String | Recipient address |
| value | BigInteger | Transferred value (wei) |
| message | String | Hexadecimal message |
| transactionIndex | BigInteger | Index in the block |

#### LedgerTransactionBuilder

Fluent builder for constructing `LedgerTransaction` objects.

#### LedgerTransactionEvent

EventBus event, emitted on each received transaction. Listening is done with the `@EventBusSubscribed` annotation.

#### LedgerTransactionPriorityEnum

Five priority levels with their value in per-mille:

| Value | Priority | Multiplier |
|---|---|---|
| 5 | VERYSLOW | gasBase * 5 / 1000 |
| 50 | SLOW | gasBase * 50 / 1000 |
| 500 | MEDIUM | gasBase * 500 / 1000 |
| 650 | FAST | gasBase * 650 / 1000 |
| 1000 | VERYFAST | gasBase * 1000 / 1000 |

The calculation formula is: `gasPrice = gasBase * priority / 1000`.

#### LedgerCredential

Authentication pair: `LedgerCredential(password, walletPath)`.

#### LedgerAddress

Record: `LedgerAddress(accountName, publicAddress)`.

### LedgerPlugin Plugins

Two implementations of `LedgerPlugin` SPI:

| Plugin | Type | Description |
|---|---|---|
| EthereumLedgerPlugin | Activeable | HTTP RPC connection via web3j |
| FakeLedgerPlugin | — | No-op, balance at zero |

#### EthereumLedgerPlugin — parameters

| Parameter | Description |
|---|---|
| urlRpcEthNode | Ethereum RPC node URL |
| myAccountName | Local account name |
| myPublicAddr | Public address of local account |
| defaultDestAccountName | Default recipient account name |
| defaultDestPublicAddr | Public address of default recipient |
| walletPassword | Wallet password |
| walletPath | Path to wallet file |

Gas calculation: `gasPrice = gasBase * priority / 1000`. A 10% margin is added to gasLimit, on storage cost only.

The plugin listens to the `transactionFlowable` stream from the node and publishes transactions on the EventBus via `LedgerTransactionEvent`.

### Examples — Project Management domain

#### Synchronous send

```java
final String hash = ledgerManager.sendData(
    "PROJECT_CREATE:PROJ-001:Migration SI");
```

#### Asynchronous send with callback

```java
ledgerManager.sendDataAsync(
    "PROJECT_UPDATE:PROJ-001:status=completed",
    () -> {
        // Post-confirmation action
        projetServices.updateProjetStatus(projetProjet, StatusEnum.COMPLETED);
    }
);
```

#### Reading balance

```java
final BigInteger balance = ledgerManager.getMyWalletBalance();
final LedgerAddress archiveAddress = new LedgerAddress("archive", "0xDef456...");
final BigInteger partnerBalance = ledgerManager.getWalletBalance(archiveAddress);
```

#### Listening to transactions via EventBus

```java
@EventBusSubscribed
public void onLedgerTransaction(final LedgerTransactionEvent event) {
    final String message = event.getLedgerTransaction().getMessage();
    logger.info("Transaction confirmed: " + message);
}
```

---

## Combined configuration

Production scenario: persistent traces in database + log archiving + Ethereum ledger.

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
                  myAccountName: "project-management"
                  myPublicAddr: "0xAbC123..."
                  defaultDestAccountName: "archive"
                  defaultDestPublicAddr: "0xDeF456..."
                  walletPassword: "..."
                  walletPath: "/wallet/project-management.p12"
```

This scenario traces each action in the database, archives a parallel log journal, and anchors critical events on the Ethereum blockchain.

Development scenario: memory traces + simulated ledger.

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

## For Experts

### Managers
| Manager | Role | Activated by |
|---|---|---|
| `TraceManager` | Write and read of audit traces (audit trail) | `trace` |
| `LedgerManager` | Data anchoring on Ethereum blockchain (or simulation) | `ledger` |

### Features (@Feature)
| Flag | Components |
|---|---|
| `trace` | `TraceManager`, `TraceManagerImpl`, DT/SmartType definitions |
| `trace.memory` | `MemoryTraceStorePlugin` |
| `trace.store` | `StoreTraceStorePlugin` |
| `trace.log` | `LogTraceStorePlugin` |
| `ledger` | `LedgerManager` + `LedgerManagerImpl` |
| `ledger.ethereum` | `EthereumLedgerPlugin` (+`Activeable`) |
| `ledger.fake` | `FakeLedgerPlugin` |

### Plugins
| Plugin | Role | Feature |
|---|---|---|
| `MemoryTraceStorePlugin` | In-memory trace storage (dev/tests) | `trace.memory` |
| `StoreTraceStorePlugin` | Transactional persistence via EntityStoreManager | `trace.store` |
| `LogTraceStorePlugin` | Complementary archiving via "audit" logger (write only) | `trace.log` |
| `EthereumLedgerPlugin` | Real anchoring via web3j HTTP RPC (Activeable) | `ledger.ethereum` |
| `FakeLedgerPlugin` | Ledger simulation, balance at zero (dev/tests) | `ledger.fake` |

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
                  myAccountName: "project-management"
                  myPublicAddr: "0xAbC123..."
                  defaultDestAccountName: "archive"
                  defaultDestPublicAddr: "0xDeF456..."
                  walletPassword: "..."
                  walletPath: "/path/to/wallet"
            - ledger.fake:
```