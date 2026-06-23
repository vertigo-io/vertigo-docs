# vertigo-basics

**vertigo-basics** est une librairie utilitaire fournissant les composants de base pour construire les `SmartType` et les `Task` d'une application Vertigo : formateurs, validateurs et moteurs d'exécution SQL. Aucune déclaration YAML n'est requise ; l'intégration se fait exclusivement via une dépendance Maven.

Le module expose trois packages :

| Package | Contenu |
|---|---|
| `io.vertigo.basics.formatter` | 7 classes de formatage pour les BasicType |
| `io.vertigo.basics.constraint` | 9 contraintes de validation |
| `io.vertigo.basics.task` | 5 TaskEngines SQL + 3 préprocesseurs |

---

## Principe

Chaque SmartType peut être annoté avec un `Formatter` (pour la conversion affichage/saisie) et une ou plusieurs `Constraint` (pour la validation). Les SmartType ainsi définis sont ensuite consommés par les TaskEngine SQL, qui exécutent les requêtes relationnelles en mappant les paramètres et résultats aux types du domaine.

Les TaskEngine passent les requêtes SQL par un pipeline de 3 préprocesseurs avant exécution : `ScriptPreProcessor` → `TrimPreProcessor` → `WhereInPreProcessor`.

```
SmartType (Formatter + Constraint)
        ↓
    Task (KSP)
        ↓
    TaskEngine SQL → Préprocesseurs → JDBC
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
| `FormatterNumber` | `BigDecimal`, `Double`, `Integer`, `Long` | Pattern `DecimalFormat` (`#,###.##`) |
| `FormatterNumberLocalized` | `BigDecimal`, `Double`, `Integer`, `Long` | `pattern \| sepDécimal \| sepMillier` |
| `FormatterDate` | `LocalDate`, `Instant` | `formatAffichage;{autresFormatsSaisie}` (défaut `dd/MM/yyyy`) |
| `FormatterBoolean` | `Boolean` | `formatOui; formatNon` |
| `FormatterId` | `Long` | — |
| `FormatterDefault` | Tous | Délège aux formateurs simples via paramètres app-level |

### SmartType avec FormatterDefault

```java
package com.monprojet.smarttypes;

import java.math.BigDecimal;

import io.vertigo.basics.formatter.FormatterDefault;
import io.vertigo.basics.formatter.FormatterNumber;
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

	@SmartTypeDefinition(BigDecimal.class)
	@Formatter(clazz = FormatterNumber.class, arg = "#,##0.00")
	@SmartTypeProperty(property = "storeType", value = "NUMERIC")
	Budget;
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

### FormatterNumberLocalized (séparateurs explicites)

```java
	@SmartTypeDefinition(BigDecimal.class)
	@Formatter(clazz = FormatterNumberLocalized.class, arg = "#,##0.00 | . | ,")
	@SmartTypeProperty(property = "storeType", value = "NUMERIC")
	MontantHt,
