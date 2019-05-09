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

### Paramètres

Vertigo Vega va automatiquement mapper la requete entrant Json vers votre méthode de WebService. Les annotations positionnés permet d'indiquer comme ce fait ce mapping. 
Vega est prévu pour gérer un maximum de cas, tout en proposant des optimisations à travers des objets propre à Vertigo (résultat de recherche, état des listes, Optional, ...).
La plus part du temps il s'agit de surtout indiquer la source de la données (paramètres de l'url, body de requetes, headers, ...).
Par défaut le contenu est attendu dans le body (**Attention** la norme HTTP indique que les requetes *GET* n'ont pas de body)

Le cas le plus courant est de réceptionner directement un DtObject, dans ce cas Vega s'occupe de formatter le Json en type Java et de valider l'objet vis-à-vis des contraintes des domains.
Il est possible de récupérer directement la saisie utilisateur en utilisant les objets génériques `UiObject` ou `UiList<MyDto>`.

Vega peuple quelques paramètres implicites (qui ne sont pas envoyé par le client). Ces éléments implicites permettent d'agir plus finement sur le comportement du WebServices. 
- UiMessageStack : pile des messages à retourner à l'IHM. Avec un états (Success, Info, Warning, Error) et une portée (globale, par objet, par champ)
- HttpServletRequest : Requete HTTP
- HttpServletResponse : Response HTTP

?> Voir les annotations directements pour le détail

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

?> Cette fonction est traitée par [`ServerSideStateWebServiceHandlerPlugin`](https://github.com/vertigo-io/vertigo/blob/master/vertigo-vega-impl/src/main/java/io/vertigo/vega/plugins/webservice/handler/ServerSideStateWebServiceHandlerPlugin.java)


### Sécurité **AccessToken**
Cette fonctionnalité propose un Token d'acces limité. La gestion de ce Token est géré par le développeur par 3 annotations :
* `AccessTokenPublish` : posée sur une méthode, il génère un Token unique aléatoire et l'ajoute comme *header* la *Response* `x-access-token`.
* `AccessTokenMandatory` : posée sur une méthode, il assure que le client a envoyé un *header* de *Request* `x-access-token` valide. Sinon le serveur retourne une erreur `HTTP 403 FORBIDDEN` `Invalid access token`.
* `AccessTokenConsume` : Idem à `AccessTokenMandatory`, mais consomme le `x-access-token` lors de l'appel (token invalidation).

### Sécurité **Rate-Limit**
Pour des raisons de sécurité, tous les WebServices publiés par Vertigo Vega sont protégés (par défaut) contre les appels massifs. La limite est de 150 appels par utilisateur sur des fenètres de 5 minutes, ce qui représente 1 appel toutes les 2 secondes.
Les utilisateurs anonymes partagent le même compteur de limite.Noté que la limite est comptabilisée par instance serveur.

Le serveur envoye des informations dans des *headers* de la *Response*
* `X-Rate-Limit-Limit` : Le maximum d'appel autorisé pour cette requete
* `X-Rate-Limit-Remaining` : Le nombre d'appel restant dans la fenetre de temps en cours
* `X-Rate-Limit-Reset` : Le nombre de seconde restant avant une remise à zéro du compteur

Si la limite du serveur est dépassée, le serveur retourne une erreur `HTTP 429 TOO_MANY_REQUEST`.

?> Cette fonction est traitée par [`RateLimitingWebServiceHandlerPlugin`](https://github.com/vertigo-io/vertigo/blob/master/vertigo-vega-impl/src/main/java/io/vertigo/vega/plugins/webservice/handler/RateLimitingWebServiceHandlerPlugin.java)
?> Le handler propose des paramètres optionels : 
?> - *windowSeconds* : Taille de la fenètre en seconde
?> - *limitValue* : Nombre d'appel maximum (dans la durée de la fenètre)

### Objet d'IHM **DtListDelta**
`DtListDelta` est un objet spécifique utilisé par Vertigo Vega.
Il est utilisé pour aggréger les modifications apportées à une liste : création, mise à jour ou suppression réalisées coté client et retourné au serveur en 1 appel.
La requete Json doit respecter ce format : 
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

Exemple : 
```Java
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
```Java
@AutoSortAndPagination
@GET("/contacts")
public DtList<Contacts> searchContacts( final ContactCriteria contactCriteria) {
    //call specific search service, and return all datas (think to add a cpu/memory/user friendly limit like 250)
		return contactService.search(contactCriteria); 
}
```

Comment ca marche :<br/>
**Vega** conserve une copie de la liste coté serveur et retourne :
* _header_ : `x-total-count` : la taille totale de la liste
* _header_ : `listServerToken` : le token de la liste coté serveur. Il devra être renvoyé par le client lorsqu'il faudra trier ou filtrer la liste
* _body_ : la portion de la liste au format Json (triée et filtrée)

Lorsque l'IHM tri ou change de page, il doit retourner : 
* _query_ : `top` : nombre max d'élément à retourner
* _query_ : `skip` : offset du premier élément à retourner
* _query_ : `sortFieldName` : nom du champ protant le tri
* _query_ : `sortDesc` : true/false pour l'ordre de tri
* _query_ : `listServerToken` : token de la liste (issus des précédents appels)
* n'importe quels autres données nécessaires, comme n'importe quel service

Noter que vous pouvez faire la même chose dans vos WebServices sans l'annotation (par exemple pour trier ou paginer dans la couche service ou dans la base de données).
Pour avoir la même API, vous avez à ajouter un paramètre  ``` @QueryParam(".") DtListState dtListState```

DtListState est une représentation de l'état d'une sous liste, avec les champs `top`, `skip`, `sortFieldName`, `sortDesc` et `listServerToken`   

Exemple :
```Java
@GET("/contacts")
public DtList<Contacts> searchContacts( final ContactCriteria contactCriteria, @QueryParam("") UiListState uiListState) {
    //think to add a total-count metadata to the returned list.
		return contactService.search(contactCriteria, uiListState.getTop(), uiListState.getSkip(), uiListState.getSortFieldName(), uiListState.getSortDesc()); 
}
```

### HTTP Code
Vertigo Vega retourne automatiquement les codes HTTP suivant  :
* `200 Success` : Quand tout va bien
* `201 Created` : Par convention tout va bien et la méthode commence par 'create'
* `204 No Content` : Quand tout va bien mais qu'il n'y a aucune donnée en retour (return null ou void)
* `401 Unauthorized` : Pas de session valide (`SessionException`)
* `403 Forbidden` : Droits insuffisants (`VSecurityException`)
* `404 Not found` : Pas de WebService/Resource trouvés
* `400 Bad request` : Erreur de syntaxe de requête (`JsonSyntaxException`)
* `422 Unprocessable entity` : Erreur de validation ou de règle métier (`ValidationUserException` ou `VUserException`)
* `429 Too many request` : Sécurité Anti spam (impose d'attendre la prochaine fenètre) (`TooManyRequestException`)
* `500 Internal server error` : Erreur interne, doit retourner un message dans le corps de la *Response*

***

## Référence complète des Annotations

### Annotations de class
* `PathPrefix` : Utilser pour ajouter un préfix commun à toutes les routes de la class

### Annotations de méthode
* `Doc` : Ajoute une documentation à la route. Apparait dans la spécification de l'API (Swagger)
* `AnonymousAccessAllowed` : Autorise l'accès aux utilisateurs anonymes (Current UserSession.isAuthenticated() == false)
* `SessionLess` : Indique de ne pas créer de Session HTTP lors de l'appel à cette route (pour les WebServices SI à SI)
* `SessionInvalidate` : Invalide la Session HTTP lors de l'appel.
* `GET` : Définit une route en `GET` pour cette méthode. `GET` est utilisé pour les services de type *chargement*. `GET` ne devrait avoir que des paramètres d'url, pas de body et devrait être idempotent (chaque appel donne le même résultat, si il n'y a pas de modification concurentes évidement).
* `POST` : Définit une route en `POST` pour cette méthode. `POST` est utilisé pour les services de type *enregistrement* et pour la majorité des services métier (archive, send, compute, ...). `POST` peut avoir un contenu dans le body et n'ont pas à être idempotent (l'état serveur est modifié). C'est une bonne pratique de décider comment des appels successifs depuis une même origine doit se comporter (gestion du back navigateur ou le multi-click des utilisateurs). Il parfois plus simple de mettre ne place des contraintes métiers pour éviter ces multiples éxécutions (contraintes d'unicité, vérification des transitions d'états, ...).
* `DELETE` : Définit une route `DELETE` pour cette méthode. `DELETE` est utilisé pour les services de type *suppression*. `DELETE` devrait rarement avoir un body et ne sont pas idempotent (l'état serveur est modifié).
* `PUT` : Définit une route `PUT` pour cette méthode. `PUT` est utilisé pour les services de type *création* ou *mise à jour* simple. `PUT` devrait avoir un body et doit être idempotent (chaque appel donne le même résultat, si il n'y a pas de modification concurentes évidement). Les principes **RESTful** sont assez ambigue sur l'utilisation de **PUT** et de **POST**, nous préconisons surtout de nous fier au contrat : **PUT** idempotent, **POST** non.
* `ExcludedFields` : Définit les champs a exclure de la réponse. A utiliser dans un objectif de sécurité.
* `IncludedFields` : Définit les champs a inclure dans la réponse (les autres sont exclus). A utiliser dans un objectif de sécurité.
* `AccessTokenPublish` : Retourne un nouveau Token d'accès sous la forme d'un header `x-access-token`. Ce Token peut être utilisé pour un temps limité. Le Token est lié à un utilisateur et ne peut être utilisé par d'autres. A utiliser dans un objectif de sécurité.
* `AccessTokenMandatory` : Définit le service comme étant *protégé par AccessToken*. Le service impose la présence d'un AccessToken valide dans le header `x-access-token` de la requête. A utiliser dans un objectif de sécurité.
* `AccessTokenConsume` : Définit le service comme étant *protégé par AccessToken*. Le service impose la présence d'un AccessToken valide dans le header `x-access-token` de la requête. Quand ce service est appellé et termine sans erreur, le Token est consommé et ne peut plus être utilisé. A utiliser dans un objectif de sécurité.
* `ServerSideSave` : Indique au serveur de conserver une copie de l'objet complèt coté serveur. L'objet retourné est complété avec un champ `serverToken` avec un identifiant unique. Ce `serverToken` devra être envoyé par le client lorsqu'il intéragit avec le serveur sur cet objet.

### Annotations de paramètre
* `PathParam` : Récupère un paramètre depuis une partie de la route (indiqué dans la route avec {myParamName}).
* `QueryParam` : Récupère un paramètre depuis la requête. Peut être un paramètre dans l'url `url?id=12&name=martin` ou un paramètre de formulaire HTTP (en POST) (l'API Servlet Java ne fait pas la différence)
* `InnerBodyParam` : Récupère un paramètre depuis un champ du body. Le body doit être un objet Json. *Cette annotation est spécifique à Vega et permet d'éviter des Objets conteneur à usage unique)*
* `HeaderParam` : Récupère un paramètre depuis le header de la requête.
* `Validate` : Définit une liste spécifique de `DtObjectValidator`. Ces validators seront passés sur les champs modifiés avant l'appel au service. Les erreurs sont ajoutées à l'UiMessageStack et envoyé avec un code HTTP 422 (SC_UNPROCESSABLE_ENTITY) le cas échéant.
* `ExcludedFields` : Définit les champs interdits de la request entrante sur un objet. A utiliser dans un objectif de sécurité. Lance une erreur `VSecurityException` si le contrat n'est pas respecté.
* `IncludedFields` : Définit les champs acceptés de la request entrante sur un objet (les autres sont interdits). A utiliser dans un objectif de sécurité. Lance une erreur `VSecurityException` si le contrat n'est pas respecté.
* `ServerSideRead` : indique au serveur de recharger la copie sauvegarder d'un objet et de le mettre à jour avec les modifications portées par la request. L'objet Json entrant est partiel et doit définir un champ `serverToken` avec le Token identifiant de l'objet source.
* `AutoSortAndPagination` : Ajout le support automatique de la pagination et du tri pour un service simple de la forme `List<?> loadBy(Criteria crit)`.

## Réferences
*Une partie de la motivation de l'inspiration de ce module vient de l'[OWASP](https://www.owasp.org/index.php/REST_Security_Cheat_Sheet#Input_validation_101) et de [@veesahni](http://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api#rate-limiting)*