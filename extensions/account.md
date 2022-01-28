# Account

Le module **Account** de Vertigo permet la gestion simplifiée des comptes utilisateurs. 
Ce module permet avant tout la mise à disposition des autres modules de la notion transverse de compte utilisateur. Ceci permet à Vertigo de proposer des extensions comme **"notifications"** ou **"commentaires"**. 

Ce module propose des fonctionnalités de gestion des utilisateurs réparties sur trois axes orthogonaux :
- **Authentication** : Gestion de l'authentification
- **Authorization** : Gestion des autorisations
- **Identity Provider** : Connexion avec des fournisseurs d'identité
 

## Configuration

Afin d'utiliser les fonctionnalités de **Account** il est nécessaire d'ajouter ce module à la configuration de l'application.
Pour plus de détails, vous pouvez vous rapporter au chapitre dédié à la [configuration](/basic/configuration) de l'application.


Voici une configuration typique d'une application utilisant le module Account

```yaml

modules
  io.vertigo.account.AccountFeatures:
    features:
      - security:
          userSessionClassName: io.mars.commons.MarsUserSession
      - account:
      - authentication:
      - authorization:
    featuresConfig:
      - account.store.store:
          userIdentityEntity: DtPerson
          groupIdentityEntity: DtGroups
          userAuthField: email
          photoFileInfo: FiFileInfoStd
          userToAccountMapping: 'id:personId, displayName:lastName, email:email, authToken:email, photo: picturefileId'
          groupToGroupAccountMapping: 'id:groupId, displayName:name'
      - authentication.text:
          filePath: /initdata/userAccounts.txt
```


### Features disponibles :
- **security** : Active le module, et le premier niveau de sécurité (authentifié ou non)
  - userSessionClassName : Nom de la class de la session applicative 
- **account** : Active les fonctionnalités autour de la notion de compte utilisateur
- **authentication** : Active les fonctionnalités d'authentification
- **authorization** : Active les fonctionnalités liées aux autorisations
- **identityProvider** : Active les fonctionnalités de fournisseur d'identité

### Paramètres des Features 

#### Account
- **account.store.store** : Stockage des *Account* par le *StoreManager*
  - userIdentityEntity : Nom de l'entité portant les *Account*
  - groupIdentityEntity : Nom de l'entité portant les groupes d'*Account* (doit avoir une FK vers *Account*)
  - userAuthField : Nom du champ relié à l'authentification *(authToken)*
  - photoFileInfo *(optional)* : Nom du *FileInfo* utilisé pour le stockage des photos
  - userToAccountMapping : Mapping des champs de l'entité vers *Account*
  - groupToGroupAccountMapping : Mapping des champs de l'entité Groupe vers *GroupeAccount*
