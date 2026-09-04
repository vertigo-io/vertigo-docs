# Security

Application security management is provided by Vertigo through the **Account** module.

This module offers related user management features:
- **Authentication**: Authentication management
- **Authorization**: Authorization management
- **Identity Provider**: Connection with identity providers


## Configuration

To use the **Account** features, this module must be added to the application configuration.
For more details, refer to the chapter dedicated to application [configuration](/en/basic/configuration).

Here is a typical configuration for an application using the Account module:

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

The security configuration is then added to the application module's manifest. <br/>
Example:

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

## Principles

In a business application, it is generally assumed that not all users will have access to everything. Vertigo provides a security mechanism that protects the elements of the application that need it.

From a technical standpoint, the mechanism allows securing fine-grained elements of the application (called *Resources*): pages, services, data, or anything else.
It can also be something more abstract, such as a **confidential** attribute that spans the entire application.<br/>
But to remain understandable, the developer configures the security mechanism to group these *Resources* into *Authorizations* that correspond to features offered by the application
(*Consult the dossiers*, *Submit a dossier*, *Validate the dossiers*, ...)

The Vertigo security mechanism is quite *low-level*. Vertigo provides the notion of **Authorization** (global — named `Atz` + authorization code, e.g. `AtzSecuredUser` — or carried by an entity via `SecuredEntity`) and the notion of **Role**: a named group of authorizations (prefix `R`), added to the user via `addRole` (the role and all its authorizations are attached in cascade). The *Role* is a building block provided by the platform, a compatibility inheritance from the ASC module: it cannot be declared in the security JSON configuration, which only contains `globalAuthorizations` and `securedEntities`. For details on the model: [the Account module documentation](/en/extensions/account).

It is up to the application to rationalize the model; for example, it is recommended that the application manage security at a more macro level, with the notions of *Profile* and *Scope*.
The list of *Profiles* associated with a user is specific to the application and remains its responsibility.
A *Profile* is a list of **Authorizations** attached to an applicative **Scope**.

**Note**<br/>
Best practice in this area is that if a user has multiple **Profiles**, only one should be active at a time (the user can switch during their session). This avoids collisions (intersections) of security rules that are hard to understand, hard to implement efficiently and hard to test.<br/>
In a system where user management is centralized, the user **Profile** can be managed by the centralized system (it provides the **Profile** per user per application)

### Notion of *security context*

The model presented above already handles many cases. But the larger the enterprises, the stronger their organization, and the more it weighs on the application's security.
Security must then be relative to a context. This context can be geographic, organizational, tied to a state, a date, or something else, or even all of these at the same time.<br/>
This *security context* is also called the security **Scope**.

The Vertigo mechanism makes it possible to ensure and to set up this type of security generically in projects.
In Vertigo terms, the *security context* is a notion:

- in which users and `SecuredEntities` are enrolled
- that is composed of axes (geographic, organizational, ...)
- each of whose axes can be hierarchical (e.g.: continent, country, regions, municipalities, cities)

To remain compatible with the mechanism provided by Vertigo, the application must respect a few rules:

- A user has one and only one active context at a time
- The user's context is cross-cutting with respect to their rights
- The context hierarchy has no exceptions and is correctly oriented (a parent accesses all its children, grandchildren, ...)

!> Exceptions must be handled specifically by the application.


### Authorization Types

Two types of authorizations are offered:
- **Global Authorizations**: Global authorizations used to protect application functions (screens, buttons, processes, ...)

- **Secured Entity Operations**: Authorizations for an operation on a secured entity
  - securityDimensions: List of security dimensions (pseudo-security fields derived from other fields of the entity)
    - type: Dimension type (SIMPLE: simple field, no ordered value and no hierarchy; ENUM: for an ordered enumeration; TREE: for a hierarchical structure)
      - For details on the dimension types: [the Account module documentation](/en/extensions/account)
    - values *(Type:ENUM)*: Ordered list of possible values
    - fields *(Type:TREE)*: List of ordered (and flat) fields of the tree
  - operations: List of possible operations on the entity
    - name: Operation code
    - rules: List of security rules.
      - SQL-like syntax (myField *operator* value (and|or)?)
        - Comparison operators: `=`, `!=`, `<`, `>`, `<=`, `>=`
        - Boolean operators: `AND` / `and` / `&&` and `OR` / `or` / `||`
        - Grouping by parentheses `( ... )`, maximum nesting depth: 3
        - `true` keyword: rule always true (see the `read` rule in the example below)
        - For details on the DSL classes: [the Account module documentation](/en/extensions/account) (section *For Experts* > *Security Rules DSL*)
      - The different rules in the list are considered in **OR**
      - **${myParam}** to place a property of the user context (scope property in the user's session)
      - Simple notation for **TREE** axes: GEO <= ${geo}: Selects the `SecuredEntities` *lower than or equal to* in the user's geographic scope (e.g.: all municipalities or within the department of a department manager)
      - Simple notation for **ENUM** axes: etaCd>=PUB AND etaCd<ARC (e.g.: all `SecuredEntities` whose state is *higher than or equal to* `PUB` (published) and *strictly lower than* `ARC` (archived))

> Each **Secured Entity Operation** is associated with a generated *authorization*. It is thus possible to check if a user has, *a priori*, the right to perform an operation on an entity, even before looking at the user's security context.
> This is used, in particular, to manage the displayed UI elements.<br/>
> **Example:** Retrieving the possible operations on an entity in order to determine the menus to offer.


## Example

Here is a typical security configuration file:

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

## Going Further

To delegate a user's authentication to an external identity server (Keycloak, for example), you should use the **OIDC** or **SAML** authentication plugins of Vega: features `authentication.oidc` / `authentication.saml2` (as well as `authentication.aad` for Azure AD).
These plugins are documented in the [Authentication Plugins](/en/basic/webservices#authentication-plugins) section of the web services chapter.
