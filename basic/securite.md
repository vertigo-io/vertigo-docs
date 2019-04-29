# Sécurité

Une gestion de la sécurité applictive est proposée par Vertigo à travers le **Account**. 

Ce module propose des fonctionnalités connexes de gestion des utilisateurs :
- **Authentication** : Gestion de l'authentification
- **Authorization** : Gestion des autorisations
- **Identity Provider** : Connexion avec des fournisseurs d'identité
 

## Configuration

Afin d'utiliser les fonctionnalités de **Account** il convient d'ajouter ce module à la configuration de l'application.
Pour plus de détail vous pouvez vous rapporter au chapitre dédié à la [configuration](/basic/configuration) de l'application.

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

La configuration de la sécurité est ensuite ajoutée au manifest du module applicatif. <br/>
Exemple : 

```Java
public class MaintenanceFeatures extends ModuleDiscoveryFeatures {

  public MaintenanceFeatures() {
    super("Maintenance");
  }

  @Override
  protected void buildFeatures() {
    super.buildFeatures();
    getModuleConfigBuilder()
        [...]
        .addDefinitionProvider(DefinitionProviderConfig.builder(JsonSecurityDefinitionProvider.class)
                .addDefinitionResource("security", "io/mars/maintenance/maintenance-authorizations.json")
                .build())
        [...]
  }

  @Override
  protected String getPackageRoot() {
    return this.getClass().getPackage().getName();
  }
}
```

## Principes

Dans une application métier on considère en générale que tous les utilisateurs n'auront pas accès à tout. Vertigo propose un mécanisme de sécurité qui permet de protéger les éléments de l'application qui doivent l'être.

D'un point de vue technique le mécanisme permet de sécuriser des éléments fins de l'application (que l'on nomme *Ressource*) : des pages, des services, des données ou autres. 
Il peut aussi s'agir de quelque chose de plus abstrait comme un caractère **confidentiel** transverse à l'application.<br/>
Mais pour rester compréhensible le développeur va paramétrer le mécanisme de sécurité pour englober ces *Ressources* dans des *Authorization* qui correspondent à des fonctionnalités proposées par l'application 
(*Consulter les dossiers*, *Déposer un dossier*, *Valider les dossiers*, ...)

Le mécanisme de sécurité de Vertigo est assez *bas niveau*. Vertigo ne connait que la notion d' **Authorization** : soit globales, soit portées par une entité (les `SecuredEntity`).

Il est laissé à l'application la charge de rationaliser le modèle, par exemple il est préconisé que l'application gère la sécurité à un niveau plus macro avec une notion de *Profil* et de *Périmètre*.
La liste des *Profils* associés à un utilisateur est spécifique à l'application et à sa charge. 
Un *Profil* étant une liste d'**Authorizations** rattaché à un **Périmètre** applicatif.

**Note**<br/>
La bonne pratique dans ce domaine est que si l'utilisateur a plusieurs **Profils**, il devra n'en avoir qu'un seul actif à la fois (il pourra en changer pendant sa session), 
ceci afin d'éviter des collisions (intersections) de règles de sécurité difficiles à comprendre, à implémenter de manières performantes et à tester.<br/>
Dans un système où la gestion des utilisateurs est centralisée, le **Profil** utilisateur peut être géré par le système centralisé (il fournit le **Profil** par utilisateur par appli) 

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

Deux types d'autorisations sont proposées :
- **Global Authorizations** : Autorisations globales utilisées pour protéger des fonctions de l'application (écrans, bouttons, traitements, ...)

- **Secured Entity Operations** : Autorisations pour une opération sur une entité sécurisée
  - securityDimensions : Listes de dimensions de sécurité (pseudo champs de sécurité déduit d'autres champs de l'entité)
    - type : Type de la dimension (ENUM : pour une énumération ordonnée, TREE : pour une structure hiérarchique)
    - values *(Type:ENUM)* : Liste ordonnées des valeurs possibles
    - fields *(Type:TREE)* : Liste des champs ordonnés (et à plat) de l'arborescence
  - operations : Liste des opérations possibles sur l'entité
    - name : Code de l'opération
    - rules : Liste de règle de sécurité. 
      - Syntaxe proche du SQL ( myField *operateur* value (and|or)? )*
      - Les différentes règles de la liste sont considérées en **OU**
      - **${myParam}** pour placer une propriété du context utilisateur (propriété de périmètre dans la session du user)
      - Ecriture simple pour les axes **TREE** : GEO <= ${geo} : On sélectionne les `SecuredEntities` *inférieur ou égale* dans le périmètre géographique de l'utilisateur (Ex: toutes les communes ou dans le département d'un responsable départementale)
      - Ecriture simple pour les axes **ENUM** : etaCd>=PUB AND etaCd<ARC (Ex : tous les `SecuredEntities` dont l'état est *supérieur ou égale* à 'PUB'*lié* et *strictement inférieur* à 'ARC'*hivé*)

> Chaque **Secured Entity Operations** est associée à une authorization générée. Il ainsi possible de vérifier si un utilisateur a "à priori" le droit d'éffectuer une opération sur une entité avant même de regarder le contexte de sécurité de l'utilisateur.
> Ceci est utilisé, notament pour gérer les éléments d'IHM affiché.<br/>
> **Exemple:** Récupération des opérations possibles sur une entité pour déterminer les menus à proposer


## Exemple 

Voici un fichier type de configuration de la sécurité 

```Json
{
  "globalAuthorizations": [{
    "name": "SecuredUser",
    "label": "security.authorization.user.secured"
  }, {
    "name": "UnsecuredUser",
    "label": "security.authorization.user.unsecured"
  }],
  "securedEntities": [{
    "entity": "Contact",
    "securityFields" : ["honorificCode", "name"],
    "securityDimensions": [],
    "operations": [  {
      "__comment": "Test de lecture : Tout le monde à le droit de lire",
      "name": "read", "label" : "Lecture",
      "rules": [ "true" ]
    }, {
      "__comment": "Test d'ecriture : Droit limité, l'utilisateur est autorisé à modifier les contacts d'un même titre honorifique et un contact particulier par son nom",
      "name": "write", "label" : "Ecriture",
      "grants": ["read"],
      "rules": [
        "honorificCode=${honorificCode} OR name=${name}"
      ]
    }, {
      "__comment": "Test de suppression : Droit limité, l'utilisateur est autorisé à supprimer un contact particulier par son nom",
      "name": "delete", "label" : "Suppression",
      "grants": ["read", "write"],
      "rules": [
        "name=${name}"
      ]
    }]
  }]
}
```

