# Vertigo UI Ecosystem

The Vertigo platform UI ecosystem consists of four libraries integrating with the main [vertigo-ui](/en/extensions/ui.md) module. Each extends the VueJS component offerings available for application pages.

## Library `vertigo-ui-vuejs` — Advanced Vue 3 Components

Base library (package `@vertigo-io/vertigo-ui-vuejs` v4.3.0) provides ready-to-use Vue 3 components built on Quasar and OpenLayers.

Plugin installs via `Vue.use(VertigoUi, { axios: ... })` and exposes:
- 15 global components (prefix `v-`)
- 5 Vue directives (prefix `v-`)
- Global `$vui` object with utility methods
- i18n support (French, English)

Available components:

| Tag | Role | Key Props |
|-----|------|-----------|
| `v-facets` | Full-text search with facets | `facets`, `selectedFacets`, `render` (`selects` \| `list`), `contextKey` |
| `v-comments` | Comments area | `concept`, `id`, `baseUrl`, `connectedAccount` |
| `v-notifications` | Notification bell | `baseUrl`, `targetUrlPrefix`, `icon`, `color` |
| `v-handles` | Quick search by handles | `baseUrl` |
| `v-chatbot` | Conversational chatbot interface | `botUrl`, `botAvatar`, `botName`, `devMode` |
| `v-commands` | Command prompt (CLI-like) | `baseUrl` |
| `v-extensions-store` | Grid of active Vertigo modules | `activeSkills` (Array<String>) |
| `v-geopoint-input` | Latitude/longitude input | `modelValue` (Object) |
| `v-json-editor` | JSON editing as fields | `modelValue` (String JSON), `readonly`, `cols` |
| `v-map` | OpenLayers map (OSM tiles) | `id`, `initialZoomLevel`, `initialCenter`, `search`, `overview` |
| `v-map-layer` | Marker layer on `v-map` | `id`, `field`, `nameField`, `list`, `cluster`, `object`, `markerColor`, `clusterColor`, `clusterCircleSize` |
| `v-tree` | Tree selector | `modelValue`, `list`, `keyField`, `labelField`, `parentKeyField`, `subTreeKey` |
| `v-file-upload` | Multi file upload | `inputId`, `accept`, `multiple`, `uploadUrl`, `downloadUrl`, `readonly` |
| `v-file-upload-quasar` | Quasar variant of `v-file-upload` | Same as `v-file-upload` |
| `v-dashboard-chart` | Dashboard chart | — (see dashboard module) |

Vue directives:

| Directive | Role | Expected Value |
|-----------|------|----------------|
| `v-autofocus` | Auto-focus on element | Boolean |
| `v-scroll-spy` | Active navigation on scroll | `{ debug, startingOffset, fixedPos, scanner }` |
| `v-alert-unsaved-updates` | `beforeunload` alert on unsaved changes | `watchKeys` (String, CSV) |
| `v-if-unsaved-updates` | Show/hide element based on unsaved changes | — |
| `v-minify` | Header that minimizes on scroll (max→min) | `{ topOffset, leftOffset, scrollContainerEl }` |

### Principles

Components make HTTP calls via the `axios` instance provided during plugin installation (`Vue.use(VertigoUi, { axios: ... })`). Data is exchanged with the server via `ViewContext` (pattern `vContext[...]`).

`v-map` uses OpenLayers with OSM tiles by default. `v-map-layer` adds markers (and their clustering) on the parent map by listening to the global `olMap` object.

## Library `vertigo-ui-dsfr` — French Design System

DSFR library (package `vertigo-dsfr` v4.3.0) integrates the French State Design System (`@gouvfr/dsfr` 1.12.1 + `@gouvminint/vue-dsfr` 8.6.0) within Vertigo.

It installs the `VueDsfr` plugin (exposing all standard DSFR components), then adds custom components adapted for Vertigo usage:

| Tag | Category | Role |
|-----|-----------|------|
| `DsfrFacets` | Advanced component | Adapts `v-facets` to DSFR theme (checkbox, tertiary buttons, dismissible tags) |
| `DsfrSelectMultiple` | Advanced component | Native DSFR multiple select |
| `DsfrMenu` | Advanced component | DSFR navigation menu |
| `DsfrMenuLink` | Advanced component | Menu link with active state management |
| `DsfrHeaderMenu` | Advanced component | Dropdown menu in header |
| `DsfrCustomHeader` | Override | Custom DSFR header with logo, service title, burger menu |
| `DsfrCustomHeaderMenuLinks` | Override | Header links |
| `DsfrCustomDataTable` | Override | DSFR table with sort, pagination, selection |
| `DsfrCustomCheckbox` | Override | DSFR checkbox with label |
| `DsfrCustomSelect` | Override | DSFR single select |
| `DsfrButtonTooltip` | Utility | Button with DSFR tooltip |
| `DsfrLinkTooltip` | Utility | Link with DSFR tooltip |
| `DsfrLink` | Utility | Stylized DSFR link with arrow |
| `RouterLink` | Integration | Bridge between DSFR and Vue router |
| `autocomplete` | Integration | TrevorEyre autocomplete for quick search |

