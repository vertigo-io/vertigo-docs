# Module geo

**Geo** est un module Vertigo proposant des fonctions de géocodage et de recherche géographique.

Il permet de convertir une adresse textuelle en coordonnées géographiques et de rechercher des entités métier indexées dans une zone géographique définie.

Deux fonctionnalités :

- **Géocodage** : Conversion d'une adresse en coordonnées GPS et calcul de distance entre deux points.
- **Recherche géographique** : Recherche d'objets métier indexés dans Elasticsearch selon un bounding box géographique.

## Configuration

Les fonctionnalités s'activent via les features de `GeoFeatures`.

```yaml
io.vertigo.geo.GeoFeatures:
  features:
    - geocoding:
    - geocoding.ban:
        proxyHost: "proxy.example.com"
        proxyPort: 8080
    - geosearch:
    - geosearch.es:
        envIndexPrefix: "proj_"
        connectorName: "main"
```

### Features disponibles

Cinq features sont disponibles :

- **geocoding** : Active l'API de géocodage (`GeoCoderManager`).
- **geocoding.ban** : Plugin BAN (Base Adresse Nationale) comme backend de géocodage.
- **geocoding.google** : Plugin Google Geocode comme backend de géocodage.
- **geosearch** : Active l'API de recherche géographique (`GeoSearchManager`).
- **geosearch.es** : Plugin Elasticsearch comme backend de recherche géographique.

### Paramètres des features

#### geocoding.ban

Connecteur REST vers `api-adresse.data.gouv.fr/search/`. Parsing JSON via Gson.

- **proxyHost** *(optionnel)* : Hôte du proxy HTTP.
- **proxyPort** *(optionnel)* : Port du proxy HTTP.

#### geocoding.google

Connecteur REST vers `maps.googleapis.com/maps/api/geocode/xml`. Parsing XPath/DOM.

- **proxyHost** *(optionnel)* : Hôte du proxy HTTP.
- **proxyPort** *(optionnel)* : Port du proxy HTTP.

#### geosearch.es

Utilise Elasticsearch REST HL avec `GeoBoundingBoxQueryBuilder`. Décodage des résultats via `CodecManager` (base64 + compression). Implémentation `Activeable`.

- **envIndexPrefix** *(requis)* : Préfixe appliqué aux noms d'index Elasticsearch.
- **connectorName** *(optionnel)* : Nom du connecteur Elasticsearch (défaut : `main`).

## Géocodage

### Architecture

Architecture en trois couches :

```
GeoCoderManager (interface)
       |
GeoCoderManagerImpl (implémentation)
       |
GeoCoderPlugin (interface)
     /    \
BanGeoCoderPlugin   GoogleGeoCoderPlugin
```

`GeoCoderManagerImpl` délègue au `GeoCoderPlugin` installé.

- **BanGeoCoderPlugin** : Appel REST vers `api-adresse.data.gouv.fr/search/`, décodage JSON avec Gson.
- **GoogleGeoCoderPlugin** : Appel REST vers `maps.googleapis.com/maps/api/geocode/xml`, décodage XML avec DOM/XPath.

### API

#### GeoCoderManager

Interface manager exposée via injection de dépendances.

- `GeoLocation findLocation(String address)` : Retourne un `GeoLocation` pour l'adresse donnée. Retourne `GeoLocation.UNDEFINED` (jamais `null`) si aucune correspondance. Vérifier avec `isUndefined()`.
- `double distanceKm(GeoLocation location1, GeoLocation location2)` : Distance en kilomètres entre deux points, calculée par la formule de Haversine (rayon terrestre : 6371 km).

#### GeoLocation

Classe finale et immuable. Inclut `GeoLocation.UNDEFINED` et `isUndefined()` pour les résultats non trouvés.

- `double getLatitude()` : Latitude en degrés décimaux. Lance exception si undefined.
- `double getLongitude()` : Longitude en degrés décimaux. Lance exception si undefined.
- `String getCountryCode()` : Code pays ISO (ex : `FR`).
- `String getLevel1()` : Niveau administratif 1 (ex : région).
- `String getLevel2()` : Niveau administratif 2 (ex : département).
- `String getLocality()` : Localité / commune.

Constructeur :

```java
GeoLocation(double latitude, double longitude, String countryCode, String level1, String level2, String locality)
```
Primitifs double, les valeurs ne peuvent pas être nulles.

### Exemples

Positionner un site de projet et mesurer la distance vers un autre site.

```java
// Géocodage d'un site de projet
final GeoLocation siteA = geoCoderManager.findLocation("12 rue de la Republique, 75001 Paris");

if (!siteA.isUndefined()) {
    System.out.println("Latitude  : " + siteA.getLatitude());
    System.out.println("Longitude : " + siteA.getLongitude());
    System.out.println("Commune   : " + siteA.getLocality());
}

// Distance entre deux sites de projet
final GeoLocation siteB = geoCoderManager.findLocation("1 place du Trocadero, 75116 Paris");
if (!siteA.isUndefined() && !siteB.isUndefined()) {
    final double distance = geoCoderManager.distanceKm(siteA, siteB);
    System.out.println("Distance entre les sites : " + distance + " km");
}
```

**Vigilance** : `findLocation` retourne `GeoLocation.UNDEFINED` (jamais `null`) si l'adresse n'est pas trouvée. Vérifier avec `.isUndefined()` avant d'utiliser le résultat.

## Recherche géographique

### Architecture

```
GeoSearchManager (interface)
         |
GeoSearchManagerImpl (implémentation)
         |
GeoSearchPlugin (interface)
         |
ESGeoSearchPlugin (Activeable)
```

