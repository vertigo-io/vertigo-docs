# EasyForms Module

## Features

Allows a functional administrator to create and modify dynamic forms, which will then be filled out by the application's users.

The module offers administrators rich functionalities such as:

- Multilingual configuration of input fields
- Adding rich text blocks with a WYSIWYG editor
- Configuring dynamic display rules for fields, allowing conditional visibility based on responses to other fields
- Setting business constraints for each field

This module is also extensible, allowing:

- Adding new field types
- Configuring specific constraints tailored to your business
- Adapting the form creation and management workflow to the project context

EasyForms relies on a flexible JSON-based storage model, ensuring full autonomy with the database.

## Installation

### Adding the Module to `pom.xml`

Add the following dependency in the `pom.xml` file to include the EasyForms module in your project:

```xml
<dependency>
   <groupId>io.vertigo</groupId>
   <artifactId>vertigo-easyforms</artifactId>
   <version>4.3.2</version>
</dependency>
```

### Adding to the Vertigo Configuration

You need to add the `EasyFormsFeatures` feature in the YAML configuration.

```yaml
  io.vertigo.easyforms.EasyFormsFeatures:
    features:
      - easyforms:
          languages: en, fr
          filestore.persist: main
          filestore.tmp: temp
```

#### Parameter Descriptions

- `languages`: Defines the supported languages for the forms (e.g., en, fr).
- `filestore.persist`: Specifies the name of the previously declared `filestore` in the configuration, used for permanently storing files associated with forms.
- `filestore.tmp`: Similar to the previous one, but for temporarily storing files before saving the form.

## Adding to the Project

The module's data persistence in database is divided into two parts:

- Form models are stored in a dedicated table (`EASY_FORM`).
- Form responses are stored in business tables via a column using the `DoEfFormData` domain.

### Configuring VertigoStudio

Add the EasyForms definitions to the Studio configuration (e.g., `studio-config.yaml`):

```yaml
resources:
  - { type: kpr, path: classpath:io/vertigo/easyforms/studio/application.kpr}
```

### Creating Database Tables

If using Liquibase:

```xml
<changeSet author="vertigo" id="init-easyforms">
    <sqlFile encoding="utf8" path="/io/vertigo/easyforms/sql/easyforms_create_init-4.2.0.sql" />
</changeSet>
```

Or manually execute the `easyforms_create_init-4.2.0.sql` file.

### Adding the Response Column to Business Tables

In the corresponding KSP file, add an attribute like this:

```ksp
field response {domain: DoEfFormData label:"Response Form" cardinality:"1"}
```

### Integrating the Administration Page into the Business Application

#### In the Controller

- Inject the designer controller:

```java
@Inject
private EasyFormsDesignerController easyFormsDesignerController;
```

- During `initContext`, initialize the designer with:

```java
easyFormsDesignerController.initContext();
```

- For saving:
    - Retrieve the form using `easyFormsController.readEasyForm(viewContext)`.
    - In the service method (to ensure a transaction), save with `easyFormsDesignerServices.saveForm(easyForm)`.

#### In the HTML Page

- Add the required JS file:

```html
<script th:src="@{/vertigo-ui/static/easyforms/js/vertigo-easyforms.js}" th:data-context="@{/}"></script>
```

- Add the following tag to display the form administration:

```html
<vu:easy-forms-admin />
```

*Note:* It is recommended to add a version-related parameter at the end of the JS URL to invalidate the browser cache on updates, e.g., `...js?t=__${appBuildTime}__`.

### Integrating a Form into a Business Page

#### In the Controller

- Inject the runner controller:

```java
@Inject
private EasyFormsRunnerController easyFormsRunnerController;
```

- During `initContext`, initialize EasyForms with:

```java
easyFormsRunnerController.initEditContext();
```

- On saving, the form response is stored as JSON in the business object.

#### In the HTML Page

- Add the required JS file:

```html
<script th:src="@{/vertigo-ui/static/easyforms/js/vertigo-easyforms.js}" th:data-context="@{/}"></script>
```

- Add the following tag to display the dynamic form:

```html
<vu:easy-forms object="myObject" field="formResponse" template="${model.formModel}" />
```

*Note:* It is recommended to add a version-related parameter at the end of the JS URL to invalidate the browser cache on updates, e.g., `...js?t=__${appBuildTime}__`.


## Advanced Features

### Additional Context

It is possible to use business context information in the form configuration (default values, display conditions, etc.). To do this, declare it:

- In the designer's `initContext` (`additionalContext` parameter) to accept these parameters.
- Optionally in the runner's `initContext` (`additionalContextKeys` parameter) so that these data are added to `VueData`.

### Custom Field Types

To declare additional field types, create a class inheriting from `DefinitionProvider<EasyFormsFieldTypeDefinition>`.

See built-in types in EasyForms: [FieldTypeDefinitionProvider.java](https://github.com/vertigo-io/vertigo-modules/blob/develop/vertigo-easyforms/src/main/java/io/vertigo/easyforms/runner/pack/provider/FieldTypeDefinitionProvider.java)

Example from the Mars project: [MarsEasyFormsFieldTypeDefinitionProvider.java](https://github.com/vertigo-io/vertigo-mars/blob/develop/src/main/java/io/mars/support/easyforms/MarsEasyFormsFieldTypeDefinitionProvider.java)

Additionally, you can declare new UI rendering types by creating a class inheriting from `DefinitionProvider<EasyFormsUiComponentDefinition>` and implementing the desired rendering inside the `<vu:easy-forms>` tag.

Example, if declaring a type named 'slider':

```html
<vu:easy-forms ...>
    <div th:case="EfUicSlider">
        ...
    </div>
</vu:easy-forms>
```

The labels for these new elements must be declared in Vertigo's i18n engine. The naming convention for the i18n key is `EfFty` followed by the field type name. If the field type includes parameters, the key for the parameter label is the field type name, followed by `$` and the parameter name. An example can be found [here](https://github.com/vertigo-io/vertigo-modules/blob/develop/vertigo-easyforms/src/main/resources/io/vertigo/easyforms/runner/pack/EfPackResources_en.properties).

### Custom Validators

Business field types include several validators that can be enabled via the form administration interface. To add custom validators, create a class inheriting from `DefinitionProvider<EasyFormsFieldValidatorTypeDefinition>`.

Built-in validators are available here: [FieldValidatorTypeDefinitionProvider.java](https://github.com/vertigo-io/vertigo-modules/blob/develop/vertigo-easyforms/src/main/java/io/vertigo/easyforms/runner/pack/provider/FieldValidatorTypeDefinitionProvider.java).

