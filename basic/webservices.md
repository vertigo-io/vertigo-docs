# WebServices

Le module Vega de Vertigo permet la création simplifiée de WebServices REST donnant ainsi la possibilité à votre application de s'interconnecter facilement avec les écosystèmes applicatifs en proposant des services numériques sous forme d'API.

Ce module est également adapté à la création d'API REST consommées par les Single Page Applications.

Le format d'échange JSON a été privilégié pour sa popularité, mais également pour sa capacité à être facilement consommable par de nombreuses technologies. L'objectif visé par Vega étant l'ouverture de l'application au monde, autant utiliser le format d'échange le plus largement adopté pour l'ouvrir au plus grand nombre.

## Configuration

Afin d'utiliser les fonctionnalités de Vega il convient d'ajouter à la configuration de l'application ce module.
Pour plus de détails vous pouvez vous rapporter au chapitre dédié à la [configuration](/basic/configuration) de l'application.

Vega propose deux méthodes de fonctionnement :

- sous forme de filtre de servlet, dans le cas où l'application fonctionne dans un conteneur de servlet (par exemple Tomcat)
- sous forme d'un serveur web embarqué (Jetty) dans le cas d'un Jar exécutable



### Cas du filtre de servlet

Voici une configuration YAML typique d'une application utilisant le module Vega et le connecteur vers Javalin

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

D'autre part voici le filtre à ajouter dans la configuration du conteneur (web.xml) dans ce cas de figure :

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

!> Ici nous avons choisi d'utiliser un préfixe pour l'ensemble des routes de webservices `/api`. C'est une pratique que nous encourageons car elle permet d'éviter des conflits de nommage.

#### AbstractFilter

Tout filtre dérivant d'`AbstractFilter` supporte deux paramètres de filtrage par URL :

- `url-include-pattern` : restreint le filtre aux URLs correspondant au pattern
- `url-exclude-pattern` : exclut les URLs correspondant au pattern

### Cas du serveur web embarqué

Voici une configuration YAML typique d'une application utilisant le module Vega avec le mode serveur embarqué

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



> Pour connaître l'intégralité des fonctionnalités disponibles se rapporter au chapitre dédié à [Vega](/extensions/vega)

## Création d'un WebService

Un webservice est un moyen de mettre à disposition des données ou un service métier via une interface web.

Vega permet d'exposer sur le web une méthode Java et de définir le comportement de ce 'endpoint' via des annotations.

> Dans Vertigo nous privilégions la création de composants de type 'WebServices' qui regroupent dans une même classe les webservices offerts sur un même domaine métier ou fonctionnel.

Dans Vertigo, tout objet qui propose des services est un composant. Un webservice n'échappe pas à la règle, c'est donc un composant, mais avec ses spécificités.  

Ainsi, avant toute chose, la lecture du [chapitre](/basic/composants) dédié au composant est utile.

Un webservice est un composant qui doit implémenter l'interface `io.vertigo.vega.webservice.WebServices`

Ce marqueur en plus de permettre au développeur de différencier les composants selon leurs fonctionnalités et leurs usages, permet au module Vega d'identifier les composants dont les méthodes doivent être analysées pour être converties en WebServices.

Pour créer un webservice commençons par créer le composant qui accueillera les méthodes à publier :

```java

public class HelloWebServices implements WebServices {
	// methods will go there
	
}
```

Ensuite ajoutons la méthode qui va être exposée :

```java
public class HelloWebServices implements WebServices {

	@AnonymousAccessAllowed
	@GET("/hello")
	public String hello() {
		return "hello world";
	}

}
```

La méthode `hello` ne prend aucun argument et retourne une chaîne de caractères. Il s'agit donc d'un exemple minimal en guise de démonstration.

L'annotation `@GET` permet de spécifier

 -  la route qui sera utilisée : ici */hello*
  -  le verbe HTTP qui sera utilisé : ici *GET*

Il existe des annotations similaires pour les différents verbes HTTP : `@POST`, `@PUT`, `@DELETE`, `@PATCH`

