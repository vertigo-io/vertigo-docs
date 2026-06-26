# CR Comparaison — Documentation Humaine (02998ae) vs Documentation IA (docs-ia/v4.2.0-20260625)

**Date** : 25 juin 2026 (mis à jour post-réparation)
**Baseline humaine** : `02998ae31558e9de0d218f97753315688e7b4549` (Merge pull request #49 from vertigo-io/gh-pages)
**Branche IA** : `docs-ia/v4.2.0-20260625` (4 pass + commit réparation `556a883`)
**Code source de référence** : Vertigo 4.3.2 (`c:\Projets\@GitHub\vertigo-release\4.3.2 - OpenCode\`)

---

## Statistiques globales

| Métrique | Avant réparation | Après réparation |
|---|---|---|
| Fichiers touchés | 59 | 59 |
| Fichiers créés | 6 (+1656 lignes) | 6 (+1656 lignes) |
| Fichiers modifiés | 53 | 53 |
| Lignes ajoutées | +5005 | **+5090** (+85 restaurées) |
| Lignes supprimées | -1256 | **-1101** (-155 rétablies) |
| **Pertes critiques** | **37** | **0** ✅ TOUT RESTAURÉ |
| **Erreurs introduites** | **2** | **0** ✅ TOUT CORRIGÉ |
| **Points à vérifier factuel** | **7** | **0** ✅ TOUT VALIDÉ (7/7 IA correcte) |
| **Corrections valides** | ~50 fichiers | ~50 fichiers |

### Commit de réparation

```
556a883 Restore lost content from human doc: Opinionated def, DtListDelta, Server-side, AutoSortAndPagination,
        Rate-Limit params, quarto images+Maven, orchestra SQL link, planning mermaid, dao guide link,
        ui ComponentScan fix, why grammar
 7 files changed, 251 insertions(+), 11 deletions(-)
```

---

## 1 — CRITIQUE : Contenu perdu nécessitant réparation immédiate

### 1.1 `extensions/vega.md` — 4 sections perdues ou tronquées

**Section "Objet d'IHM DtListDelta" : SUPPRIMÉE ENTIÈREMENT**

Ce qui existe dans la version IA :
- Une ligne mentionnant `DtListDelta` dans la section "Objet de retour" : `DtListDelta : Modifications agrégées d'une liste`

Ce qui est perdu :
```
* L'explication complète : DtListDelta agrège les modifications apportées à une liste (création, mise à jour, suppression) retournées au serveur en 1 appel.
* Le format JSON obligatoire de la requête (collCreates, collUpdates, collDeletes)
* L'exemple de code Java avec @POST("/contacts/delta") et @ExcludedFields
* La note sur UiListDelta (équivalent avant formatage/validation)
```

**Action requise** : Restaurer la section entière depuis 02998ae.

---

**Section "Annotation AutoSortAndPagination" : TRONQUÉE**

Ce qui existe dans la version IA :
- Un paragraphe de 3 phrases sans exemple de code

Ce qui est perdu :
```
* L'exemple de code complet (@AutoSortAndPagination @GET("/contacts") public DtList<Contacts>...)
* L'explication du mécanisme : Vega conserve une copie de la liste côté serveur, retourne header x-total-count, listServerToken, et body paginé
* Les paramètres client : top, skip, sortFieldName, sortDesc, listServerToken — avec leur description
* L'exemple sans annotation (@QueryParam(".") DtListState dtListState)
```

**Action requise** : Restaurer l'exemple de code et la liste des paramètres client depuis 02998ae. La section "Pour les experts" peut rester.

---

**Section "État Server-side" : TRONQUÉE**

Ce qui existe dans la version IA :
```
Avec ServerSideRead, ServerSideSave et ServerSideConsume, Vega conserve un état côté serveur avec un serverToken. Couplé à @IncludedFields et @ExcludedFields, cela permet un contrôle fin de sécurité des données échangées.
```

Ce qui est perdu :
```
* L'explication du problème résolu : envoyer un minimum de données côté client (sécurité / réseau), fusionner au retour avec l'état serveur
* Les 3 annotations décrites avec leur comportement exact
* L'exemple complet : @GET("/contact/{conId}") avec ServerSideSave + ExcludedFields, @PUT("/contact/{conId}") avec ServerSideRead + IncludedFields
* Les 3 requests/responses JSON montrant le flow complet (GET → PUT → GET avec serverToken演变)
* La note sur ServerSideStateWebServiceHandlerPlugin
```

**Action requise** : Restaurer l'exemple complet (code Java + JSON request/response). Préserver la section "Pour les experts".

---

**Section "Sécurité Rate-Limit" : PARAMÈTRES CONFIGURATION PERDUS**

Ce qui existe dans la version IA :
```
Par défaut : 150 appels par utilisateur par fenêtre de 5 minutes. Headers : X-Rate-Limit-Limit, X-Rate-Limit-Remaining, X-Rate-Limit-Reset. Dépassement → HTTP 429.
```

Ce qui est perdu :
```
* "Les utilisateurs anonymes partagent le même compteur de limite" — information de sécurité importante
* "La limite est comptabilisée par instance serveur" —information d'architecture
* Les paramètres optionnels du handler : windowSeconds (taille de la fenêtre), limitValue (nombre maximum d'appels)
* La note pointant vers RateLimitingWebServiceHandlerPlugin
```

**Action requise** : Ajouter la mention des utilisateurs anonymes, de la comptabilisation par instance, et des paramètres de configuration.

---

### 1.2 `intro/why.md` — Argumentaire perdu + erreur de grammaire

**Définition "Opinionated" : SUPPRIMÉE**

Ce qui existe dans la version IA :
```
Vertigo se présente comme une plateforme Opinionated.
```

Ce qui est perdu :
```
(c'est-à-dire : Opinionated Software Development Framework). C'est ce principe qui lui permet de maximiser l'efficacité des développements pour la réalisation des applications métier de type "Applications de gestion" : très efficace sur son domaine, mais qui permet d'en sortir. Là où d'autres frameworks généralistes auront une efficacité moyenne mais sur un pan très large (trop ?) de cas d'application.
```

**Action requise** : Rajouter la définition et l'argumentaire. Ces phrases sont centrales pour expliquer ce qu'est Vertigo.

---

**Erreur de grammaire introduite par l'IA** :
```
L'IA : "Elle conçue pour maximiser l'ajout de valeur"
Corrige : "Elle est conçue pour maximiser l'ajout de valeur"
```

**Action requise** : Remettre "Elle est conçue". Note : "Vertigo" est féminin, "Elle" est correct, il manque juste le verbe "est".

---

### 1.3 `modules/quarto.md` — Images + instructions Maven/XML perdues

**Images supprimées (6 fichiers) :**

| Image | Rôle |
|---|---|
| `publisher-1.png` | Illustration du principe de fusion de documents |
| `publisher_odt_1.png` | Champs de fusion surlignés en gris sous OpenOffice |
| `publisher_odt_2.png` | Navigateur de champs (clic droit → Champs) |
| `publisher_odt_3.png` | Dialogue "Champ" → onglet Fonctions |
| `publisher_odt_4.png` | Résultat : champ ajouté avec annotation |
| `publisher_odt_5.png` | Dialogue "Script" pour les tags opérationnels |
| `publisher_odt6.png` (référé) | Remplir Annotation, Insérer |

**Action requise** : Garder les références aux images (`![](./images/publisher-1.png)`, etc.) dans le texte réécrit, même si l'IA a résumé les explications de capture d'écran. Le texte autour des images peut être simplifié mais les références image doivent rester.

---

**Section "Mise en place" : SUPPRIMÉE ENTIÈREMENT**

Ce qui est perdu :
```
* Dépendance Maven vertigo-quarto
* Dépendances Maven pour XDocReportConverterPlugin (fr.opensagres.xdocreport.converter.docx.xwpf, version 2.0.2)
* Dépendances Maven pour OpenOfficeLocalConverterPlugin (fr.opensagres.xdocreport.converter.odt.odfdom, version 2.0.2)
* Configuration XML du provider : <module name="myApp-ressources"><definitions><provider class="..."/>
* Configuration XML du module : <module name="vertigo-quarto"><component api="PublisherManager" class="..."><plugin class="...OpenOfficeMergerPlugin"/></component></module>
```

**Action requise** : Restaurer la section "Mise en place"/"Installation" avec les dépendances Maven et config XML. Les sections "Configuration YAML" peuvent rester.

---

### 1.4 `basic/ui.md` — Erreur de code introduite

**Parenthèse fermante supprimée** :

```
Original : @ComponentScan({        //place here your controller packages for spring component scanning  })
IA       : @ComponentScan({        //place here your controller packages for spring component scanning
```

La parenthèse `})` qui fermait le `@ComponentScan` est supprimée. Le code Java résultant est invalide.

**Action requise** : Remettre `})` à la fin du commentaire.

---

### 1.5 Autres pertes significatives

| Fichier | Contenu perdu | Gravité |
|---|---|---|
| `modules/orchestra.md` | Lien vers le script SQL d'initialisation (github.com/vertigo-io/vertigo-extensions/.../orchestra_create_init_v1.0.0.sql) | 🔴 CRITIQUE — sans ce lien, l'utilisateur ne peut pas créer la base |
| `modules/planning.md` | Lien vers le diagramme mermaid du modèle de données (github.com/.../mermaid-io-vertigo-planning.html) | 🟠 MODÉRÉ — utile pour la compréhension du modèle |
| `basic/dao.md` | Lien vers l'atelier DAO (`/guide/samples_dao`) remplacé par "consulter la documentation sur les Tâches" | 🟠 MODÉRÉ — si le guide existe, c'est une perte |
| `basic/dao.md` | `int actors` dans le KSP batch corrigé en `in actors` | ⚠️ À vérifier — `int` = in + out ? |
| `basic/composants.md` | `@Named("offset")` corrigé en `@ParamValue("offset")` | 🔴 À vérifier — voir §3 |

---

## 2 — Points vérifiés contre code 4.3.2 ✓ TOUS VALIDÉS

**Résultat** : Les 7 corrections IA sont justifiées. La doc humaine comportait des références périmées (API renommées, package réorganisé, chemin de Vega déplacé).

| # | Fichier | Doc humaine (erronée) | Code 4.3.2 | Verdict |
|---|---|---|---|---|
| 1 | `basic/configuration.md` | `AppConfig` | `NodeConfig` (`vertigo-core/io/vertigo/core/node/config/NodeConfig.java`) | ✅ IA correcte |
| 2 | `basic/configuration.md` | `AutoCloseableApp` | `AutoCloseableNode` (`vertigo-core/io/vertigo/core/node/AutoCloseableNode.java`) | ✅ IA correcte |
| 3 | `basic/composants.md` | `@Named` | `@ParamValue` (`vertigo-core/io/vertigo/core/param/ParamValue.java`) | ✅ IA correcte |
| 4 | `modules/orchestra.md` | `impl.process.execution` | `impl.services.execution` (`vertigo-orchestra/io/vertigo/orchestra/impl/services/execution/AbstractActivityEngine.java`) | ✅ IA correcte |
| 5 | `modules/orchestra.md` | `DateUtil.newDateTime()` | `java.time.Instant` (`ProcessScheduler.scheduleAt(ProcessDefinition, Instant, Map)`) | ✅ IA correcte |
| 6 | `overview/core.md` | `AProcess` | `Trace` (`vertigo-core/io/vertigo/core/analytics/trace/Trace.java`) | ✅ IA correcte |
| 7 | `basic/webservices.md` | `/advanced/vega` | `/extensions/vega` (confirmé par `_sidebar.md` line 40) | ✅ IA correcte |

### 2.1 Bonus — `basic/dao.md` : `int actors` → `in actors`

Le mot-clé KSP pour un paramètre d'entrée de type batch est `in`, pas `int`. `int` est une faute de frappe. **LA CORRECTION IA EST JUSTE.**

---

## 3 — Corrections valides (aucune perte)

Ces modifications sont correctes et ne nécessitent pas d'action :

### 3.1 Corrections orthographiques (~45 fichiers)

Typos corrigées : `élement` → `élément`, `maitriser` → `maîtriser`, `permier` → `premier`, `Elless` → `Elles`, `clareté` → `clarté`, `suveillance` → `surveillance`, etc.

### 3.2 Corrections de syntaxe YAML (4 fichiers)

| Fichier | Correction |
|---|---|
| `basic/securite.md` | `modules` → `modules:` |
| `basic/webservices.md` | `modules` → `modules:`, `- port : 8080` → `port: 8080` |
| `extensions/recherche.md` | `io.vertigo.dynamo.DynamoFeatures` → `io.vertigo.datafactory.DataFactoryFeatures` |
| `extensions/social.md` | `modules` → `modules:` |

### 3.3 Corrections de liens obsolètes (3 fichiers)

| Lien | Correction |
|---|---|
| `KleeGroup/vertigo/wiki/routes` | → `vertigo-io/vertigo-core/wiki/routes` |
| `KleeGroup/analytica-server` | → `vertigo-io/vertigo-analytics-server` |
| `KleeGroup/vertigo/blob/master/.../vertigo_1_0.xsd` | → `vertigo-io/vertigo/...` |

### 3.4 Mapping obsolète (2 fichiers)

| Ancien | Nouveau |
|---|---|
| `vertigo-dynamo` | → `vertigo-datastore` |
| `Vertigo-Extensions` | → `Vertigo-Libs` |

### 3.5 Conformité RdvPref (2 fichiers)

Les références au projet RdvPref ont été remplacées par un domaine générique ("gestionprojet", "Projet"), conformément à la règle du SKILL.

### 3.6 Ajouts enrichissants (validés)

Les sections "Pour les experts" ajoutées par l'IA (tableaux de Manages, Features, Plugins, Configuration YAML) sont correctes et enrichissantes. Les garder.

Les 6 fichiers créés (`basics.md`, `datafactory.md`, `stella.md`, `ui-ecosystem.md`, `modules.manifest.md`, `v4.3.0/index.html`) sont nécessaires.

---

## 4 — Propositions d'amélioration (optionnelles)

### 4.1 `intro/why.md` : Clarifier la définition d'Opinionated

Plutôt que de simplement restaurer le texte original, proposer :

```
Vertigo se présente comme une plateforme **Opinionated** (c'est-à-dire un *Opinionated Software Development Framework* — un framework qui prend des positions claires sur l'architecture et les bonnes pratiques).
Ce principe lui permet de maximiser l'efficacité des développements pour les applications métier de type "Application de gestion" : très efficace sur son domaine cible, tout en permettant d'en sortir quand le besoin se fait sentir. Là où d'autres frameworks généralistes visent une efficacité moyenne sur un spectre très large de cas d'usage, Vertigo privilégie la spécialisation.
```

### 4.2 `basic/quarto.md` : Images manquantes — proposer des alternatives

Si les images OpenOffice sont perdues (supprimées du dépôt), proposer :
- Soit restaurer les images depuis le commit 02998ae (`git checkout 02998ae:modules/images/publisher_odt_*.png`)
- Soit les remplacer par des captures d'écran mises à jour (OpenOffice 4.x / LibreOffice 7.x)
- Soit ajouter une note : "Les captures d'écran OpenOffice sont disponibles dans la [documentation complète du Publisher](lien)"

### 4.3 `modules/orchestra.md` : Script SQL

Si le lien GitHub vers le script SQL d'initialisation est mort (repo renommé), proposer :
- Mettre à jour le lien vers le nouveau path
- Ou inclure le contenu du script dans le fichier docs (inline code block)

### 4.4 `basic/dao.md` : Atelier DAO

Si `/guide/samples_dao` n'existe plus dans la sidebar, proposer :
- Soit restaurer la section guide dans le repo docs
- Soit ajouter un lien vers les tests KSP/DAO dans le repo vertigo-core sur GitHub

---

## 5 — Résumé des actions

### Priorité 1 (CRITIQUE — faire immédiatement)

1. `extensions/vega.md` : Restaurer les sections DtListDelta, AutoSortAndPagination (exemples), État Server-side (exemple complet), Rate-Limit (params)
2. `intro/why.md` : Restaurer définition Opinionated + corriger "Elle conçue" → "Elle est conçue"
3. `modules/quarto.md` : Restaurer les 6 références d'images + section "Mise en place" (Maven + XML)
4. `basic/ui.md` : Remettre `})` dans le `@ComponentScan`

### Priorité 2 (À vérifier contre code 4.3.2, puis acter)

5. `basic/configuration.md` : Vérifier `AppConfig` → `NodeConfig`, `AutoCloseableApp` → `AutoCloseableNode`
6. `basic/composants.md` : Vérifier `@Named` → `@ParamValue`
7. `modules/orchestra.md` : Vérifier `impl.process` → `impl.services`, `DateUtil` → `Instant`/`LocalDate`
8. `overview/core.md` : Vérifier `AProcess` → `Trace`
9. `basic/webservices.md` : Vérifier `/advanced/vega` → `/extensions/vega`

### Priorité 3 (Modéré — faire si temps)

10. `modules/orchestra.md` : Restaurer lien script SQL d'initialisation
11. `modules/planning.md` : Restaurer lien mermaid
12. `basic/dao.md` : Vérifier état de `/guide/samples_dao`
13. `basic/dao.md` : Vérifier `int actors` → `in actors` dans KSP batch

### Priorité 4 (Pas de correction — laisser tel quel)

- Les 45 corrections orthographiques : ✅ gardées
- Les corrections YAML : ✅ gardées
- Les corrections de liens KleeGroup → vertigo-io : ✅ gardées
- Les mappings obsolètes (dynamo → datastore, Extensions → Libs): ✅ gardées
- Les sections "Pour les experts" ajoutées : ✅ gardées
- Les 6 fichiers créés : ✅ gardés
- Les substitutions RdvPref → Domaine générique : ✅ gardées
