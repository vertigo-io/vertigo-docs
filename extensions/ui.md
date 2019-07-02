# UI

L'extension vertigo-ui permet la création d'écrans riches, de manière simple et sécurisée.

Les principes généraux sont explicités dans [basic/ui](/basic/ui) : 

Nous présentons ici, les éléments plus spécifiques qui aident à la prise en main du module Vertigo-ui.

## Controller : SpringMVC

La documentation de SpringMVC sur [docs.spring.io](https://docs.spring.io/spring/docs/3.2.x/spring-framework-reference/html/mvc.html)

Le fonctionnement principale de SpringMVC est de permettre de mapper simplement des requetes HTTP vers des méthodes Java.
Pour cela deux mécanismes cohabitent : 

- par annotations Java pour décrire le comportement et le mapping mis en place
- par paramétrage dans la configuration Spring de `Resolver` automatique (`ReturnValueHandler` et `ArgumentResolver`) spécifiques réalisant la conversion des données entrantes ou sortantes de manière transparente

Pour fluidifier les développements Vertigo-ui utilise et complète ces deux mécanismes de SpringMVC par défaut avec des annotations spécifiques et des resolvers spécifiques.

Ci-dessous les annotations que l'on utilise le plus souvant :

### Annotations SpringMVC

- **@Controller** : Indique que le Bean est un controller. Doit hériter de `AbstractVSpringMvcController`
- **@RequestMapping** : Préfix des urls de ce Controller. Doit respecter le nommage *moduleApplicatif*/*EntitéMétier*, ce nommage se retrouve partout : Url, packages java, répertoires des vues, déclaration du model, etc...
- **@Inject** : Mécanisme d'injection standard. On ne doit injecter dans des controllers que des Services (ou exceptionnellemnt un autre controller, lorsqu'il y a des éléments du context, ou des actions, en commun par exemple pour les bandeaux de page de détail)
- **@GetMapping("myUrl")** : Déclare l'url en GET. Elle représente le point d'entrée sur le controller. Par convention la méthode est nommée `initContext`, prend l'object [ViewContext](#ViewContext) et les paramètres d'entrée nécessaires (bindé avec @PathVariable ou @RequestParam par exemple)
- **@PostMapping("/_myAction")** : Déclare l'url en POST. Elle représente le point d'action sur le controller. Par convention l'url est préfixée par `_` et la méthode par `do`. La méthode prend les données attendues annotées avec `@ViewAttribute("nomDuParam")`.
- **@DeleteMapping("_myAction")** : Déclare l'url en DELETE.
- **@PathVariable("paramName")** : Map une variable avec une portion de l'url du service. Ex: `https://localhost:8080/base/12/mainPicture`, méthode du controller annotée : `@GetMapping("{baseId}/mainPicture")`, le paramètre de la méthode est annoté : `@PathVariable("baseId") final Long baseId` 
- **@RequestParam("paramName")** : Map une variable avec un paramètre de la request. Ex: `https://localhost:8080/base/myUrl?baseId=12`, méthode du controller annotée : `@GetMapping("myUrl")`, le paramètre de la méthode est annoté : `@RequestParam("baseId") final Long baseId`. Ce cas est finallement rarement mis en place, car on préfère une approche *REST-like* ou les identifiants sont dans le path de l'url, ou bien on passe des objets complèts (mappés par @ViewAttribute).

### Annotations Vertigo-ui

- **@ViewAttribute("nomDuParam")** : Map une variable de type objet, avec les données de formulaire lors d'un POST. Le nom doit correspondre à une clé du context (voir [ViewContextKey](#ViewContextKey)). L'objet est récupéré du context, mis à jour par les données du POST, validées puis passées à la méthode.
- **@QueryParam("paramName")** : Utiliser dans quelques cas pour indiquer le nom du paramètre de la request. Typiquement pour opérations sur les fichiers ([VFile](VFile) et [FileInfoURI](FileInfoURI)

### ArgumentResolver Vertigo-ui

- **ViewContext** : Objet représentant le context de la page. Vierge sur un GET, il a vocation a être peuplé, récupérer et mis à jour sur un POST il est utlisé pour réaliser l'action.
- **DtListState** : Objet représentant l'état d'affichage d'une page : tri et pagination.
- **UiMessageStack** : Objet contenant la pile des messages de l'action : erreurs de format et de surface (validation des contraintes et du caractère non null), il peut être passé au service et complété avec des messages d'erreur, de warning, d'info ou de succès globaux, par objet ou par champs 
- **FileInfoURI** : Permet de recevoir une uri de fichier. Nécessite de nommer le paramètre avec `@QueryParam`. A noter que les URI de fichiers sont protégées dans la page (transformées), lorsqu'elle reviens sur le serveur on fait la traduction inverse.
- **VFile** : Permet de recevoir un fichier. Nécessite de nommer le paramètre avec `@QueryParam`. Le fichier est temporaire et doit être persisté si besoin dans un service.
- **Optional<AutreType> ** : Permet de supporter les paramètres optionnels.

### ReturnValueHandler Vertigo-ui

- **void** : Lorsqu'une méthode du controller mappée en POST ou autre ne retourne rien (`void`), la page est rafraichit en prenant en compte les modifications du context effectuées dans la méthode du controller. *(ce évidement pas vraiment un ReturnValueHandler)*
- **ViewContext** : Retourne spécifiquement un viewContext mis à jour. Ceci est utilisé dans le cas des appels Ajax, qui ne doivent recevoir en retour que des données Json et non la page HTML.
- **FileInfoURI** : Permet d'envoyer une uri fichier. L'uri est protégée (transformée) et n'est pas envoyée en clair.
- **VFile** : Permet d'envoyer un fichier.

### Autres spécificités Vertigo-ui

- **ViewContextKey<AutreType>** : Déclare une entrée typée dans le context de la page.

API du **ViewContext**
- publishRef : Ajoute au context un simple objet sérialisable
- publishDto : Ajoute au context un objet (DtObject) de formulaire
- checkDtoErrors : Vérifie les erreurs de l'objet. Celles-ci sont ajoutées à l'uiMessageStack si nécessaire
- readDto : Retourne l'objet métier validé. Lance une exception si erreur.
- publishDtList : Ajoute au context une liste (DtList)
- readDtList : Retourne l'objet métier validé. Lance une exception si erreur.
- publishDtListModifiable : Ajoute au context une liste modifiable (DtList)
- checkDtListErrors : Vérifie les erreurs de la liste. Celles-ci sont ajoutées à l'uiMessageStack si nécessaire
- readDtListModifiable : Retourne la liste des objets métier validés. Lance une exception si erreur.
- publishMdl : Ajoute au context une liste de référence (MDL : Master Data List), en précisant l'entité et le code de la liste.
- publishFacetedQueryResult : Ajoute au context le résultat d'une recherche avec facette. 

- getUiObject : Récupère du context l'objet venant de l'IHM, tel que reçu sur le serveur. A réserver à quelques cas : utilisé pour faire des controles non bloquant par exemple.
- getUiList : Récupère du context la liste venant de l'IHM, tel que reçu sur le serveur. A réserver à quelques cas.
- getUiListModifiable : Récupère du context la liste modifiables venant de l'IHM
- getString : Récupère une string du context
- getLong : Récupère un Long du context
- getInteger : Récupère un Integer du context
- getBoolean : Récupère un Boolean du context
- getSelectedFacetValues : Récupère la liste des facettes séléctionnées depuis l'IHM de la recherche à facette.

## IMH : Comment lire ?

Comme nous l'avons déjà présenté, l'IHM est la composition de plusieurs briques : Vue.js, Quasar, Thymeleaf et Vertigo-ui.
Avant de rentrer dans le détail de chacune de ces briques, voici quelques éléments pour s'y retrouver.

- La page est rendue en deux endroits : sur le serveur par Thymeleaf et les composants Vertigo-ui, et sur le client par Vue.js et Quasar.
- le préfix `th:` indique à thymeleaf d'interpréter le composant ou l'attribut
- le préfix `:` indique à vue.js d'interpréter le composant ou l'attribut
- le préfix `th::` est la somme des deux : thymeleaf interpretera et laissera le `:` pour vue.js
- le préfix `layout:` est une extension thymeleaf qui propose du templating comme *Tiles*.
- les attributs commencant par `v-` sont des directives Vue.js
- les tags commencant par `<q-` sont des composants Quasar.  
- les tags commencant par `<vu:` sont des composants Vertigo-ui.  


## Moteur de rendu : Vue.js

La documentation de Vue.js sur [vuejs.org](https://vuejs.org/v2/guide/)

Vue.js propose une approche WebComponent avec une IHM réactive mappée sur un model de vue, selon le pattern Observer/Observable. 

- **inline {{abc}}**
- **prefix :**
- **|abc|** 
- **v-if**
- **v-for**
- **v-model**
- **@click**
- **v-cloak**

## Bibliothèque de composant : Quasar

La documentation de Quasar sur [quasar.dev](https://v0-17.quasar-framework.org/guide/)

!> Vertigo-ui 2.0.0 utilise la version 0.17 de Quasar, la 1.0.0 étant toujours en RC, à l'heure ou nous écrivons ces lignes.

- **q-page**
- **q-layout**
- **q-toolbar**
- **q-btn**
- **q-item**
- **q-popover**
- **q-page-sticky**

## Moteur de templating : Thymeleaf

Nécessite : 
```HTML
<html xmlns:th="http://www.thymeleaf.org">
```
La documentation de Thymeleaf sur [thymeleaf.org](https://www.thymeleaf.org/doc/tutorials/3.0/usingthymeleaf.html)

- **inline __${abc}__**
- **prefix th:**
- **abc?:bcd**
- **${abc}**
- **@{abc}**
- **~{abc::bcd}**
- **th:if**
- **th:with="var1=${...}, var2=${...}"**
- **th:attr**
- **th:text**
- **th:replace**
- **th:include**
- **th:remove**


## Moteur de layout : Thymeleaf Layout

La documentation de Thymeleaf Layout sur [github](https://ultraq.github.io/thymeleaf-layout-dialect/)

Nécessite : 
```HTML
<html xmlns:layout="http://www.ultraq.net.nz/thymeleaf/layout">
```

- **head**
- **layout:decorate**
- **layout:fragment**

## Composants nommés Vertigo-ui

Les composants Vertigo-ui utilise le templating Thymeleaf, chaque composant est en fait un th:replace avec un peu d'intelligence complémentaire.
Le principe (et du code) est repris de [thymeleaf-component-dialect](https://github.com/Serbroda/thymeleaf-component-dialect)

Nécessite : 
```HTML
<html xmlns:vu="http://www.morphbit.com/thymeleaf/component>
```

- **abc_slot**
- **abc_attrs**
- **other_attrs**
- **contentTags**


- **vu:page**
- **vu:include-data**
  - object
  - field
- **vu:include-data-primitive**
- **vu:include-data-protected**
- **vu:slot**


- **vu:page**
- **vu:head**
- **vu:block**
- **vu:form**
- **vu:grid**
  - cols
  - contentTags
- **vu:grid-cell**
- **vu:messages**
- **vu:modal**


- **vu:label**
- **vu:text-field**
- **vu:text-area**
- **vu:autocomplete**
- **vu:checkbox**
- **vu:select**
- **vu:radio**
- **vu:date**
- **vu:datetime**
- **vu:knob**
- **vu:slider**
- **vu:chips-autocomplete**
- **vu:fileupload**

- **vu:cards**
- **vu:field-read**
- **vu:table**
  - list
  - componentId
  - selectable
  - rowKey
  - rowsPerPage
  - sortUrl
  - navOnRow
  - color
  - tableClass
  - autoColClass
  - top_right_slot
  - top_left_slot
  - actions_slot
  - tr_attrs
  - other_attrs
- **vu:column**
- **vu:list**
- **vu:search**
- **vu:facets**
- **vu:content**
- **vu:content-slot**
    - name
- **vu:content-item**

- **vu:button-link**
- **vu:button-submit**

## Composants Vue.js Vertigo-ui

- **vueData**
- **v-notifications**
- **v-comments**
- **v-scroll-spy**
- **v-json-editor**
- **v-chatbot**