> Pour en savoir plus sur les routes et les verbes vous pouvez vous référer à des bonnes pratiques que nous proposons [ici](https://github.com/vertigo-io/vertigo-core/wiki/routes).

Par souci de simplicité et de concision il est possible d'ajouter un préfixe à toutes les routes des méthodes d'une même classe en utilisant l'annotation `@PathPrefix` sur la classe.

!> Ici l'annotation `@AnonymousAccessAllowed` permet l'accès du webservice sans authentification. Des endpoints publics légitimes (services exposés au grand public, accès par token) peuvent l'utiliser volontairement : l'employer alors **avec prudence**, en restant conscient de l'exposition du webservice.

## Utilisation de paramètres

Afin d'aller plus loin dans la création d'un WebService, il est évidemment possible de complexifier les signatures de méthode et ainsi prendre en entrée des paramètres et retourner des objets et des collections d'objets.

Concernant les paramètres d'entrée et de sortie ils peuvent être de différentes natures

- Des primitives Java

- Des objets

- Des collections d'objets


Concernant les paramètres d'entrée il est possible de les récupérer depuis :

- l'URL : via l'annotation `@PathParam`
- les paramètres d'URL : via l'annotation `@QueryParam`
- le corps de la requête (au format JSON) : via l'annotation `@InnerBodyParam`
- un header : via l'annotation `@HeaderParam`

Concernant les paramètres de retour ces derniers seront automatiquement sérialisés (convertis) en format JSON.

Ainsi il est possible d'écrire par exemple les webservices suivants :

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



## Sécurisation du WebService

Il est absolument indispensable de sécuriser les appels de webservices.

Afin de répondre à cet enjeu de sécurité de nombreux mécanismes sont disponibles dans Vega.

Par défaut l'ensemble des WebServices est accessible uniquement à un utilisateur authentifié. Il s'agit du premier niveau de sécurisation. Évidemment celui-ci est **nécessaire** mais **non suffisant**.

!> **Ne jamais déclarer `ComponentCmdWebServices` en production** : ce webservice d'introspection expose `GET /vertigo/components`, qui retourne le NodeConfig complet **avec les paramètres** (mots de passe LDAP, secrets de connexion...), le tout en `@AnonymousAccessAllowed`. Il n'est activé par **aucune** feature : il n'est présent que s'il a été déclaré explicitement dans la configuration — vérifier qu'il ne l'est pas sur les environnements de production. De même, réserver les features `webservices.swagger` et `webservices.catalog` aux environnements de développement/recette si elles ne sont pas indispensables : elles divulguent la surface complète de l'API.

Pour aller plus loin il est possible d'utiliser les fonctionnalités issues du module Vertigo-Account qui propose un modèle de sécurité qu'il est possible d'appliquer aux WebServices.

Il est ainsi possible de vérifier lors d'un appel de WebService :

- Que l'utilisateur authentifié possède un droit parmi les droits nécessaires pour être autorisé à l'appeler
- Que les entités (objets métiers au sens Vertigo) sont manipulables par l'utilisateur authentifié

```java
@Secured("Contact$read")
@GET("/{conId}")
public Contact read(@PathParam("conId") final long conId) {
	final Contact contact = contactDao.get(conId);
	return contact;
}
```

> Ici on vérifie que l'utilisateur connecté possède le droit **Contact$read** donc la capacité à lire des contacts

> L'annotation `@Secured` applique automatiquement le préfixe `Atz` au droit vérifié : le nom réellement contrôlé est donc `AtzContact$read`. La valeur indiquée est le nom d'autorisation d'opération `EntitéCamelCase$operation`, l'opération étant telle que déclarée dans la configuration de sécurité (typiquement en minuscule : `read`, `write`, `delete`...).
> <!-- source : AuthorizationAspect.java:L57-78, Authorization.java:L98 -->

```java
@PUT("/contactView")
public ContactView updateContactView(
    @SecuredOperation("write") final ContactView contactView) {
		return contactView;
}
```

> Ici on vérifie que l'utilisateur connecté possède l'autorisation d'écriture sur l'entité ContactView : le nom de l'opération est `write`, tel que déclaré dans la configuration de sécurité. Ce contrôle de sécurité dépend à la fois des attributs de l'utilisateur et du Contact. Il s'agit donc d'un contrôle de sécurité très fin.

> L'annotation `@SecuredOperation` porte le nom de l'opération **sans préfixe** : il s'agit d'un `OperationName` et non d'un nom d'autorisation `Atz...`. Le paramètre annoté doit être une entité (Entity).
> <!-- source : AuthorizationAspect.java:L66-78 -->

### `@SessionLess`

L'annotation `@SessionLess` (`io.vertigo.vega.webservice.stereotype.SessionLess`) s'applique à une **méthode** de webservice et ne porte aucun membre.
<!-- source : SessionLess.java:L32-35 -->

Son effet : **aucune session HTTP n'est créée ni liée** pour ce webservice. La session Vertigo est tout de même créée pour la sécurité, mais sans liaison au `HttpSession` ; si une `HttpSession` existe déjà, elle est réutilisée. Elle est conçue pour les services anonymes ou à faible consommation de ressources.
<!-- source : SessionLess.java:L27-30 -->

Concrètement, le scanner pose `needSession = false` sur le webservice et, à l'exécution, le handler de session `SessionWebServiceHandlerPlugin` (stack index 60) ne s'applique plus à ce webservice.
<!-- source : AnnotationsWebServiceScannerUtil.java:L141-142 -->
<!-- source : SessionWebServiceHandlerPlugin.java:L64 -->

> `@SessionLess` est **incompatible avec `@ServerSideSave`** : l'assertion « Session mandatory for serverSideState » est levée.
> <!-- source : WebServiceDefinition.java:L121-122 -->

## CORS (Cross-Origin Resource Sharing)

Le plugin `CorsAllowerWebServiceHandlerPlugin` permet de gérer les requêtes cross-origin. Il s'active via la fonctionnalité `webservices.cors`.

Les paramètres de configuration sont :

- `originCORSFilter` (obligatoire) : filtre les origines autorisées
- `methodCORSFilter` (optionnel) : filtre les méthodes HTTP autorisées, par défaut `GET, POST, DELETE, PUT, OPTIONS`

La validation des URIs est stricte : seules les URI complètes sans path ni query string sont acceptées.

## OIDC (OpenID Connect)

Vega supporte l'authentification OIDC via les interfaces et classes suivantes :

- `AppLoginHandler<T>` : interface de gestion de connexion applicative
- `OIDCAppLoginHandler` : marqueur pour un handler de connexion OIDC
- `WebAuthenticationPlugin<T>` : plugin d'authentification web générique
- `OIDCWebAuthenticationPlugin` : plugin d'authentification OIDC avec les paramètres :
   - `scopes` : les scopes OIDC à demander
   - `urlPrefix` : préfixe d'URL
   - `urlHandlerPrefix` : préfixe d'URL pour les handlers
   - `externalUrl` : URL externe de l'application
   - `connectorName` : nom du connecteur OIDC

### Brancher le handler de login applicatif (feature `authentication`)

En 4.4, le `SecurityFilter` injecte un `Optional<WebAuthenticationManager>` : si la feature `authentication` est active, la chaîne de sécurité (page de login, connexion, déconnexion) est pilotée par ce composant ; sinon le comportement classique s'applique, **401** si l'utilisateur n'est pas authentifié. L'ancien mécanisme — un init-param web.xml `delegate-authentication-handler-component` lu par le filtre `LegacySecurityFilter` de la 3.x — a disparu avec ce filtre dès 4.0 (suppression au commit `65db5ab049`, contenu dans le tag `vertigo-4.0.0`) ; l'interface `DelegateAuthenticationFilterHandler`, devenue obsolète et sans usage, subsiste en tant que trace dans le code. Le remplacement est la feature `authentication` + `appLoginHandler`.
<!-- source : SecurityFilter.java:L59-60, L96-121 -->

La feature `authentication` (méthode `withWebAuthentication(Param...)`) active le composant `WebAuthenticationManager` (implémentation `WebAuthenticationManagerImpl`) et expose le paramètre :
<!-- source : VegaFeatures.java:L194-199 -->

- `appLoginHandler` (String) : nom du composant applicatif à résoudre en `AppLoginHandler` via `Node.getNode().getComponentSpace().resolve(appLoginHandler, AppLoginHandler.class)`
<!-- source : WebAuthenticationManagerImpl.java:L63, L172, L183 -->

`AppLoginHandler<T>` est une **interface générique** :
<!-- source : AppLoginHandler.java:L28-62 -->

- `String doLogin(HttpServletRequest, Map<String, Object> claims, T rawResult, Optional<String> requestedUrl)` : à implémenter — retourne la page de redirection après un login réussi
- `default Optional<String> doLogout(HttpServletRequest)` : page de redirection après déconnexion (vide par défaut)
- `default void loginFailed(HttpServletRequest, HttpServletResponse)` : appelé en cas d'échec du login — renvoie par défaut **403**

C'est ce composant qui pilote la page de login applicative : les connexions OIDC, SAML et locale passent par lui.

Exemple de configuration :

```yaml
modules:
  io.vertigo.vega.VegaFeatures:
    features:
        - webservices:
        - authentication:
            appLoginHandler: monComposantLogin
```

## SwaggerApi

L'API ainsi créée avec ce module est exposée au format standard Swagger **2.0**. Vertigo inclut la mise à disposition de l'API via l'UI standard de Swagger.
Il suffit d'ajouter la façade webservice : `io.vertigo.vega.impl.webservice.catalog.SwaggerWebServices`

![](./images/swaggerUi.png)

L'objet `SwaggerApi` est représenté comme un `LinkedHashMap<String, Object>`.

Règles de construction des noms de définition Swagger :

- Le caractère `$` dans le nom de la définition du webservice (`webServiceDefinition.getName()`) sert de séparateur pour structurer les définitions imbriquées
- Les séquences de tirets bas multiples sont réduites à un seul `_` (ex: `__` → `_`)
- Il n'y a **pas** de remplacement automatique de `$` par `_`

Le JSON des facettes `FacetedQueryResult` expose l'attribut `isMultiSelectable` sur chaque facette. `FacetedQueryResultJsonSerializerV5` est le sérialiseur **par défaut**.

## LogExceptionsHandlerPlugin

Le plugin `LogExceptionsHandlerPlugin` est activé par défaut, sans paramètre de configuration. Il est toujours actif et génère un log d'erreur (status, verbe, path, path params) pour toute réponse HTTP avec un code entre 500 et 599.

## Rate Limiting

Le rate limiting permet de limiter le nombre d'appels autorisés sur une fenêtre de temps glissante.

Les adresses localhost (`127.0.0.1`, `[0:0:0:0:0:0:0:1]`) figurent dans l'ensemble `USER_EXCLUDED_IPS` : elles sont ignorées lorsqu'elles sont lues dans les headers (`X-Forwarded-For` / en-tête custom) — protection contre le spoofing. Il ne s'agit **pas** d'une exemption du rate limiting.
<!-- source : RateLimitingManagerImpl.java:L66 — USER_EXCLUDED_IPS, utilisé uniquement dans obtainUserIpFromHeader -->

Deux features distinctes sont disponibles :

- `webservices.rateLimiting` : active le handler `RateLimitingWebServiceHandlerPlugin` (stack index 100, compteur en mémoire) avec les paramètres `windowSeconds` (défaut `300`) et `limitValue` (défaut `150`)
- `rateLimiting` : active le composant `RateLimitingManager` (implémentation `RateLimitingManagerImpl`) avec les paramètres du tableau ci-dessous
<!-- source : RateLimitingWebServiceHandlerPlugin.java:L53, L55-56, L83-95 -->
<!-- source : VegaFeatures.java:L89-94 -->

### Paramètres de la feature `rateLimiting`

| Paramètre | Type | Défaut |
|---|---|---|
| `windowSeconds` | `Optional<Integer>` | `300` |
| `maxRequests` | `Optional<Long>` | `150` |
| `maxDayRequests` | `Optional<Long>` | — (doit être ≥ `maxRequests`) |
| `errorCode` | `Optional<Integer>` | `429` |
| `overRateLimitMode` | `Optional<String>` | `reject` (valeurs : `nothing` / `logOnly` / `reject` / `banish`) |
| `insertHeaders` | `Optional<Boolean>` | `true` (pose les headers `X-Rate-Limit-Limit` / `X-Rate-Limit-Remaining` / `X-Rate-Limit-Reset`) |
| `useForwardedFor` | `Optional<Boolean>` | `false` |
| `useHeaderUserIp` | `Optional<String>` | — (nom d'un en-tête custom, type `True-Client-Ip`) |
| `useUserIp` | `Optional<Boolean>` | `true` (sinon `sessionId`, sinon `anonymous`) |
| `logEveryXRequests` | `Optional<Integer>` | `100` |
| `banishSeconds` | `Optional<Long>` | `1800` |
| `banishRepeaterMult` | `Optional<Double>` | `2` |
| `maxBanishSeconds` | `Optional<Long>` | `604800` |
| `banishMessage` | `Optional<String>` | calculé (« N requests/min… ») |
| `whiteListUsers` | `Optional<String>` | — (IPs séparées par `,` ou `;`, max 100 000) |

<!-- source : RateLimitingManagerImpl.java:L130-184 -->

Le backend de stockage de la feature `rateLimiting` est fourni par l'une des features stores associées : `rateLimiting.redis` (Redis, compatible cluster) ou `rateLimiting.mem` (mémoire locale) — cf. section *RateLimiting* de la partie *Pour les experts*.
<!-- source : VegaFeatures.java:L96-108 -->

## Pour les experts

### Plugins de sécurité

| Plugin | Feature | Stack Index | Description |
|---|---|---|---|
| `AccessTokenWebServiceHandlerPlugin` | `webservices.token` | 90 | Génération et vérification de tokens jetables pour actions sensibles |
| `ApiKeyWebServiceHandlerPlugin` | `webservices.auth.apiKey` | 45 | Authentification par clé API. Paramètres : `apiKey` (String), `headerName` (Optional<String>) |

### Services système

| Service | Feature | Route | Description |
|---|---|---|---|
| `HealthcheckWebServices` | `webservices.healthcheck` | Auto-généré | Endpoint de supervision de la plateforme |
| `CatalogWebServices` | `webservices.catalog` | Auto-généré | Catalogue des webservices (métadonnées, définitions) |

### WebServiceClient (Proxy)

La feature `webservices.proxyclient` active l'`AmplifierMethod` `WebServiceClientAmplifierMethod` qui génère dynamiquement des proxies Java à partir d'une `WebServiceDefinition`. Le proxy utilise un `HttpRequestBuilder` interne pour construire les requêtes HTTP (méthode, URL, headers, body JSON) et un `JsonEngine` (implémentation par défaut `GoogleJsonEngine`/Gson, injectée) pour la lecture/écriture JSON.

### HandlerChain — Architecture interne

Vega traite chaque requête HTTP via une chaîne de plugins (`WebServiceHandlerPlugin`) triés par `getStackIndex()`. La `HandlerChain` itère sur les handlers actifs et appelle `accept(WebServiceDefinition)` pour déterminer si un handler s'applique à ce webservice. Le premier qui accepte exécute `handle()` et passe au suivant via `chain.handle()`. Si le dernier handler ne produit pas de body, une `IllegalStateException` est levée.

Le nombre maximum de handlers dans une chaîne est 50 (détection de boucle infinie via `MAX_NB_HANDLERS`).

#### Ordre des handlers

| Index | Handler | Activé par |
|---|---|---|
| 5 | `LogExceptionsHandlerPlugin` | Toujours actif |
| 10 | `ExceptionWebServiceHandlerPlugin` | Toujours actif |
| 20 | `CorsAllowerWebServiceHandlerPlugin` | `webservices.cors` |
| 30 | `AnalyticsWebServiceHandlerPlugin` | Toujours actif |
| 40 | `JsonConverterWebServiceHandlerPlugin` | Toujours actif |
| 45 | `ApiKeyWebServiceHandlerPlugin` | `webservices.auth.apiKey` |
| 50 | `SessionInvalidateWebServiceHandlerPlugin` | `webservices.security` |
| 60 | `SessionWebServiceHandlerPlugin` | `webservices.security` |
| 70 | `SecurityWebServiceHandlerPlugin` | `webservices.security` |
| 80 | `ServerSideStateWebServiceHandlerPlugin` | `webservices.token` |
| 90 | `AccessTokenWebServiceHandlerPlugin` | `webservices.token` |
| 100 | `RateLimitingWebServiceHandlerPlugin` | `webservices.rateLimiting` |
| 110 | `ValidatorWebServiceHandlerPlugin` | Toujours actif |
| **120** | `RestfulServiceWebServiceHandlerPlugin` | Toujours actif ← **toujours dernier** |

Un handler personnalisé doit avoir un `getStackIndex()` entre 0 et 119. Le dernier (`RestfulServiceWebServiceHandlerPlugin`, index 120) est celui qui exécute la méthode Java cible et retourne le body.

### Servlet Filters vs HandlerChain

Les Servlet Filters s'exécutent **avant** la HandlerChain et opèrent au niveau Servlet Spec (pas Vega). Ils ne filtrent pas par `WebServiceDefinition` mais par URL pattern (`url-include-pattern` / `url-exclude-pattern` via `AbstractFilter`).

| Filter | Rôle |
|---|---|
| `SetCharsetEncodingFilter` | Force le charset de la **requête** (`request.setCharacterEncoding`), défini par l'init-param obligatoire `charset` |
| `CompressionFilter` | Compresse la réponse en **gzip** (selon `Accept-Encoding`), selon le seuil `compressionThreshold` et l'user-agent |
| `CacheControlFilter` | Pose les headers `Cache-Control` (private, max-age, no-cache) |
| `SecurityFilter` | Filtre de session/authentification : lie la `UserSession` de l'application en attribut de la session J2EE (`io.vertigo.Session`), renvoie **401** si l'utilisateur n'est pas authentifié ; init-param `url-no-authentification` (URLs exemptées d'authentification). Ne pose **aucun** header HTTP |
| `ContentSecurityPolicyFilter` | Gère les headers CSP |
| `HeaderControlFilter` | Contrôle des headers d'entrée/sortie |
| `AuthorizationWebFilter` | Filtre de routes par autorisation : chaque init-param est **nommé** d'après le(s) nom(s) d'autorisation préfixé(s) `Atz` (séparés par `;` = OR) et sa **valeur** est le(s) pattern(s) d'URL ; init-params réservés : `errorCode` (Integer, défaut 403), `url-include-pattern` / `url-exclude-pattern` ; ne lit pas `@Secured` |
| `RateLimitingFilter` | Rate limiting au niveau Servlet (séparé du handler) |
| `AnalyticsFilter` | Collecte métriques au niveau Servlet |

!> **`SetCharsetEncodingFilter` doit être déclaré en premier**, avant tout filtre susceptible de lire les paramètres de la requête — sa propre javadoc l'indique : « Doit être le premier filter pour être efficace ». La spec Servlet impose en effet d'appeler `setCharacterEncoding` **avant** la première lecture des paramètres, sinon l'appel est sans effet. Symptôme typique d'un mauvais ordre : accents corrompus dans les critères de recherche saisis par l'utilisateur.

> **Détail — `AuthorizationWebFilter`** : la déclaration du filtre repose sur la sémantique **nom / valeur** des init-params — le **nom** d'un init-param est un nom d'autorisation, sa **valeur** est un pattern d'URL :
> <!-- source : AuthorizationWebFilter.java:L56-165 -->
>
> - **Nom** : le nom — ou les noms séparés par `;` (**OR**) — de l'autorisation contrôlée, **obligatoirement préfixé `Atz`** (une assertion est levée si le préfixe est absent)
> - **Valeur** : le pattern — ou les patterns séparés par `;` (**OR**) — d'URL contrôlé(s) ; conversion : `.` échappée, `*` en fin de pattern → `.*`, `*` en milieu de pattern → `[^/]*`
> - Init-params **réservés** : `errorCode` (Integer, défaut **403**), `url-include-pattern` / `url-exclude-pattern` (hérités de `AbstractFilter`)
> <!-- source : AuthorizationWebFilter.java:L87-97 -->
> <!-- source : AbstractFilter.java:L84-94 -->
>
> Le filtre lit la `UserSession` de la session HTTP (attribut `io.vertigo.Session`) puis les `UserAuthorizations` (attribut `vertigo.account.authorizations`) ; en l'absence de session ou de droits, il émet `sendError(errorCode)` + `VSecurityException`. Ce filtre ne lit **pas** l'annotation `@Secured`.

Exemple de déclaration (noms d'autorisation et URLs fictifs) :

```xml
<init-param>
	<param-name>AtzVoirSwagger</param-name>
	<param-value>/api/swagger*;/api/catalog*</param-value>
</init-param>
```

> Le paramètre `devMode.authzLogOnly` **n'est pas un init-param** du filtre : c'est un paramètre du `ParamManager` (résolu dans le component space) qui, en mode de développement, fait logguer les refus d'autorisation au lieu de renvoyer l'erreur HTTP.
> <!-- source : AuthorizationWebFilter.java:L58, L158-164 -->

### Cycle de vie

1. **DefinitionSpace** : `AnnotationsWebServiceScannerPlugin` scanne les composants implémentant `WebServices`, extrait les méthodes annotées (`@GET`, `@POST`, ...) et génère les `WebServiceDefinition`
2. **ComponentSpace** : `WebServiceManager` assemble les `WebServiceDefinition` et trie les `WebServiceHandlerPlugin` par `getStackIndex()`
3. **Runtime** : Requête HTTP → Servlet Filter chain → HandlerChain → méthode Java cible → réponse JSON

### Authentication Plugins

| Plugin | Feature | Description |
|---|---|---|
| `LocalWebAuthenticationPlugin` | `authentication.local` | Authentification locale via formulaire |
| `OIDCWebAuthenticationPlugin` | `authentication.oidc` | OpenID Connect |
| `SAML2WebAuthenticationPlugin` | `authentication.saml2` | SAML 2.0 |
| `AzureAdWebAuthenticationPlugin` | `authentication.aad` | Azure Active Directory |

### RateLimiting

Le `RateLimitingWebServiceHandlerPlugin` implémente le rate limiting via une fenêtre glissante. Le backend de stockage est configurable :

| Backend | Feature | Description |
|---|---|---|
| Mémoire locale | `rateLimiting.mem` | Stockage local, non persisté, non partagé |
| Redis | `rateLimiting.redis` | Stockage partagé via Redis, compatible cluster |

Les adresses localhost (`127.0.0.1`, `[0:0:0:0:0:0:0:1]`) sont ignorées comme **source d'IP utilisateur issue des headers** (`X-Forwarded-For` / en-tête custom) — protection contre le spoofing ; elles ne sont **pas** exemptées du rate limiting.
<!-- source : RateLimitingManagerImpl.java:L66 — USER_EXCLUDED_IPS, utilisé uniquement dans obtainUserIpFromHeader -->

### Debug

- Activer le logging du `WebServiceManager` pour tracer le chargement des webservices et l'assemblage de la HandlerChain
- Le `LogExceptionsHandlerPlugin` logge automatiquement toutes les réponses 5xx (status, verbe, path, path params)
- Le `AnalyticsWebServiceHandlerPlugin` expose les métriques de performance (temps d'exécution par webservice)
- Pour déboguer l'ordre des handlers, vérifier que chaque `accept()` retourne `true` uniquement pour les webservices ciblés