- **account.store.text** : Stockage des *Account* par un fichier text
  - accountFilePath : Chemin du fichier des *Account* 
  - accountFilePattern : RegExp de lecture du fichier (avec des capturesGroup [nommés](https://stackoverflow.com/a/415635/2273508) : id, displayName, email, authToken, photoUrl)
  - groupFilePath : Chemin du fichier des *AccountGroup* 
  - groupFilePattern :  RegExp de lecture du fichier (avec des capturesGroup [nommés](https://stackoverflow.com/a/415635/2273508) : id, displayName, accountIds)
- **account.store.loader** : Stockage des *Account* délégué à un loader spécifique *(implements [AccountLoader](https://github.com/vertigo-io/vertigo/blob/master/vertigo-account-impl/src/main/java/io/vertigo/account/plugins/account/store/loader/AccountLoader.java))*
- **account.cache.memory** : Active le cache mémoire (**Attention** : pas de purge automatique)
- **account.cache.redis** : Active le cache Redis via le *RedisConnector* (**Attention** : pas de purge automatique)

#### Authorization
?> Pas de configuration particulière. Le comportement de ce composant est porté par le fichier de configuration des règles des [Autorisations](#Autorisations). 


## Authentification

### Principe

L'authentification dans une application métier est basée sur le rapprochement d'un moyen d'Authentification avec une source d'authentification.

- **AuthenticationToken** représente le moyen d'authentification. 
- Les **AuthenticationPlugin** représentent les sources d'authentification autorisées par le développeur.

### Configuration 

Vertigo propose, de base, deux types de moyens d'authentification :
- **UsernameAuthenticationToken** : Une seule information texte représentant le *Login* de l'utilisateur
- **UsernamePasswordAuthenticationToken** : Deux informations texte, de type *Login* / *Password*

Vertigo propose quatre types de source d'authentification :
- **LdapAuthenticationPlugin** : Authentification par Login/Password au près d'un LDAP. 
  - Si authentifié retourne le Login.
- **StoreAuthenticationPlugin** : Authentification par Login/Password ou Login seul au près de la base de données.
  - Si authentifié peut retourner une autre colonne de la table (pour un token de sécurité par exemple)
  - Le Password doit être salé et hashé par le `PasswordHelper` de Vertigo (ie : PBKDF2)
- **TextAuthenticationPlugin** : Authentification par Login/Password ou Login seul à partir d'un fichier texte.
  - Si authentifié retourne la clé du compte
  - Le Password doit être salé et hashé par le `PasswordHelper` de Vertigo (ie : PBKDF2)
- **MockAuthenticationPlugin** : Authentification par Login/Password ou Login, utilisé pour les tests (tous comptes autorisés).


**Configuration de la *Feature* (Yaml)**

- **authentication.text** : Permet l'authentification basée sur un fichier texte
  - filePath : Chemin du fichier. (Format du fichier : accountKey    login    password    //comments )
?> Le hash des mots de passe utilise l'algorithme [PBKDF2WithHmacSHA256](https://en.wikipedia.org/wiki/PBKDF2)

- **authentication.store** : Permet l'authentification basée sur le *StoreManager*
  - userCredentialEntity : Nom de l'entité portant l'authentification
  - userLoginField : Nom du champ 
  - userPasswordField : Nom du champ password
  - userTokenIdField : Nom du champ *authToken* (champ utilisé pour le lien vers *Account*)
?> Le hash des mots de passe utilise l'algorithme [PBKDF2WithHmacSHA256](https://en.wikipedia.org/wiki/PBKDF2)

- **authentication.ldap** : Permet l'authentification déportée sur un LDAP
  - userLoginTemplate : Template du DN de l'utilisateur (contient {0} pour fusionner le login)
  - ldapServerHost : Nom du serveur LDAP
  - ldapServerPort : Port du serveur LDAP
  
- **authentication.mock** : Pour les tests, authentification toujours réussie


### Utilisations

L'usage de ce module est assez simple :
- On récupère les informations depuis le controller
- On crée un Token portant ces informations
- On délègue l'authentification à l'`authenticationManager`
- Si l'authentification est bonne, on récupère l'entité de l'utilisateur et on fait les traitements spécifiques (association dans la session, récupération des droits, etc...) 
 
Globalement le login est réalisé ainsi dans le service métier : 

```java
public void login(final String login, final String password) {
  final Optional<Account> loggedAccount = authenticationManager.login(new UsernamePasswordAuthenticationToken(login, password));
  if (!loggedAccount.isPresent()) {
    throw new VUserException("Login or Password invalid");
  }
  final Account account = loggedAccount.get();
  final Person person = personServices.getPerson(Long.valueOf(account.getId()));
  getUserSession().setLoggedPerson(person);
  
  //Load Profil and authorizations
  getUserSession().setCurrentProfile("Administrator");
}
```

## Autorisations

### Principes

Dans une application métier, on considère en général que tous les utilisateurs n'auront pas accès à tout. Vertigo propose un mécanisme de sécurité qui permet de protéger les éléments de l'application qui doivent l'être.

D'un point de vue technique, le mécanisme permet de sécuriser des éléments fins de l'application (que l'on nomme *Ressource*) : des pages, des services, des données ou autres.
Il peut aussi s'agir de quelque chose de plus abstrait comme un caractère **confidentiel** transverse à l'application.<br/>
Mais pour rester compréhensible, le développeur va paramétrer le mécanisme de sécurité pour englober ces *Ressources* dans des *Authorizations* qui correspondent à des fonctionnalités proposées par l'application 
(*Consulter les dossiers*, *Déposer un dossier*, *Valider les dossiers*, ...)

Le mécanisme de sécurité de Vertigo est assez *bas niveau*. Vertigo ne connait que la notion d' **Authorization** : soit globales, soit portées par une entité (les `SecuredEntity`).

Il est laissé à l'application la charge de rationaliser le modèle, par exemple il est préconisé que l'application gère la sécurité à un niveau plus macro avec une notion de *Profil* et de *Périmètre*.
La liste des *Profils* associés à un utilisateur est spécifique à l'application et à sa charge. 
Un *Profil* étant une liste d'**Authorizations** rattaché à un **Périmètre** applicatif.

**Note**<br/>
La bonne pratique dans ce domaine est que si l'utilisateur a plusieurs **Profils**, il ne devra en avoir qu'un seul actif à la fois (il pourra en changer pendant sa session), 
ceci afin d'éviter des collisions (intersections) de règles de sécurité difficiles à comprendre, à implémenter de manière performante et à tester.<br/>
Dans un système où la gestion des utilisateurs est centralisée, le **Profil** utilisateur peut être géré par le système centralisé (il fournit le **Profil** par utilisateur par appli).

### Notion de *contexte de sécurité*

Le modèle présenté ci-dessus permet déjà de gérer de nombreux cas. Mais plus les clients sont gros et plus ils ont une organisation forte qui pèse sur la sécurité de l'application. 
Il apparaît alors que la sécurité doit être relative à un contexte. Ce contexte peut être géographique, organisationnel, lié à un état, à une date ou autre, voir tout ça en même temps. <br/>
Ce *contexte de sécurité* est aussi appellé **Périmètre** de sécurité.

Le mécanisme de Vertigo permet d’assurer et de mettre en place ce type de sécurité de manière générique dans les projets.
Au sens vertigo le *contexte de sécurité* est une notion :

- dans laquelle s'inscrivent les utilisateurs et les `SecuredEntities` 
- qui est composée d'axes (géographique, organisationnel, ...)
- dont chaque axe peut être hiérarchique (ex: continent, pays, régions, communes, villes)

Pour rester compatible avec le mécanisme prévu par Vertigo, l'application doit respecter quelques règles :

- L'utilisateur n'a qu'un et un seul contexte actif à la fois
- Le contexte de l'utilisateur est transverse à ses droits 
- La hiérarchie du contexte est sans exception et correctement orienté (un parent accède à tous ses enfants, petits-enfants ...) 

!>Les exceptions devront être gérées spécifiquement par l'application.


### Types d'autorisation

Deux types d'autorisations sont proposés :
- **Global Authorizations** : Autorisations globales utilisées pour protéger des fonctions de l'application (écrans, boutons, traitements, ...)
  - name : Code de l'autorisation
  - label : Libellé de l'autorisation

- **Secured Entity Operations** : Autorisations pour une opération sur une entité sécurisée
  - entity : Nom de l'entité protégé
  - securityFields : Liste des champs participant aux contraintes de sécurité (ie : critères de filtrage)
  - securityDimensions : Liste de dimensions de sécurité (pseudo champs de sécurité déduit d'autres champs de l'entité)
    - name : Nom de la dimension
    - type : Type de la dimension (ENUM : pour une énumération ordonnée, TREE : pour une structure hiérarchique)
    - values *(Type:ENUM)* : Liste ordonnée des valeurs possibles
    - fields *(Type:TREE)* : Liste des champs ordonnés (et à plat) de l'arborescence
  - operations : Liste des opérations possibles sur l'entité
    - __comment : Permet de placer un commentaire dans la configuration
    - name : Code de l'opération
    - label : Libellé de l'opération
    - grants *(optional)* : Liste d'opérations données par cette opération (ie : l'utilisateur ayant cette opération, possède aussi celles du grants)
    - overrides *(optional)* : Liste d'opérations surchargées par cette opération (ie : pour l'utilisateur ayant cette opération, la règle de cette opération surcharge celles des autres overrides)
    - rules : Liste de règle de sécurité. 
      - Syntaxe proche du SQL ( myField *operateur* value (and|or)? )*
      - Les différentes règles de la liste sont considérées en **OU**
      - **${myParam}** pour placer une propriété du context utilisateur (propriété de périmètre dans la session du user)
      - Ecriture simple pour les axes **TREE** : GEO <= ${geo} : On sélectionne les `SecuredEntities` *inférieur ou égale* dans le périmètre géographique de l'utilisateur (Ex: toutes les communes ou dans le département d'un responsable départementale)
      - Ecriture simple pour les axes **ENUM** : etaCd>=PUB AND etaCd<ARC (Ex : tous les `SecuredEntities` dont l'état est *supérieur ou égale* à 'PUB'*lié* et *strictement inférieur* à 'ARC'*hivé*)

> Chaque **Secured Entity Operation** est associée à une authorization générée. Il ainsi possible de vérifier si un utilisateur a "à priori" le droit d'éffectuer une opération sur une entité avant même de regarder le contexte de sécurité de l'utilisateur.
> Ceci est utilisé, notamment pour gérer les éléments d'IHM affiché.<br/>
> **Exemple:** Récupération des opérations possibles sur une entité pour déterminer les menus à proposer

### Utilisations

La force du modèle de sécurité de Vertigo, est de permettre une unique définition du modèle pour une utilisation dans plusieurs technologies ayant chacune leur syntaxe et leurs cas d'usage.

#### API

L'API proposée par le AuthorizationManager permet de gérer la plupart des cas d'usages rencontrés.

- **hasAuthorization(AuthorizationName...)** : Vérifie que l'utilisateur a l'une des autorisations passées en paramètre
- **isAuthorized(Entity, OperationName)** : Vérifie que l'utilisateur peut réaliser l'opération sur l'**entity** avec son contexte de sécurité actif
- **getCriteriaSecurity(Class<Entity>, OperationName)** : Génère un [Criteria] valable pour l'utilisateur connecté, un type d'entité et une opération. Le Criteria permet de nombreux usages, voir détails plus bas.
- **getSearchSecurity(Class<KeyConcept>, OperationName)** : Génère le filtre de sécurité dans la syntaxe ElasticSearch applicable pour l'utilisateur connecté, un type d'entité et une opération.
- **getAuthorizedOperations(KeyConcept)** : Liste des opérations possibles par l'utilisateur connecté sur l'entité passée en paramètre (utilisé par la couche IHM pour adapter les actions possibles)

#### Criteria

Le Criteria Vertigo est un élément transverse représentant un filtre, qui peut ensuite être traduit dans plusieurs langages.

> Peut être utilisé directement dans le DAO.findAll

- **toPredicate** : Conversion en Predicat Java (pour les stream, ou un test localisé)
- **toSQL** : Conversion en clause WHERE pour une requète SQL (préférer l'usage par le DAO)

 
Pour l'appliquer sur des requetes générales du DAO
```Java
 final Criteria<Equipment> securityFilter = authorizationManager.getCriteriaSecurity(Equipment.class, SecuredEntities.EquipmentOperations.read);
	return equipmentDAO.findAll(securityFilter, dtListState);
```

 Pour l'appliquer sur des tasks spécifique du DAO.
 Il faut 
```Java
return equipmentDAO.getLastPurchasedEquipmentsByBaseId(baseId,
				AuthorizationUtil.authorizationCriteria(Equipment.class, SecuredEntities.EquipmentOperations.read));
```
 ```JSON
create Task TkGetLastPurchasedEquipmentsByBaseId {  
    className : "io.vertigo.basics.task.TaskEngineSelect"
    request : "
            select 
            	equ.*
			from (<%=securedEquipment.asSqlFrom(\"equipment\", ctx)%>) equ
			where equ.base_id = #baseId#
			order by equ.purchase_date desc
			limit 50
             "
    in 	baseId           {domain : DoId         	cardinality: "1"}
    in  securedEquipment {domain : DoAuthorizationCriteria    cardinality: "1"}
    out equipments       {domain : DoDtEquipment	cardinality: "*"}
}
```

 
Pour l'appliquer à une recherche
```Java
 final ListFilter securityListFilter = ListFilter.of(authorizationManager.getSearchSecurity(Equipment.class, SecuredEntities.EquipmentOperations.read));
	final SearchQuery searchQuery = equipmentIndexSearchClient.createSearchQueryBuilderEquipment(criteria, selectedFacetValues)
				.withSecurityFilter(securityListFilter)
				.build();
 ```
 
#### AuthorizationUtil

Cet utilitaire propose des méthodes static facilement utilisable pour vérifer les authorisations de l'utilisateur dans les services métiers.
Il est préférable de faire les controles le plus tôt possible dans le traitement pour des questions de performances. 
Mais si l'utilisateur n'a pas les authorisations suffisantes, une exception est lancée ce qui rollbackera la transaction et affichera une erreur à l'utilisateur.

- **assertAuthorizations(message*(optionel)*, AuthorizationName...)** : Vérifie que l'utilisateur a l'une des autorisations passées en paramètre et lance une exception sinon
- **assertOperations(Entity, OperationName, message*(optionel)*)** : Vérifie que l'utilisateur peut réaliser l'opération sur l'**entity** avec son contexte de sécurité actif
- **assertOperationsOnOriginalEntity(Entity, OperationName, message*(optionel)*)** : Comme **assertOperations** mais reload d'abord l'objet original pour faire le controle de sécurité AVANT d'appliquer les modifications de l'utilisateur
 - **assertOr(BooleanSupplier...)** : Permet d'assembler plusieurs controle en OR
 - **hasAuthorization(BooleanSupplier...)** : Vérifie que l'utilisateur a l'une des autorisations passées en paramètre
 - **authorizationCriteria(<Class<Entity>, OperationName)** : Construit un criteria représentant le filtre de sécurité pour un type d'opération sur une entity
 - **assertOperationsWithLoadIfNeeded(StoreVAccessor, OperationName, message*(optionel)*)** : Vérifie que l'utilisateur peut réaliser l'opération sur l'**entity** porté par cette accessor (FK), l'accessor sera loadé si besoin 
 
 Exemple:
```Java
  //check d'opération sur une entity
 AuthorizationUtil.assertOperations(baseDAO.get(baseId), SecuredEntities.BaseOperations.read);
 
 //util pour les FK
 AuthorizationUtil.assertOperationsWithLoadIfNeeded(ticket.equipment(), SecuredEntities.EquipmentOperations.readTickets);
```
	
#### UiAuthorizationUtil

Pour le rendu des pages, un utilitaire permet de valider que l'utilisateur possède des authorizations globales, ou les authoriations pour une opération sur une entité.
Cela permet de désactiver l'affichage de bouton ou lien dans l'UI.
Habituellement les controles sont fait en thymeleaf avec un `th:if`
Exemple:
```HTML
 th:if="${authz.hasAuthorization('AdmUser','ViewAcademy')}"
 ```

Api:
- **hasAuthorization(AuthorizationName...)** : Vérifie que l'utilisateur a l'une des autorisations passées en paramètre
- **hasOperation(UiObject, OperationName)** : Vérifie que l'utilisateur peut réaliser l'opération sur l'**entity** avec son contexte de sécurité actif
 
!> La désactivation d'un bouton n'est pas suffisante pour assurer un niveau de sécurité minimum. Le controle des authorizations doit surtout être réalisé coté serveur

#### Aspect

!> Bien que pratique, le controle de sécurité par aspect n'est pas préconisé, à cause du caractère non-systématique de cette technique (non-réentrance). A réserver aux développeurs avertis.

**Vertigo Authorization** propose deux annotations permettant l'implémentation des controles de sécurité par AOP.

- **@Secured({`liste de nom d'authorization`})** : Permet de sécuriser une *méthode* seule ou toute une *class* en vérifiant que l'utilisateur a l'une des autorisations
- **@SecuredOperation(`nom d'authorization`)** : Permet de sécuriser une `SecuredEntity` passée en paramètre en vérifiant que l'utilisateur est autorisé à réaliser cette opération sur l'entité

> Dans ces annotations, il n'est pas nécessaire d'utiliser le préfix `Atz` pour le nom des authorisations
 
> `@SecuredOperation` nécessite que la méthode soit annotée par `@Secured`

!> Attention : les annotations sont vérifiées par AOP, ce mode de contrôle est donc **non-réentrant**

!> Re-attention : Le `@SecuredOperation` nécessite l'entité, ce qui signifie qu'elle doit déjà être chargée (du coup avant le check de sécurité)


 
### Chargement

Les autorisations sont chargées via un DefinitionProvider dans la Feature du module applicatif.<br/>

*Exemple :*
```java 
  .addDefinitionProvider(DefinitionProviderConfig.builder(JsonSecurityDefinitionProvider.class)
    .addDefinitionResource("security", "mars-auth-config.json")
    .build())
```


### Exemple pour les règles de sécurité : ENUM et TREE

**ENUM** : Exemple de cas d’usage pour un dossier.<br/>
Etats possibles : 
- (ENC) En cours de saisie
- (SOU) Soumis
- (ACC) Accepté
- (REF) Refusé
- (ARC) Archivé

![](./images/security-enum.png)


**TREE** : Exemple de cas d’usage pour un dossier.<br/>
Arbre géographique : 
- (NAT) National
- (DEP) Département
- (COM) Commune

![](./images/security-tree.png)


## Identity Providers

### Principe

Vertigo propose un manager de haut niveau pour simplifier la synchronisation des comptes utilisateurs de l'application avec un source d'identité externe (**IdP** ou **Id**entity **P**rovider).
Typiquement, l'API proposée permet de récupérer les utilisateurs au format de l'Entity gérée localement.
 - soit utilisateur par utilisateur à partir de son TokenAuthentification (récupéré par le `AuthenticationManager`)
 - soit la photo seule d'un utilisateur
 - soit par la liste des utilisateurs

### Configuration

Vertigo propose de base trois types de sources d'identité :

**Configuration de la *Feature* IdentityProvider (Yaml)**

- **identityProvider.store** : Provision des *Identités* depuis le *StoreManager*
  - userIdentityEntity : Nom de l'entité portant les *Identités*
  - userAuthField : Nom du champ relié à l'authentification *(authToken)*
  - photoIdField *(optional)* : Id du FileInfo de stockage de la photo
  - photoFileInfo *(optional)* : Nom du *FileInfo* utilisé pour le stockage des photos
- **identityProvider.ldap** : Provision des *Identités* depuis un LDAP
  - ldapServerHost : Nom du serveur LDAP
  - ldapServerPort : Port du serveur LDAP (par défaut : 389)
  - ldapAccountBaseDn : Base de recherche des DNs d'Accounts
  - ldapReaderLogin : Login du reader LDAP
  - ldapReaderPassword : Password du reader LDAP
  - ldapUserAuthAttribute : Attribut LDAP utilisé pour retrouver un user par son *authToken*
  - userIdentityEntity : Nom de l'entité portant l'identité (ie: du User au sens application)
  - ldapUserAttributeMapping : Mapping des champs du LDAP vers l'entité d'identité
- **identityProvider.text** : Provision des *Identités* depuis un fichier texte
  - identityFilePath : Chemin du fichier des *Identités* 
  - identityFilePattern : RegExp de lecture du fichier (avec des capturesGroup [nommés](https://stackoverflow.com/a/415635/2273508))
  - userAuthField : Nom du champ relié à l'authentification *(authToken)*
  - userIdentityEntity : Nom de l'entité portant l'identité (ie: du User au sens application)










