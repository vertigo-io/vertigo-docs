# UI

Extension vertigo-ui enables creation of rich screens, simply and securely.

General principles are explained in [basic/ui](/en/basic/ui):

Here we present more specific elements to help onboard to the Vertigo-ui module.

## Controller: SpringMVC

SpringMVC documentation on [docs.spring.io](https://docs.spring.io/spring/docs/5.2.x/spring-framework-reference/web.html)

SpringMVC's main mechanism maps HTTP requests to Java methods. Two mechanisms coexist:

- Java annotations describing behavior and mapping
- Spring configuration parameters for specific automatic resolvers converting incoming/outgoing data transparently (`ReturnValueHandler` and `ArgumentResolver`)

To streamline vertigo-ui development, SpringMVC's two mechanisms are enhanced by default with specific annotations and resolvers.

Below are the most frequently used annotations:

### SpringMVC Annotations

- `@Controller`: Indicates the Bean is a controller. Must extend `AbstractVSpringMvcController`
- `@RequestMapping`: URL prefix for this Controller. Must follow naming *applicationModule*/*BusinessEntity*; this naming appears everywhere: URLs, Java packages, view directories, model declaration, etc.
- `@Inject`: Standard injection mechanism. Only Services should be injected into controllers (or exceptionally another controller, e.g., when sharing context elements or actions like detail page banners)
- `@GetMapping("myUrl")`: Declares GET URL. Entry point on the controller. By convention, method is named `initContext`, takes [ViewContext](#ViewContext) object and necessary input parameters (bound with @PathVariable or @RequestParam, etc.)
- `@PostMapping("/_myAction")`: Declares POST URL. Action point on the controller. By convention, URL is prefixed by `_` and method by `do`. Method takes expected data annotated with `@ViewAttribute("paramName")`.
- `@DeleteMapping("_myAction")`: Declares DELETE URL.
- `@PathVariable("paramName")`: Maps a variable to a URL segment. Ex: `https://localhost:8080/base/12/mainPicture`, controller method annotated: `@GetMapping("{baseId}/mainPicture")`, method parameter annotated: `@PathVariable("baseId") final Long baseId`
- `@RequestParam("paramName")`: Maps a variable to a request parameter. Ex: `https://localhost:8080/base/myUrl?baseId=12`, controller method annotated: `@GetMapping("myUrl")`, method parameter annotated: `@RequestParam("baseId") final Long baseId`. Rarely used, as a *REST-like* approach is preferred with identifiers in the URL path, or complete objects are passed (mapped by @ViewAttribute).

### Vertigo-ui Annotations

- `@ViewAttribute("paramName")`: Maps an object-type variable with form data on POST. Name must match a context key (see [ViewContextKey](#ViewContextKey)). Object is retrieved from context, updated by POST data, validated, then passed to the method.
- `@QueryParam("paramName")`: Used in some cases to indicate request parameter name. Typically for file operations (`VFile` and `FileInfoURI`)
- `@Secured("authname")`: Used on controllers or controller methods to verify the user has these authorizations. (Uses vertigo-account authorization configuration)

### Vertigo-ui ArgumentResolver

- `ViewContext`: Object representing page context. Empty on GET, populated, retrieved, and updated on POST for action execution.
- `DtListState`: Object representing page display state: sort and pagination.
- `UiMessageStack`: Object containing the action message stack: format and surface errors (constraint and null checks); can be passed to service and completed with global, per-object, or per-field error, warning, info, or success messages
- `FileInfoURI`: Receives a file URI. Requires parameter naming with `@QueryParam`. File URIs are protected on the page (transformed); on server return, inverse translation is applied.
- `VFile`: Receives a file. Requires parameter naming with `@QueryParam`. File is temporary and must be persisted if needed in a service.
- `Optional<OtherType>`: Supports optional parameters.

### Vertigo-ui ReturnValueHandler

- `void`: When a POST-or-other-mapped controller method returns nothing (`void`), the page refreshes incorporating context modifications from the controller method.
- `ViewContext`: Returns a specific updated viewContext. Used for Ajax calls, which should receive only JSON data, not HTML pages.
- `FileInfoURI`: Sends a file URI. URI is protected (transformed), not sent in plaintext.
- `VFile`: Sends a file.

### Other Vertigo-ui Specifics

- `ViewContextKey<OtherType>`: Declares a typed entry in page context.
- `UiUtil`: Utility passed to templating engine as `uiUtil`; provides functions useful for Vertigo-ui components and page rendering. Generally, pages don't need it, but components do.
- `UiAuthorizationUtil`: Utility passed to templating engine as `authz`; provides functions to simplify security checks during display. 3 usage modes:
  - 1- Simple string:
    `vu:authz="myGlobalAuthz"` or `vu:authz="mySecuredEntityAuthz$read"`
    => equivalent to `authz.hasAuthorization('myGlobalAuthz')`
    Supports multiple lists with `,` for OR and `!` for NOT
  - 2- Path to a `UiObject<Entity>` from context:
    `vu:authz="model.myEntity$read"` or `vu:authz="model.list[0]$read"`
    => equivalent to `authz.hasOperation(model.myEntity, 'read')`
    (first part evaluated as `${model.myEntity}`)
  - 3- Evaluated expression (starts with `${`):
    `vu:authz="${authz.hasAuthorization('myGlobalAuthz') && authz.hasAuthorization('mySecuredEntityAuthz$read')}"`
    => exactly equivalent to `th:if`. But keep `th:if` for business logic and `vu:authz` for security logic

**ViewContext** API
- `publishRef`: Adds a simple serializable object to context
- `publishDto`: Adds a form object (DtObject) to context
- `checkDtoErrors`: Checks object errors. Added to uiMessageStack if needed
- `readDto`: Returns validated business object. Throws exception on error.
- `publishDtList`: Adds a list (DtList) to context
- `readDtList`: Returns validated business object. Throws exception on error.
- `publishDtListModifiable`: Adds a modifiable list (DtList) to context
- `checkDtListErrors`: Checks list errors. Added to uiMessageStack if needed
- `readDtListModifiable`: Returns validated business object list. Throws exception on error.
- `publishMdl`: Adds a reference list (MDL: Master Data List) to context, specifying entity and list code.
- `publishFacetedQueryResult`: Adds faceted search result to context.
- `getUiObject`: Retrieves from context the object from UI as received on server. Reserved for specific cases: non-blocking checks, etc.
- `getUiList`: Retrieves from context the list from UI as received on server. Reserved for specific cases.
- `getUiListModifiable`: Retrieves modifiable list from UI context
- `getString`: Retrieves a string from context
- `getLong`: Retrieves a Long from context
- `getInteger`: Retrieves an Integer from context
- `getBoolean`: Retrieves a Boolean from context
- `getSelectedFacetValues`: Retrieves selected facet list from faceted search UI.

## UI: How to read?

As presented, the UI is composed of several building blocks: VueJS, Quasar, Thymeleaf, and Vertigo-ui.
Before detailing each block, here are elements for orientation.

- Page renders in two places: server-side by Thymeleaf and Vertigo-ui components, client-side by VueJS and Quasar.
- Prefix `th:` tells Thymeleaf to interpret the component or attribute
- Prefix `:` tells VueJS to interpret the component or attribute
- Prefix `th::` is composition of `th:` and `:`; Thymeleaf interprets and leaves `:` for VueJS
- Prefix `layout:` is a Thymeleaf extension providing templating like *Tiles*.
- Attributes starting with `v-` are VueJS directives
- Tags starting with `<q-` are Quasar components.
- Tags starting with `<vu:` are Vertigo-ui components.

## Rendering Engine: VueJS

VueJS documentation on [vuejs.org](https://vuejs.org/v2/guide/)

VueJS offers a WebComponent approach with a reactive UI mapped to a view model, following the Observer/Observable pattern.

- **inline** `{{abc}}`: *Mustache* usage directly adds value of `abc` to the DOM. Value is *reactive* and HTML-encoded
- **prefix** `:`: Indicates VueJS should interpret the following attribute. Enables VueJS on standard HTML attributes or webComponent (like Quasar's src, value, or icon)
- `v-if="..."`: Display condition on a DOM node. Condition can be a vueData variable or expression to evaluate. Element disappears from DOM but remains client-side; not suitable for security
- `v-for="item in items"`: Element with `v-for` is duplicated per element. Loop variable can be used to change each iteration's rendering
- `v-model`: Indicates vueData data bound to the component
- `@click`: Specifies action on component's `click` event. Variant `@click.native` maps directly to HTML component's onClick
- `v-cloak`: Tells Vue this DOM part should be hidden until interpreted. Prevents "flickering" during page display

## Component Library: Quasar

Quasar documentation on [quasar.dev](https://quasar.dev/vue-components/)

!> Vertigo-ui 2.1.0 uses Quasar version 1.4.1.

Most common components:
- `q-page`
- `q-layout`
- `q-toolbar`
- `q-btn`
- `q-item`
- `q-popover`
- `q-page-sticky`
- `q-icon`

## Templating Engine: Thymeleaf

Requires:
```HTML
<html xmlns:th="http://www.thymeleaf.org">
```
Thymeleaf documentation on [thymeleaf.org](https://www.thymeleaf.org/doc/tutorials/3.0/usingthymeleaf.html)

- **inline** `__${...}__`: Preprocessor. Tells Thymeleaf to pre-process this portion. Used for expressions inside larger expressions.
- **inline** `|...|`: Literal substitution. Writes a string containing parts to evaluate, simplifying writing and avoiding string concatenation.
- **inline html** `[[...]]`: Literal substitution. Writes dynamic text in HTML directly (`[(...)]` for `th:utext` equivalent). Requires `th:inline` on a parent tag.
- **prefix** `th:`: Tells Thymeleaf to interpret the following attribute. Enables Thymeleaf on standard HTML attributes. On tags, corresponds to Thymeleaf-specific tag namespace.
- `abc?:bcd`: Often used to simplify writing; equivalent of `abc != null ? abc : bcd`
- `${...}`: Evaluates a variable expression. Ex: `${name}` or `${user.name}`
- `@{...}`: Rebuilds a link URL.
- `#{...}`: References an i18n resource.
- `~{abc::bcd}`: Selects a fragment. Syntax is `~{ path/to/the/template.html :: fragmentSelector}`. Selector is either a fragment name or a standard JavaScript selector (`#id`, `.class`, ...)
- `th:if`: Display condition on a tag (and body). Filter is server-side and suitable for security.
- `th:with="var1=${...}, var2=${...}"`: Declares local variables. Scope is tag content, even outside the file: when including other fragments, the variable remains accessible.
- `th:attr="var1=${...}, var2=${...}"`: Declares global variables. Use with caution.
- `th:text`: Evaluates attribute content and adds to tag body.
- `th:each="abc : bcd"`: Creates a loop on the tag. Loops over `bcd`, current element in variable `abc`.
- `th:include="abc::bcd"`: Thymeleaf templating component. Template tag body is copied into the tag with the attribute; template tag is lost. Same syntax as fragment selector `~{abc::bcd}`.
- `th:replace="abc::bcd"`: Thymeleaf templating component. Tag with attribute is replaced by the template tag. Same syntax as fragment selector `~{abc::bcd}`.
- `th:remove="*mode*"`: Removes tags from DOM, depending on mode. Most common modes:
  - `all` removes tag and children
  - `tag` removes tag and keeps children
- `th:fragment="fragName"`: Thymeleaf templating component. Used to name a reusable template.

## Layout Engine: Thymeleaf Layout

Thymeleaf Layout documentation on [github](https://ultraq.github.io/thymeleaf-layout-dialect/)

Requires:
```HTML
<html xmlns:layout="http://www.ultraq.net.nz/thymeleaf/layout">
```

- `<head>`: `<head>` attributes are automatically merged between page and layout. Some are overridden (like `<title>`), others concatenated (like `<script>`).
- `layout:decorate`: Added on content's `<html>` tag to specify which layout the content uses (it *decorates*).
- `layout:fragment`: Added on internal content tags to indicate which layout fragment receives this specific content.

> Layouts can inherit from other layouts.

Layouts share all recurring page parts: banner, menu, footer, ...
Principle: a layout is a *hole*paged page; holes are named in the template and can have default values. When writing a page, indicate *decorating* a particular layout and only specify hole *values*. Goal: page elements are specific; all common content is in the layout.
The Mars demo app proposes [layouts](https://github.com/vertigo-io/vertigo-mars/tree/develop/src/main/webapp/WEB-INF/views/templates) that can be adapted and reused.

## Vertigo-ui Named Components

Vertigo-ui components use Thymeleaf templating; each component is a `th:replace` with additional intelligence.
Principle (and code) is adapted from [thymeleaf-component-dialect](https://github.com/Serbroda/thymeleaf-component-dialect)

Vertigo-ui components are Thymeleaf fragments evaluated server-side; several encapsulate VueJS or Quasar components.
Vertigo-ui is not meant to encapsulate all UI components. Strategy for vertigo-ui components considers:

- Component is a high-level component representing a logical component. Beneath it will be several UI components, enhanced behavior, ergonomics adapted to our context.
- Component requires special context interactions. E.g., selecting data for vueData integration, sometimes encoding it specifically.
- Component offers a more user-friendly, less verbose API for the developer

Requires:
```HTML
<html xmlns:vu="http://www.morphbit.com/thymeleaf/component">
```

### Component Parameters
- `abc_slot`: Retrieves a `vu:slot` from the calling tag body and places it in the component (Ex: `vu:table`)
- `abc_attrs`: Aggregation of all parameters prefixed with `abc_` passed when calling the component. Ex: on `vu:table`, attribute `tr_class` can be passed; parameter `class` (with value) is retrieved by component parameter `tr_attrs` to place on internal `tr` tag. *Avoids anticipating all cases during component design.*
- `other_attrs`: Aggregation of all parameters not identified as component parameters, determining placement. (Ex: in `vu:text-field`, attributes not identified as parameters are placed on internal `q-input`; `<vu:text-field round` gives `<q-input round`)
- `contentTags`: Special parameter retrieving tags in component body on call, as a list of `contentItem`. Rare; usually `<vu:content>` is used instead, which places all body. `contentItem` tests tags for specific processing (Ex: `grid` places tags in blocks and `vu:grid-cell` has special behavior)

### Vertigo-UI Components: layout
- `vu:page`: Mandatory component framing the VueJS active zone.
  - `content`: Tag body is preserved
  - `vuiDevMode`: Activates developer mode for VertigoUi components (requires nodeJs server pushing built js `npm serve`..)
  - `vuiSsr`: Activates Server Side Rendering mode (requires nodeJs server rendering pages)
- `vu:head`: Sets head tag and HTML head meta
  - `title`*: Page title
  - `content`: Tag body is preserved
- `vu:head-meta`: Mandatory component setting head **meta** elements (js script, css, ...)
  - `vuejsDevMode`: Sets VueJs to dev mode *(we noted bugs with VueJs in some cases only in devMode)*
- `vu:form`: Sets a form and references its associated page context
  - `content`: Tag body is preserved
  - `other_attrs`: Attributes to add on the form (`<form>` tag)
- `vu:block`: Block component (graphically visible), represented as a card
  - `title`: Block title
  - `subtitle`: Block subtitle
  - `icon`: Block icon
  - `withFab` **boolean**: Adds class `withFab` if needed
  - `actions_slot`: Slot for positioning block actions *(replaces icon)*
  - `header_attrs`: Attributes for block header (`<div>` tag)
  - `content_attrs`: Attributes for block body (`<div class="q-card-main">`)
  - `card_attrs`: Attributes for block parent (`<div class="q-card">`)
  - `content`: Tag body is preserved
- `vu:grid`: Declares a grid layout
  - `cols`: Column count. Default: 2
  - `dense`: Applies *dense* mode reducing gutter size
  - `contentTags`: Tag content is preserved. Each element is placed in a `<div>` with expected width. (single column forced under breakpoint **xs**)
- `vu:grid-cell`: Declares a specific **grid** cell
  - `col`: Cell column count
  - `class`: Cell CSS class
  - `div_attrs`: Attributes for cell body (`<div>` tag)
  - `content`: Tag body is preserved
- `vu:messages`: Component adding global message list from processing added to context (**uiMessageStack** with Errors, Warnings, Info, Success)
- `vu:modal`: Sets modal container, usable later in the screen.
  - `componentId`: Component name, used to target in JS
  - `title`: Modal title
  - `closeLabel`: Modal close label
  - `srcUrl`: Modal URL (optional, usually set by open script)
  - `iframe_attrs`: Attributes for iframe
  - `modal_attrs`: Attributes for modal (`<q-modal>` tag)

Modal usage example on Mars [ticketDetail.html](https://github.com/vertigo-io/vertigo-mars/blob/develop/src/main/webapp/WEB-INF/views/maintenance/ticket/ticketDetail.html):
```HTML
  <q-btn round icon="edit" label="View detail" th:@click="|openModal('workOrderEditModal', '@{/maintenance/workorder/}' + props.row.woId , {'successCallback' : 'onWorkOrderSuccess' })|"></q-btn>
  <vu:modal componentId="workOrderEditModal" title="Work Order" iframe_width="800" iframe_height="400" />
  <script type="text/javascript">
    function onWorkOrderSuccess() {
      componentStates.workOrderEditModal.opened = false;
      VUi.methods.httpPostAjax("[[@{/maintenance/ticket/_reloadWorkOrders}]]", {});
    }
  </script>
```

- `vu:content`: Tag used in components to mark `content` insertion (tag body). Body can be used to define default rendering.
- `vu:content-item`: Tag used in components to mark `contentItem` insertion. Used when components in another component's body must be interpreted separately. Example: `grid` component. Parent must have contentTags attribute, loop with item name `contentItem`. (cf. [grid](https://raw.githubusercontent.com/vertigo-io/vertigo-libs/master/vertigo-ui/src/main/resources/io/vertigo/ui/components/quasar/layout/grid.html))
- `vu:slot` *tag*: Component passing slot content to parent component. Parent slots are referenced by `_slot` suffix.
  - `name`: Slot name
  - `content`: Body is passed to parent and inserted with `vu:slot` attribute or `<vu:content-slot />` tag
- `vu:slot` *attribute*: Attribute used in components to mark slot insertion. Tag is preserved. Equivalent of `th:include="${my_slot}"`.
  - `value`: Slot name (Ex: `vu:slot="top_left_slot"`)
- `vu:content-slot`: Tag used in components to mark `slot` insertion. Replaced by the slot. Body can define default rendering.
  - `name`: Slot name

### Vertigo-UI Components: utils

Technical components.
`include-data-*` components all have same role: tell server to transfer data from server context (`CTX`) to Vue context (`vueData` object).
Strategy ensures only useful data is pushed client-side. Usually not used directly, set by `inputs` components needing them.
Useful for precisely adding data to `vueData`, e.g., specific vue components.

- `vu:include-data`: Includes an object field
  - `object`: Context object name
  - `field`: Field name
  - `modifiable`: Field is editable client-side and can be sent to server
  - `modifiableAllLines`: All lines are modifiable
- `vu:include-data-primitive`: Includes a primitive context data
  - `key`: Data key
  - `modifiable`: Field is editable client-side and can be sent to server
- `vu:include-data-map`: Includes an object field and applies denormalization on its value (translates id to label, etc.)
  - `object`: Context object name
  - `field`: Field name
  - `list`: Mapping list
  - `listKey`: Mapping list key field
  - `listDisplay`: Mapping list label field
- `vu:include-data-protected`: Includes an object field. Client-side value is protected (not plaintext, not modifiable); real value stays server-side. Used for file identifiers, etc.
  - `object`: Context object name
  - `field`: Field name

### Vertigo-UI Components: inputs

Main components for building application forms.
Simplify screen writing; most handle `viewMode` for **Edit** or **ReadOnly** rendering.
**Edit** components natively handle validation error messages.

- `vu:label`: Label component
  - `object`*: Context object name
  - `field`*: Field name
  - `label`: Label override
  - `other_attrs`: Attributes for label (`<q-field>` tag)
- `vu:text-field`: Text field component
  - `object`*: Context object name
  - `field`*: Field name
  - `label`: Label override
  - `suffix`: Suffix override
  - `label_attrs`: Attributes for label (`<q-field>`)
  - `input_attrs`: Attributes for input (`<q-input>`)
- `vu:text-area`: Text area component
  - `object`*: Context object name
  - `field`*: Field name
  - `label`: Label override
  - `label_attrs`: Attributes for label (`<q-field>`)
  - `input_attrs`: Attributes for input (`<q-input>`)
- `vu:autocomplete`: Autocomplete: choice from list by label, sets field value
  - `object`*: Context object name
  - `field`*: Field name
  - `label`: Label override
  - `list`*: Context list name
  - `valueField`: List field used as value, assigned to object
  - `labelField`: List field used as label
  - `componentId`: vueJs component id
  - `label_attrs`: Attributes for label (`<q-field>`)
  - `input_attrs`: Attributes for input (`<q-select>`)
- `vu:checkbox`: Checkbox component
  - `object`*: Context object name
  - `field`*: Field name
  - `label`: Label override
  - `label_attrs`: Attributes for label (`<q-field>`)
  - `input_attrs`: Attributes for input (`<q-checkbox>`)
- `vu:select`: Combobox selection
  - `object`*: Context object name
  - `field`*: Field name
  - `label`: Label override
  - `list`*: Context list name
  - `valueField`: List field as value
  - `labelField`: List field as label
  - `label_attrs`: Attributes for label (`<q-field>`)
  - `input_attrs`: Attributes for input (`<q-select>`)
- `vu:select-multiple`: Multiple combobox selection
  - Same parameters as `vu:select`
- `vu:radio`: Radio button list selection
  - `object`*: Context object name
  - `field`*: Field name
  - `label`: Label override
  - `list`*: Context list name
  - `valueField`: List field as value
  - `labelField`: List field as label
  - `layout`: Radio layout: `horizontal` or `vertical`
  - `label_attrs`: Attributes for label (`<q-field>`)
  - `input_attrs`: Attributes for input (`<q-select>`)
- `vu:date`: Date selection
  - `object`*: Context object name
  - `field`*: Field name
  - `label`: Label override
  - `format`: Date value format (default `DD/MM/YYYY`)
  - `date_attrs`: Attributes for date (`<q-date>`)
  - `input_attrs`: Attributes for input (`<q-input>`)
- `vu:datetime`: Date/time selection
  - `object`*: Context object name
  - `field`*: Field name
  - `label`: Label override
  - `format`: Date value format (default `DD/MM/YYYY HH:mm`)
  - `date_attrs`: Attributes for date (`<q-date>`)
  - `time_attrs`: Attributes for time (`<q-time>`)
  - `input_attrs`: Attributes for input (`<q-input>`)
- `vu:knob`: Numeric value modification widget
  - `object`*: Context object name
  - `field`*: Field name
  - `label`: Label override
  - `min`: Minimum value
  - `max`: Maximum value
  - `step`: Value step
  - `label_attrs`: Attributes for label (`<q-field>`)
  - `input_attrs`: Attributes for input (`<q-knob>`)
- `vu:slider`: Numeric value slider
  - `object`*: Context object name
  - `field`*: Field name
  - `label`: Label override
  - `min`: Minimum value
  - `max`: Maximum value
  - `step`: Value step
  - `label_attrs`: Attributes for label (`<q-field>`)
  - `input_attrs`: Attributes for input (`<q-slider>`)
- `vu:chips-autocomplete`: Tag list autocomplete
  - `object`*: Context object name
  - `field`*: Field name
  - `label`: Label override
  - `list`*: Context list name
  - `valueField`: List field as value
  - `labelField`: List field as label
  - `componentId`: vueJs component id
  - `staticData`: Static data (or from WebService `@{/autocomplete/_searchFullText}`)
  - `label_attrs`: Attributes for label (`<q-field>`)
  - `input_attrs`: Attributes for input (`<q-select>`)
- `vu:fileupload`: File upload (unlike other input components, file id is not stored in a business object)
  - `url`*: Upload WebService URL
  - `key`*: Context key receiving files
  - `multiple`: Allows multiple files
  - `uploader_attrs`: Attributes for input (`<q-uploader>`)

> To adapt rendering, components use specific mechanisms. Generally, a **Vertigo-UI: inputs** component is written as:
```XML
<th:block th:fragment="label-edit(object,field, label, other_attrs)" vu:alias="label" vu:selector="${viewMode=='edit'}" >
  <vu:content/>
</th:block>
<th:block th:fragment="label-read(object, field, label, other_attrs)" vu:alias="label" vu:selector="${viewMode=='read'}" >
  <vu:content/>
</th:block>
```
> - `th:fragment` names the specific component and parameters.
> - `vu:alias` sets the component alias, often the name used in pages
> - `vu:selector` is an expression evaluated in component context, selecting the fragment to use with the alias

### Vertigo-UI Components: collections
- `vu:cards`: Generates a card list. During card render, use VueJS attribute `item` for current object.
- `vu:field-read`
- `vu:list`
- `vu:search`
- `vu:facets`

### Vertigo-UI Components: tables
- `vu:table`: Generates a table. During row render, use VueJS attribute `props.row` for current object.
  - list, componentId, selectable, rowKey, rowsPerPage, sortUrl, navOnRow, color, tableClass, autoColClass, top_right_slot, top_left_slot, actions_slot, tr_attrs, other_attrs
- `vu:column`
  - list, field, name, label, align, sortable, class, td_attrs

### Vertigo-UI Components: buttons
- `vu:button-link`: Link-type button (`<q-btn type="a"`)
  - label, icon, url, ariaLabel, disabled (**boolean**), other_attrs (on `<q-btn`)
- `vu:button-link-confirm`: Link button with confirmation popin
  - actions_slot, label, icon, url, ariaLabel, disabled, confirmMessage, labelOk (default Yes), labelCancel (default No), other_attrs
- `vu:button-submit`: Submit button (`<q-btn type="submit"`)
  - label, icon, action, ariaLabel, other_attrs
- `vu:button-submit-confirm`: Submit button with confirmation popin
  - actions_slot, label, icon, action*, ariaLabel, formId*, confirmMessage, labelOk (Yes), labelCancel (No), other_attrs

## Vertigo-ui VueJS Components

- `vueData`
- `v-notifications`
- `v-comments`
- `v-scroll-spy`
- `v-json-editor`
- `v-chatbot`

## For Experts

### Managers & Configuration

Module vertigo-ui has no dedicated `XxxFeatures.java`. UI components are auto-injected via `DefaultUiModuleFeatures.addUi()` adding `VSpringMvcConfigDefinitionProvider` with parameters `name`, `packages`, `componentDirs`.

### ViewContext

`ViewContext` is the central UI layer object, representing page context. Publishes and reads objects, lists, and primitives between controller and view.

| Method | Description |
|---|---|
| `publishDto` | Publishes form object (DtObject) to context |
| `readDto` | Reads and validates form object (throws `ExpiredViewContextException` on error) |
| `publishDtList` | Publishes list (DtList) to context |
| `publishDtListModifiable` | Publishes modifiable list |
| `publishMdl` | Publishes reference list (Master Data List) |
| `publishFacetedQueryResult` | Publishes faceted search result |
| `getUiObject` / `getUiList` | Retrieves data as received from UI |
| `ViewContextMap` | Typed map for context element access via `ViewContextKey` |
| `ViewContextUpdateSecurity` | Controls context update security |

### Spring MVC

| Component | Description |
|---|---|
| `VSpringWebConfig` | Base Spring MVC configuration |
| `VSpringMvcConfigDefinition` | MVC configuration definition |
| `AbstractVSpringMvcController` | Parent controller to extend |
| `VSpringMvcControllerAdvice` | Global exception handling and shared data |
| `VSpringMvcExceptionHandler` | Centralized exception handler |
| `VSpringMvcUiMessageStack` | UI message stack for error rendering |
| `VRequestToViewNameTranslator` | Request-to-view-name translation |
| `VertigoLocaleResolver` | User-based locale resolution |

#### Argument Resolvers

| Resolver | Supported Type |
|---|---|
| `ViewContextReturnValueAndArgumentResolver` | `ViewContext` (read and return) |
| `ViewAttributeMethodArgumentResolver` | Objects annotated `@ViewAttribute` |
| `UiMessageStackMethodArgumentResolver` | `UiMessageStack` |
| `UserSessionMethodArgumentResolver` | User session |
| `DtListStateMethodArgumentResolver` | `DtListState` (sort, pagination) |
| `VFileMethodArgumentResolver` | `VFile` (with `@QueryParam`) |
| `FileInfoURIConverter` | `FileInfoURI` (protected URI conversion) |
| `VegaJsonHttpMessageConverter` | Vega JSON conversion |

#### Return Value Handlers

| Handler | Return Type |
|---|---|
| `VFileReturnValueHandler` | `VFile` |
| `UiFileInfoReturnValueHandler` | `UiFileInfo` |
| `FileInfoURIConverterValueHandler` | `FileInfoURI` |

#### Interceptors

| Interceptor | Priority | Description |
|---|---|---|
| `VSpringMvcAuthorizationInterceptor` | — | `@Secured` verification on controllers |
| `VSpringMvcViewContextInterceptor` | — | ViewContext initialization |
| `VSpringMvcErrorInterceptor` | — | Error interception and rendering |
| `RateLimitingHandlerInterceptor` | — | Rate limiting on MVC requests |
| `VAnnotationHandlerInterceptorImpl` | — | `@VControllerInterceptor`-based interception |
| `VControllerInterceptorEngine` | — | Interceptor execution engine |

### Thymeleaf

| Component | Description |
|---|---|
| `VUiStandardDialect` | Custom Thymeleaf dialect (`vu:`) |
| `VuiResourceTemplateResolver` | Template resolution from classpath/webapp |
| `VSpringTemplateEngine` | Configured Spring-thymeleaf template engine |

#### `vu:` Components (Thymeleaf dialect)

| Component | Class |
|---|---|
| `vu:named` | `NamedComponentDefinition`, `NamedComponentParser`, `NamedComponentElementProcessor` |
| `vu:content` | `ContentComponentProcessor` |
| `vu:content-item` | `ContentItemComponentProcessor` |
| `vu:content-slot` | `ContentSlotComponentProcessor` |
| `vu:slot` | `SlotComponentProcessor`, `SlotAttributeTagProcessor` |
| `vu:authz` | `AuthzAttributeTagProcessor` |
| `vu:once` | `OnceAttributeTagProcessor` |
| `vu:text` | `VuiTextTagProcessor` |
| Utilities | `FragmentUtil`, `ResourcePathFinder` |

### UI Data Wrappers

| Class | Description |
|---|---|
| `UiListUnmodifiable` | Read-only list |
| `BasicUiListModifiable` | Client-side modifiable list |
| `UiMdList` | Master Data list (reference) |
| `MapUiObject` | Map-form UI object |
| `UiFileInfo` / `UiFileInfoList` | Secure file information |
| `ClusterUiList` | Display cluster list |
| `UiSelectedFacetValues` | Selected facets in a search |
| `ComponentRef` / `ComponentStates` | Vue component reference and state |
| `FormMode` | Form mode (edit/read) |
| `AjaxResponseBuilder` | AJAX response builder |
| `ProtectedValueUtil` / `FileInfoURIAdapter` | Protected value encoding |

### Quasar Tree

| Class | Description |
|---|---|
| `Tree` | Tree representation |
| `TreeNode` / `TreeNodeData` | Tree node |
| `TreeBuilder` | Fluent tree builder |
| `LevelContext` / `ListContext` | Per-level rendering context |

### Jetty Boot

| Class | Description |
|---|---|
| `JettyBoot` | Embedded Jetty server startup |
| `JettyBootParams` | Jetty configuration parameters |
| `JettyBootParamsBuilder` | Parameter builder |
| `KVSessionDataStoreFactory` | Jetty session store factory |
| `KVSessionDataStore` | Jetty session storage via KVStore |

### Vue.js SSR

| Class | Description |
|---|---|
| `VuejsSsrFilter` | Servlet Filter for Vue.js Server-Side Rendering |
| `VuejsSsrServletResponseWrapper` | SSR HTTP response wrapper |
| `VuejsSsrResponseStream` | SSR output stream |
| `UnAutoCloseTagsFilter` | Double-opened tags filter |

### Exceptions

| Exception | Description |
|---|---|
| `ExpiredViewContextException` | Thrown when ViewContext has expired |

### YAML Configuration

```yaml
io.vertigo.ui.DefaultUiModuleFeatures:
    buildFeatures:
        - addUi:
            name: "my-ui"
            packages: "io.myapp.controllers"
            componentDirs: "/io/vertigo/ui/components"
```