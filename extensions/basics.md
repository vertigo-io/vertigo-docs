# vertigo-basics

**vertigo-basics** est une librairie utilitaire fournissant les composants de base pour construire les `SmartType` et les `Task` d'une application Vertigo : formateurs, validateurs et moteurs d'exécution SQL. Aucune déclaration YAML n'est requise ; l'intégration se fait exclusivement via une dépendance Maven.

Le module expose trois packages :

| Package | Contenu |
|---|---|
| `io.vertigo.basics.formatter` | 5 classes de formatage pour les BasicType |
| `io.vertigo.basics.constraint` | 10 classes de validation (incluant `ConstraintUtil`) |
| `io.vertigo.basics.task` | 3 TaskEngine SQL (`AbstractTaskEngineSQL`, `TaskEngineProcBatch`, `TaskEngineInsertBatch`) |

---

## Principe

Chaque SmartType peut être annoté avec un `Formatter` (pour la conversion affichage/saisie) et une ou plusieurs `Constraint` (pour la validation). Les SmartType ainsi définis sont ensuite consommés par les TaskEngine SQL, qui exécutent les requêtes relationnelles en mappant les paramètres et résultats aux types du domaine.

```
SmartType (Formatter + Constraint)
        ↓
    Task (KSP)
        ↓
    TaskEngine SQL → JDBC
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

| Formatter | BasicType | Args |
|---|---|---|
| `FormatterString` | `String` | `BASIC`, `UPPER`, `LOWER`, `UPPER_FIRST` |
| `FormatterDate` | `LocalDate`, `Instant` | `formatAffichage;{autresFormatsSaisie}` (défaut `dd/MM/yyyy`) |
| `FormatterBoolean` | `Boolean` | `formatOui; formatNon` |
| `FormatterId` | `Long` | — |
| `FormatterDefault` | Tous | Délège aux formateurs simples via paramètres app-level |

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
	@Formatter(clazz = FormatterBoolean.class, arg = "Actif; Inactif")
	@SmartTypeProperty(property = "storeType", value = "BOOLEAN")
	EstActif,
```

---

## Contraintes

Valident une donnée selon les règles du SmartType. Déclarées via `@Constraint(clazz = ..., arg = "...")`. La classe utilitaire `ConstraintUtil` regroupe les méthodes d'aide pour la programmation des contraintes.

| Contrainte | Args | Rôle |
|---|---|---|
| `ConstraintStringLength` | entier | Max nombre de caractères |
| `ConstraintIntegerLength` | entier (< 10) | Max nombre de chiffres |
| `ConstraintLongLength` | entier (< 19) | Max nombre de chiffres |
| `ConstraintDoubleLength` | entier (n) | Amplitude ]-10^n, 10^n[ |
| `ConstraintBigDecimalLength` | entier (n) | Amplitude ]-10^n, 10^n[ |
| `ConstraintBigDecimal` | `M,D` | Décimal(M,D) : M chiffres totaux, D décimales |
| `ConstraintNumberMinimum` | double | Valeur ≥ seuil |
| `ConstraintNumberMaximum` | double | Valeur ≤ seuil |
| `ConstraintRegex` | pattern | Correspondance RegExp |

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

Les classes `AbstractTaskEngineSQL`, `TaskEngineProcBatch` et `TaskEngineInsertBatch` sont fournies par le package `io.vertigo.basics.task`. Voir [database.md](database.md) pour les TaskEngine concrets.

Le `className` dans le KSP détermine le moteur SQL utilisé. Voir [database.md](database.md) pour les exemples complets de SELECT, INSERT, UPDATE, DELETE.

---

## Vigilance

- **Format vs Saisie** : `FormatterDate` prend un format d'affichage et des formats de saisie séparés par `;`. Ne pas confondre l'ordre : le premier format est **toujours** l'affichage.
- **Constraint empilées** : plusieurs `@Constraint` sur un même SmartType sont toutes évaluées. L'ordre de déclaration détermine l'ordre de validation.
- **FormatterDefault** : délègue aux formateurs simples en lisant les paramètres de configuration application-level. Si aucun paramètre n'est défini, le comportement par défaut dépend du BasicType (toString() pour les cas non couverts).

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
| **Contraintes** | `ConstraintUtil`, `ConstraintNumberMinimum`, `ConstraintNumberMaximum`, `ConstraintStringLength`, `ConstraintIntegerLength`, `ConstraintDoubleLength`, `ConstraintBigDecimal`, `ConstraintBigDecimalLength`, `ConstraintLongLength`, `ConstraintRegex` | `constraint/ConstraintUtil.java` |
| **Formatters** | `FormatterBoolean`, `FormatterDate`, `FormatterDefault`, `FormatterId`, `FormatterString` | `formatter/FormatterBoolean.java` |
| **Task Engines** | `AbstractTaskEngineSQL`, `TaskEngineProcBatch`, `TaskEngineInsertBatch` | `task/AbstractTaskEngineSQL.java` |
