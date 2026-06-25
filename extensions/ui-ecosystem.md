# Écosystème UI Vertigo

L'écosystème UI de la plateforme Vertigo se compose de quatre bibliothèques qui s'intègrent au module [vertigo-ui](extensions/ui.md) principal. Chacune étend l'offre de composants VueJS disponibles pour les pages de l'application.

## Bibliothèque `vertigo-ui-vuejs` — Composants Vue 3 avancés

La bibliothèque de base (package `@vertigo-io/vertigo-ui-vuejs` v4.3.2) fournit des composants Vue 3 prêts à l'emploi, construits sur Quasar et OpenLayers.

Le plugin s'installe via `Vue.use(VertigoUi, { axios: ... })` et expose :
- 16 composants globaux (préfixe `v-`)
- 5 directives Vue (préfixe `v-`)
- Un objet global `$vui` avec des méthodes utilitaires
- Du support i18n (français, anglais)

Composants disponibles :

| Tag | Rôle | Props clés |
|-----|------|-----------|
| `v-facets` | Recherche full-text à facettes | `facets`, `selectedFacets`, `render` (`selects` \| `list`), `contextKey` |
| `v-comments` | Zone de commentaires | `concept`, `id`, `baseUrl`, `connectedAccount` |
| `v-notifications` | Bell de notifications | `baseUrl`, `targetUrlPrefix`, `icon`, `color` |
| `v-handles` | Recherche rapide par handles | `baseUrl` |
| `v-comments` | Zone de commentaires collaborative | `concept`, `id`, `baseUrl`, `connectedAccount` |
| `v-chatbot` | Interface chatbot conversationnelle | `botUrl`, `botAvatar`, `botName`, `devMode` |
| `v-commands` | Invite de commande (CLI-like) | `baseUrl` |
| `v-comments` | Échange de commentaires sur un concept métier | `concept`, `id`, `baseUrl`, `connectedAccount` |
| `v-extensions-store` | Grille des modules Vertigo activés | `activeSkills` (Array<String>) |
| `v-geopoint-input` | Saisie latitude/longitude | `modelValue` (Object) |
| `v-json-editor` | Édition JSON sous forme de champs | `modelValue` (String JSON), `readonly`, `cols` |
| `v-map` | Carte OpenLayers (tiles OSM) | `id`, `initialZoomLevel`, `initialCenter`, `search`, `overview` |
| `v-map-layer` | Calque de marqueurs sur `v-map` | `id`, `field`, `nameField`, `list`, `cluster`, `object`, `markerColor`, `clusterColor`, `clusterCircleSize` |
| `v-tree` | Sélecteur arborescent | `modelValue`, `list`, `keyField`, `labelField`, `parentKeyField`, `subTreeKey` |
| `v-file-upload` | Upload de fichiers multi | `inputId`, `accept`, `multiple`, `uploadUrl`, `downloadUrl`, `readonly` |
| `v-file-upload-quasar` | Variante Quasar de `v-file-upload` | Identique à `v-file-upload` |
| `v-dashboard-chart` | Graphique de dashboard | — (voir module dashboard) |

Directives Vue :

| Directive | Rôle | Valeur attendue |
|-----------|------|----------------|
| `v-autofocus` | Focus automatique sur un élément | Boolean |
| `v-scroll-spy` | Navigation active au scroll | `{ debug, startingOffset, fixedPos, scanner }` |
| `v-alert-unsaved-updates` | Alerte `beforeunload` si modifications non sauvegardées | `watchKeys` (String, CSV) |
| `v-if-unsaved-updates` | Affiche/masque l'élément selon les modifications non sauvegardées | — |
| `v-minify` | Header qui se minimise au scroll (maxi→mini) | `{ topOffset, leftOffset, scrollContainerEl }` |

### Principes

Les composants font des appels HTTP via l'instance `axios` fournie lors de l'installation du plugin (`Vue.use(VertigoUi, { axios: ... })`). Les données sont échangées avec le serveur via le contexte `ViewContext` (pattern `vContext[... ]`).

