# EasyForms Module

## Features

EasyForms allows a functional administrator to create and modify dynamic forms, then filled out by application users.

The module offers administrators advanced features:

* Multilingual configuration of input fields
* Addition of rich text blocks via a WYSIWYG editor
* Dynamic field display rules, enabling conditional visibility based on responses to other fields
* Definition of specific business constraints per field

This module is extensible and allows:

* Adding new field types
* Configuring constraints specific to your business
* Adapting the form creation and management workflow to the project context

EasyForms relies on a flexible JSON storage model, guaranteeing total autonomy from the database.

---

## Installation

### Adding the module to `pom.xml`

Add the following dependency to the `pom.xml` file:

```xml
<dependency>
   <groupId>io.vertigo</groupId>
   <artifactId>vertigo-easyforms</artifactId>
   <version>4.3.2</version>
</dependency>
```

### Adding to Vertigo configuration

In the YAML configuration, activate the `EasyFormsFeatures` feature:

```yaml
  io.vertigo.easyforms.EasyFormsFeatures:
    features:
      - easyforms:
          languages: en, fr
          filestore.persist: main
          filestore.tmp: temp
```

#### Parameter description

* `languages`: List of languages supported for forms (e.g.: en, fr).
* `filestore.persist`: Name of the `filestore` declared in the configuration, used for permanent storage of form-related files.
* `filestore.tmp`: Name of the `filestore` for temporary file storage before saving.

---

## Adding to the project

Database persistence is organized in two parts:

* Form templates are stored in a dedicated table (`EASY_FORM`).
* Form responses are saved in business tables, via a column of type `DoEfFormData`.

### VertigoStudio configuration

Add EasyForms definitions to the Studio configuration (e.g. `studio-config.yaml`):

```yaml
resources:
  - { type: kpr, path: classpath:io/vertigo/easyforms/studio/application.kpr}
```

### Creating database tables

If using Liquibase:

```xml
<changeSet author="vertigo" id="init-easyforms">
    <sqlFile encoding="utf8" path="/io/vertigo/easyforms/sql/easyforms_create_init-4.2.0.sql" />
</changeSet>
```

Or manually execute the `easyforms_create_init-4.2.0.sql` file.

### Adding the response column to business tables

In the corresponding KSP file:

```ksp
field response {domain: DoEfFormData label:"Form response" cardinality:"1"}
```

---

## Integration in the application

### Form administration

#### Controller side

* Inject the designer controller:

```java
@Inject
private EasyFormsDesignerController easyFormsDesignerController;
```

* Initialization during `initContext`:

```java
easyFormsDesignerController.initContext();
```

* Save:

  * Retrieve the form via `easyFormsController.readEasyForm(viewContext)`.
  * Save in service (transaction) via `easyFormsDesignerServices.saveForm(easyForm)`.

#### HTML side

* Add the required script:

```html
<script th:src="@{/vertigo-ui/static/easyforms/js/vertigo-easyforms.js}" th:data-context="@{/}"></script>
```

* Add the tag:

```html
<vu:easy-forms-admin />
```

*Tip*: Add a version parameter in the JS URL to invalidate browser cache on updates, e.g.:
`...js?t=__${appBuildTime}__`

---

### Integrating a form in a business page

#### Controller side

* Inject the runner controller:

```java
@Inject
private EasyFormsRunnerController easyFormsRunnerController;
```

* Initialization during `initContext`:

```java
easyFormsRunnerController.initEditContext();
```

* Save: the response is saved as JSON in the business object.

#### HTML side

* Add the required script:

```html
<script th:src="@{/vertigo-ui/static/easyforms/js/vertigo-easyforms.js}" th:data-context="@{/}"></script>
```

* Add the tag:

```html
<vu:easy-forms object="myObject" field="formResponse" template="${model.formModel}" />
```

*Tip*: same recommendation as for administration regarding the version parameter.

---

## Advanced features

### Additional context

It is possible to use business context information in form configuration (default values, display conditions, etc.):

* In the designer's `initContext` (`additionalContext`) to accept these parameters.
* Optionally in the runner's (`additionalContextKeys`) to add them to `VueData`.

---

### Custom field types

To declare new field types:

