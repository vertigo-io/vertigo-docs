# Vega

Le module **Vega** permet de mettre en place simplement des WebServices dans l'application. 
Ce module est orienté pour le développement d'applications *Single-Page-Application*, mais peut évidement être utilisé pour des WebServices d'applications Web standards ou de SI à SI.
Il intègre un ensemble de solutions *production-ready* pour accélérer et sécuriser l'application.

## Composant interne
En sous jacent, le module utilise [java-spark](https://github.com/perwendel/spark).<br/>
Et propose une publication de l'API par le standard [Swagger](https://swagger.io/).<br/>
Pour publier les WebServices, il suffit d'un ensemble d'annotations sur une Facade de vos services métiers. Les Annotations sont volontairement une sous partie du standard [JAX-RS](https://javaee.github.io/javaee-spec/javadocs/javax/ws/rs/package-summary.html)

## Quick start
1\. Le service doit être déclaré comme un *Composant* Vertigo
2\. Le service doit implémenter [WebServices](https://github.com/vertigo-io/vertigo/blob/master/vertigo-vega-api/src/main/java/io/vertigo/vega/webservice/WebServices.java)  
3\. Ajouter les annotations sur les méthodes, exemple:   
```Java 
@AnonymousAccessAllowed 
@GET("/anonymousTest")
```
4\. Ajouter la feature *webservices* dans la configuration :

```yaml
modules
  io.vertigo.commons.CommonsFeatures:
  io.vertigo.vega.VegaFeatures:
    features:
      - webservices
    featuresConfig:
      - webservices.apiPrefix
          apiPrefix : /api
```
  
5\. Démmarer l'application
6\. **C'est bon**. Vous pouvez appeler votre webservice:  [http//:localhost:8088/anonymousTest] (http//:localhost:8088/anonymousTest)

Vertigo propose des WebServices intégrés [SwaggerWebServices](https://github.com/vertigo-io/vertigo/blob/master/vertigo-vega-impl/src/main/java/io/vertigo/vega/impl/webservice/catalog/SwaggerWebServices.java) qui vous donne la vue de l'api des WebServices disponibles.<br/>
* IHM Swagger :  [http//:localhost:8088/swaggerUi] (http//:localhost:8088/swaggerUi)
* API Swagger seule : [http//:localhost:8088/swaggerApi] (http//:localhost:8088/swaggerApi)


## API

### Code exemples :
De nombreux exemples complets sont présent dans les tests sur GitHub : [Tests Exemples](https://github.com/vertigo-io/vertigo/tree/master/vertigo-vega-impl/src/test/java/io/vertigo/vega/webservice/data/ws)

### Syntaxe des routes
Lors de la définition des routes, vous pouvez utiliser `{myParamName}` pour déclarer une variable de l'url qui est utilisée comme paramètre du service.  
Example:
```Java
@GET("/contact/{id}")
public Contact getContact(@PathParam("conId") final int contactId) {
...
}
```
Cet exemple accepte les URLs comme `http://localhost:8080/contact/134` ou `http://localhost:8080/contact/756`  
et appelle le service sous-jacent commme `getContact(134)` ou `getContact(756)`


### Objet de retour
Le resultat de votre service est automatiquement sérialisé en Json.
La serialisation Json est optimisée pour les Objects spécifiques de Vertigo :
- Entity
- UiObject : object composite générique, utiliser pour charger un context complet de page
- FacetedQueryResult : l'objet resultat du moteur de recherche (avec facettes, groupements et highlights)

```Java
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
```Json
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
En cas d'Exceptions levées dans le service, un code HTTP est automatiquement positionné et un message d'erreur Json est envoyé. Le retour d'erreur est volontairement simplifié pour des raisons de sécurité de l'application (pas de stacktrace par exemple)
```Json
{
  "globalErrors": "Error message or simple class name"
}
```

Si le service lance une **Exception utilisateur** (saisie utilisateur ou une erreur métier), le message est plus complete et précise les informations pour le positionement des erreurs dans l'écrans :
```Json
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

Pour les erreurs sur un object, le nom repris dans le Json d'erreur est le même que celui envoyé lors de la request. Pour un object dans une liste, le nom utilisé est :
`nom de la liste dans la request`+ `idx` + index dans la liste (commence à 0)
Example : 
```Json
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
Vertigo Vega propose de conserver un état coté serveur. 

Cette fonctionalité permet d'adresser simplement le besoin d'envoyer le minimum de données coté client (nécessaire pour des besoins de sécurité des données ou de contraintes réseau),
et de continuer d'utiliser des objets complèts coté serveur dans les services métiers pour les garder les plus simples possibles et ne pas multiplier les API d'entrées.
En conservant les services métiers sur des objets complets, ceux-ci sont plus facilement testables car il n'est pas nécessaire de gérer la combinatoire des entrées/sorties des WebServices.

!> L'état server-side est limité dans le temps, lié à la session utilisateur et non modifiable. S'il y a un besoin de modifications concurrentes, cela devra être traité au niveau du service.

Grace à cette fonctionnalité vous pouvez : 
* conserver l'état d'un objet à l'envoi, filtrer les champs qui doivent être réellement nécessaire
* au retour du client, Vega fusionne l'état conservé et le nouveau état envoyé par le client (filtré lui aussi)
* utiliser un object métier complèt dans la couche métier.

Pour ce faire, vous avez à votre disposition trois annotations :
* `ServerSideSave` : appliquée sur une Méthode, il indique à Vega de conserver l'objet retourné et poser une référence avec un `serverToken` id.
* `ServerSideRead` : appliquée sur un Parametre, il indique que Vega qu'il attend un objet Json avec quelques champs et une référence `serverToken`, Vega fusionnera l'ancien état avec les données reçues. Toutes les validations seront effectuées comme lors de n'importe quel appels.
* `ServerSideConsume` : Comme `ServerSideRead`, mais l'état conservé est consommé lors de l'appel.

Exemple : 
```Java
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

Request: `GET http://localhost:8088/contact/1`

Response:
```Json
{
	"conId":"1",
	"honorificCode":"MR_",
	"name":"Martin",
	"firstName":"Jean",
	"serverToken":"cb44ab11-4eac-41e9-a3d1-c0fc20ea55e1"
}
```


Request: `PUT http://localhost:8088/contact/1`
```Json
{
	"firstName":"Jean-denis",
	"serverToken":"cb44ab11-4eac-41e9-a3d1-c0fc20ea55e1"
}
```
Response:
```Json
{
	"conId":"1",
	"honorificCode":"MR_",
	"name":"Martin",
	"firstName":"Jean-denis",
	"serverToken":"b04edfef-7385-4d5d-b5ca-23d195c87200"
}
```

!>
!> TODO : A traduire
!>

### AccessToken security
This feature provides a limited access token. To manage this token developers have to use three annotations :
* `AccessTokenPublish` : apply on method, it generates a random unique token and sets a response header `x-access-token`.
* `AccessTokenMandatory` : apply on method, it ensures the client sent a valid `x-access-token` as request header. If not the server sends a `HTTP 403 FORBIDDEN` `Invalid access token` error.
* `AccessTokenConsume` : same as AccessTokenMandatory, but consumes `x-access-token` at call (token invalidation).



### Rate-Limit security
For security purpose all published web-services in _Vertigo-Vega/rest_ are rate-limited. By default, the limit is set at 150 calls per 15 minutes (sliding window) per user. That's one call every 6 seconds. Anonymous users share this limit among them.
Server sends information in response headers:
* `X-Rate-Limit-Limit` : the rate limit ceiling for that given request
* `X-Rate-Limit-Remaining` : the number of requests left for the M minute window
* `X-Rate-Limit-Reset` : the remaining seconds before the rate limit resets

If limit is exceeded the server issues a `HTTP 429 TOO_MANY_REQUEST` error. Note also this is a per server instance limit.

### DtListDelta support
DtListDelta is a specific object supported by _Vertigo-Vega/rest_ for it's web-service.
It's used for aggregating list modifications : created, updated and deleted objects send from IHM.
The request Json must respect this format: 
```Json
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


Example : 
```Java
@POST("/contacts/delta")
@ExcludedFields({ "birthday", "email", "passport" }) // All secret fields are excluded
public String updateContacts( final DtListDelta<Contacts> contactsDelta) {
                //objects were checked, just like single updates.
		updateContacts(contactsDelta.getCreates(),contactsDelta.getUpdates(),contactsDelta.getDeletes()); 
		return "OK : contacts updated";
}
```

### AutoSortAndPagination support
AutoSortAndPagination annotation is the simplest way to publish a service with sorting and paging.  
You just publish a service which return a DtList and add this annotation.  

Example :
```Java
@AutoSortAndPagination
@GET("/contacts")
public DtList<Contacts> searchContacts( final ContactCriteria contactCriteria) {
    //call specific search service, and return all datas (think to add a cpu/memory/user friendly limit like 250)
		return contactService.search(contactCriteria); 
}
```

**Vega** will keep a copy of the full list and return :
* _header_ : `x-total-count` : the total count of this list
* _header_ : `listServerToken` : the serverSide list's id token, should be resend by client when paging or sorting the list
* _body_ : the sublist in Json format

When client sort or change page, it should send :
* _query_ : `top` : max elements to return
* _query_ : `skip` : offset of first element to return
* _query_ : `sortFieldName` : field name in camelCase to sort by
* _query_ : `sortDesc` : true/false for sort order
* _query_ : `listServerToken` : refering to a serverSide list
* any payloads do you need, just like other services

Note that you can do the same thing within your own service.   
To keep this API, you should just declare a ``` @QueryParam(".") UiListState uiListState``` for your service.   
UiListState is a representation of sublist state, with `top`, `skip`, `sortFieldName`, `sortDesc` and `listServerToken` fields.   

Example :
```Java
@GET("/contacts")
public DtList<Contacts> searchContacts( final ContactCriteria contactCriteria, @QueryParam("") UiListState uiListState) {
    //think to add a total-count metadata to the returned list.
		return contactService.search(contactCriteria, uiListState.getTop(), uiListState.getSkip(), uiListState.getSortFieldName(), uiListState.getSortDesc()); 
}
```


### HTTP Code
Vertigo automatically returns HTTP Code :
* `200 Success` : When things are ok
* `201 Created` : By convention when things are ok and method name starts with 'create'
* `204 No Content` : When things are ok but there is no returning data
* `401 Unauthorized` : No valid session
* `403 Forbidden` : Not enough rights
* `404 Not found` : No service found
* `400 Bad request` : Default returning code
* `422 Unprocessable entity` : Validations or business error
* `429 Too many request` : Anti spam security (must wait for next time window)
* `500 Internal server error` : As it says any server error, should return a message in body

***

## Annotations reference

### Classes annotations
* `PathPrefix` : Used to add a prefix to all route of a class

### Methods annotations
* `Doc` : Adds a documentation to your route. Displayed when calling default `/catalog` url
* `AnonymousAccessAllowed` : Allows access for anonymous user (Current UserSession.isAuthenticated() == false)
* `SessionLess` : Don't create a new Session when calling this route
* `SessionInvalidate` : Invalidates Session on call
* `GET` : Defines a `GET` route for this method. `GET` is use for load-like services. `GET` should have only query parameters, no body and are idempotent (can be call again with same result, if no concurrency of course).
* `POST` : Defines a `POST` route for this method. `POST` is used for save-like services and most business services (archive, send, compute, ...). `POST` could have body payload and are not-idempotent (server state is modified). It's a best practice to decide how successive calls from a same origin should behave (browser back feature or user misbehavior like mutiple click). If necessary a business constraint must prevent such executions.
* `DELETE` : Defines a `DELETE` route for this method. `DELETE` is used for remove-like services. `DELETE` might have body payload and are not-idempotent (it changes the server state).
* `PUT` : Defines a `PUT` route for this method. `PUT` is used for update-like services. `PUT` could have body payload and are idempotent (can be call again with same result, if no concurrency of course).
* `ExcludedFields` : Defines fields to be excluded from output response. Use it for security purpose.
* `IncludedFields` : Defines fields to be included into output response (others are excluded). Use it for security purpose.
* `AccessTokenPublish` : Returns a new AccessToken as header `x-access-token`. This token may be use for a limited time. The token is bounded to one user and can't be use by others. Use it for security purpose.
* `AccessTokenMandatory` : Defines this service as **AccessTokenProtected**. The service will require a valid AccessToken from query header `x-access-token`. Use it for security purpose.
* `AccessTokenConsume` : Defines this service as **AccessTokenProtected**. The service will require a valid AccessToken from query header `x-access-token`. When this service succeeds the token is consumed and can't be reused anymore. Use it for security purpose.
* `ServerSideSave` : Tells the server to keep a saved version of this object server side. The returned json view is completed with a `serverToken` field. This `serverToken` must be sent back by client when interacting with server for this object.

### Parameters annotations
* `PathParam` : maps a parameter from url
* `QueryParam` : maps a parameter from query. Can be url params : `url?id=12&name=martin` or http form params.
* `InnerBodyParam` : maps a parameter from a body json field. The body must be a json object.
* `HeaderParam` : maps a parameter from a header field.
* `Validate` : defines a list of specific `DtObjectValidator`, which must be passed on modified field before the service call. Errors are added into UiMessageStack and send in a 422 (SC_UNPROCESSABLE_ENTITY) Response.
* `ExcludedFields` : Defines fields to be excluded from input request. Use it for security purpose.
* `IncludedFields` : Defines fields to be accept from input request (other are rejected). Use it for security purpose.
* `ServerSideRead` : Tells the server to read a previously saved object and merge it with incoming updates. The partial json object must defined a `serverToken` field which contains the previously saved object reference token. 
* `AutoSortAndPagination` : Adds pagination and sort support for a standard `List<?> loadBy(Criteria crit)` service.

## References
_Some of motivations and inspirations comes from [OWASP](https://www.owasp.org/index.php/REST_Security_Cheat_Sheet#Input_validation_101) and [@veesahni](http://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api#rate-limiting)_  