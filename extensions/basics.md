# vertigo-basics

**vertigo-basics** est une bibliothèque utilitaire fournissant les composants de base pour construire les `SmartType` et les `Task` d'une application Vertigo : formateurs, validateurs et moteurs d'exécution SQL. Aucune déclaration YAML n'est requise ; l'intégration se fait exclusivement via une dépendance Maven.

Le module expose trois packages :

| Package | Contenu |
|---|---|
| `io.vertigo.basics.formatter` | 9 classes de formatage pour les BasicType |
| `io.vertigo.basics.constraint` | 12 classes de validation (incluant `AbstractConstraintLength` et `ConstraintUtil`) |
| `io.vertigo.basics.task` | 9 classes de TaskEngine SQL et préprocesseurs |

---

## Principe

Chaque SmartType peut être annoté avec un `Formatter` (pour la conversion affichage/saisie) et une ou plusieurs `Constraint` (pour la validation). Les SmartType ainsi définis sont ensuite consommés par les TaskEngine SQL, qui exécutent les requêtes relationnelles en mappant les paramètres et résultats aux types du domaine.

Le flux complet d'exécution SQL intègre une chaîne de préprocesseurs pour la transformation des scripts avant exécution JDBC :

```
Script SQL brut
        ↓
ScriptPreProcessor  (<% %>, <%= %>)
        ↓
TrimPreProcessor   (nettoyage retours chariot)
        ↓
WhereInPreProcessor  (expansion IN, chunking 1000)
        ↓
AbstractTaskEngineSQL (transaction, injection managers)
        ↓
    doExecute (Select / Proc / Insert)
        ↓
    JDBC
        ↓
    DTO / DTC
```

---

## Activation

Ajouter les dépendances Maven :

```xml
<!-- Obligatoire : définitions SmartType, DTO, Task -->
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-datamodel</artifactId>
</dependency>

<!-- Optionnel : TaskEngine SQL (SELECT, INSERT, UPDATE, DELETE) -->
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-database</artifactId>
</dependency>
```

Aucune feature YAML, aucun paramétrage complémentaire. Les classes sont détectées par le classpath.

---

## Formatters

Convertissent une donnée typée vers une chaîne affichable et inversement. Déclarés sur un SmartType via `@Formatter(clazz = ..., arg = "...")`.

| Formatter | Héritage | BasicType | Args |
|---|---|---|---|
| `FormatterString` | final | `String` | `BASIC`, `UPPER`, `LOWER`, `UPPER_FIRST` (via enum `FormatterString.Mode`) |
| `FormatterNumber` | héritable | `BigDecimal`, `Double`, `Integer`, `Long` | Pattern `DecimalFormat` (défaut : séparateur décimal virgule, milliers espace) |
| `FormatterNumberLocalized` | héritable | Idem `FormatterNumber` | Extension locale : utilise `LocaleManager`, cache `DecimalFormatSymbols` par locale |
| `FormatterId` | final | `Long` | — (conversion sans séparateur) |
| `FormatterDate` | final | `LocalDate`, `Instant` | `formatAffichage;{autresFormatsSaisie}` (défaut `dd/MM/yyyy`). Utilise `LocaleManager` + `ZoneId` |
| `FormatterBoolean` | final | `Boolean` | `formatOui;formatNon` (texte affiché). Saisie accepte `true`/`false`/`1`/`0` |
| `FormatterDefault` | final | Tous | Facade dispatch par `BasicType`. Args via `ParamManager` : `FmtStringDefaultArgs`, `FmtLocalDateDefaultArgs`, `FmtInstantDefaultArgs`, `FmtBooleanDefaultArgs`, `FmtNumberDefaultArgs` |

Les erreurs de formatage utilisent 4 clés i18n définies dans `Resources` (package `formatter`).

### SmartType avec FormatterDefault

```java
package com.monprojet.smarttypes;

import java.math.BigDecimal;

import io.vertigo.basics.formatter.FormatterDefault;
import io.vertigo.datamodel.smarttype.annotations.Formatter;
import io.vertigo.datamodel.smarttype.annotations.SmartTypeDefinition;
import io.vertigo.datamodel.smarttype.annotations.SmartTypeProperty;

public enum MonProjetSmartTypes {

	@SmartTypeDefinition(String.class)
	@Formatter(clazz = FormatterDefault.class)
	@SmartTypeProperty(property = "storeType", value = "TEXT")
	Label,

	@SmartTypeDefinition(Long.class)
	@Formatter(clazz = FormatterDefault.class)
	@SmartTypeProperty(property = "storeType", value = "NUMERIC")
	Id,
}
```

### FormatterDate avec formats de saisie multiples

```java
	@SmartTypeDefinition(LocalDate.class)
	@Formatter(clazz = FormatterDate.class, arg = "dd/MM/yyyy;yyyy-MM-dd;dd-MM-yyyy")
	@SmartTypeProperty(property = "storeType", value = "DATE")
	DateDebut,
```

