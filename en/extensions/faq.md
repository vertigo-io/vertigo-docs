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

## [Ui] Part of my page disappears, or a `v-if` applies to too many elements
Check that no Vue/Quasar component is self-closed: never write `<q-btn ... />` in a vertigo-ui page, always close explicitly `<q-btn ...></q-btn>`.
In HTML5, self-closing does not exist for non-void elements: the browser ignores the `/` and treats the tag as a plain opening tag. All following content then becomes a child of the component: a `v-if` extends its scope, whole blocks disappear (swallowed as the component's slot).
The cause is the browser's *in-DOM* template parsing (see Vue doc "DOM Template Parsing Caveats": self-closing is only valid in SFCs).
Server-side processed tags (`th:*`, `vu:*`) are not affected: they are expanded by Thymeleaf before reaching the browser. Self-closing thus remains fine for `th:block`, `vu:*` components and HTML void elements (`<br>`, `<img>`, ...).

?> Starting with vertigo-ui 4.5.0, self-closed tags are automatically closed at render time. The legacy `UnAutoCloseTagsFilter` servlet filter (declared in web.xml) is deprecated, then removed in 5.0.0: its regex-based repair was partial — it misses any tag holding a `>` inside an attribute value (e.g. `:disable="[1,2].length > 5"`) and only knows the `q-*`/`v-*` prefixes.

## [Ui] How to edit my Thymeleaf pages without restarting the server?
Spring Boot's `spring.thymeleaf.cache=false` has no effect in vertigo-ui: template caching is driven by the `isDevMode()` method of `VSpringWebConfig` (`setCacheable(!isDevMode())`).
`isDevMode()` returns `true` by default (cache disabled): it is the project's override in its `VSpringWebConfig` that enables the cache in production. In dev, simply do not override `isDevMode()` to `false`.
Also disable auto-reload of the web module in Eclipse's Tomcat, otherwise every resource change restarts the webapp.

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

Common pitfall: publishing the data (`publishDto`, `publishMdl`, ...) is not enough — a mustache expression `{{...}}` or a purely client-side binding (`:color`, `openModal(...)`, building a link) shows "undefined" if no `vu:` component actually renders that field. Include it explicitly with `<vu:include-data .../>`. Invisible pitfall in HTTP/curl testing: the symptom only shows in a real browser.

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

UI-side: display certain buttons when items selected with `v-if="componentStates.equipmentsTable.selected.length > 0"`

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

## [Core] How to run an asynchronous or recurring task?
Two mechanisms depending on the need:
- `@DaemonScheduled(name = "DmnMyTask", periodInSeconds = 60)` (io.vertigo.core.daemon) for non-vital recurring technical tasks (purge, cache refresh, ...). Simple, but no recovery nor monitoring: a missed run is lost;
- **Orchestra** for critical business jobs: scheduling, execution tracking in database, error recovery, multi-node.

!> Creating your own `ExecutorService` is an anti-pattern: threads escape the node lifecycle (clean shutdown, supervision) and transactions.

## [Core] How do Aspects work (and why doesn't mine apply)?
Aspects are **global**: they apply to all components of the node, there is no per-module scoping.
Loading order matters though: an aspect must be declared in a module loaded **before** the modules of the components using it (and within a single module, components are registered before aspects). Declared too late, the aspect does not apply to already-loaded components.
Another limit: the aspect is carried by a **proxy** (javassist subclass) delegating to the real instance. It therefore only applies to calls going through the injected reference of the component: an **internal call** (`this.myMethod()`, or an implicit call between two methods of the same class) does not trigger the aspect. And only **public** methods are intercepted — never private ones.
To benefit from an aspect (e.g. `@Transactional`) on a sub-process, either put the annotation on the public entry method, or move the sub-process to another injected component.
?> `@Transactional` is an aspect like any other, with REQUIRED semantics: it joins the current transaction if there is one, otherwise creates one.

## [Studio] Double association in .ksp to same DtObject generates two methods with same name
Give each association a role (`roleA` and `roleB`); this role names the navigation accessor.
In KSP, an association is declared with `roleA`/`roleB`, `labelA`/`labelB` and `fkFieldName` (mandatory, lowerCamelCase); the shortcut `type : "*>1"` carries cardinalities and navigability:

```
create Association ADosUtiDestinataire {
	fkFieldName : "utiIdDestinataire"
	dtDefinitionA : DtDossier
	type : "*>1"
	dtDefinitionB : DtUtilisateur
	roleA : "Dossier"
	labelA : "Dossier"
	roleB : "Destinataire"
	labelB : "Destinataire"
}
```

The role names the generated accessor: here `dossier.destinataire()`, which returns a `StoreVAccessor` (`StoreListVAccessor` on the multiple side), used through `.load()` then `.get()`.
In XMI/OOM modeling, the FK suffix comes from the association name (see the Enterprise Architect entry below); this suffix is mandatory for a self-join (otherwise an "AutoJointure" exception).

?> Special case: a reflexive NN association (entity linked to itself) is impossible by construction — the join table columns are the PKs of both nodes (no `fkFieldName` for NN), so there would be two columns with the same name. Workarounds: a carrying entity (own PK + 2 FKs) or a JSON column.

## [Studio] How to set field names, labels and foreign keys in Enterprise Architect (XMI)?
At **attribute** level: the *Name* becomes the column code and the *Alias* the business label (used in error messages, among others).
At **association** level: the *Role* becomes the navigation accessor name (the role's *Alias* is not read).
The FK column name is derived from the target PK plus a suffix extracted from the **association name**, in the `{TriA}{TriB}{Suffix}` format: an association named `DosUtiDestinataire` between DOSSIER and UTILISATEUR generates the FK `UTI_ID_DESTINATAIRE`.
The loader's `constFieldName` parameter still exists (default `true`: the model is expected in CONST_CASE).

## [Studio] How to share DTOs between several projects (common module)?
Definitions generated by Studio in the shared module (`DtDefinitions` class + SmartTypes) are declared on the consumer side through a `DefinitionProviderConfig`:
```java
getModuleConfigBuilder()
	.addDefinitionProvider(DefinitionProviderConfig.builder(ModelDefinitionProvider.class)
		.addDefinitionResource("smarttypes", "commons.domain.CommonsSmartTypes")
		.addDefinitionResource("dtobjects", "commons.domain.DtDefinitions")
		.build());
```
!> YAML configuration cannot declare definition resources: this code must live in a Java `Features` class (the shared module's), itself referenced in the consuming project's YAML.

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

## [DataStore] My large reference list is not cached (compression limit)
The cache serializes and compresses elements by default, with a maximum size of **20 MB** after serialization (`CompressionCodec.MAX_SIZE_FOR_COMPRESSION`): beyond that, caching fails.
For large unmodifiable lists, disable serialization by setting the `serializeElements` parameter of the `CacheDefinition` to `false`: the list is then kept as-is in memory (careful: objects are then shared, they must not be modified).

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

## [Vega] A computed field of my entity does not appear in the JSON of my WebService
This is nominal behavior: Vega serialization (Gson + `DtObjectJsonAdapter`) iterates over the fields of the entity definition and **explicitly excludes `computed` fields** (it does add loaded accessors, though). An ad hoc Java getter is never serialized either: only definition fields count. Deserialization applies the same filter: a `computed` field sent in the incoming JSON is ignored.
Solution: declare the field in the model as a **non-persistent** field and fill it via the Task SQL or in the service — being part of the definition, it is serialized normally.

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

## [DataStore] I get the error "Accessor is not loaded, you must load it before calling get method"
Navigation accessors (`StoreVAccessor` / `StoreListVAccessor`) never load anything automatically: you must explicitly call `load()` before `get()`.
```java
dossier.destinataire().load();
final Utilisateur destinataire = dossier.destinataire().get();
```
`load()` performs a SQL access: it must therefore run **inside a `@Transactional` service** — the controller then only publishes the loaded entity into the ViewContext.
Escape hatches:
- `loadIfAbsent()`: only loads if the accessor is not loaded yet (useful in a service reached through several paths);
- `lazyGet()`: performs the `load()` if needed, but is marked `@deprecated` since its addition (4.3.0) — a transition helper, do not generalize it.

## [DataStore] How to load an entity with all its associations (JPA-style fetch join)?
There is no equivalent, and it is a deliberate choice: loading object graphs is a classic source of performance problems (uncontrolled loads, N+1) and makes service costs hard to reason about. Vertigo requires loading explicitly what the process needs.
Three patterns depending on the case:
1. **Display list**: a dedicated DTO filled in one query by a SELECT with ad hoc joins (Task);
2. **Business processing**: two queries — the main entities, then their children via a `WHERE IN`;
3. **Search index**: a single query with `GROUP BY` + `string_agg` to flatten sub-entities (see the entry about the facet from a tag list).

## [DataStore] How to insert a large number of entities efficiently (and get the generated keys back)?
`DAO.createList(DtList<E>)` inserts in batch (engine `TaskEngineInsertBatch`) **and** sets the generated keys back on the entities: after the call, each element of the list carries its PK.
For a parent/child graph inserted in a custom Task, it remains possible to pre-draw sequence values in bulk (`SELECT nextval(...)`) to assign parent PKs and fill children FKs before the two batch inserts.

## [DataStore] How to handle a unique constraint with a proper user message?
The constraint is set in SQL:
```sql
ALTER TABLE UTILISATEUR ADD CONSTRAINT UNQ_UTILISATEUR_EMAIL UNIQUE (EMAIL);
```
On violation, Vertigo (`AbstractSqlExceptionHandler`, wired for H2, Oracle, PostgreSQL and SQL Server) translates the SQL exception into a `VUserException` using **the constraint name as the message key**.
Simply declare a resource with that key (`UNQ_UTILISATEUR_EMAIL=This email is already in use`); otherwise the generic message (`DYNAMO_SQL_CONSTRAINT_ALREADY_REGISTERED`) is shown.

## [DataStore] How to guarantee an element is not processed by two concurrent treatments?
Use `EntityStoreManager.readOneForUpdate(uid)` (or the DAO's `getForUpdate`): a `SELECT ... FOR UPDATE` is generated according to the database dialect (SQL Server: `WITH (UPDLOCK, INDEX(PK_...))`). The lock is set on the row and released at transaction commit or rollback.
!> Do not rely on `synchronized`: a JVM lock does not protect in multi-node deployments. The database lock is the only synchronization point shared by all nodes.

## [Transaction] How to perform a write that survives a rollback (logging, audit trail)?
`VTransactionManager.createAutonomousTransaction()` (vertigo-commons) opens a transaction independent from the current one:
```java
try (VTransactionWritable tx = transactionManager.createAutonomousTransaction()) {
	journalDAO.create(journal);
	tx.commit();
}
```
It is committed even if the enclosing transaction is later rolled back — typical use case: logging a failed attempt.
Conversely, to trigger an action only if the main transaction succeeds, use `VTransaction.addAfterCompletion(...)`: the `afterCompletion(boolean txCommitted)` callback lets you test the transaction outcome.

## [DataStore] Why can't a VFile be created directly from an InputStream?
Because a `VFile` is a **lazy stream provider**: the stream must be (re)creatable on demand, and the consumer opens and closes it (HTTP sending, storage, ...). An already-open `InputStream` can only be read once and raises the question of who closes it.
The factories reflect this principle:
- `FSFile.of(path)` for a file present on the filesystem;
- `StreamFile.of(...)` which takes a `DataStream` (io.vertigo.core.lang), i.e. a lambda able to open a new stream on each call: `() -> new ByteArrayInputStream(bytes)` for instance.

## [DataStore] Berkeley (KVStore): how is data purged, and why are my writes refused (DiskLimitException)?
Expired elements are purged by a dedicated daemon running every 60 s. TTL is defined **per collection** in the plugin's `collections` parameter: `myCollection;TTL=3600` (seconds; `;inMemory` possible; default -1 = eternal). The `purgeVersion` parameter (V1/V2/V3, default V3) selects the purge algorithm.
Disk-wise, Berkeley requires **at least 1 GB of free disk space** (`je.freeDisk` threshold, hard-coded, not configurable): below this threshold, any write is refused with a `DiskLimitException`. Plan for it in sizing — all the more since Berkeley files never shrink: space freed by the purge is reused, not returned to the filesystem.

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
   final String fullPath = fileService.saveMyFile(vFile);
   final String protectedPath = ProtectedValueUtil.generateProtectedValue(fullPath);
   return new FileInfoURI(new FileInfoDefinition("FiDummy", "none"), protectedPath);
}
```

## [Ui] How to display a PDF generated after a form POST?
Simple case first: if the page does not need to be updated (no vueData refresh, no error messages to display), a POST controller can return the `VFile` directly. Vertigo-ui sends it with `Content-Disposition: attachment` (`VFileReturnValueHandler`): the browser stays on the page and offers the download.
The real issue comes with **Ajax** POSTs — the usual mode of vertigo-ui screens, required as soon as you need to update the vueData or display input errors: an XHR response is not "displayed" by the browser, a binary received through Ajax triggers neither a download nor a document opening. Same constraint to open the PDF in a **new tab**: a GET URL is needed.
In those cases, the pattern is two-step, fully tooled by vertigo-ui:
1. the POST generates the PDF, stores it temporarily and returns a `FileInfoURI`: returned by a SpringMVC controller, it automatically goes to the client as a **protected** value, and is resolved back when it comes in as a parameter;
2. the client triggers a GET with that value; the controller returns a `VFile`, sent with `Content-Disposition: attachment`.

For temporary storage, use the `filestore.fullFilesystem` feature (`FsFullFileStorePlugin`): the full file (content + metadata) goes to the filesystem, and the `purgeDelayMinutes` parameter enables a daemon purging obsolete files.

?> Value protection relies on `ProtectedValueUtil` (vertigo-ui), which requires a KVStore with a `protected-value` collection.

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

## [Search] How to filter on a list of values (12 OR 13 OR ...)?
Declare a grouped criterion in the search DSL, e.g. `+PRO_ID:(#proIds#)`, and pass the values separated by **spaces** (`"12 13"`): inside a group, a space means **OR**.
- For an **AND** (all terms mandatory), prefix the field in the reference: `+PRO_ID:(#+proIds#)`;
- an empty or `null` criterion field generates **no filter**: the block is ignored, no need to build the query dynamically;
- a separator glued to the criterion text is not re-tokenized: this is intended, to search codes, IP addresses, etc. as-is.

## [Search] How to sort search results on several fields?
Sorting is driven by `DtListState`: a single `sortFieldName` and a single direction. The ElasticSearch plugin does split the field name on commas though: `"lastName,firstName"` sorts on both fields, with the **same direction** for all.
To favor recent documents without imposing a strict sort, prefer the relevance boost on the `SearchQuery` builder: `withDateBoost(dateField, numDaysOfBoostRef, mostRecentBoost)`.
For a real multi-column sort with different directions, sort in SQL in a Task (outside full-text search).

## [Search] How to sort a facet in descending order?
Facet orders (`FacetOrder`) are `alpha`, `count` (default for term facets) and `definition` (default for range facets) — there is no descending order.
The solution is a **range** facet: the `definition` order renders ranges in declaration order, so declare them from most recent to oldest. Relative bounds use ElasticSearch date-math, in **lowercase**: `now-1y`, `now-10y`, ...

## [Search] When is the index updated after a create/update/delete?
Indexing is triggered **at transaction commit**, never before: the store event is posted in an `addAfterCompletion` guarded by `if (txCommitted)`.
Consequences:
- a rollback indexes nothing: the index stays consistent with the database;
- rolled-back transactional tests do not pollute the index;
- within the current transaction, a search does not yet see the in-flight changes.

## [Search] Can I index a nested structure in my index?
No: the mapping generated by Vertigo is **flat**, no `nested` or `object` type can be declared. The index is meant to find documents, not to carry the relational model.
Two approaches:
- flat **multi-valued** field: ElasticSearch natively accepts arrays of values (see the entry about the facet from a tag list);
- **denormalization**: if sub-entities must be searched individually, create one index document per sub-entity.

## [Search] How to search across several entity types?
Create a dedicated index aggregating the different entities into a single "generic" index document:
- a supporting KeyConcept and a specific `SearchLoader` loading and transforming each entity type;
- a document id built as a URN (type + id) to find the original entity back;
- a "type" facet to filter by entity type.
Alternative: one search per index, then merge results with `FacetedQueryResultMerger`.

## [Search] How to do a "contains" search (substring)?
A SmartType's `indexType` carries only **one analyzer** (syntax `myAnalyzer{:type}{:stored}{:sortable}{:facetable}`): there is no separate `search_analyzer`. An edgeNGram analyzer would therefore also apply to the typed query (noise); a full nGram is discouraged anyway (huge index).
In practice:
- for a "starts with", use the wildcard in the DSL: `#query*#`;
- for a real business "contains", build a computed field in the SearchLoader with an appropriate splitting (business tokens), rather than relying on the analyzer.

## [Search] How to index the content of a file (PDF, Word, ...)?
Vertigo only ships `tika-core` (MIME type detection): add the **`tika-parsers`** dependency to the project, then extract the text with Tika in the `SearchLoader` when building the index document.
Declare the field as `notStored`: the extracted text is used for searching but does not need to be returned nor to inflate index storage.

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

## [Task] How to process a very large table without exhausting memory?
There is no cursor or stream API (`SqlManager.executeQuery` returns a list bounded by a limit). The pattern is **keyset pagination**: process in batches, restarting from the last id read.
```sql
SELECT ...
FROM MY_TABLE
WHERE MY_TABLE_ID > #lastId#
ORDER BY MY_TABLE_ID ASC
```
with a batch limit, looping while the returned list is not empty (the last id read becomes the next batch's bound).
Unlike an OFFSET, this traversal is stable if data changes and stays fast (index scan). For bulk writing, use `TaskEngineProcBatch`.

## [Task] Can SQL be factored between several KSP Tasks (include)?
No, there is no include mechanism in KSP files. Two workarounds:
- a **specific TaskEngine** building the common SQL part in Java;
- passing the SQL fragment as a Task **parameter** with the `<%= myFragment %>` syntax (injected as-is into the query: reserve it for SQL produced by code, never for user input).

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

## [Search] The SQL concatenation of my multi-valued fields exceeds database limits
When `string_agg`/`LISTAGG` reaches its limits (maximum size, SQL readability), move the assembly to Java: `SearchLoader.loadData(SearchChunk)` is where index documents are built — load the chunk's sub-entities and build the string (or the multi-valued field) there.

## [DataStore] Should my authentication (credential) entity be a reference list?
No. Never declare the credential entity in a `MasterDataDefinitionProvider`: it breaks authentication (login fails silently, empty response or 404).
Keep this entity out of reference data.

## [Orchestra] An Orchestra activity goes to ABORTED even though the code did not fail
**Symptom**: The activity ends with `status: "ok"` in the workspace, but its state in the database is `ABORTED`. Error message: `DbProcessExecutorPlugin - Error in activity state, activity execution N is already terminated`.

**Cause**: A long-running daemon (>60s) blocks the shared daemon thread pool (2 threads default). The orchestra daemon heartbeat is no longer updated, and another node considers this node dead.

**Solutions**:
1. Find your long-running daemons (>60s) via the analytics dashboard (`/dashboard`, `poolUtilization` healthcheck)
2. If necessary, increase `threadPoolSize` in `boot.params` of `configuration.yaml` (minimum 4 recommended)
3. Move very long-running tasks out of the daemon pool (execute in a dedicated thread)

## [Config] Liquibase: checksum error at startup after a regeneration
Liquibase stores the **md5sum** of each applied `changeSet` and compares it at every startup.
Never reference a regenerable file (studio generation output, `javagen/sqlgen/…`): as soon as it changes, any already-migrated database refuses to start (*checksum mismatch*).
Copy the creation script to a **frozen**, versioned folder (e.g. `src/main/resources/sql/`), and never modify an already-delivered `changeSet` (create a new one instead).

## [Config] Must some features be enabled even if I don't use them directly?
Yes, whenever a component you use injects a manager in a non-optional way.
For example, the generic autocomplete controller (`io.vertigo.ui.controllers.ListAutocompleteController`) injects `CollectionsManager`: the `dataFactory` feature (bare, without an index plugin) is therefore required as soon as a `vu:autocomplete` is present, without pulling in Lucene or Elasticsearch.
Likewise, storing *Account* via the *StoreManager* (`account.store.store`) injects a non-optional `FileStoreManager`: the `filestore` feature (bare) is required even without file management.


## [Security] How to prevent two simultaneous sessions with the same login?
Nothing native in Vertigo. Application pattern: keep a `ConcurrentHashMap<String, UserSession>` login → session in a component; on login, invalidate (`logout()`) the previous session of the same login before registering the new one.
!> In multi-node deployments, this map is local to each JVM: you need session affinity, or to externalize this state (database, shared cache) for the rule to be global.

## [Security] How to set up Windows SSO (user does not type a password)?
Favor standard protocols, natively tooled in vertigo-vega: `OIDCWebAuthenticationPlugin`, `AzureAdWebAuthenticationPlugin` and `SAML2WebAuthenticationPlugin` (features `authentication.oidc`, `authentication.aad`, `authentication.saml2`). With an AD / Entra ID directory, OIDC or SAML2 provides SSO with nothing to handle on the application side.
For pure legacy intranet (no IdP available): Kerberos/SPNEGO handled by a front-end (Apache/IIS) or by Tomcat (`tomcatAuthentication="false"` on the AJP connector), then retrieve the identity via `request.getRemoteUser()` in the authentication plugin. NTLM is deprecated by Microsoft: do not build on it.

## [Config] Intermittent disconnections from the database or ElasticSearch (after a period of inactivity)
Classic cause: a firewall between the application and the database/ES drops idle TCP connections (often after 10-20 min), while the OS default TCP keepalive is 2 h — the dead connection is only detected on the next use.
Symptoms: IO errors / HTTP `ConnectException` with the ElasticSearch REST client; `NoNodeAvailableException` with the legacy TransportClient (`elasticsearch_7_17` connector); JDBC errors on invalid connections.
Remedies:
- lower the OS TCP keepalive below the firewall's idle timeout;
- PostgreSQL: `tcp_keepalives_idle = 600` on the server;
- enable connection validation on borrow in the JDBC pool.

## [Config] An audit requires the database password not to be stored in plaintext — what are the options?
First, a reminder: the password does not live in the versioned YAML anyway — it is environment-dependent and resolved by the paramManager from the host's configuration (external properties file, environment variables via `EnvParamPlugin`).
If the requirement is "not in plaintext on the server's disk", the options depend on the deployment:
- the robust answer, valid everywhere: **certificate** authentication (no password at all), supported by most DBMS; or a secrets vault on the hosting side injecting the environment variable at startup;
- with a **Tomcat + JNDI** deployment (`DataSourceConnectionProviderPlugin`, params `classname` and `source`): the connection configuration lives in Tomcat's `context.xml`, and an overridden `DataSourceFactory` can decode an encoded password;
- with **embedded Jetty** (the standard vertigo-ui mode), there is no JNDI: the password comes through the external configuration. Encoding the file with a key sitting on the same machine is only obfuscation — to be acknowledged as such if the audit accepts it.

?> Worth keeping in mind to frame the discussion with the auditor: as soon as the application boots unattended, everything needed to connect is reachable from the machine — none of these mechanisms resists a compromise of the machine itself. Their value lies elsewhere: preventing configuration-file leaks (backups, tickets, shares — a plaintext password can be copy-pasted and reused, a certificate cannot), and limiting the blast radius through rotation, short-lived credentials and revocation.

## [Config] How to run a Vertigo batch from the command line (outside a webapp)?
A Vertigo node starts without a web server using `AutoCloseableNode` (io.vertigo.core.node):
```java
try (AutoCloseableNode node = new AutoCloseableNode(nodeConfig)) {
	final MyBatchServices batchServices = Node.getNode().getComponentSpace().resolve(MyBatchServices.class);
	batchServices.run(...);
}
```
YAML configuration is loaded via `YamlNodeConfigBuilder`. Package the batch as a Maven fat-jar and use picocli for command-line argument parsing.
?> For recurring scheduled processing, prefer Orchestra over an external cron: execution tracking, recovery, and execution hosted by the existing webapp.

## [Config] What convention for naming loggers?
By default, one logger per class (`LogManager.getLogger(MyClass.class)`).
Vertigo additionally uses **transverse categories** for technical concerns: `sql` (SQL queries), `tasks` (Task execution), `health`, `metric`. They are driven directly in the log4j2 configuration (e.g. set `sql` to DEBUG to trace queries).
?> The analytics plugin `SmartLoggerAnalyticsConnectorPlugin` logs by category and switches to ERROR beyond the `durationThreshold` threshold (1000 ms by default) — handy to spot slow processing without flooding the logs.