`GeoSearchManagerImpl` délègue au `GeoSearchPlugin` installé. La valeur par défaut de `maxRows` est 1000. La limite effective est 1000 (bug connu : le code compare contre `DEFAULT_MAX_ROWS` au lieu de `MAX_MAX_ROWS`).

**ESGeoSearchPlugin** : Plugin concret implémentant la recherche via Elasticsearch REST HL. Utilise `GeoBoundingBoxQueryBuilder` pour filtrer les documents. Les objets métier sont décodés depuis le stockage Elasticsearch via `CodecManager` (sérialisation base64 avec compression). La classe implémente `Activeable`.

### API

#### GeoSearchManager

- `<D extends DataObject> DtList<D> searchInBoundingBox(GeoLocation topLeft, GeoLocation bottomRight, String indexName, Class<D> dtIndexClass, DataFieldName<D> fieldName, Optional<Integer> maxRowsOpt)`

Paramètres :

- **topLeft** : Coin haut-gauche du rectangle (latitude maximale, longitude minimale).
- **bottomRight** : Coin bas-droit du rectangle (latitude minimale, longitude maximale).
- **indexName** : Nom de l'index Elasticsearch à interroger.
- **dtIndexClass** : Classe du DataObject indexé.
- **fieldName** : Champ du DataObject contenant les coordonnées géographiques.
- **maxRowsOpt** : Nombre maximal de résultats (défaut et maximum effectif : 1000. Bug connu : `MAX_MAX_ROWS`=5000 ignoré, la validation utilise `DEFAULT_MAX_ROWS`=1000).

Retourne un `DtList<D>` contenant les objets métier situés dans la zone géographique.

### Exemple

Rechercher les sites de projet situés dans une zone géographique donnée.

```java
// Definition du bounding box
final GeoLocation topLeft     = new GeoLocation(48.870, 2.280, null, null, null, null);
final GeoLocation bottomRight = new GeoLocation(48.840, 2.330, null, null, null, null);

// Recherche des sites de projet dans la zone
final DtList<DtSiteProjet> sites = geoSearchManager.searchInBoundingBox(
    topLeft,
    bottomRight,
    "idx-site-projet",
    DtSiteProjet.class,
    DtSiteProjetFields.siteGeo,
    Optional.of(500)
);

for (final DtSiteProjet site : sites) {
    System.out.println("Site : " + site.getNom());
}
```

**Vigilance** :

- `searchInBoundingBox` prend des objets `GeoLocation`, pas de coordonnées brutes.
- Le paramètre `maxRows` ne peut pas dépasser 1000 (bug connu : la validation utilise `DEFAULT_MAX_ROWS`=1000 au lieu de `MAX_MAX_ROWS`=5000).
- `topLeft` correspond à la latitude maximale / longitude minimale (coin nord-ouest).
- `bottomRight` correspond à la latitude minimale / longitude maximale (coin sud-est).

### Dépendances Elasticsearch

La feature `geosearch.es` requiert le connecteur Elasticsearch.

```xml
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-elasticsearch-connector</artifactId>
</dependency>
```

Configuration du connecteur :

```yaml
io.vertigo.connectors.elasticsearch.ElasticSearchFeatures:
  features:
    - native:
        connectorName: "main"
        host: "localhost"
        port: 9200
```

## Dépendances du module

Dépendance obligatoire :

- **vertigo-datamodel** : Requis pour la manipulation des `DataObject` et `DtList`.

Dépendances optionnelles :

- **vertigo-elasticsearch-connector** : Requis uniquement avec la feature `geosearch.es`.
- **Elasticsearch REST High Level Client** : Requis uniquement avec la feature `geosearch.es`.
- **com.google.gson** : Utilisé par `BanGeoCoderPlugin` pour le décodage JSON (dépendance transitive).

```xml
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-geo</artifactId>
</dependency>
```

## Pour les experts

### Managers
| Manager | Rôle | Activé par |
|---|---|---|
| `GeoCoderManager` | Conversion adresse textuelle → coordonnées GPS, calcul de distance (Haversine) | `geocoding` |
| `GeoSearchManager` | Recherche d'objets métier dans un bounding box géographique via Elasticsearch | `geosearch` |

### Features (@Feature)
| Flag | Composants |
|---|---|
| `geocoding` | `GeoCoderManager` + `GeoCoderManagerImpl` |
| `geocoding.google` | `GoogleGeoCoderPlugin` |
| `geocoding.ban` | `BanGeoCoderPlugin` (Base Adresse Nationale) |
| `geosearch` | `GeoSearchManager` + `GeoSearchManagerImpl` |
| `geosearch.es` | `ESGeoSearchPlugin` (+`Activeable`) |

### Plugins
| Plugin | Rôle | Feature |
|---|---|---|
| `GoogleGeoCoderPlugin` | Géocodage via API Google (XML DOM/XPath) | `geocoding.google` |
| `BanGeoCoderPlugin` | Géocodage via API BAN api-adresse.data.gouv.fr (Gson) | `geocoding.ban` |
| `ESGeoSearchPlugin` | Recherche géospatiale via Elasticsearch REST HL | `geosearch.es` |

### Configuration YAML
```yaml
modules:
    io.vertigo.geo.GeoFeatures:
        features:
            - geocoding:
            - geosearch:
        featuresConfig:
            - geocoding.ban:
                  proxyHost: "proxy.example.com"
                  proxyPort: 8080
            - geocoding.google:
                  proxyHost: "proxy.example.com"
                  proxyPort: 8080
            - geosearch.es:
                  envIndexPrefix: "prod_"
                  connectorName: "main"
```
```