Le composant `v-map` utilise OpenLayers avec tuiles OSM par défaut. Le composant `v-map-layer` ajoute des marqueurs (et leur clustering) sur la map parente en écoutant l'objet `olMap` global.

## Bibliothèque `vertigo-ui-dsfr` — Design System français

La bibliothèque DSFR (package `vertigo-dsfr` v4.3.2) intégre le Design System de l'État français (`@gouvfr/dsfr` 1.12.1 + `@gouvminint/vue-dsfr` 8.6.0) au sein de Vertigo.

Elle installe le plugin `VueDsfr` (qui expose tous les composants DSFR standards), puis ajoute des composants personnalisés adaptés à l'usage Vertigo :

| Tag | Catégorie | Rôle |
|-----|-----------|------|
| `DsfrFacets` | Composant avancé | Adaptation du `v-facets` au thème DSFR (checkbox, boutons tertiaires, tags dismissibles) |
| `DsfrSelectMultiple` | Composant avancé | Select multiple DSFR natif |
| `DsfrMenu` | Composant avancé | Menu de navigation DSFR |
| `DsfrMenuLink` | Composant avancé | Lien de menu avec gestion des états actifs |
| `DsfrHeaderMenu` | Composant avancé | Menu déroulant dans le header |
| `DsfrCustomHeader` | Surcharge | Header DSFR personnalisé avec logo, service titre, menu burger |
| `DsfrCustomHeaderMenuLinks` | Surcharge | Liens du header |
| `DsfrCustomDataTable` | Surcharge | Tableau DSFR avec tri, pagination, sélection |
| `DsfrCustomCheckbox` | Surcharge | Checkbox DSFR avec label |
| `DsfrCustomSelect` | Surcharge | Select unique DSFR |
| `DsfrButtonTooltip` | Utilitaire | Bouton avec tooltip DSFR |
| `DsfrLinkTooltip` | Utilitaire | Lien avec tooltip DSFR |
| `DsfrLink` | Utilitaire | Lien stylisé DSFR avec flèche |
| `RouterLink` | Intégration | Pont entre DSFR et router Vue |
| `autocomplete` | Intégration | Composant autocomplete TrevorEyre pour recherche rapide |

Le plugin expose également un objet `DSFR.methods` avec des méthodes utilitaires et un objet `DSFR.utils` avec des utilitaires (ex: génération aléatoire).

### Intégration

Pour activer le thème DSFR, inclure le fichier CSS et JS DSFR compilé (build via `build-lib`) et installer le plugin Vue `DSFR` :

```js
Vue.use(VueDsfr)
Vue.use(DSFR)
```

Dans une application Vertigo, le thème DSFR est activé en utilisant les composants `<dsfr-*-html>` dans les templates Thymeleaf ou les composants Vue dans les pages Vue. Les projets **adesi**, **fgv-webapp** et **nova** utilisent cette intégration.

## Bibliothèque `vertigo-ui-wysiwyg` — Éditeur de texte enrichi

La bibliothèque WYSIWYG (package `vertigo-wysiwyg` v2.12.0) fournit un composant `<v-wysiwyg>` basé sur TipTap (v2.12.0) pour l'édition de texte enrichi.

| Tag | Rôle |
|-----|------|
| `v-wysiwyg` | Éditeur WYSIWYG (TipTap) |

Extensions TipTap activées :
- Formatage : **bold**, *italic*, underline, ~~strike~~, subscript, superscript
- Structure : heading, paragraph, bullet-list, ordered-list, list-item, horizontal-rule, blockquote, hard-break
- Contenu : link, text, gapcursor (clic dans les cellules vides)
- Contrôle : history (undo/redo), bubble-menu (menu contextuel flottant)
- Mise en page : text-align (left, center, right, justify)

Utilisation dans le module vertigo-ui : inclure le fichier `vertigo-wysiwyg.*.js` compilé et utiliser le tag `<vu:wysiwyg>` dans les templates Thymeleaf, ou `<v-wysiwyg>` dans les composants Vue.

## Bibliothèque `vertigo-ui-server-ssr` — Rendu côté serveur