* Create a class extending `DefinitionProvider<EasyFormsFieldTypeDefinition>`.
* See built-in types in: [FieldTypeDefinitionProvider.java](https://github.com/vertigo-io/vertigo-modules/blob/develop/vertigo-easyforms/src/main/java/io/vertigo/easyforms/runner/pack/provider/FieldTypeDefinitionProvider.java)
* Example: [MarsEasyFormsFieldTypeDefinitionProvider.java](https://github.com/vertigo-io/vertigo-mars/blob/develop/src/main/java/io/mars/support/easyforms/MarsEasyFormsFieldTypeDefinitionProvider.java)

To add a custom UI rendering:

* Create a class extending `DefinitionProvider<EasyFormsUiComponentDefinition>` and implement the rendering in the `<vu:easy-forms>` tag.

Example for a `slider` type:

```html
<vu:easy-forms ...>
    <div th:case="EfUicSlider">
        ...
    </div>
</vu:easy-forms>
```

Labels must be added to the Vertigo i18n engine with the convention `EfFty<TypeName>` or `EfFty<TypeName>$<ParamName>`.

---

### Custom validators

To add specific validators:

* Create a class extending `DefinitionProvider<EasyFormsFieldValidatorTypeDefinition>`.
* See built-in validators here: [FieldValidatorTypeDefinitionProvider.java](https://github.com/vertigo-io/vertigo-modules/blob/develop/vertigo-easyforms/src/main/java/io/vertigo/easyforms/runner/pack/provider/FieldValidatorTypeDefinitionProvider.java)

## For Experts

### Managers & Services

| Manager | Role | Associated components |
|---|---|---|
| `EasyFormsRunnerManager` | Form execution engine | `EasyFormsRunnerServices`, `EasyFormsRunnerController`, `EasyFormsFileUploadController` |
| `EasyFormsDesignerManager` | Form design engine | `EasyFormsDesignerServices`, `EasyFormsDesignerController` |

### Definition Providers (always active via `buildFeatures()`)

| Provider | Description |
|---|---|
| `FieldTypeDefinitionProvider` | Built-in field types: LABEL, EMAIL, DATE, PHONE, TEXT, FILE, CUSTOM_LIST\_*, YES_NO, … |
| `UiComponentDefinitionProvider` | UI components: TEXT_FIELD, TEXT_AREA, SELECT, RADIO, CHECKBOX, FILE, NUMBER, DATE, READ_ONLY, … |
| `FieldValidatorTypeDefinitionProvider` | Validators: EMAIL_NOT_IN_BLACKLIST, GTE_18_ANS, IN_FUTURE, PHONE_FR, … |
| `ModelDefinitionProvider` | Definitions of DtObjects and SmartTypes |

### Extension interfaces (Suppliers)

| Interface | Usage |
|---|---|
| `IEasyFormsFieldTypeDefinitionSupplier` | Adding custom field types |
| `IEasyFormsUiComponentDefinitionSupplier` | Adding custom UI components |

### Constraints (`EasyFormsConstraint`)

| Constraint | Usage |
|---|---|
| `ConstraintPhone` | Phone number validation |
| `ConstraintAgeMinimum` | Minimum age check |
| `ConstraintAgeMaximum` | Maximum age check |
| `ConstraintLocalDateMinimum` | Minimum date check |
| `ConstraintLocalDateMaximum` | Maximum date check |
| `ConstraintEmailBlackList` | Check email not in blacklist |

### Rule engine

| Class | Role |
|---|---|
| `EasyFormsRuleParser` | Parsing of conditional rules |
| `EasyFormsRule` | Rule representation |
| `ValueRule` | Rule based on field value |
| `FormContextDescription` | Context description for rules |

### Adapters

| Adapter | Role |
|---|---|
| `EasyFormsJsonAdapter` | JSON adaptation |
| `EasyFormsMapInputAdapter` | Map → model adaptation |

### Domain Model (DtObjects)

| DtObject | Description |
|---|---|
| `EasyForm` | Form |
| `EasyFormsSectionUi` | Form section |
| `EasyFormsLabelUi` | Label |
| `EasyFormsItemUi` | Item / field |
| `EasyFormsFieldTypeUi` | Field type |
| `EasyFormsFieldValidatorTypeUi` | Validator type |

### Template Model

| Class | Description |
|---|---|
| `EasyFormsTemplate` | Form template |
| `EasyFormsTemplateSection` | Template section |
| `EasyFormsTemplateItemField` | Template field |
| `EasyFormsTemplateItemBlock` | Template block |
| `EasyFormsData` | Form data |

### DAO

| DAO | Role |
|---|---|
| `EasyFormDAO` | Form persistence |

### Features

| Flag | Parameters | Components |
|---|---|---|
| `easyforms` | `filestore.persist`, `filestore.tmp`, `languages` | `EasyFormsRunnerManager` + controllers |

### Configuration YAML

```yaml
io.vertigo.easyforms.EasyFormsFeatures:
    features:
        - easyforms:
            languages: en, fr
            filestore.persist: main
            filestore.tmp: temp
```