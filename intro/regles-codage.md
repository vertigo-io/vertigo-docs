# Règles et conventions de codage

La [philosophie de Vertigo](/intro/philosophie) fixe le cap : simple, modulaire, rapide. Ces principes ne valent que s'ils se retrouvent dans le code, ligne à ligne. Cette page décrit les règles concrètes appliquées dans tout le framework — et que nous recommandons d'appliquer dans les applications construites avec.

## Bannir null

Vertigo applique le *design by contract* formalisé par Bertrand Meyer (langage Eiffel) : chaque méthode annonce un contrat — ce qu'elle exige de ses arguments, ce qu'elle garantit en retour — et le vérifie **à l'exécution, au plus tôt**.

L'outil est la classe `Assertion` (`io.vertigo.core.lang`), une API fluide placée en tête de chaque méthode publique :

```java
public MovieDisplay getMovieDisplay(final Long movieId, final String locale) {
	Assertion.check()
			.isNotNull(movieId, "L'id du film est obligatoire")
			.isNotBlank(locale, "La locale {0} doit être renseignée", locale);
	// ---
	final Movie movie = movieDAO.get(movieId);
	return toDisplay(movie, locale);
}
```

Les règles associées :

- **Le bloc d'assertions ouvre la méthode**, un séparateur `// ---` le distingue du corps. En lisant une méthode, le contrat se voit d'un coup d'œil ; tout ce qui suit le séparateur peut supposer le contrat rempli.
- **Distinguer contrat et état** : `isNotNull` / `isNotBlank` vérifient les *arguments* (le contrat vis-à-vis de l'appelant), `isTrue` / `isFalse` vérifient une *condition* — typiquement l'état interne de l'objet. Les exceptions levées suivent cette distinction (`NullPointerException` / `IllegalArgumentException` pour le contrat, `IllegalStateException` pour l'état).

```java
public void start() {
	Assertion.check()
			.isFalse(started, "Le composant est déjà démarré");
	// ---
	started = true;
}
```

- **Une API publique ne retourne jamais null** : un résultat facultatif est un `Optional<T>`. L'appelant est forcé de traiter l'absence, le compilateur travaille pour vous.
- **Une collection n'est jamais nulle** : au pire elle est vide. `for` et `stream()` fonctionnent alors sans garde.

Le bénéfice est double : l'erreur éclate **au plus près de sa cause** (un argument invalide est détecté à l'entrée de la méthode, pas trois couches plus bas dans une `NullPointerException` anonyme), et le corps des méthodes est débarrassé des `if (x != null)` défensifs qui gonflent la complexité cyclomatique sans rien garantir.

## Favoriser l'immutabilité

Un objet immuable ne peut pas être observé dans un état incohérent : une fois construit, il est définitif. Les règles :

- l'état est **injecté au constructeur** (et validé par assertions) ;
- **pas de setters** ;
- classes et champs déclarés **`final`** ;
- les collections exposées sont enveloppées par `Collections.unmodifiableList` / `unmodifiableMap`...

```java
public final class MovieInfo {
	private final String title;
	private final List<String> tags;

	public MovieInfo(final String title, final List<String> tags) {
		Assertion.check()
				.isNotBlank(title)
				.isNotNull(tags);
		// ---
		this.title = title;
		this.tags = Collections.unmodifiableList(new ArrayList<>(tags));
	}

	public String getTitle() {
		return title;
	}

	public List<String> getTags() {
		return tags;
	}
}
```

Le bénéfice : la **thread-safety par construction** (aucune synchronisation à écrire, aucun état partagé mutable) et le **raisonnement local** — la valeur d'un objet immuable ne dépend ni du moment ni du chemin par lequel il vous arrive.

## Builders et style fluent

Immutabilité et objets riches en options se concilient par le pattern **Builder** : le builder est mutable et guide la construction, l'objet construit est immuable. Vertigo le formalise par l'interface `io.vertigo.core.lang.Builder<T>`, omniprésente dans le framework (`NodeConfig`, `ModuleConfig`, `SearchQuery`...) :

```java
public interface Builder<T> {
	T build();
}
```

Exemple réel, la configuration d'un nœud (voir [Configuration](/basic/configuration)) :

```java
final NodeConfig nodeConfig = NodeConfig.builder()
	.addModule(new CommonsFeatures().build())
	.addModule(new VegaFeatures()
		.withWebServices()
		.build())
	.addModule(ModuleConfig.builder("Hello")
		.addComponent(HelloWebServices.class)
		.build())
	.build();
```

Les conventions de nommage portent le sens :

- **`with...`** : l'élément est renseigné **au plus une fois** (un serveur embarqué, un nom d'application...) ;
- **`add...`** : l'appel est **répétable**, chaque appel ajoute un élément (un module, un composant...).

La méthode `build()` valide la cohérence de l'ensemble (par assertions) et retourne l'objet définitif. Le code de configuration se lit alors comme une description, pas comme une suite d'affectations.

## Util vs Helper

Deux familles de classes outillent le code, à ne pas confondre :

- **Util** : classe **statique et sans état**, donc threadsafe par nature. Exemples dans `io.vertigo.core.util` : `StringUtil` (formatage de messages, conversions camelCase/CONST_CASE), `ClassUtil` (introspection), `BeanUtil` (accès aux propriétés).

```java
final String columnName = StringUtil.camelToConstCase("movieTitle"); // MOVIE_TITLE
```

- **Helper** : classe **à état**, dont le constructeur prend l'objet à manipuler ; les méthodes travaillent ensuite sur cet objet. Un helper s'instancie au plus près de l'usage et ne se partage pas entre threads.

```java
final MovieHelper movieHelper = new MovieHelper(movie);
movieHelper.applyDefaultRating();
```

Si une classe `Util` accumule des paramètres passés à chaque appel, c'est le signe qu'un `Helper` est plus adapté — et inversement, un helper sans état n'a pas de raison d'être instancié.

?> Note : `DateUtil` ne sert plus qu'au parsing d'**expressions de dates relatives** (`parseToLocalDate` / `parseToInstant`, ex. `"now+8d"`), utilisées notamment par les facettes range de la recherche. Pour tout le reste, `java.time` couvre le besoin.

## Loggers

La règle par défaut : **un logger au nom de la classe**, qui suit le découpage du code.

```java
private static final Logger LOG = LogManager.getLogger(MovieServices.class);
```

En complément, Vertigo utilise des **loggers de catégorie** pour extraire un flux transverse, indépendamment des classes qui le produisent : `sql` (requêtes SQL), `tasks` (exécution des Tasks), `health`, `metric`. Les deux approches coexistent : la classe pour situer le code, la catégorie pour suivre un type d'événement de bout en bout. La configuration log4j2 pilote chaque flux séparément :

```xml
<Logger name="sql" level="info" additivity="false">
	<AppenderRef ref="sqlAppender" />
</Logger>
```

Enfin, le **SmartLogger** du module analytics (`SmartLoggerAnalyticsConnectorPlugin`) logge les processus **par catégorie** avec un seuil de durée `durationThreshold` (1000 ms par défaut) : sous le seuil un processus est loggé en INFO, au-delà il passe en **ERROR** — les traitements anormalement lents ressortent d'eux-mêmes dans les logs.
