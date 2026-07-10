# WebServices

The Vega module of Vertigo simplifies the creation of REST WebServices, allowing your application to easily interconnect with application ecosystems by offering digital services as APIs.

This module is also suitable for creating REST APIs consumed by Single Page Applications.

The JSON exchange format was preferred for its popularity and its ability to be easily consumed by a wide range of technologies. Vega's goal being to open the application to the world, it makes sense to use the lingua franca of data exchange for the broadest possible reach.

## Configuration

To use Vega features, this module must be added to the application configuration.
For more details, refer to the chapter dedicated to application [configuration](/en/basic/configuration).

Vega offers two operating methods:

- as a servlet filter, when the application runs in a servlet container (e.g., Tomcat)
- as an internal web server (Jetty) for executable JARs



### Servlet Filter Case

Here is a typical YAML configuration for an application using the Vega module and the Javalin connector:

```yaml
modules:
  io.vertigo.connectors.javalin.JavalinFeatures:
    features:
      - standalone:
  io.vertigo.datamodel.DataModelFeatures:
  io.vertigo.vega.VegaFeatures:
    features:
        - webservices:
    featuresConfig:
        - webservices.javalin:
            apiPrefix: /api
        - webservices.security:
        - webservices.swagger:
```

Additionally, here is the filter to add in the servlet for this case:

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

!> Here we chose to use a prefix for all webservice routes `/api`. This is a practice we encourage as it avoids naming conflicts.

### Embedded Web Server Case

Here is a typical YAML configuration for an application using the Vega module with the embedded server mode:

```yaml
modules:
  io.vertigo.connectors.javalin.JavalinFeatures:
    features:
      - embeddedServer:
          port: 8080
  io.vertigo.datamodel.DataModelFeatures:
  io.vertigo.vega.VegaFeatures:
    features:
        - webservices:
    featuresConfig:
        - webservices.javalin:
            apiPrefix: /api
        - webservices.security:
        - webservices.swagger:
```



> For the complete list of available features, refer to the chapter dedicated to [Vega](/en/extensions/vega)

## Creating a WebService

A webservice is a way to make data or a business service available via a web interface.

Vega allows exposing a Java method on the web and defining the behavior of this 'endpoint' through annotations.

> In Vertigo, we prefer creating 'WebServices' type components that group webservices offered on the same business or functional domain within a single class.

In Vertigo, any object offering services is a component. A webservice is no exception; it is a component, but with its own specifics.

Therefore, first of all, reading the [chapter](/en/basic/composants) dedicated to components is useful.

A webservice is a component that must implement the `io.vertigo.vega.webservice.WebServices` interface.

This marker not only allows the developer to differentiate components by their features and usage, but also enables the Vega module to identify components whose methods must be analyzed and converted to WebServices.

To create a webservice, start by creating the component that will host the methods to publish:

```java

public class HelloWebServices implements WebServices {
	// methods will go there

}
```

Then, let's add the method to be exposed:

```java
public class HelloWebServices implements WebServices {

	@AnonymousAccessAllowed
	@GET("/hello")
	public String hello() {
		return "hello world";
	}

}
```

The `hello` method takes no arguments and returns a string. This is a minimal example for demonstration purposes.

The `@GET` annotation allows specifying

 - the route to be used: here */hello*
 - the HTTP VERB to be used: here *GET*

Similar annotations exist for different HTTP verbs: `@POST`, `@PUT`, `@DELETE`, `@PATCH`