Le premier format est utilisé pour l'affichage. Les formats suivants sont tentés lors de la saisie.

### FormatterBoolean sur mesure

```java
	@SmartTypeDefinition(Boolean.class)
	@Formatter(clazz = FormatterBoolean.class, arg = "Actif;Inactif")
	@SmartTypeProperty(property = "storeType", value = "BOOLEAN")
	EstActif,
```

---

## Contraintes

Valident une donnée selon les règles du SmartType. Déclarées via `@Constraint(clazz = ..., arg = "...")`. Il est possible de surcharger le message d'erreur via le paramètre optionnel `msg` de l'annotation.

Les contraints de longueur (`StringLength`, `IntegerLength`, `LongLength`, `DoubleLength`, `BigDecimalLength`) partagent une implémentation commune via `AbstractConstraintLength`, qui gère la propriété `maxLength` et `DtProperty.MAX_LENGTH`. Les erreurs de contrainte utilisent 8 clés i18n définies dans `Resources` (package `constraint`).

| Contrainte | Héritage | Args | Rôle |
|---|---|---|---|
| `ConstraintStringLength` | final | entier (maxLength) | `String.length()` ≤ maxLength |
| `ConstraintRegex` | final | pattern | Correspondance `Pattern.matches()` |
| `ConstraintNumberMinimum` | final | double | `Number.doubleValue()` ≥ minValue |
| `ConstraintNumberMaximum` | final | double | `Number.doubleValue()` ≤ maxValue |
| `ConstraintLongLength` | final (via Abstract) | entier (< 19) | `Long` ∈ ]-10^n, 10^n[ |
| `ConstraintIntegerLength` | final (via Abstract) | entier (< 10) | `Integer` ∈ ]-10^n, 10^n[ |
| `ConstraintDoubleLength` | final (via Abstract) | entier (n) | `Double` ∈ ]-10^n, 10^n[ |
| `ConstraintBigDecimalLength` | final (via Abstract) | entier (n) | `BigDecimal` ∈ ]-10^n, 10^n[ |
| `ConstraintBigDecimal` | final | `M,D` | Décimal(M,D) : M chiffres totaux, D décimales. Applique `stripTrailingZeros()` |

La classe utilitaire `ConstraintUtil` (final, constructeur privé, méthodes statiques) regroupe les méthodes d'aide pour construire les messages d'erreur via `LocaleMessageText`.

### SmartType avec contraintes composées

```java
package com.monprojet.smarttypes;

import java.math.BigDecimal;

import io.vertigo.basics.constraint.ConstraintBigDecimal;
import io.vertigo.basics.constraint.ConstraintNumberMaximum;
import io.vertigo.basics.constraint.ConstraintNumberMinimum;
import io.vertigo.basics.constraint.ConstraintRegex;
import io.vertigo.basics.constraint.ConstraintStringLength;
import io.vertigo.datamodel.smarttype.annotations.Constraint;
import io.vertigo.datamodel.smarttype.annotations.SmartTypeDefinition;
import io.vertigo.datamodel.smarttype.annotations.SmartTypeProperty;

public enum MonProjetSmartTypes {

	// Budget : max 10 chiffres, 2 décimales
	@SmartTypeDefinition(BigDecimal.class)
	@Constraint(clazz = ConstraintBigDecimal.class, arg = "10,2")
	@SmartTypeProperty(property = "storeType", value = "NUMERIC")
	Budget,

	// Pourcentage d'avancement : entre 0 et 100
	@SmartTypeDefinition(BigDecimal.class)
	@Constraint(clazz = ConstraintBigDecimal.class, arg = "5,2")
	@Constraint(clazz = ConstraintNumberMinimum.class, arg = "0")
	@Constraint(clazz = ConstraintNumberMaximum.class, arg = "100")
	@SmartTypeProperty(property = "storeType", value = "NUMERIC")
	TacheAvancee,

	// Code tâche interne : 3 lettres puis 4 chiffres
	@SmartTypeDefinition(String.class)
	@Constraint(clazz = ConstraintRegex.class, arg = "^[A-Z]{3}-\\d{4}$")
	@SmartTypeProperty(property = "storeType", value = "TEXT")
	CodeInterne,

	// Libellé court : max 50 caractères
	@SmartTypeDefinition(String.class)
	@Constraint(clazz = ConstraintStringLength.class, arg = "50")
	@SmartTypeProperty(property = "storeType", value = "TEXT")
	TacheLibelle;
}
```

Plusieurs `@Constraint` peuvent empiler sur un même SmartType. Toutes les contraintes sont évaluées à chaque validation.

---

## TaskEngine SQL

Les TaskEngine SQL sont organisés autour de `AbstractTaskEngineSQL`, classe abstraite fournissant l'infrastructure commune : chaîne de préprocesseurs SQL, gestion transactionnelle, et injection de 5 managers (`SqlManager`, `ScriptManager`, `VTransactionManager`, `SmartTypeManager`, `AnalyticsManager`). Chaque sous-classe implémente la méthode abstraite `doExecute`.

Les constantes `SQL_MAIN_RESOURCE_ID` et `SQL_ROWCOUNT` sont définies dans `AbstractTaskEngineSQL`.

| TaskEngine | Héritage | Rôle |
|---|---|---|
| `TaskEngineSelect` | héritable | Requêtes SELECT. Dispatch automatique entre `DtList` (multi-lignes) et singleton (une ligne). |
| `TaskEngineProc` | héritable | Requêtes INSERT/UPDATE/DELETE. Retourne le rowcount d'exécution. |
| `TaskEngineInsert` | héritable | INSERT avec injection de clés générées via `DataAccessor`. Utilisé par `SqlEntityStorePlugin` et accessible aux développeurs. |
| `TaskEngineProcBatch` | final | Exécution batch de requêtes SQL. Un attribut IN de type hasMany. |
| `TaskEngineInsertBatch` | final | Insertion batch avec retour des générées clés. |

### Préprocesseurs SQL

`AbstractTaskEngineSQL` applique automatiquement une chaîne de trois préprocesseurs à chaque script SQL avant exécution :

1. **ScriptPreProcessor** — Syntaxe SQL JSP-like : `<% %>` pour les blocs conditionnels, `<%= %>` pour l'interpolation d'expressions.
2. **TrimPreProcessor** — Nettoyage des retours chariot redondants pour produire du SQL compact.
3. **WhereInPreProcessor** — Expansion des clauses `IN` : chunking automatique par tranche de 1000 éléments. Collections vides résolues en `1=1` (SELECT) ou `1=2` (DML).

Les préprocesseurs ont une visibilité package et ne sont pas destinés à un usage direct depuis les projets application. Pour plus d'informations sur les TaskEngine SQL, voir [database.md](database.md).

---

## Vigilance

- **Format vs Saisie** : `FormatterDate` prend un format d'affichage et des formats de saisie séparés par `;`. Ne pas confondre l'ordre : le premier format est **toujours** l'affichage. Les formats peuvent inclure l'heure (ex: `dd/MM/yyyy HH:mm`) pour les `Instant`.
- **Constraint empilées** : plusieurs `@Constraint` sur un même SmartType sont toutes évaluées. L'ordre de déclaration détermine l'ordre de validation. Le message d'erreur par défaut peut être surchargé via `msg`.
- **FormatterDefault** : délègue aux formateurs simples en lisant les paramètres de configuration application-level via `ParamManager`. Si aucun paramètre n'est défini, le comportement par défaut dépend du BasicType (`toString()` pour les cas non couverts).
- **FormatterNumber vs FormatterNumberLocalized** : `FormatterNumber` applique un formatage fixe (virgule décimale, espace milliers). `FormatterNumberLocalized` adapte le formatage à la locale de l'utilisateur via `LocaleManager`.
- **Préprocesseurs package-private** : les classes `ScriptPreProcessor`, `TrimPreProcessor` et `WhereInPreProcessor` ne sont accessibles qu'en interne. Ne pas tenter de les instancier directement depuis le code application.
- **Chunking IN (1000)** : `WhereInPreProcessor` divise les collections de plus de 1000 éléments en plusieurs clauses `IN` pour respecter les limites SGBD. Collections vides produisent `1=1` en sélection et `1=2` en modification.

---

## Pour les experts

### Managers
Aucun.

### Features
Aucune classe `*Features.java` — vertigo-basics ne déclare pas de features. L'intégration se fait par dépendance Maven uniquement.

### Plugins
Aucun.

### Composition

| Catégorie | Classes | Fichier clé |
|---|---|---|
| **Formatters** | `FormatterString`, `FormatterNumber`, `FormatterNumberLocalized`, `FormatterId`, `FormatterDate`, `FormatterBoolean`, `FormatterDefault`, `FormatterString.Mode`, `Resources` | `io/vertigo/basics/formatter/FormatterString.java` |
| **Contraintes** | `AbstractConstraintLength`, `ConstraintStringLength`, `ConstraintRegex`, `ConstraintNumberMinimum`, `ConstraintNumberMaximum`, `ConstraintLongLength`, `ConstraintIntegerLength`, `ConstraintDoubleLength`, `ConstraintBigDecimalLength`, `ConstraintBigDecimal`, `ConstraintUtil`, `Resources` | `io/vertigo/basics/constraint/AbstractConstraintLength.java` |
| **Task Engines** | `AbstractTaskEngineSQL`, `TaskEngineSelect`, `TaskEngineProc`, `TaskEngineInsert`, `TaskEngineProcBatch`, `TaskEngineInsertBatch` | `io/vertigo/basics/task/AbstractTaskEngineSQL.java` |
| **Préprocesseurs** | `ScriptPreProcessor`, `TrimPreProcessor`, `WhereInPreProcessor` | `io/vertigo/basics/task/ScriptPreProcessor.java` |