Plugin also exposes `DSFR.methods` object with utility methods and `DSFR.utils` with utilities (e.g., random generation).

### Integration

To activate the DSFR theme, include compiled DSFR CSS and JS files (build via `build-lib`) and install the Vue `DSFR` plugin:

```js
Vue.use(VueDsfr)
Vue.use(DSFR)
```

In a Vertigo application, the DSFR theme is activated by using `<dsfr-*-html>` components in Thymeleaf templates or Vue components in Vue pages. Projects **adesi**, **fgv-webapp**, and **nova** use this integration.

## Library `vertigo-ui-wysiwyg` — Rich Text Editor

WYSIWYG library (package `vertigo-wysiwyg` v2.12.0) provides a `<v-wysiwyg>` component based on TipTap (v2.12.0) for rich text editing.

| Tag | Role |
|-----|------|
| `v-wysiwyg` | WYSIWYG editor (TipTap) |

TipTap extensions enabled:
- Formatting: **bold**, *italic*, underline, ~~strike~~, subscript, superscript
- Structure: heading, paragraph, bullet-list, ordered-list, list-item, horizontal-rule, blockquote, hard-break
- Content: link, text, gapcursor (click in empty cells)
- Control: history (undo/redo), bubble-menu (floating contextual menu)
- Layout: text-align (left, center, right, justify)

Usage in vertigo-ui module: include compiled `vertigo-wysiwyg.*.js` file and use `<vu:wysiwyg>` tag in Thymeleaf templates, or `<v-wysiwyg>` in Vue components.

## Library `vertigo-ui-server-ssr` — Server-Side Rendering

SSR library (package `@vertigo-io/vertigo-ui-server-ssr` v3.5.0) enables server-side rendering of VueJS components in a Vertigo application.

Based on Node.js with Express and `vue-template-compiler`, it provides an Express server that compiles Vue templates server-side for initial HTML rendering (useful for SEO and initial display time).

`index.js` exposes an Express middleware that:
1. Receives HTML request from Java server (Javalin/Spring)
2. Compiles Vue templates server-side
3. Returns rendered HTML with injected data

### Integration

As a Maven dependency of the application, SSR is automatically activated by the vertigo-ui module. No manual configuration is needed in most cases. Node.js server runs in parallel with the Java server and communicates via internal HTTP.

vertigo-ui module orchestrates hybrid rendering: HTML structure (Thymeleaf) is rendered server-side, then VueJS components hydrate the application client-side. SSR sends a complete first HTML render to the browser, reducing perceived display time.

## For Experts

### vertigo-ui-vuejs plugin installation

```js
import VertigoUi from 'vertigo-ui-vuejs'

Vue.createApp(App).use(VertigoUi, { axios: axiosInstance })
```

### Build pipeline

Each library uses Vite to compile its components:

| Library | Command | Output |
|--------------|----------|--------|
| vertigo-ui-vuejs | `npm run build-lib` | `dist/vertigo-ui.*` → `vertigo-ui/static/js/` |
| vertigo-ui-dsfr | `npm run build-lib` | `dist/*.*` → `vertigo-ui/static/3rdParty/dsfr/` |
| vertigo-ui-wysiwyg | `npm run build-lib` | `dist/*.*` → `vertigo-ui/static/js/wysiwyg/` |

### External dependencies by library

| Library | Critical Dependencies | Versions |
|-------------|----------------------|----------|
| vertigo-ui-vuejs | Quasar, Vue 3, OpenLayers, d3-color, lodash.debounce | Q 2.18.1, Vue 3.5.17, OL 10.6.1 |
| vertigo-ui-dsfr | DSFR, VueDSFR, Autocomplete-Trevor, Vue 3 | DSFR 1.12.1, VueDSFR 8.6.0 |
| vertigo-ui-wysiwyg | TipTap, Vue 3 | TipTap 2.12.0, Vue 3.5.13 |
| vertigo-ui-server-ssr | Express, vue-template-compiler | Express 4.17.2, VTC 2.7.14 |

### YAML Configuration vertigo-ui with extensions

UI libraries have no dedicated YAML features. They are automatically activated when `vertigo-ui` is included as a Maven dependency:

```yaml
io.vertigo.ui.UISpringWebFeatures:
    features:
        - ui:
```

Library integration is frontend-side (CSS/JS inclusion in Thymeleaf templates or `head.html`). Choice between Quasar theme and DSFR theme is made at the application's base template level.

### Migration notes

- Component `v-autocomplete` (outside `@trevoreyre/autocomplete`) is part of vertigo-ui (`<vu:autocomplete>`) not vertigo-ui-vuejs.
- Directives `v-scroll-spy`, `v-minify` are tied to page structure and should be used cautiously (global scroll, window events).
- Parameter `fitOnDataUpdate` on `v-map-layer` controls automatic map resize when data changes.
- Component `v-chatbot` requires an HTTP endpoint (`botUrl`) to a chatbot service compatible with the API defined in the component (message format `{ text, sent, label, ... }`).
