# Vega

Le module **Vega** permet de mettre en place simplement des WebServices dans l'application.
Ce module est orienté pour le développement d'applications *Single-Page-Application*, mais peut évidemment être utilisé pour des WebServices d'applications Web standards ou de SI à SI.
Il intègre une chaîne de plugins de traitement (handler chain), une authentification web (SAML2, OIDC, Azure AD, local), un système de rate limiting, et un ensemble de solutions *production-ready* pour accélérer et sécuriser l'application.

Vega propose également un client de WebService pour appeler simplement des WebServices d'un autre nœud Vertigo, ou d'une autre application.

## Composants internes

En interne, le module utilise [Javalin](https://github.com/tipsy/javalin) pour le serveur embarqué et Servlet pour les environnements WAR.
Il propose une publication de l'API par le standard [Swagger](https://swagger.io/).
Pour publier les WebServices, il suffit d'un ensemble d'annotations sur une façade de vos services métier. Les annotations sont volontairement une sous-partie du standard [JAX-RS](https://javaee.github.io/javaee-spec/javadocs/javax/ws/rs/package-summary.html)

Pour la partie cliente, le module utilise le HttpClient du JDK.
Pour appeler des WebServices, il suffit d'une interface avec les annotations standard de Vega.

### Handler Chain (Pipe)

Chaque requête traverse une chaîne de `WebServiceHandlerPlugin` classés par priorité :

| Priorité | Plugin | Rôle |
|---|---|---|
| 5 | `LogExceptionsHandlerPlugin` | Log des erreurs 5XX |
| 10 | `ExceptionWebServiceHandlerPlugin` | Gestion des exceptions |
| 20 | `CorsAllowerWebServiceHandlerPlugin` | Gestion CORS *(feature `webservices.cors`)* |
| 30 | `AnalyticsWebServiceHandlerPlugin` | Tracing AnalyticsManager |
| 40 | `JsonConverterWebServiceHandlerPlugin` | Conversion JSON (entrée/sortie) |
| 45 | `ApiKeyWebServiceHandlerPlugin` | Clé API *(feature `webservices.auth.apiKey`)* |
| 50 | `SessionInvalidateWebServiceHandlerPlugin` | Invalidation de session *(feature `webservices.security`)* |
| 60 | `SessionWebServiceHandlerPlugin` | Gestion session *(feature `webservices.security`)* |
| 70 | `SecurityWebServiceHandlerPlugin` | Sécurité globale *(feature `webservices.security`)* |
| 80 | `ServerSideStateWebServiceHandlerPlugin` | État server-side *(feature `webservices.token`)* |
| 90 | `AccessTokenWebServiceHandlerPlugin` | Tokens d'accès *(feature `webservices.token`)* |
| 100 | `RateLimitingWebServiceHandlerPlugin` | Rate limiting *(feature `webservices.rateLimiting`)* |
| 110 | `ValidatorWebServiceHandlerPlugin` | Validation DTO |
| 120 | `RestfulServiceWebServiceHandlerPlugin` | Routage vers le service métier |

## Quick start server

1. La classe du webservice doit implémenter l'interface [WebServices](https://github.com/vertigo-io/vertigo-extensions/blob/master/vertigo-vega/src/main/java/io/vertigo/vega/webservice/WebServices.java)
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

Vertigo propose des WebServices intégrés [SwaggerWebServices](https://github.com/vertigo-io/vertigo-extensions/blob/master/vertigo-vega/src/main/java/io/vertigo/vega/impl/webservice/catalog/SwaggerWebServices.java) qui vous donnent la vue de l'API des WebServices disponibles.<br/>
* IHM Swagger :  [http://localhost:8080/*maWebApp*/api/swaggerUi](http://localhost:8080/*maWebApp*/api/swaggerUi)
* API Swagger seule : [http://localhost:8080/*maWebApp*/api/swaggerApi](http://localhost:8080/*maWebApp*/api/swaggerApi)
- Feature `webservices.catalog` → `CatalogWebServices` (catalogue des services)
- Feature `webservices.healthcheck` → `HealthcheckWebServices` (tests de santé)

?> Vega peux être lancé en mode serveur intégré avec le paramètre *webservices.embeddedServer*, dans ce cas, il est inutile de spécifier un filtre dans le *web.xml*

## Quick start client

Pour appeler un WebService distant :

1. Reproduire l'API du WebService avec une interface Java. Cette interface doit hériter de `io.vertigo.core.node.component.Amplifier` et avoir l'annotation `@WebServiceProxyAnnotation`. Elle sera détectée par Vertigo comme les autres composants par [l'autodiscovery du module métier](getting-started/realworld_helloworld.md#_5-configuration-de-l39application)
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
5. Utiliser le WebService en injectant l'interface dans votre service métier.
L'autocloseable `HttpClientCookie` permet de conserver les cookies pour effectuer des appels succéssifs :
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
!> Le `HttpClientCookie` conserve le cookie distant dans un threadlocal.
Il est donc adapté pour des WebServices appellés dans un batch ou dans le traitement d'un écran de l'application.
Mais pas pour être conservé tout le temps d'une navigation utilisateur.

?> Le connecteur `HttpClient` propose d'autres paramètres optionnels :
- `name` pour gérer plusieurs *endpoint*, il faut alors préciser le nom de la connexion dans l'annotation `@WebServiceProxyAnnotation`
- `connectTimeoutSecond` pour définir le timeout
- `proxy` et `proxyPort` pour gérer les proxy

## API

### Code exemples :
De nombreux exemples complets sont présents dans les tests de Vertigo sur GitHub : [Tests Exemples](https://github.com/vertigo-io/vertigo-extensions/blob/master/vertigo-vega/src/test/java/io/vertigo/vega/webservice/data/ws)

### Syntaxe des routes

Lors de la définition des routes, `{myParamName}` déclare une variable de l'URL utilisée comme paramètre du service.
```java
@GET("/contact/{id}")
public Contact getContact(@PathParam("id") final int contactId) { ... }
```

### Paramètres

Vega mappe automatiquement la requête JSON entrante vers votre méthode. Les annotations indiquent la source des données (paramètres URL, body, headers…). Par défaut, le contenu est attendu dans le body (**Attention** : HTTP spécifie que les requêtes *GET* n'ont pas de body).

Le cas le plus courant est de réceptionner directement un DtObject. Dans ce cas, Vega s'occupe de formater le JSON en type Java et de valider l'objet vis-à-vis des contraintes des domains.
Il est possible de récupérer directement la saisie utilisateur en utilisant les objets génériques `UiObject` ou `UiList<MyDto>`.

Vega peuple quelques paramètres implicites :
- `UiMessageStack` : pile des messages à retourner (Success, Info, Warning, Error). Avec une portée (globale, par objet, par champ)
- `HttpServletRequest` : Requête HTTP
- `HttpServletResponse` : Réponse HTTP

?> Voir les annotations directement pour le détail

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
Result :
```json
{
	"testDate":"2014-07-29T00:00:00.000Z",
	"contactFrom":{
			"honorificCode":"MR_",
			"name":"Martin",
			"firstName":"Jean"
		},
	"testString":"the String test",
	"contactTo":{
			"honorificCode":"MIS",
			"name":"Dubois",
			"firstName":"Marie"
		},
	"testLong":12
}
```

### Handler des Exceptions

En cas d'Exceptions levées dans le service, un code HTTP est automatiquement positionné et un message d'erreur JSON est envoyé. Le retour d'erreur est volontairement simplifié pour des raisons de sécurité de l'application (pas de stacktrace par exemple).
```json
{
  "globalErrors": "Error message or simple class name"
}
```

Si le service lance une **Exception utilisateur** (saisie utilisateur ou une erreur métier), le message est plus complet et précise les informations pour le positionnement des erreurs dans l'écran :
```json
{
  "globalErrors": [ "list of error messages", ...],
  "globalWarnings": [ "list of warning messages", ...],
  "globalInfos": [ "list of infos messages", ...],
  "globalSuccess": [ "list of success messages", ...],
	
  "fieldErrors": { 
    "field1": [ "list of error messages for this field", ...], 
    "field2": [ ... ], 
    ... 
  },
  "fieldWarnings": { /* same structure than fieldErrors but for warnings */ },
  "fieldInfos": { /* same structure than fieldErrors but for infos */ },

  "objectFieldErrors": { 
    "object1": { 
      "field1": [ "list of error messages for this field", ... ],
      "field2": [ ... ],
      ... 
    },
    "object2": { 
      "field1": [ "list of error messages for this field", ... ],
      ... 
    },                        
  "objectFieldWarnings": { /* same structure than objectFieldErrors but for warnings */ },
  "objectFieldInfos": { /* same structure than objectFieldErrors but for infos*/ },
}
```

Pour les erreurs sur un object, le nom repris dans le JSON d'erreur est le même que celui envoyé lors de la request. Pour un object dans une liste, le nom utilisé est :
`nom de la liste dans la request`+ `idx` + index dans la liste (commence à 0)
Exemple : 
```json
Request : 
{ 
  "persons" : [
    { "name":"Julius", "isValid":"true" },
    { "name":"Bob", "isValid":"true" },
    { "name":"Elmond", "isValid":"false" },
    { "name":"Mark", "isValid":"false" }
  ]
}

Response : 
{
  "objectFieldErrors": { 
    "persons.idx2": { 
      "isValid": [ "personn must be valid" ]
    },
    "persons.idx3": { 
      "isValid": [ "personn must be valid" ],
    }
}
```

### État Server-side

Vertigo Vega propose de conserver un état côté serveur.

Cette fonctionnalité permet d'adresser simplement le besoin d'envoyer le minimum de données côté client (nécessaire pour des besoins de sécurité des données ou de contraintes réseau),
et de continuer d'utiliser des objets complets côté serveur dans les services métier pour les garder les plus simples possibles et ne pas multiplier les API d'entrée.

Grâce à cette fonctionnalité, vous pouvez :
* conserver l'état d'un objet à l'envoi, filtrer les champs qui doivent être réellement nécessaires
* au retour du client, Vega fusionne l'état conservé et le nouvel état envoyé par le client (filtré lui aussi)
* utiliser un objet métier complet dans la couche métier.

!> L'état server-side est limité dans le temps, lié à la session utilisateur et non-modifiable. S'il y a un besoin de modifications concurrentes, cela devra être traité au niveau du service.

En conservant les services métier sur des objets complets, ceux-ci sont plus facilement testables car il n'est pas nécessaire de gérer la combinatoire des entrées/sorties des WebServices.

Pour ce faire, vous avez à votre disposition trois annotations :
* `ServerSideSave` : appliquée sur une Méthode, elle indique à Vega de conserver l'objet retourné et poser une référence avec un `serverToken` id.
* `ServerSideRead` : appliquée sur un Paramètre, elle indique à Vega qu'il attend un objet JSON avec quelques champs et une référence `serverToken`, Vega fusionnera l'ancien état avec les données reçues.
* `ServerSideConsume` : Comme `ServerSideRead`, mais l'état conservé est consommé lors de l'appel.

Exemple :
```java
@GET("/contact/{conId}")
@ExcludedFields({ "birthday", "email", "passport" }) // All secret fields are excluded
@ServerSideSave  // Full contact data are kept serverSide, exclusion are done on json convert only
public Contact getContact(@PathParam("conId") final long conId) {
	return loadContact(conId);
}

@PUT("/contact/{conId}")
@ExcludedFields({ "birthday", "email", "passport" }) //All secret fields are re-excluded
@ServerSideSave //will save the new state, and returns a new serverToken id
public Contact updateFirstNameContact(
	@ServerSideRead //will read the previous object state from sent serverToken
	@IncludedFields({ "firstName" }) //check accepted/refused fields (or send a forbidden error)
	final Contact contact) {
		saveContact(contact); //save a full object, not just the firstName field, this ensure data consistency
		return loadContact(conId); //returns updated contact
}
```

Request: `GET http://localhost:8080/*maWebApp*/api/contact/1`

Response:
```json
{
	"conId":"1",
	"honorificCode":"MR_",
	"name":"Martin",
	"firstName":"Jean",
	"serverToken":"cb44ab11-4eac-41e9-a3d1-c0fc20ea55e1"
}
```

Request: `PUT http://localhost:8080/*maWebApp*/api/contact/1`
```json
{
	"firstName":"Jean-denis",
	"serverToken":"cb44ab11-4eac-41e9-a3d1-c0fc20ea55e1"
}
```
Response:
```json
{
	"conId":"1",
	"honorificCode":"MR_",
	"name":"Martin",
	"firstName":"Jean-denis",
	"serverToken":"b04edfef-7385-4d5d-b5ca-23d195c87200"
}
```

?> Cette fonction est traitée par `ServerSideStateWebServiceHandlerPlugin`

### Sécurité AccessToken

La gestion des tokens d'accès limitée est assurée par `TokenManager` / `TokenManagerImpl` et trois annotations :

- `AccessTokenPublish` : Génère un token temporaire dans le header `x-access-token`
- `AccessTokenMandatory` : Vérifie la présence d'un token valide. Sinon le serveur retourne une erreur `HTTP 403 FORBIDDEN` `Invalid access token`
- `AccessTokenConsume` : Idem, mais consomme (invalide) le token après usage

### Sécurité **Rate-Limit**

Pour des raisons de sécurité, tous les WebServices publiés par Vertigo Vega sont protégés (par défaut) contre les appels massifs. La limite est de 150 appels par utilisateur sur des fenêtres de 5 minutes, ce qui représente 1 appel toutes les 2 secondes.
Les utilisateurs anonymes partagent le même compteur de limite. Notez que la limite est comptabilisée par instance serveur.

Le serveur envoie des informations dans des *headers* de la *Response*
* `X-Rate-Limit-Limit` : Le maximum d'appels autorisé pour cette requête
* `X-Rate-Limit-Remaining` : Le nombre d'appels restant dans la fenêtre de temps en cours
* `X-Rate-Limit-Reset` : Le nombre de secondes restant avant une remise à zéro du compteur

Si la limite du serveur est dépassée, le serveur retourne une erreur `HTTP 429 TOO_MANY_REQUEST`.

?> Cette fonction est traitée par [`RateLimitingWebServiceHandlerPlugin`](https://github.com/vertigo-io/vertigo-extensions/blob/master/vertigo-vega/src/main/java/io/vertigo/vega/plugins/webservice/handler/RateLimitingWebServiceHandlerPlugin.java)
?> Le handler propose des paramètres optionnels :
> - *windowSeconds* : Taille de la fenêtre en seconde
> - *limitValue* : Nombre d'appels maximum (dans la durée de la fenêtre)

### Objet d'IHM **DtListDelta**

`DtListDelta` est un objet spécifique utilisé par Vertigo Vega.
Il est utilisé pour agréger les modifications apportées à une liste : création, mise à jour ou suppression réalisées côté client et retournées au serveur en 1 appel.
La requête JSON doit respecter ce format :
```json
{
	"collCreates": {
		"clientId1" : { ... object1 ... },
		"clientId2" : { ... object2 ... }
	},
	"collUpdates": {
		"clientId4" : { ... object4 ... },
		"clientId5" : { ... object5 ... }
	},
	"collDeletes": {
		"clientId6" : { ... object6 ... },
		"clientId7" : { ... object7 ... }
	}
}
```

Exemple :
```java
@POST("/contacts/delta")
@ExcludedFields({ "birthday", "email", "passport" }) // All secret fields are excluded
public String updateContacts(final DtListDelta<Contact> contactsDelta) {
	//objects were checked, just like single updates.
	updateContacts(contactsDelta.getCreates(), contactsDelta.getUpdates(), contactsDelta.getDeletes());
	return "OK : contacts updated";
}
```

?> Il existe un équivalent `UiListDelta` qui permet de récupérer des UiObjects (c'est-à-dire avant formatage et validation)

### Annotation **AutoSortAndPagination**

L'annotation `AutoSortAndPagination` est le moyen le plus simple pour publier un service en ajoutant le support de la pagination et du tri.
En partant d'un service métier qui retourne une DtList complète, il suffit d'ajouter un WebService avec cette annotation qui retourne directement le résultat du service.

Exemple :
```java
@AutoSortAndPagination
@GET("/contacts")
public DtList<Contact> searchContacts(final ContactCriteria contactCriteria) {
	//call specific search service, and return all datas (think to add a cpu/memory/user friendly limit like 250)
	return contactService.search(contactCriteria);
}
```

Comment ça marche :<br/>
**Vega** conserve une copie de la liste côté serveur et retourne :
* _header_ : `x-total-count` : la taille totale de la liste
* _header_ : `listServerToken` : le token de la liste côté serveur. Il devra être renvoyé par le client lorsqu'il faudra trier ou filtrer la liste
* _body_ : la portion de la liste au format JSON (triée et filtrée)

Lorsque l'IHM trie ou change de page, il doit retourner :
* _query_ : `top` : nombre max d'éléments à retourner
* _query_ : `skip` : offset du premier élément à retourner
* _query_ : `sortFieldName` : nom du champ portant le tri
* _query_ : `sortDesc` : true/false pour l'ordre de tri
* _query_ : `listServerToken` : token de la liste (issu des précédents appels)
* n'importe quelles autres données nécessaires, comme n'importe quel service

Notez que vous pouvez faire la même chose dans vos WebServices sans l'annotation (par exemple pour trier ou paginer dans la couche service ou dans la base de données).
Pour avoir la même API, vous avez à ajouter un paramètre `@QueryParam(".") DtListState dtListState`.

DtListState est une représentation de l'état d'une sous-liste, avec les champs `top`, `skip`, `sortFieldName`, `sortDesc` et `listServerToken`.
Sans annotation, utiliser `@QueryParam("") DtListState dtListState` pour le même résultat.

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

**Handler Chain** : `LogExceptionsHandlerPlugin` (5), `ExceptionWebServiceHandlerPlugin` (10), `CorsAllowerWebServiceHandlerPlugin` (20), `AnalyticsWebServiceHandlerPlugin` (30), `JsonConverterWebServiceHandlerPlugin` (40), `ApiKeyWebServiceHandlerPlugin` (45), `SessionInvalidateWebServiceHandlerPlugin` (50), `SessionWebServiceHandlerPlugin` (60), `SecurityWebServiceHandlerPlugin` (70), `ServerSideStateWebServiceHandlerPlugin` (80), `AccessTokenWebServiceHandlerPlugin` (90), `RateLimitingWebServiceHandlerPlugin` (100), `ValidatorWebServiceHandlerPlugin` (110), `RestfulServiceWebServiceHandlerPlugin` (120)

**WebServer** : `JavalinWebServerPlugin`, `VegaJavalinFilter`

**JSON** : `DefaultJsonConverter`, `DtObjectJsonConverter`, `DtListJsonConverter`, `DtListDeltaJsonConverter`

**Rate Limiting** : `RateLimitingMemStorePlugin`, `RateLimitingRedisStorePlugin`

**Web Authentication** : `LocalWebAuthenticationPlugin`, `SAML2WebAuthenticationPlugin`, `OIDCWebAuthenticationPlugin`, `AzureAdWebAuthenticationPlugin`

**Scanner** : `AnnotationsWebServiceScannerPlugin` (scan des annotations `@GET`, `@POST`, etc.)

### Configuration

`buildFeatures()` (toujours actif) : `GoogleJsonEngine` (implémente `JsonEngine`).