La bibliothèque SSR (package `@vertigo-io/vertigo-ui-server-ssr` v3.5.0) permet le rendu côté serveur de composants VueJS dans une application Vertigo.

Basée sur Node.js avec Express et `vue-template-compiler`, elle fournit un serveur Express qui compile les templates Vue du côté serveur pour un premier rendu HTML (utile pour le SEO et le temps d'affichage initial).

Le fichier `index.js` expose un middleware Express qui :
1. Reçoit la requête HTML du serveur Java (Javalin/Spring)
2. Compile les templates Vue côté serveur
3. Retourne le HTML rendu avec les données injectées

### Intégration

En tant que dépendance Maven de l'application, le SSR est activé automatiquement par le module vertigo-ui. Aucune configuration manuelle n'est nécessaire dans la majorité des cas. Le serveur Node.js s'exécute en parallèle du serveur Java et communique via HTTP interne.

Le module vertigo-ui orchestre le rendu hybride : la structure HTML (Thymeleaf) est rendue côté serveur, puis les composants VueJS hydratent l'application côté client. Le SSR permet d'envoyer un premier rendu HTML complet au navigateur, réduisant le temps d'affichage perçu par l'utilisateur.

## Pour les experts

### Installation plugin vertigo-ui-vuejs

```js
import VertigoUi from 'vertigo-ui-vuejs'

Vue.createApp(App).use(VertigoUi, { axios: axiosInstance })
```

### Pipeline de build

Chaque bibliothèque utilise Vite pour compiler ses composants :

| Bibliothèque | Commande | Sortie |
|--------------|----------|--------|
| vertigo-ui-vuejs | `npm run build-lib` | `dist/vertigo-ui.*\` → `vertigo-ui/static/js/` |
| vertigo-ui-dsfr | `npm run build-lib` | `dist/*.*\` → `vertigo-ui/static/3rdParty/dsfr/` |
| vertigo-ui-wysiwyg | `npm run build-lib` | `dist/*.*\` → `vertigo-ui/static/js/wysiwyg/` |

### Dépendances externes par bibliothèque

| Bibliothèque | Dépendances critiques | Versions |
|-------------|----------------------|----------|
| vertigo-ui-vuejs | Quasar, Vue 3, OpenLayers, d3-color, lodash.debounce | Q 2.18.1, Vue 3.5.17, OL 10.6.1 |
| vertigo-ui-dsfr | DSFR, VueDSFR, Autocomplete-Trevor, Vue 3 | DSFR 1.12.1, VueDSFR 8.6.0 |
| vertigo-ui-wysiwyg | TipTap, Vue 3 | TipTap 2.12.0, Vue 3.5.13 |
| vertigo-ui-server-ssr | Express, vue-template-compiler | Express 4.17.2, VTC 2.7.14 |

### Configuration YAML vertigo-ui avec extensions

Les bibliothèques UI ne disposent pas de features YAML dédiées. Elles sont activées automatiquement quand le module `vertigo-ui` est inclus en dépendance Maven :

```yaml
io.vertigo.ui.UISpringWebFeatures:
    features:
        - ui:
```

L'intégration des bibliothèques se fait côté frontend (inclusion CSS/JS dans les templates Thymeleaf ou dans `head.html`). Le choix entre thème Quasar et thème DSFR se fait au niveau du template de base de l'application.

### Notes de migration

- Le composant `v-autocomplete` (hors `@trevoreyre/autocomplete`) fait partie de vertigo-ui (`<vu:autocomplete>`) et non de vertigo-ui-vuejs.
- Les directives `v-scroll-spy`, `v-minify` sont liées à la structure des pages et doivent être utilisées avec prudence (scroll global, événements window).
- Le paramètre `fitOnDataUpdate` de `v-map-layer` contrôle le redimensionnement automatique de la carte quand les données changent.
- Le composant `v-chatbot` nécessite un point d'entrée HTTP (`botUrl`) vers un service de chatbot compatible avec l'API définie dans le composant (format de message `{ text, sent, label, ... }`).
