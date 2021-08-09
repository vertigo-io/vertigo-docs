# Vega

Le module **Vega** permet de mettre en place simplement des WebServices dans l'application. 
Ce module est orienté pour le développement d'applications *Single-Page-Application*, mais peut évidemment être utilisé pour des WebServices d'applications Web standards ou de SI à SI.
Il intègre un ensemble de solutions *production-ready* pour accélérer et sécuriser l'application.

Vega propose également un client de WebService pour appeller simplement des WebServices d'un autre noeud Vertigo, ou d'une autre application.

## Composant interne
En interne, le module utilise [java-spark](https://github.com/perwendel/spark).<br/>
Il propose une publication de l'API par le standard [Swagger](https://swagger.io/).<br/>
Pour publier les WebServices, il suffit d'un ensemble d'annotations sur une façade de vos services métier. Les annotations sont volontairement une sous-partie du standard [JAX-RS](https://javaee.github.io/javaee-spec/javadocs/javax/ws/rs/package-summary.html)

Pour la partie cliente, le module utilise le HttpClient du JDK.<br/>
Pour appeler des WebServices, il suffit d'une interface avec les annotations standard de Vega.

## Quick start server

1. La classe du webservice doit implémenter l'interface [WebServices](https://github.com/vertigo-io/vertigo/blob/master/vertigo-vega-api/src/main/java/io/vertigo/vega/webservice/WebServices.java)
2. La classe doit être déclaré comme un *Composant* Vertigo, concrètement, cela est fait par [l'autodiscovery du module métier](getting-started/realworld_helloworld.md#_5-configuration-de-l39application) 
3. Ajouter les annotations sur les méthodes, exemple:
```java 
@AnonymousAccessAllowed 
@GET("/anonymousTest")
```
4. Ajouter la feature *webservices* dans la configuration :

```yaml
modules:
  io.vertigo.commons.CommonsFeatures:
  io.vertigo.vega.VegaFeatures:
    features:
      - webservices:
    featuresConfig:
      - webservices.apiPrefix:
          apiPrefix: /api
```

5. Déclarer le filtre dans le fichier *web.xml*

```xml
	<filter>
		<filter-name>VegaSparkFilter</filter-name>
		<filter-class>io.vertigo.vega.plugins.webservice.webserver.sparkjava.VegaSparkFilter</filter-class>
	</filter>
	<filter-mapping>
		<filter-name>VegaSparkFilter</filter-name>
		<url-pattern>/api/*</url-pattern>
	</filter-mapping>
```
 
6. Démarrer l'application
7. **C'est bon**. Vous pouvez appeler votre webservice :  [http://localhost:8080/*maWebApp*/api/anonymousTest](http://localhost:8080/*maWebApp*/api/anonymousTest)

Vertigo propose des WebServices intégrés [SwaggerWebServices](https://github.com/vertigo-io/vertigo/blob/master/vertigo-vega-impl/src/main/java/io/vertigo/vega/impl/webservice/catalog/SwaggerWebServices.java) qui vous donnent la vue de l'API des WebServices disponibles.<br/>
* IHM Swagger :  [http://localhost:8080/*maWebApp*/api/swaggerUi](http://localhost:8080/*maWebApp*/api/swaggerUi)
* API Swagger seule : [http://localhost:8080/*maWebApp*/api/swaggerApi](http://localhost:8080/*maWebApp*/api/swaggerApi)


?> Vega peux être lancé en mode serveur intégré avec le paramètre *webservices.embeddedServer*, dans ce cas, il est inutile de spécifier un filtre dans le *web.xml* 


## Quick start client

Pour appeler un WebService distant
1. Il faut reproduire l'api du WebService avec une interface Java. Cette interface doit hériter de `io.vertigo.core.node.component.Amplifier` et avoir l'annotation `@WebServiceProxyAnnotation`
Elle sera détectée par Vertigo comme les autres composants par [l'autodiscovery du module métier](getting-started/realworld_helloworld.md#_5-configuration-de-l39application) 

2. Ajouter la *featureConfig* dans la configuration de Vega
```yaml
  io.vertigo.vega.VegaFeatures:
    features:
      - webservices:
    featuresConfig:
      - webservices.proxyclient:
```

3. Ajouter le connecteur HttpClient dans la configuration
```yaml
  io.vertigo.connectors.httpclient.HttpClientConnector:
    features:
      - httpclient:
          urlPrefix:  http://mySpUrl:8080
```

4. Ajouter les annotations sur les méthodes de l'interface, exemple:
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

5. Pour "utiliser" votre WebService, il suffit d'injecter l'interface dans votre service métier.
L'autocloseable `HttpClientCookie` permet de conserver les cookies pour effectuer des appels succéssifs :

```java
  @Inject
  private SimplerClientTestWebServices otherWService;
	
  @Test
  public void myBusinessService() {
    try (HttpClientCookie httpClientCookie = new HttpClientCookie()) {
      otherWService.login();
      final Contact result = otherWService.testRead(2);
	  //do something
    }
  }
```
!> Le `HttpClientCookie` conserve le cookie distant sur dans un threadlocal.
Il est donc adapté pour des WebServices appellés dans un batch ou dans le traitement d'un écran de l'application. 
Mais pas pour être conservé tout le temps d'une navigation utilisateur.

?> Le connecteur `HttpClient` propose d'autres paramètres optionnels :
- `name` pour gérer plusieurs *endpoint*, il faut alors préciser le nom de la connexion dans l'annotation `@WebServiceProxyAnnotation`
- `connectTimeoutSecond` pour définir le timeout
- `proxy` et `proxyPort` pour gérer les proxy


## API

### Code exemples :
De nombreux exemples complets sont présents dans les tests de Vertigo sur GitHub : [Tests Exemples](https://github.com/vertigo-io/vertigo/tree/master/vertigo-vega-impl/src/test/java/io/vertigo/vega/webservice/data/ws)

### Syntaxe des routes
Lors de la définition des routes, vous pouvez utiliser `{myParamName}` pour déclarer une variable de l'URL qui est utilisée comme paramètre du service.  
Exemple:
```java
@GET("/contact/{id}")
public Contact getContact(@PathParam("conId") final int contactId) {
...
}
```
Cet exemple accepte les URLs comme `http://localhost:8080/*maWebApp*/api/contact/134` ou `http://localhost:8080/*maWebApp*/api/contact/756`  
et appelle le service sous-jacent comme `getContact(134)` ou `getContact(756)`

### Paramètres

Vertigo Vega va automatiquement mapper la requête entrant Json vers votre méthode de WebService. Les annotations positionnées permettent d'indiquer comment se fait ce mapping. 
Vega est prévu pour gérer un maximum de cas, tout en proposant des optimisations à travers des objets propres à Vertigo (résultat de recherche, état des listes, Optional, ...).
La plupart du temps, il s'agit surtout d'indiquer la source des données (paramètres de l'URL, body de requêtes, headers, ...).
Par défaut, le contenu est attendu dans le body (**Attention** : la norme HTTP indique que les requêtes *GET* n'ont pas de body).

Le cas le plus courant est de réceptionner directement un DtObject. Dans ce cas, Vega s'occupe de formater le JSON en type Java et de valider l'objet vis-à-vis des contraintes des domains.
Il est possible de récupérer directement la saisie utilisateur en utilisant les objets génériques `UiObject` ou `UiList<MyDto>`.

Vega peuple quelques paramètres implicites (qui ne sont pas envoyés par le client). Ces éléments implicites permettent d'agir plus finement sur le comportement du WebService. 
- UiMessageStack : pile des messages à retourner à l'IHM. Avec un état (Success, Info, Warning, Error) et une portée (globale, par objet, par champ)
- HttpServletRequest : Requête HTTP
- HttpServletResponse : Réponse HTTP

?> Voir les annotations directement pour le détail

### Objet de retour
Le résultat de votre service est automatiquement sérialisé en JSON.
La serialisation JSON est optimisée pour les Objects spécifiques de Vertigo :
- Entity
- UiObject : objet composite générique, utilisé pour charger un contexte complet de page
- FacetedQueryResult : l'objet résultat du moteur de recherche (avec facettes, groupements et highlights)

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


### Etat Server-side
Vertigo Vega propose de conserver un état côté serveur. 

Cette fonctionnalité permet d'adresser simplement le besoin d'envoyer le minimum de données côté client (nécessaire pour des besoins de sécurité des données ou de contraintes réseau),
et de continuer d'utiliser des objets complets côté serveur dans les services métier pour les garder les plus simples possibles et ne pas multiplier les API d'entrée.
En conservant les services métier sur des objets complets, ceux-ci sont plus facilement testables car il n'est pas nécessaire de gérer la combinatoire des entrées/sorties des WebServices.

!> L'état server-side est limité dans le temps, lié à la session utilisateur et non-modifiable. S'il y a un besoin de modifications concurrentes, cela devra être traité au niveau du service.

Grâce à cette fonctionnalité, vous pouvez : 
* conserver l'état d'un objet à l'envoi, filtrer les champs qui doivent être réellement nécessaire
* au retour du client, Vega fusionne l'état conservé et le nouvel état envoyé par le client (filtré lui aussi)
* utiliser un objet métier complet dans la couche métier.

Pour ce faire, vous avez à votre disposition trois annotations :
* `ServerSideSave` : appliquée sur une Méthode, elle indique à Vega de conserver l'objet retourné et poser une référence avec un `serverToken` id.
* `ServerSideRead` : appliquée sur un Paramètre, elle indique que Vega qu'il attend un objet JSON avec quelques champs et une référence `serverToken`, Vega fusionnera l'ancien état avec les données reçues. Toutes les validations seront effectuées comme lors de n'importe quel appel.
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

?> Cette fonction est traitée par [`ServerSideStateWebServiceHandlerPlugin`](https://github.com/vertigo-io/vertigo/blob/master/vertigo-vega-impl/src/main/java/io/vertigo/vega/plugins/webservice/handler/ServerSideStateWebServiceHandlerPlugin.java)


### Sécurité **AccessToken**
Cette fonctionnalité propose un Token d'accès limité. La gestion de ce Token est gérée par le développeur par 3 annotations :
* `AccessTokenPublish` : posée sur une méthode, elle génère un Token unique aléatoire et l'ajoute comme *header* la *Response* `x-access-token`.
* `AccessTokenMandatory` : posée sur une méthode, elle assure que le client a envoyé un *header* de *Request* `x-access-token` valide. Sinon le serveur retourne une erreur `HTTP 403 FORBIDDEN` `Invalid access token`.
* `AccessTokenConsume` : Idem à `AccessTokenMandatory`, mais consomme le `x-access-token` lors de l'appel (token invalidation).

### Sécurité **Rate-Limit**
Pour des raisons de sécurité, tous les WebServices publiés par Vertigo Vega sont protégés (par défaut) contre les appels massifs. La limite est de 150 appels par utilisateur sur des fenêtres de 5 minutes, ce qui représente 1 appel toutes les 2 secondes.
Les utilisateurs anonymes partagent le même compteur de limite. Notez que la limite est comptabilisée par instance serveur.

Le serveur envoie des informations dans des *headers* de la *Response*
* `X-Rate-Limit-Limit` : Le maximum d'appels autorisé pour cette requête
* `X-Rate-Limit-Remaining` : Le nombre d'appels restant dans la fenêtre de temps en cours
* `X-Rate-Limit-Reset` : Le nombre de secondes restant avant une remise à zéro du compteur

Si la limite du serveur est dépassée, le serveur retourne une erreur `HTTP 429 TOO_MANY_REQUEST`.

> Cette fonction est traitée par [`RateLimitingWebServiceHandlerPlugin`](https://github.com/vertigo-io/vertigo/blob/master/vertigo-vega-impl/src/main/java/io/vertigo/vega/plugins/webservice/handler/RateLimitingWebServiceHandlerPlugin.java)
> Le handler propose des paramètres optionnels : 
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
		"clientId2" : { ... object2 ... },
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
public String updateContacts( final DtListDelta<Contacts> contactsDelta) {
                //objects were checked, just like single updates.
		updateContacts(contactsDelta.getCreates(),contactsDelta.getUpdates(),contactsDelta.getDeletes()); 
		return "OK : contacts updated";
}
```

?> Il existe un équivalent `UiListDelta` qui permet de récupérer des UiObjects (ie. avant formatage et validation)

### Annotation **AutoSortAndPagination**
L'annotation `AutoSortAndPagination` est le moyen le plus simple pour publier un service en ajoutant le support de la pagination et du tri.
En partant d'un service métier qui retourne une DtList complète, il suffit d'ajouter un WebService avec cette annotation qui retourne directement le résultat du service.

Exemple :
```java
@AutoSortAndPagination
@GET("/contacts")
public DtList<Contacts> searchContacts( final ContactCriteria contactCriteria) {
    //call specific search service, and return all datas (think to add a cpu/memory/user friendly limit like 250)
		return contactService.search(contactCriteria); 
}
```

Comment ca marche :<br/>
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
Pour avoir la même API, vous avez à ajouter un paramètre  ``` @QueryParam(".") DtListState dtListState```

DtListState est une représentation de l'état d'une sous-liste, avec les champs `top`, `skip`, `sortFieldName`, `sortDesc` et `listServerToken`   

Exemple :
```java
@GET("/contacts")
public DtList<Contacts> searchContacts( final ContactCriteria contactCriteria, @QueryParam("") UiListState uiListState) {
    //think to add a total-count metadata to the returned list.
		return contactService.search(contactCriteria, uiListState.getTop(), uiListState.getSkip(), uiListState.getSortFieldName(), uiListState.getSortDesc()); 
}
```

### HTTP Code
Vertigo Vega retourne automatiquement les codes HTTP suivants :
* `200 Success` : Quand tout va bien
* `201 Created` : Par convention, tout va bien et la méthode commence par 'create'
* `204 No Content` : Quand tout va bien mais qu'il n'y a aucune donnée en retour (return null ou void)
* `401 Unauthorized` : Pas de session valide (`SessionException`)
* `403 Forbidden` : Droits insuffisants (`VSecurityException`)
* `404 Not found` : Pas de WebService/Resource trouvé
* `400 Bad request` : Erreur de syntaxe de requête (`JsonSyntaxException`)
* `422 Unprocessable entity` : Erreur de validation ou de règle métier (`ValidationUserException` ou `VUserException`)
* `429 Too many requests` : Sécurité anti-spam (impose d'attendre la prochaine fenêtre) (`TooManyRequestException`)
* `500 Internal server error` : Erreur interne, doit retourner un message dans le corps de la *Response*

***

## Référence complète des Annotations

### Annotations de classe
* `PathPrefix` : Utilisé pour ajouter un préfixe commun à toutes les routes de la classe

### Annotations de méthode
* `Doc` : Ajoute une documentation à la route. Apparaît dans la spécification de l'API (Swagger)
* `AnonymousAccessAllowed` : Autorise l'accès aux utilisateurs anonymes (Current UserSession.isAuthenticated() == false)
* `SessionLess` : Indique de ne pas créer de session HTTP lors de l'appel à cette route (pour les WebServices SI à SI)
* `SessionInvalidate` : Invalide la Session HTTP lors de l'appel.
* `GET` : Définit une route en `GET` pour cette méthode. `GET` est utilisé pour les services de type *chargement*. `GET` ne devrait avoir que des paramètres d'url, pas de body et devrait être idempotent (chaque appel donne le même résultat, s'il n'y a pas de modification concurrente évidemment).
* `POST` : Définit une route en `POST` pour cette méthode. `POST` est utilisé pour les services de type *enregistrement* et pour la majorité des services métier (archive, send, compute, ...). `POST` peut avoir un contenu dans le body et n'a pas à être idempotent (l'état serveur est modifié). C'est une bonne pratique de décider comment des appels successifs depuis une même origine doivent se comporter (gestion du back navigateur ou le multi-click des utilisateurs). Il est parfois plus simple de mettre en place des contraintes métier pour éviter ces multiples exécutions (contraintes d'unicité, vérification des transitions d'état, ...).
* `DELETE` : Définit une route `DELETE` pour cette méthode. `DELETE` est utilisé pour les services de type *suppression*. `DELETE` devrait rarement avoir un body et n'est pas idempotent (l'état serveur est modifié).
* `PUT` : Définit une route `PUT` pour cette méthode. `PUT` est utilisé pour les services de type *création* ou *mise à jour* simples. `PUT` devrait avoir un body et doit être idempotent (chaque appel donne le même résultat, s'il n'y a pas de modification concurrente évidemment). Les principes **RESTful** sont assez ambigus sur l'utilisation de **PUT** et de **POST**, nous préconisons surtout de nous fier au contrat : **PUT** idempotent, **POST** non.
* `ExcludedFields` : Définit les champs à exclure de la réponse. A utiliser dans un objectif de sécurité.
* `IncludedFields` : Définit les champs à inclure dans la réponse (les autres sont exclus). A utiliser dans un objectif de sécurité.
* `AccessTokenPublish` : Retourne un nouveau token d'accès sous la forme d'un header `x-access-token`. Ce token peut être utilisé pour un temps limité. Le token est lié à un utilisateur et ne peut être utilisé par d'autres. A utiliser dans un objectif de sécurité.
* `AccessTokenMandatory` : Définit le service comme étant *protégé par AccessToken*. Le service impose la présence d'un AccessToken valide dans le header `x-access-token` de la requête. A utiliser dans un objectif de sécurité.
* `AccessTokenConsume` : Définit le service comme étant *protégé par AccessToken*. Le service impose la présence d'un AccessToken valide dans le header `x-access-token` de la requête. Quand ce service est appelé et termine sans erreur, le token est consommé et ne peut plus être utilisé. A utiliser dans un objectif de sécurité.
* `ServerSideSave` : Indique au serveur de conserver une copie de l'objet complet côté serveur. L'objet retourné est complété avec un champ `serverToken` avec un identifiant unique. Ce `serverToken` devra être envoyé par le client lorsqu'il interagit avec le serveur sur cet objet.

### Annotations de paramètre
* `PathParam` : Récupère un paramètre depuis une partie de la route (indiqué dans la route avec {myParamName}).
* `QueryParam` : Récupère un paramètre depuis la requête. Peut être un paramètre dans l'url `url?id=12&name=martin` ou un paramètre de formulaire HTTP (en POST) (l'API Servlet Java ne fait pas la différence)
* `InnerBodyParam` : Récupère un paramètre depuis un champ du body. Le body doit être un objet Json. *Cette annotation est spécifique à Vega et permet d'éviter des Objets conteneurs à usage unique)*
* `HeaderParam` : Récupère un paramètre depuis le header de la requête.
* `Validate` : Définit une liste spécifique de `DtObjectValidator`. Ces validators seront passés sur les champs modifiés avant l'appel au service. Les erreurs sont ajoutées à l'UiMessageStack et envoyées avec un code HTTP 422 (SC_UNPROCESSABLE_ENTITY) le cas échéant.
* `ExcludedFields` : Définit les champs interdits de la request entrante sur un objet. A utiliser dans un objectif de sécurité. Lance une erreur `VSecurityException` si le contrat n'est pas respecté.
* `IncludedFields` : Définit les champs acceptés de la request entrante sur un objet (les autres sont interdits). A utiliser dans un objectif de sécurité. Lance une erreur `VSecurityException` si le contrat n'est pas respecté.
* `ServerSideRead` : indique au serveur de recharger la copie sauvegardée d'un objet et de le mettre à jour avec les modifications portées par la request. L'objet JSON entrant est partiel et doit définir un champ `serverToken` avec le token identifiant de l'objet source.
* `AutoSortAndPagination` : Ajoute le support automatique de la pagination et du tri pour un service simple de la forme `List<?> loadBy(Criteria crit)`.

## Références
*Une partie de la motivation / de l'inspiration de ce module vient de l'[OWASP](https://www.owasp.org/index.php/REST_Security_Cheat_Sheet#Input_validation_101) et de [@veesahni](http://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api#rate-limiting)*
