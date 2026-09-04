# Sécurité

Une gestion de la sécurité applicative est proposée par Vertigo à travers le module **Account**.

Ce module propose des fonctionnalités connexes de gestion des utilisateurs :
- **Authentication** : Gestion de l'authentification
- **Authorization** : Gestion des autorisations
- **Identity Provider** : Connexion avec des fournisseurs d'identité


## Configuration

Afin d'utiliser les fonctionnalités d'**Account**, il convient d'ajouter ce module à la configuration de l'application.
Pour plus de détails vous pouvez vous rapporter au chapitre dédié à la [configuration](/basic/configuration) de l'application.

Voici une configuration typique d'une application utilisant le module Account :

```yaml
modules:
  io.vertigo.account.AccountFeatures:
    features:
      - security:
          userSessionClassName: io.gestionprojet.commons.GestionProjetUserSession
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

```java
public class GestionProjetFeatures extends DefaultUiModuleFeatures<GestionProjetFeatures> {

  public GestionProjetFeatures() {
    super("gestionprojet");
  }

  @Override
  protected void buildFeatures() {
    super.buildFeatures();
    getModuleConfigBuilder()
        [...]
        .addDefinitionProvider(DefinitionProviderConfig.builder(JsonSecurityDefinitionProvider.class)
                .addDefinitionResource("security", "io/gestionprojet/gestionprojet-authorizations.json")
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

Dans une application métier, on considère en général que tous les utilisateurs n'auront pas accès à tout. Vertigo propose un mécanisme de sécurité qui permet de protéger les éléments de l'application qui doivent l'être.

D'un point de vue technique, le mécanisme permet de sécuriser des éléments fins de l'application (que l'on nomme *Ressource*) : des pages, des services, des données ou autres.
Il peut aussi s'agir de quelque chose de plus abstrait comme un caractère **confidentiel** transverse à l'application.<br/>
Mais pour rester compréhensible, le développeur va paramétrer le mécanisme de sécurité pour englober ces *Ressources* dans des *Authorizations* qui correspondent à des fonctionnalités proposées par l'application
(*Consulter les dossiers*, *Déposer un dossier*, *Valider les dossiers*, ...)

Le mécanisme de sécurité de Vertigo est assez *bas-niveau*. Vertigo fournit la notion d'**Authorization** (globale — nommée `Atz` + code de l'autorisation, ex. `AtzSecuredUser` — ou portée par une entité via les `SecuredEntity`) et la notion de **Role** : un groupe nommé d'autorizations (préfixe `R`), ajouté à l'utilisateur via `addRole` (le rôle et toutes ses authorizations sont rattachés en cascade). Le *Role* est une brique fournie par la plateforme, héritage de compatibilité du module ASC : il n'est pas déclarable dans la configuration JSON de sécurité, qui ne contient que `globalAuthorizations` et `securedEntities`. Pour le détail du modèle : [la documentation du module Account](/extensions/account).

Il est laissé à l'application la charge de rationaliser le modèle, par exemple il est préconisé que l'application gère la sécurité à un niveau plus macro avec une notion de *Profil* et de *Périmètre*.
La liste des *Profils* associés à un utilisateur est spécifique à l'application et reste à sa charge.
Un *Profil* étant une liste d'**Authorizations** rattachée à un **Périmètre** applicatif.

**Note**<br/>
La bonne pratique dans ce domaine est que si l'utilisateur a plusieurs **Profils**, il devra n'en avoir qu'un seul actif à la fois (il pourra en changer pendant sa session), ceci afin d'éviter des collisions (intersections) de règles de sécurité difficiles à comprendre, à implémenter de manière performante et à tester.<br/>
Dans un système où la gestion des utilisateurs est centralisée, le **Profil** utilisateur peut être géré par le système centralisé (il fournit le **Profil** par utilisateur par appli)

### Notion de *contexte de sécurité*

Le modèle présenté ci-dessus permet déjà de gérer de nombreux cas. Mais plus les entreprises sont de taille importante, plus elles ont une organisation forte qui pèse sur la sécurité de l'application.
Il apparaît alors que la sécurité doit être relative à un contexte. Ce contexte peut être géographique, organisationnel, lié à un état, à une date ou autre, voire tout cela en même temps. <br/>
Ce *contexte de sécurité* est aussi appelé **Périmètre** de sécurité.

Le mécanisme de Vertigo permet d’assurer et de mettre en place ce type de sécurité de manière générique dans les projets.
Au sens Vertigo, le *contexte de sécurité* est une notion :

- dans laquelle s'inscrivent les utilisateurs et les `SecuredEntities`
- qui est composée d'axes (géographique, organisationnel, ...)
- dont chaque axe peut être hiérarchique (ex: continent, pays, régions, communes, villes)

Pour rester compatible avec le mécanisme prévu par Vertigo, l'application doit respecter quelques règles :

- L'utilisateur n'a qu'un et un seul contexte actif à la fois
- Le contexte de l'utilisateur est transverse à ses droits
- La hiérarchie du contexte est sans exception et correctement orientée (un parent accède à tous ses enfants, petits-enfants...)

!> Les exceptions devront être gérées spécifiquement par l'application.


### Types d'autorisation

Deux types d'autorisations sont proposés :
- **Global Authorizations** : Autorisations globales utilisées pour protéger des fonctions de l'application (écrans, boutons, traitements, ...)

- **Secured Entity Operations** : Autorisations pour une opération sur une entité sécurisée
  - securityDimensions : Liste de dimensions de sécurité (pseudo-champs de sécurité déduits d'autres champs de l'entité)
    - type : Type de la dimension (SIMPLE : champ simple, sans valeur ordonnée ni hiérarchie ; ENUM : pour une énumération ordonnée ; TREE : pour une structure hiérarchique)
      - Pour le détail des types de dimensions : [la documentation du module Account](/extensions/account)
    - values *(Type:ENUM)* : Liste ordonnée des valeurs possibles
    - fields *(Type:TREE)* : Liste des champs ordonnés (et à plat) de l'arborescence
  - operations : Liste des opérations possibles sur l'entité
    - name : Code de l'opération
    - rules : Liste de règles de sécurité.
      - Syntaxe proche du SQL ( myField *opérateur* value (and|or)? )*
        - Opérateurs de comparaison : `=`, `!=`, `<`, `>`, `<=`, `>=`
        - Opérateurs booléens : `AND` / `and` / `&&` et `OR` / `or` / `||`
        - Groupement par parenthèses `( ... )`, profondeur de nesting maximale : 3
        - Mot-clé `true` : règle toujours vraie (cf. règle `read` de l'exemple ci-dessous)
        - Pour le détail des classes du DSL : [la documentation du module Account](/extensions/account) (section *Pour les experts* > *DSL de règles*)
      - Les différentes règles de la liste sont considérées en **OU**
      - **${myParam}** pour placer une propriété du contexte utilisateur (propriété de périmètre dans la session de l'utilisateur)
      - Écriture simple pour les axes **TREE** : GEO <= ${geo} : On sélectionne les `SecuredEntities` *inférieurs ou égaux* dans le périmètre géographique de l'utilisateur (Ex: toutes les communes ou dans le département d'un responsable départemental)
      - Écriture simple pour les axes **ENUM** : etaCd>=PUB AND etaCd<ARC (Ex : tous les `SecuredEntities` dont l'état est *supérieur ou égal* à `PUB` (publié) et *strictement inférieur* à `ARC` (archivé))

> Chaque **Secured Entity Operation** est associée à une *authorization* générée. Il est ainsi possible de vérifier si un utilisateur a "à priori" le droit d'effectuer une opération sur une entité avant même de regarder le contexte de sécurité de l'utilisateur.
> Ceci est utilisé, notamment pour gérer les éléments d'IHM affichés.<br/>
> **Exemple :** Récupération des opérations possibles sur une entité pour déterminer les menus à proposer.


## Exemple

Voici un fichier type de configuration de la sécurité

```json
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
      "__comment": "Test de lecture : Tout le monde a le droit de lire",
      "name": "read", "label" : "Lecture",
      "rules": [ "true" ]
    }, {
      "__comment": "Test d'écriture : Droit limité, l'utilisateur est autorisé à modifier les contacts d'un même titre honorifique et un contact particulier par son nom",
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

## Pour aller plus loin

Pour déléguer l'authentification d'un utilisateur à un serveur d'identité externe (Keycloak, par exemple), il convient d'utiliser les plugins d'authentification **OIDC** ou **SAML** de Vega : features `authentication.oidc` / `authentication.saml2` (ainsi que `authentication.aad` pour Azure AD).
Ces plugins sont documentés dans la section [Authentication Plugins](/basic/webservices#authentication-plugins) du chapitre web services.
