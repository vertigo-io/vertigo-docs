# Vega

Le module **Vega** permet de mettre en place simplement des WebServices dans l'application.
Ce module est orienté pour le développement d'applications *Single-Page-Application*, mais peut évidemment être utilisé pour des WebServices d'applications Web standards ou de SI à SI.
Il intègre une chaîne de plugins de traitement (handler chain), une authentification web (SAML2, OIDC, Azure AD, local), un système de rate limiting, et un ensemble de solutions *production-ready* pour accélérer et sécuriser l'application.

Vega propose également un client de WebService pour appeler simplement des WebServices d'un autre nœud Vertigo, ou d'une autre application.

## Composants internes

En interne, le module utilise [Javalin](https://github.com/tipsy/javalin) pour le serveur embarqué et Servlet pour les environnements WAR.
Il propose une publication de l'API par le standard [Swagger](https://swagger.io/).
Pour publier les WebServices, il suffit d'un ensemble d'annotations sur une façade de vos services métier. Les annotations sont volontairement une sous-partie du standard [JAX-RS](https://javaee.github.io/javaee-spec/javadocs/javax/ws/rs/package-summary.html).

### Handler Chain (Pipe)

Chaque requête traverse une chaîne de `WebServiceHandlerPlugin` classés par priorité :

| Priorité | Plugin | Rôle |
|---|---|---|
| 10 | `ExceptionWebServiceHandlerPlugin` | Gestion des exceptions |
| 20 | `CorsAllowerWebServiceHandlerPlugin` | Gestion CORS *(feature `webservices.cors`)* |
| 30 | `SessionInvalidateWebServiceHandlerPlugin` | Invalidation de session *(feature `webservices.security`)* |
| 40 | `SessionWebServiceHandlerPlugin` | Gestion session *(feature `webservices.security`)* |
| 50 | `RateLimitingWebServiceHandlerPlugin` | Rate limiting *(feature `webservices.rateLimiting`)* |
| 60 | `SecurityWebServiceHandlerPlugin` | Sécurité globale *(feature `webservices.security`)* |
| — | `ApiKeyWebServiceHandlerPlugin` | Clé API *(feature `webservices.auth.apiKey`)* |
| — | `AnalyticsWebServiceHandlerPlugin` | Analyse analytique |
| 70 | `AccessTokenWebServiceHandlerPlugin` | Tokens d'accès *(feature `webservices.token`)* |
| 80 | `JsonConverterWebServiceHandlerPlugin` | Conversion JSON |
| 90 | `ValidatorWebServiceHandlerPlugin` | Validation DTO |
| — | `ServerSideStateWebServiceHandlerPlugin` | État server-side *(feature `webservices.token`)* |
| 120 | `RestfulServiceWebServiceHandlerPlugin` | Routage vers le service métier |
| — | `LogExceptionsHandlerPlugin` | Journalisation |

## Quick start server

1. La classe du webservice doit implémenter l'interface `WebServices`
2. La classe doit être déclarée comme un *Composant* Vertigo, concrètement, cela est fait par [l'autodiscovery du module métier](getting-started/realworld_helloworld.md#_5-configuration-de-l39application)
3. Ajouter les annotations sur les méthodes, exemple :
```java
@AnonymousAccessAllowed
@GET("/anonymousTest")
```
4. Ajouter la feature *webservices* dans la configuration :

```yaml
modules:
  io.vertigo.vega.VegaFeatures:
    features:
      - webservices:
    featuresConfig:
      - webservices.javalin:
          apiPrefix: /api
          embeddedServer: true
```

5. Déclarer le filtre dans le fichier *web.xml* *(optionnel si mode serveur intégré)* :

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

6. Démarrer l'application
7. **C'est bon**. Vous pouvez appeler votre webservice : [http://localhost:8080/*maWebApp*/api/anonymousTest](http://localhost:8080/*maWebApp*/api/anonymousTest)

Vertigo propose des WebServices intégrés : **Swagger**, **Catalog** et **Healthcheck** :

- Feature `webservices.swagger` → `SwaggerWebServices` (interface Swagger UI + API JSON)
- Feature `webservices.catalog` → `CatalogWebServices` (catalogue des services)
- Feature `webservices.healthcheck` → `HealthcheckWebServices` (tests de santé)

?> Vega peut être lancé en mode serveur intégré avec la feature `webservices.javalin` (paramètre `embeddedServer: true`), dans ce cas, il est inutile de spécifier un filtre dans le *web.xml*.

## Quick start client

Pour appeler un WebService distant :

1. Reproduire l'API du WebService avec une interface Java ayant l'annotation `@WebServiceProxyAnnotation`. Elle sera détectée par Vertigo comme les autres composants par [l'autodiscovery du module métier](getting-started/realworld_helloworld.md#_5-configuration-de-l39application)
2. Ajouter la feature `webservices.proxyclient` dans la configuration de Vega :
```yaml
  io.vertigo.vega.VegaFeatures:
    features:
      - webservices:
    featuresConfig:
      - webservices.proxyclient:
```
3. Ajouter le connecteur HttpClient dans la configuration :
```yaml
  io.vertigo.connectors.httpclient.HttpClientConnector:
    features:
      - httpclient:
          urlPrefix: http://mySpUrl:8080
```
4. Ajouter les annotations sur les méthodes de l'interface :
```java
@WebServiceProxyAnnotation
@PathPrefix("/test")
public interface SimplerClientTestWebServices {

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
5. Utiliser le WebService en injectant l'interface dans votre service métier :
```java
  @Inject
  private SimplerClientTestWebServices otherWService;

  public void myBusinessService() {
    otherWService.login();
    final Contact result = otherWService.testRead(2);
  }
```

?> Le connecteur `HttpClient` propose d'autres paramètres optionnels :
- `name` pour gérer plusieurs *endpoint*, il faut alors préciser le nom de la connexion dans l'annotation `@WebServiceProxyAnnotation`
- `connectTimeoutSecond` pour définir le timeout
- `proxy` et `proxyPort` pour gérer les proxy

## API

### Code exemples :
De nombreux exemples complets sont présents dans les tests de Vertigo sur GitHub

### Syntaxe des routes

Lors de la définition des routes, `{myParamName}` déclare une variable de l'URL utilisée comme paramètre du service.
```java
@GET("/contact/{id}")
public Contact getContact(@PathParam("id") final int contactId) { ... }
```

### Paramètres

Vega mappe automatiquement la requête JSON entrante vers votre méthode. Les annotations indiquent la source des données (paramètres URL, body, headers…). Par défaut, le contenu est attendu dans le body (**Attention** : HTTP spécifie que les requêtes *GET* n'ont pas de body).

Vega peuple quelques paramètres implicites :
- `UiMessageStack` : pile des messages à retourner (Success, Info, Warning, Error)
- `HttpServletRequest` : Requête HTTP
- `HttpServletResponse` : Réponse HTTP

### JSON Reader

Le `JsonReader` et ses implémentations permettent de lire des données JSON depuis différentes sources :

| Reader | Source | Annotation |
|---|---|---|
| `BodyJsonReader` | Body de la requête | (par défaut) |
| `QueryJsonReader` | Query parameters | — |
| `PathJsonReader` | Chemin URL | `@PathParam` |
| `HeaderJsonReader` | Headers HTTP | `@HeaderParam` |
| `InnerBodyJsonReader` | Champ du body | `@InnerBodyParam` |
| `RequestJsonReader` | Requête complète | — |

### Objet de retour

Le résultat est automatiquement sérialisé en JSON. La sérialisation est optimisée pour les objets Vertigo :

- `Entity` : Objet métier persistant
- `UiObject` : Objet composite générique pour charger un contexte complet de page
- `UiContext` : Collection nommée d'objets
- `FacetedQueryResult` : Résultat de recherche avec facettes et highlights
- `DtListDelta` : Modifications agrégées d'une liste
- `UiList<MyDto>` : Liste d'objets UI
- `ExtendedObject` : Objet extensible

```java
@GET("/uiContext/{contactIdFrom}/{contactIdTo}")
public UiContext testUiContext(@PathParam("contactIdFrom") final long contactIdFrom, @PathParam("contactIdTo") final long contactIdTo) {
	final UiContext uiContext = new UiContext();
	uiContext.put("contactFrom", loadContact(contactIdFrom));
	uiContext.put("contactTo", loadContact(contactIdTo));
	return uiContext;
}
```

### Handler des Exceptions

| Code HTTP | Exception | Rôle |
|---|---|---|
| `200` | — | Succès |
| `201` | — | Créé (méthode commence par `create`) |
| `204` | — | Succès, pas de données en retour |
| `400` | `JsonSyntaxException` | Erreur de syntaxe |
| `401` | `SessionException` | Pas de session valide |
| `403` | `VSecurityException` | Droits insuffisants |
| `404` | — | Pas de WebService trouvé |
| `422` | `ValidationUserException` | Erreur de validation (message détaillé avec `globalErrors`, `fieldErrors`, `objectFieldErrors`) |
| `429` | `TooManyRequestException` | Rate limiting dépassé |
| `500` | — | Erreur interne |

### Validation

Le framework de validation (`DtObjectValidator`, `DefaultDtObjectValidator`) intercepte les erreurs de saisie et retourne HTTP 422 avec une structure JSON détaillée :
- `globalErrors`, `globalWarnings`, `globalInfos`, `globalSuccess`
- `fieldErrors`, `fieldWarnings`, `fieldInfos`
- `objectFieldErrors`, `objectFieldWarnings`, `objectFieldInfos`

Pour les objets dans une liste, le nom est `nomListe.idxN` (ex : `"persons.idx2"`).

### État Server-side

Avec `ServerSideRead`, `ServerSideSave` et `ServerSideConsume`, Vega conserve un état côté serveur avec un `serverToken`. Couplé à `@IncludedFields` et `@ExcludedFields`, cela permet un contrôle fin de sécurité des données échangées.

### Sécurité AccessToken

La gestion des tokens d'accès limitée est assurée par `TokenManager` / `TokenManagerImpl` et trois annotations :

- `AccessTokenPublish` : Génère un token temporaire dans le header `x-access-token`
- `AccessTokenMandatory` : Vérifie la présence d'un token valide (403 si invalide)
- `AccessTokenConsume` : Idem, mais consomme (invalide) le token après usage

### Sécurité Rate-Limit

Par défaut : 150 appels par utilisateur par fenêtre de 5 minutes. Headers de réponse : `X-Rate-Limit-Limit`, `X-Rate-Limit-Remaining`, `X-Rate-Limit-Reset$. Dépassement → HTTP 429.

Le `RateLimitingManager` utilise un `RateLimitingStorePlugin` :
- `RateLimitingMemStorePlugin` *(feature `rateLimiting.mem`)* — Stockage mémoire local
- `RateLimitingRedisStorePlugin` *(feature `rateLimiting.redis`)* — Stockage Redis partagé

### Web Authentication

Le `WebAuthenticationManager` gère l'authentification web avec 4 plugins :

| Plugin | Feature | Description |
|---|---|---|
| `LocalWebAuthenticationPlugin` | `authentication.local` | Authentification locale (login/mot de passe) |
| `SAML2WebAuthenticationPlugin` | `authentication.saml2` | Fédération SAML 2.0 |
| `OIDCWebAuthenticationPlugin` | `authentication.oidc` | OpenID Connect |
| `AzureAdWebAuthenticationPlugin` | `authentication.aad` | Microsoft Azure Active Directory |

Chaque plugin expose un `AppLoginHandler` pour rediriger vers le fournisseur d'identité et traiter la réponse.

### Annotation AutoSortAndPagination

L'annotation `@AutoSortAndPagination` ajoute automatiquement la pagination et le tri. Vega conserve une copie de la liste avec un `listServerToken`, retourne une portion paginée dans le body et le `x-total-count` dans les headers.

Sans annotation, utiliser `@QueryParam("") DtListState dtListState` pour le même résultat.

### SessionLess

L'annotation `@SessionLess` indique de ne pas créer de session HTTP *(pour les WebServices SI à SI)*.

## Référence complète des Annotations

### Annotations de classe

- `PathPrefix` : Préfixe commun à toutes les routes de la classe
- `RequireApiKey` : Protège toutes les routes avec un header API Key (feature `webservices.auth.apiKey`)

### Annotations de méthode

- `Doc` : Documentation Swagger
- `AnonymousAccessAllowed` : Autorise l'accès anonyme
- `SessionLess` : Pas de session HTTP *(WS SI à SI)*
- `SessionInvalidate` : Invalide la session HTTP
- `GET` : Route GET (chargement, idempotent)
- `POST` : Route POST (enregistrement, non idempotent)
- `PUT` : Route PUT (création/mise à jour, idempotent)
- `PATCH` : Route PATCH (mise à jour partielle)
- `DELETE` : Route DELETE (suppression)
- `ExcludedFields` / `IncludedFields` : Contrôle les champs de la réponse
- `AccessTokenPublish` / `AccessTokenMandatory` / `AccessTokenConsume` : Tokens d'accès
- `ServerSideSave` : Conserve une copie serveur de l'objet retourné
- `RequireApiKey` : Protège une seule route avec API Key
- `FileAttachment` : Indique que la réponse est une pièce jointe

### Annotations de paramètre

- `PathParam` : Paramètre depuis l'URL
- `QueryParam` : Paramètre depuis la requête/formulaire
- `InnerBodyParam` : Champ du body JSON *(spécifique Vega)*
- `HeaderParam` : Header HTTP
- `Validate` : Validation `DtObjectValidator` spécifique *(HTTP 422 si erreur)*
- `ExcludedFields` / `IncludedFields` : Contrôle les champs entrants *(VSecurityException si violation)*
- `ServerSideRead` : Recharge la copie serveur et fusionne les modifications
- `AutoSortAndPagination` : Pagination et tri automatique

## Références

*Une partie de la motivation / de l'inspiration de ce module vient de l'[OWASP](https://www.owasp.org/index.php/REST_Security_Cheat_Sheet#Input_validation_101) et de [@veesahni](http://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api#rate-limiting)*

---

## Pour les experts

### Managers

| Manager | Impl | Feature |
|---|---|---|
| `WebServiceManager` | `WebServiceManagerImpl` | `webservices` |
| `TokenManager` | `TokenManagerImpl` | `webservices.token` |
| `RateLimitingManager` | `RateLimitingManagerImpl` | `rateLimiting` |
| `WebAuthenticationManager` | `WebAuthenticationManagerImpl` | `authentication` |

### Features

| Flag | Params | Composants ajoutés |
|---|---|---|
| `webservices` | — | `WebServiceManagerImpl` + plugins de base |
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

**Handler Chain** : `ExceptionWebServiceHandlerPlugin` (10), `CorsAllowerWebServiceHandlerPlugin` (20), `SessionInvalidateWebServiceHandlerPlugin` (30), `SessionWebServiceHandlerPlugin` (40), `RateLimitingWebServiceHandlerPlugin` (50), `SecurityWebServiceHandlerPlugin` (60), `ApiKeyWebServiceHandlerPlugin`, `AnalyticsWebServiceHandlerPlugin`, `AccessTokenWebServiceHandlerPlugin` (70), `JsonConverterWebServiceHandlerPlugin` (80), `ValidatorWebServiceHandlerPlugin` (90), `RestfulServiceWebServiceHandlerPlugin` (120), `ServerSideStateWebServiceHandlerPlugin`, `LogExceptionsHandlerPlugin`

**WebServer** : `JavalinWebServerPlugin`, `VegaJavalinFilter`

**JSON** : `DefaultJsonConverter`, `DtObjectJsonConverter`, `DtListJsonConverter`, `DtListDeltaJsonConverter`

**Rate Limiting** : `RateLimitingMemStorePlugin`, `RateLimitingRedisStorePlugin`

**Web Authentication** : `LocalWebAuthenticationPlugin`, `SAML2WebAuthenticationPlugin`, `OIDCWebAuthenticationPlugin`, `AzureAdWebAuthenticationPlugin`

**Scanner** : `AnnotationsWebServiceScannerPlugin` (scan des annotations `@GET`, `@POST`, etc.)

### Configuration

`buildFeatures()` (toujours actif) : `GoogleJsonEngine` (implémente `JsonEngine`).