> To learn more about routes and verbs, you can refer to best practices we propose [here](https://github.com/vertigo-io/vertigo-core/wiki/routes).

For simplicity and conciseness, it is possible to add a prefix to all routes of methods in the same class by using the `@PathPrefix` annotation on the class.

!> Here the `@AnonymousAccessAllowed` annotation allows webservice access without authentication. This behavior should not be used in production.

## Using Parameters

To go further in creating a WebService, it is of course possible to complicate method signatures and accept input parameters while returning objects and collections of objects.

Regarding input and output parameters, they can be of different kinds:

- Java primitives

- Objects

- Collections of objects


Regarding input parameters, they can be retrieved from:

- the URL: via the `@PathParam` annotation
- URL parameters: via the `@QueryParam` annotation
- the request body (in JSON format): via the `@InnerBodyParam` annotation
- a header: via the `@HeaderParam` annotation

Regarding return parameters, these will be automatically serialized (converted) to JSON format.

Thus, it is possible to write, for example, the following webservices:

```java
@PUT("/movies/{id}")
public Movie updateMovie(final @PathParam("id") long id, final Movie movie) {
    movieServices.saveMovie(movie);
	return movieServices.getMovie(id);
}
```

```java
@POST("/movies/_search")
public FacetedQueryResult search(
    @InnerBodyParam("criteria") final String criteria,
	@InnerBodyParam("facets") final SelectedFacetValues selectedFacetValues,
	@InnerBodyParam("group") final Optional<String> clusteringFacetName,
    final DtListState dtListState) {
		return movieServices.searchMovies(criteria, selectedFacetValues, dtListState,
				clusteringFacetName);
}
```



## Securing the Webservice

It is absolutely essential to secure webservice calls.

To address this security concern, many mechanisms are available in Vega.

By default, all WebServices are accessible only to authenticated users. This is the first level of security. Obviously, it is **necessary** but **not sufficient**.

To go further, you can use features from the Vertigo-Account module, which provides a security model applicable to WebServices.

Thus, during a Webservice call, you can verify:

- That the authenticated user has one of the required rights to be authorized to call it
- That entities (business objects in the Vertigo sense) can be manipulated by the authenticated user

```java
@Secured("CONTACT$READ")
@GET("/{conId}")
public Contact read(@PathParam("conId") final long conId) {
	final Contact contact = contactDao.get(conId);
	return contact;
}
```

> Here we check that the connected user has the CONTACT$READ right, meaning the ability to read contacts

```java
@PUT("/contactView")
public ContactView updateContactView(
    @SecuredOperation("WRITE") final ContactView contactView) {
		return contactView;
}
```

> Here we check that the connected user has write authorization on the ContactView entity. This security check depends on both the user's attributes and the Contact's attributes. This is therefore a very fine-grained security check.

## SwaggerApi

The API created with this module is exposed in standard Swagger format. Vertigo includes the API availability through the standard Swagger UI.
Simply add the webService facade: `io.vertigo.vega.impl.webservice.catalog.SwaggerWebServices`

![](./images/swaggerUi.png)

The `SwaggerApi` object is represented as a `LinkedHashMap<String, Object>`.

Rules for constructing Swagger definition names:

- The `$` character in the webservice definition name (`webServiceDefinition.getName()`) acts as a separator to structure nested definitions
- Multiple underscore sequences are reduced to a single `_` (e.g., `__` → `_`)
- There is **no** automatic replacement of `$` by `_`

The JSON facets `FacetedQueryResult` exposes the `isMultiSelectable` attribute on each facet. `FacetedQueryResultJsonSerializerV5` is the **default** serializer.

## Going Further

It is possible to enrich Webservice behavior with Vega by using the following features:

- **rate-limiting**: Limiting the number of allowed calls within a sliding time window
- **tokens**: Generation and consumption of tokens to secure critical operations
- **server-side**: Server-side state management to efficiently handle certain processes
- **etc...**

All these features and their APIs are available in [this](/en/extensions/vega) chapter.

## CORS (Cross-Origin Resource Sharing)

The `CorsAllowerWebServiceHandlerPlugin` plugin manages cross-origin requests. It is enabled via the `webservices.cors` feature.

The configuration parameters are:

- `originCORSFilter` (required): filters allowed origins
- `methodCORSFilter` (optional): filters allowed HTTP methods, default `GET, POST, DELETE, PUT, OPTIONS`

URI validation is strict: only complete URIs without path or query string are accepted.

The `url-include-pattern` and `url-exclude-pattern` parameters allow restricting the plugin to matching URLs.

## OIDC (OpenID Connect)

Vega supports OIDC authentication through the following interfaces and classes:

- `AppLoginHandler<T>`: application login handler interface
- `OIDCAppLoginHandler`: marker for an OIDC login handler
- `WebAuthenticationPlugin<T>`: generic web authentication plugin
- `OIDCWebAuthenticationPlugin`: OIDC authentication plugin with the following parameters:
  - `scopes`: OIDC scopes to request
  - `urlPrefix`: URL prefix
  - `urlHandlerPrefix`: URL prefix for handlers
  - `externalUrl`: external URL of the application
- `connectorName`: OIDC connector name

## LogExceptionsHandlerPlugin

The `LogExceptionsHandlerPlugin` is enabled by default, with no configuration parameter. It is always active and generates an error log (status, verb, path, path params) for any HTTP response with a code between 500 and 599.

## Rate Limiting

Rate limiting allows limiting the number of calls allowed within a sliding time window.

The IPv6 localhost address `[0:0:0:0:0:0:0:1]` is added by default to the list of excluded IPs.

## For Experts

### Security Plugins

| Plugin | Feature | Stack Index | Description |
|---|---|---|---|
| `AccessTokenWebServiceHandlerPlugin` | `webservices.token` | 90 | Generation and verification of disposable tokens for sensitive actions |
| `ApiKeyWebServiceHandlerPlugin` | `webservices.auth.apiKey` | 45 | API key authentication. Parameters: `apiKey` (String), `headerName` (Optional<String>) |

### System Services

| Service | Feature | Route | Description |
|---|---|---|---|
| `HealthcheckWebServices` | `webservices.healthcheck` | Auto-generated | Platform monitoring endpoint |
| `CatalogWebServices` | `webservices.catalog` | Auto-generated | Webservice catalog (metadata, definitions) |

### Client Proxy

The feature `webservices.proxyclient` enables the `AmplifierMethod` `WebServiceClientAmplifierMethod` which dynamically generates Java proxies from a `WebServiceDefinition`. The proxy uses an internal `HttpRequestBuilder` to build URLs and `DefaultJsonSerializer` for JSON serialization.

### HandlerChain — Internal Architecture

Vega processes each HTTP request through a chain of plugins (`WebServiceHandlerPlugin`) sorted by `getStackIndex()`. The `HandlerChain` iterates over active handlers and calls `accept(WebServiceDefinition)` to determine whether a handler applies to this webservice. The first one that accepts executes `handle()` and passes to the next via `chain.handle()`. If the last handler does not produce a body, an `IllegalStateException` is thrown.

The maximum number of handlers in a chain is 50 (infinite loop detection via `MAX_NB_HANDLERS`).

#### Handler Order

| Index | Handler | Enabled by |
|---|---|---|
| 5 | `LogExceptionsHandlerPlugin` | Always active |
| 10 | `ExceptionWebServiceHandlerPlugin` | Always active |
| 20 | `CorsAllowerWebServiceHandlerPlugin` | `webservices.cors` |
| 30 | `AnalyticsWebServiceHandlerPlugin` | Always active |
| 40 | `JsonConverterWebServiceHandlerPlugin` | Always active |
| 45 | `ApiKeyWebServiceHandlerPlugin` | `webservices.auth.apiKey` |
| 50 | `SessionInvalidateWebServiceHandlerPlugin` | `webservices.security` |
| 60 | `SessionWebServiceHandlerPlugin` | `webservices.security` |
| 70 | `SecurityWebServiceHandlerPlugin` | `webservices.security` |
| 80 | `ServerSideStateWebServiceHandlerPlugin` | `webservices.token` |
| 90 | `AccessTokenWebServiceHandlerPlugin` | `webservices.token` |
| 100 | `RateLimitingWebServiceHandlerPlugin` | `webservices.rateLimiting` |
| 110 | `ValidatorWebServiceHandlerPlugin` | Always active |
| **120** | `RestfulServiceWebServiceHandlerPlugin` | Always active ← **always last** |

A custom handler must have a `getStackIndex()` between 0 and 119. The last one (`RestfulServiceWebServiceHandlerPlugin`, index 120) is the one that executes the target Java method and returns the body.

### Servlet Filters vs HandlerChain

Servlet Filters execute **before** the HandlerChain and operate at the Servlet Spec level (not Vega). They do not filter by `WebServiceDefinition` but by URL pattern (`url-include-pattern` / `url-exclude-pattern` via `AbstractFilter`).

| Filter | Role |
|---|---|
| `SetCharsetEncodingFilter` | Forces UTF-8 charset on requests |
| `CompressionFilter` | Compresses response if `Accept-Encoding: gzip/deflate` |
| `CacheControlFilter` | Sets `Cache-Control` headers (private, max-age, no-cache) |
| `SecurityFilter` | Adds HTTP security headers (X-Frame-Options, X-XSS-Protection) |
| `ContentSecurityPolicyFilter` | Manages CSP headers |
| `HeaderControlFilter` | Controls input/output headers |
| `AuthorizationWebFilter` | Verifies `@Secured` at Servlet level |
| `RateLimitingFilter` | Rate limiting at Servlet level (separate from handler) |
| `AnalyticsFilter` | Collects metrics at Servlet level |
| `DelegateAuthenticationFilterHandler` | Delegates authentication to an external provider |

### Lifecycle

1. **DefinitionSpace**: `AnnotationsWebServiceScannerPlugin` scans components implementing `WebServices`, extracts annotated methods (`@GET`, `@POST`, ...) and generates `WebServiceDefinition`
2. **ComponentSpace**: `WebServiceManager` assembles `WebServiceDefinition` and sorts `WebServiceHandlerPlugin` by `getStackIndex()`
3. **Runtime**: HTTP Request → Servlet Filter chain → HandlerChain → target Java method → JSON response

### Authentication Plugins

| Plugin | Feature | Description |
|---|---|---|
| `LocalWebAuthenticationPlugin` | `authentication.local` | Local authentication via form |
| `OIDCWebAuthenticationPlugin` | `authentication.oidc` | OpenID Connect |
| `SAML2WebAuthenticationPlugin` | `authentication.saml2` | SAML 2.0 |
| `AzureAdWebAuthenticationPlugin` | `authentication.aad` | Azure Active Directory |

### RateLimiting

The `RateLimitingWebServiceHandlerPlugin` implements rate limiting via a sliding window. The storage backend is configurable:

| Backend | Feature | Description |
|---|---|---|
| Local memory | `rateLimiting.mem` | Local storage, not persisted, not shared |
| Redis | `rateLimiting.redis` | Shared storage via Redis, cluster compatible |

The IPv6 localhost address `[0:0:0:0:0:0:0:1]` is excluded by default from all limiting.

### WebServiceClient (Proxy)

The feature `webservices.proxyclient` enables the `AmplifierMethod` `WebServiceClientAmplifierMethod` which dynamically generates Java proxies from a `WebServiceDefinition`. The proxy uses an internal `HttpRequestBuilder` to build HTTP requests (method, URL, headers, JSON body).

### Debug

- Enable logging of `WebServiceManager` to trace webservice loading and HandlerChain assembly
- `LogExceptionsHandlerPlugin` logs automatically all 5xx responses (status, verb, path, path params)
- `AnalyticsWebServiceHandlerPlugin` exposes performance metrics (execution time per webservice)
- To debug handler order, verify that each `accept()` returns `true` only for targeted webservices
