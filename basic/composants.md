# Composants

Les composants sont des objets offrant des services.
Ils doivent à minima implémenter l'interface `io.vertigo.core.component.Component` qui n'est rien d'autre qu'un simple marqueur ou bien implémenter une interface métier qui contractualise les services offerts.

!> Les composants sont des singletons, ils doivent donc avoir un comportant **threadsafe**. Un moyen simple de s'en assurer est d'en faire des objets totalement **stateless**.

Voici les principaux types de composants utilisés dans un projet Vertigo :
- les **Manager** qui sont les composants internes de Vertigo et qui offrent des fonctionnalités essentielles (ex: `StoreManager`,  `AuthorizationManager`, etc...) 
- les **DAO** qui encapsulent l'accès aux données. Ces composants sont en règle générale générés (voir MDA)
- les **Services** qui comportent la logique métier du projet et offrent donc des services de haut niveau. Les extensions Vertigo proposent également des services de haut niveau.
- les **WebServices** qui en règle générale consomment les services métier et les exposent sous forme de webservices REST


## Construction

Les composants sont instantiés par le moteur d'injection et sont utilisables par les autres composants par ce même mécanisme d'injection de dépendances.

Pour être créé, un composant doit donc avoir au choix :

- aucun constructeur (c'est donc le constructeur par défaut qui sera utilisé)
- un (et un seul) constructeur public déclaré. Lorqu'un constructeur est déclaré, celui-ci doit porter l'annotation `@Inject`. 


Il est possible d'injecter dans un composant, soit sous la forme de variables d'instance, soit sous la forme de paramètres du constructeur, les éléments suivants :

- un paramètre de type primitif portant l'annotation `@Named` afin de spécifier son nom
- un composant
- un plugin
- une liste de plugins du même type 


```java
@Inject
public Calculator3(@Named("offset") final Optional<Integer> offset) {
	this.offset = offset.orElse(0);
}
```

?> L'injection de paramètres permet la gestion des `Optional` lorsque ceux-ci peuvent-être nuls


```java
@Inject
public Calculator6(final List<OperationPlugin> operationPlugins) {
	operationDispatcher = new HashMap<>();
	for (final OperationPlugin operationPlugin : operationPlugins) {
		operationDispatcher.put(operationPlugin.getOperator(), operationPlugin);
	}
}
```

```java
@Inject
private OperationPlugin operationPlugin;
```

```java
@Inject
@Named("log")
private boolean log;
```

## Utilisation

Pour être utilisé par un traitement, un composant doit être récupéré dans l'objet nécessitant l'utilisation de ce composant. 

Cet objet est souvent lui-même un composant et dans ce cas l'injection de dépendances doit être utilisée pour récupérer l'instance et donc appeler les méthodes offertes par le composant.

> La classe qui doit être utilisée lors de l'injection (Calculator1 dans l'exemple ci-dessous) est l'interface lorsque le composant implémente une interface ou sa classe d'implémentation dans le cas contraire.

```java
@Inject
private Calculator1 calculator1;
```

?> Ce mécanisme est disponible dans la totalité des classes manipulées par le développeur. Il est donc à privilégier.

> C'est le cas des DAO qui sont utilisés par les services métier ou les services métier eux-même utilisés par les webservices.

Dans le cas où l'objet n'est pas lui-même un composant et donc n'est pas créé par le moteur d'injection, il est possible d'activer manuellement l'injection de dépedances :
- soit lors de la création de l'instance :
```java
DIInjector.newInstance(Samples.class, Node.getNode().getComponentSpace())
```
- soit après coup :
```java
final Samples sample = new Samples();
DIInjector.injectMembers(sample, Node.getNode().getComponentSpace());
```

## Accès direct au registre de composants

Il est également possible de récupérer le composant directement dans l'espace des composants.

```java
final Calculator2 calculator2 = Node.getNode().getComponentSpace().resolve(Calculator2.class)
```
!> Attention : cette pratique n'est à utiliser que dans les cas très particuliers (et extrèmement rares) où l'injection n'est pas disponible.

Il est ensuite possible d'utiliser les services offerts par ce composant

```java
calculator1.sum(1, 2, 3, 4);
```

## Comportement

Il est possible d'ajouter les comportements suivants aux composants :
- `Activeable` : permet d'avoir des points d'appel au démarrage et à l'arrêt du composant

```java
@Override
public void start() {
}

@Override
public void stop() {
}
```

- `DefinitionProvider` et `SimpleDefinitionProvider` : permet d'enrichir l'espace des définitions
```java
@Override
public List<Definition> provideDefinitions(final DefinitionSpace definitionSpace) {
	return Collections.emptyList();
}
```

## Exemple

Voici un exemple de service métier qui peut être implémenté avec Vertigo. Ce dernier utilise un autre composant DAO ainsi qu'un aspect `@Transactional` permettant de gérér la transactionalité des méthodes de services.

```java
@Transactional
public class MovieServicesImpl implements MovieServices {

	@Inject
	private MovieDAO movieDAO;

	@Override
	public Movie getMovieById(final Long movId) {
		Assertion.checkNotNull(movId);
		// ---
		return movieDAO.get(movId);
	}

}
```