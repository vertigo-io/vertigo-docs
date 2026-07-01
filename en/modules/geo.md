# Geo module

**Geo** is a Vertigo module providing geocoding and geographical search functions.

It converts a textual address into geographic coordinates and searches for business entities indexed within a defined geographical area.

Two features:

- **Geocoding**: Converts an address to GPS coordinates and calculates distance between two points.
- **Geographical search**: Searches for business objects indexed in Elasticsearch by geographical bounding box.

## Configuration

Features are activated via features of `GeoFeatures`.

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

### Available features

Five features are available:

- **geocoding**: Activates the geocoding API (`GeoCoderManager`).
- **geocoding.ban**: BAN (Base Adresse Nationale) plugin as geocoding backend.
- **geocoding.google**: Google Geocode plugin as geocoding backend.
- **geosearch**: Activates the geographical search API (`GeoSearchManager`).
- **geosearch.es**: Elasticsearch plugin as geographical search backend.

### Feature parameters

#### geocoding.ban

REST connector to `api-adresse.data.gouv.fr/search/`. JSON parsing via Gson.

- **proxyHost** *(optional)*: HTTP proxy host.
- **proxyPort** *(optional)*: HTTP proxy port.

#### geocoding.google

REST connector to `maps.googleapis.com/maps/api/geocode/xml`. XPath/DOM parsing.

- **proxyHost** *(optional)*: HTTP proxy host.
- **proxyPort** *(optional)*: HTTP proxy port.

#### geosearch.es

Uses Elasticsearch REST HL with `GeoBoundingBoxQueryBuilder`. Result decoding via `CodecManager` (base64 + compression). `Activeable` implementation.

- **envIndexPrefix** *(required)*: Prefix applied to Elasticsearch index names.
- **connectorName** *(optional)*: Elasticsearch connector name (default: `main`).

## Geocoding

### Architecture

Three-layer architecture:

```
GeoCoderManager (interface)
       |
GeoCoderManagerImpl (implementation)
       |
GeoCoderPlugin (interface)
     /    \
BanGeoCoderPlugin   GoogleGeoCoderPlugin
```

`GeoCoderManagerImpl` delegates to the installed `GeoCoderPlugin`.

- **BanGeoCoderPlugin**: REST call to `api-adresse.data.gouv.fr/search/`, JSON decoding with Gson.
- **GoogleGeoCoderPlugin**: REST call to `maps.googleapis.com/maps/api/geocode/xml`, XML decoding with DOM/XPath.

### API

#### GeoCoderManager

Manager interface exposed via dependency injection.

- `GeoLocation findLocation(String address)`: Returns a `GeoLocation` for the given address. Returns `GeoLocation.UNDEFINED` (never `null`) if no match. Check with `isUndefined()`.
- `double distanceKm(GeoLocation location1, GeoLocation location2)`: Distance in kilometers between two points, calculated using the Haversine formula (earth radius: 6371 km).

#### GeoLocation

Final and immutable class. Includes `GeoLocation.UNDEFINED` and `isUndefined()` for not-found results.

- `double getLatitude()`: Latitude in decimal degrees. Throws exception if undefined.
- `double getLongitude()`: Longitude in decimal degrees. Throws exception if undefined.
- `String getCountryCode()`: ISO country code (e.g.: `FR`).
- `String getLevel1()`: Administrative level 1 (e.g.: region).
- `String getLevel2()`: Administrative level 2 (e.g.: department).
- `String getLocality()`: Locality / municipality.

Constructor:

```java
GeoLocation(double latitude, double longitude, String countryCode, String level1, String level2, String locality)
```
Primitive doubles, values cannot be null.

### Examples

Position a project site and measure distance to another site.

```java
// Geocode a project site
final GeoLocation siteA = geoCoderManager.findLocation("12 rue de la Republique, 75001 Paris");

if (!siteA.isUndefined()) {
    System.out.println("Latitude  : " + siteA.getLatitude());
    System.out.println("Longitude : " + siteA.getLongitude());
    System.out.println("Municipality: " + siteA.getLocality());
}

// Distance between two project sites
final GeoLocation siteB = geoCoderManager.findLocation("1 place du Trocadero, 75116 Paris");
if (!siteA.isUndefined() && !siteB.isUndefined()) {
    final double distance = geoCoderManager.distanceKm(siteA, siteB);
    System.out.println("Distance between sites: " + distance + " km");
}
```

**Caution**: `findLocation` returns `GeoLocation.UNDEFINED` (never `null`) if the address is not found. Check with `.isUndefined()` before using the result.

## Geographical search

### Architecture

```
GeoSearchManager (interface)
         |
GeoSearchManagerImpl (implementation)
         |
GeoSearchPlugin (interface)
         |
ESGeoSearchPlugin (Activeable)
```

