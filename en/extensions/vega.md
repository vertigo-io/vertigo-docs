# Vega

Module **Vega** enables easy WebService setup in the application.
It is oriented toward *Single-Page-Application* development, but can also be used for standard web application WebServices or system-to-system communication.
It integrates a handler chain, web authentication (SAML2, OIDC, Azure AD, local), rate limiting, and a set of *production-ready* solutions to accelerate and secure the application.

Vega also provides a WebService client to easily call WebServices from another Vertigo node or application.

## Internal Components

Internally, the module uses [Javalin](https://github.com/tipsy/javalin) for the embedded server and Servlet for WAR environments.
It provides API publication via the [Swagger](https://swagger.io/) standard.
To publish WebServices, a set of annotations on your business service facade is sufficient. Annotations are intentionally a subset of the [JAX-RS](https://javaee.github.io/javaee-spec/javadocs/javax/ws/rs/package-summary.html) standard.

For the client side, the module uses the JDK HttpClient.
To call WebServices, only an interface with standard Vega annotations is needed.

### Handler Chain (Pipe)

Each request traverses a chain of `WebServiceHandlerPlugin` sorted by priority:

| Priority | Plugin | Role |
|---|---|---|
| 5 | `LogExceptionsHandlerPlugin` | Logs 5XX errors |
| 10 | `ExceptionWebServiceHandlerPlugin` | Exception handling |
| 20 | `CorsAllowerWebServiceHandlerPlugin` | CORS management *(feature `webservices.cors`)* |
| 30 | `AnalyticsWebServiceHandlerPlugin` | AnalyticsManager tracing |
| 40 | `JsonConverterWebServiceHandlerPlugin` | JSON conversion (input/output) |
| 45 | `ApiKeyWebServiceHandlerPlugin` | API Key *(feature `webservices.auth.apiKey`)* |
| 50 | `SessionInvalidateWebServiceHandlerPlugin` | Session invalidation *(feature `webservices.security`)* |
| 60 | `SessionWebServiceHandlerPlugin` | Session management *(feature `webservices.security`)* |
| 70 | `SecurityWebServiceHandlerPlugin` | Global security *(feature `webservices.security`)* |
| 80 | `ServerSideStateWebServiceHandlerPlugin` | Server-side state *(feature `webservices.token`)* |
| 90 | `AccessTokenWebServiceHandlerPlugin` | Access tokens *(feature `webservices.token`)* |
| 100 | `RateLimitingWebServiceHandlerPlugin` | Rate limiting *(feature `webservices.rateLimiting`)* |
| 110 | `ValidatorWebServiceHandlerPlugin` | DTO validation |
| 120 | `RestfulServiceWebServiceHandlerPlugin` | Routing to business service |

## Quick start server

1. WebService class must implement [WebServices](https://github.com/vertigo-io/vertigo-extensions/blob/master/vertigo-vega/src/main/java/io/vertigo/vega/webservice/WebServices.java)
2. Class must be declared as a Vertigo *Component*, done via [business module autodiscovery](/en/getting-started/realworld_helloworld.md#_5-configuration-de-l39application)
3. Add annotations on methods, example:
```java
@AnonymousAccessAllowed
@GET("/anonymousTest")
```
4. Add *webservices* feature to configuration:

```yaml
modules:
  io.vertigo.vega.VegaFeatures:
    features:
      - webservices:
    featuresConfig:
      - webservices.javalin:
          apiPrefix: /api
```

For embedded server mode (optional), add `embeddedServer` feature from Javalin connector:

```yaml
modules:
  io.vertigo.connectors.javalin.JavalinFeatures:
    features:
      - embeddedServer:
```

5. Declare the filter in *web.xml* *(optional in embedded server mode)*:

```xml
   <filter>
       <filter-name>VegaJavalinFilter</filter-name>
       <filter-class>io.vertigo.vega.plugins.webservice.webserver.javalin.VegaJavalinFilter</filter-class>
   </filter>
   <filter-mapping>
       <filter-name>VegaJavalinFilter</filter-name>
       <url-pattern>/api/*</url-pattern>
   </filter-mapping>
```

6. Start the application
7. **Done**. You can call your webservice: [http://localhost:8080/*myWebApp*/api/anonymousTest](http://localhost:8080/*myWebApp*/api/anonymousTest)

Vertigo provides built-in WebServices [SwaggerWebServices](https://github.com/vertigo-io/vertigo-extensions/blob/master/vertigo-vega/src/main/java/io/vertigo/vega/impl/webservice/catalog/SwaggerWebServices.java) showing the available WebServices API.<br/>
* Swagger UI: [http://localhost:8080/*myWebApp*/api/swaggerUi](http://localhost:8080/*myWebApp*/api/swaggerUi)
* Swagger API only: [http://localhost:8080/*myWebApp*/api/swaggerApi](http://localhost:8080/*myWebApp*/api/swaggerApi)
- Feature `webservices.catalog` → `CatalogWebServices` (service catalog)
- Feature `webservices.healthcheck` → `HealthcheckWebServices` (health checks)

?> Vega can run in embedded server mode via `embeddedServer` feature of `JavalinFeatures`; specifying a filter in *web.xml* is unnecessary in that case.

## Quick start client

To call a remote WebService:

1. Reproduce the WebService API with a Java interface. Interface must extend `io.vertigo.core.node.component.Amplifier` and have `@WebServiceProxyAnnotation`. Detected by Vertigo like other components via [business module autodiscovery](/en/getting-started/realworld_helloworld.md#_5-configuration-de-l39application)
2. Add feature `webservices.proxyclient` to Vega configuration:
```yaml
  io.vertigo.vega.VegaFeatures:
    features:
      - webservices:
    featuresConfig:
      - webservices.proxyclient:
```
3. Add HttpClient connector to configuration:
```yaml
  io.vertigo.connectors.httpclient.HttpClientConnector:
    features:
      - httpclient:
          urlPrefix: http://mySpUrl:8080
```
4. Add annotations on interface methods:
```java
@WebServiceProxyAnnotation
@PathPrefix("/test")
public interface SimplerClientTestWebServices extends Amplifier {

  @AnonymousAccessAllowed
  @GET("/login")
  void login();

  @SessionInvalidate
  @GET("/logout")
  void logout();

  @GET("/{conId}")
  Contact testRead(@PathParam("conId") final long conId);
}
```
5. Use the WebService by injecting the interface into business service.
The autocloseable `HttpClientCookie` preserves cookies for successive calls:
```java
  @Inject
  private SimplerClientTestWebServices otherWService;

  public void myBusinessService() {
    try (HttpClientCookie httpClientCookie = new HttpClientCookie()) {
      otherWService.login();
      final Contact result = otherWService.testRead(2);
    }
  }
```
!> `HttpClientCookie` stores the remote cookie in a threadlocal.
Suitable for WebServices called in a batch or screen processing.
Not suitable for preserving across an entire user navigation.

?> `HttpClient` connector offers optional parameters:
- `name` to manage multiple *endpoints*; specify connection name in `@WebServiceProxyAnnotation`
- `connectTimeoutSecond` to define timeout
- `proxy` and `proxyPort` for proxy management

## API

### Code examples:
Numerous complete examples are in Vertigo tests on GitHub: [Tests Examples](https://github.com/vertigo-io/vertigo-extensions/blob/master/vertigo-vega/src/test/java/io/vertigo/vega/webservice/data/ws)

### Route Syntax

For route definitions, `{myParamName}` declares a URL variable used as a service parameter.
```java
@GET("/contact/{id}")
public Contact getContact(@PathParam("id") final int contactId) { ... }
```

### Parameters

Vega automatically maps incoming JSON to your method. Annotations indicate data source (URL parameters, body, headers…). By default, content is expected in the body (**Warning**: HTTP specifies *GET* requests have no body).

The most common case is receiving a DtObject directly. Vega formats JSON to Java type and validates against domain constraints.
User input can be retrieved directly via generic objects `UiObject` or `UiList<MyDto>`.

Vega populates implicit parameters:
- `UiMessageStack`: Message return stack (Success, Info, Warning, Error). With scope (global, per object, per field)
- `HttpServletRequest`: HTTP Request
- `HttpServletResponse`: HTTP Response

?> See annotations directly for details

### JSON Reader

`JsonReader` and its implementations read JSON data from various sources:

| Reader | Source | Annotation |
|---|---|---|
| `BodyJsonReader` | Request body | (default) |
| `QueryJsonReader` | Query parameters | — |
| `PathJsonReader` | URL path | `@PathParam` |
| `HeaderJsonReader` | HTTP headers | `@HeaderParam` |
| `InnerBodyJsonReader` | Body field | `@InnerBodyParam` |
| `RequestJsonReader` | Complete request | — |

### Return Object

Result is automatically serialized to JSON. Serialization is optimized for Vertigo objects:

- `Entity`: Persistent business object
- `UiObject`: Generic composite object for loading a complete page context
- `UiContext`: Named collection of objects
- `FacetedQueryResult`: Search result with facets and highlights
- `DtListDelta`: Aggregated list modifications
- `UiList<MyDto>`: UI object list
- `ExtendedObject`: Extensible object

```java
@GET("/uiContext/{contactIdFrom}/{contactIdTo}")
public UiContext testMultiPartBody(@PathParam("contactIdFrom") final long contactIdFrom, @PathParam("contactIdTo") final long contactIdTo) {
	final UiContext uiContext = new UiContext();
	uiContext.put("contactFrom", loadContact(contactIdFrom));
	uiContext.put("contactTo", loadContact(contactIdTo));
	uiContext.put("testLong", 12);
	uiContext.put("testString", "the String test");
	uiContext.put("testDate", DateUtil.newDate());
	return uiContext;
}
```
Result:
```json
{
	"testDate":"2014-07-29T00:00:00.000Z",
	"contactFrom":{"honorificCode":"MR_","name":"Martin","firstName":"Jean"},
	"testString":"the String test",
	"contactTo":{"honorificCode":"MIS","name":"Dubois","firstName":"Marie"},
	"testLong":12
}
```

### Exception Handling

On exceptions thrown in the service, an HTTP code is automatically set and a JSON error message is sent. Error response is intentionally simplified for application security (no stacktrace, etc.).
```json
{
  "globalErrors": "Error message or simple class name"
}
```

For **user exceptions** (user input or business errors), the message is more complete and specifies information for error positioning on the screen:
```json
{
  "globalErrors": [ "list of error messages", ...],
  "globalWarnings": [ "list of warning messages", ...],
  "globalInfos": [ "list of info messages", ...],
  "globalSuccess": [ "list of success messages", ...],
  "fieldErrors": { "field1": [ "list of error messages for this field", ...], "field2": [ ... ], ... },
  "fieldWarnings": { /* same structure than fieldErrors but for warnings */ },
  "fieldInfos": { /* same structure than fieldErrors but for infos */ },
  "objectFieldErrors": { "object1": { "field1": [ "list of error messages", ... ], "field2": [ ... ] }, "object2": { "field1": [ "list", ... ] } },
  "objectFieldWarnings": { /* same than objectFieldErrors but for warnings */ },
  "objectFieldInfos": { /* same than objectFieldErrors but for infos*/ },
}
```

For object errors, the JSON name matches the request name. For objects in a list, the name is:
`list name in request`+ `idx` + index in the list (starts at 0)

### Server-Side State

Vertigo Vega preserves a server-side state.

This functionality addresses the need to send minimum data to the client (for data security or network constraints) while continuing to use full objects server-side in business services to keep them simple and avoid multiplying input APIs.

With this functionality, you can:
* preserve object state on send, filter fields that are truly needed
* on client return, Vega merges preserved state with new state sent by the client (also filtered)
* use a full business object in the business layer.

!> Server-side state is time-limited, tied to user session, and non-modifiable. Concurrent modifications must be handled at the service level.

Preserving business services on full objects makes them more testable — no need to handle WebService input/output combinatory.

Three annotations are available:
* `ServerSideSave`: on a Method, tells Vega to preserve the returned object and create a reference with a `serverToken` id.
* `ServerSideRead`: on a Parameter, tells Vega to expect JSON with some fields and a `serverToken` reference; Vega merges old state with received data.
* `ServerSideConsume`: Same as `ServerSideRead`, but consumed (invalidated) on call.

Example:
```java
@GET("/contact/{conId}")
@ExcludedFields({ "birthday", "email", "passport" }) // Secret fields excluded
@ServerSideSave  // Full contact kept server-side, exclusion done on JSON convert only
public Contact getContact(@PathParam("conId") final long conId) {
	return loadContact(conId);
}

@PUT("/contact/{conId}")
@ExcludedFields({ "birthday", "email", "passport" }) // Secret fields re-excluded
@ServerSideSave // Saves new state, returns new serverToken
public Contact updateFirstNameContact(
	@ServerSideRead // Reads previous state from sent serverToken
	@IncludedFields({ "firstName" }) // Checks accepted/refused fields (or sends forbidden error)
	final Contact contact) {
		saveContact(contact); // Saves full object, not just firstName, ensures data consistency
		return loadContact(conId); // Returns updated contact
}
```

Request: `GET http://localhost:8080/*myWebApp*/api/contact/1`
Response:
```json
{ "conId":"1", "honorificCode":"MR_", "name":"Martin", "firstName":"Jean", "serverToken":"cb44ab11-4eac-41e9-a3d1-c0fc20ea55e1" }
```

Request: `PUT http://localhost:8080/*myWebApp*/api/contact/1`
```json
{ "firstName":"Jean-denis", "serverToken":"cb44ab11-4eac-41e9-a3d1-c0fc20ea55e1" }
```
Response:
```json
{ "conId":"1", "honorificCode":"MR_", "name":"Martin", "firstName":"Jean-denis", "serverToken":"b04edfef-7385-4d5d-b5ca-23d195c87200" }
```

?> Handled by `ServerSideStateWebServiceHandlerPlugin`

### AccessToken Security

Limited access token management via `TokenManager` / `TokenManagerImpl` and three annotations:

- `AccessTokenPublish`: Generates a temporary token in header `x-access-token`
- `AccessTokenMandatory`: Verifies valid token presence. Returns `HTTP 403 FORBIDDEN` `Invalid access token` if missing.
- `AccessTokenConsume`: Same, but consumes (invalidates) the token after use

### **Rate-Limit** Security

For security, all WebServices published by Vertigo Vega are protected (by default) against massive calls. Limit: 150 calls per user in 5-minute windows (1 call every 2 seconds).
Anonymous users share the same limit counter. Limit is counted per server instance.

Server sends info in *Response* *headers*:
* `X-Rate-Limit-Limit`: Max calls authorized for this request
* `X-Rate-Limit-Remaining`: Remaining calls in current time window
* `X-Rate-Limit-Reset`: Seconds remaining before counter reset

On exceeding the server limit, returns `HTTP 429 TOO_MANY_REQUEST`.

?> Handled by [`RateLimitingWebServiceHandlerPlugin`](https://github.com/vertigo-io/vertigo-extensions/blob/master/vertigo-vega/src/main/java/io/vertigo/vega/plugins/webservice/handler/RateLimitingWebServiceHandlerPlugin.java)
?> Optional parameters:
> - *windowSeconds*: Window size in seconds
> - *limitValue*: Maximum number of calls (within window duration)

### UI Object **DtListDelta**

`DtListDelta` is a specific object used by Vertigo Vega.
Aggregates modifications made to a list: creation, update, or deletion performed client-side and returned to server in 1 call. JSON request must follow this format:
```json
{
	"collCreates": { "clientId1": { ... object1 ... }, "clientId2": { ... object2 ... } },
	"collUpdates": { "clientId4": { ... object4 ... }, "clientId5": { ... object5 ... } },
	"collDeletes": { "clientId6": { ... object6 ... }, "clientId7": { ... object7 ... } }
}
```

Example:
```java
@POST("/contacts/delta")
@ExcludedFields({ "birthday", "email", "passport" })
public String updateContacts(final DtListDelta<Contact> contactsDelta) {
	updateContacts(contactsDelta.getCreates(), contactsDelta.getUpdates(), contactsDelta.getDeletes());
	return "OK : contacts updated";
}
```

?> Equivalent `UiListDelta` retrieves UiObjects (before formatting and validation)

### Annotation **AutoSortAndPagination**

`AutoSortAndPagination` is the simplest way to publish a service with pagination and sorting support.
Starting from a business service returning a full DtList, add a WebService with this annotation returning the service result directly.

Example:
```java
@AutoSortAndPagination
@GET("/contacts")
public DtList<Contact> searchContacts(final ContactCriteria contactCriteria) {
	return contactService.search(contactCriteria);
}
```

How it works:<br/>
**Vega** preserves a server-side list copy and returns:
* _header_: `x-total-count`: total list size
* _header_: `listServerToken`: server-side list token. Client sends it back for sorting or filtering.
* _body_: list portion in JSON format (sorted and filtered)

When the UI sorts or changes page, return:
* _query_: `top`: max number of elements to return
* _query_: `skip`: first element offset
* _query_: `sortFieldName`: field for sorting
* _query_: `sortDesc`: true/false for sort order
* _query_: `listServerToken`: list token (from previous calls)
* Any other necessary data, like any service

Note: you can do the same in WebServices without the annotation (e.g., sort or paginate in the service layer or database).
Same API: add parameter `@QueryParam(".") DtListState dtListState`.

DtListState represents a sub-list state with fields `top`, `skip`, `sortFieldName`, `sortDesc`, `listServerToken`.
Without annotation, use `@QueryParam("") DtListState dtListState` for the same result.

`RateLimitingManager` uses a `RateLimitingStorePlugin`:
- `RateLimitingMemStorePlugin` *(feature `rateLimiting.mem`)* — Local memory storage
- `RateLimitingRedisStorePlugin` *(feature `rateLimiting.redis`)* — Shared Redis storage

### Web Authentication

`WebAuthenticationManager` handles web authentication with 4 plugins:

| Plugin | Feature | Description |
|---|---|---|
| `LocalWebAuthenticationPlugin` | `authentication.local` | Local authentication (login/password) |
| `SAML2WebAuthenticationPlugin` | `authentication.saml2` | SAML 2.0 federation |
| `OIDCWebAuthenticationPlugin` | `authentication.oidc` | OpenID Connect |
| `AzureAdWebAuthenticationPlugin` | `authentication.aad` | Microsoft Azure Active Directory |

Each plugin exposes an `AppLoginHandler` to redirect to the identity provider and process the response.

### SessionLess

`@SessionLess` indicates no HTTP session creation *(for system-to-system WebServices)*.

## Complete Annotation Reference

### Class Annotations

- `PathPrefix`: Common prefix for all class routes
- `RequireApiKey`: Protects all routes with API Key header (feature `webservices.auth.apiKey`)

### Method Annotations

- `Doc`: Swagger documentation
- `AnonymousAccessAllowed`: Allows anonymous access
- `SessionLess`: No HTTP session *(system-to-system WS)*
- `SessionInvalidate`: Invalidates HTTP session
- `GET`: GET route (loading, idempotent)
- `POST`: POST route (save, non-idempotent)
- `PUT`: PUT route (create/update, idempotent)
- `PATCH`: PATCH route (partial update)
- `DELETE`: DELETE route (removal)
- `ExcludedFields` / `IncludedFields`: Controls response fields
- `AccessTokenPublish` / `AccessTokenMandatory` / `AccessTokenConsume`: Access tokens
- `ServerSideSave`: Preserves server-side object copy
- `RequireApiKey`: Protects a single route with API Key
- `FileAttachment`: Response is an attachment

### Parameter Annotations

- `PathParam`: Parameter from URL
- `QueryParam`: Parameter from request/form
- `InnerBodyParam`: JSON body field *(Vega-specific)*
- `HeaderParam`: HTTP header
- `Validate`: Specific `DtObjectValidator` validation *(HTTP 422 on error)*
- `ExcludedFields` / `IncludedFields`: Controls incoming fields *(VSecurityException on violation)*
- `ServerSideRead`: Reloads server copy and merges changes
- `AutoSortAndPagination`: Automatic pagination and sorting

## References

*Part of the motivation/inspiration for this module comes from [OWASP](https://www.owasp.org/index.php/REST_Security_Cheat_Sheet#Input_validation_101) and [@veesahni](http://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api#rate-limiting)*

---

## For Experts

### Managers

| Manager | Impl | Feature |
|---|---|---|
| `WebServiceManager` | `WebServiceManagerImpl` | `webservices` |
| `TokenManager` | `TokenManagerImpl` | `webservices.token` |
| `RateLimitingManager` | `RateLimitingManagerImpl` | `rateLimiting` |
| `WebAuthenticationManager` | `WebAuthenticationManagerImpl` | `authentication` |

### Features

| Flag | Params | Added Components |
|---|---|---|
| `webservices` | — | `WebServiceManagerImpl` + base plugins |
| `webservices.javalin` | `Param...` | `JavalinWebServerPlugin` |
| `webservices.cors` | `originCORSFilter` | `CorsAllowerWebServiceHandlerPlugin` |
| `webservices.rateLimiting` | `Param...` | `RateLimitingWebServiceHandlerPlugin` |
| `webservices.security` | — | `SessionInvalidateWebServiceHandlerPlugin` + `SessionWebServiceHandlerPlugin` + `SecurityWebServiceHandlerPlugin` |
| `webservices.auth.apiKey` | `Param...` | `ApiKeyWebServiceHandlerPlugin` |
| `webservices.token` | `tokens` | `ServerSideStateWebServiceHandlerPlugin` + `AccessTokenWebServiceHandlerPlugin` + `TokenManagerImpl` |
| `webservices.json` | — | — *(via buildFeatures)* |
| `webservices.swagger` | — | `SwaggerWebServices` |
| `webservices.catalog` | — | `CatalogWebServices` |
| `webservices.healthcheck` | — | `HealthcheckWebServices` |
| `webservices.proxyclient` | — | `WebServiceClientAmplifierMethod` |
| `rateLimiting` | `Param...` | `RateLimitingManagerImpl` |
| `rateLimiting.redis` | `Param...` | `RateLimitingRedisStorePlugin` |
| `rateLimiting.mem` | `Param...` | `RateLimitingMemStorePlugin` |
| `authentication` | `Param...` | `WebAuthenticationManagerImpl` |
| `authentication.saml2` | `Param...` | `SAML2WebAuthenticationPlugin` |
| `authentication.oidc` | `Param...` | `OIDCWebAuthenticationPlugin` |
| `authentication.aad` | `Param...` | `AzureAdWebAuthenticationPlugin` |
| `authentication.local` | `Param...` | `LocalWebAuthenticationPlugin` |

### Plugins

**Handler Chain**: `LogExceptionsHandlerPlugin` (5), `ExceptionWebServiceHandlerPlugin` (10), `CorsAllowerWebServiceHandlerPlugin` (20), `AnalyticsWebServiceHandlerPlugin` (30), `JsonConverterWebServiceHandlerPlugin` (40), `ApiKeyWebServiceHandlerPlugin` (45), `SessionInvalidateWebServiceHandlerPlugin` (50), `SessionWebServiceHandlerPlugin` (60), `SecurityWebServiceHandlerPlugin` (70), `ServerSideStateWebServiceHandlerPlugin` (80), `AccessTokenWebServiceHandlerPlugin` (90), `RateLimitingWebServiceHandlerPlugin` (100), `ValidatorWebServiceHandlerPlugin` (110), `RestfulServiceWebServiceHandlerPlugin` (120)

**WebServer**: `JavalinWebServerPlugin`, `VegaJavalinFilter`

**JSON**: `DefaultJsonConverter`, `DtObjectJsonConverter`, `DtListJsonConverter`, `DtListDeltaJsonConverter`

**Rate Limiting**: `RateLimitingMemStorePlugin`, `RateLimitingRedisStorePlugin`

**Web Authentication**: `LocalWebAuthenticationPlugin`, `SAML2WebAuthenticationPlugin`, `OIDCWebAuthenticationPlugin`, `AzureAdWebAuthenticationPlugin`

**Scanner**: `AnnotationsWebServiceScannerPlugin` (scans `@GET`, `@POST`, etc. annotations)

### Configuration

`buildFeatures()` (always active): `GoogleJsonEngine` (implements `JsonEngine`).