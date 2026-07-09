# from 4.4.x to 5.0.0

* **[Core] Upgrade to JDK25**. Update your `pom.xml` source/target and IDE settings.
* **[Vega] ContentSecurityPolicyFilter ${..} are now resolved by the paramManager. Old syntax must be updated :**
  - `${cspFrameAncestor}` => `${CSP_FRAME_ANCESTOR}`
  - `${cspParam1}` => `${CSP_PARAM1}`
  - `${cspParam2}` => `${CSP_PARAM2}`
  - `${cspParam3}` => `${CSP_PARAM3}`

# from 4.3.2 to 4.4.0

* **[DataFactory] Upgrade Search plugin to ElasticSearch v9** (ES7/ES8 plugins available in vertigo-lts-libs)
  - `EmbeddedServer` removed — use testcontainer for tests
  - `_all` field removed from index mapping
  - `markToOptimize` only applies to deletes (removeByQuery)
* **[DataFactory] Remove deprecated `searchManager.findIndexDefinitionByKeyConcept`** — you must use `findFirstIndexDefinitionByKeyConcept` instead
* **[Ui] Reset componentStates each request.** If you relied on component states persisting across multiple requests within the same context, you must manage them explicitly.
* **[Redis] `RedisSingleConnector` deprecated** — no longer supports Sentinel configuration. If you use Sentinel, switch to the `withJedisSentineled` connector.
* [Ui] Remove specific css rules from vertigo-ui.css affecting projects that uses quasar components and dsfr css (more detail, see https://github.com/vertigo-io/vertigo-libs/commit/1e4d857028171a81c02f26bd1b280fe6c9b383f0)
* **[Ui][DSFR] `dsfr.icons4quasar.js` updated for DSFR 1.14.4**. 21 icon names changed (RemixIcon → DSFR native SVG). If you have a custom icon mapping extending the default, check the [diff](https://github.com/vertigo-io/vertigo-libs/commit/131aa8d536) for updated names. 41 icons remain unchanged.

# from 4.3.1 to 4.3.2

* [Vega] JsonEngine `fromJson` with String in first parameter now need extra parameters. Add `, Collections.emptySet(), Collections.emptySet()` to keep old behavior.

# from 4.3.0 to 4.3.1

This is a version with multiple fix and added features.. only few changes..
* **[Ui-vuejs] i18n API changed from string key to object navigation**. If you use `this.i18n()` in custom JS/Vue code:

Before:
```javascript
this.i18n('uploader.progress')
```

After:
```javascript
$vui.i18n().uploader.progress
```

* **[Studio] Fix name multiSelectable in FacetDefinition** (multi**s**electable before)
* [Ui][Quasar] Add Reactive components for select, text-field and text-editor (use th:with="reactive=true")
You may need it, if you have some input component in table. It force a `vue-js client side` reactive version.
* [Ui] Update Spring 6.2.5 -> 6.2.8. You may update your versions, if using other spring modules (like spring-test)

# from 4.2.0 to 4.3.0

[**Renaming tool**](https://raw.githubusercontent.com/vertigo-io/vertigo-tools/master/migration-tools/update-renaming-tool.xml) _(beta)_<br/>

* **[DataModel] Package renamed `io.vertigo.datamodel.structure.*` → `io.vertigo.datamodel.data.*`**. Update your imports:
* **[DataModel] `Criteria`, `Task`, and property-related classes moved to DataFactory** module. Update your pom.xml if you import these classes directly (they're no longer in vertigo-datamodel).
* **[Core] Renamed `MessageKey` to `LocaleMessageKey`**. Update your imports and class references.
* **[Planning] vueData date format changed to ISO (yyyy-MM-dd).** If you have custom JS handling Planning dates, update your parsers.
* **[Ui] `vu:page` attributes moved to `vu:head` : `vuiDevMode`, `vuejsDevMode`, `quasarVersion`, `vertigoUiVersion`**
* **[Ui] Default format for date is now iso: `YYYY-MM-DD`. You may change some of your js code. If needed you can include data formatted with suffix `_fmt`**

Example: 
```Javascript
<vu:include-data object="agendaRange" field="firstDate" />
<vu:include-data object="agendaRange" field="firstDate_fmt" />		                      
```

* **[DataFactory] Elastic *deprecated* Transport protocol renamed maven artifact from `transport` to `x-pack-transport`**
* [commons] `Base64Codec` renamed to `Base64UrlCodec` (and add `Base64LegacyCodec` if needed)
* [Ui] Remove `UiRequestUtil.removeCurrentUiMessageStack`, you may use `UiRequestUtil.setCurrentUiMessageStack(new VSpringMvcUiMessageStack());` instead
* [Ui] `vu:messages-dsfr` renamed to `vu:dsfr-messages`
* [Ui] when using SSR, `vu:head` needs the `vuiSsr` attribute to the same value as `<vu:page>`
* [Ui] Add wysiwyg editor based on tiptap (**quasar editor is renamed from `vu:text-editor` to `vu:q-text-editor`**, you may rename it in your pages if using it)
* [Ui] usage of `v-modal` class for dialog, make the dialog to be fullscreen and may broke your layout
* [Ui] `vu:page` slot `libraries_slot` no longer exists, move your declarations to your `<head>`
If your script need `Quasar` (check browser console), you should could use an event to wait libs to load.
Example for iconSet :
```JavaScript
window.addEventListener('vui-before-plugins', function(event) {
    Quasar.iconSet.set( { /** all icon set data **/ });
});
```
* [Ui] When we added dsfr components, we moved legacy ui components to `io/vertigo/ui/components/quasar/` base path. You may have use this path, if you declared ResourceBundleMessageSource basenames. (then replace `"io/vertigo/ui/components/` by `"io/vertigo/ui/components/quasar/`)
* [Ui] Quasar js file is now included with defer attribute, you may need to listen for vui events to trigger your code after vue initialization (eg: using `Quasar.dom.ready` method)
* [Vega][OIDC] `OIDCDeploymentConnector` (OIDCFeatures in yaml config) `scopes` and `externalUrl` parameters moved to `OIDCWebAuthenticationPlugin` (VegaFeatures -> authentication.oidc parameters in yaml config)
* [Vega][OIDC] `OIDCDeploymentConnector` (OIDCFeatures in yaml config) `loginLocaleParamName` parameter renamed to `localeParamNameOpt`

Reminder : Since 4.0.0, `vertigo-ui-mpa.js` trigger events at different initializations point :
- vui-before-app-create
- vui-before-plugins
- vui-before-page-mounted
- vui-after-page-mounted

You can use them for example to register vue components :

`window.addEventListener('vui-before-page-mounted', function(event) { Vue.use(xxx); })`

* [Planning] Some refactoring to support new features
- If lots of changes, you may use `AgendaControllerHelper` instead of AbstractController
- `AbstractAgendaController.initContext` add param modeTranchesHoraire, use `false` for older behaviour
- `PlanningServices.createPlageHoraire` use List<UID<Agenda>> and add param maxWeekDaysNumber
* [Core] If you have testing activeFlags via paramManager (`VERTIGO_BOOT_ACTIVE_FLAGS`), you may prefer to use `Node.getNode().getNodeConfig().activeFlags()`

# from 4.1.0 to 4.2.0

* **[Core] Moved `io.vertigo.core.util.NamedThreadFactory` to `io.vertigo.core.lang.NamedThreadFactory`**. Update your imports if you extend or instantiate this class.

⚠️ Do not use 4.2.0 of vertigo-studio, use 4.2.0a instead

[**Renaming tool**](https://raw.githubusercontent.com/vertigo-io/vertigo-tools/master/migration-tools/update-renaming-tool.xml) _(beta)_<br/>

* **[DataModel] Renamings** : (use renaming tool)
  - `DtObject` to `DataObject`
  - `DtField` to `DataField`
  - `DtFieldName` to `DataFieldName`
  - `DtDefinition` to `DataDefinition`
  - `DtObjectUtil` to `DataModelUtil`

* **[Ui] Add better handling of missing context with a redirectUrl** 

There is a new mandatory KVCollection to set in your configuration : `VViewInitContext`. It keep the initContext parameters of each page. When the context is missing, Vertigo try to reload the initContext of the page with these parameters. 
The TTL of this KVCollection should be greater or equals to the `VViewContext` TTL.

For berkeley db, it may look like this : 

```Yaml
        - kvStore.berkeley:
          collections: VViewContext;TTL=3600, VViewInitContext;TTL=3600 #=1h
          dbFilePath: ${java.io.tmpdir}/vertigo-ui/ViewContext
```

* [Ui] : modal component now have `width` and `height` parameter. If you were using `iframe_width` and `iframe_height`, you must change to the new parameters.

# from 4.0.0 to 4.1.0
* [Ui] with new kvStorePlugin : berkeleyDb isn't embedded with vertigo-datastore anymore : you should add needed lib for your kvStorePlugin into your pom.xm
* [Ui] Change namedComponent parametre encode : check you use `th:` prefix for thymeleaf, (before param value may be interpreted even without `th:`)

Example, before `th:` not needed : 
```html
<vu:select object="myObj" field="id" labelField="label" list="elements" @update:model-value="|httpPostAjax('@{_reload}',vueDataParams(['myObj']))|"/>
```
  now `th:` needed :
```html
<vu:select object="myObj" field="id" labelField="label" list="elements" th:@update:model-value="|httpPostAjax('@{_reload}',vueDataParams(['myObj']))|"/>
```
* AbstractSqlSearchLoader : 1st generic attribute is removed
* OIDCAppLoginHandler : `doLogin` last parameter, change from `AuthorizationSuccessResponse` to `OIDCTokens`
* ElasticSearchFeatures, restHL feature (RestHighLevelElasticSearchConnector) have now mandatory boolean parameter `ssl` 

# from 3.6.0 to 4.0.0

[**Renaming tool**](https://raw.githubusercontent.com/vertigo-io/vertigo-tools/master/migration-tools/update-renaming-tool.xml) _(beta)_<br/>

* [Core] Update to JDK17
* [Core] Rename MessageText to LocaleMessageText (included in renaming tool)
* **[Core] Rename @Analytics to @Trace** — signature changed, must be done manually :
  - `@Analytics(processName = "xxx")` → `@Trace(category = "yyy", name = "xxx")`
* [Core] Rename Tuple.getValX() to Tuple.valX()
* [Core] Rename record's getter from getMyProperty to myProperty()
* **[Ui, Vega] jakarta namespace : Spring 6, Javalin 5, Jetty 11**
  - use `jakarta` package instead of `javax`
* **[Ui] Quasar v1 to v2** (see https://quasar.dev/start/upgrade-guide/)
  - The color CSS variable names in Quasar have changed (cf link), somes was defined by Vertigo and have changed too :
    - `--q-color-primary-invert` => `--v-primary-invert`
    - `--q-color-secondary-invert` => `--v-secondary-invert`
    - `--q-color-accent-invert` => `--v-accent-invert`
* **[Ui] Vue2 -> Vue3** (see https://v3-migration.vuejs.org/)
  - use `@vue:mounted` instead of `@hook:mounted`
  - Attributes on `<img>` are more strict, width and height must not contains unit (eg: px) or it will be set to 0
* **[Ui] Replace buttons attribute ariaLabel to title** (aria-label wasn't use for a11y in button, title was)
  - if `icon` attribute is set, `title` is mandatory
* [Quarto] Rename feature `export` to `exporter`

# from 3.5.0 to 3.6.0
* [Core] Protect URL resolver only accept file, classpath or jar url.
If you use other unsafe protocols you may use UnsafeURLResourceResolverPlugin 
* **[Vega]** `authentication` feature no longer have `defaultRedirectUrl` parameter. Redirect Url must be provided through the `doLogin` method of the `appLoginHandler`. Redirect Url after logout is provided with the new `doLogout` method.
* **[Ui] Quasar fix the usage of `q-table__control` for table's slots** (before it add a q-table-control which doesnt exists) : check rendering if you use slots or subtitles.

To rollback to old rendering, you may add a `<div class="column">` or switch flex direction to `column` of `q-table__control` when necessary

* **[Ui] Add xxx_content_slot on input components to define specific vue's slots (xxx = input, date, or time)**
Check usage of content for input tags in edit mode. Search for `</vu:`. If you passed content to inputs component put this content into a `<vu:slot name="xxx_content_slot">`
**Use `edit_content_slot`** for : `autocomplete-edit`, `autocomplete-multiple-edit`, `checkbox-edit`, `checkbox-multiple-edit`, `chips-autocomplete-edit`, `datetime-edit`, `knob-edit`, `radio-edit`, `select-edit`, `select-multiple-edit`, `slider-edit`, `text-area-edit`, `text-editor-edit`, `text-field-edit`     
**Use `date_content_slot`** for : `date-edit`

# from 3.4.0 to 3.5.0
WIP
* [Audit] Refactoring api
* [vega] CSP : Rename parameter externalUrl to cspFrameAncestor
* [Ui] Add support to link activation of SpringMvcConfig to Vertigo Modules : now you could active Spring controller with the same rules as your vertigo modules : **check your module's feature with Spring controllers extends DefaultUiModuleFeatures**.

# from 3.3.0 to 3.4.0
* **[Core] ParamManager return Optional param values** 
* **[database] Switch postgre to GENERATED_COLUMNS ()**
Previously we used `generated_keys`, but this don't work with PostGresql if PK isn't the first column.
But with `GENERATED_COLUMNS` postgre's jdbc driver add a the column **case-sensitive**, this **break** vertigo insert queries.
We need to add a parameter in the jdbc url : `quoteReturningIdentifiers=false`. You may update the jdbc driver version.
* [Ui] @RequestMapping are now mandatory, add them if missing on controllers
* [vega] Rename package auth -> authentication

The other changes are added features or fixes that can be updated seamlessly.

# from 3.2.0 to 3.3.0
* **[Datafactory] Change FacetedQueryDefinition linked to DtIndex instead KeyConcept (support multiple indices)** 
* **[Studio] Generated SearchClient are generated per DtIndex instead of KeyConcept.**
* **[Studio] Change detection of Association code : must have CamelCase AFTER 2 trigrams or a number. You may change some associations codes.**
* [Datafactory] Upgraded loadList api to search into multiple indices
* [Account] Rename api withCriteria to withSecurityKeys
* **[Ui] Add ViewContext update security : only allow data with a writeable input in UI** : 
Vertigo Ui inputs components are updated, but you may check if you use direclty `vu:include-data`, add `modifiable` attribute if you send this data to server.

* [Ui] Param name of selectedFacets is now defined by `@ViewAttribut("paramName")` (was 'selectedFacets' by default)
Check if you specify a `paramName, ensure it's the same name in the html page.

* **[DataFactory] Rename `innerWriteTo` of customAggregation to `_innerWriteTo`**
* [All] Remove log4j2 conf by default in vertigo jar : Check you have provided one


# from 3.1.1 to 3.2.0
This version contains mostly fixes and have very few effects on project code

# from 3.1.0 to 3.1.1
This version contains mostly fixes and have few effects on project code : 
* [Ui] Refactor UploadFile component; you may update your FileUploadControler (check [mars FileUploadController](https://github.com/vertigo-io/vertigo-mars/blob/v3.1.1/src/main/java/io/mars/support/controllers/FileUploadController.java)
* [Ui] Changed how components are override. If you had some, declare their path in your WebConfig
```java
@Override
protected String getCustomComponentsPathPrefix() {
  return "io/mars/ui/";
}
```
* [Ui] Added Server side rendering, which can be use to comply with a strict CSP.
* [Ui] Added a thymeleaf vu:text for render escaped text


# from 3.0.0 to 3.1.0

**We encourage to upgrade to 3.1.1 version it contains some important fix**

# from 2.1.0 to 3.0.0
[**Renaming tool**](https://raw.githubusercontent.com/vertigo-io/vertigo-tools/master/migration-tools/update-renaming-tool.xml) _(beta)_<br/>
* **[Dynamo] Split Dynamo to multiple module : DataStore, DataModel, DataBase, DataFactory**
* [Core] Update to Java 11
* [Core] Lots of renames (you should use renaming tools)
  * io.vertigo.app to io.vertigo.core.node
  * io.vertigo.app.Home to io.vertigo.core.node.Node
  * io.vertigo.app.AutoCloseableApp to io.vertigo.core.node.AutoCloseableNode
  * io.vertigo.core.component to io.vertigo.core.node.component
  * io.vertigo.lang to io.vertigo.core.lang
  * io.vertigo.util to io.vertigo.core.util
* [Core] Added support of connectors (plugin could use a connector to obtain a singleton client); connectors open the raw API to project fore more specific usage
* [Search] Rename search envIndex param to envIndexPrefix (change your myapp.yaml)
* [Model] Change field required property to cardinality (1, * or ?) : change your ksp or Java DtObject @Field annotation
* [Dynamo] With the split of dynamo your yaml should change, standard DynamoFeatures may look like this 
```yaml
  io.vertigo.datamodel.DataModelFeatures:
  io.vertigo.datastore.DataStoreFeatures:
  features:
    - store:
    - kvStore:
  featuresConfig:
    - store.data.sql:
    - store.data.sql:
      dataSpace: orchestra
    - store.file.db:
      storeDtName: DtMediaFileInfo
    - kvStore.berkeley:
      collections: VViewContext;TTL=43200
      dbFilePath: ${java.io.tmpdir}/vertigo-ui/MarsVViewContext
  io.vertigo.datafactory.DataFactoryFeatures:
  features:
    - search:
  featuresConfig:
    - collections.luceneIndex:
    - search.elasticsearch.restHL:
      envIndexPrefix: mars
      rowsPerQuery: 50
      config.file: search/elasticsearch.yml
```
* [Datastore] Remove FileManager. It used to be use to create Files, you should use `StreamFile.of(...` or `FSFile.of(...` instead
* [All] Lots of renames (you should use renaming tools)
  * io.vertigo.dynamo.domain.model.FileInfoURI to io.vertigo.dynamo.file.model.FileInfoURI
  * io.vertigo.dynamo.domain.model.EnumVAccessor to io.vertigo.dynamo.impl.store.datastore.EnumStoreVAccessor
  * io.vertigo.dynamo.domain.model.VAccessor to io.vertigo.dynamo.impl.store.datastore.StoreVAccessor
  * io.vertigo.dynamo.collections to io.vertigo.datafactory.collections
  * io.vertigo.dynamo.search to io.vertigo.datafactory.search
  * io.vertigo.dataxxx.yyy.metamodel to io.vertigo.dataxxx.yyy.definitions
  * io.vertigo.database.timeseries.TimeSeriesDataBaseManager to io.vertigo.database.timeseries.TimeSeriesManager;
  * io.vertigo.dynamox.search.AbstractSqlSearchLoader to io.vertigo.datafactory.impl.search.loader.AbstractSqlSearchLoader
  * io.vertigo.dynamox.domain.constraint to io.vertigo.datamodel.impl.smarttype.constraint
  * io.vertigo.dynamox.domain.formatter to io.vertigo.datamodel.impl.smarttype.formatter
  * io.vertigo.social.services.* to io.vertigo.social.*
  * io.vertigo.social.services.notification.NotificationServices to io.vertigo.social.notification.NotificationManager
  * io.vertigo.social.services.comment.CommentServices to io.vertigo.social.comment.CommentManager
  * io.vertigo.social.services.handle.HandleServices to io.vertigo.social.handle.HandleManager
  * io.vertigo.geo.services.* to io.vertigo.geo.*
  * io.vertigo.geo.services.geosearch.GeoSearchServices to io.vertigo.geo.geosearch.GeoSearchManager
  * io.vertigo.datamodel.smarttype.ModelDefinitionProvider to io.vertigo.datamodel.impl.smarttype.ModelDefinitionProvider
  * ModelManager to SmartTypeManager
  * io.vertigo.dynamo.plugins.environment.StudioDefinitionProvider to io.vertigo.studio.plugins.metamodel.vertigo.StudioDefinitionProvider
  * *.smarttype.constraint.Constraint to io.vertigo.basics.constraint.Constraint
  * *.smarttype.formatter.Formatter to io.vertigo.basics.formatter.Formatter
  * io.vertigo.dynamox.task.TaskEngineSelect to io.vertigo.basics.task.TaskEngineSelect
  * io.vertigo.dynamox.search.AbstractSqlSearchLoader to io.vertigo.datafactory.impl.search.loader.AbstractSqlSearchLoader
  * StoreManager is split in two Managers : storeManager.getDataStore() to EntityStoreManager, and storeManager.getFileStore() to FileStoreManager

* [Studio] Change how resource are registered (there are MetamodelResource and not DefinitionProvider). Check sample on [mars/mda](https://github.com/vertigo-io/vertigo-mars/tree/v3.0.0/src/main/java/io/mars/support/mda)
Studio use a specific studio-config.yaml like this : 
```yaml
resources: 
  - { type: kpr, path: src/main/resources/io/mars/application.kpr}
  - { type: security, path: src/main/resources/io/mars/basemanagement/base-auth-config.json}
  - { type: security, path: src/main/resources/io/mars/hr/hr-auth-config.json}
mdaConfig:
  projectPackageName: io.mars
  targetGenDir : src/main/
  properties: 
  vertigo.domain.java: true
  vertigo.domain.java.generateDtResources: false
  vertigo.domain.sql: true
  vertigo.domain.sql.targetSubDir: javagen/sqlgen
  vertigo.domain.sql.baseCible: H2
  vertigo.domain.sql.generateDrop: true
  vertigo.domain.sql.generateMasterData: true
  vertigo.task: true
  vertigo.search: true
  vertigo.authorization: true
  mermaid: true
```
* [Studio] StaticMasterData support values writed in declaration, example :
```
create DtDefinition DtTicketStatus {
  stereotype: "StaticMasterData"
  id ticketStatusId {domain: DoCode label:"Id"}
  field label {domain: DoLabel label:"Status Label" }
  values : `{
  "open": { "ticketStatusId":"OPEN", "label":"Open"},
  "assigned": { "ticketStatusId":"ASSIGNED", "label":"Assigned"},
  "closed": { "ticketStatusId" : "CLOSED", "label":"Closed"}}`
}
```
* **[Studio] Domains aren't defined in ksp anymore. There are renamed by SmartTypes and are declared in a java enum**

Before : 
```
create Domain DoId {
  dataType : Long
  formatter : FmtId
  storeType : "NUMERIC"
}

create Domain DoInstant {
  dataType : Instant
  formatter : FmtDateHeure
  storeType : "TIMESTAMP"
}

create Domain DoLocaldate {
  dataType : LocalDate
  formatter : FmtDate
  storeType : "DATE"
}

create Domain DoCurrency {
  dataType : BigDecimal
  formatter : FmtCurrency
  unit : "$"
  storeType: "NUMERIC(12,2)"
}

create Domain DoHealth {
  dataType: Integer
  formatter : FmtDefault
  constraint : [CkMinHealthValue0, CkMaxHealthValue100]
  storeType : "NUMERIC"
}

create Domain DoLabel {
  dataType : String
  formatter : FmtDefault
  constraint : [CkMaxLength100]
  storeType : "VARCHAR(100)"
  indexType : "text_fr:sortable"
}

create Domain DoEmail {
  dataType : String
  formatter : FmtDefault
  constraint : [CkEmail, CkMaxLength150]
  storeType : "VARCHAR(150)"
}
```

After: 
```java
public enum MarsSmartTypes {

  @SmartTypeDefinition(Long.class)
  @Formatter(clazz = FormatterId.class, arg = "")
  Id,

  @SmartTypeDefinition(Instant.class)
  @Formatter(clazz = FormatterDate.class, arg = "dd/MM/yyyy ' ' HH'h'mm")
  Instant,

  @SmartTypeDefinition(LocalDate.class)
  @Formatter(clazz = FormatterDate.class, arg = "dd/MM/yyyy")
  Localdate,

  @SmartTypeDefinition(BigDecimal.class)
  @Formatter(clazz = FormatterDefault.class)
  Currency,

  @SmartTypeDefinition(Integer.class)
  @Formatter(clazz = FormatterDefault.class)
  @Constraint(clazz = ConstraintNumberMinimum.class, arg = "0", msg = "")
  @Constraint(clazz = ConstraintNumberMaximum.class, arg = "100", msg = "")
  Health,

  @SmartTypeDefinition(String.class)
  @Formatter(clazz = FormatterDefault.class)
  @Constraint(clazz = ConstraintStringLength.class, arg = "100", msg = "")
  @SmartTypeProperty(property = "indexType", value = "text_fr:sortable")
  Label,

  @SmartTypeDefinition(String.class)
  @Formatter(clazz = FormatterDefault.class)
  @Constraint(clazz = ConstraintRegex.class, arg = "^[_a-zA-Z0-9-]+(\\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\\.[_a-zA-Z0-9-]+)*(\\.[a-zA-Z0-9-]{2,3})+$", msg = "L'email n'est pas valide")
  @Constraint(clazz = ConstraintStringLength.class, arg = "150", msg = "")
  Email,
}
```

In KSP, keep dataType and storeType only (used by generations).
```
create Domain DoId {
  dataType : Long
  storeType : "NUMERIC"
}

create Domain DoInstant {
  dataType : Instant
  storeType : "TIMESTAMP"
}

create Domain DoLocaldate {
  dataType : LocalDate
  storeType : "DATE"
}

create Domain DoCurrency {
  dataType : BigDecimal
  storeType: "NUMERIC(12,2)"
}

create Domain DoHealth {
  dataType: Integer
  storeType : "NUMERIC"
}

create Domain DoLabel {
  dataType : String
  storeType : "VARCHAR(100)"
}

create Domain DoEmail {
  dataType : String
  storeType : "VARCHAR(150)"
}
```

You could use this regexp to start your ProjectSmartTypes.java file (you must finished manually) :
`create Domain Do(.*)\s*\{(\r?\n)\s*dataType\s*:\s*(\w+)\r?\n([^}]*\r?\n)*\s*\}`
replaced by 
`@SmartTypeDefinition(\3.class)\2@Formatter(clazz = FormatterDefault.class)\2\1,`

* [Commons] Move Cache from module commons to module DataStore (change in `yourConfig.yaml` from CmmonsFeatures to DataStoreFeatures)
* [Commons] Assertion refactor API checkXXX->check().xxx isEmpty -> IsBlank; argNotEmpty -> isNotBlank; isNotNull, isTrue; 
* [Commons] Rename StringUtil.isEmpty to StringUtil.isBlank
* [Vega] Switch from sparkjava to javalin
In yaml conf : 
```yaml
io.vertigo.connectors.javalin.JavalinFeatures:
  features:
    - standalone:
io.vertigo.vega.VegaFeatures:
  features:
    - webservices:
  featuresConfig:
    - webservices.javalin:
        apiPrefix: /api
``` 

in web.xml : 
```xml
  <filter>
    <filter-name>VegaFilter</filter-name>
    <filter-class>io.vertigo.vega.plugins.webservice.webserver.javalin.VegaJavalinFilter</filter-class>
  </filter>
  <filter-mapping>
    <filter-name>VegaFilter</filter-name>
    <url-pattern>/api/*</url-pattern>
  </filter-mapping>
```
* [Vega] Removed AutoSortAndPagination, but it's easier to do it. You cou use DtListState into collectionsManager or storeManager
* [Ui] Url mandatory on fileUpload component
* [Ui] Move VUi.methods.httpPostAjax to VUiPage.httpPostAjax
* [Ui] componentStates are no in VUiPage.$data.componentStates

# from 2.0.0 to 2.1.0

* __[extensions/ui] Upgrade to quasar 0.17 to 1.4.1 for migration also follow Quasar's upgrade guide available here :__ https://quasar.dev/start/upgrade-guide#Upgrading-from-0.x-to-v1 
* [core] add support of flag negation in yaml config
* [commons] commands WIP
* [commons] analytics better logger name
* [database] Close DataStream when set as statement params
* [dynamo] BugFix on concurrency saving first file of the day
* [dynamo] UpperCamelCase feature when import domain definition from XMI
* [dynamo] Merge pull request #137
* [dynamo] fix EA and OOM Loaders with UpperCamelCase
* [dynamo] fixed associations conventions in EA and OOM
* [dynamo] move formatterId in dynamox
* [dynamo] handles WIP
* [vega] Merge pull request #138
* [vega] Fix #141 Added serializeNulls params to GoogleJsonEngine. Default false
* [vega] Fixed #142 Swagger parameterized type support only class or parameterizedType
* [vega] Remaned AppServletStarter2 to AppServletStarterXml
* [vega] Fixed #147 : can't close app if start fail
* [vega] Fixed #148 when routes contains digits at end
* [vega] Updated swagger ui site to v3.24.0
* [studio] fix generated javadoc for xAO
* [all] Updated libs versions
  * junit-jupiter 5.4.2 -> 5.5.2
  * freemarker 2.3.28 -> 2.3.29
  * spark 2.8.0 -> 2.9.1
  * rest-assured 3.3.0 -> 4.1.2
  * log4j-core 2.11.2 -> 2.12.1
  * slf4j 1.7.25 -> 1.7.28
  * cglib 3.2.10 -> 3.3.0
  * gson 2.8.5 -> 2.8.6
  * snakeyaml 1.23 -> 1.25
  * servlet-api 3.1.0 -> 4.0.1
  * h2     1.4.199 -> 1.4.200
  * postgresql 42.2.5 -> 42.2.8
  * c3p0   0.9.5.3 -> 0.9.5.4
  * janino 3.0.8 -> 3.1.0
  * ehcache 2.10.6 -> 3.8.1
  * jedis 2.9.0 -> 3.1.0
  * lucene 8.0.0 -> 8.2.0
  * elasticsearch 7.1.0 -> 7.4.1

# from 1.1.3 to 2.0.0

[**Renaming tool**](https://raw.githubusercontent.com/vertigo-io/vertigo-tools/master/migration-tools/update-renaming-tool.xml) _(beta)_<br/>
This tools is a set of ant's tasks. In case of this 2.0, it comes with two usefull targets :

- CONST Java Entity to CamelCase java : Replace old java definitions to CamelCase definition new in vertigo 2.0
- CONST KSP to CamelCase ksp : Replace old ksp definitions to CamelCase definition new in vertigo 2.0

Replacements are generated in folders : `generated-java` and `generated-ksp`

* [all] tests in junit 5 (use AbstractTestCaseJU5)
* __[all] Migrate from CONST_CASE to UpperCamelCase everywhere except in SQL databases__ a tool is provided to help migration
* __[core] all definitions are UpperCamelCase__
* [core] discovery : Added conditions to filter abstract classes
* [core] Removed deprecated Date DataType + remove all use of java.util.Date
* [core] Removed MessageTextBuilder (.of + simple)
* [core] Removed Tuple3, Tuples.Tuple2 renamed to Tuple
* [core] syntaxic sugar : use InjectorUtil instead of DIInjector
* __[core] replaced `@Named` by `@ParamValue`__
* __[core] Removed unused concept of named components__
* __[core] add yaml configuration with flippable features, xml configuration is now discouraged and will be removed in next version (even 2.x)__
* [core] refactored AppConfig -> Renamed in NodeConfig
* [commons] Fixed aggregate health status : 1 or more Red drive to Red
* [commons] Added ability to track non single thread processes
* [database] Added timeseries in database module
* __[database,dynamo,studio] remove hibernate support__
* [dynamo] Added check on association fix #129
* [dynamo] notNull is replaced by required in all ksp (task and entities)
* [dynamo] key is replaced by id in ksp
* [dynamo] URI is replaced by UID
* [dynamo] Made FacetedQueryResult serializable
* __[dynamo] Modified date pattern for ES query (breaking change)__
* [dynamo] localdate support in query
* [dynamo] ES: added optional param for embeded
* [dynamo] ES: Fix urn type, no normalizer
* [dynamo] ES: Fixed reindexall task when removed old elements
* [dynamo] From io.File to nio.Path
* [dynamo] DtListState.of
* [dynamo] Changed default charset ok Ksp loader from iso-8859-1 to utf-8
* [dynamo] Add FileInfoURI convert key for DataStore
* [dynamo] Upgraded ES version from 5.6.8 to 7.0.0, and Lucene from 6.6.0  to 8.0.0
* [dynamo] Fixed Search user DSL to escape bad syntax instead of VUser
* [dynamo] Added ElasticSearch plugin for v5.6
* [dynamo] Added clustering to CollectionsManager
* [dynamo] Fixed empty facets from Json with Vega
* __[dynamo] KSP Definition in CamelCase__
* [dynamo] remove brokerbatch and moved brokerNN in DataStore
* [dynamo] Fixed search by prefix with accents
* [dynamo] Simplified syntax to declare an association in ksp
* [dynamo] Fix domain metrics
* [dynamo] Replaced DAO access with DtListState instead of RowMax only
* [dynamo] Fix masterdatas to comply with with boot order : no more MasterDataInitializer -> replaced by a DefinitionProvider. Devs can use AbstractMasterDataDefinitionProvider
* __[es2.4] Remove ElasticSearch 2.4 plugin__
* [account] Allow comments in textauthentication plugin
* [account] Fixed account store plugin and null value
* [account] Support Id conversion from Account to Entity source
* __[account] Removed deprecated personna__
* [account] Removed definition prefix from authorization aspect
* [vega] fix Bug Content-Type sous JBoss
* [vega] Added support of '.' in exclude and include fieldname
* [vega] App version for swagger is a string
* [vega] Added Instant and LocalDate support to SwaggerApi
* [vega] UID Json encoding now send only key part, and use generics in order to resolved entity class
* [vega] Set attribute 'SessionExpired' true in case of session expiration
* [vega] Fixed iterator of uiListModifiable : remove change the expected count
* [vega] Inactive CacheControlFilter when Cache-Control header is already set
* [vega] Removed securityCheck of URL : may use @secured on WS
* [vega] Removed deprecated UiListState
* [studio] multiple files for sql init of staticmasterdatas
* [studio] MasterDataManager is now mandatory
* [studio] dt objects can be splitted by feature
* [studio] fix dao import when dt_index = keyconcept
* [studio] created a SearchClient component dedicated to search access
* [studio] Drop if exists
* [studio] Removed sequences for non numeric PK
* [Social] Move MailManager from vertigo-mail to Vertigo-Social
* [all] update dependencies log4j2 2.11.0 -> 2.11.2 ; cglib-nodep 3.2.6 -> 3.2.10 ; gson 2.8.2 -> 2.8.5 ; c3p0 0.9.5.2 -> 0.9.5.3 ; janino  3.0.8 -> 3.0.12 ; ehcache 2.10.4 -> 2.10.6 ; berkleydb sleepycat je 7.5.11 -> 18.3.12 ; rest-assured 3.0.7 -> 3.3.0 ; freemarker 2.3.23 -> 2.3.28 ; javax-mail 1.6.0 -> 1.6.2 ; h2 1.4.196 -> 1.4.199 ; struts2 2.5.16 -> 2.5.20 ; fr.opensagres.xdocreport.converter.odt.odfdom 2.0.1 -> 2.0.2 ; fr.opensagres.xdocreport.converter.docx.xwpf 2.0.1 -> 2.0.2 ; org.apache.poi 3.16 -> 4.0.1


# from 1.1.2 to 1.1.3

This is a minor release with several fixes. We encourage you to update to this version.
Use this version for use in a java9+ project.

# from 1.1.1 to 1.1.2

This is a minor release with several fixes. We encourage you to update to this version.
Use this version for use in a java9+ project.

# from 1.1.0 to 1.1.1

This is a minor release with several fixes. We encourage you to update to this version.

# from 1.0.0 to 1.1.0

A new [**Renaming tool**](https://github.com/vertigo-io/vertigo/raw/vertigo-1.1.3/replace-1.0.0.jar) _(beta)_<br/>
The file to use to migrate from 1.0.0 to 1.1.0 [here](https://github.com/vertigo-io/vertigo/raw/vertigo-1.1.3/replace-1.0.0-1.1.0.json)
See previous migration to see usage : [Usage](#usage)
*(this one isn't the ant file)*

## Detail
* [Dynamo] VFile use Instant instead of Date, you should replaced new Date() by Instant.now()
* [Dynamo] Removed deprecated `getListByDtField`, use `getListByDtFieldName` instead
* [Dynamo] Refactor Domain, moved `DtField.getDomain().getFormatter().valueToString` to `DtField.getDomain().valueToString`
* [Dynamo] Type of field has been changed. Now DtObject and DtList aren't a DataType anymore. You could determined them from domain by using !getScope().isPrimitive() and domain.isMultiple().
* [Dynamo] Refactored createSearchQueryBuilderContact from DAO to support multi selected facets. Now use a SelectedFacetValues object instead of a List<ListFilter>. Common usage with new ArrayList<ListFilter>() could be replaced by SelectedFacetValues.empty().build()
SelectedFacetValues could be use from WebServices params to DAO.
If necessary `UiSelectedFacet` api have a `toSelectedFacetValues` method.
* [Dynamo] changed syntax of parameters in TaskEngineProcBatch : the fake '.0' must be removed

 before : 
```
create Task TK_INSERT_COUNTRIES_BATCH {
  className : "io.vertigo.dynamox.task.TaskEngineProcBatch"
    request : "
      INSERT INTO MY_COUNTRY (COU_ID, NAME) values (#COUNTRY_LIST.0.COU_ID#, #COUNTRY_LIST.0.NAME#) 
      "
  attribute COUNTRY_LIST     {domain : DO_DT_COUNTRY_DTC    notNull:"true"   inOut :"in"}
}
``` 

 after :
```
create Task TK_INSERT_COUNTRIES_BATCH {
  className : "io.vertigo.dynamox.task.TaskEngineProcBatch"
    request : "
      INSERT INTO MY_COUNTRY (COU_ID, NAME) values (#COUNTRY_LIST.COU_ID#, #COUNTRY_LIST.NAME#) 
      "
  attribute COUNTRY_LIST     {domain : DO_DT_COUNTRY_DTC    notNull:"true"   inOut :"in"}
}
```

* [Commons] We changed HealthChecked parameters : `feature` for the global feature checked (like DB, Mail, etc...) and `name` for detailled check done.
With renaming tool, we set feature to "APP", but you should 
* [Commons] HealthCheck constructor have new parameters : `module` and `feature`

* [Dynamo] Update ElasticSearch to 5.6, and Lucene to 6.6.0
This update need some reworks in your project due to a lots of api breaking changes in ElasticSearch.
- keyword fields aren't tokenized by definition : now you can't use an analyzer for them anymore : you must use a normalizer instead.

before : 
```YAML
index :
    analysis :
        analyzer :
            code :
                tokenizer : keyword
                filter : [standard]
            multiple_code :
                tokenizer : piped_keywords
                filter : [standard]
            sortable :
                tokenizer : keyword
                filter : [lowercase, asciifolding]
            text_fr :
                tokenizer : standard
                filter : [standard, lowercase, snowball, elision]
        tokenizer :
            keyword :
                type : keyword
            piped_keywords :
                type : pattern
                pattern : '([|])'
        filter :
            snowball:
                type : snowball
                language: French
            elision:
                type : elision
                articles: [l, m, t, qu, n, s, j, d]
```

after : 
```YAML
index :
    analysis :
        normalizer :
            code :
                type : custom
            sortable :
                type : custom
                filter : ["lowercase", "asciifolding"]  
        analyzer :
            multiple_code :
                tokenizer : piped_keywords
                filter : [standard]
            text_fr :
                tokenizer : standard
                filter : [standard, lowercase, snowball, elision]
        tokenizer :
            keyword :
                type : keyword
            piped_keywords :
                type : pattern
                pattern : '([|])'
        filter :
            snowball:
                type : snowball
                language: French
            elision:
                type : elision
                articles: [l, m, t, qu, n, s, j, d]
```

- fields are managed in a new way in ES and can't be use for facet if not configured to (not a FieldData by default in ES). We extends indexType params in domain's definitions to support a `facetable` parameter, it must be use for fields in facets. (fieldType look like : `indexType: "string:facetable"`)


- We added a `sortable` parameter in indexType. This add a duplication of the value with a keyword normalizer. This new field is named from the source field and the `.keyword` suffix. Vertigo switch automatically to this keyword field when necessary for sort or facet. 
This replace the previous usage of copy field for sort field (like `*_not_analyzed` fields). Copy fields could be use for aggregate many fields in one.
* **[Studio] Moved Tasks with only one input of data-object from xxModuleNamexxPAO to xxObjectxxDAO.**
* [Vega] Some renames link to Search's rework. In WebServices API, UiListState should be replace by DtListState. And UiSelectedFacets should be replace by SelectedFacetValues.

# from 0.9.4 to 1.0.0

A new renaming tool, more powerfull but still in beta is now available.
[**Renaming tool**](https://github.com/vertigo-io/vertigo/raw/vertigo-1.1.3/replace-1.0.0.jar) _(beta)_<br/>
The file to use to migrate from 0.9.4 to 1.0.0 [here](https://github.com/vertigo-io/vertigo/raw/vertigo-1.1.3/replace-0.9.4-1.0.0.json)

## usage

1. open a commandline at the root of your project
2. put *replace-1.0.0.jar* and *replace-0.9.4-1.0.0.json* (see above for download) at the root of your project
3. run the following command : java -jar replace-1.0.0.jar replace-0.9.4-1.0.0.json
4. finish your migration by hand for the things that cannot be scripted (see below for more detail)

## more detail
* [vertigo] Builder Refactoring (General use is now : ObjectToBuild.builder() )
* [core] silent => verbose (silently mode by default)
* [core] replace new Param with Params.of
* [core] removed withApi(boolean) on moduleConfigBuilder
* [core] refactoring MessageText and VUserException (use the added shortcut)
Before
```JAVA
throw new VUserException(new MessageText(messageKey,params))
```
After
```JAVA
throw new VUserException(messageKey, params)
```
* [core] removed describable replaced by HealthCheck and HealthManager
* [core] components are now definition providers to register definitions from a component
* [core] move components related classes from io.vertigo.lang to io.vertigo.core.component
* [core] move locale related classes from io.vertigo.lang to io.vertigo.core.locale
* [core] changed life cycle : Typical changes implied with SearchLoader
Before
```java
public class RobotSearchLoader extends AbstractSqlSearchLoader<Long, Robot, RobotIndex> {

  private final SearchIndexDefinition indexDefinition;
  @Inject
  private RobotPAO robotPAO;

  /**
   * Construct an instance of RobotSearchLoader.
   *
   * @param searchManager
   * @param taskManager
   * @param transactionManager
   */
  @Inject
  public RobotSearchLoader(final SearchManager searchManager, final TaskManager taskManager,
      final VTransactionManager transactionManager) {
    super(taskManager, transactionManager);
    indexDefinition = searchManager.findIndexDefinitionByKeyConcept(Robot.class);
  }

  /** {@inheritDoc} */
  @Override
  public List<SearchIndex<Robot, RobotIndex>> loadData(final SearchChunk<Robot> searchChunk) {
        [...]
  }
```

After

```java
public class RobotSearchLoader extends AbstractSqlSearchLoader<Long, Robot, RobotIndex> implements Activeable {
  private SearchIndexDefinition indexDefinition;
  @Inject
  private RobotPAO robotPAO;
  
  private SearchManager searchManager;

  

  /**
   * Construct an instance of RobotSearchLoader.
   *
   * @param searchManager
   * @param taskManager
   * @param transactionManager
   */
  @Inject
  public RobotSearchLoader(final SearchManager searchManager, final TaskManager taskManager,
      final VTransactionManager transactionManager) {
    super(taskManager, transactionManager);
    this.searchManager = searchManager;
  }

  /** {@inheritDoc} */
  @Override
  public List<SearchIndex<Robot, RobotIndex>> loadData(final SearchChunk<Robot> searchChunk) {
    ...
  }

  @Override
  public void start() {
    indexDefinition = searchManager.findIndexDefinitionByKeyConcept(Robot.class);
  }

  @Override
  public void stop() {
    // NOP
  }
```

* [account] To keep using the old persona user session replace inheritance of your userSession from UserSession to PersonaUserSession
* [commons] you must use the @EventBusSubscribed on a component's method to subscribes to an event type
* [commons] you must use the @DaemonScheduled on a component's method to register a daemon
For example
 ```JAVA
@DaemonScheduled(name = "DMN_DAEMON_NAME", periodInSeconds = 60 )
public void aMethodName() {
  //method body
}

@EventBusSubscribed
public void aMethodName(final TypeOfEvent event) {
    //method body
}
```

* **[dynamo] removed dynamic behaviour on DtDefinition**
* [dynamo] replacewith by add in FacetedQueryResultBuilder
* [dynamo] Renamed FacetedQueryResultBuilder to FacetedQueryResultMerger
* [dynamo] moved criteria from dynamo/store to dynamo/criteria
* **[dynamo] Removed elasticSearch1_7 plugin (you must switch to 2.4.5)**
* [dynamo] replaced CollectionsManager by Criterions for ranges and value filtering
* **[dynamo] remove SqlCallableStatement and out parameters in sql** Use SqlPreparedStatement instead
* [dynamo] move database in new module : add it to your pom
* **[Vega] DtObject Json serialization now use the field's getter. It won't work if it send a exception. Previous usage of search copy_to fields sent exception and must be rewrite.**
* [tempo] remove module (use vertigo-mail and vertigo-orchestra extensions). Two use vertigo-orchestra use the provided [readme](https://github.com/vertigo-io/vertigo-extensions/tree/develop/vertigo-orchestra) 
* [tempo] Rename io.vertigo.tempo.mail to io.vertigo.mail

For simpler refactoring from Tempo to Orchestra you may use the memory plugins:
`MemoryProcessExecutorPlugin`, `MemoryProcessSchedulerPlugin`, `MemoryProcessDefinitionStorePlugin`

1. transform your old Runnable Job class into a *RunnableActivityEngine*
 before
```JAVA
public final class MyJob implements Runnable {
   ...
}
```
after
```JAVA
public final class MyJob extends RunnableActivityEngine {
   ...
}
```

2. use the legacy builder of processDefinition
```JAVA
final ProcessDefinition processDefinition = ProcessDefinition.legacyBuilder("PRO_MY_OLD_TEMPO_JOB_NAME", MYJob.class)
        .build();
```

## Cleaning
For projects that need to transition from version 1.7 to version 2.4, the indexType becomes mandatory for String and BigDecimal types:

- In the domain definitions (.ksp), the index_type for all domains of type String becomes mandatory => for a VARCHAR field of type code use indexType: “code”, for a “CLOB” or “VARCHAR” field of free entry type use “text_fr”
- In the domain definitions (.ksp), the index_type for all domains of type BigDecimal becomes mandatory => use an indexType “double”.
- In the domain definitions (.ksp) for all domains of type Long, the index_type SHOULD NOT be specified.

# from 0.9.3 to 0.9.4

WARN : There is a blocker issue in vertigo-studio use vertigo-studio v0.9.4a

[**Renaming tool**](https://raw.githubusercontent.com/vertigo-io/vertigo-tools/master/migration-tools/update-renaming-tool.xml) _(beta)_<br/>
* Simpler boot declaration in managers.xml *(not in renaming tool)*. 
  - Remove all loaderPlugins 
  - Remove all RegistryPlugin
  - Declare Definition providers

Your boot should look like this:
```XML
  <boot locales="fr_FR">
   <plugin class="io.vertigo.core.plugins.resource.classpath.ClassPathResourceResolverPlugin" />
   <plugin class="io.vertigo.core.plugins.resource.url.URLResourceResolverPlugin" />
  </boot>
...
<module name="definitions">
<definitions>
  <provider class="io.vertigo.dynamo.plugins.environment.DynamoDefinitionProvider" >
   <param name="encoding" value="utf-8" />
   <resource type ="xmi" path="/project/model/project.xml"/>
   <resource type="classes" path="my.project.DtDefinitions" />
   <resource type ="kpr" path="/project/mda/generation.kpr"/>
  </provider>
  <provider class="io.vertigo.persona.plugins.security.loaders.SecurityDefinitionProvider" >
   <resource type="security" path="boot/components/project-auth-config.xml" /> 
  </provider>
 </definitions>
</module>
```

* Rename io.vertigo.lang.Describable to io.vertigo.core.component.Describable
* Rename io.vertigo.core.spaces.component.ComponentInfo to io.vertigo.core.component.ComponentInfo
* Rename io.vertigo.core.component.di.injector.Injector to io.vertigo.core.component.di.injector.DIInjector

* [Dynamo] A DtList can't be optional (especially in Tasks)
Be sure to make notNull task's attributes of type DtList 

* [Persona] Replaced Security DTD by XSD
  - Remove the DTD declaration from your security config file
  - tag `<authorisation-config>` is now replaced with `<authorisationConfig>`

* Rename io.vertigo.core.spaces.component.ComponentInitializer in io.vertigo.core.component.ComponentInitializer
* Rename loadList and getList to findAll
* Replace FilterCriteriaBuilder with Criterions

For example this code 
```JAVA
final FilterCriteriaBuilder<MyEntity> fcb = new FilterCriteriaBuilder<>();
  fcb.withFilter(MyEntityFields.DCU_ID, dcuId);
```
is replaced by 
```JAVA
final Criteria<MyEntity> criteria = Criterions.isEqualTo(MyEntityFields.DCU_ID, dcuId);
```
You can now chain Criterions with "and" and "or" operators ans operations are extended (see Criterions API)

* [All] Always use WrappedException (wrap & unwrap), and params order changed
Replace `throw new WrappedException(e);` with `throw WrappedException.wrap(e);`
Replace `throw WrappedException.wrapIfNeeded(e);` with `throw WrappedException.wrap(e);`

* [Dynamo] Refactored Data access (database dialect moved from StoreManager to DataBaseManager)
  - Use SqlDataStorePlugin instead of OracleDataStorePlugin, PostgresqlDataStorePlugin, etc
  - Component SqlDataBaseManager must now be declared is the same module as StoreManager

Your managers.xml should look like this:
```XML
<component api="SqlDataBaseManager" class="io.vertigo.dynamo.impl.database.SqlDataBaseManagerImpl">
 <plugin class="io.vertigo.dynamo.plugins.database.connection.datasource.DataSourceConnectionProviderPlugin">
   <param name="source" value="java:/comp/env/jdbc/DataSource" />
   <param name="classname" value="io.vertigo.dynamo.impl.database.vendor.postgresql.PostgreSqlDataBase" />
  </plugin>
</component>
<component api="StoreManager" class="io.vertigo.dynamo.impl.store.StoreManagerImpl" >
  <plugin class="io.vertigo.dynamo.plugins.store.datastore.sql.SqlDataStorePlugin">
   <param name="sequencePrefix" value="SEQ_" />
  </plugin>
</component>
```

* Rename io.vertigo.x.impl.`extension` to io.vertigo.x.`extension`.impl for notification, account, comment, rules

* DefinitionSpace.put(Definition) is now hidden, to add Definitions you should add a DefinitionProvider to your managers.xml. It's get() method may returned your definitions

# from 0.9.2 to 0.9.3
[**Renaming tool**](https://raw.githubusercontent.com/vertigo-io/vertigo-tools/master/migration-tools/update-renaming-tool.xml) _(beta)_<br/>
* __[All] Updated to JDK 8__ : Change your JRE in your pom.xml, project IDE config, compile, ant execution, etc...
* __[All] Renamed vertigo Option to jdk Optional__
* __[Dynamo] Split DtObject as Entity (persistent) and simple DtObject (non persistent)__ : 
 * Now persistent property on DtObject aren't usefull. Persistent object had a key, other have none.
 * Key are mandatory on Entity and forbidden on DtObject
 * `persistent` property on DtObject should be removed. Add a key field if `persistent:"true"`, remove key field if `persistent:"false"`
 * URI are URI of Entity : Replace `URI<D extends DtObject>` by `URI<E extends Entity>`
__This change have some impact, keep it in mind if you have some exceptions__ 
* [Dynamo] AbstractSqlSearchLoader constructor take VTransactionManager, should be added in specific SearchLoaders
* [Dynamo] SearchLoader should implements  `loadData(final SearchChunk<Person> searchChunk)` instead of `loadData(final List<URI<Utilisateur>> uris)`
* [dynamo] SearchLoader should use KeyConcept's URI instead of IndexDtDefinition ones. You may replace `indexDefinition.getIndexDtDefinition()` to `indexDefinition.getKeyConceptDtDefinition()`
* [Dynamo] Reindexer job don't start transaction anymore, you should create it in your `SearchLoader::loaData`
Like
```Java
  /** {@inheritDoc} */
  @Override
  public List<SearchIndex<Car, Car>> loadData(final SearchChunk<Car> searchChunk) {
  try (final VTransactionWritable tx = getTransactionManager().createCurrentTransaction()) {
    final List<SearchIndex<Car, Car>> result = new ArrayList<>();
    final DtDefinition dtDefinition = DtObjectUtil.findDtDefinition(Car.class);
    for (final Car car : loadCarList(searchChunk)) {
    final URI<Car> uri = new URI<>(dtDefinition, car.getId());
    result.add(SearchIndex.createIndex(indexDefinition, uri, car));
    }
    return result;
  }
  }
```

* [Dynamo] DtListProcessor is now typed, should create a DtListProcessor with type like `collectionsManager.<MyObj>createDtListProcessor()`
* [Dynamo] Moved ExportManagerImpl to quarto
* [Dynamo] Updated ElasticSearch to 2.3.5 : to continue to use ElasticSearch 1.7, you must changes your pom.xml
```XML
<dependency>
  <groupId>io.vertigo</groupId>
  <artifactId>vertigo-dynamo-plugin-elasticsearch_1_7</artifactId>
  <version>${vertigo.version}</version>
</dependency>
```
and reference the ElasticSearch 1.7 plugins in your managers.xml : (just change the package name)
```XML
<plugin class="io.vertigo.dynamo.plugins.search.elasticsearch_1_7.transport.ESTransportSearchServicesPlugin">
  <param name="servers.names" value="${boot.es.server.names}" />
  <param name="envIndex" value="${boot.es.env.index}" />
  <param name="rowsPerQuery" value="50" />
  <param name="config.file" value="search/elasticsearch.yml" />
  <param name="cluster.name" value="${boot.es.cluster.name}" />
</plugin>
```
You may need to clear your index directory

* [Dynamo] ElasticSearch 2.3.5 there is no more standard analyzer by default, for primitive types you should declared an empty analyzer name like `indexType:":integer"`
* [Dynamo] Attributes `DTC notNull:"false"` aren't accepted anymore : A list is never optional


# from 0.9.1 to 0.9.2
[**Renaming tool**](https://raw.githubusercontent.com/vertigo-io/vertigo-tools/master/migration-tools/update-renaming-tool.xml) _(beta)_<br/>
* [Core] Aligned vertigo Option api to JDK api. You could use the rename tool, in order to rename previous Option api to the new one rename (`isPresent`, `ofNullable`, `orElse`, `of`, `none`). Note that isEmpty is deprecated and hasn't equivalent in jdk api, replace it by !otp.isPresent()
* [Core] Splitted App and autoCloseable. You should use try(new AutoCloseableApp() { } in unit tests
* [Dynamo] Renamed DAOBroker to DAO
* [Dynamo] Renamed CRUD methods. You should replace some method name `get => read` and `getList => findAll`
* [Dynamo] Search FacetedQueryResult json v3 (#59). You could select your api version by the parameter `searchApiVersion` param on `GoogleJsonEngine` component in your managers.xml. Added Highlight for search results in FacetedQueryResult json v4
* [Dynamo] Renamed methods : `toUrn` to `urn`
* [Dynamo] Create URI public on `DtObjectUtil`

# from 0.9.0 to 0.9.1
[**Renaming tool**](https://raw.githubusercontent.com/vertigo-io/vertigo-tools/master/migration-tools/update-renaming-tool.xml) _(beta)_<br/>

__Important__ : Use v0.9.1a for vertigo quarto. (0.9.1 have a buggy pom.xml)

* Added `boolean serializeElements` to DataStoreConfig, you could set it to true by default (false on big/unmodifiable list). And removed `noSerialization` from CachePlugin implementations.
* Removed SortState. It's simpler : juste a fieldName and an order desc/asc. Its always case insensitive and null first.
* Renamed `get(uri)` to `read(uri)` on FileStore
* Removed TextFile. You should create one on your project if need it (but think about it, it's pretty useless)
[TextFile.java](https://github.com/vertigo-io/vertigo/blob/vertigo-0.9.0/vertigo-dynamo-impl/src/main/java/io/vertigo/dynamo/impl/file/model/TextFile.java)

* Removed `initClass=ManagerInitializer` into managers.xml files. Now you should add them into a `<init>` tag at the end of <config> tag.
Like this : 
```Xml
<init>
  <initializer class="lollipop.boot.DataBaseInitializer"/>
  <initializer class="lollipop.boot.MasterDataInitializer"/>
  <initializer class="lollipop.boot.I18nRessourcesInitializer"/>    
</init>
```
* Removed `inheritance` into managers.xml files
* Renamed `EventManager` to EventBusManager
* Removed WorkManager. (in fact moved into another vertigo module, not released yet)
* Renamed io.vertigo.vega.plugins.webservice.instrospector.annotations.AnnotationsWebServiceIntrospectorPlugin to io.vertigo.vega.plugins.webservice.scanner.annotations.AnnotationsWebServiceScannerPlugin
* Removed MockConnectionProviderPlugin use io.vertigo.dynamo.plugins.database.connection.c3p0.C3p0ConnectionProviderPlugin instead.
Need c3p0 dependency in pom.xml:
```Xml
<dependency>
  <groupId>com.mchange</groupId>
  <artifactId>c3p0</artifactId>
  <version>0.9.5.2</version>
  <scope>test</scope>
</dependency>
```

* [Dynamo] FileManager add a daemon in order to purge TempFiles. __DaemonManager is mandatory when FileManager was used__.
* SearchLoader change chunk api, and now return a `Iterable<Option<SearchChunk<K>>>` it's a really simple change to do, just to say that `hasNext` isn't reliable before `next` was called.
* [Vega] Refactored JsonSerializer for FacetedQueryResultJson v2    
**Watch out the new search API :**

Before:
```Json
{
  "groups": {
    "composer": [ {...composers}, ... ],
    "actor": [ {...actors}, ... ],
    "producer": [ {...producers}, ... ]
  },
  "facets": {
    "FCT_PEOPLE_TITLE": {
      "f":200,
      "m": 275
    },
    "FCT_PEOPLE_PROFESSION": {
      "composer": 46,
      "actor": 355,
      "producer": 74
    }
  },
  "totalCount": 475
}
```

After:
```Json
{
  "groups": [
    { "composer" :[ {...composers}, ... ] },
    { "actor" :[ {...actors}, ... ] }
    { "producer" :[ {...producers}, ... ] }
  ],
  "facets": [
      { "FCT_PEOPLE_TITLE":[ 
        { "f":200 },
        { "m":275 }] 
      },
      { "FCT_PEOPLE_PROFESSION":[ 
        { "composer":46 },
        { "actor":355 },
        { "producer":74 }] 
      }
  ],
  "totalCount": 475
}
```

* Renamed storeName of TaskDefinition to dataSpace

# from 0.8.3 to 0.9.0
[**Renaming tool**](https://raw.githubusercontent.com/vertigo-io/vertigo-tools/master/migration-tools/update-renaming-tool.xml) _(beta)_<br/>
_Renaming tool doesn't do all renames, you should do them manually !_

* Added params storeDtName to DbFileStorePlugin.
* Major changes in managers.xml. Mandatory Managers are set bey default : LocalManager, RessourceManager, ParamManager and EnvironmentManager. You just need to declared plugins and locales (`,` separated). _If you declared other Manager in your boot section you should moved them in another module._
_If you use Initializer in your boot section you should moved them to another module, they are no more dedicated to a Component._

Now your boot should looks like : 
```XML
<boot locales="fr_FR">
  <plugin class="io.vertigo.core.plugins.resource.classpath.ClassPathResourceResolverPlugin" />
  <plugin class="io.vertigo.core.plugins.resource.url.URLResourceResolverPlugin" />
  <plugin class="io.vertigo.dynamo.plugins.environment.loaders.kpr.KprLoaderPlugin" />
  <plugin class="io.vertigo.dynamo.plugins.environment.registries.domain.DomainDynamicRegistryPlugin" />
  <plugin class="io.vertigo.dynamo.plugins.environment.registries.task.TaskDynamicRegistryPlugin" />
  <plugin class="io.vertigo.dynamo.plugins.environment.registries.file.FileDynamicRegistryPlugin" />
</boot>
```

* Multistore support need some changes for FileInfo (no changes needed for DtDefinition)
In KSP FileInfo definitions reference a storeName. This storeName should be declared in managers.xml on usefull plugin. If not set plugin's name default to 'main'.
Exemple : 
```Json 
create FileInfo FI_FILE_INFO_STD {
  storeName : "main"
}

create FileInfo FI_FILE_INFO_TEMP {
  storeName : "temp"
}
```

* Multistore for DtDefinition need to be altered into ksp like this : 
```Json 
alter DtDefintion DT_DATA_TO_IMPORT {
  storeName : "distantStore"
}
```

```XML
<plugin class="io.vertigo.dynamo.plugins.store.filestore.fs.FsFullFileStorePlugin">
  <param name="name" value="temp"/>
  <param name="path" value="java.io.tmpdir/testVertigo/"/>
  <!-- <param name="purgeDelayMinutes" value="1440" />  --> <!--  24h -->
</plugin>
<plugin class="io.vertigo.dynamo.plugins.store.filestore.db.DbFileStorePlugin">
  <!-- implicit name : main  -->
  <param name="storeDtName" value="DT_VX_FILE_INFO"/> <!-- Dt use in DataBase -->
</plugin>
```
* Renamed io.vertigo.commons.plugins.resource.java.ClassPathResourceResolverPlugin to io.vertigo.core.plugins.resource.classpath.ClassPathResourceResolverPlugin
* Renamed io.vertigo.commons.plugins.resource.url.URLResourceResolverPlugin to io.vertigo.core.plugins.resource.url.URLResourceResolverPlugin
* Renamed `Home.getComponentSpace()` to `Home.getApp().getComponentSpace()`
* Renamed `Home.getDefinitionSpace()` to `Home.getApp().getDefinitionSpace()`
* Moved some class from `io.vertigo.core` to `io.vertigo.app` : Home, App, AppListener, Boot, Logo
* Renamed package `io.vertigo.core.config` to `io.vertigo.app.config` 
* Renamed ConfigManager to ParamManager
* Renamed ConfigPlugin to ParamPlugin
* Changed API of ParamManager : merge path and name in one name
Exemple : 
```Java
/* replace  */
configManager.getStringValue("mail", "from");
/* to */
paramManager.getStringValue("mail.from");
```

* Changed XML Config syntax : (no more trees)

Before : 
```XML
<application-config>
  <config name="file.store">
    <property name="path" value="/var/tmp/" />
  </config>
</application-config>
```

After : 
```XML
<config>
  <path name="file.store">
  <param name="path" value="/var/tmp/" />
   </path>
</config>
```
* In managers.xml, for external params replaced {xxx} to ${xxx}
and if your project use ParamContainerManager (it's native yet) replaced 'conf:xxx' by '${xxx}'

* Splitted KVStore and DataStore : if you use KVStorePlugin you must add the KVStoreManager component.
* Renamed io.vertigo.dynamo.plugins.kvdatastore.delayedmemory.DelayedMemoryKVDataStorePlugin to io.vertigo.dynamo.plugins.kvstore.delayedmemory.DelayedMemoryKVStorePlugin
* Renamed `dataStoreName` of KVStore to `collection` in KVStorePlugin and in TokenManagerImpl

* Refactored initializers : they are no more specialized for one component. Remove generics and use injection if necessary.

* Refactored ElasticSearch indexes : now they are use as environments, documents are splitted by type. This mean you could use the same ElasticSearch instance for multiple environment. **Previously created indexes are deprecated and must be recreated**.
* Refactored ElasticSearch plugins : ``cores`` params is deprecated, and should be replaced by `envIndex` whith the name of this environment (like : `myApp-prod`)

# from 0.8.2 to 0.8.3
[**Renaming tool**](https://raw.githubusercontent.com/vertigo-io/vertigo-tools/master/migration-tools/update-renaming-tool.xml) _(beta)_

* In your index definitions ksp, use DslListFilterBuilder instead of RegExpListFilterBuilder (before named DefaultListFilterBuilder)


# from 0.8.1 to 0.8.2
[**Renaming tool**](https://raw.githubusercontent.com/vertigo-io/vertigo-tools/master/migration-tools/update-renaming-tool.xml) _(beta)_

* Renamed io.vertigo.vega.rest.* to io.vertigo.vega.webservice.* (like io.vertigo.vega.rest.model.UiListState to io.vertigo.vega.webservice.model.UiListState)
* Renamed io.vertigo.vega.plugins.rest.* to io.vertigo.vega.plugins.webservice.* 
* Renamed session attribute vertigo.rest.Session to vertigo.webservice.Session 
* Renamed XxxxRestHandlerPlugin to XxxxWebServiceHandlerPlugin (may be done in your managers.xml config)
* Renamed parent class DefaultSearchLoader to AbstractSqlSearchLoader
* Renamed io.vertigo.vega.rest.RestfulService to io.vertigo.vega.webservice.WebServices
* Renamed io.vertigo.vega.impl.rest.servlet.ApplicationServletContextListener to io.vertigo.vega.impl.webservice.servlet.AppServletContextListener (in web.xml)
* Replaced io.vertigo.vega.plugins.rest.routesregister.sparkjava.VegaSparkApplication by a new VegaSparkFilter. <br/>In web.xml you should replace SparkFilter like this :
```XML
<filter>
  <filter-name>SparkFilter</filter-name>
  <filter-class>io.vertigo.vega.plugins.webservice.webserver.sparkjava.VegaSparkFilter</filter-class>  
</filter>
```

* [Core] Refactor java.lang.Timer to DeamonManager. The new DaemonManager is almost mandatory.
<br/>Add this component into your config : 
```XML
<component api="DaemonManager" class="io.vertigo.commons.impl.daemon.DaemonManagerImpl"/>
```
* [Vega] Extract ServerState behaviour in a new optional plugin. Now ServerState behaviour is optional. 
<br/>Now your Vega module should be like this :
```XML
<module name="vertigo-vega" api="false" inheritance="java.lang.Object">
  <component api="WebServiceManager" class="io.vertigo.vega.impl.webservice.WebServiceManagerImpl">
    <plugin class="io.vertigo.vega.plugins.webservice.instrospector.annotations.AnnotationsEndPointIntrospectorPlugin" />
    <plugin class="io.vertigo.vega.plugins.webservice.webserver.sparkjava.SparkJavaServletFilterWebServerPlugin" />
    <!-- Handlers -->
    <plugin class="io.vertigo.vega.plugins.webservice.handler.ExceptionWebServiceHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.webservice.handler.CorsAllowerWebServiceHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.webservice.handler.SessionInvalidateWebServiceHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.webservice.handler.SessionWebServiceHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.webservice.handler.RateLimitingWebServiceHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.webservice.handler.SecurityWebServiceHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.webservice.handler.AccessTokenWebServiceHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.webservice.handler.JsonConverterWebServiceHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.webservice.handler.ServerSideStateWebServiceHandlerPlugin" /> <!-- optional -->
    <plugin class="io.vertigo.vega.plugins.webservice.handler.AccessTokenWebServiceHandlerPlugin" /> <!-- optional -->
    <plugin class="io.vertigo.vega.plugins.webservice.handler.PaginatorAndSortWebServiceHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.webservice.handler.RateLimitingWebServiceHandlerPlugin" /> <!-- optional -->
    <plugin class="io.vertigo.vega.plugins.webservice.handler.ValidatorWebServiceHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.webservice.handler.RestfulServiceWebServiceHandlerPlugin" />
  </component>
  <component api="JsonEngine" class="io.vertigo.vega.engines.webservice.json.GoogleJsonEngine"/>
  <component api="TokenManager" class="io.vertigo.vega.impl.token.TokenManagerImpl">
    <param name="dataStoreName" value="demo-tokens" />
  </component>
</module>
```

# from 0.8.0 to 0.8.1
* Renamed io.vertigo.core.Home.App to io.vertigo.core.App
* Renamed io.vertigo.core.boot to io.vertigo.core.config
* Renamed io.vertigo.core.di to io.vertigo.core.component.di
* Refactor XMLAppConfigBuilder : replace 
```java
new XMLAppConfigBuilder()
.withBootConfig(new BootConfigBuilder().[...].build())
.withModules([...])
.build();
```
to 
```java
new XMLAppConfigBuilder()
.withModules([...])
.beginBoot().[...].endBoot()
.build();
```
* Refactor modules's definitions in managers.xml. Loading order are more predictible now : 

1. boot module
2. definitions
3. other components module per module (as before)

For that, previously module `core` may be renamed boot and `resource` tags must be put into a `definitions` tag.
Should declared `resource` tags into a `definitions` tag.

Now your managers.xml may looks like: 
```XML
<?xml version =  '1.0' encoding = 'UTF-8'?>
<config>
  <boot>
  <component api="LocaleManager" class="io.vertigo.core.impl.locale.LocaleManagerImpl" >
    <param name="locales" value="fr_FR" />
  </component>
  <component api="ResourceManager" class="io.vertigo.core.impl.resource.ResourceManagerImpl">
    <plugin class="io.vertigo.commons.plugins.resource.java.ClassPathResourceResolverPlugin" />
    <plugin class="io.vertigo.commons.plugins.resource.url.URLResourceResolverPlugin" />
  </component>
  <component api="EnvironmentManager" class="io.vertigo.core.impl.environment.EnvironmentManagerImpl">
      <plugin class="io.vertigo.dynamo.plugins.environment.loaders.poweramc.OOMLoaderPlugin" />
      <plugin class="io.vertigo.dynamo.plugins.environment.loaders.kpr.KprLoaderPlugin" >
        <param name="encoding" value="UTF-8" />
      </plugin>
      <plugin class="io.vertigo.dynamo.plugins.environment.registries.domain.DomainDynamicRegistryPlugin" />
      <plugin class="io.vertigo.dynamo.plugins.environment.registries.task.TaskDynamicRegistryPlugin" />
      <plugin class="io.vertigo.dynamo.plugins.environment.registries.search.SearchDynamicRegistryPlugin" />
      <plugin class="io.vertigo.dynamo.plugins.environment.registries.file.FileDynamicRegistryPlugin" />
    </component>
  </boot>
  
  <module name="model">
  <definitions>
    <resource type ="oom" path="file:./src/main/database/model/yourmodel.oom"/>
    <resource type ="kpr" path="file:./src/main/resources/mda/generation.kpr"/>     
  </definitions>
  </module> 

  <module name="vertigo-dynamo">
    <!-- dynamo components declarations -->
  </module>

  <module name="<!-- other modules -->">
  <!-- components declarations -->
  </module> 
</config>
```
* Moved LocalManager and ResourceManager from commons to core 
Should renamed :
 * `io.vertigo.commons.locale` to `io.vertigo.core.locale`
 * `io.vertigo.commons.impl.locale` to `io.vertigo.core.impl.locale`
 * `io.vertigo.commons.resource` to `io.vertigo.core.resource`
 * `io.vertigo.commons.impl.resource` to `io.vertigo.core.impl.resource`

Note that plugins has been moved too but not renamed yet.

* Moved EnvironmentManager from dynamo to core
Should renamed :
 * `io.vertigo.dynamo.environment` to `io.vertigo.core.environment`
 * `io.vertigo.dynamo.impl.environment` to `io.vertigo.core.impl.environment`

* Update search query analyzer with wildcard
* Fixed search securityFilter, it could be set in FacetedSearchQueryBuilder
* Add default value to DefaultListFilterBuilder. Syntax usage is : ``#myNullableField#!(myDefaultValue)``. Note that parenthesis are mandatory
* SearchManager return Future<Long> on reindexAll to allow join on reindex and get indexed document count
* CSVExporter should kept empty value as empty. No more replaced "" to " "
* Renamed ESSearchServicePlugin to ESNodeSearchServicePlugin 
* Fixed store object without index

# from 0.7.5 to 0.8.0
* Renamed io.vertigo.tempo.plugins.job.* to io.vertigo.tempo.plugins.scheduler.*
* Renamed io.vertigo.dynamo.persistance.* to io.vertigo.dynamo.store.*
* Renamed PersistenceManager to StoreManager.
* Renamed Broker to DataStore.
* Removed KVDataStoreManager and KVDataStorePlugin is now a StoreManager's plugin
* Added EventManager it's mandatory with StoreManager.
Should add this manager in managers.xml :
```XML
<component api="EventManager" class="io.vertigo.commons.impl.event.EventManagerImpl" />
```
* Moved SecurityResourceLoaderPlugin from VSecurityManager to EnvironmentManager in managers.xml
* JobManager is now slipt into : 
 * JobManager for JobDefinitions and execution
 * SchedulerManager for scheduling
Your managers.xml, should now defined these both managers : 
```XML
<component api="JobManager" class="io.vertigo.tempo.impl.job.JobManagerImpl" />
<component api="SchedulerManager" class="io.vertigo.tempo.impl.scheduler.SchedulerManagerImpl">
  <plugin class="io.vertigo.tempo.plugins.scheduler.basic.BasicSchedulerPlugin" />
</component>
```
* Renamed withField to addField in quarto ExportSheetBuilder

# from 0.7.4 to 0.7.5
* Rename KTransaction to VTransaction
* Rename KSecurityManager to VSecurityManager
* Rename KFile to VFile
* Rename KxFileInfo to VxFileInfo
* Service SearchManager.loadList take a new parameter for sorting and/or paging (it's nullable)

Notes complémentaires
* Ajout du paramètre targetSubDir dans les différents *GeneratorPlugin :
```XML
    <component api="MdaManager" class="io.vertigo.studio.impl.mda.MdaManagerImpl">
      <param name ="targetGenDir" value="src/main/javagen/"/>
      <param name ="encoding" value="UTF-8"/>
      <param name ="projectPackageName" value="fr.dgac.stitch"/>
    
      <plugin class="io.vertigo.studio.plugins.mda.domain.DomainGeneratorPlugin">
        <param name="targetSubDir" value="."/>
        <param name="generateDtResources" value="false" /><!-- FALSE -->
        <param name="generateDtDefinitions" value="true" />
        <param name="generateDtObject" value="true" />
        <param name="generateJpaAnnotations" value="false" /><!-- FALSE -->
      </plugin>
       
      <plugin class="io.vertigo.studio.plugins.mda.domain.SqlGeneratorPlugin">
        <param name="targetSubDir" value="sqlgen"/>
        <param name="baseCible" value="PostgreSql" />
        <param name="generateDrop" value="false" />
      </plugin>
      <plugin class="io.vertigo.studio.plugins.mda.domain.JSGeneratorPlugin">
        <param name="targetSubDir" value="."/>
        <param name="generateDtResourcesJS" value="true" />
        <param name="generateJsDtDefinitions" value="true" />
      </plugin>
      <plugin class="io.vertigo.studio.plugins.mda.task.TaskGeneratorPlugin">
        <param name="targetSubDir" value="."/>
      </plugin>
      <!-- plugin class="io.vertigo.studio.plugins.mda.search.SearchGeneratorPlugin"/  -->
      <plugin class="io.vertigo.studio.plugins.mda.file.FileInfoGeneratorPlugin">
        <param name="targetSubDir" value="."/>
      </plugin>
      <plugin class="io.vertigo.studio.plugins.mda.security.SecurityGeneratorPlugin">      
        <param name="targetSubDir" value="."/>
      </plugin>
    </component> 
```
* io.vertigo.dynamo.impl.persistence.util.DAOBroker : suppression du "getOption(P).get()", on fait directement un get(P).
* Suppression du RouteHandler et du SessionHandler. En cas de surcharge du SessionHandler, il faut créer à la place un SessionRestHandlerPlugin à passer au RestManagerImpl
* DefinitionSpace.containsValue renommé containsDefinition
* AbstractFormatterImpl qui était extend lorsque l'on définit un formatter a disparu. Il faut désormais implémenter l'interface Formatter (s'inspirer de FormatterDate par exemple).
* PersistenceManager : getBrokerConfiguration, getMasterDataConfiguration, ... renommage des "Configuration" en "Config".
* StringUtil.constToCamelCase avec un booleén, remplacé par StringUtil.constToLowerCamelCase et StringUtil.constToUpperCamelCase
* Renommage des DtListURIForAssociation en DtListURIForNNAssociation
* Suppression de la méthode save dans io.vertigo.dynamo.impl.persistence.datastore.BrokerImpl (à remplacer par un appel à create ou à update selon le cas).
* XMLModulesBuilder remplacé par XMLAppConfigBuilder : 
Exemple :
```java
protected AppConfig buildAppConfig() {
    final Properties prop = new Properties();
    prop.putAll(properties);
    final String[] managersXml;
    if (prop.containsKey("boot.applicationConfiguration")) {
      managersXml = prop.getProperty("boot.applicationConfiguration").split(";");
      prop.remove("boot.applicationConfiguration");
    } else {
      managersXml = getManagersXmlFileName();
    }
    return new XMLAppConfigBuilder().withSilence(true).withModules(getClass(), prop, managersXml).build();
  }
```
* Modifications sur ElasticSearchHandler : entre autre, la recherche prend désormais un DtListState pour prendre en compte la pagination et le tri dans la requête envoyée à ES.

# from 0.7.3 to 0.7.4
* Significative updated dependencies (if you use them) : struts2 2.3.20, elasticsearch 1.4.4, lucene 4.10.3
* Check early removed deprecated : PersistenceManager.getBrokerConfiguration, PersistenceManager.getMasterDataConfiguration, UiMessageStack.hasErrorOnField, UiRequestUtil.getHttpServletRequest, UiRequestUtil.getHttpSession
* managers.xml : (Vega only) Add restHandlerPlugins. Vega module looks like :
```XML
<module name="vertigo-vega" api="false" inheritance="java.lang.Object">
  <component api="RestManager" class="io.vertigo.vega.impl.rest.RestManagerImpl">
    <plugin class="io.vertigo.vega.plugins.rest.instrospector.annotations.AnnotationsEndPointIntrospectorPlugin" />
    <plugin class="io.vertigo.vega.plugins.rest.routesregister.sparkjava.SparkJavaRoutesRegisterPlugin" />
    <!-- Handlers -->
    <plugin class="io.vertigo.vega.plugins.rest.handler.ExceptionRestHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.rest.handler.CorsAllowerRestHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.rest.handler.SessionInvalidateRestHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.rest.handler.SessionRestHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.rest.handler.RateLimitingRestHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.rest.handler.SecurityRestHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.rest.handler.AccessTokenRestHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.rest.handler.JsonConverterRestHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.rest.handler.PaginatorAndSortRestHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.rest.handler.ValidatorRestHandlerPlugin" />
    <plugin class="io.vertigo.vega.plugins.rest.handler.RestfulServiceRestHandlerPlugin" />
  </component>
  <component api="JsonEngine" class="io.vertigo.vega.rest.engine.GoogleJsonEngine"/>
  <component api="TokenManager" class="io.vertigo.vega.impl.token.TokenManagerImpl">
    <param name="dataStoreName" value="lollipop-tokens" />
  </component>
</module>
```
* managers.xml : Rename vertigoimpl.commons to vertigo.commons.impl
* managers.xml : Add SecurityResourceLoaderPlugin to KSecurityManager :
```XML
<plugin class="io.vertigo.persona.plugins.security.loaders.SecurityResourceLoaderPlugin" />
```
* managers.xml : When using ElasticSearch as SearchPlugin you could use your embedded config file (yml)
* model (om/ksp) : This version added Stereotype support on DtObject, you could define stereotype in oom or ksp. Will be use more significantly in future releases.
* Struts2 : Multiple Radio buttons don't include $lt;br&gt; anymore, so then could be horizontal or vertical. You could use CSS instead.
* web.xml : (Vega only) Rename SparkApplication to VegaSparkApplication. Filter looks like : 
```XML
<filter>
  <filter-name>SparkFilter</filter-name>
  <filter-class>spark.servlet.SparkFilter</filter-class>
  <init-param>
    <param-name>applicationClass</param-name>
    <param-value>io.vertigo.vega.plugins.rest.routesregister.sparkjava.VegaSparkApplication</param-value>
  </init-param>
</filter>
```


# from 0.7.2 to 0.7.3
* NameSpace2Java : `build-mda.properties` file must be in classPath. (Ex: file:build-mda.properties -> /META-INF/build-mda.properties)
* NameSpace2Java : Some generation params move from .properties to managers.xml. `projectPackageName`, `targetGenDir`, `encoding`.
* managers-mda.xml : MdaManager refactored, exemple : 
```XML
<component api="MdaManager" class="io.vertigo.studio.impl.mda.MdaManagerImpl">
  <param name="projectPackageName" value="io.vertigo.dynamock" />
  <param name="targetGenDir" value="target/javagen/" />
  <param name="encoding" value="utf8" />
  <plugin class="io.vertigo.studio.plugins.mda.domain.DomainGeneratorPlugin">
    <param name="generateDtResources" value="true" />
    <param name="generateJpaAnnotations" value="true" />
    <param name="generateDtDefinitions" value="true" />
    <param name="generateDtObject" value="true" />
  </plugin>  
  <plugin class="io.vertigo.studio.plugins.mda.domain.SqlGeneratorPlugin">
    <param name="baseCible" value="PostgreSql" />
    <param name="generateDrop" value="true" />
  </plugin>  
  <plugin class="io.vertigo.studio.plugins.mda.domain.JSGeneratorPlugin">
    <param name="generateDtResourcesJS" value="true" />
    <param name="generateJsDtDefinitions" value="true" />
  </plugin>
  <plugin class="io.vertigo.studio.plugins.mda.task.TaskGeneratorPlugin" />
  <!-- plugin class="io.vertigo.studio.plugins.mda.search.SearchGeneratorPlugin"/ -->
  <plugin class="io.vertigo.studio.plugins.mda.file.FileInfoGeneratorPlugin"/>
</component>
```

* managers.xml : params in web.xml must be prefixed by `boot.` <br/>Exemple : `db.source` -> `boot.db.source`

* persistence.xml : To fix hibernate sequence your must remove the parameter `hibernate.id.new_generator_mappings`

* FileInfo ksp : remove `storeName` attribute in fileInfo definition : 
```Javascript
create FileInfo FI_FILE_INFO_STD {
   root : "DT_KX_FILE_INFO"
}
```
* managers.xml : Moved all DataStorePlugin from `io.vertigo.dynamo.plugins.persistence` to `io.vertigo.dynamo.plugins.persistence.datastore`
* managers.xml : Renamed `io.vertigo.commons.plugins.cache.map.MapCachePlugin` to `io.vertigo.commons.plugins.cache.memory.MemoryCachePlugin`
* app-services.xml : `<module>` renamed to `<config>`
* app-services.xml : Moved DaoBroker, this could change your inheritance attribute.<br/>Exemple:
```XML
<module name="dao" api="false" inheritance="io.vertigo.dynamo.impl.persistence.util.DAOBroker">  
```

# from 0.7.0 to 0.7.1
* managers.xml : Split `DomainGeneratorPlugin` into more specific plugin. <br/>Exemple:
```XML
<plugin class="io.vertigo.studio.plugins.mda.domain.DomainGeneratorPlugin">
  <param name="generateDtResources" value="true" />
  <param name="generateJpaAnnotations" value="true" />
  <param name="generateDtDefinitions" value="true" />
  <param name="generateDtObject" value="true" />
</plugin>  
<plugin class="io.vertigo.studio.plugins.mda.domain.SqlGeneratorPlugin">
  <param name="baseCible" value="PostgreSql" />
  <param name="generateDrop" value="true" />
</plugin>  
<plugin class="io.vertigo.studio.plugins.mda.domain.JSGeneratorPlugin">
  <param name="generateDtResourcesJS" value="true" />
  <param name="generateJsDtDefinitions" value="true" />
</plugin>
```
* services.xml : Changed aspect declaration, more simple. Must be declared before Services. <br/>Exemple:
```XML 
<module name="aspects" inheritance="java.lang.Object" >
  <aspect class="io.vertigo.dynamo.impl.transaction.KTransactionAspect"/>
  <aspect class="io.vertifo.demo.util.ComponentLoggerAspect"/>
</module>
```


# from 0.6.x to 0.7.0
* struts.xml : in order to use vertigo ftl tags, add 
```XML 
<constant name="struts.freemarker.manager.classname" value="io.vertigo.struts2.impl.views.freemarker.VFreemarkerManager" />
```
* web.xml : If you override some ftl tags, you should set a context param to your template's path. <br/>Exemple :
```XML
<context-param>
  <param-name>TemplatePath</param-name>
  <param-value>webapp://WEB-INF/classes/</param-value>
</context-param>
```
* managers.xml : Syntaxe change, rename `<modules>` to `<config>`
* global : Renamed package `io.vertigo.core.util` to `io.vertigo.util`
* global : Renamed package `io.vertigo.core.lang` to `io.vertigo.lang`
* global : Moved `VUserException` to `io.vertigo.lang.VUserException`
* global : class `ComponentSpaceConfigBuilder`replaced by `AppConfigBuilder`
* global : interface `UiSecurityTokenManager` renamed to `TokenManager`, and class `io.vertigo.vega.impl.security.UiSecurityTokenManagerImpl` replaced by `io.vertigo.vega.impl.token.TokenManagerImpl`
* SearchManager : Moved public api from `SearchServicePlugin` to `SearchManager`
* ExportManager: Replace `exportManager.createExportListParameters` by `exportBuilder` fluent usage.
<br/>Exemple :
```Java
final DtList<D> dtList = resultsRef.readDtList();
final Export export = new ExportBuilder(ExportFormat.CSV, "ExportDossier")
    .beginSheet(dtList, "dossiers")
    .withField(DossierFields.CODE)
    .withField(DossierFields.TITLE)
    .withField(DossierFields.MANAGER)
    .withField(DossierFields.STATE)
    .withField(DossierFields.CREATION_DATE)
    .endSheet()
    .build();
return exportManager.createExportFile(export);
```
