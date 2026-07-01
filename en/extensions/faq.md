# FAQ

Common questions and answers.
Feel free to contact us at support@vertigo.io or on our Discord.

## [DataStore] My project stores attachments, which storage type should I choose?
Vertigo offers several storage types.
Choice depends on volume and hosting constraints.
For low volume, database storage is possible.
Otherwise, prefer metadata in database and files on FileSystem.
For large volumes, object storage (MinIO type) may be preferable.

## [Ui] Components seem not to work
To activate components, configure SpringMvc: your project config file must inherit from VertigoUi's VSpringWebConfig, which sets up all necessary Spring config.
See Mars config example: https://github.com/vertigo-io/vertigo-mars/blob/master/src/main/java/io/mars/support/boot/MarsVSpringWebConfig.java
The Maven archetype typically sets this up correctly.

## [Ui] Page refuses to display and stays blank
If page contains `layout:decorate="~{templates/MyLayout}"`, the page must follow MyLayout structure.
A layout is a full page with holes.
For a page, you specify which layout to use and what goes in the holes.
Multiple layout levels are possible but hurt readability; don't overdo it.
Typically: one general layout, one for search/home pages, one for detail pages.

## [Studio] Which data modeling tool to use?
Vertigo Studio is natively compatible with PowerDesigner and Enterprise Architect.
PowerDesigner is recommended as more complete; Enterprise Architect uses XMI.
Latest Vertigo offers HTML model rendering (via mermaid-js). Expensive tools can then be avoided.

