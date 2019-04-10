# Sécurité

Le module **Account** de Vertigo permet la gestion simplifiée des comptes utilisateurs. 
Ce module permet avant tout la mise à disposition aux autres modules de la notion transverse de compte utilisateur. Ceci permet à Vertigo de proposer des extensions comme *"notifications"* ou *"commentaires"*. 

Ce module propose des fonctionnalités de gestion des utilisateurs réparties sur trois axes orthogonaux :
- authentication
- authorization
- identity provider
 

## Configuration

Afin d'utiliser les fonctionnalités de **Account** il convient d'ajouter ce module à la configuration de l'application.
Pour plus de détail vous pouvez vous rapporter au chapitre dédié à la [configuration](/basic/configuration) de l'application.


Voici une configuration Yaml typique d'une application utilisant le module Account

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
- security : Active le module, et le premier niveau de sécurité (authentifié ou non)
  - userSessionClassName : Nom de la class de la session applicative 
- account : Active les fonctionnalités autour de la notion de compte utilisateur
- authentication : Active les fonctionnalités d'authentification
- identityProvider : Active les fonctionnalités de fournisseur d'identité
- authorization : Active les fonctionnalités liés aux autorisations

### Configurations standards 
- account.store.store : Stockage des *Account* par le *StoreManager*
  - userIdentityEntity : Nom de l'entité portant les *Account*
  - groupIdentityEntity : Nom de l'entité portant les groupes d'*Account* (doit avoir une FK vers *Account*)
  - userAuthField : Nom du champ relié à l'authentication *(authToken)*
  - photoFileInfo *(optional)* : Nom du *FileInfo* utilisé pour le stockage des photos
  - userToAccountMapping : Mapping des champs de l'entité vers *Account*
  - groupToGroupAccountMapping : Mapping des champs de l'entité Groupe vers *GroupeAccount*
- account.store.text : Stockage des *Account* par un fichier text
  - accountFilePath : Chemin du fichier des *Account* 
  - accountFilePattern : RegExp de lecture du fichier (avec des capturesGroup [nommés](https://stackoverflow.com/a/415635/2273508) : id, displayName, email, authToken, photoUrl)
  - groupFilePath : Chemin du fichier des *AccountGroup* 
  - groupFilePattern :  RegExp de lecture du fichier (avec des capturesGroup [nommés](https://stackoverflow.com/a/415635/2273508) : id, displayName, accountIds)
- account.store.loader : Stockage des *Account* délégué à un loader spécifique *(implements [AccountLoader](https://github.com/vertigo-io/vertigo/blob/master/vertigo-account-impl/src/main/java/io/vertigo/account/plugins/account/store/loader/AccountLoader.java))*
- account.cache.memory : Active le cache mémoire (**Attention** pas de purge automatique)
- account.cache.redis : Active le cache Redis via le *RedisConnector*(**Attention** pas de purge automatique)

- authentication.text : Permet l'authentification basée sur un fichier text
  - filePath : Chemin du fichier. (Format du fichier : accountKey    login    password    //comments )
- authentication.store : Permet l'authentification basée sur le *StoreManager*
  - userCredentialEntity : Nom de l'entité portant l'authentification
  - userLoginField : Nom du champ 
  - userPasswordField : Nom du champ password
  - userTokenIdField : Nom du champ *authToken* (champ utilisé pour le lien vers *Account*)
- authentication.ldap : Permet l'authentification déporté sur un LDAP
  - userLoginTemplate : Template du DN de l'utilisateur (contient {0} pour fusionner le login)
  - ldapServerHost : Nom du serveur LDAP
  - ldapServerPort : Port du serveur LDAP
- authentication.mock : Pour les tests, authentification toujours vrai

?> Le hash des mots de passe pour les modules le nécessitant utitlise l'algorithme [PBKDF2WithHmacSHA256](https://en.wikipedia.org/wiki/PBKDF2)

- identityProvider.store : Provision des *Identités* depuis le *StoreManager*
  - userIdentityEntity : Nom de l'entité portant les *Identités*
  - userAuthField : Nom du champ relié à l'authentication *(authToken)*
  - photoIdField *(optional)* : Id du FileInfo
  - photoFileInfo *(optional)* : Nom du *FileInfo* utilisé pour le stockage des photos
- identityProvider.ldap : Provision des *Identités* depuis un LDAP
  - ldapServerHost : Nom du serveur LDAP
  - ldapServerPort : Port du serveur LDAP (par defaut : 389)
  - ldapAccountBaseDn : Base de recherche des DNs d'Accounts
  - ldapReaderLogin : Login du reader LDAP
  - ldapReaderPassword : Password du reader LDAP
  - ldapUserAuthAttribute : Attribut LDAP utilisé pour retrouver un user par son *authToken*
  - userIdentityEntity : Nom de l'entité portant l'identité (ie: du User au sens application)
  - ldapUserAttributeMapping : Mapping des champs du LDAP vers l'entité d'identité
- identityProvider.text : Provision des *Identités* depuis un fichier text
  - identityFilePath : Chemin du fichier des *Identité* 
  - identityFilePattern : RegExp de lecture du fichier (avec des capturesGroup [nommés](https://stackoverflow.com/a/415635/2273508))
  - userAuthField : Nom du champ relié à l'authentication *(authToken)*
  - userIdentityEntity : Nom de l'entité portant l'identité (ie: du User au sens application)

  
## Autorisations

Les autorisations sont chargées via un DefinitionProvider dans la Feature du module applicatif.
```Java 
  .addDefinitionProvider(DefinitionProviderConfig.builder(JsonSecurityDefinitionProvider.class)
    .addDefinitionResource("security", "mars-auth-config.json")
    .build())
```

