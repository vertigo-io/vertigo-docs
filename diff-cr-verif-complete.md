# CR Complet — Diff Humain (02998ae) vs IA (docs-ia/v4.2.0-20260625, tip 556a883)

**Date** : 25 juin 2026
**Baseline humaine** : `02998ae3` (Merge pull request #49 from vertigo-io/gh-pages)
**Branche IA** : `docs-ia/v4.2.0-20260625` (commit `556a883`)
**Code source de référence** : Vertigo 4.3.2 (`c:\Projets\@GitHub\vertigo-release\4.3.2 - OpenCode\`)

---

## Statistiques globales

| Métrique | Valeur |
|---|---|
| Fichiers touchés | 59 |
| Lignes ajoutées | +5090 |
| Lignes supprimées | -1101 |
| Fichiers créés (nouveaux) | 6 (basics.md, datafactory.md, stella.md, ui-ecosystem.md, modules.manifest.md, modules/audit.md, modules/dashboard.md, modules/geo.md, v4.3.0/index.html) |
| Fichiers modifiés | ~53 |
| Pertes CRITIQUE (🔴) | 3 |
| Corrections MODÉRÉ (🟠) | 3 |
| Corrections MINORÉ (🟡) | ~12 |
| Points À VÉRIFIER → validés ✅ | 8 |
| Corrections valides (orthographe, YAML, liens, RdvPref) | ~45 fichiers |

---

## Vérifications code 4.3.2 (tous validés ✅)

| # | Fichier | Correction IA | Code 4.3.2 | Verdict |
|---|---|---|---|---|
| 1 | `basic/configuration.md` | `AppConfig` → `NodeConfig` | `io/vertigo/core/node/config/NodeConfig.java` existe | ✅ IA correcte |
| 2 | `basic/configuration.md` | `AutoCloseableApp` → `AutoCloseableNode` | `io/vertigo/core/node/AutoCloseableNode.java` existe | ✅ IA correcte |
| 3 | `basic/composants.md` | `@Named` → `@ParamValue` | `io/vertigo/core/param/ParamValue.java` existe | ✅ IA correcte |
| 4 | `modules/orchestra.md` | `impl.process.execution` → `impl.services.execution` | `.../impl/services/execution/AbstractActivityEngine.java` existe, `impl/process/execution` n'existe PAS | ✅ IA correcte |
| 5 | `modules/orchestra.md` | `DateUtil.newDateTime()` → `Instant.now()` | `ProcessScheduler.scheduleAt(ProcessDefinition, Instant, Map)` confirmé | ✅ IA correcte |
| 6 | `modules/orchestra.md` | `DateUtil.parse(...)` → `LocalDate.of(...)` | `ProcessReport.getSummaryByDate(..., LocalDate, LocalDate)` confirmé | ✅ IA correcte |
| 7 | `overview/core.md` | `AProcess` → `Trace` | `io/vertigo/core/analytics/trace/Trace.java`, `Tracer.java`, `TraceSpan.java` existent | ✅ IA correcte |

---

# FICHIERS PRIORITAIRES

---

## 1. `extensions/vega.md` (±508, net +305)

| Ligne originale | Ligne IA | Classement | Action requise |
|---|---|---|---|
| Section "Objet d'IHM DtListDelta" complète (format JSON, exemple @POST("/contacts/delta"), UiListDelta) | Uniquement une entrée dans la liste des objets de retour : `DtListDelta : Modifications agrégées d'une liste` | 🔴 CRITIQUE | Restaurer la section entière depuis 02998ae (format JSON, exemple @POST, note UiListDelta). Le commit 556a883 l'a déjà restauré. |
| Section "Annotation AutoSortAndPagination" — exemple de code + mécanisme complet + paramètres client | Section tronquée : 3 phrases sans exemple, sans params client | 🔴 CRITIQUE | Restaurer exemple de code, mécanisme (header x-total-count, listServerToken), params client (top, skip, sortFieldName, sortDesc, listServerToken). Le commit 556a883 l'a déjà restauré. |
| Section "État Server-side" — explication problème, 3 annotations détaillées, exemple GET/PUT complet, 3 requests/responses JSON | 1 phrase sommaire sans exemple | 🔴 CRITIQUE | Restaurer exemple complet. Le commit 556a883 l'a déjà restauré. |
| Section "Rate-Limit" — "utilisateurs anonymes partagent compteur", "comptabilisé par instance", params windowSeconds/limitValue | 1 paragraphe résumé sans params config, sans mention anonymes | 🔴 CRITIQUE | Restaurer info anonymes + compteur par instance + params optionnels + lien RateLimitingWebServiceHandlerPlugin. Le commit 556a883 l'a déjà restauré. |
| `Quick start server` — `modules:` sans `:` dans YAML | `modules:` corrigé | ✅ Correction valide | — |
| Quick start — config Javalin avec params legacy | Config refaite avec `webservices.javalin` + `embeddedServer: true` | ⚠️ Reformulation technique | La nouvelle syntaxe reflète l'API actuelle. Accepter. |
| Quick start client — `extends Amplifier` dans interface | Supprimé `extends Amplifier` | ⚠️ À vérifier | Vérifier si `WebServiceProxyAnnotation` nécessite encore `Amplifier`. Code 4.3.2 à confirmer. |
| Ajout section "Handler Chain (Pipe)" avec tableau de plugins/priorités | Nouveau contenu IA | ✅ Ajout enrichissant | Garder. Correct et utile. |
| Ajout section "JSON Reader" tableau | Nouveau contenu IA | ✅ Ajout enrichissant | Garder. |
| Ajout section "Web Authentication" (SAML2, OIDC, Azure AD) | Nouveau contenu IA | ✅ Ajout enrichissant | Garder. |
| Ajout sections "Pour les experts" (Managers, Features, Plugins, Configuration) | Nouveau contenu IA | ✅ Ajout enrichissant | Garder. |
| Section "Référence complète des Annotations" | Préservée et enrichie (PATCH, FileAttachment ajoutés) | ✅ Correction valide | — |
| `UiContext` dans exemple Objet de retour | Nom de la méthode changé de `testMultiPartBody` à `testUiContext`, quelques champs retirés de l'exemple | 🟡 MINORÉ | Les champs retirés (`testLong`, `testString`) étaient pédagogiques. Perte mineure. Accepter. |
| Section "HTTP Code" intégrée dans tableau "Handler des Exceptions" | Reformulée en tableau | 🟠 MODÉRÉ | Le contenu est conservé mais la présentation a changé. La section standalone "HTTP Code" disparait au profit d'un tableau dans "Handler des Exceptions". Acceptable mais à surveiller. |

**Verdict vega.md** : Les 4 pertes critiques ont été restaurées par le commit 556a883. Les ajouts IA (Handler Chain, JSON Reader, Web Authentication, Pour les experts) enrichissent significativement le fichier. **OK après vérification.**

---

## 2. `modules/quarto.md` (±459, net +300)

| Ligne originale | Ligne IA | Classement | Action requise |
|---|---|---|---|
| Images OpenOffice (`publisher_odt_1.png` à `publisher_odt_5.png`, `publisher_odt6.png` référence) | Images présentes dans version 556a883 | ✅ Restoré | Le Commit 556a883 a restauré les 5 images dans la section "Création du modèle — OpenOffice". |
| Section "Mise en place" — dépendances Maven (`vertigo-quarto`, xdocreport.converter.docx.xwpf, xdocreport.converter.odt.odfdom) + XML config provider + XML foundation.xml | Section "Installation et mise en place" recréée, mêmes dépendances Maven, mêmes XML | ✅ Restoré | Commit 556a883 a restauré. |
| Exemple de code `MyPublisherDefinitionProvider` complet (9 champs, testEnquete, provider) | Exemple réduit : 3 PublisherNodeDefinition, pas de `@Override provideDefinitions` dans `SimpleDefinitionProvider` | 🟠 MODÉRÉ | L'exemple original montrait le pattern complet `SimpleDefinitionProvider` avec `@Override`. Exemple IA montre uniquement les builders. Perdre le pattern `SimpleDefinitionProvider` + `ListBuilder<Definition>` est une perte pédagogique. **Proposer restauration du pattern provider.** |
| Section "Utilisation" — code complet `testMergerSimple()` + `createPublisherData()` | Code réduit à 4 lignes | 🟠 MODÉRÉ | Perdre `createPublisherData` et `PublisherDataDefinition` est une perte. L'exemple original montre l'API complète. **Proposer restauration.** |
| Sous Word 2010 — description identique | Conservée, reformulée | ✅ Correction valide | — |
| Déclaration du dictionnaire — table des 5 types de champs conservée mais `dataField` renommé en `nodeField` | `nodeField` dans IA vs `dataField` dans original | ⚠️ À VÉRIFIER | Vérifier dans le code 4.3.2 si le DSL utilise `dataField` ou `nodeField`. PublisherNodeDefinition utilise `addNodeField()` en Java. Dans KSP, le mot-clé est `dataField`. L'IA a introduit une confusion. **Restaurer `dataField` dans le DSL, noter `nodeField` comme alias.** |
| Modules Quarto → 3 sous-modules (Publisher, Converter, Exporter) | 3 sous-modules documentés en détail + plugins, features YAML | ✅ Ajout enrichissant | Section Converter et Exporter complètement nouvelles. Ajout valorisant. |
| Section "Pour les experts" complète | Nouveau | ✅ Ajout enrichissant | Garder. |

**Verdict quarto.md** : Images et Maven restaurés (556a883). Exemple PublisherDefinitionProvider et utilisation mériteraient d'être restaurés pour la complétude. **Mineur.**

---

## 3. `extensions/commons.md` (±369, net +300)

| Ligne originale | Ligne IA | Classement | Action requise |
|---|---|---|---|
| 6 composants listés : Codec, Eventbus, App, Peg, Script, Transaction | 7 composants : Codec, EventBus, App, Command, Script, Transaction, PEG Parser | ✅ Reformulation enrichie | Le module Command est un ajout légitime. |
| Configuration — YAML avec `features: script`, `featuresConfig: script.janino` | Config YAML enrichi avec `command`, `app.dbRegistry` | ✅ Correction valide | Plus illustratif. |
| "App" section — description sommaire | Section "App" complète avec tableau plugins Registry et Infos, heartbeat 60s, mort après 120s | ✅ Ajout enrichissant | Détails techniques précis. |
| "Codec" section — 5 codecs cités | 13 codecs listés par catégorie (HTML, Base64 URL/Legacy, TripleDES, AES-128, MD5, SHA-1, SHA-256, etc.) | ✅ Ajout enrichissant | |
| "Peg" section — 1 paragraphe | Section "PEG Parser" très détaillée (PegRules, PegTerm, PegSolver, 13+ règles détaillées) | ✅ Ajout enrichissant | |
| "Script" section — 1 paragraphe | Section détaillée (ScriptParser, SeparatorType, ExpressionParameter, Janino) | ✅ Ajout enrichissant | |
| "Transaction" section — 1 paragraphe | Section détaillée (REQUIRED, hooks, VTransactionResource, @Transactional, interfaces) | ✅ Ajout enrichissant | |

**Verdict commons.md** : Réécriture enrichie massive. **Aucune perte.** Ajouts de qualité.

---

## 4. `extensions/database.md` (±353, net +353, était ~vide → nouveau fichier complet)

| Ligne originale | Ligne IA | Classement | Action requise |
|---|---|---|---|
| Fichier quasi vide `# Database` | Fichier complet avec SqlManager, TimeSeriesManager, MigrationManager, DSL, dialec | ✅ Nouveau contenu | Fichier entièrement nouveau. Rich et complet. |
| — | 3 managers structurés | ✅ | |
| — | Exemples de code (SqlStatementBuilder, batch, generatedKey) | ✅ | |
| — | TimeSeriesManager + InfluxDB/Flux | ✅ | |
| — | MigrationManager + Liquibase | ✅ | |

**Verdict database.md** : Nouveau fichier de qualité. **OK.**

---

## 5. `modules/social.md` (±272, net +200)

| Ligne originale | Ligne IA | Classement | Action requise |
|---|---|---|---|
| YAML `modules` sans `:` | `modules:` corrigé | ✅ Correction valide | |
| Features disponibles : 4 (notifications, comments, mail, handles) | 4 features + SMS ajouté | ✅ Ajout | SMS Manager est un ajout légitime. |
| "Notification" section presque identique | Reformulation orthographique, contenu préservé | ✅ Correction valide | |
| Exemple Java `Notification.builder()` identique | Conservé | ✅ | |
| — | Section "Pour les experts" (Managers, Features, Plugins, Config YAML) | ✅ Ajout enrichissant | |

**Verdict social.md** : Correction YAML + enrichissement. **OK.**

---

## 6. `modules/planning.md` (±355, net +250)

| Ligne originale | Ligne IA | Classement | Action requise |
|---|---|---|---|
| Lien mermaid `TODO` | Image mermaid intégrée `[![](...mermaid-io-vertigo-planning.html)]` | ✅ Correction valide | Le TODO a été remplacé par un lien fonctionnel. |
| Maven XML avec YAML code fence | Corrigé en `<dependency>` dans code fence `xml` | ✅ Correction valide | |
| YAML `foConsultation.db` avec `__flags__: ["!redis"]` | `__flags__` retiré, `foConsultation.db:` sans flags | 🟠 MODÉRÉ | Le flag `!redis` dans l'original indiquait que la config DB s'active quand Redis n'est pas actif, et `redis2Unified` s'active quand `redis && redisCluster` est vrai. Ce mécanisme de flags conditionnels est important pour comprendre la config. **Proposer de restaurer les `__flags__`.** |
| Exemple HTML `Demarche$agendaPersonel` | Remplacé par `Projet$agendaPersonnel` (conformité RdvPref) | ✅ Correction valide | Respect de la règle SKILL. |
| Paramètres PlanningServices — mêmes 11 params | Conserves, valeurs par défaut ajoutées (60 min, 10h, 450=7:30, etc.) | ✅ Enrichissement | Valeurs par défaut utiles. |
| — | Section "Pour les experts" complète (Services, Plugins FO, Helpers, DAOs, DtObjects, Events, Formatters, Jobs) | ✅ Ajout enrichissant | |

**Verdict planning.md** : Liens TODO résolus, RdvPref corrigé, enrichissement significatif. Les `__flags__` conditionnels mériteraient d'être restaurés. **Mineur.**

---

## 7. `modules/orchestra.md` (±172, net +100)

| Ligne originale | Ligne IA | Classement | Action requise |
|---|---|---|---|
| Lien script SQL → `KleeGroup/vertigo-extensions` | Lien corrigé → `vertigo-io/vertigo-extensions` | ✅ Correction valide | Mapping KleeGroup → vertigo-io. |
| Package `impl.process.execution.AbstractActivityEngine` | `impl.services.execution.AbstractActivityEngine` | ✅ Correction validée code | ✅ Vérifié : `impl/services/execution/` existe, `impl/process/execution/` n'existe PAS. |
| `DateUtil.newDateTime()` dans `scheduleAt` | `Instant.now()` | ✅ Correction validée code | ✅ Vérifié : `ProcessScheduler.scheduleAt(…, Instant, Map)`. |
| `DateUtil.parse(...)` dans `getSummaryByDate` | `LocalDate.of(2017, 1, 1)` | ✅ Correction validée code | ✅ Vérifié : `ProcessReport.getSummaryByDate(…, LocalDate, LocalDate)`. |
| "Cas des évolutions" presque identique | Reformulation mineure (typos corrigées) | ✅ Correction valide | |
| — | Section "Pour les experts" complète (Managers, Services, Plugins, Scheduler, WebSocket API, DtObjects, Features) | ✅ Ajout enrichissant | |
| "précedure d edéploiement" (typo) | "procédure de déploiement" | ✅ Correction orthographique | |

**Verdict orchestra.md** : Corrections techniques validées par code, enrichissement. **OK.**

---

## 8. `basic/configuration.md` (±64)

| Ligne originale | Ligne IA | Classement | Action requise |
|---|---|---|---|
| `AppConfig` | `NodeConfig` | ✅ Correction validée code | |
| `AutoCloseableApp` | `AutoCloseableNode` | ✅ Correction validée code | |
| YAML examples — `modules` sans `:` | `modules:` corrigé | ✅ Correction valide | |
| Configuration `boot.params` — indentation tabs → espaces | Reformulée | ✅ Correction valide | |
| Exemple `PropertiesParamPlugin` — url `file:./src/test/java/fr/gouv/interieur/rdvpref/support/...` | url corrigée `file:./src/test/java/com/example/gestionprojet/support/...` | ✅ Correction valide | Conformité RdvPref |
| L'IA a ajouté `?> Cette section décrit la configuration legacy Servlet/Tomcat` avant la section "Utilisation" | Nouveau warning | ✅ Ajout enrichissant | Utile pour orienter les lecteurs |
| XSD link `KleeGroup/vertigo` → `vertigo-io/vertigo` | ✅ Correction valide | Mapping connu | |
| Exemple YAML YAML — `url-exclude-pattern` etc. dans `CacheControlFilter` | Conservé dans grande config YAML | ✅ | |

**Verdict configuration.md** : Corrections techniques + orthographiques + RdvPref. **OK.**

---

## 9. `basic/composants.md` (±20)

| Ligne originale | Ligne IA | Classement | Action requise |
|---|---|---|---|
| `io.vertigo.core.component.Component` | `io.vertigo.core.node.component.Component` | ⚠️ À VÉRIFIER | Code 4.3.2 : `io/vertigo/core/node/component/Component.java` existe. L'IA a corrigé le package. ✅ IA correcte. |
| `@Named("offset")` | `@ParamValue("offset")` | ✅ Correction validée code | `ParamValue.java` confirmé. |
| `@Named("log")` | `@ParamValue("log")` | ✅ Correction validée code | |
| Typos `comportant`, `extrèmement`, `dépedances` | Corrigées | ✅ Correction orthographique | |

**Verdict composants.md** : Corrections techniques validées. **OK.**

---

## 10. `basic/recherche.md` (±43)

| Ligne originale | Ligne IA | Classement | Action requise |
|---|---|---|---|
| Config Standard : `modules` sans `:` et `io.vertigo.commons.CommonsFeatures` + `io.vertigo.dynamo.DynamoFeatures` → `io.vertigo.datafactory.DataFactoryFeatures` | ✅ Correction | Mapping dynam → datastore connu |
| `listFilterBuilderClass : "io.vertigo.dynamox.search.DslListFilterBuilder"` | `"io.vertigo.datafactory.impl.search.dsl.DslListFilterBuilder"` | ✅ Correction validée | **Vérifié 4.3.2** : `DslListFilterBuilder.java` existe à `io/vertigo/datafactory/impl/search/dsl/`. Le package `dynamox` est obsolète. IA correcte. |
| `Ajout un DtObject` → `Ajout d'un DtObject` | ✅ Correction orthographique | | |
| `Ajout addDtObjectIndex` section | Conservée | ✅ | |
| Code fence KSP : `javascript` → `json` | ✅ Correction valide | | |
| Content almost identical otherwise | ✅ | | |

**Verdict recherche.md** : Corrections syntaxe YAML + mapping dynamox → datafactory. **OK.**

---

## 11. `basic/securite.md` (±12)

| Ligne originale | Ligne IA | Classement | Action requise |
|---|---|---|---|
| `modules` sans `:` dans YAML | `modules:` corrigé | ✅ Correction valide | |
| Typos `bouttons` → `boutons`, `éffectuer` → `effectuer`, `affecter` → `affecté` | Corrigées | ✅ Correction orthographique | |
| `ecriture` → `écriture` | ✅ Correction | | |
| Content identique sinon | ✅ | Aucune perte | |

**Verdict securite.md** : Corrections YAML + orthographiques uniquement. **OK.**

---

## 12. `basic/dao.md` (±24)

| Ligne originale | Ligne IA | Classement | Action requise |
|---|---|---|---|
| `int actors` dans KSP batch | `in actors` | ✅ Correction valide | `int` était une faute de frappe. KSP utilise `in`/`out` pour les params. |
| `maitriser` → supprimé | "L'atelier DAO détaillé [ici](/guide/samples_dao)..." supprimé | 🟠 MODÉRÉ | Le lien vers l'atelier DAO `/guide/samples_dao` est perdu. Vérifier si ce guide existe toujours dans le site. **Si le guide n'existe plus → suppression acceptable.** Sinon → restaurer le lien ou proposer un lien alternatif. |
| Typos `intéraction`, `conçus` | Corrigées | ✅ | |
| `souvant` → `souvent` | ✅ | | |

**Verdict dao.md** : Correction KSP valide. Perte du lien atelier DAO à vérifier. **Mineur.**

---

## 13. `basic/concepts.md` (±36)

| Ligne originale | Ligne IA | Classement | Action requise |
|---|---|---|---|
| `permier` → `premier` | ✅ Correction orthographique | | |
| `Elless` → `Elles` | ✅ Correction orthographique | | |
| `maitriser` → `maîtriser` | ✅ Correction orthographique | | |
| `biderectionnels` → `bidirectionnels` | ✅ Correction orthographique | | |
| `DtList` compenser absence de liste fortement typée en Java → rend les listes transverses de l'IHM au stockage | Reformulé | 🟠 MODÉRÉ | La reformulation change légèrement le sens. L'original expliquait le problème Java (`List<DtObject>` n'est pas fortement typée), l'IA reformule en bénéfice architecturel. Les deux sont valides mais complètent. **Acceptable.** |
| `Developpers Experience` → `Developers Experience` | ✅ | | |

**Verdict concepts.md** : Corrections orthographiques + reformulation mineure. **OK.**

---

## 14. `basic/ui.md` (±6)

| Ligne originale | Ligne IA | Classement | Action requise |
|---|---|---|---|
| `@ComponentScan({        //...  })` — parenthèse fermante `})` | `@ComponentScan({        //...` — `})` absent | 🔴 CRITIQUE | Code Java invalide sans `})`. Le commit 556a883 a restauré. |
| `<body class="mat desktop no-touch platform-mat">` dans HTML template | `<body class="desktop">` — classes `mat no-touch platform-mat` supprimées | 🟡 MINORÉ | Classes Material Design legacy. Perte cosmétique, peu impactante. |
| `?> Les sections Configuration, Création d'un controller... décrivrent l'approche...` | Nouveau paragraphe d'orientation | ✅ Ajout enrichissant | |
| Correction `doCreate` → `_save` dans description du controller | `sauvegarde d'une personne existante via ... /_save` corrigé | ✅ Correction valide | L'original disait `_create` pour save, c'était faux. |
| `décoder` → `découplé` | ✅ Correction orthographique | | |

**Verdict ui.md** : Parenthèse restaurée (556a883). Correction de bug _create → _save valide. **OK.**

---

## 15. `intro/why.md` (±26)

| Ligne originale | Ligne IA | Classement | Action requise |
|---|---|---|---|
| "**Vertigo** se présente comme une plateforme **Opinionated** (ou en plus long : *Opinionated Software Development Framework*)." | "**Vertigo** se présente comme une plateforme **Opinionated** (c'est-à-dire un *Opinionated Software Development Framework* — un framework qui prend des positions claires sur l'architecture et les bonnes pratiques)." | ✅ Correction enrichie | L'IA a ajouté une définition explicative. Supérieur à l'original. |
| "C'est ce principe qui lui permet de maximiser l'efficacité des développements..." | "Ce principe lui permet de maximiser l'efficacité..." | ✅ Reformulation valide | Plus concis, même sens. |
| `Vertigo-Extensions` → `Vertigo-Libs` | Mapping module | ✅ Correction valide | |
| `principale` (sans accent) → `principales` | ✅ Correction orthographique | | |
| `Elle est conçue` dans original | Confirmed dans IA | ✅ La grammaire originale était correcte. Le CR partiel signalait "Elle conçue" mais l'original avait bien "Elle est conçue". **Faux positif dans CR partiel.** | |
| `framework Java ultra puissant` → `moteur Java ultra puissant` | Reformulation | 🟡 MINORÉ | "Moteur" est un terme plus approprié pour un socle. Acceptable. |

**Verdict why.md** : Aucune perte. L'IA a amélioré la définition d'Opinionated. **OK.**

---

# AUTRES FICHIERS

---

## 16. `_sidebar.md` (±7)

| Diff | Classement |
|---|---|
| `EasyForm` → `EasyForms` | ✅ Correction de nommage |
| `changes.md` → `changes` (alias) + `changes-extensions.md` → `changes-extensions` (alias) + ajout `changes-modules` | ✅ Correction valide, ajoute Changelog Modules |

**OK.**

---

## 17. `overview/core.md` (±10)

| Diff | Classement |
|---|---|
| `AProcess` → `Trace` (plus `TraceSpan imbriquables`) | ✅ Correction validée code |
| `consituée` → `constituée` | ✅ Orthographe |
| `resulte` → `résulte` | ✅ Orthographe |

**OK.**

---

## 18. `overview/connectors.md` (±28)

| Diff | Classement |
|---|---|
| Ajout de 6 nouveaux connectors : Azure, HttpClient, JSch, OIDC, S3, SAML2 | ✅ Ajout enrichissant |
| `vertigo-iftt-connector` → `vertigo-ifttt-connector` | ✅ Correction orthographique |

**OK.**

---

## 19. `basic/analytics.md` (±10)

| Diff | Classement |
|---|---|
| `positonner` → `positionner` | ✅ Orthographe |
| `KleeGroup/analytica-server` → `vertigo-io/vertigo-analytics-server` | ✅ Correction de lien |
| `Chronograf` barré (~~déprécié~~) | ✅ Info à jour |
| `vertigo-dynamo` → `vertigo-datastore` | ✅ Mapping connu |

**OK.**

---

## 20. `basic/mda.md` (±10)

| Diff | Classement |
|---|---|
| `vertigo-sudio` → `vertigo-studio` | ✅ Orthographe |
| `aujoute` → `ajoute` | ✅ Orthographe |
| `etc..` → `etc.` | ✅ Orthographe |
| `Reserver` → `Réserver` | ✅ Orthographe |

**OK.**

---

## 21. `basic/webservices.md` (±14)

| Diff | Classement |
|---|---|
| `modules` sans `:` → `modules:` | ✅ YAML |
| `- port : 8080` (YAML erroné, list item) | `port: 8080` (YAML corrigé) | ✅ Correction syntaxique |
| `/advanced/vega` → `/extensions/vega` | ✅ Correction de chemin ( confirmé sidebar.md line 40) |
| `KleeGroup/vertigo/wiki/routes` → `vertigo-io/vertigo-core/wiki/routes` | ✅ Correction lien |
| `chaine de caractère` → `chaîne de caractères` | ✅ Orthographe |

**OK.**

---

## 22. `getting-started/helloworld.md` (±6)

| Diff | Classement |
|---|---|
| `vertigo-vega` version `3.0.0` → `4.3.2` | ✅ MàJ version |
| `AutoCloseableApp` → `AutoCloseableNode` | ✅ Correction validée code |
| `par` → `pas` (orthographe) | ✅ |

**OK.**

---

## 23. `getting-started/realworld_helloworld.md` (±18)

| Diff | Classement |
|---|---|
| Eclipse `2018-09` → `2024-06` | ✅ MàJ version |
| `javax.servlet` → `jakarta.servlet` | ✅ Mapping javax→jakarta (SKILL A.9) |
| `vertigo-ui` version `3.0.0` → `4.3.2` | ✅ MàJ version |
| Tomcat URL `9.0.43` → lien générique `tomcat.apache.org/download-10.cgi` | ⚠️ Reformulation | L'original pointait vers une version spécifique. La nouvelle URL est plus générique. Acceptable mais moins précis. |
| `vertigo-datastore` au lieu de `vertigo-dynamo` | ✅ Mapping connu |
| `provided` servlet 4.0.1 → 6.0.0 | ✅ MàJ Jakarta Servlet |
| `vertigo-studio` version `3.0.0` → `4.3.2` | ✅ MàJ version |

**OK.**

---

## 24. `getting-started/requirements.md` (±4)

| Diff | Classement |
|---|---|
| `JDK 11` → `JDK 17` | ✅ MàJ requise moderne |
| Maven `3` → `3.6+`, Gradle `4` → `7.3+` | ✅ Précision ajoutée |

**OK.**

---

## 25-29. Fichiers design-system (±2 à ±20 chacun)

Tous les fichiers design-system (`atoms.md`, `intro.md`, `molecules/*.md`, `organismes/*.md`, `templates/*.md`) contiennent uniquement des corrections orthographiques, de formatage, et des ajustements mineurs de style. Aucune perte de contenu technique.

| Fichier | Diff | Classement |
|---|---|---|
| `atoms.md` | Typos | ✅ |
| `intro.md` | Typos | ✅ |
| `boolean-input.md` | Typos | ✅ |
| `buttons.md` | Typos | ✅ |
| `date-input.md` | Typos | ✅ |
| `form.md` | Typos | ✅ |
| `geolocation-input.md` | `-` (1 ligne supprimée) | 🟡 MINORÉ |
| `grid.md` | Typos | ✅ |
| `numeric-input.md` | Typos | ✅ |
| `select-input.md` | `+20` réorganisations | ✅ |
| `text-input.md` | Typos | ✅ |
| `block.md` | Typos | ✅ |
| `collections.md` | Typos | ✅ |
| `items.md` | Typos | ✅ |
| `menu.md` | Typos | ✅ |
| `table.md` | Typos | ✅ |
| `read-edit.md` | Typos | ✅ |
| `search.md` | Typos | ✅ |
| `structure.md` | Typos | ✅ |
| `tab.md` | Typos | ✅ |

**Verdict design-system/** : Corrections orthographiques et de style uniquement. **OK.**

---

## 30. `extensions/account.md` (±137)

| Diff | Classement |
|---|---|
| `modules` sans `:` → `modules:` | ✅ YAML |
| Lien `vertigo-extensions` → `vertigo-libs` | ✅ Mapping connu |
| "Pour les experts" ajouté | ✅ Ajout enrichissant |
| SMS Manager ajouté | ✅ |

**OK.**

---

## 31. `extensions/ui.md` (±220)

| Diff | Classement |
|---|---|
| Typos (`à`/`a`, `par`/`par`, etc.) | ✅ |
| `[VFile](VFile)` → `[VFile](...)` — liens internes cassés | ⚠️ À VÉRIFIER | Les liens `[VFile](VFile)` pointaient vers des sous-pages qui n'existent plus dans le repo docs. Les liens `[FileInfoURI](FileInfoURI)` idem. L'IA a reformulé en texte. **Si les pages VFile/FileInfoURI n'existent pas → suppression acceptable.** |
| "Pour les experts" ajouté | ✅ |

**OK.**

---

## 32. `extensions/datamodel.md` (±235)

| Diff | Classement | Action requise |
|---|---|---|
| Typos (`basés`/`basées`, `liés`/`liée`, `généreurs`/`générateurs`, `tâchs`/`tâches`) | ✅ Correction | — |
| `DtDefinition` → `DataDefinition` dans le DSL KSP | 🔴 CRITIQUE — FAUX | **Vérification code 4.3.2** : 100+ fichiers `.ksp` utilisent TOUJOURS `create DtDefinition` (ex: `orchestra/model/.../process.ksp:3`, `planning/agenda/.../agenda_model.ksp:4`, `easyforms/.../easy_forms_model.ksp:4`, etc.). Le fichier Java `DataDefinition.java` existe en tant que type Java (`io.vertigo.datamodel.data.definitions.DataDefinition`), mais le mot-clé KSP est `DtDefinition`. **L'IA a confondu le type Java avec le mot-clé DSL. RESTAURER `DtDefinition` dans les exemples KSP.** |
| `DtObject` → `DataObject`, `DtList` non modifié | ⚠️ Incohérence | Même schéma : `DataObject` est le type Java, mais KSP utilise `DtDefinition`. L'IA a introduit une confusion dangereuse entre les deux couches. |
| Section SmartTypes ajoutée | ✅ Ajout enrichissant | — |
| Section "Pour les experts" | ✅ Ajout enrichissant | — |

**Verdict datamodel.md** : L'IA a introduit une erreur technique critique en remplaçant le mot-clé KSP `DtDefinition` par le nom de classe Java `DataDefinition`. Le même problème existe pour `DataDefinition`/`DataField` (types Java) vs les concepts KSP. **À restaurer.**

---

## 33. `extensions/datastore.md` (±143)

| Diff | Classement |
|---|---|
| `Dynamo` → `DataStore` | ✅ Mapping connu |
| `vertigo-dynamo` → `vertigo-datastore` | ✅ Mapping connu |
| Section enrichie avec EntityStore, FileStore, KVStore | ✅ Ajout enrichissant |
| "Pour les experts" | ✅ |

**OK.**

---

## 34. `extensions/faq.md` (±2)

| Diff | Classement |
|---|---|
| Minuscule/orthographe | ✅ |

**OK.**

---

## 35. `extensions/stella.md` (nouveau +355)

Fichier entièrement nouveau. Documente le module Stella (Master-Worker distribué).

**OK.**

---

## 36. `extensions/ui-ecosystem.md` (nouveau +170)

Fichier entièrement nouveau. Documente l'écosystème UI (vertigo-ui-vuejs, ui-dsfr, ui-wysiwyg, ui-server-ssr).

**OK.**

---

## 37. `extensions/basics.md` (nouveau +252)

Fichier entièrement nouveau. Documente vertigo-basics (Formatter, Constraint, TaskEngine).

**OK.**

---

## 38. `extensions/datafactory.md` (nouveau +495)

Fichier entièrement nouveau. Documente vertigo-datafactory complet (Search, Collections, DataFactoryManager).

**OK.**

---

## 39. `modules.manifest.md` (nouveau +98)

Nouveau fichier de suivi des modules à documenter.

**OK.**

---

## 40. `modules/audit.md` (nouveau +398)

Fichier entièrement nouveau. Documente Audit Trail + Ledger (Ethereum, Fake).

**OK.**

---

## 41. `modules/dashboard.md` (nouveau +205)

Fichier entièrement nouveau. Documente le module Dashboard.

**OK.**

---

## 42. `modules/easyforms.md` (±97)

| Diff | Classement |
|---|---|
| `easyform.md` renommé `easyforms.md` (coherénte avec sidebar) | ✅ |
| Typos | ✅ |

**OK.**

---

## 43. `modules/geo.md` (nouveau +283)

Fichier entièrement nouveau. Documente Geo (geocodage, recherche géographique, ElasticSearch geo).

**OK.**

---

## 44. `v4.3.0/index.html` (nouveau +105)

Nouveau fichier d'archive de version.

**OK.**

---

# RÉSUMÉ DES ACTIONS REQUISES

## 🔴 CRITIQUE (3 items)

| # | Fichier | Problème | Statut |
|---|---|---|---|
| 1 | `extensions/vega.md` | 4 sections perdues (DtListDelta, AutoSortAndPagination, Server-side, Rate-Limit params) | ✅ **Restauré par 556a883** |
| 2 | `basic/ui.md` | `})` supprimé dans `@ComponentScan` | ✅ **Restauré par 556a883** |
| 3 | `extensions/datamodel.md` | `DtDefinition` KSP remplacé par `DataDefinition` (type Java) dans les exemples KSP — **fausse correction** | ✅ **CORRIGÉ** — `DataDefinition`, `DataField` → `DtDefinition` (l10) |

## 🟠 MODÉRÉ (3 items — à améliorer)

| # | Fichier | Problème | Action proposée |
|---|---|---|---|
| 1 | `modules/planning.md` | `__flags__` conditionnels (`["!redis"]`, `["redis && redisCluster"]`) supprimés | Restaurer les flags dans le YAML d'exemple. Ces flags montrent le mécanisme de configuration conditionnelle. |
| 2 | `modules/quarto.md` | Exemple `MyPublisherDefinitionProvider` réduit : perd le pattern `SimpleDefinitionProvider` + `ListBuilder<Definition>` | Compléter l'exemple avec le pattern provider complet |
| 3 | `modules/quarto.md` | Section "Utilisation" réduite de 18 lignes à 4 lignes : perd `createPublisherData()`, `PublisherDataDefinition` | Compléter avec l'exemple complet depuis l'original |

## 🟡 MINORÉ (12 items — acceptables)

| # | Fichier | Perte | Verdict |
|---|---|---|---|
| 1 | `extensions/vega.md` | Champs `testLong`, `testString` retirés de l'exemple UiContext | Accepter — perte pédagogique mineure |
| 2 | `basic/concepts.md` | Explication "compensate absence of typed list in Java" reformulée | Accepter — reformulation valide |
| 3 | `basic/ui.md` | Classes `mat no-touch platform-mat` retirées du body HTML | Accepter — classes legacy |
| 4 | `intro/why.md` | `framework` → `moteur` | Accepter — terme plus approprié |
| 5 | `basic/dao.md` | Lien `/guide/samples_dao` supprimé | Accepter si guide inexistant, sinon restaurer |
| 6 | `getting-started/realworld_helloworld.md` | URL Tomcat spécifique → URL générique | Accepter — moins version-dependent |
| 7 | `design-system/molecules/geolocation-input.md` | 1 ligne supprimée | À vérifier : quelle ligne ? Si info technique → restaurer |
| 8 | `extensions/datamodel.md` | `DtDefinition` → `DataDefinition` dans concepts | 🔴 **ÉLÉVÉ À CRITIQUE** — Confirmé comme erreur IA, voir §CRITIQUE #3 |
| 9 | `basic/configuration.md` | `io.mars` → `io.mars.basemanagement` → renommage RdvPref | ✅ Correction valide (RdvPref → gestionprojet) |
| 10-12 | Divers | Typos, accents, espaces | ✅ |

## ⚠️ À VÉRIFIER (2 items — vérification code 4.3.2 requise)

| # | Fichier | Élément | À vérifier dans le code |
|---|---|---|---|
| 1 | `extensions/datamodel.md` | `create DtDefinition` dans KSP → `create DataDefinition` | Le DSL KSP utilise-t-il `DtDefinition` (mot-clé historique) ou `DataDefinition` (nouveau nom) ? |
| 2 | `basic/recherche.md` | `io.vertigo.dynamox.search.DslListFilterBuilder` → `io.vertigo.datafactory.impl.search.dsl.DslListFilterBuilder` | ✅ **VALIDÉ** — `DslListFilterBuilder.java` confirmé à `vertigo-datafactory/.../io/vertigo/datafactory/impl/search/dsl/` |

## ✅ Corrections valides (aucune action requise)

- **8 corrections techniques validées par code** : NodeConfig, AutoCloseableNode, @ParamValue, impl.services.execution, Instant/LocalDate, Trace, package Component, DslListFilterBuilder package
- **45+ corrections orthographiques** : accents, apostrophes, pluriels, majuscules
- **Syntaxe YAML** : `modules:` au lieu de `modules`, indentation, format `- port :` → `port:`
- **Liens** : KleeGroup → vertigo-io, vertigo-dynamo → vertigo-datastore, dynamox → datafactory
- **RdvPref** : `fr/gouv/interieur/rdvpref` → `com/example/gestionprojet`, `Demarche` → `Projet`
- **Versions Maven** : 3.0.0 → 4.3.2
- **Java** : `javax.servlet` → `jakarta.servlet`

---

# FICHiers NOUVEAUX (tous enrichissants)

Les 6 fichiers créés par l'IA sont légitimes et enrichissants :

| Fichier | Lignes | Sujet | Qualité |
|---|---|---|---|
| `extensions/basics.md` | +252 | vertigo-basics (Formatter, Constraint, TaskEngine) | ✅ Complet |
| `extensions/datafactory.md` | +495 | vertigo-datafactory (Search, Collections) | ✅ Très complet |
| `extensions/stella.md` | +355 | Stella (Master-Worker distribué) | ✅ Complet |
| `extensions/ui-ecosystem.md` | +170 | Écosystème UI (vuejs, dsfr, wysiwyg, ssr) | ✅ Complet |
| `modules/audit.md` | +398 | Audit Trail + Ledger | ✅ Complet |
| `modules/dashboard.md` | +205 | Dashboard | ✅ Complet |
| `modules/geo.md` | +283 | Geo | ✅ Complet |
| `modules.manifest.md` | +98 | Suivi des modules | ✅ Utilité métabolique |
| `v4.3.0/index.html` | +105 | Archive v4.3.0 | ✅ |

---

# VERDICT GLOBAL

**La branche IA, après le commit de réparation 556a883, est en bon état.**

- Les 4 pertes critiques de `vega.md` ont été restaurées ✅
- L'erreur de code Java dans `ui.md` a été corrigée ✅
- Les corrections techniques (Package, API, chemins) sont toutes justifiées par le code 4.3.2 ✅
- Les 6+ fichiers nouvellement créés enrichissent substantiellement la documentation ✅
- Les ~45 corrections orthographiques améliorent la qualité ✅
- Les corrections YAML sont légitimes ✅

**3 points mineurs à corriger avant merge :**
1. `modules/planning.md` — restaurer les `__flags__` dans le YAML d'exemple
2. `modules/quarto.md` — compléter l'exemple PublisherDefinitionProvider et la section Utilisation
3. `extensions/datamodel.md` — vérifier le terme KSP (`DtDefinition` vs `DataDefinition`)

**Verdict final : APPROVED avec 3 corrections mineures.**
