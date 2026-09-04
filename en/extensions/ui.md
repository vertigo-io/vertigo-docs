# UI

The vertigo-ui extension allows the creation of rich screens, in a simple and secure way.

General principles are explained in [basic/ui](/en/basic/ui).

We present here the more specific elements that help you get started with the vertigo-ui module.

## Controller: SpringMVC

SpringMVC documentation on [docs.spring.io](https://docs.spring.io/spring-framework/reference/web/webmvc.html)

The main behavior of SpringMVC is to allow HTTP requests to be mapped simply to Java methods.
For this, two mechanisms coexist:

- by Java annotations to describe the behavior and the mapping set up
- by configuration in the Spring configuration of specific automatic resolvers performing the conversion of incoming or outgoing data transparently (`ReturnValueHandler` and `ArgumentResolver`)

To streamline the developments, Vertigo-UI uses and complements these two default SpringMVC mechanisms with specific annotations and specific resolvers.

Below are the annotations that are used most often:

### SpringMVC Annotations

- `@Controller`: Indicates that the Bean is a controller. Must inherit from `AbstractVSpringMvcController`
- `@RequestMapping`: URL prefix of this Controller. Must respect the naming *applicativeModule*/*BusinessEntity*, this naming is found everywhere: Url, java packages, view directories, model declaration, etc...
- `@Inject`: Standard injection mechanism. Only Services should be injected in controllers (or exceptionally another controller, when there are elements of the context, or actions, in common, for example for the banners of detail pages)
- `@GetMapping("myUrl")`: Declares the url in GET. It represents the entry point on the controller. By convention the method is named `initContext`, takes the [ViewContext](#viewcontext) object and the necessary input parameters (bound with @PathVariable or @RequestParam for example)
- `@PostMapping("/_myAction")`: Declares the url in POST. It represents the action point on the controller. By convention the url is prefixed by `_` and the method by `do`. The method takes the expected data annotated with `@ViewAttribute("paramName")`.
- `@DeleteMapping("_myAction")`: Declares the url in DELETE.
- `@PathVariable("paramName")`: Maps a variable with a portion of the url of the service. Ex: `https://localhost:8080/base/12/mainPicture`, controller method annotated: `@GetMapping("{baseId}/mainPicture")`, the method parameter is annotated: `@PathVariable("baseId") final Long baseId`
- `@RequestParam("paramName")`: Maps a variable with a request parameter. Ex: `https://localhost:8080/base/myUrl?baseId=12`, controller method annotated: `@GetMapping("myUrl")`, the method parameter is annotated: `@RequestParam("baseId") final Long baseId`. This case is rarely used in the end, as a *REST-like* approach is preferred where the identifiers are in the path of the url, or complete objects are passed (mapped by @ViewAttribute).

### Vertigo-UI Annotations

- `@ViewAttribute("paramName")`: Maps an object-type variable with the form data during a POST. The name must match a key of the context (see `ViewContextKey`). The object is retrieved from the context, updated by the POST data, validated then passed to the method.
- `@QueryParam("paramName")`: Used in a few cases to indicate the name of the request parameter. Typically for the operations on files (`VFile` and `FileInfoURI`)
- `@Secured("authname")`: Used on the controllers or the controller methods to check that the user has these authorizations. (Uses the vertigo-account authorization configuration)

### Vertigo-UI ArgumentResolver

- `ViewContext`: Object representing the context of the page. Blank on a GET, it is meant to be populated, retrieved and updated on a POST. It is used to perform the action.
- `DtListState`: Object representing the display state of a page: sort and pagination.
- `UiMessageStack`: Object containing the stack of messages of the action: formatting and display errors (constraint and non-null validation), it can be passed to the service and filled with global, per object or per field error, warning, info or success messages
- `FileInfoURI`: Allows receiving a file uri. Requires naming the parameter with `@QueryParam`. File URIs are protected in the page (transformed), on the return to the server we do the inverse translation.
- `VFile`: Allows receiving a file. Requires naming the parameter with `@QueryParam`. The file is temporary and must be persisted if needed in a service.
- `Optional<OtherType>`: Allows supporting optional parameters.

### Vertigo-UI ReturnValueHandler

- `void`: When a controller method mapped in POST or other returns nothing (`void`), the page is refreshed taking into account the context modifications performed in the controller method. *(this is of course not really a ReturnValueHandler)*
- `ViewContext`: Specifically returns an updated viewContext. This is used in the case of Ajax calls, which should receive in return only Json data and not the HTML page.
- `FileInfoURI`: Allows sending a file uri. The uri is protected (transformed) and is not sent in the clear (plaintext).
- `VFile`: Allows sending a file.

### Other Vertigo-UI specifics

- `ViewContextKey<OtherType>`: Declares a typed entry in the context of the page.
- `UiUtil`: utility exposed to the context of the page, accessible in the templates via `model.util` (`util` key of the ViewContext). It offers functions that are useful for the Vertigo-UI components and the rendering of the pages. In general, the pages rarely need it; the components do.
- `UiAuthorizationUtil`: Utility made available to the templating engine as `authz`; it offers functions to simplify the security checks when displaying. 3 usage modes:
     - 1- With a simple string:
        `vu:authz="myGlobalAuthz"` or `vu:authz="mySecuredEntityAuthz$read"`
         => equivalent to `authz.hasAuthorization('myGlobalAuthz')`
         `hasAuthorization` automatically applies the `Atz` prefix to the names passed: we write `myGlobalAuthz` and not `AtzMyGlobalAuthz`.
         Supports multiple lists with `,` for OR and `!` for NOT
     - 2- With a path to a `UiObject<Entity>` of the context:
        `vu:authz="model.myEntity$read"` or `vu:authz="model.list[0]$read"`
        => equivalent to `authz.hasOperation(model.myEntity, 'read')`
        (the first part is evaluated as `${model.myEntity}`)
      - 3- With an evaluated expression (starts with `${`)
        `vu:authz="${authz.hasAuthorization('myGlobalAuthz') && authz.hasAuthorization('mySecuredEntityAuthz$read')}"`
        => exactly equivalent to `th:if`. But keep `th:if` for business logic and `vu:authz` for security logic

**ViewContext** API
- `publishRef`: Adds to the context a simple serializable object
- `publishDto`: Adds to the context a form object (DtObject)
- `checkDtoErrors`: Checks the errors of the object. These are added to the uiMessageStack if needed
- `readDto`: Returns the validated business object. Throws an exception on error.
- `publishDtList`: Adds to the context a list (DtList)
- `readDtList`: Returns the validated business object. Throws an exception on error.
- `publishDtListModifiable`: Adds to the context a modifiable list (DtList)
- `checkDtListErrors`: Checks the errors of the list. These are added to the uiMessageStack if needed
- `readDtListModifiable`: Returns the list of validated business objects. Throws an exception on error.
- `publishMdl`: Adds to the context a reference list (MDL: Master Data List), specifying the entity and the code of the list.
- `publishFacetedQueryResult`: Adds to the context the result of a faceted search.
- `getUiObject`: Retrieves from the context the object coming from the UI, as received on the server. Reserved for a few cases: used to do non-blocking checks for example.
- `getUiList`: Retrieves from the context the list coming from the UI, as received on the server. Reserved for a few cases.
- `getUiListModifiable`: Retrieves from the context the modifiable list coming from the UI
- `getString`: Retrieves a string from the context
- `getLong`: Retrieves a Long from the context
- `getInteger`: Retrieves an Integer from the context
- `getBoolean`: Retrieves a Boolean from the context
- `getSelectedFacetValues`: Retrieves the list of facets selected from the UI of the faceted search.

## UI: How to read?

As presented above, the UI is the composition of several building blocks: VueJS, Quasar, Thymeleaf and Vertigo-UI.
Before going into the details of each of these building blocks, here are some elements to help you get your bearings.

- The page is rendered in two places: on the server by Thymeleaf and the Vertigo-UI components, and on the client by VueJS and Quasar.
- the `th:` prefix indicates to Thymeleaf to interpret the component or the attribute
- the `:` prefix indicates to VueJS to interpret the component or the attribute
- the `th::` prefix is the composition of `th:` and `:`, Thymeleaf will interpret and leave the `:` for VueJS
- the `layout:` prefix is a Thymeleaf extension that offers templating like *Tiles*.
- the attributes starting with `v-` are VueJS directives
- the tags starting with `<q-` are Quasar components.
- the tags starting with `<vu:` are Vertigo-UI components.


## Rendering Engine: VueJS

VueJS documentation on [vuejs.org](https://vuejs.org/guide/)

VueJS 3 offers a WebComponent approach with a reactive UI mapped to a view model, according to the Observer/Observable pattern.

- **inline** `{{abc}}`: The use of *mustaches* allows directly adding the value of `abc` to the DOM. The value is *reactive* and HTML-encoded
- **prefix** `:`: This prefix indicates that VueJS must interpret the following attribute. This allows VueJS to interpret standard HTML attributes or those of a webComponent (like src, value or icon of quasar)
- `v-if="..."`: Gives the display condition on a node of the DOM. The condition can be a variable of the vueData or an expression to evaluate. Note: the element disappears from the DOM, but is present on the client side and is not suitable for the setup of security.
- `v-for="item in items"`: The element on which the `v-for` is set is duplicated for each element. The loop variable can be used to change the rendering of each loop
- `v-model`: Indicates the data of the vueData bound on the component
- `@click`: Specifies an action to perform on the `click` event of the component. The `@click.native` variant is no longer necessary with Vue 3 (events are automatically forwarded)
- `v-pre`: Indicates to Vue to skip the compilation of this portion of DOM. Used automatically by `vu:utext` to protect against XSS injections
- `v-once`: Renders the node and its children in one pass, subsequent reactivity jumps are ignored

For a pure Vue application (SPA) without Thymeleaf server-side rendering, Vertigo does not provide a client-side authorization mechanism. The recommended pattern consists in exposing the user's rights via a WebService (*a priori* authorizations and authorized operations per entity), then evaluating the display accordingly on the client side. This client-side control only serves the display: the server-side control remains mandatory — it is the one that counts. See the [Vue SPA](/en/extensions/account#vue-spa) section of the vertigo-account module for the detailed pattern, and the [Other Vertigo-UI specifics](#other-vertigo-ui-specifics) section of this file for SSR (`vu:authz` / `th:if`).

## Component Library: Quasar

Quasar documentation on [quasar.dev](https://quasar.dev/vue-components/)

!> Vertigo-UI 4.4.1 uses Quasar **2.21.1** (Vue 3). The Quasar 1 → 2 migration notably concerned `q-modal` → `q-dialog` (`QModal` is absent from Quasar 2). For file upload, this is not a Quasar API change: `QUploader` does exist in Quasar 2.21.1; it is the Vertigo-UI component that now uses the in-house component `v-file-upload-quasar` (instead of Quasar's `q-uploader`).

The most common components are:

- `q-page`
- `q-layout`
- `q-toolbar`
- `q-btn`
- `q-item`
- `q-dialog` (replaces `q-modal` of Quasar 1)
- `q-icon`
- `q-knob`
- `q-slider`

> **Themes**: the theme of a layout is chosen with `useDsfr` (default `false`, available on `vu:head` and `vu:head-meta`), which loads the DSFR theme (`vertigo-dsfr.css` + `dsfr.umd.js`). The `onlyDsfrStyle` parameter (default `false`) is exclusive to `vu:head-meta`: it masks all non-DSFR 3rd-party CSS (including the Quasar CSS) — passed on `vu:head`, it has no effect. The DSFR theme is completed by a family of `vu:dsfr-*` components (buttons, collections, inputs, layout, table), documented in the [UI Ecosystem](/en/extensions/ui-ecosystem) page.

## Templating Engine: Thymeleaf

Requires:
```HTML
<html xmlns:th="http://www.thymeleaf.org">
```
Thymeleaf documentation on [thymeleaf.org](https://www.thymeleaf.org/doc/thymeleaf-spring6) (version 3.1.5, compatible with Spring 6)

- **inline** `__${...}__`: Preprocessor. Indicates to Thymeleaf that this portion must be pre-processed. This is used for expressions inside another more global expression.
- **inline** `|...|`: Literal substitution. Allows writing a string containing parts to evaluate, to simplify writing it and avoid string concatenations.
- **inline html** `[[...]]`: Literal substitution. Allows writing a string containing dynamic text directly in the html (`[(...)]` for the equivalent of `th:utext`). It requires a `th:inline` in one of the parent tags of the content.
- **prefix** `th:`: This prefix indicates that Thymeleaf must interpret the following attribute. This allows Thymeleaf to interpret standard HTML attributes. On the tags, this corresponds to the namespace of the Thymeleaf-specific tags.
- `abc?:bcd`: Often used to simplify the writing, equivalent of `abc != null ? abc : bcd`
- `${...}`: Evaluates a variable expression. Ex: `${name}` or `${user.name}`
- `@{...}`: Rebuilds the url of a link.
- `#{...}`: References an i18n resource.
- `~{abc::bcd}`: Selects a fragment. The syntax is `~{ path/to/the/template.html :: fragmentSelector}`. The selector is either the name of a fragment, or a standard javascript selector (`#id`, `.class`, ...)
- `th:if`: Gives the display condition on a tag (and its body). The filter is performed on the server side and is suitable for security.
- `th:with="var1=${...}, var2=${...}"`: Declares local variables. The scope is the content of the tag, even outside the file: when other fragments are included the variable remains accessible.
- `th:attr="var1=${...}, var2=${...}"`: Declares global variables. To be used with caution.
- `th:text`: Evaluates the content of the attribute and adds it to the body of the tag.
- `th:each="abc : bcd"`: Allows creating a loop on the tag that carries it. Loop on `bcd`, current element in the variable `abc`.
- `th:include="abc::bcd"`: Base component of the Thymeleaf templating. The body of the template tag is copied over in the tag carrying the attribute, the template tag is lost. The syntax is the same as for the fragment selector `~{abc::bcd}`.
- `th:replace="abc::bcd"`: Component of the Thymeleaf templating. The tag carrying the attribute is replaced by the one of the template. The syntax is the same as for the fragment selector `~{abc::bcd}`.
- `th:remove="*mode*"`: Removes tags from the DOM, depending on the mode. The most common modes are:
  - `all` removes the tag and its children
  - `tag` removes the tag and keeps its children
- `th:fragment="fragName"`: Base component of the Thymeleaf templating. Used to name a reusable template.


## Layout Engine: Thymeleaf Layout

Thymeleaf Layout documentation on [thymeleaf-layout-dialect](https://ultraq.github.io/thymeleaf-layout-dialect/)

Requires:
```HTML
<html xmlns:layout="http://www.ultraq.net.nz/thymeleaf/layout">
```

- `<head>`: The attributes of `<head>` are automatically merged between the page and its layout. Some are overridden (like `<title>`), others concatenated (like the `<script>`).
- `layout:decorate`: Added on the `<html>` tag of the content, it allows specifying which layout this content uses (it *decorates* it).
- `layout:fragment`: Added on the internal tags of the content, it allows indicating in which fragment of the layout this specific content is placed.

> Layouts can inherit from other layouts.

Layouts allow sharing all the recurring parts of the pages: banner, menu, footer, ...
The principle is that a layout is a page with holes, the holes are named in the template and can have a default value. When writing a page, we indicate that we *decorate* a particular layout, and we only specify the value of the *holes*. The goal is that the elements written in the page are only the elements specific to this page, all the common content is in the layout.
The webapp of a current Vertigo application is on the classpath: the templates — a base layout (banner, menu, footer) that each page will decorate — are typically in `src/main/resources/<packageRoot>/webapp/WEB-INF/views/templates`.


## Vertigo-UI Named Components

Vertigo-UI components use Thymeleaf templating, each component is in fact a `th:replace` with a bit of complementary intelligence.
The principle (and the code) is taken from [thymeleaf-component-dialect](https://github.com/Serbroda/thymeleaf-component-dialect)

Vertigo-UI components are Thymeleaf fragments, they are evaluated on the server side and several of them thus encapsulate a VueJS or quasar component.
Vertigo-UI is not intended to encapsulate all UI components this way, the strategy on the Vertigo-UI components is studied according to the following points:

- the component is a high-level component representing a logical component. Beneath it there will be several UI components, an enriched behavior, ergonomic choices adapted to our context.
- the component requires particular interactions with the context. For example to select the data to integrate in vueData, and sometimes to encode them in a specific way.
- the component offers a more ergonomic, more suitable or less verbose API for the developer

Requires:
```HTML
<html xmlns:vu="http://www.morphbit.com/thymeleaf/component">
```

### Component Parameters
- `abc_slot`: Allows retrieving a `vu:slot` in the body of the calling tag and placing it in the component (Ex: `vu:table`)
- `abc_attrs`: Aggregation of all the parameters prefixed by `abc_` passed during the call of the component. Ex: on `vu:table` one can pass the attribute `tr_class`, the parameter `class` (with its value) will be retrieved in the component by the parameter `tr_attrs` to place it on the internal `tr` tag. *Avoids having to provide for all cases during the design of the component.*
- `other_attrs`: Aggregation of all the parameters not identified as a parameter of the component, and allows determining where they should be placed. (Ex: in the component `vu:text-field`, the attributes not identified as a parameter are placed on the internal `q-input`, for example `<vu:text-field round>` will give `<q-input round>`)
- `contentTags`: Particular parameter retrieving the tags in the body of the component during the call, in the form of a list of `contentItem`. This case is quite rare, usually one rather uses `<vu:content>` which places the whole body. `contentItem` allows testing the tags to process them specifically (Ex: `grid` places the tags in blocks and `vu:grid-cell` has a particular behavior)

### Vertigo-UI Components: layout
- `vu:page`: Mandatory component framing the zone on which VueJS is active.
  - `content`: The body of the tag is kept
  - `vuiSsr`: **boolean** (default `false`). If `true`, activates Server Side Rendering: the content of the page is placed in a `<vertigo-ssr>` tag which is replaced by the rendering, the Vue template being pre-compiled on the server side by `VuejsSsrFilter` (CSP compliant). If `false`: classic client-side rendering
- `vu:head`: Sets the head tag and the metas of the html head
  - `title`*: Title of the page
  - `content`: The body of the tag is kept
  - `vueJsVersion`: Version of the loaded VueJS (default `3.5.39`)
  - `axiosVersion`: Version of the loaded Axios JS library (default `1.18.1`)
  - `vuejsDevMode`: **boolean** (default `false`): switches VueJS to dev mode — loads the non-minified builds (`vue.global.js` instead of `vue.global.prod.js`, and `quasar.umd.js` instead of `quasar.umd.prod.js`) *(we have noted bugs on VueJS in a few cases that only appear in devMode)*
  - `vuiDevMode`: **boolean** (default `false`): activates the developer mode for the Vertigo-UI components (a Vite dev server is required — `npm run dev`, port 3000 — which distributes the source modules transformed on the fly)
  - `vuiSsr`: **boolean** (default `false`): Activates the Server Side Rendering mode (the Node.js server is optional; failing that, the pre-compilation of the template is ensured by the embedded Nashorn engine — `vue-template-compiler` browser.js) — loads `vertigo-ui-mpa-ssr.js` instead of `vertigo-ui-mpa.js`
  - `vertigoUiVersion`: Version of Vertigo-UI, used as a `?v=` cache-buster on the local assets (vertigo-ui.css, vertigo-ui.umd.js, vertigo-ui-mpa, wysiwyg, DSFR) (default `4.4.1`)
  - `useQuasar`: **boolean** (default `true`): loads Quasar (CSS, UMD script, locale)
  - `quasarVersion`: Version of the loaded Quasar (default `2.21.1`)
  - `robotoVersion`: Version of the loaded Roboto font (default `51`; the value `null` does not load Roboto)
  - `fontAwesomeVersion`: Version of the loaded Font Awesome (default `6.7.2`; the value `null` does not load Font Awesome)
  - `useDsfr`: **boolean** (default `false`): loads the DSFR theme (`vertigo-dsfr.css` + `dsfr.umd.js`)
  - `useWysiwyg`: **boolean**: loads the assets of the Vertigo-Wysiwyg editor (tiptap) — `vertigo-wysiwyg.css` + `vertigo-wysiwyg.umd.js`; not loaded if not specified
  - `additional_defer_libs_slot`: Slot to inject additional (deferred) scripts, placed after Quasar and before the Vertigo-UI UMD
- `vu:head-meta`: Mandatory component setting the **meta** elements of the head (js script, css, ...)
  - `vueJsVersion`: Version of the loaded VueJS (default `3.5.39`)
  - `axiosVersion`: Version of the loaded Axios JS library (default `1.18.1`)
  - `vuejsDevMode`: **boolean** (default `false`): switches VueJS to dev mode — loads the non-minified builds (`vue.global.js` instead of `vue.global.prod.js`, and `quasar.umd.js` instead of `quasar.umd.prod.js`) *(we have noted bugs on VueJS in a few cases that only appear in devMode)*
  - `vuiDevMode`: **boolean** (default `false`): activates the developer mode for the Vertigo-UI components (a Vite dev server is required — `npm run dev`, port 3000 — which distributes the source modules transformed on the fly)
  - `vuiSsr`: **boolean** (default `false`): Activates the Server Side Rendering mode — loads `vertigo-ui-mpa-ssr.js` instead of `vertigo-ui-mpa.js`
  - `vertigoUiVersion`: Version of Vertigo-UI, used as a `?v=` cache-buster on the local assets (vertigo-ui.css, vertigo-ui.umd.js, vertigo-ui-mpa, wysiwyg, DSFR) (default `4.4.1`)
  - `useQuasar`: **boolean** (default `true`): loads Quasar (CSS, UMD script, locale)
  - `quasarVersion`: Version of the loaded Quasar (default `2.21.1`)
  - `onlyDsfrStyle`: **boolean** (default `false`): masks all non-DSFR 3rd-party CSS (Roboto, Material Icons, Font Awesome, Ionicons, Material Design Icons, Animate.css) as well as the Quasar CSS (the Quasar JS scripts remain loaded)
  - `robotoVersion`: Version of the loaded Roboto font (default `51`; the value `null` does not load Roboto) — not loaded if `onlyDsfrStyle`
  - `fontAwesomeVersion`: Version of the loaded Font Awesome (default `6.7.2`; the value `null` does not load Font Awesome) — not loaded if `onlyDsfrStyle`
  - `useDsfr`: **boolean** (default `false`): loads the DSFR theme (`vertigo-dsfr.css` + `dsfr.umd.js`)
  - `useWysiwyg`: **boolean**: loads the assets of the Vertigo-Wysiwyg editor (tiptap) — `vertigo-wysiwyg.css` + `vertigo-wysiwyg.umd.js`; not loaded if not specified
  - `additional_defer_libs_slot`: Slot to inject additional (deferred) scripts, placed after Quasar and before the Vertigo-UI UMD
   <!-- source : head.html:1-89 — params exhaustifs extraits du fragment -->
- `vu:form`: Sets a form and references the associated page context
  - `content`: The body of the tag is kept
  - `other_attrs`: List of attributes to add on the form (tag `<form>`)
- `vu:block`: Block component (graphically visible), represented in the form of a card
  - `title`: Title of the block
  - `subtitle`: Subtitle of the block
  - `icon`: Icon of the block
  - `withFab` **boolean**: Adds the `withFab` class if necessary
  - `actions_slot`: Slot for positioning actions on the block *(replaces the icon)*
  - `header_attrs`: List of attributes to add on the header of the block (tag `<div>`)
  - `content_attrs`: List of attributes to add on the body of the block (tag `<div class="q-card-section">`)
  - `card_attrs`: List of attributes to add on the parent of the block (tag `<div class="q-card">`)
  - `content`: The body of the tag is kept
- `vu:grid`: Declares a grid layout
  - `cols`: Number of columns. Default: 2
  - `dense`: Applies a *dense* mode reducing the size of the gutters
  - `contentTags`: The content of the tag is kept. Each element is placed in a `<div>` with the expected width. (a single column is forced under the **xs** breakpoint)
- `vu:grid-cell`: Declares a specific cell of a **grid**
  - `col`: Number of columns of the cell
  - `class`: CSS class of the cell
  - `div_attrs`: List of attributes to add on the body of the cell (tag `<div>`)
  - `content`: The body of the tag is kept
- `vu:messages`: Component adding the list of global messages from a processing that have been added in the context (**uiMessageStack** with Errors, Warnings, Info and Success)
- `vu:modal`: Sets the modal container, which can be used later in the screen.
  - `componentId`: Name of the component, used to target the modal in Js
  - `title`: Title of the modal
  - `closeLabel`: Label of the modal closing
  - `srcUrl`: Url of the modal (optional, usually passed by the opening script)
  - `iframe_attrs`: List of attributes to add on the iframe
  - `modal_attrs`: List of attributes to add on the modal (tag `<q-dialog>`)

!> `componentStates` is reset on each request (`new ComponentStates()` in `prepareContext`/`preInitContext`). The states of the components no longer persist between requests: `opened = false` in an AJAX callback works because everything stays on the client side.

Modal usage example:
```HTML
  <q-btn round icon="edit" label="View detail" th:@click="|openModal('dossierDetailModal', '@{/projet/dossier/}' + props.row.dossierId , {'successCallback' : 'onDossierSuccess' })|"></q-btn>

  <vu:modal componentId="dossierDetailModal" title="Dossier" iframe_width="800" iframe_height="400"  />
      
  <script type="text/javascript">
    function onDossierSuccess() {
      VUiPage.$data.componentStates.dossierDetailModal.opened = false;
      VUiPage.httpPostAjax("[[@{/projet/dossier/_reloadDossiers}]]", {});
    }
  </script>
```

- `vu:content`: Tag used in the components to mark the insertion of the `content` (ie: the body of the tag when using this component). The body can be used to define the default rendering.
- `vu:content-item`: Tag used in the components to mark the insertion of the `contentItem`. Used in particular cases where the components placed in the body of another component must be interpreted separately. The example case is the `grid` component. To be used correctly, the parent component must have a contentTags attribute, set a loop on it with the item name `contentItem`. (cf. [grid](https://raw.githubusercontent.com/vertigo-io/vertigo-libs/master/vertigo-ui/src/main/resources/io/vertigo/ui/components/quasar/layout/grid.html) )
- `vu:slot` *tag*: Component that passes the content of a slot to the parent component. The slots of the parent component are referenced by the suffix `_slot`.
  - `name`: Name of the slot
  - `content`: The body of the tag is passed to the parent component and will be inserted either with the `vu:slot` attribute or the `<vu:content-slot />` tag
- `vu:slot` *attribute*: Attribute used in the components to mark the insertion of the slot. The tag is kept. Equivalent of a `th:include="${my_slot}"`.
  - `value`: Name of the slot (Ex: `vu:slot="top_left_slot"`)
- `vu:content-slot`: Tag used in the components to mark the insertion of the `slot`. This tag is replaced by the slot. The body can be used to define the default rendering.
  - `name`: Name of the slot

### Vertigo-UI Components: utils

These components are technical components.
The `include-data-*` components all have the same role: they indicate to the server to transfer the data from the server context (`CTX`) into the Vue context (`vueData` object).
This strategy ensures that only useful data are pushed on the client side. Most of the time they are not used directly, as they are set by the `inputs` components that need them.
They remain useful to precisely add data in the `vueData`, for specific vue components for example.

- `vu:include-data`: Includes the field of an object
  - `object`: Name of the object of the context
  - `field`: Name of the field
  - `modifiable`: Indicates that the field is modifiable on the client side and can be sent back to the server
  - `modifiableAllLines`: Indicates that all the lines are modifiable
- `vu:include-data-primitive`: Includes a primitive data of the context
  - `key`: Key of the data
  - `modifiable`: Indicates that the field is modifiable on the client side and can be sent back to the server
- `vu:include-data-map`: Includes the field of an object and applies a denormalization on its value (translates an id into a label for example)
  - `object`: Name of the object of the context
  - `field`: Name of the field
  - `list`: List of the mapping to apply
  - `listKey`: Key field of the mapping list
  - `listDisplay`: Label field of the mapping list
- `vu:include-data-protected`: Includes the field of an object. The value set on the client side is protected (not in clear and not modifiable), the real value stays on the server side. This system is used for file identifiers for example.
  - `object`: Name of the object of the context
  - `field`: Name of the field
- `vu:utext`: Tag.processor applying `th:utext` **and** `v-pre` automatically. Allows displaying dynamic HTML with untrusted content while protecting against VueJS XSS injections. The `v-pre` prevents VueJS from compiling the injected content.
  - `content`: HTML content processed by the tag processor
- `vu:vue-data`: Sets the view data for VueJS. **Must not be used directly**, it is set by `vu:page`


### Vertigo-UI Components: inputs

These components are the main components for building the forms of the applications.
To simplify the writing of the screens, most of them handle the `viewMode` in order to propose a rendering depending on the **Edit** mode or the **ReadOnly** mode.
The components in **Edit** also natively handle the error messages from the validation controls.

- `vu:label`: Label component
  - `object`*: Name of the object of the context
  - `field`*: Name of the field
  - `label`: Override of the label
  - `other_attrs`: List of attributes to add on the label (tag `<q-field>`)
- `vu:text-field`: Text field component
  - `object`*: Name of the object of the context
  - `field`*: Name of the field
  - `label`: Override of the label
  - `suffix`: Override of the suffix
  - `label_attrs`: List of attributes to add on the label (tag `<q-field>`)
  - `input_attrs`: List of attributes to add on the input field (tag `<q-input>`)
- `vu:text-area`: Text area component
  - `object`*: Name of the object of the context
  - `field`*: Name of the field
  - `label`: Override of the label
  - `label_attrs`: List of attributes to add on the label (tag `<q-field>`)
  - `input_attrs`: List of attributes to add on the input field (tag `<q-input>`)
- `vu:autocomplete`: Autocomplete component: choice in a list from the label, which assigns the value to the field
  - `object`*: Name of the object of the context
  - `field`*: Name of the field
  - `label`: Override of the label
  - `list`*: Name of the list of the context
  - `valueField`: Name of the field of the list used as value, to assign in the object
  - `labelField`: Name of the field of the list used as label
  - `componentId`: id of the VueJS component
  - `label_attrs`: List of attributes to add on the label (tag `<q-field>`)
  - `input_attrs`: List of attributes to add on the input field (tag `<q-select>`)
- `vu:checkbox`: Checkbox component
  - `object`*: Name of the object of the context
  - `field`*: Name of the field
  - `label`: Override of the label
  - `label_attrs`: List of attributes to add on the label (tag `<q-field>`)
  - `input_attrs`: List of attributes to add on the input field (tag `<q-checkbox>`)
- `vu:select`: Selection component by a combobox
  - `object`*: Name of the object of the context
  - `field`*: Name of the field
  - `label`: Override of the label
  - `list`*: Name of the list of the context
  - `valueField`: Name of the field of the list used as value, to assign in the object
  - `labelField`: Name of the field of the list used as label
  - `label_attrs`: List of attributes to add on the label (tag `<q-field>`)
  - `input_attrs`: List of attributes to add on the input field (tag `<q-select>`)
- `vu:select-multiple`: Multiple selection component by a combobox
  - `object`*: Name of the object of the context
  - `field`*: Name of the field
  - `label`: Override of the label
  - `list`*: Name of the list of the context
  - `valueField`: Name of the field of the list used as value, to assign in the object
  - `labelField`: Name of the field of the list used as label
  - `label_attrs`: List of attributes to add on the label (tag `<q-field>`)
  - `input_attrs`: List of attributes to add on the input field (tag `<q-select>`)
- `vu:radio`: Selection component by a list of radio buttons
  - `object`*: Name of the object of the context
  - `field`*: Name of the field
  - `label`: Override of the label
  - `list`*: Name of the list of the context
  - `valueField`: Name of the field of the list used as value, to assign in the object
  - `labelField`: Name of the field of the list used as label
  - `layout`: Layout of the radio: `horizontal` or `vertical`
  - `label_attrs`: List of attributes to add on the label (tag `<q-field>`)
  - `input_attrs`: List of attributes to add on the input field (tag `<q-radio>`)
- `vu:date`: Date selection component
  - `object`*: Name of the object of the context
  - `field`*: Name of the field
  - `label`: Override of the label
  - `format`: Display format of the date (default `DD/MM/YYYY`). The value is always stored and exchanged in ISO `YYYY-MM-DD`.
  - `date_attrs`: List of attributes to add on the date (tag `<q-date>`)
  - `input_attrs`: List of attributes to add on the input field (tag `<q-input>`)
- `vu:datetime`: Date/time selection component
  - `object`*: Name of the object of the context
  - `field`*: Name of the field
  - `label`: Override of the label
  - `format`: Display format of the date/time (default `DD/MM/YYYY HH:mm`). The value is always stored and exchanged in ISO `YYYY-MM-DDTHH:mm`.
  - `date_attrs`: List of attributes to add on the date (tag `<q-date>`)
  - `time_attrs`: List of attributes to add on the time (tag `<q-time>`)
  - `input_attrs`: List of attributes to add on the input field (tag `<q-input>`)
- `vu:knob`: Graphic component for modifying a numeric value
  - `object`*: Name of the object of the context
  - `field`*: Name of the field
  - `label`: Override of the label
  - `min`: Minimum value
  - `max`: Maximum value
  - `step`: Step of the value modifications
  - `label_attrs`: List of attributes to add on the label (tag `<q-field>`)
  - `input_attrs`: List of attributes to add on the input field (tag `<q-knob>`)
- `vu:slider`: Graphic component for modifying a numeric value
  - `object`*: Name of the object of the context
  - `field`*: Name of the field
  - `label`: Override of the label
  - `min`: Minimum value
  - `max`: Maximum value
  - `step`: Step of the value modifications
  - `label_attrs`: List of attributes to add on the label (tag `<q-field>`)
  - `input_attrs`: List of attributes to add on the input field (tag `<q-slider>`)
- `vu:chips-autocomplete`: Component for adding a list of tags by autocomplete
  - `object`*: Name of the object of the context
  - `field`*: Name of the field
  - `label`: Override of the label
  - `list`*: Name of the list of the context
  - `valueField`: Name of the field of the list used as value, to assign in the object
  - `labelField`: Name of the field of the list used as label
  - `componentId`: id of the VueJS component
  - `staticData`: Indicates if the data are static (or from a WebService `@{/autocomplete/_searchFullText}`)
  - `label_attrs`: List of attributes to add on the label (tag `<q-field>`)
  - `input_attrs`: List of attributes to add on the input field (tag `<q-select>`)
- `vu:fileupload`: File addition component (unlike the other input components, the id of the file is not stored in a business object)
  - `url`*: Url of the upload WebService
  - `key`*: Key of the context receiving the files
  - `multiple`: Indicates if several files are allowed
  - `maxFileSize`: Maximum size per file in MB (ex: `5`)
  - `maxTotalSize`: Maximum total size of all the files
  - `maxFiles`: Maximum number of allowed files
  - `accept`: MIME filter of the accepted files (ex: `"image/*,.pdf"`)
  - `uploader_attrs`: List of attributes to add on the upload component (tag `v-file-upload-quasar`)
- `vu:fileupload-dropzone`: File drop zone by drag-and-drop
  - `fileComponentId`*: Mandatory identifier linking the drop zone to the corresponding upload component

> To adapt their rendering these components use particular mechanisms.
> Globally a **Vertigo-UI: inputs** component is written thus:

```XML
<th:block th:fragment="label-edit(object,field, label, other_attrs)" vu:alias="label" vu:selector="${viewMode=='edit'}" >
  <vu:content/>
</th:block> 

<th:block th:fragment="label-read(object, field, label, other_attrs)" vu:alias="label" vu:selector="${viewMode=='read'}" >
  <vu:content/>
</th:block> 
```

> - The `th:fragment` names the particular component and its parameters.
> - the `vu:alias` names the alias of the component, it is often this name that is used in the pages
> - the `vu:selector` is an expression that is evaluated in the context of the component and allows selecting the fragment to use when using the alias
> - the `-edit`/`-read` fragments (ex. `vu:select-edit`, `vu:select-read`, `vu:text-field-read`) can be called directly to force the rendering mode without depending on `viewMode`


### Vertigo-UI Components: collections
- `vu:cards`: Generates a list of cards. During the rendering of a card, you can use the VueJS attribute `item` to retrieve the current object.
- `vu:collection`
- `vu:field-read`
- `vu:list`
- `vu:search`
- `vu:facets`


### Vertigo-UI Components: tables
- `vu:table`: Generates a table. During the rendering of a line, you can use the VueJS attribute `props.row` to retrieve the current object.
  - list
  - componentId
  - selectable
  - rowKey
  - rowsPerPage
  - sortUrl
  - navOnRow
  - color
  - tableClass
  - autoColClass
  - top_right_slot
  - top_left_slot
  - actions_slot
  - tr_attrs
  - other_attrs
- `vu:column`
  - list
  - field
  - name
  - label
  - align
  - sortable
  - class
  - td_attrs

### Vertigo-UI Components: buttons
- `vu:button`: Sets an action button (tag `<q-btn>`), whose behavior (ex. `@click`) is carried by the passed attributes — complement of `vu:button-link` (url) and `vu:button-submit` (form)
   - label: label of the button
   - icon: icon of the button
   - color: color of the button (default `primary`)
   - text-color: color of the text of the button
   - title: label for accessibility
   - v-title: label for accessibility (reactive VueJS variant)
   - other_attrs: all other attributes. Set on the `<q-btn>`
- `vu:button-confirm`: Sets an action button with a confirmation popin (tag `<q-btn>` opening a `q-dialog`)
   - actions_slot: slot of the cancel and confirmation buttons
   - key: instance key of the popin (suffix of the internal ref, default `props?.rowIndex`)
   - label: label of the button
   - icon: icon of the button
   - color: color of the button (default `primary`)
   - text-color: color of the text of the button
   - title: label for accessibility
   - v-title: label for accessibility (reactive VueJS variant)
   - confirmMessage: confirmation message
   - labelOk: label of the OK button (default Yes)
   - labelCancel: label of the cancel button (default No)
   - ok_attrs: all other attributes. Set on the OK button of the confirmation
   - other_attrs: all other attributes. Set on the `<q-btn>` (not on the internal confirmation button)
- `vu:button-link`: Sets a button of link type (tag `<q-btn type="a">`)
   - label: label of the button
   - icon: icon of the button
   - url: url of the link
   - title: label for accessibility
   - disabled: **boolean** if the button is disabled
   - other_attrs: all other attributes. Set on the `<q-btn>`
- `vu:button-link-confirm`: Sets a button of link type with a confirmation popin (tag `<q-btn type="a">`)
   - actions_slot: slot of the cancel and confirmation buttons
   - label: label of the button
   - icon: icon of the button
   - url: url of the link
   - title: label for accessibility
   - disabled: **boolean** if the button is disabled
   - confirmMessage: confirmation message
   - labelOk: label of the OK button (default Yes)
   - labelCancel: label of the cancel button (default No)
   - other_attrs: all other attributes. Set on the `<q-btn>` (not on the internal confirmation button)
- `vu:button-submit`: Sets a button of submit type (tag `<q-btn type="submit">`)
   - label: label of the button
   - icon: icon of the button
   - action: name of the associated action
   - title: label for accessibility
   - other_attrs: all other attributes. Set on the `<q-btn>`

- `vu:button-submit-confirm`: Sets a button of submit type (tag `<q-btn type="submit">`)
   - actions_slot: slot of the cancel and confirmation buttons
   - label: label of the button
   - icon: icon of the button
   - action*: name of the associated action
   - title: label for accessibility
   - formId*: identifier of the form (necessary because the popin is outside the form)
   - confirmMessage: confirmation message
   - labelOk: label of the OK button (default Yes)
   - labelCancel: label of the cancel button (default No)
   - other_attrs: all other attributes. Set on the `<q-btn>` (not on the internal confirmation button)


## Vertigo-UI VueJS Components

- `vueData`
- `v-notifications`
- `v-comments`
- `v-scroll-spy`
- `v-json-editor`
- `v-chatbot`

## For Experts

### Managers & Configuration

The vertigo-ui module has no dedicated `XxxFeatures.java`. UI components are activated by the applicative Features class, which extends the abstract class `DefaultUiModuleFeatures`. The UI activation (addition of the `VSpringMvcConfigDefinitionProvider` with the parameters `name`, `packages` and `componentDirs`, whose values are derived from the root package of the applicative module (no parameter to provide manually)) is triggered by the call `addUi()`, performed by the **inherited** `buildFeatures()` from `DefaultUiModuleFeatures`: in minimal form, the applicative class does not override `buildFeatures()`; if it must add its own providers there, the override MUST start with `super.buildFeatures()` (otherwise no DAO/Service/WebService of the module is registered).

### ViewContext

`ViewContext` is the central object of the UI layer, representing the context of a page. It allows publishing and reading objects, lists and primitives between the controller and the view.

| Method | Description |
|---|---|
| `publishDto` | Publishes a form object (DtObject) in the context |
| `readDto` | Reads and validates the form object (throws `ValidationUserException` on validation error) |
| `publishDtList` | Publishes a list (DtList) in the context |
| `publishDtListModifiable` | Publishes a modifiable list |
| `publishMdl` | Publishes a reference list (Master Data List) |
| `publishFacetedQueryResult` | Publishes the result of a faceted search |
| `getUiObject` / `getUiList` | Retrieves the data as received from the UI |
| `ViewContextMap` | Typed map to access the elements of the context via `ViewContextKey` |
| `ViewContextUpdateSecurity` | Controls the security of the updates of the context |

### Spring MVC

| Component | Description |
|---|---|
| `VSpringWebConfig` | Base Spring MVC configuration |
| `VSpringMvcConfigDefinition` | Definition of the MVC configuration |
| `AbstractVSpringMvcController` | Parent controller to extend |
| `VSpringMvcControllerAdvice` | Global handling of exceptions and shared data |
| `VSpringMvcExceptionHandler` | Centralized exception handler |
| `VSpringMvcUiMessageStack` | UI message stack for the **rendering** of errors |
| `VRequestToViewNameTranslator` | Translation of the requests to view names |
| `VertigoLocaleResolver` | Resolution of the locale per user |

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
| `VSpringMvcAuthorizationInterceptor` | — | `@Secured` verification on the controllers |
| `VSpringMvcViewContextInterceptor` | — | Initialization of the ViewContext |
| `VSpringMvcErrorInterceptor` | — | Interception and rendering of errors |
| `RateLimitingHandlerInterceptor` | — | Rate limiting on the MVC requests |
| `VAnnotationHandlerInterceptorImpl` | — | Interception based on `@VControllerInterceptor` |
| `VControllerInterceptorEngine` | — | Interceptor execution engine |

### Thymeleaf

| Component | Description |
|---|---|
| `VUiStandardDialect` | Custom Thymeleaf dialect (`vu:`) |
| `VuiResourceTemplateResolver` | Resolution of templates from classpath/webapp |
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

!> **`vu:authz` in development mode**: with the context variable `authz-dev`, the unauthorized elements are not removed, they are displayed in locked state. This allows visualizing the authorizations (which elements are hidden and why) and testing the server-side security in development conditions.

### UI Data Wrappers

| Class | Description |
|---|---|
| `UiListUnmodifiable` | Read-only list |
| `BasicUiListModifiable` | List modifiable on the client side |
| `UiMdList` | Master Data list (reference) |
| `MapUiObject` | UI object in the form of a Map |
| `UiFileInfo` / `UiFileInfoList` | Secure file information |
| `ClusterUiList` | List for the cluster display |
| `UiSelectedFacetValues` | Facets selected in a search |
| `ComponentRef` / `ComponentStates` | Reference and state of the Vue components |
| `FormMode` | Form mode (edit/read) |
| `AjaxResponseBuilder` | Construction of AJAX responses |
| `ProtectedValueUtil` / `FileInfoURIAdapter` | Encoding of protected values |

### Quasar Tree

| Class | Description |
|---|---|
| `Tree` | Representation of a tree |
| `TreeNode` / `TreeNodeData` | Node of the tree |
| `TreeBuilder` | Fluent construction of trees |
| `LevelContext` / `ListContext` | Rendering context per level |

### Jetty Boot

| Class | Description |
|---|---|
| `JettyBoot` | Startup of the embedded Jetty server |
| `JettyBootParams` | Configuration parameters of Jetty |
| `JettyBootParamsBuilder` | Construction of the parameters |
| `withSessionTimeoutMinutes` | Configures `setMaxInactiveInterval` on the HTTP session (converts minutes → seconds) |
| `KVSessionDataStoreFactory` | Factory of Jetty session storage |
| `KVSessionDataStore` | Storage of the Jetty sessions via KVStore |

### VueJS SSR

| Class | Description |
|---|---|
| `VuejsSsrFilter` | Servlet Filter for the VueJS Server-Side Rendering |
| `VuejsSsrServletResponseWrapper` | Wrapper of the SSR HTTP response |
| `VuejsSsrResponseStream` | Output stream of the SSR rendering |
| `UnAutoCloseTagsFilter` | Filter to correct tags opened in double |

### Exceptions

| Exception | Description |
|---|---|
| `ExpiredViewContextException` | Thrown when the ViewContext is expired |

### YAML Configuration

`DefaultUiModuleFeatures` is an abstract class: it is the base class that the applicative module extends to activate the UI components. The activation of the UI does not go through any YAML key: cf. the "Managers & Configuration" section above (first section of the "For Experts" part) for the mechanism (`DefaultUiModuleFeatures`, `addUi()`, `super.buildFeatures()` warning).

```java
package io.gestionprojet;

import io.vertigo.ui.impl.springmvc.config.DefaultUiModuleFeatures;

public class GestionProjetFeatures extends DefaultUiModuleFeatures<GestionProjetFeatures> {

    public GestionProjetFeatures() {
        super("gestionprojet");
    }
}
```

The applicative module is then simply declared in the YAML configuration (no `ui` feature to activate):

```yaml
modules:
  io.gestionprojet.GestionProjetFeatures:
```
