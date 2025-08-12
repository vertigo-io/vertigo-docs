# Module EasyForms

## Fonctionnalités

EasyForms permet à un administrateur fonctionnel de créer et modifier des formulaires dynamiques, ensuite remplis par les utilisateurs de l'application.

Le module offre aux administrateurs des fonctionnalités avancées :

* Configuration multilingue des champs de saisie
* Ajout de blocs de texte enrichi via un éditeur WYSIWYG
* Mise en place de règles dynamiques d’affichage des champs, permettant une visibilité conditionnelle en fonction des réponses à d’autres champs
* Définition de contraintes métier spécifiques à chaque champ

Ce module est extensible et permet :

* L’ajout de nouveaux types de champs
* La configuration de contraintes spécifiques à votre métier
* L’adaptation du workflow de création et gestion des formulaires au contexte projet

EasyForms repose sur un modèle de stockage flexible au format JSON, garantissant une autonomie totale vis-à-vis de la base de données.

---

## Installation

### Ajout du module dans `pom.xml`

Ajoutez la dépendance suivante dans le fichier `pom.xml` :

```xml
<dependency>
   <groupId>io.vertigo</groupId>
   <artifactId>vertigo-easyforms</artifactId>
   <version>4.3.2</version>
</dependency>
```

### Ajout à la configuration Vertigo

Dans la configuration YAML, activez la fonctionnalité `EasyFormsFeatures` :

```yaml
  io.vertigo.easyforms.EasyFormsFeatures:
    features:
      - easyforms:
          languages: en, fr
          filestore.persist: main
          filestore.tmp: temp
```

#### Description des paramètres

* `languages` : Liste des langues prises en charge pour les formulaires (ex. : en, fr).
* `filestore.persist` : Nom du `filestore` déclaré dans la configuration, utilisé pour le stockage permanent des fichiers liés aux formulaires.
* `filestore.tmp` : Nom du `filestore` pour le stockage temporaire des fichiers avant enregistrement.

---

## Ajout au projet

La persistance des données en base est organisée en deux parties :

* Les modèles de formulaire sont stockés dans une table dédiée (`EASY_FORM`).
* Les réponses aux formulaires sont enregistrées dans les tables métier, via une colonne de type `DoEfFormData`.

### Configuration VertigoStudio

Ajoutez les définitions EasyForms à la configuration Studio (ex. `studio-config.yaml`) :

```yaml
resources:
  - { type: kpr, path: classpath:io/vertigo/easyforms/studio/application.kpr}
```

### Création des tables en base

Si vous utilisez Liquibase :

```xml
<changeSet author="vertigo" id="init-easyforms">
    <sqlFile encoding="utf8" path="/io/vertigo/easyforms/sql/easyforms_create_init-4.2.0.sql" />
</changeSet>
```

Ou exécutez manuellement le fichier `easyforms_create_init-4.2.0.sql`.

### Ajout de la colonne de réponse dans les tables métier

Dans le fichier KSP correspondant :

```ksp
field response {domain: DoEfFormData label:"Réponse formulaire" cardinality:"1"}
```

---

## Intégration dans l’application

### Administration des formulaires

#### Côté contrôleur

* Injection du contrôleur designer :

```java
@Inject
private EasyFormsDesignerController easyFormsDesignerController;
```

* Initialisation lors du `initContext` :

```java
easyFormsDesignerController.initContext();
```

* Sauvegarde :

  * Récupérer le formulaire via `easyFormsController.readEasyForm(viewContext)`.
  * Sauvegarder en service (transaction) via `easyFormsDesignerServices.saveForm(easyForm)`.

#### Côté HTML

* Ajout du script nécessaire :

```html
<script th:src="@{/vertigo-ui/static/easyforms/js/vertigo-easyforms.js}" th:data-context="@{/}"></script>
```

* Ajout de la balise :

```html
<vu:easy-forms-admin />
```

*Conseil* : Ajoutez un paramètre de version dans l’URL JS pour invalider le cache navigateur lors des mises à jour, par ex. :
`...js?t=__${appBuildTime}__`

---

### Intégration d’un formulaire dans une page métier

#### Côté contrôleur

* Injection du contrôleur runner :

```java
@Inject
private EasyFormsRunnerController easyFormsRunnerController;
```

* Initialisation lors du `initContext` :

```java
easyFormsRunnerController.initEditContext();
```

* Sauvegarde : la réponse est enregistrée en JSON dans l’objet métier.

#### Côté HTML

* Ajout du script nécessaire :

```html
<script th:src="@{/vertigo-ui/static/easyforms/js/vertigo-easyforms.js}" th:data-context="@{/}"></script>
```

* Ajout de la balise :

```html
<vu:easy-forms object="myObject" field="formResponse" template="${model.formModel}" />
```

*Conseil* : même recommandation que pour l’administration concernant le paramètre de version.

---

## Fonctionnalités avancées

### Contexte additionnel

Il est possible d’utiliser des informations du contexte métier dans la configuration du formulaire (valeurs par défaut, conditions d’affichage, etc.) :

* Dans le `initContext` du designer (`additionalContext`) pour accepter ces paramètres.
* Facultativement dans celui du runner (`additionalContextKeys`) pour les ajouter à `VueData`.

---

### Types de champs personnalisés

Pour déclarer de nouveaux types de champs :

* Créer une classe héritant de `DefinitionProvider<EasyFormsFieldTypeDefinition>`.
* Voir les types intégrés dans : [FieldTypeDefinitionProvider.java](https://github.com/vertigo-io/vertigo-modules/blob/develop/vertigo-easyforms/src/main/java/io/vertigo/easyforms/runner/pack/provider/FieldTypeDefinitionProvider.java)
* Exemple : [MarsEasyFormsFieldTypeDefinitionProvider.java](https://github.com/vertigo-io/vertigo-mars/blob/develop/src/main/java/io/mars/support/easyforms/MarsEasyFormsFieldTypeDefinitionProvider.java)

Pour ajouter un rendu UI personnalisé :

* Créer une classe héritant de `DefinitionProvider<EasyFormsUiComponentDefinition>` et implémenter le rendu dans la balise `<vu:easy-forms>`.

Exemple pour un type `slider` :

```html
<vu:easy-forms ...>
    <div th:case="EfUicSlider">
        ...
    </div>
</vu:easy-forms>
```

Les libellés doivent être ajoutés au moteur i18n Vertigo avec la convention `EfFty<NomType>` ou `EfFty<NomType>$<NomParam>`.

---

### Validateurs personnalisés

Pour ajouter des validateurs spécifiques :

* Créer une classe héritant de `DefinitionProvider<EasyFormsFieldValidatorTypeDefinition>`.
* Voir les validateurs intégrés ici : [FieldValidatorTypeDefinitionProvider.java](https://github.com/vertigo-io/vertigo-modules/blob/develop/vertigo-easyforms/src/main/java/io/vertigo/easyforms/runner/pack/provider/FieldValidatorTypeDefinitionProvider.java)

---

Si tu veux, je peux aussi te formater cette doc **exactement** comme celles présentes dans [`vertigo-docs/extensions`](https://github.com/vertigo-io/vertigo-docs/tree/gh-pages/extensions) pour qu’elle s’intègre directement dans le site officiel Vertigo.
Veux-tu que je fasse cette mise en forme ?
