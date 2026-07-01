# Security

Application security management is provided by Vertigo through the **Account** module.

This module offers related user management features:
- **Authentication**: Authentication management
- **Authorization**: Authorization management
- **Identity Provider**: Connection with identity providers


## Configuration

To use **Account** features, you must add this module to the application configuration.
For more details, refer to the chapter dedicated to application [configuration](/en/basic/configuration).

Here is a typical configuration for an application using the Account module:

```yaml
modules:
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

The security configuration is then added to the application module's manifest. <br/>
Example:

```java
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

## Principles

In a business application, it is generally assumed that not all users will have access to everything. Vertigo provides a security mechanism to protect application elements that require it.

From a technical perspective, the mechanism secures fine-grained application elements (called *Resources*): pages, services, data, or other items.
It can also be something more abstract, such as a **confidential** characteristic that spans the application.<br/>
But to remain understandable, the developer configures the security mechanism to group these *Resources* into *Authorizations* corresponding to features offered by the application
(*Consult files*, *Submit files*, *Validate files*, ...)

The Vertigo security mechanism is quite *low-level*. Vertigo only knows the notion of **Authorization**: either global, or carried by an entity (the `SecuredEntity`s).

It is up to the application to rationalize the model. For example, it is recommended that the application manage security at a more macro level with *Profile* and *Scope* notions.
The list of *Profiles* associated with a user is application-specific and remains the application's responsibility.
A *Profile* is a list of **Authorizations** attached to an applicative **Scope**.

**Note**<br/>
Best practice in this area is that if a user has multiple **Profiles**, only one should be active at a time (the user can switch profiles during their session). This avoids security rule collisions (intersections) that are hard to understand, implement performantly, and test.<br/>
In a system where user management is centralized, the user **Profile** can be managed by the centralized system (it provides the **Profile** per user per application).

### Notion of *security context*

The model presented above already handles many cases. But the larger the organization, the more its structure affects application security.
Security must then be relative to a context. This context can be geographic, organizational, state-related, date-related, or all of these simultaneously.<br/>
This *security context* is also called the **Scope**.

The Vertigo mechanism ensures and implements this type of security generically in projects.
In Vertigo terms, the *security context* is a notion:

- in which users and `SecuredEntity`s are registered
- composed of axes (geographic, organizational, ...)
- each of which can be hierarchical (e.g.: continent, country, regions, districts, cities)

To remain compatible with Vertigo's planned mechanism, the application must follow some rules:

- The user has only one active context at a time
- The user's context is transversal across their rights
- The context hierarchy has no exceptions and is properly oriented (a parent accesses all its children, grandchildren...)

!>Exceptions must be handled specifically by the application.


### Authorization Types

Two types of authorizations are offered:
- **Global Authorizations**: Global authorizations used to protect application functions (screens, buttons, processes, ...)

- **Secured Entity Operations**: Authorizations for an operation on a secured entity
  - securityDimensions: List of security dimensions (pseudo-security fields derived from other entity fields)
    - type: Dimension type (ENUM: for an ordered enumeration, TREE: for a hierarchical structure)
    - values *(Type:ENUM)*: Ordered list of possible values
    - fields *(Type:TREE)*: Ordered list of fields (flattened) from the tree
  - operations: List of possible operations on the entity
    - name: Operation code
    - rules: List of security rules.
      - SQL-like syntax (myField *operator* value (and|or)?)
      - The different rules in the list are considered in **OR**
      - **${myParam}** to place a user context property (scope property in the user's session)
      - Simple notation for **TREE** axes: GEO <= ${geo}: Selects `SecuredEntity`s *less than or equal* in the user's geographic scope (e.g., all communes or within the department of a department manager)
      - Simple notation for **ENUM** axes: etaCd>=PUB AND etaCd<ARC (e.g.: all `SecuredEntity`s whose state is *greater than or equal* to 'PUB'*lished* and *strictly less* than 'ARC'*hived*)

> Each **Secured Entity Operation** is associated with a generated *authorization*. It is thus possible to check if a user has the right to perform an operation on an entity *a priori*, even before checking the user's security context.
> This is used notably to manage displayed UI elements.<br/>
> **Example:** Retrieving possible operations on an entity to determine menus to offer.


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
      "__comment": "Read test: Everyone has read rights",
      "name": "read", "label" : "Read",
      "rules": [ "true" ]
    }, {
      "__comment": "Write test: Limited rights, the user is authorized to modify contacts with the same honorific title and a particular contact by name",
      "name": "write", "label" : "Write",
      "grants": ["read"],
      "rules": [
        "honorificCode=${honorificCode} OR name=${name}"
      ]
    }, {
      "__comment": "Delete test: Limited rights, the user is authorized to delete a particular contact by name",
      "name": "delete", "label" : "Delete",
      "grants": ["read", "write"],
      "rules": [
        "name=${name}"
      ]
    }]
  }]
}
```

## For Experts

Vertigo provides a very simple mechanism with vertigo-keycloak-connector and Vertigo-Vega to delegate user authentication to a KeyCloak server.
