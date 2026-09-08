# UI

L'extension vertigo-ui permet la création d'écrans riches, de manière simple et sécurisée.

Les principes généraux sont explicités dans [basic/ui](/basic/ui).

Nous présentons ici les éléments plus spécifiques qui aident à la prise en main du module vertigo-ui.

## Controller : SpringMVC

La documentation de SpringMVC sur [docs.spring.io](https://docs.spring.io/spring-framework/reference/web/webmvc.html)

Le fonctionnement principal de SpringMVC est de permettre de mapper simplement des requêtes HTTP vers des méthodes Java.
Pour cela deux mécanismes cohabitent :

- par annotations Java pour décrire le comportement et le mapping mis en place
- par paramétrage dans la configuration Spring de resolvers automatiques spécifiques réalisant la conversion des données entrantes ou sortantes de manière transparente (`ReturnValueHandler` et `ArgumentResolver`)

Pour fluidifier les développements Vertigo-UI utilise et complète ces deux mécanismes de SpringMVC par défaut avec des annotations spécifiques et des resolvers spécifiques.

Ci-dessous les annotations que l'on utilise le plus souvent :

### Annotations SpringMVC

- `@Controller` : Indique que le Bean est un controller. Doit hériter de `AbstractVSpringMvcController`
- `@RequestMapping` : Préfixe des urls de ce Controller. Doit respecter le nommage *moduleApplicatif*/*EntitéMétier*, ce nommage se retrouve partout : Url, packages java, répertoires des vues, déclaration du modèle, etc...
- `@Inject` : Mécanisme d'injection standard. On ne doit injecter dans des controllers que des Services (ou exceptionnellement un autre controller, lorsqu'il y a des éléments du contexte, ou des actions, en commun par exemple pour les bandeaux de page de détail)
- `@GetMapping("myUrl")` : Déclare l'url en GET. Elle représente le point d'entrée sur le controller. Par convention la méthode est nommée `initContext`, prend l'objet [ViewContext](#viewcontext) et les paramètres d'entrée nécessaires (bindé avec @PathVariable ou @RequestParam par exemple)
- `@PostMapping("/_myAction")` : Déclare l'url en POST. Elle représente le point d'action sur le controller. Par convention l'url est préfixée par `_` et la méthode par `do`. La méthode prend les données attendues annotées avec `@ViewAttribute("nomDuParam")`.
- `@DeleteMapping("_myAction")` : Déclare l'url en DELETE.
- `@PathVariable("paramName")` : Mappe une variable avec une portion de l'url du service. Ex: `https://localhost:8080/base/12/mainPicture`, méthode du controller annotée : `@GetMapping("{baseId}/mainPicture")`, le paramètre de la méthode est annoté : `@PathVariable("baseId") final Long baseId`
- `@RequestParam("paramName")` : Mappe une variable avec un paramètre de la request. Ex: `https://localhost:8080/base/myUrl?baseId=12`, méthode du controller annotée : `@GetMapping("myUrl")`, le paramètre de la méthode est annoté : `@RequestParam("baseId") final Long baseId`. Ce cas est finalement rarement mis en place, car on préfère une approche *REST-like* où les identifiants sont dans le path de l'url, ou bien on passe des objets complets (mappés par @ViewAttribute).

### Annotations Vertigo-UI

- `@ViewAttribute("nomDuParam")` : Mappe une variable de type objet, avec les données de formulaire lors d'un POST. Le nom doit correspondre à une clé du contexte (voir `ViewContextKey`). L'objet est récupéré du contexte, mis à jour par les données du POST, validées puis passées à la méthode.
- `@QueryParam("paramName")` : Utiliser dans quelques cas pour indiquer le nom du paramètre de la request. Typiquement pour les opérations sur les fichiers (`VFile` et `FileInfoURI`)
- `@Secured("authname")` : Utiliser sur les controllers ou les méthodes de controller pour vérifier que l'utilisateur a bien ces autorisations. (Utilise la configuration de vertigo-account authorization)

### ArgumentResolver Vertigo-UI

- `ViewContext` : Objet représentant le contexte de la page. Vierge sur un GET, il a vocation à être peuplé, récupéré et mis à jour sur un POST. Il est utilisé pour réaliser l'action.
- `DtListState` : Objet représentant l'état d'affichage d'une page : tri et pagination.
- `UiMessageStack` : Objet contenant la pile des messages de l'action : erreurs de format et de surface (validation des contraintes et du caractère non null), il peut être passé au service et complété avec des messages d'erreur, de warning, d'info ou de succès globaux, par objet ou par champ
- `FileInfoURI` : Permet de recevoir une uri de fichier. Nécessite de nommer le paramètre avec `@QueryParam`. Les URI de fichiers sont protégées dans la page (transformées), lors du retour sur le serveur on fait la traduction inverse.
- `VFile` : Permet de recevoir un fichier. Nécessite de nommer le paramètre avec `@QueryParam`. Le fichier est temporaire et doit être persisté si besoin dans un service.
- `Optional<AutreType>` : Permet de supporter les paramètres optionnels.

### ReturnValueHandler Vertigo-UI

- `void` : Lorsqu'une méthode du controller mappée en POST ou autre ne retourne rien (`void`), la page est rafraîchie en prenant en compte les modifications du contexte effectuées dans la méthode du controller. *(ce n'est évidemment pas vraiment un ReturnValueHandler)*
- `ViewContext` : Retourne spécifiquement un viewContext mis à jour. Ceci est utilisé dans le cas des appels Ajax, qui ne doivent recevoir en retour que des données Json et non la page HTML.
- `FileInfoURI` : Permet d'envoyer une uri fichier. L'uri est protégée (transformée) et n'est pas envoyée en clair.
- `VFile` : Permet d'envoyer un fichier.

### Autres spécificités Vertigo-UI

- `ViewContextKey<AutreType>` : Déclare une entrée typée dans le contexte de la page.
- `UiUtil` : utilitaire exposé au contexte de la page, accessible dans les templates via `model.util` (clé `util` du ViewContext). Il propose des fonctions qui sont utiles pour les composants Vertigo-UI et le rendu des pages. En général, les pages n'ont pas besoin de l'utiliser, mais plus les composants.
- `UiAuthorizationUtil` : Utilitaire passé au moteur de templating `authz`, il propose des fonctions pour simplifier les contrôles de sécurité lors de l'affichage. 3 modes d'utilisation :
     - 1- Avec une chaîne simple :
        `vu:authz="myGlobalAuthz"` ou `vu:authz="mySecuredEntityAuthz$read"`
         => équivalent à `authz.hasAuthorization('myGlobalAuthz')`
         `hasAuthorization` applique automatiquement le préfixe `Atz` aux noms passés : on écrit `myGlobalAuthz` et non `AtzMyGlobalAuthz`.
         Supporte les listes multiples avec `,` pour OR et `!` pour NOT
     - 2- Avec un chemin vers un `UiObject<Entity>` du contexte :
        `vu:authz="model.myEntity$read"` ou `vu:authz="model.list[0]$read"`
        => équivalent à `authz.hasOperation(model.myEntity, 'read')`
        (la première partie est évaluée comme `${model.myEntity}`)
     - 3- Avec une expression évaluée (commence par `${` )
        `vu:authz="${authz.hasAuthorization('myGlobalAuthz') && authz.hasAuthorization('mySecuredEntityAuthz$read')}"`
        => exactement équivalent à `th:if`. Mais gardez `th:if` pour la logique métier et `vu:authz` pour la logique de sécurité

API du **ViewContext**
- `publishRef` : Ajoute au contexte un simple objet sérialisable
- `publishDto` : Ajoute au contexte un objet (DtObject) de formulaire
- `checkDtoErrors` : Vérifie les erreurs de l'objet. Celles-ci sont ajoutées à l'uiMessageStack si nécessaire
- `readDto` : Retourne l'objet métier validé. Lance une exception si erreur.
- `publishDtList` : Ajoute au contexte une liste (DtList)
- `readDtList` : Retourne l'objet métier validé. Lance une exception si erreur.
- `publishDtListModifiable` : Ajoute au contexte une liste modifiable (DtList)
- `checkDtListErrors` : Vérifie les erreurs de la liste. Celles-ci sont ajoutées à l'uiMessageStack si nécessaire
- `readDtListModifiable` : Retourne la liste des objets métier validés. Lance une exception si erreur.
- `publishMdl` : Ajoute au contexte une liste de référence (MDL : Master Data List), en précisant l'entité et le code de la liste.
- `publishFacetedQueryResult` : Ajoute au contexte le résultat d'une recherche avec facette.
- `getUiObject` : Récupère du contexte l'objet venant de l'IHM, tel que reçu sur le serveur. À réserver à quelques cas : utilisé pour faire des contrôles non bloquants par exemple.
- `getUiList` : Récupère du contexte la liste venant de l'IHM, telle que reçue sur le serveur. À réserver à quelques cas.
- `getUiListModifiable` : Récupère du contexte la liste modifiable venant de l'IHM
- `getString` : Récupère une string du contexte
- `getLong` : Récupère un Long du contexte
- `getInteger` : Récupère un Integer du contexte
- `getBoolean` : Récupère un Boolean du contexte
- `getSelectedFacetValues` : Récupère la liste des facettes sélectionnées depuis l'IHM de la recherche à facette.

## IHM : Comment lire ?

Comme nous l'avons déjà présenté, l'IHM est la composition de plusieurs briques : VueJS, Quasar, Thymeleaf et Vertigo-UI.
Avant de rentrer dans le détail de chacune de ces briques, voici quelques éléments pour s'y retrouver.

- La page est rendue en deux endroits : sur le serveur par Thymeleaf et les composants Vertigo-UI, et sur le client par VueJS et Quasar.
- le préfixe `th:` indique à Thymeleaf d'interpréter le composant ou l'attribut
- le préfixe `:` indique à VueJS d'interpréter le composant ou l'attribut
- le préfixe `th::` est la composition de `th:` et `:`, Thymeleaf interprétera et laissera le `:` pour VueJS
- le préfixe `layout:` est une extension Thymeleaf qui propose du templating comme *Tiles*.
- les attributs commençant par `v-` sont des directives VueJS
- les tags commençant par `<q-` sont des composants Quasar.  
- les tags commençant par `<vu:` sont des composants Vertigo-UI.  


## Moteur de rendu : VueJS

La documentation de VueJS sur [vuejs.org](https://vuejs.org/guide/)

VueJS 3 propose une approche WebComponent avec une IHM réactive mappée sur un modèle de vue, selon le pattern Observer/Observable.

- **inline** `{{abc}}` : L'utilisation des *moustaches* permet d'ajouter directement la valeur de `abc` dans le DOM. La valeur est *réactive* et encodée en HTML
- **prefix** `:` : Ce préfixe indique que VueJS doit interpréter l'attribut qui suit. Cela permet de faire du VueJS sur des attributs HTML standards ou d'un webComponent (comme src, value ou icon de quasar)
- `v-if="..."` : Donne la condition d'affichage sur un noeud du DOM. La condition peut être une variable du vueData ou une expression à évaluer. Attention, l'élément disparaît du DOM, mais est présent côté client et ne convient pas à la mise en place de la sécurité.
- `v-for="item in items"` : L'élément sur lequel est posé le `v-for` est dupliqué pour chaque élément. La variable de boucle peut être utilisée pour changer le rendu de chaque boucle
- `v-model` : Indique la donnée du vueData bindé sur le composant
- `@click` : Précise une action à réaliser sur l'événement `click` du composant. La variante `@click.native` n'est plus nécessaire avec Vue 3 (les événements sont automatiquement forwardés)
- `v-pre` : Indique à Vue de sauter la compilation de cette portion de DOM. Utilisé automatiquement par `vu:utext` pour protéger contre les injections XSS
- `v-once` : Rend le noeud et ses enfants en une seule passe, les sauts de réactivité ultérieurs sont ignorés

Pour une application Vue pure (SPA) sans rendu serveur Thymeleaf, Vertigo ne fournit pas de mécanisme d'autorisation côté client. Le pattern recommandé consiste à exposer les droits de l'utilisateur via un WebService (autorisations *à priori* et opérations autorisées par entité), puis à évaluer l'affichage en conséquence côté client. Ce contrôle côté client ne sert qu'à l'affichage : le contrôle côté serveur reste obligatoire, c'est lui qui fait foi. Voir la section [Vue SPA](/extensions/account#vue-spa) du module vertigo-account pour le pattern détaillé, et la section [Autres spécificités Vertigo-UI](#autres-spécificités-vertigo-ui) du présent fichier pour le SSR (`vu:authz` / `th:if`).

## Bibliothèque de composants : Quasar

La documentation de Quasar sur [quasar.dev](https://quasar.dev/vue-components/)

!> Vertigo-UI 4.4.1 utilise Quasar **2.21.1** (Vue 3). La migration Quasar 1 → 2 concernait notamment `q-modal` → `q-dialog` (`QModal` est absent de Quasar 2). Pour l'upload de fichiers, ce n'est pas un changement d'API Quasar : `QUploader` existe bien dans Quasar 2.21.1 ; c'est le composant Vertigo-UI qui utilise désormais le composant maison `v-file-upload-quasar` (plutôt que `q-uploader` de Quasar).

Les composants les plus courants sont :

- `q-page`
- `q-layout`
- `q-toolbar`
- `q-btn`
- `q-item`
- `q-dialog` (remplace `q-modal` de Quasar 1)
- `q-icon`
- `q-knob`
- `q-slider`

> **Thèmes** : le thème d'un layout se choisit avec `useDsfr` (défaut `false`, disponible sur `vu:head` et `vu:head-meta`), qui charge le thème DSFR (`vertigo-dsfr.css` + `dsfr.umd.js`). Le paramètre `onlyDsfrStyle` (défaut `false`) est exclusif à `vu:head-meta` : il masque tous les CSS 3rd-party non-DSFR (y compris le CSS Quasar) — passé sur `vu:head`, il est sans effet. Le thème DSFR est complété par une famille de composants `vu:dsfr-*` (boutons, collections, inputs, layout, table), documentée dans la page [Écosystème UI](/extensions/ui-ecosystem).

## Moteur de templating : Thymeleaf

Nécessite :
```HTML
<html xmlns:th="http://www.thymeleaf.org">
```
La documentation de Thymeleaf sur [thymeleaf.org](https://www.thymeleaf.org/doc/thymeleaf-spring6) (version 3.1.5, compatible Spring 6)

- **inline** `__${...}__` : Préprocesseur. Indique à Thymeleaf que cette portion doit être prétraitée. C'est utilisé pour des expressions à l'intérieur d'une autre expression plus globale.
- **inline** `|...|` : Literal substitution. Permet d'écrire une chaîne contenant des parties à évaluer, afin de simplifier l'écriture et éviter des concaténations de chaînes.
- **inline html** `[[...]]` : Literal substitution. Permet d'écrire une chaîne contenant du texte dynamique dans le html directement (`[(...)]` pour l'équivalent du `th:utext`). Il faut un `th:inline` dans un des tags parents du contenu.
- **prefix** `th:` : Ce préfixe indique que Thymeleaf doit interpréter l'attribut qui suit. Cela permet de faire du Thymeleaf sur des attributs HTML standards. Sur les tags, cela correspond au namespace des tags spécifiques Thymeleaf.
- `abc?:bcd` : Souvent utilisé pour simplifier l'écriture, équivalent de `abc != null ? abc : bcd`
- `${...}` : Évalue une expression de variable. Ex : `${name}` ou `${user.name}`
- `@{...}` : Reconstruit l'url d'un lien.
- `#{...}` : Référence une ressource i18n.
- `~{abc::bcd}` : Sélectionne un fragment. La syntaxe est `~{ path/to/the/template.html :: fragmentSelector}`. Le sélecteur est soit le nom d'un fragment, soit un sélecteur javascript standard (`#id`, `.class`, ...)
- `th:if` : Donne la condition d'affichage sur un tag (et son body). Le filtre est effectué côté serveur et convient pour la sécurité.
- `th:with="var1=${...}, var2=${...}"` : Déclare des variables locales. La portée est le contenu du tag, même hors du fichier : lorsqu'on inclut d'autres fragments la variable reste accessible.
- `th:attr="var1=${...}, var2=${...}"` : Déclare des variables globales. À utiliser avec attention.
- `th:text` : Évalue le contenu de l'attribut et l'ajoute dans le body du tag.
- `th:each="abc : bcd"` : Permet de créer une boucle sur le tag qui le porte. Boucle sur `bcd`, élément courant dans la variable `abc`.
- `th:include="abc::bcd"` : Composant de base du templating Thymeleaf. Le body du tag du template est recopié dans le tag portant l'attribut, le tag du template est perdu. La syntaxe est la même que pour le sélecteur de fragment `~{abc::bcd}`.
- `th:replace="abc::bcd"` : Composant du templating Thymeleaf. Le tag portant l'attribut est remplacé par celui du template. La syntaxe est la même que pour le sélecteur de fragment `~{abc::bcd}`.
- `th:remove="*mode*"` : Retire des tags du DOM, en fonction du mode. Les modes les plus courants sont :
  - `all` retire le tag et ses enfants
  - `tag` retire le tag et conserve ses enfants
- `th:fragment="fragName"` : Composant de base du templating Thymeleaf. Utilisé pour nommer un template réutilisable.


## Moteur de layout : Thymeleaf Layout

La documentation de Thymeleaf Layout sur [thymeleaf-layout-dialect](https://ultraq.github.io/thymeleaf-layout-dialect/)

Nécessite :
```HTML
<html xmlns:layout="http://www.ultraq.net.nz/thymeleaf/layout">
```

- `<head>` :  Les attributs du `<head>` sont automatiquement fusionnés entre la page et son layout. Certains sont surchargés (comme `<title>`), d'autres concaténés (comme les `<script>`).
- `layout:decorate` : Ajouté sur le tag `<html>` du contenu, il permet de préciser quel layout ce contenu utilise (il le *décore*).
- `layout:fragment` : Ajouté sur les tags internes du contenu, il permet d'indiquer dans quel fragment du layout est posé ce contenu spécifique.

> Les layouts peuvent hériter d'autres layouts.

Les layouts permettent de mutualiser toute la partie récurrente des pages : bandeau, menu, footer, ...
Le principe est qu'un layout est une page *à trou*, les trous sont nommés dans le template et peuvent avoir une valeur par défaut. Lorsque l'on écrit une page, on indique que l'on *décore* un layout particulier, et on ne précise que la valeur des *trous*. Le but étant que les éléments écrits dans la page ne sont que les éléments spécifiques à cette page, tout le contenu commun est dans le layout.
Le webapp d'une application Vertigo courante est sur le classpath : les templates — un layout de base (bandeau, menu, footer) que chaque page viendra décorer — sont typiquement dans `src/main/resources/<packageRoot>/webapp/WEB-INF/views/templates`.


## Composants nommés Vertigo-UI

Les composants Vertigo-UI utilisent le templating Thymeleaf, chaque composant est en fait un `th:replace` avec un peu d'intelligence complémentaire.
Le principe (et le code) est repris de [thymeleaf-component-dialect](https://github.com/Serbroda/thymeleaf-component-dialect)

Les composants Vertigo-UI sont des fragments Thymeleaf, ils sont évalués côté serveur et plusieurs d'entre eux encapsulent ainsi un composant VueJS ou quasar.
Vertigo-UI n'a pas vocation à encapsuler ainsi tous les composants d'ihm, la stratégie sur les composants Vertigo-UI est étudiée en fonction des points suivants :

- le composant est un composant de haut-niveau représentant un composant logique. Sous jacent il y aura plusieurs composants d'ihm, un comportement enrichi, des choix ergonomiques adaptés à notre contexte.
- le composant nécessite des interactions particulières avec le contexte. Par exemple pour sélectionner les données à intégrer dans vueData, et parfois pour les encoder de manière spécifique.
- le composant propose une API plus ergonomique, plus adaptée ou moins verbeuse pour le développeur

Nécessite :
```HTML
<html xmlns:vu="http://www.morphbit.com/thymeleaf/component">
```

### Paramètres de composant
- `abc_slot` : Permet de récupérer un `vu:slot` dans le body du tag appelant et de le placer dans le composant (Ex: `vu:table`)
- `abc_attrs` : Agrégation de tous les paramètres préfixés par `abc_` passés lors de l'appel du composant. Ex: sur `vu:table` on peut passer l'attribut `tr_class`, le paramètre `class` (avec sa valeur) sera récupéré dans le composant par le paramètre `tr_attrs` pour le placer sur le tag `tr` interne. *Évite de prévoir tous les cas lors de la conception du composant.*
- `other_attrs` : Agrégation de tous les paramètres non identifiés comme paramètre du composant, et permet de déterminer où ils doivent être placés. (Ex: dans le composant `vu:text-field`, les attributs non identifiés comme paramètre sont placés sur le `q-input` interne, par exemple `<vu:text-field round>` donnera `<q-input round>`)
- `contentTags` : Paramètre particulier récupérant les tags dans le body du composant lors de l'appel, sous forme de liste de `contentItem`. Ce cas est assez rare, habituellement on utilise plutôt `<vu:content>` qui place tout le body. `contentItem` permet de tester les tags pour faire un traitement spécifique (Ex: `grid` place les tags dans des blocs et `vu:grid-cell` possède un comportement particulier)

### Composants Vertigo-UI : layout
- `vu:page` : Composant obligatoire encadrant la zone sur laquelle VueJS est actif.
  - `content` : Le body du tag est conservé
  - `vuiSsr` : **boolean** (défaut `false`). Si `true`, active le Server Side Rendering : le contenu de la page est posé dans un tag `<vertigo-ssr>` qui est remplacé par le rendu, le template Vue étant pré-compilé côté serveur par `VuejsSsrFilter` (conforme CSP). Si `false` : rendu classique côté client
- `vu:head` : Pose le tag head et les méta du head html
  - `title`* : Titre de la page
  - `content` : Le body du tag est conservé
  - `vueJsVersion` : Version du VueJS chargé (défaut `3.5.39`)
  - `axiosVersion` : Version de la librairie JS Axios chargée (défaut `1.18.1`)
  - `vuejsDevMode` : **boolean** (défaut `false`) : passe VueJS en mode dev — charge les builds non minifiés (`vue.global.js` au lieu de `vue.global.prod.js`, et `quasar.umd.js` au lieu de `quasar.umd.prod.js`) *(nous avons noté des bugs sur VueJS dans quelques cas qui n'apparaissent qu'en devMode)*
  - `vuiDevMode` : **boolean** (défaut `false`) : active le mode développeur pour les composants Vertigo-UI (il faut un serveur de dev Vite — `npm run dev`, port 3000 — qui distribue les modules source transformés à la volée)
  - `vuiSsr` : **boolean** (défaut `false`) : Active le mode Server Side Rendering (le serveur Node.js est optionnel ; à défaut, la pré-compilation du template est assurée par le moteur Nashorn embarqué — `vue-template-compiler` browser.js) — charge `vertigo-ui-mpa-ssr.js` au lieu de `vertigo-ui-mpa.js`
  - `vertigoUiVersion` : Version de Vertigo-UI, utilisée en cache-buster `?v=` sur les assets locaux (vertigo-ui.css, vertigo-ui.umd.js, vertigo-ui-mpa, wysiwyg, DSFR) (défaut `4.4.1`)
  - `useQuasar` : **boolean** (défaut `true`) : charge Quasar (CSS, script UMD, locale)
  - `quasarVersion` : Version du Quasar chargé (défaut `2.21.1`)
  - `robotoVersion` : Version de la police Roboto chargée (défaut `51` ; la valeur `null` ne charge pas Roboto)
  - `fontAwesomeVersion` : Version de Font Awesome chargée (défaut `6.7.2` ; la valeur `null` ne charge pas Font Awesome)
  - `useDsfr` : **boolean** (défaut `false`) : charge le thème DSFR (`vertigo-dsfr.css` + `dsfr.umd.js`)
  - `useWysiwyg` : **boolean** : charge les assets de l'éditeur Vertigo-Wysiwyg (tiptap) — `vertigo-wysiwyg.css` + `vertigo-wysiwyg.umd.js` ; non chargé si non précisé
  - `additional_defer_libs_slot` : Slot pour injecter des scripts supplémentaires (deferred), posés après Quasar et avant l'UMD Vertigo-UI
- `vu:head-meta` : Composant obligatoire posant les éléments **méta** du head (script js, css, ...)
  - `vueJsVersion` : Version du VueJS chargé (défaut `3.5.39`)
  - `axiosVersion` : Version de la librairie JS Axios chargée (défaut `1.18.1`)
  - `vuejsDevMode` : **boolean** (défaut `false`) : passe VueJS en mode dev — charge les builds non minifiés (`vue.global.js` au lieu de `vue.global.prod.js`, et `quasar.umd.js` au lieu de `quasar.umd.prod.js`) *(nous avons noté des bugs sur VueJS dans quelques cas qui n'apparaissent qu'en devMode)*
  - `vuiDevMode` : **boolean** (défaut `false`) : active le mode développeur pour les composants Vertigo-UI (il faut un serveur de dev Vite — `npm run dev`, port 3000 — qui distribue les modules source transformés à la volée)
  - `vuiSsr` : **boolean** (défaut `false`) : Active le mode Server Side Rendering — charge `vertigo-ui-mpa-ssr.js` au lieu de `vertigo-ui-mpa.js`
  - `vertigoUiVersion` : Version de Vertigo-UI, utilisée en cache-buster `?v=` sur les assets locaux (vertigo-ui.css, vertigo-ui.umd.js, vertigo-ui-mpa, wysiwyg, DSFR) (défaut `4.4.1`)
  - `useQuasar` : **boolean** (défaut `true`) : charge Quasar (CSS, script UMD, locale)
  - `quasarVersion` : Version du Quasar chargé (défaut `2.21.1`)
  - `onlyDsfrStyle` : **boolean** (défaut `false`) : masque tous les CSS 3rd-party non-DSFR (Roboto, Material Icons, Font Awesome, Ionicons, Material Design Icons, Animate.css) ainsi que le CSS Quasar (les scripts JS Quasar restent chargés)
  - `robotoVersion` : Version de la police Roboto chargée (défaut `51` ; la valeur `null` ne charge pas Roboto) — non chargé si `onlyDsfrStyle`
  - `fontAwesomeVersion` : Version de Font Awesome chargée (défaut `6.7.2` ; la valeur `null` ne charge pas Font Awesome) — non chargé si `onlyDsfrStyle`
  - `useDsfr` : **boolean** (défaut `false`) : charge le thème DSFR (`vertigo-dsfr.css` + `dsfr.umd.js`)
  - `useWysiwyg` : **boolean** : charge les assets de l'éditeur Vertigo-Wysiwyg (tiptap) — `vertigo-wysiwyg.css` + `vertigo-wysiwyg.umd.js` ; non chargé si non précisé
  - `additional_defer_libs_slot` : Slot pour injecter des scripts supplémentaires (deferred), posés après Quasar et avant l'UMD Vertigo-UI
  <!-- source : head.html:1-89 — params exhaustifs extraits du fragment -->
- `vu:form` : Pose un formulaire et référence le contexte de page associé
  - `content` : Le body du tag est conservé
  - `other_attrs` : Liste des attributs à ajouter sur le formulaire (tag `<form>`)
- `vu:block` : Composant de block (visible graphiquement), représenté sous forme de card
  - `title` : Titre du block
  - `subtitle` : Sous titre du block
  - `icon` : Icône du block
  - `withFab` **boolean** : Ajoute la classe `withFab` si nécessaire
  - `actions_slot` : Slot pour positionner des actions sur le block *(remplace l'icône)*
  - `header_attrs` : Liste des attributs à ajouter sur le header du block (tag `<div>`)
  - `content_attrs` : Liste des attributs à ajouter sur le corps du block (tag `<div class="q-card-section">`)
  - `card_attrs` : Liste des attributs à ajouter sur le parent du block (tag `<div class="q-card">`)
  - `content` : Le body du tag est conservé
- `vu:grid` : Déclare une mise en page de grille
  - `cols` : Nombre de colonnes. Par défaut : 2
  - `dense` : Applique un mode *dense* réduisant la taille des gutters
  - `contentTags` : Le contenu du tag est conservé. Chaque élément est posé dans un `<div>` avec la largeur attendue. (on force une seule colonne sous le breakpoint **xs**)
- `vu:grid-cell` : Déclare une cellule spécifique d'une **grid**
  - `col` : Nombre de colonnes de la cellule
  - `class` : Classe CSS de la cellule  
  - `div_attrs` : Liste des attributs à ajouter sur le corps de la cellule (tag `<div>`)
  - `content` : Le body du tag est conservé  
- `vu:messages` : Composant ajoutant la liste des messages globaux issus d'un traitement qui ont été ajoutés dans le contexte (**uiMessageStack** avec Errors, Warnings, Info et Success)  
- `vu:modal` : Pose le conteneur de modal, pouvant être utilisé ensuite dans l'écran.
  - `componentId` : Nom du composant, utilisé pour cibler la modale en Js
  - `title` : Titre de la modale
  - `closeLabel` : Libellé de la fermeture de la modale
  - `srcUrl` : Url de la modale (optionnelle, habituellement passée par le script d'ouverture)  
  - `iframe_attrs` : Liste des attributs à ajouter sur l'iframe
  - `modal_attrs` : Liste des attributs à ajouter sur la modale (tag `<q-dialog>`)

!> `componentStates` est réinitialisé à chaque requête (`new ComponentStates()` dans `prepareContext`/`preInitContext`). Les états des composants ne persistent plus entre requêtes : `opened = false` dans un callback AJAX fonctionne car tout reste côté client.

Exemple d'utilisation d'une modale :
```HTML
  <q-btn round icon="edit" label="View detail" th:@click="|openModal('dossierDetailModal', '@{/projet/dossier/}' + props.row.dossierId , {'successCallback' : 'onDossierSuccess' })|"></q-btn>

  <vu:modal componentId="dossierDetailModal" title="Dossier" iframe_width="800" iframe_height="400"  />
      
  <script type="text/javascript">
    function onDossierSuccess() {
      VUiPage.$data.componentStates.dossierDetailModal.opened = false;
      VUiPage.httpPostAjax("[[@{/projet/dossier/_reloadDossiers}]]", {});
    }
  </script>
```

- `vu:content` : Tag utilisé dans les composants pour marquer l'insertion du `content` (ie : le body du tag lors de l'utilisation de ce composant). Le body peut être utilisé pour définir le rendu par défaut.
- `vu:content-item` : Tag utilisé dans les composants pour marquer l'insertion du `contentItem`. Utilisé dans les cas particuliers où les composants placés dans le corps d'un autre composant doivent être interprétés séparément. Le cas d'exemple est le composant `grid`. Pour être utilisé correctement, il faut que le composant parent ait un attribut contentTags, pose une boucle dessus avec pour nom d'item `contentItem`. (cf. [grid](https://raw.githubusercontent.com/vertigo-io/vertigo-libs/master/vertigo-ui/src/main/resources/io/vertigo/ui/components/quasar/layout/grid.html) )
- `vu:slot` *tag* : Composant permettant de passer le contenu d'un slot au composant parent. Les slots du composant parent sont référencés par le suffixe `_slot`.
  - `name` : Nom du slot
  - `content` : Le body du tag est passé au composant parent et sera inséré soit avec l'attribut `vu:slot` soit le tag `<vu:content-slot />`  
- `vu:slot` *attribute* : Attribut utilisé dans les composants pour marquer l'insertion du slot. Le tag est conservé. Équivalent d'un `th:include="${my_slot}"`.
  - `value` : Nom du slot (Ex: `vu:slot="top_left_slot"`)
- `vu:content-slot` : Tag utilisé dans les composants pour marquer l'insertion du `slot`. Ce tag est remplacé par le slot. Le body peut être utilisé pour définir le rendu par défaut.
  - `name` : Nom du slot

### Composants Vertigo-UI : utils

Ces composants sont des composants techniques.
Les composants `include-data-*` ont tous le même rôle : ils indiquent au serveur de transférer une donnée du contexte serveur (`CTX`) dans le contexte Vue (objet `vueData`).
Cette stratégie permet d'assurer que seules les données utiles sont poussées côté client. La plupart du temps ils ne sont pas utilisés directement, car ils sont posés par les composants `inputs` qui en ont besoin.
Ils restent utiles pour ajouter précisément des données dans le `vueData`, pour des composants vue spécifiques par exemple.

- `vu:include-data` : Inclut le champ d'un objet
  - `object` : Nom de l'objet du contexte
  - `field` : Nom du champ
  - `modifiable` : Indique que le champ est modifiable côté client et peut être renvoyé au serveur
  - `modifiableAllLines` : Indique que toutes les lignes sont modifiables
- `vu:include-data-primitive` : Inclut une donnée primitive du contexte
  - `key` : Clé de la donnée
  - `modifiable` : Indique que le champ est modifiable côté client et peut être renvoyé au serveur
- `vu:include-data-map` : Inclut le champ d'un objet et applique une dénormalisation sur sa valeur (traduit un id en libellé par exemple)
  - `object` : Nom de l'objet du contexte
  - `field` : Nom du champ
  - `list` : Liste du mapping à appliquer
  - `listKey` : Champ clé de la liste du mapping
  - `listDisplay` : Champ libellé de la liste du mapping
- `vu:include-data-protected` : Inclut le champ d'un objet. La valeur posée côté client est protégée (non en clair et non modifiable), la valeur réelle reste côté serveur. Ce système est utilisé pour les identifiants de fichier par exemple.
  - `object` : Nom de l'objet du contexte
  - `field` : Nom du champ
- `vu:utext` : Tag.processor appliquant `th:utext` **et** `v-pre` automatiquement. Permet d'afficher du HTML dynamique au contenu non-trusté en protégeant contre les injections XSS VueJS. Le `v-pre` empêche VueJS de compiler le contenu injecté.
  - `content` : Contenu HTML traité par le tag processor
- `vu:vue-data` : Pose les données de vue pour VueJS. **Ne doit pas être utilisé directement**, il est posé par `vu:page`


### Composants Vertigo-UI : inputs

Ces composants sont les composants principaux de construction des formulaires des applications.
Pour simplifier l'écriture des écrans, la plupart gèrent le `viewMode` afin de proposer un rendu dépendant du mode **Edit** ou du mode **ReadOnly**.
Les composants en **Edit** gèrent également nativement les messages d'erreurs issus des contrôles de validation.

- `vu:label` : Composant label
  - `object`* : Nom de l'objet du contexte
  - `field`* : Nom du champ
  - `label` : Surcharge du label
  - `other_attrs` : Liste des attributs à ajouter sur le label (tag `<q-field>`)
- `vu:text-field` : Composant champ de texte
  - `object`* : Nom de l'objet du contexte
  - `field`* : Nom du champ
  - `label` : Surcharge du label
  - `suffix` : Surcharge du suffixe
  - `label_attrs` : Liste des attributs à ajouter sur le label (tag `<q-field>`)
  - `input_attrs` : Liste des attributs à ajouter sur le champ de saisie (tag `<q-input>`)
- `vu:text-area` : Composant zone de texte
  - `object`* : Nom de l'objet du contexte
  - `field`* : Nom du champ
  - `label` : Surcharge du label
  - `label_attrs` : Liste des attributs à ajouter sur le label (tag `<q-field>`)
  - `input_attrs` : Liste des attributs à ajouter sur le champ de saisie (tag `<q-input>`)
- `vu:autocomplete` : Composant d'auto-complétion : choix dans une liste à partir du libellé, qui affecte la valeur au champ
  - `object`* : Nom de l'objet du contexte
  - `field`* : Nom du champ
  - `label` : Surcharge du label
  - `list`* : Nom de la liste du contexte
  - `valueField` : Nom du champ de la liste utilisée comme valeur, à affecter dans l'objet
  - `labelField` : Nom du champ de la liste utilisée comme label
  - `componentId` : id du composant VueJS
  - `label_attrs` : Liste des attributs à ajouter sur le label (tag `<q-field>`)
  - `input_attrs` : Liste des attributs à ajouter sur le champ de saisie (tag `<q-select>`)
- `vu:checkbox` : Composant case à cocher
  - `object`* : Nom de l'objet du contexte
  - `field`* : Nom du champ
  - `label` : Surcharge du label
  - `label_attrs` : Liste des attributs à ajouter sur le label (tag `<q-field>`)
  - `input_attrs` : Liste des attributs à ajouter sur le champ de saisie (tag `<q-checkbox>`)  
- `vu:select` : Composant de sélection par une combobox
  - `object`* : Nom de l'objet du contexte
  - `field`* : Nom du champ
  - `label` : Surcharge du label
  - `list`* : Nom de la liste du contexte
  - `valueField` : Nom du champ de la liste utilisée comme valeur, à affecter dans l'objet
  - `labelField` : Nom du champ de la liste utilisée comme label
  - `label_attrs` : Liste des attributs à ajouter sur le label (tag `<q-field>`)
  - `input_attrs` : Liste des attributs à ajouter sur le champ de saisie (tag `<q-select>`)
- `vu:select-multiple` : Composant de sélection multiple par une combobox
  - `object`* : Nom de l'objet du contexte
  - `field`* : Nom du champ
  - `label` : Surcharge du label
  - `list`* : Nom de la liste du contexte
  - `valueField` : Nom du champ de la liste utilisée comme valeur, à affecter dans l'objet
  - `labelField` : Nom du champ de la liste utilisée comme label
  - `label_attrs` : Liste des attributs à ajouter sur le label (tag `<q-field>`)
  - `input_attrs` : Liste des attributs à ajouter sur le champ de saisie (tag `<q-select>`)
- `vu:radio` : Composant de sélection par une liste de boutons radio
  - `object`* : Nom de l'objet du contexte
  - `field`* : Nom du champ
  - `label` : Surcharge du label
  - `list`* : Nom de la liste du contexte
  - `valueField` : Nom du champ de la liste utilisée comme valeur, à affecter dans l'objet
  - `labelField` : Nom du champ de la liste utilisée comme label
  - `layout` : Mise en forme du radio : `horizontal` ou `vertical`
  - `label_attrs` : Liste des attributs à ajouter sur le label (tag `<q-field>`)
  - `input_attrs` : Liste des attributs à ajouter sur le champ de saisie (tag `<q-radio>`)
- `vu:date` : Composant de sélection de date
  - `object`* : Nom de l'objet du contexte
  - `field`* : Nom du champ
  - `label` : Surcharge du label
  - `format` : Format d'affichage de la date (par défaut `DD/MM/YYYY`). La valeur est toujours stockée et échangée en ISO `YYYY-MM-DD`.
  - `date_attrs` : Liste des attributs à ajouter sur la date (tag `<q-date>`)
  - `input_attrs` : Liste des attributs à ajouter sur le champ de saisie (tag `<q-input>`)
- `vu:datetime` : Composant de sélection de date/time
  - `object`* : Nom de l'objet du contexte
  - `field`* : Nom du champ
  - `label` : Surcharge du label
  - `format` : Format d'affichage de la date/heure (par défaut `DD/MM/YYYY HH:mm`). La valeur est toujours stockée et échangée en ISO `YYYY-MM-DDTHH:mm`.
  - `date_attrs` : Liste des attributs à ajouter sur la date (tag `<q-date>`)
  - `time_attrs` : Liste des attributs à ajouter sur l'heure (tag `<q-time>`)
  - `input_attrs` : Liste des attributs à ajouter sur le champ de saisie (tag `<q-input>`)
- `vu:knob` : Composant graphique de modification de valeur numérique
  - `object`* : Nom de l'objet du contexte
  - `field`* : Nom du champ
  - `label` : Surcharge du label
  - `min` : Valeur minimum
  - `max` : Valeur maximum
  - `step` : Pas des modifications de la valeur
  - `label_attrs` : Liste des attributs à ajouter sur le label (tag `<q-field>`)
  - `input_attrs` : Liste des attributs à ajouter sur le champ de saisie (tag `<q-knob>`)
- `vu:slider` : Composant graphique de modification de valeur numérique
  - `object`* : Nom de l'objet du contexte
  - `field`* : Nom du champ
  - `label` : Surcharge du label
  - `min` : Valeur minimum
  - `max` : Valeur maximum
  - `step` : Pas des modifications de la valeur
  - `label_attrs` : Liste des attributs à ajouter sur le label (tag `<q-field>`)
  - `input_attrs` : Liste des attributs à ajouter sur le champ de saisie (tag `<q-slider>`)
- `vu:chips-autocomplete` : Composant d'ajout d'une liste de tags par auto-complétion
  - `object`* : Nom de l'objet du contexte
  - `field`* : Nom du champ
  - `label` : Surcharge du label
  - `list`* : Nom de la liste du contexte
  - `valueField` : Nom du champ de la liste utilisée comme valeur, à affecter dans l'objet
  - `labelField` : Nom du champ de la liste utilisée comme label
  - `componentId` : id du composant VueJS
  - `staticData` : Indique si les données sont statiques (ou issues d'un WebService `@{/autocomplete/_searchFullText}`)
  - `label_attrs` : Liste des attributs à ajouter sur le label (tag `<q-field>`)
  - `input_attrs` : Liste des attributs à ajouter sur le champ de saisie (tag `<q-select>`)
- `vu:fileupload` : Composant d'ajout de fichier (contrairement aux autres composants de saisie, l'id du fichier n'est pas stocké dans un objet métier)
  - `url`* : Url du WebService d'upload
  - `key`* : Clé du contexte réceptionnant les fichiers
  - `multiple` : Indique si on autorise plusieurs fichiers
  - `maxFileSize` : Taille maximum par fichier en MB (ex: `5`)
  - `maxTotalSize` : Taille maximum totale de tous les fichiers
  - `maxFiles` : Nombre maximum de fichiers autorisés
  - `accept` : Filtre MIME des fichiers acceptés (ex: `"image/*,.pdf"`)
  - `uploader_attrs` : Liste des attributs à ajouter sur le composant upload (tag `v-file-upload-quasar`)
- `vu:fileupload-dropzone` : Zone de dépôt de fichiers par glisser-déposer
  - `fileComponentId`* : Identifiant obligatoire liant la zone de dépôt au composant d'upload correspondant

> Pour adapter leur rendu ces composants utilisent des mécanismes particuliers.
> Globalement un composant **Vertigo-UI : inputs** s'écrit ainsi :

```XML
<th:block th:fragment="label-edit(object,field, label, other_attrs)" vu:alias="label" vu:selector="${viewMode=='edit'}" >
  <vu:content/>
</th:block> 

<th:block th:fragment="label-read(object, field, label, other_attrs)" vu:alias="label" vu:selector="${viewMode=='read'}" >
  <vu:content/>
</th:block> 
```

> - Le `th:fragment` nomme le composant particulier et ses paramètres.
> - le `vu:alias` nomme l'alias du composant, c'est souvent ce nom qui est utilisé dans les pages
> - le `vu:selector` est une expression qui est évaluée dans le contexte du composant et permet de sélectionner le fragment à utiliser lorsque l'on utilise l'alias
> - les fragments `-edit`/`-read` (ex. `vu:select-edit`, `vu:select-read`, `vu:text-field-read`) peuvent être appelés directement pour forcer le mode de rendu sans dépendre de `viewMode`


### Composants Vertigo-UI : collections
- `vu:cards` : Génère une liste de card. Lors du rendu d'une card, vous pouvez utiliser l'attribut VueJS `item` pour récupérer l'objet courant.
- `vu:collection`
- `vu:field-read`
- `vu:list`
- `vu:search`
- `vu:facets`


### Composants Vertigo-UI : tables
- `vu:table` : Génère un tableau. Lors du rendu d'une ligne, vous pouvez utiliser l'attribut VueJS `props.row` pour récupérer l'objet courant.
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
- `vu:column`
  - list
  - field
  - name
  - label
  - align
  - sortable
  - class
  - td_attrs

### Composants Vertigo-UI : buttons
- `vu:button` : Pose un bouton d'action (tag `<q-btn>`), dont le comportement (ex. `@click`) est porté par les attributs passés — complément de `vu:button-link` (url) et `vu:button-submit` (formulaire)
   - label : libellé du bouton
   - icon : icône du bouton
   - color : couleur du bouton (par défaut `primary`)
   - text-color : couleur du texte du bouton
   - title : libellé pour l'accessibilité
   - v-title : libellé pour l'accessibilité (variante réactive VueJS)
   - other_attrs : tous autres attributs. Posés sur le `<q-btn>`
- `vu:button-confirm` : Pose un bouton d'action avec une popin de confirmation (tag `<q-btn>` ouvrant un `q-dialog`)
   - actions_slot : slot des boutons d'annulation et de confirmation
   - key : clé d'instance de la popin (suffixe du ref interne, défaut `props?.rowIndex`)
   - label : libellé du bouton
   - icon : icône du bouton
   - color : couleur du bouton (par défaut `primary`)
   - text-color : couleur du texte du bouton
   - title : libellé pour l'accessibilité
   - v-title : libellé pour l'accessibilité (variante réactive VueJS)
   - confirmMessage : message de confirmation
   - labelOk : libellé du bouton OK (par défaut Oui)
   - labelCancel : libellé du bouton annuler (par défaut Non)
   - ok_attrs : tous autres attributs. Posés sur le bouton OK de la confirmation
   - other_attrs : tous autres attributs. Posés sur le `<q-btn>` (pas sur le bouton interne de confirmation)
- `vu:button-link` : Pose un bouton de type lien (tag `<q-btn type="a">`)
   - label : libellé du bouton
   - icon : icône du bouton
   - url : url du lien
   - title : libellé pour l'accessibilité
   - disabled : **boolean** si le bouton est désactivé
   - other_attrs : tous autres attributs. Posés sur le `<q-btn>`
- `vu:button-link-confirm` : Pose un bouton de type lien avec une popin de confirmation (tag `<q-btn type="a">`)
   - actions_slot : slot des boutons d'annulation et de confirmation
   - label : libellé du bouton
   - icon : icône du bouton
   - url : url du lien
   - title : libellé pour l'accessibilité
   - disabled : **boolean** si le bouton est désactivé
   - confirmMessage : Message de confirmation
   - labelOk : libellé du bouton OK (par défaut Oui)
   - labelCancel : libellé du bouton annuler (par défaut Non)
   - other_attrs : tous autres attributs. Posés sur le `<q-btn>` (pas sur le bouton interne de confirmation)
- `vu:button-submit` : Pose un bouton de type submit (tag `<q-btn type="submit">`)
   - label : libellé du bouton
   - icon : icône du bouton
   - action : nom de l'action associée
   - title : libellé pour l'accessibilité
   - other_attrs : tous autres attributs. Posés sur le `<q-btn>`

- `vu:button-submit-confirm` : Pose un bouton de type submit (tag `<q-btn type="submit">`)
   - actions_slot : slot des boutons d'annulation et de confirmation
   - label : libellé du bouton
   - icon : icône du bouton
   - action* : nom de l'action associée
   - title : libellé pour l'accessibilité
   - formId* : identifiant du formulaire (nécessaire car la popin est hors du formulaire)
   - confirmMessage : Message de confirmation
   - labelOk : libellé du bouton OK (par défaut Oui)
   - labelCancel : libellé du bouton annuler (par défaut Non)
   - other_attrs : tous autres attributs. Posés sur le `<q-btn>` (pas sur le bouton interne de confirmation)


## Composants VueJS Vertigo-UI

- `vueData`
- `v-notifications`
- `v-comments`
- `v-scroll-spy`
- `v-json-editor`
- `v-chatbot`

## Pour les experts

### Managers & Configuration

Le module vertigo-ui ne dispose pas de `XxxFeatures.java` dédié. Les composants UI sont activés par la classe de Features applicative, qui étend la classe abstraite `DefaultUiModuleFeatures`. L'activation UI (ajout du `VSpringMvcConfigDefinitionProvider` avec les paramètres `name`, `packages` et `componentDirs`, dont les valeurs sont dérivées du package racine du module applicatif (aucun paramètre à fournir manuellement)) est déclenchée par l'appel `addUi()`, effectué par le `buildFeatures()` **hérité** de `DefaultUiModuleFeatures` : en forme minimale, la classe applicative ne surcharge pas `buildFeatures()` ; si elle doit y ajouter ses propres providers, la surcharge DOIT commencer par `super.buildFeatures()` (sinon aucun DAO/Service/WebService du module n'est enregistré).

### ViewContext

`ViewContext` est l'objet central de la couche UI, représentant le contexte d'une page. Il permet de publier et lire des objets, listes et primitives entre le contrôleur et la vue.

| Méthode | Description |
|---|---|
| `publishDto` | Publie un objet formulaire (DtObject) dans le contexte |
| `readDto` | Lit et valide l'objet formulaire (lève `ValidationUserException` en cas d'erreur de validation) |
| `publishDtList` | Publie une liste (DtList) dans le contexte |
| `publishDtListModifiable` | Publie une liste modifiable |
| `publishMdl` | Publie une liste de référence (Master Data List) |
| `publishFacetedQueryResult` | Publie le résultat d'une recherche à facettes |
| `getUiObject` / `getUiList` | Récupère les données telles que reçues depuis l'IHM |
| `ViewContextMap` | Map typée pour accéder aux éléments du contexte via `ViewContextKey` |
| `ViewContextUpdateSecurity` | Contrôle la sécurité des mises à jour du contexte |

### Spring MVC

| Composant | Description |
|---|---|
| `VSpringWebConfig` | Configuration Spring MVC de base |
| `VSpringMvcConfigDefinition` | Définition de la configuration MVC |
| `AbstractVSpringMvcController` | Controller parent à étendre |
| `VSpringMvcControllerAdvice` | Gestion globale des exceptions et données partagées |
| `VSpringMvcExceptionHandler` | Gestionnaire d'exceptions centralisé |
| `VSpringMvcUiMessageStack` | Pile de messages UI pour le **rendu** des erreurs |
| `VRequestToViewNameTranslator` | Traduction des requêtes vers les noms de vues |
| `VertigoLocaleResolver` | Résolution de la locale par utilisateur |

#### Argument Resolvers

| Resolver | Type Supporté |
|---|---|
| `ViewContextReturnValueAndArgumentResolver` | `ViewContext` (lecture et retour) |
| `ViewAttributeMethodArgumentResolver` | Objets annotés `@ViewAttribute` |
| `UiMessageStackMethodArgumentResolver` | `UiMessageStack` |
| `UserSessionMethodArgumentResolver` | Session utilisateur |
| `DtListStateMethodArgumentResolver` | `DtListState` (tri, pagination) |
| `VFileMethodArgumentResolver` | `VFile` (avec `@QueryParam`) |
| `FileInfoURIConverter` | `FileInfoURI` (conversion URI protégée) |
| `VegaJsonHttpMessageConverter` | Conversion JSON Vega |

#### Return Value Handlers

| Handler | Type Retour |
|---|---|
| `VFileReturnValueHandler` | `VFile` |
| `UiFileInfoReturnValueHandler` | `UiFileInfo` |
| `FileInfoURIConverterValueHandler` | `FileInfoURI` |

#### Interceptors

| Interceptor | Priorité | Description |
|---|---|---|
| `VSpringMvcAuthorizationInterceptor` | — | Vérification `@Secured` sur les contrôleurs |
| `VSpringMvcViewContextInterceptor` | — | Initialisation du ViewContext |
| `VSpringMvcErrorInterceptor` | — | Interception et rendu des erreurs |
| `RateLimitingHandlerInterceptor` | — | Limitation de débit sur les requêtes MVC |
| `VAnnotationHandlerInterceptorImpl` | — | Interception basée sur `@VControllerInterceptor` |
| `VControllerInterceptorEngine` | — | Moteur d'exécution des intercepteurs |

### Thymeleaf

| Composant | Description |
|---|---|
| `VUiStandardDialect` | Dialecte Thymeleaf personnalisé (`vu:`) |
| `VuiResourceTemplateResolver` | Résolution de templates depuis classpath/webapp |
| `VSpringTemplateEngine` | Moteur de template Spring-thymeleaf configuré |

#### Composants `vu:` (dialecte Thymeleaf)

| Composant | Classe |
|---|---|
| `vu:named` | `NamedComponentDefinition`, `NamedComponentParser`, `NamedComponentElementProcessor` |
| `vu:content` | `ContentComponentProcessor` |
| `vu:content-item` | `ContentItemComponentProcessor` |
| `vu:content-slot` | `ContentSlotComponentProcessor` |
| `vu:slot` | `SlotComponentProcessor`, `SlotAttributeTagProcessor` |
| `vu:authz` | `AuthzAttributeTagProcessor` |
| `vu:once` | `OnceAttributeTagProcessor` |
| `vu:text` | `VuiTextTagProcessor` |
| Utilitaires | `FragmentUtil`, `ResourcePathFinder` |

!> **`vu:authz` en mode développement** : avec la variable de contexte `authz-dev`, les éléments non autorisés ne sont pas supprimés, ils sont affichés en état verrouillé. Cela permet de visualiser les autorisations (quels éléments sont masqués et pourquoi) et de tester la sécurité côté serveur en conditions de développement.

### UI Data Wrappers

| Classe | Description |
|---|---|
| `UiListUnmodifiable` | Liste en lecture seule |
| `BasicUiListModifiable` | Liste modifiable côté client |
| `UiMdList` | Liste de Master Data (référence) |
| `MapUiObject` | Objet UI sous forme de Map |
| `UiFileInfo` / `UiFileInfoList` | Informations fichier sécurisées |
| `ClusterUiList` | Liste pour l'affichage cluster |
| `UiSelectedFacetValues` | Facettes sélectionnées dans une recherche |
| `ComponentRef` / `ComponentStates` | Référence et état des composants Vue |
| `FormMode` | Mode de formulaire (edit/read) |
| `AjaxResponseBuilder` | Construction de réponses AJAX |
| `ProtectedValueUtil` / `FileInfoURIAdapter` | Encodage de valeurs protégées |

### Quasar Tree

| Classe | Description |
|---|---|
| `Tree` | Représentation d'un arbre |
| `TreeNode` / `TreeNodeData` | Nœud de l'arbre |
| `TreeBuilder` | Construction fluide d'arbres |
| `LevelContext` / `ListContext` | Contexte de rendu par niveau |

### Jetty Boot

| Classe | Description |
|---|---|
| `JettyBoot` | Démarrage du serveur Jetty embarqué |
| `JettyBootParams` | Paramètres de configuration de Jetty |
| `JettyBootParamsBuilder` | Construction des paramètres |
| `withSessionTimeoutMinutes` | Configure `setMaxInactiveInterval` sur la session HTTP (convertit minutes → secondes) |
| `KVSessionDataStoreFactory` | Fabricant de stockage de sessions Jetty |
| `KVSessionDataStore` | Stockage des sessions Jetty via KVStore |

### VueJS SSR

| Classe | Description |
|---|---|
| `VuejsSsrFilter` | Filtre Servlet pour le Server-Side Rendering VueJS |
| `VuejsSsrServletResponseWrapper` | Wrapper de la réponse HTTP SSR |
| `VuejsSsrResponseStream` | Flux de sortie du rendu SSR |
| `UnAutoCloseTagsFilter` | Filtre pour corriger les tags ouverts en double |

### Exceptions

| Exception | Description |
|---|---|
| `ExpiredViewContextException` | Lancée quand le ViewContext est expiré |

### Configuration YAML

`DefaultUiModuleFeatures` est une classe abstraite : c'est la classe de base que le module applicatif étend pour activer les composants UI. L'activation de l'UI ne passe par aucune clé YAML : cf. la section « Managers & Configuration » ci-dessus (première section de la partie « Pour les experts ») pour le mécanisme (`DefaultUiModuleFeatures`, `addUi()`, avertissement `super.buildFeatures()`).

```java
package io.mars.basemanagement;

import io.vertigo.ui.impl.springmvc.config.DefaultUiModuleFeatures;

public class BasemanagementFeatures extends DefaultUiModuleFeatures<BasemanagementFeatures> {

    public BasemanagementFeatures() {
        super("basemanagement");
    }
}
```

Le module applicatif est ensuite simplement déclaré dans la configuration YAML (aucune feature `ui` à activer) :

```yaml
modules:
  io.mars.basemanagement.BasemanagementFeatures:
    features:
      - auth:
```