## [Ui] Where are CSS classes like `col-md-3 col-xs-12 q-jumbotron bg-white`?
These are classes from the Quasar component library (https://quasar.dev/layout/grid/introduction-to-flexbox#Responsive-Design)

## [Ui] How to debug Vue.js/Quasar screens?
Browser extension `Vue.js devtools` helps with debugging. Requires non-minified Vue.js version (add at page top).
Developer view and debugger can also be used.

## [Ui] `<vu:button-link>` buttons only work inside `<section>` tags
Section tag is related to Thymeleaf layouts.
All HTML code outside of tags actually included in the page is kept; the rest is lost.

## [Ui] On the UI side, how to access context data in the page?
Client-side data is accessible in VUiPage.vueData.
Only data requested during server-side rendering is accessible client-side for security.
Best practice: maximize server-side rendering.
For static information, use Thymeleaf tags directly server-side.

## [Ui] How to add a reference list to context?
A reference list is added to context with method `publishMdl`.
First declare the reference list:
Need a DefinitionProvider, e.g., `MarsMasterDataDefinitionProvider`.
DefinitionProvider must be added to module configuration, e.g., `io.mars.support.SupportFeatures`.
StaticMasterData provides enums for static reference lists not manageable via UI.

## [Ui] What is `<vu:include-data>` tag in mars demo screens?
Includes server context data into client vueData.
Normally display components handle include-data automatically.
In some cases, no display component (no vu:textfield, vu:column, ...) but client-side data is needed (e.g., to build a link); include manually.

## [Ui] I have `<vu:select>` in my form, it displays label instead of id, how to reproduce in a list with `<vu:column>`?
Often the underlying list object is a specific UI object; add a field to the list and adapt SQL to retrieve label directly.
For reference lists (watch performance), this can be done automatically by defining column content:
```HTML
<vu:column name="equipmentType" label="Equipment Type">
    <vu:field-read field="equipmentTypeId" list="equipmentTypes" listKey="equipmentTypeId" listDisplay="label" />
</vu:column>
```
Two ways to define a column:
- by referencing a field
- by defining a name then column content
Once in the second case, use special field `<vu:field-read>` as content to display a read-only field pointing to a list.

## [Ui] How to make list items selectable?
Add `selectable` attribute on `vu:table`.
Use authorization to propose if user has rights: `selectable="${authz.hasAuthorization('Equipment$delete')}"`

This activates selection binding in `componentStates.${componentId}.selected`.
To emit selection to server, specific code is needed.
Developer must use it to send to server in desired format.

UI-side: display certain buttons when items selected with `v-if="componentStates.reservationsTable.selected.length > 0"`

Example sending id list via Ajax (to delete items):
```Javascript
VUiExtensions.methods.deleteSelectedEquipment = function(deleteEquipmentUrl) {
  var formParams = this.vueDataParams(['deleteEquipmentMessage']);
  formParams.append('vContext[deletedEquipmentIds]', JSON.stringify(VertigoUi.componentStates.equipmentsTable.selected.map(row => row.equId)));
  this.httpPostAjax(deleteEquipmentUrl, formParams, {
    onSuccess: function(response) {
      this.$data.componentStates.equipmentsTable.selected = [];
    }.bind(this)
  });
};
```

Controller-side needs context element to receive (note: in this example, Controller has no pre-selection, would need componentStates setup):
```Java
private static final ViewContextKey<Long[]> deletedEquipmentIdsKey = ViewContextKey.of("deletedEquipmentIds");

public void initContext(final ViewContext viewContext) {
  viewContext.publishTypedRef(deletedEquipmentIdsKey, new Long[0], Long[].class);
}

@PostMapping("/_deleteEquipments")
public ViewContext deleteEquipments(final ViewContext viewContext,
   @ViewAttribute("deleteEquipmentMessage") final DeleteEquipmentMessage deleteEquipmentMessage,
   @ViewAttribute("deletedEquipmentIds") final Long[] equipmentIds,
   final UiMessageStack uiMessageStack) {
   final var equUids = Stream.of(equipmentIds).map(equId -> UID.of(Equipment.class, equId)).toList();
   equipmentServices.deleteEquipments(equUids, deleteEquipmentMessage, uiMessageStack);
   return viewContext;
}
```

## [Ui] How to make a field required based on another field?
Use DtObjectValidator.
Controller code to run validator on object:
```java
viewContext.getUiObject(contextKey).mergeAndCheckInput(Collections.singletonList(new YourCustomDtObjectValidator()), uiMessageStack);
if (uiMessageStack.hasErrors()) {
    throw new ValidationUserException();
}
```
To get uiMessageStack, include it in controller method signature (like ViewContext).

## [Mail] How to send an email?
MailManager helps send emails. (https://github.com/vertigo-io/vertigo-libs/blob/master/vertigo-social/src/test/java/io/vertigo/social/mail/MailManagerTest.java)

## [Ui] Can I have 2 `<vu:messages>` tags in a page?
No, only one.
Best to have `<vu:messages>` in the parent template.

## [Core] Vertigo Manager implementation not found (Components or params not found)
Activate the feature in app YAML config file (https://vertigo-io.github.io/vertigo-docs/#/basic/configuration)

## [Core] How to make a YAML config parameter modifiable by the hoster?
Parameters can be externalized with `${myParamName}` tag.
Value is then resolved by paramManager.

## [Studio] Double association in .ksp to same DtObject generates two methods with same name
Give each association a role (roleA and roleB); this role names the navigation method.

## [Ui] How to show a notification to user?
Use Quasar Notify API (cf: https://quasar.dev/quasar-plugins/notify#Notify-API)
After Ajax call, to get Quasar's `$q`:
- Bind function to this: `function(response){ this.$q.notify({message: 'TEST', type: 'positive'}).bind(this)`
- Or use global `VUiPage.$q.notify`

## [Ui] What is the Ajax call API?
Method `httpPostAjax` signature:
`httpPostAjax(url, params, options)`

Last parameter provides callbacks for success and error:
```java
{
   onSuccess: function (response) { // do something },
   onError(error) { // do something }
}
```

## [Ui] How to let user select multiple choices from a reference list?
Depends on storage mode. Two approach

1- In criteria object, add field with FK domain and cardinality `*`.
Field added to vueData as id array, mapped to checkbox:
```
<q-checkbox v-model="selectedTimeZoneList" v-for="item in vueData.timeZoneList" :val="item" :label="item"></q-checkbox>
```
Controller: field is id array. Not directly persistent; service translates to persistent data.

2- Use *SmartTypes*.
In criteria object, add field with SmartType domain (e.g., `DoIds`) with BasicType String.
Associate UI adapter to SmartType that transforms string to id list; serialized to JSON in vueData, used by checkbox as in case 1.
Controller: field is string, can be persisted directly if needed.

## [Ui] Ajax file upload not working

Page-side:
```Html
<vu:fileupload th:if="${model.modeEdit}" float-label="Add new pictures here" th:url="'@{/commons/upload}'" key="baseTmpPictureUris" multiple />
```

Controller-side:
```java
@PostMapping("/_save")
public String doSave(
      final ViewContext viewContext,
      @Validate(DefaultDtObjectValidator.class) @ViewAttribute("base") final Base base,
      @QueryParam("baseTmpPictureUris") final List<FileInfoURI> addedPictureFile,
      final UiMessageStack uiMessageStack) {
```

Upload component works in two steps:
1- User drops file on component; file is immediately sent to server, temporary id stored in form.
2- On form post, file id goes with business data; server retrieves file by id; controller receives business data and file.

When step 2 is Ajax, retrieve id manually:
```Html
<q-btn th:@click="|httpPostAjax('', {baseTmpPictureUris:VUiPage.componentStates.uploaderbaseTmpPictureUris.fileUris.toString()})|" label="Save"></q-btn>
```

## [DataStore] How to choose file storage plugin?
Vertigo offers several storage types.
Choice depends on volume and hosting constraints.
Low volume: database storage with `DbFileStorePlugin`.
Need mapping object with `FILE_DATA` field of type Blob (or `bytea` on PostgreSQL).

Otherwise: metadata in database and files on FileSystem with `FsFileStorePlugin`.
Mapping object with `FILE_PATH` String field storing physical file path.
Path points to project-appropriate space (e.g., NAS).

## [Ui] How to add extra parameter to `input` tag of `<vu:text-field>`?
Thymeleaf components accept `_attrs` suffixed parameters aggregating extra developer parameters.
Naming convention based:
Component `<vu:date>` has parameters: `object, field, label, format, date_attrs, input_attrs`.
On render:
- `date_attrs` value set on underlying `q-date` tag
- `input_attrs` value set on underlying `q-input` tag (main tag)

Usage:
When developer adds a parameter other than explicitly named ones `(object, field, label, format)`, it goes into an `_attrs` parameter:
- Prefixed by `date_`: aggregated in `date_attrs`
- Prefixed by `input_`: aggregated in `input_attrs`
- Unrecognized: aggregated in last `_attrs`, i.e., `input_attrs`
Adding `date_landscape` sets `landscape` on `q-date`.
Adding `input_placeholder="Placeholder"` sets `placeholder="Placeholder"` on `q-input`.
Adding `placeholder="Placeholder"` sets `placeholder="Placeholder"` on `q-input`.

## [DataStore] Can I filter a reference list to get only specific elements?
Reference lists are *named*: when registering (via `MasterDataDefinitionProvider`), specify:
- a name
- object type
- optional filter (via field, two fields, or Predicate)
Use named lists by publishing to `context` with `publishMdl`.
Special case: unnamed lists (`null`) default with no filter.

Example: retrieve only 'active' elements (boolean field with value):
In module's `MasterDataDefinitionProvider` (`extends AbstractMasterDataDefinitionProvider`):
```java
registerDtMasterDatas(EquipmentType.class, Map.of("active", EquipmentType::getActive), true);
```

In controller context:
```java
viewContext.publishMdl(ViewContextKey.of("equipmentTypes"), EquipmentType.class, "active");
```

## [DataStore] What does `isReloadedByList` parameter of `AbstractMasterDataDefinitionProvider.registerDtMasterDatas` mean?

Defines list reload mode on cache expiry: either reloads entire list and redispatches by id/value, or line by line.
List mode is recommended for most cases.
Unit mode is for large lists, like municipality list.

## [Ui] `vu:autocomplete` shows id instead of label
Autocomplete does not expect ViewContext return type; expects more specific format.
See generic autocomplete controller:
`io.vertigo.ui.controllers.ListAutocompleteController`

Issue may occur if underlying component (QSelect) lacks id-to-label mapping.
Normally done server-side in Thymeleaf template; Ajax requires special handling.

## [Ui] 404 on page but URL seems correct
With 404, controller is likely not registered in Spring.
Check:
- Controller annotations (unique `@RequestMapping(...)`)
- Spring configuration (*Project*`SpringWebConfig`) (notably scan packages)

## [Ui] Need Ajax on page because I have a map and can't lose it
"Manual" postAjax creation is possible for specific needs, but you lose accelerators. Ensure your case is justified.
`httpPostAjax` posts to a route (first argument), with parameters (second argument), handles return and errors:

```java
httpPostAjax('_saveMyData', {
  'vContext[myDataForm][field1]': vueData.myDataForm.field1,
  'vContext[myDataForm][field2]': vueData.myDataForm.field2,
  'vContext[myDataForm][field3]': vueData.myDataForm.field3
})
```

## [Ui] Need editable list but data not received server-side
DtList object is not modifiable by client for security.
For editable list in context, use `context.publishDtListModifiable`.
Table component `<vu:table>` requires row identifier: object must be an entity (persistent), or define `rowKey` on `<vu:table>`.

## [Vega] How to enable Swagger WebService viewing?
Documentation: https://vertigo-io.github.io/vertigo-docs/#/basic/webservices?id=swaggerapi
From version 2.1.0, Swagger catalog is activated by default.
Go to `/swaggerUi`.
If API prefix configured in Vega, use it: `_apiPrefix_/swaggerUi`.

## [Ui] Want automatic validation on an object input to my webservice
DtObjects have fields with business types: `SmartTypes`.
`SmartTypes` have constraint lists; Vertigo provides several, custom ones can be added.
When DtObject (or DtList) arrives via Vega WebService or SpringMVC controller, it passes through `DtObjectValidator`.
Default: `DefaultDtObjectValidator` checking `SmartType` constraints for all API-passed fields.
Add custom validator with `@Validate` annotation:
```java
@Validate(YourValidator.class)
```
Or multiple:
```java
@Validate({ YourValidator.class, YourOtherValidator.class })
```
Custom validators enable multi-field checks.

## [DataStore] Can I `load()` all `accessors` of an object at once?
No. Load is a significant operation (1 DB access). Load data based on service process.
Service granularity should be adapted; avoid services handling all app cases.
=> 2 distinct processes need 2 different business services.
Complete entity display case: rarely show everything at once.
- Dedicated DTO with SQL select filling it at once
- Tab-based layout presenting different information (controller loads data)

## [Ui] How to transfer files (pdf, word, ...) via WebServices?
Fully supported by Vertigo. For download, return `VFile`.
For upload with `<vu:fileupload>`, service takes VFile parameter; uses standard HTML multipart protocol.
*System protects identifier, not sent in plaintext client-side (cf. `ProtectedValueUtil`)*
**Important**: respect verbs: `GET` for download, `POST` for upload.

Example:
```java
@GetMapping("/myFiles/{protectedUrl}")
public VFile loadFile(@PathVariable("protectedUrl") final String protectedUrl) throws URISyntaxException, IOException {
   final URI fullPath = getClass().getResource(ProtectedValueUtil.readProtectedValue(protectedUrl, String.class)).toURI();
   return fileService.loadMyFile(fullPath);
}

@PostMapping("/upload")
public FileInfoURI uploadFile(@QueryParam("file") final VFile vFile) {
   final String fullPath = fileService.loadMyFile(fullPath);
   final String protectedPath = ProtectedValueUtil.generateProtectedValue(fullPath);
   return new FileInfoURI(new FileInfoDefinition("FiDummy", "none"), protectedPath);
}
```

## [Ui] How to pass parameter from page to page server-side? (via FlashAttribute?)
**Simplest: pass data via URL.**
Data can be *protected* with Vertigo utility `ProtectedValueUtil`.
Data security must be done on pages during data loading: showing identifier in URL is not a problem if security is properly applied.

**Server-side passing**
Simplest: parameter via session.
Alternatively, server-side *forward* with `ModelAndView`.

## [Vega] Why does `securityManager.getCurrentUserSession()` return empty Optional?
Abnormal; there should always be a UserSession.
Automatic. Important: io.vertigo.vega.impl.servlet.filter.SecurityFilter must be in web.xml.

```XML
<filter>
     <filter-name>Security Filter</filter-name>
     <filter-class>io.vertigo.vega.impl.servlet.filter.SecurityFilter</filter-class>
     <init-param>
         <param-name>url-exclude-pattern</param-name>
         <param-value>/static/*</param-value>
     </init-param>
     <init-param>
         <param-name>url-no-authentification</param-name>
         <param-value>/login;/login/*</param-value>
     </init-param>
</filter>
<filter-mapping>
     <filter-name>Security Filter</filter-name>
     <url-pattern>/*</url-pattern>
</filter-mapping>
```

! Parameter **url-exclude-pattern** disables the filter; only use on pages without Session (e.g., WebServices to other systems).

## [Ui] How to change landscape behavior of `vu:date` or `vu:datetime`?
Pass `landscape` attribute on `q-date` component.
Checking component (vertigo-ui/.../ date.html), default attributes go to `q-input` (since `input_attrs` is the last attrs parameter):

```XML
<th:block th:fragment="date-edit(object, field, label, format, date_attrs, input_attrs)" ... >
```

To set attribute on `q-date`, prefix with `date_`.
Since VueJs must *evaluate* the attribute, add `:`.
Example:
```
date_:landscape="'$q.screen.gt.md'"
```

## [Ui] How to make application multilingual?
**Note**: Applies to multilingual applications. Need to externalize messages should be considered (in general, keeping text in page is equally simple to modify and keeps context).
For multilingual application, handle multiple content types:
- Page-specific texts (titles, menus, ...)
- Field labels (associated to entity fields)
- Formatting rules (date/number format depends on language)
- Business rule messages
- User error messages
- Multilingual reference data
- Business data

These apply in different places with different approaches.

**Page-specific texts** use Thymeleaf syntax: `#{my.code}`; `.properties` files placed next to `.html` using them.

**Field labels** defined in model definition. Use Vertigo multilingual mechanism via LocalManager. Properties i18n files with field identifier as key.

**Formatting rules** defined in Quasar components.

**Business rule messages**: via UiMessageStack use Vertigo multilingual mechanism via LocalManager, or Spring MessageSource.

**User errors** via UserException; use Vertigo multilingual mechanism via LocalManager.

**Multilingual reference data**, implement in app. Several solutions:
- Multi-valued field (per language); possible with SmartTypeAdapter
- Field per language (labelFr, labelEs, labelEn, ...); add this dynamism to component attribute in page

**Business data**, implement in app. Data can be multilingual (multiple languages for same entity) or language-associated (one language per entity).

## [Search] How to preselect facets when user arrives on search screen?
Search component API takes parameter for selected facets. Initialize `SelectedFacetValues` object; use Builder.

Example:
```Java
final SelectedFacetValues initialSelectedFacetValues = SelectedFacetValues.empty()
     .add("FctEquipmentEquipmentTypeName", "building")
     .build();
```

## [Config] How to use a custom plugin for an existing manager (e.g., Quarto)?
Modules start sequentially. Feature configuration must be complete.
In YAML config, specify specific plugin classes:

Example:
```Yaml
modules:
  io.vertigo.core.node.config.yaml.YamlBioFeatures:
      features:
        - bio:
        - math:
            start: 100
      plugins:
        - io.vertigo.core.node.component.data.SimpleMathPlugin:
            factor: 20
```

Verify interface implemented by plugin; determines plugin type and injection into Manager.
Identifier is auto-calculated; multiple plugins get suffixes $1, $2, etc.

> At startup, if error indicates two components have same ID, the same plugin may be loaded in two modules.

!> **Warning**: notably project features often in autodiscovery; all components in a package are loaded (including custom plugins for other Managers). If so, move plugin to non-scanned package OR annotate with `@NotDiscoverable`.

## [Ui] How to add a VueJs component to my project
To add a VueJs component, use appropriate function on VueJs instance.

For correct timing, Vertigo provides an event:
```Javascript
window.addEventListener('vui-before-plugins', function(event) {
    let vuiApp = event.detail.vuiAppInstance;
    vuiApp.component('v-my-component', MyComponent);
});
```
> Can also register directives (`vuiApp.directive(...)`)

Build component in `.vue` file, build with vite, webpack, etc. in `umd` format.
Or create in JavaScript file via `Vue.defineComponent`.

Example:
```Javascript
const MyComponent = Vue.defineComponent({
  name: 'MyComponent',
  props: {
    message: { type: String, required: true },
    initialCounter: { type: Number, default: 0 },
  },
  data() { return { counter: this.initialCounter }; },
  methods: {
    increment() { this.counter++; },
    decrement() { if (this.counter > 0) { this.counter--; } },
  },
  template: `<div><h1>{{ message }}</h1><p>Counter: {{ counter }}</p><button @click="increment">+</button><button @click="decrement">-</button></div>`,
});
```

## [List] How to disable client-side pagination for a list?
Underlying component uses Quasar component.
Per API documentation (https://quasar.dev/vue-components/table#qtable-api), set rows per page to 0:
```HTML
<vu:table ... myRowsPerPage="0" ...>
```

## [List] Internal Server Error (500) with too many list elements, what to do?

During standard list render, entire list from viewContext is displayed.
To protect system, limit list size already in query service.

Server-side limit changes client-side list behavior since navigation operations must go server-side: (sort, filter, ...)
*Note: Pagination can stay client-side, as it shows first X elements for a given sort.*
*Cannot offer all results via pagination; databases cannot efficiently retrieve data from distant pages.*

You'll likely need an object for filtering: dropdown, search prefix, dates, etc.
For sort and pagination criteria, Vertigo provides `DtListState`.

Steps:

Service-side, complete query with dtListState:
```Java
public DtList<Document> getAuthorizedDocuments(final DocumentFilter documentFilter, final DtListState dtListState) {
  final Criteria<Document> securityCriteria = authorizationManager.getCriteriaSecurity(Document.class, DocumentOperations.readDocument);
  final Criteria<Document> documentCriteria = Criterions.isEqualTo(DocumentFields.documentTypeId, DocumentTypeEnum.document.getEntityUID().getId())
    .and(Criterions.startsWith(DocumentFields.name, documentFilter.getNamePrefix()));
  return documentDAO.findAll(securityCriteria.and(documentCriteria), dtListState);
}
```

Controller: modify initContext to add filter and limited list loading.
Add reload WebService applying filter and sort (initContext reuses this method):
```Java
@GetMapping("/")
public void initContext(final ViewContext viewContext, final UiMessageStack uiMessageStack) {
  final DocumentFilter documentFilter = new DocumentFilter();
  viewContext.publishDto(documentFilterKey, documentFilter);
  reload(documentFilter, DtListState.of(MAX_ELEMENTS, 0, DocumentFields.name.name(), false), viewContext, uiMessageStack);
}

@PostMapping("/_reload")
public ViewContext reload(@ViewAttribute("documentFilter") final DocumentFilter documentFilter, final DtListState dtListState, final ViewContext viewContext, final UiMessageStack uiMessageStack) {
  final DtList<Document> documents = documentsServices.getAuthorizedDocuments(documentFilter, dtListState.withDefault(MAX_ELEMENTS, TemplateFields.name, false));
  if (documents.size() >= MAX_ELEMENTS) {
    uiMessageStack.info("List shows only first " + MAX_ELEMENTS + " elements, refine your filter.");
  }
  viewContext.publishDtList(documentsKey, documents);
  return viewContext;
}
```

Page: add filter and activate server-side sort on table with `sortUrl` on `vu:table`.
Example: `sortUrl="@{_reload}"`

Reload list on filter change with VueJs `$watch`:
```Javascript
VUiPage.$watch('vueData.documentFilter', Quasar.debounce(
    (newValue, oldValue) => { VUiPage.httpPostAjax('_reload', VUiPage.vueDataParams(['documentFilter']))}, 500
    ), { deep: true });
```

*Note: Example in UI training (https://github.com/vertigo-io/vertigo-university/blob/master/sample-vertigo-ui-full/Level2.4.md#Detail screen - Server-side sort)*
*Note2: Total row count can be shown in table header. Total stored in list as metadata: `list.setMetaData(DtList.TOTAL_COUNT_META, service.countByCriteria(filter));`*

## [Ui] How to change active table page when criteria change?
If page offers Ajax list refresh and user changed active page, current page may exceed max pages after update.
When refreshing paginated list via Ajax, return to first page on criteria change.
Modify `pagination` object in component state on `onSuccess`.

Example:
```Javascript
httpPostAjax('_reload', ['myCriteria'], {
    onSuccess: function() {
        this.$data.componentStates.myTableRef.pagination.page = 0;
    }
}.bind(this)
})
```

Reminder: to react to criteria changes, use `watch` on criteria object:
```Javascript
VUiPage.$watch('vueData.fileCriteria', () => reload('file'), { deep: true });
```

## [Database] How to easily access my environment database?
Security awareness: in defense-in-depth, database should not be directly accessible.
However, during debugging phases and depending on project context, it can be useful.

In configuration.yaml, add manager to launch H2 console (test database with JDBC client):
```yaml
  io.vertigo.mars.support.SupportFeatures:
    features:
      - h2Console:
          __flags__: ["devMode"]
```

In SupportFeatures:
```java
@Feature("h2Console")
public SupportFeatures withH2Console(final Param... params) {
    getModuleConfigBuilder().addComponent(H2ConsoleManager.class, params);
    return this;
}
```

H2ConsoleManager:
```java
import org.h2.tools.Console;

public final class H2ConsoleManager implements Component, Activeable {
    private final Console console = new Console();
    private final String[] args;
    @Inject
    public H2ConsoleManager(@ParamValue("args") final Optional<String> argsOpt) {
        args = argsOpt.map(cmdArgs -> cmdArgs.split("\\|")).orElseGet(() -> new String[] { "-web" });
    }
    @Override
    public void start() {
        try { console.runTool(args); }
        catch (final SQLException e) { throw WrappedException.wrap(e); }
    }
    @Override
    public void stop() { console.shutdown(); }
}
```

Console starts at startup, accessible via URL in log:
`Web Console server running at http://127.0.0.1:8082?key=0103....bf8a (only local connections)`

Configure connection using JDBC URL info for easy database access.

## [Search] How to create facet from tag list in object?

*Note: Example in Mars demo for equipment facet by tags ([mars](https://github.com/vertigo-io/vertigo-mars/))*

Start with index column containing tag list with separator.
Use term facet: values based on index values.
As term facet, build on unmodified input value using keyword mode.
For multiple values, use separator: pipe `|` (not legitimate punctuation).

Special analyzer in elasticsearch configuration:

`elasticsearch.yaml`
```yaml
index:
    analysis:
        normalizer:
            code:
                type: custom
        analyzer:
            multiple_code:
                tokenizer: piped_keywords
                filter: []
        tokenizer:
            piped_keywords:
                type: pattern
                pattern: '([|,;]*)'
```

Adapted smartype using this analyzer:
`MarsSmartTypes.java`
```Java
@SmartTypeDefinition(String.class)
@Formatter(clazz = FormatterDefault.class)
@SmartTypeProperty(property = "storeType", value = "TEXT")
@SmartTypeProperty(property = "indexType", value = "multiple_code:facetable")
Tags,
```

In search ksp, add field:
`searchEquipment.ksp`
```Javascript
create DtDefinition DtEquipmentIndex {
    ...
    field tags {domain: DoTags, label: "Tags"}
    ...
}
```

Complete search query to concatenate:
`searchTasks.ksp`
```SQL
SELECT
    equ.EQUIPMENT_ID,
    ...
    COALESCE(t.TAG_LIST, '') as TAGS,
    ...
FROM EQUIPMENT equ
JOIN BASE bas on bas.base_id = equ.base_id
LEFT JOIN LATERAL (
    SELECT STRING_AGG(tg.LABEL, '|') as TAG_LIST
    FROM TAGS tg
    WHERE tg.EQUIPMENT_ID = equ.EQUIPMENT_ID
) t ON true
WHERE equ.EQUIPMENT_ID in (#equipmentIds.rownum#);
```
*Note: LATERAL used for PostgreSQL performance*

Facet is automatic.
ElasticSearch splits tag column values by `|`. Uppercase and spaces preserved.
Automatically populates facet with values.