`GeoSearchManagerImpl` delegates to the installed `GeoSearchPlugin`. The default value of `maxRows` is 1000. The effective limit is 1000 (known bug: code compares against `DEFAULT_MAX_ROWS` instead of `MAX_MAX_ROWS`).

**ESGeoSearchPlugin**: Concrete plugin implementing search via Elasticsearch REST HL. Uses `GeoBoundingBoxQueryBuilder` to filter documents. Business objects are decoded from Elasticsearch storage via `CodecManager` (base64 serialization with compression). The class implements `Activeable`.

### API

#### GeoSearchManager

- `<D extends DataObject> DtList<D> searchInBoundingBox(GeoLocation topLeft, GeoLocation bottomRight, String indexName, Class<D> dtIndexClass, DataFieldName<D> fieldName, Optional<Integer> maxRowsOpt)`

Parameters:

- **topLeft**: Top-left corner of the rectangle (maximum latitude, minimum longitude).
- **bottomRight**: Bottom-right corner of the rectangle (minimum latitude, maximum longitude).
- **indexName**: Name of the Elasticsearch index to query.
- **dtIndexClass**: Class of the indexed DataObject.
- **fieldName**: Field of the DataObject containing geographic coordinates.
- **maxRowsOpt**: Maximum number of results (default and effective maximum: 1000. Known bug: `MAX_MAX_ROWS`=5000 ignored, validation uses `DEFAULT_MAX_ROWS`=1000).

Returns a `DtList<D>` containing business objects located within the geographical area.

### Example

Search for project sites located within a given geographical area.

```java
// Define bounding box
final GeoLocation topLeft     = new GeoLocation(48.870, 2.280, null, null, null, null);
final GeoLocation bottomRight = new GeoLocation(48.840, 2.330, null, null, null, null);

// Search for project sites in the area
final DtList<DtSiteProjet> sites = geoSearchManager.searchInBoundingBox(
    topLeft,
    bottomRight,
    "idx-project-site",
    DtSiteProjet.class,
    DtSiteProjetFields.siteGeo,
    Optional.of(500)
);

for (final DtSiteProjet site : sites) {
    System.out.println("Site: " + site.getNom());
}
```

**Cautions**:

- `searchInBoundingBox` takes `GeoLocation` objects, not raw coordinates.
- The `maxRows` parameter cannot exceed 1000 (known bug: validation uses `DEFAULT_MAX_ROWS`=1000 instead of `MAX_MAX_ROWS`=5000).
- `topLeft` corresponds to maximum latitude / minimum longitude (north-west corner).
- `bottomRight` corresponds to minimum latitude / maximum longitude (south-east corner).

### Elasticsearch dependencies

The `geosearch.es` feature requires the Elasticsearch connector.

```xml
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-elasticsearch-connector</artifactId>
</dependency>
```

Connector configuration:

```yaml
io.vertigo.connectors.elasticsearch.ElasticSearchFeatures:
  features:
    - native:
        connectorName: "main"
        host: "localhost"
        port: 9200
```

## Module dependencies

Mandatory dependency:

- **vertigo-datamodel**: Required for `DataObject` and `DtList` manipulation.

Optional dependencies:

- **vertigo-elasticsearch-connector**: Required only with the `geosearch.es` feature.
- **Elasticsearch REST High Level Client**: Required only with the `geosearch.es` feature.
- **com.google.gson**: Used by `BanGeoCoderPlugin` for JSON decoding (transitive dependency).

```xml
<dependency>
    <groupId>io.vertigo</groupId>
    <artifactId>vertigo-geo</artifactId>
</dependency>
```

## For Experts

### Managers
| Manager | Role | Activated by |
|---|---|---|
| `GeoCoderManager` | Textual address → GPS coordinates conversion, distance calculation (Haversine) | `geocoding` |
| `GeoSearchManager` | Business object search in geographical bounding box via Elasticsearch | `geosearch` |

### Features (@Feature)
| Flag | Components |
|---|---|
| `geocoding` | `GeoCoderManager` + `GeoCoderManagerImpl` |
| `geocoding.google` | `GoogleGeoCoderPlugin` |
| `geocoding.ban` | `BanGeoCoderPlugin` (Base Adresse Nationale) |
| `geosearch` | `GeoSearchManager` + `GeoSearchManagerImpl` |
| `geosearch.es` | `ESGeoSearchPlugin` (+`Activeable`) |

### Plugins
| Plugin | Role | Feature |
|---|---|---|
| `GoogleGeoCoderPlugin` | Geocoding via Google API (XML DOM/XPath) | `geocoding.google` |
| `BanGeoCoderPlugin` | Geocoding via BAN API api-adresse.data.gouv.fr (Gson) | `geocoding.ban` |
| `ESGeoSearchPlugin` | Geospatial search via Elasticsearch REST HL | `geosearch.es` |

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