```

---

## Contraintes

Valident une donnée selon les règles du SmartType. Déclarées via `@Constraint(clazz = ..., arg = "...")`.

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
import io.vertigo.basics.formatter.FormatterNumber;
import io.vertigo.datamodel.smarttype.annotations.Constraint;
import io.vertigo.datamodel.smarttype.annotations.Formatter;
import io.vertigo.datamodel.smarttype.annotations.SmartTypeDefinition;
import io.vertigo.datamodel.smarttype.annotations.SmartTypeProperty;

public enum MonProjetSmartTypes {

	// Budget : max 10 chiffres, 2 décimales
	@SmartTypeDefinition(BigDecimal.class)
	@Formatter(clazz = FormatterNumber.class, arg = "#,##0.00")
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

5 moteurs couvrent les opérations relationnelles. Le `className` dans le KSP détermine le moteur utilisé.

| Classe | Rôle |
|---|---|
| `TaskEngineSelect` | SELECT → DTO ou DTC |
| `TaskEngineProc` | INSERT / UPDATE / DELETE unitaire |
| `TaskEngineProcBatch` | INSERT / UPDATE / DELETE par lots |
| `TaskEngineInsert` | INSERT → retourne la clé générée |
| `TaskEngineInsertBatch` | Batch INSERT → retourne les clés générées |

### SELECT

```ksp
create Task TkFindTachesByProjet {
	className : "io.vertigo.basics.task.TaskEngineSelect"
	request : "
		SELECT t.*
		FROM tache t
		WHERE t.PROJ_ID = #projId#
		ORDER BY t.DATE_DEBUT, t.TACHE_ID
		"
	in   projId	{domain : DoId			cardinality: "1"	}
	out taches	{domain : DoDtTache		cardinality: "*"	}
}
```

### INSERT avec clé générée

```ksp
create Task TkSaveProjet {
	className : "io.vertigo.basics.task.TaskEngineInsert"
	request : "
		INSERT INTO projet (PROJ_ID, PROJ_NOM, PROJ_ETAT)
		VALUES (null, #dto.projNom#, #dto.projEtat#)
		"
	in   dto	{domain : DoDtProjet		cardinality: "1"	}
}
```

Le premier paramètre de la colonne clé est passé `null` ; la base génère la valeur. La clé générée est réinjectée automatiquement dans le DTO d'entrée.

### UPDATE / DELETE (TaskEngineProc)

```ksp
create Task TkUpdateTacheEtat {
	className : "io.vertigo.basics.task.TaskEngineProc"
	request : "
		UPDATE tache
		SET TACHE_ETAT = #nouvelEtat#
		WHERE TACHE_ID = #tacheId#
		"
	in   tacheId		{domain : DoId		cardinality: "1"	}
	in   nouvelEtat	{domain : DoLabel	cardinality: "1"	}
	out intSqlRowcount	{domain : DoId		cardinality: "1"	}
}
```

### Batch INSERT avec clés générées

```ksp
create Task TkBatchSaveTaches {
	className : "io.vertigo.basics.task.TaskEngineInsertBatch"
	request : "
		INSERT INTO tache (TACHE_ID, PROJ_ID, TACHE_LIBELLE, DATE_DEBUT)
		VALUES (null, #tachees.projetId#, #tachees.libelle#, #tachees.dateDebut#)
		"
	in   tachees	{domain : DoDtTache		cardinality: "*"	}
}
```

### Batch UPDATE (TaskEngineProcBatch)

```ksp
create Task TkBatchArchiveTaches {
	className : "io.vertigo.basics.task.TaskEngineProcBatch"
	request : "
		UPDATE tache
		SET TACHE_ETAT = 'ARCHIVE'
		WHERE TACHE_ID = #tacheId#
		"
	in   tacheIds	{domain : DoId		cardinality: "*"	}
	out intSqlRowcount	{domain : DoId		cardinality: "1"	}
}
```

---

## Préprocesseurs SQL

Les TaskEngineSQL passent chaque requête par un pipeline de 3 préprocesseurs, dans cet ordre :

| Préprocesseur | Rôle |
|---|---|
| `ScriptPreProcessor` | Évalue du code Java embarqué (syntaxe JSP-like `<% %>`) pour construire dynamiquement le SQL |
| `TrimPreProcessor` | Nettoie les CRLF et espaces superflus générés par les blocs conditionnels |
| `WhereInPreProcessor` | Expand `#NOM.ROWNUM.FIELD#` en clause IN avec paramètres bindés (scinde en lots de 1 000) |

### Conditions dynamiques (ScriptPreProcessor)

```ksp
create Task TkFindTachesByCriteria {
	className : "io.vertigo.basics.task.TaskEngineSelect"
	request : "
		SELECT t.*
		FROM tache t
		WHERE 1=1
		<%if(projId != null) {%>
			AND t.PROJ_ID = #projId#
		<%}%>
		<%if(etat != null) {%>
			AND t.TACHE_ETAT = #etat#
		<%}%>
		ORDER BY t.DATE_DEBUT
		"
	in   projId	{domain : DoId		cardinality: "?"	}
	in   etat	{domain : DoLabel	cardinality: "?"	}
	out  taches	{domain : DoDtTache	cardinality: "*"	}
}
```

Le code entre `<% %>` a accès aux variables d'entrée de la Task. Le `TrimPreProcessor` nettoie automatiquement les sauts de ligne vides laissés par les branches non prises.

### Expansion WHERE IN (WhereInPreProcessor)

```ksp
create Task TkFindTachesByProjets {
	className : "io.vertigo.basics.task.TaskEngineSelect"
	request : "
		SELECT t.*
		FROM tache t
		WHERE t.PROJ_ID IN (#projets.ROWNUM.projId#)
		ORDER BY t.DATE_DEBUT
		"
	in   projets	{domain : DoDtProjet	cardinality: "*"	}
	out  taches	{domain : DoDtTache	cardinality: "*"	}
}
```

`#projets.ROWNUM.projId#` est expandé en `#projets.0.projId#, #projets.1.projId#, …` (indices 0-based). Les listes dépassant 1 000 éléments sont automatiquement scindées en clauses IN/OR multiples.

---

## Syntaxe SQL dans les requêtes KSP

| Syntaxe | Direction | Exemple |
|---|---|---|
| `#NOM#` | IN | `WHERE ID = #id#` |
| `#DTO.FIELD#` | IN (champ DTO) | `VALUES (#dto.nom#)` |
| `%NOM%` | OUT | `OUT %rowcount%` |
| `@NOM@` | INOUT | `@cursor@` |
| `#NOM.ROWNUM.FIELD#` | IN (liste) | `IN (#items.ROWNUM.id#)` |
| `<% code Java %>` | Script | `<%if(x != null){%> AND x=#x# <%}%>` |

---

## Vigilance

- **Format vs Saisie** : `FormatterDate` prend un format d'affichage et des formats de saisie séparés par `;`. Ne pas confondre l'ordre : le premier format est **toujours** l'affichage.
- **Constraint empilées** : plusieurs `@Constraint` sur un même SmartType sont toutes évaluées. L'ordre de déclaration détermine l'ordre de validation.
- **WHERE IN avec scission automatique** : `WhereInPreProcessor` scinde automatiquement les listes > 1 000 éléments en clauses IN/OR multiples. Pas de limitation côté applicatif.
- **ScriptPreProcessor et injection** : le code `<% %>` est du Java interprété. Les seules variables accessibles sont les paramètres d'entrée de la Task — aucune donnée utilisateur brute n'y transite, ce qui préserve la protection contre l'injection SQL.
- **FormatterDefault** : délègue aux formateurs simples en lisant les paramètres de configuration application-level. Si aucun paramètre n'est défini, le comportement par défaut dépend du BasicType (toString() pour les cas non couverts).
- **generatedKey** : avec `TaskEngineInsert`, la colonne clé du VALUES doit être `null` pour que la base génère la valeur. La clé générée est réinjectée automatiquement dans le DTO d'entrée — aucun OUT séparé n'est nécessaire.
