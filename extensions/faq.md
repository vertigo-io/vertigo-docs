# FAQ

Nous présentons ici, les éléments questions les courantes.
N'hésitez pas à nous contacter à support@vertigo.io ou sur notre discord 

## Mon projet stocke des pièces jointes, quel type de stockage choisir ?
Vertigo propose plusieurs types de stockage.
Le choix dépendra de la volumétrie et des contraintes de l'hébergeur.
Si le volume est faible, un stockage en base de données est possible.
Sinon, préférer un stockage metadonnées en base de données et fichier sur FileSystem
En cas de gros volume, un stockage objet (type min.io) peut être préférable

## Les composants ne semblent pas fonctionner
Pour activer les composants, il faut le faire dans le config de SpringMvc : le fichier de config de ton projet doit hériter du VSpringWebConfig de VertigoUi, il met toute la conf Spring nécessaire.
Regarde l'exemple de la config de Mars : https://github.com/vertigo-io/vertigo-mars/blob/master/src/main/java/io/mars/support/boot/MarsVSpringWebConfig.java
Normalement l'archetype Maven le pose déjà comme il faut.

## La page refuse de s'afficher
Si la page contient `layout:decorate="~{templates/MonLayout}"`, alors il faut que la page respecte la structure de MonLayout
Un layout c'est la page complète avec des trous
Pour faire une page on indique quel layout prendre et ce que l'on met dans les trous.
Il est possible de faire plusieurs niveaux de layout mais ça n'aide pas la lisibilité alors il n'en faut pas trop
En principe, un layout général, un layout pour les pages de recherche, d'accueil ou autre, un layout pour les pages de détail

## Quel outil de modélisation de données utiliser ?
Vertigo studio est nativement compatible avec PowerDesigner et Entreprise Architect.
PowerDesigner est préconisé car plus complete, Entreprise Architect passe par le XMI
La dernière version de Vertigo, propose un rendu html de la modélisation (via mermaid-js). Il est alors possible de se passer d’outils couteux.

## Où sont les classes css du genre : `col-md-3 col-xs-12 q-jumbotron bg-white`
Ce sont des classes fournies par la librairie de composant Quasar (https://quasar.dev/layout/grid/introduction-to-flexbox#Responsive-Design)

## Comment debuger les écrans vue.js/quasar ?
Il existe une extension navigateur pour vueJs qui aide au debug : `Vue.js devtools`. Pour l'utiliser il faut vue.js en version non minifiée (à ajouter au début de la page)
Sinon la vue développeur et le débug peuvent être utilisée.

## Les boutons `<vu:button-link>` ne fonctionnent que si ils sont placés à l'intérieur de balises `<section>`
La balise section est liée aux layout thymeleaf.
Tous codes html hors des balises qui sont effectivement inclus dans la page sont gardés, le reste est perdu.

## Coté IHM comment accéder dans la page aux données mises dans le context ?
Les données coté client sont accessible dans le VUiPage.vueData
Seules les données demandées lors du rendu coté serveur sont accessibles coté client afin d'améliorer la sécurité de l'application
Le mieux est tout de même de privilégier au maximum le rendu coté serveur
Ainsi pour afficher des informations statiques le mieux est de le faire avec une balise thymeleaf directement coté serveur

## Comment mettre une liste de référence dans le context ?
Une liste de référence est ajoutée dans le context avec la méthode `publishMdl`
Il faut au préalable déclarer la liste de référence :
Il faut un DefinitionProvider, par exemple : `MarsMasterDataDefinitionProvider`
Le définitionProvider doit être ajouté dans la configuration du module, par exemple `io.mars.support.SupportFeatures`
StaticMasterData permettent d'avoir des enums pour les listes de référence statique donc non administrables via ihm

## A quoi sert le tag `<vu:include-data>` dans certains écrans de la démo mars ?
Ce tag permet d'inclure la donnée du context serveur dans le vueData client.
Normalement le composant d'affichage s'occupe du include-data et il n'y a rien à faire.
Dans certains cas, il n'y a pas de composant d'affichage (ni vu:textfield, ni vu:column, ...) mais on en a besoin coté client (pour construire un lien par exemple), il faut alors l'inclure manuellement.

## J'ai un `<vu:select>` dans mon formulaire, il permet d'afficher le libellé et non l'id, comment reproduire le comportement dans une liste avec le `<vu:column>` ?
Dans de nombreux cas, l'objet sous-jacent à une liste est un objet spécifique d'IHM, il est alors possible d'ajouter un champ dans la liste, et adapter le select SQL pour récupérer le libellé directement.
Dans le cas d'une liste de référence (sinon attention aux performances), cela peut être fait automatiquement en définissant le contenu de la colonne :
```HTML
<vu:column name="equipmentType" label="Equipment Type" >
    <vu:field-read field="equipmentTypeId" list="equipmentTypes" listKey="equipmentTypeId" listDisplay="label" />
</vu:column>
```
Il y a deux manières de définir une colonne :
- en référençant un field
- en définissant un name puis le contenu de la colonne
Une fois que tu es dans le cas deux tu peux utiliser comme contenu un champ spécial `<vu:field-read>` qui s'occupe d'afficher un champ en read-only qui pointe vers une liste

## Comment rendre les éléments d'une liste sélectionnable ?
Il suffit de poser l'attribut selectable="true" sur la table.
Cela active un binding de la selection dans un : componentStates.${componentId}.selected 
Pour émettre la selection coté serveur, il faut ajouter du code spécifique.

## Comment rendre un champ obligatoire en fonction d'un autre ?
Il faut utiliser un DtObjectValidator
Voici le code à mettre dans la méthode de controleur pour lancer le contrôle du validateur sur l'objet
```java
viewContext.getUiObject(contextKey).mergeAndCheckInput(Collections.singletonList(new YourCustomDtObjectValidator()), uiMessageStack);
if (uiMessageStack.hasErrors()) {
            throw new ValidationUserException();
 }
```
Pour récupérer l'uiMessageStack il suffit de l'inclure dans la signature de la méthode du controlleur (comme le ViewContext)

## Comment envoyer un mail ?
Le MailManager aide pour l'envoi de mail. (https://github.com/vertigo-io/vertigo-extensions/blob/master/vertigo-social/src/test/java/io/vertigo/social/mail/MailManagerTest.java)


## Peux-t-on avoir 2 balises `<vu:messages>` dans une page ?
Non il faut une seule
Le plus simple est que le `<vu:message>` soit dans le template parent

## L'implémentation d'un Manager vertigo est introuvable (Components or params not found)
Il faut penser à activer la fonctionnalité dans le fichier de configuration yaml de l'appli (https://vertigo-io.github.io/vertigo-docs/#/basic/configuration)

## Comment rendre un paramètre du fichier de configuration yaml modifiable par l'hébergeur ?
Les paramètres peuvent être externalisés avec une balise de type : ${myParamName}
La valeur est alors résolue par le paramManager.

## [Studio] J'essaye de faire une double association dans un .ksp vers le même DtObject, mais studio génère deux méthodes avec le même nom.
Il faut donner un rôle à chaque association (roleA et roleB), ce rôle est utilisé pour nommer la méthode de navigation


## Je souhaite faire apparaitre une notification à l'utilisateur, comment faire ?
Il faut utiliser l'api Notify de Quasar (cf : https://quasar.dev/quasar-plugins/notify#Notify-API)
Attention, si c'est après un appel Ajax, pour récupérer le `$q`de Quasar, il faut :
- soit binder la fonction sur this pour pouvoir utiliser `$`q : `function(response){ this.$q.notify({message : 'TEST', type : 'positive'}).bind(this)`
- soit passer par l'instance Globale de `VUiPage.$q.notify`


## Quel est l'api pour faire des appels Ajax ?
La signature de la méthode `httpPostAjax` est la suivante :
`httpPostAjax(url, params, options)`

Le dernier paramètre permet de fournir un objet qui contient le callback en cas de succès et en cas d'erreur
```java
{
   onSuccess : function (response) {
      // do something
   }, 
   onError(error) {
      // do something
   }
}
```

## Comment proposer à un utilisateur de sélectionner plusieurs choix parmi les éléments d'une liste de référence  ?
Cela dépend du mode de stockage.
Mais globalement, nous proposons deux fonctionnements : 
1- Dans l'objet de critère, on ajoute un champ avec le domain de la FK et une cardinalité `*`
Dans ce cas le champ sera bien ajouté au vueData en tant que tableau d'id et pourra être mappé sur la checkbox comme ceci :
```
<q-checkbox v-model="selectedTimeZoneList" v-for="item in vueData.timeZoneList" :val="item" :label="item"></q-checkbox>
``` 
Coté `Controller`, il y aura un champ qui est un tableau d'id. Ce champ n'est pas persistable en tant que tel, charge au service de le traduire en donnée persistable.

2- L'autre solution, consiste à utiliser les *SmartTypes*. 
Dans l'objet critère, on ajoute un champ avec un domain qui est un SmartType (par exemple `DoIds`) avec comme BasicType une String
On associe au SmartType un adapteur UI qui transforme la chaine de caractère une liste d'Id, celle-ci sera sérialisée en Json lors de l'ajout au vueData, et pourra être utilisé par le composant checkbox comme dans le cas 1.
Coté `Controller`, le champ sera une chaine de caractère qui pourra être persistée directement si besoin.


## Je n'arrive pas à faire fonctionner l'upload de fichier en Ajax

Coté page :
```Html
<vu:fileupload th:if="${model.modeEdit}" float-label="Add new pictures here" th:url="'@{/commons/upload}'" key="baseTmpPictureUris" multiple />   
```

Coté Controller
```java
@PostMapping("/_save")
   public String doSave(
         final ViewContext viewContext,
         @Validate(DefaultDtObjectValidator.class) @ViewAttribute("base") final Base base,
         @QueryParam("baseTmpPictureUris") final List<FileInfoURI> addedPictureFile,
         final UiMessageStack uiMessageStack) {
```

Le composant d'upload marche en deux temps : 
1- l'utilisateur dépose son fichier sur le composant, celui-ci envoi tout de suite le fichier coté serveur et récupère un id temporaire qu'il stock dans le formulaire
2- Lorsque l'utilisateur poste son formulaire, l'id du fichier part avec le reste des données métiers, coté serveur l'id permet de retrouver le fichier et la méthode du controlleur reçoit les données métiers et le fichier en entrée.

Lorsque l'étape 2 est faite en Ajax, il faut récupérer l'id *à la main*. Le code à ajouter ressemble à :
```Html
<q-btn 
   th:@click="|httpPostAjax('', {baseTmpPictureUris:VUiPage.componentStates.uploaderbaseTmpPictureUris.fileUris.toString()})|"  
   label="Save"></q-btn>
```

## Comment choisir mon plugin de stockage de fichier ?
Vertigo propose plusieurs types de stockage.
Le choix dépendra de la volumétrie et des contraintes de l'hébergeur.
Si le volume est faible, un stockage en base de données est possible (avec `DbFileStorePlugin`).
Il faut alors un objet de mapping avec un champ `FILE_DATA` de type Blob (ou `bytea` sur PostgreSQL)

Sinon, préférer un stockage métadonnées en base de données et fichier sur FileSystem (avec `FsFileStorePlugin`).
Il faut alors un objet de mapping avec un champ `FILE_PATH` de type String dans lequel on stocke le path vers le fichier physique. 
Ce path doit pointer vers un espace adapté au contexte du projet (par exemple un NAS)

## Comment ajouter un paramètre en plus au tag `input` de mon composant `<vu:text-field>` ?
Les composants thymeleaf accepte des paramètres particuliers suffixés par `_attrs`, ces paramètres agrègent les paramètres supplémentaires posés par le développeur.
Le système est basé sur une règle de nommage.
Exemple : 
Le composant `<vu:date>` a les paramètres suivant : `object, field, label, format, date_attrs, input_attrs`
Lors du rendu : 
- La valeur du paramètre `date_attrs` est posé sur le tag `q-date` sous-jacent
- La valeur du paramètre `input_attrs` est posé sur le tag `q-input` sous-jacent (tag principal)

A l'usage : 
Lorsque le développeur ajoute un paramètre autre que ceux nommés explicitement `(object, field, label, format)`, il rentre dans un des paramètres `_attrs`
S'il est préfixé par `date_` il est agrégé dans `date_attrs`. 
S'il est préfixé par `input_` il est agrégé dans `input_attrs`. 
S'il n'est pas reconnu il est agrégé dans le dernier paramètre `_attrs`, soit : `input_attrs`.
En ajoutant `date_landscape`, l'attribut `landscape` sera posé sur le `q-date`
En ajoutant `input_placeholder="Placeholder"`, l'attribut `placeholder="Placeholder"` sera posé sur le `q-input`
En ajoutant `placeholder="Placeholder"`, l'attribut `placeholder="Placeholder"` sera posé sur le `q-input`


## Est ce que lorsque utilise une liste de référence, on peut utiliser un filtrer pour ne récupérer que certains éléments ?
Les liste des références sont des listes "nommées" : quand on les enregistre (via un `MasterDataDefinitionProvider`) on spécifie : 
- un nom
- un type d'objet
- un filtre optionnel (soit via un champ, soit deux, soit un Predicat)
Ensuite on utilise ces listes nommées en les publiant dans le `context` avec la méthode `publishMdl`
Il existe un cas particulier des listes qui n'ont pas de nom (`null`) qui est la valeur par défaut pour n'associer aucun filtre

Exemple:
Pour ne récupérer que les éléments 'actifs' (donc avec un champ booléen qui a une certaine valeur)
Dans le `MasterDataDefinitionProvider` du module (`extends AbstractMasterDataDefinitionProvider`)
```java
registerDtMasterDatas(EquipmentType.class, Map.of("active", EquipmentType::getActive), true);
```

Et pour le poser dans le `context`, dans le controller :
```java
viewContext.publishMdl(ViewContextKey.of("equipmentTypes"), EquipmentType.class, "active");
```

## A quoi correspond le paramètre `isReloadedByList` de `AbstractMasterDataDefinitionProvider.registerDtMasterDatas` ?

Ce paramètre défini le mode de rechargement de la liste lors de l'expiration du cache, soit il recharge la liste entière et redispach en id, value, soit il fait ligne par ligne. 
Le mode liste est préconisé pour la plupart des cas.
Le mode unitaire, est utilisé pour les grosses listes, comme la liste des communes par exemple

## Le composant `vu:autocomplete` n'affiche pas le libellé de la donnée mais son identifiant
Le composant autocomplete ne s'attend pas à recevoir un ViewContext en type de retour, mais un autre format plus spécifique.
Pour inspiration voir comment est faire le controller générique qui gère les autocomplete
`io.vertigo.ui.controllers.ListAutocompleteController`

Le problème peut apparaitre si le composant sous-jacent (QSelect) n'a pas la map pour associer l'identifiant en libellé. 
Normalement cette opération est effectuée coté serveur dans le template thymeleaf, en Ajax il faut alors un traitement particulier.

## J'ai une 404 pour ma page, pourtant l'url semble bonne
Avec une 404 c'est sans doute que le controller n'est pas enregistré dans Spring
A vérifier :
- les annotations du controlleur (il doit y avoir unicité des `@RequestMapping(...)` )
- la configuration de spring (*Projet*`SpringWebConfig`) (notamment les packages à scanner)

## J'ai besoin de faire de l'ajax sur ma page car j'ai une carte et je ne dois pas la perdre
Il est possible de créer le postAjax "à la main" pour des besoins particuliers. Mais dans ce cas, vous perdez les accélérateurs, assurez-vous que votre cas est pertinent.
`httpPostAjax` poste en ajax sur une route (le premier argument), avec des paramètres (le second argument) et gère le retour et les erreurs

```java
httpPostAjax('_saveMyData', {
  'vContext[myDataForm][field1]' : vueData.myDataForm.field1,
  'vContext[myDataForm][field2]' : vueData.myDataForm.field2,
  'vContext[myDataForm][field3]' : vueData.myDataForm.field3
})
```

## J'ai besoin de proposer une liste éditable dans mon écran, mais je ne reçois pas les données coté serveur
L'object DtList est un objet qui ne permet pas de modification par le client pour des raisons de sécurité.
Pour avoir une liste éditable dans le context, il faut utiliser le `context.publishDtListModifiable`
Le composant de tableau `<vu:table>` nécessite un identifiant de ligne, il faut soit que l'objet soit une entité (stockable en base), soit définir le `rowKey` sur le `<vu:table>`


## Comment activer la consultation des WebServices avec Swagger ?
La documentation est ici : https://vertigo-io.github.io/vertigo-docs/#/basic/webservices?id=swaggerapi
A partir de la version 2.1.0, le catalogue swagger est activé par défaut.
Il suffit d'aller sur la page `/swaggerUi`
Si vous avez mis un prefix d'api dans la configuration de vega vous devez l'utiliser.
Par exemple `_apiPrefix_/swaggerUi`


## Je voudrais ajouter un contrôle automatique sur un objet en entrée de mon webservice
Les DtObjects portent des champs qui ont tous un type métier : `SmartTypes`. 
Ces `SmartTypes` portent une liste de contrainte, il en existe plusieurs fournit par Vertigo, mais il est possible d'en ajouter dans le projet.
Lorsqu'un DtObject (ou une DtList) arrive par un WebService Vega ou un controlleur SpringMVC, l'objet passe par un `DtObjectValidator`.
Si rien n'est précisé il passe par le `DefaultDtObjectValidator` qui vérifie les contraintes des `SmartTypes` pour tous les champs passés par l'api.
Pour ajouter votre propre validateur il suffit d'annoter le paramètre d'entrée avec l'annotation `@Validate`
```java
@Validate(YourValidator.class)
```
Ou même avec plusieurs 
```java
@Validate({ YourValidator.class, YourOtherValidator.class })
```
Utiliser votre propre validateur, permet de faire des contrôles multi-champs.


## Y a-t-il un moyen de `load()` tous les `accessors` d'un objet donné en une fois
Non, car le load est une opération qu'il ne faut pas prendre à la légère (1 accès base). Il faut charger les données en fonction du process que le service est entrain de dérouler.
De cette règle découle le fait que la granularité du service doit être adapté, il faut éviter les services qui font tous les cas métier de l'appli 
=> pour 2 process relativement distincts il faut 2 services métiers différents.
Il reste le cas de l'affichage d'une entité complète, dans ce cas il est assez rare de devoir tout afficher d'un coup : 
- soit on a un DTO dédié à l'affichage avec un select SQL qui à permis de le remplir en une fois, 
- soit on a un découpage en onglet qui présente des informations différentes (et c'est plutôt le controller qui charge les données)

## Comment faire pour transférer des fichiers (pdf, word, ...) via des webservices ?
Tout est pris en charge par vertigo, pour le download il suffit de retourner un `VFile`.
Pour l'upload en utilisant le composant `<vu:fileupload>`, il suffit d'avoir un service qui prend un VFile en paramètre, le protocole utilisé est le standard multipart HTML.
*Il existe un système pour protéger l'identifiant et ne pas l'envoyé en clair coté client (cf. `ProtectedValueUtil`)*
**Attention** à bien respecter les verbes : `GET` pour un download et `POST` pour l'upload.

Exemple : 
```java
@GetMapping("/myFiles/{protectedUrl}")
public VFile loadFile(@PathVariable("protectedUrl") final String protectedUrl) throws URISyntaxException, IOException {
   final URI fullPath = getClass().getResource(ProtectedValueUtil.readProtectedValue(protectedUrl, String.class)).toURI();
   return fileService.loadMyFile(fullPath);
}

@PostMapping("/upload")
public FileInfoURI uploadFile(@QueryParam("file") final VFile vFile) {
   final String fullPath = fileService.loadMyFile(fullPath);
   final String protectedPath = ProtectedValueUtil.generateProtectedValue(fullPath);
   return new FileInfoURI(new FileInfoDefinition("FiDummy", "none"), protectedPath);
}
```

## Comment faire pour passer un paramètre d'une page à une autre coté serveur ? (par FlashAttribute ?)
**Le plus simple est de passer les données par l'url.**
Il est possible de "protéger" les données avec un utilitaire Vertigo `ProtectedValueUtil`.
La sécurité des données doit être réalisé sur les pages lors du chargement des données : faire apparaitre un identifiant dans l'url n'est pas un problème si la sécurité est correctement appliquée.

**Pour un passage coté serveur**
Le plus simple est de passer le paramètre par la session.
Sinon, il est possible de faire un *forward* coté serveur en passant un `ModelAndView`

## Pourquoi actuellement `securityManager.getCurrentUserSession();` retourne un Option vide ?
Ce n'est pas normale, normalement y a toujours une UserSession.
C'est automatique. Ce qui compte c'est le io.vertigo.vega.impl.servlet.filter.SecurityFilter qui doit etre présent dans le web.xml

```XML
<filter>   
     <filter-name>Security Filter</filter-name>
     <filter-class>io.vertigo.vega.impl.servlet.filter.SecurityFilter</filter-class>
     <init-param>
         <param-name>url-exclude-pattern</param-name>
         <param-value>/static/*</param-value>
     </init-param>
	 <init-param>
         <param-name>url-no-authentification</param-name>
         <param-value>/login;/login/*</param-value>
     </init-param>
</filter>
<filter-mapping>
     <filter-name>Security Filter</filter-name>
     <url-pattern>/*</url-pattern>
</filter-mapping>
```

! Attention le paramètre **url-exclude-pattern** désactive le filter, il ne faut le faire que sur les pages qui n'ont pas de Session (par exemple sur les WebServices vers d'autres SI)

## Comment changer le comportement landscape de mon composant `vu:date` ou `vu:datetime` ?
Il faut passer l'attribut `landscape` sur le composant `q-date`. 
Si on vérifie dans le composant (vertigo-ui/.../ date.html), on voit que les attributs par défaut vont sur le `q-input` (car `input_attrs` est le dernier paramètre attrs)

```XML
<th:block th:fragment="date-edit(object, field, label, format, date_attrs, input_attrs)" ... >
```

Pour poser l'attribut sur le `q-date` il faut donc le préfixer par `date_`
Comme on veut que l'attribut soit *évalué* par VueJs, il faut un `:`
Ce qui donnera par exemple : 
```
date_:landscape="'$q.screen.gt.md'"
```

## Comment rendre mon application multilingue ?
**Note**: Cette réponse s'applique pour les applications multilingues. Le seul besoin d'externaliser les messages doit être réfléchit (en général laisser le texte dans la page, est tout aussi simple à modifier et permet de la garder dans son contexte) 
Pour rendre une application multilingue, il faut traiter plusieurs contenus :
- Les textes propre aux pages (titre, menu, etc..)
- Les libellé des champs (associé aux champs des entités)
- Les règles de formatage (format de date et nombre dépendent de la langue)
- Les messages de règle de gestion
- Les messages d'erreur utilisateur
- Les données de référence multilingue
- Les données métier 

Ces contenus ne s'appliquent pas au même endroit et ont souvent des manières de faire différentes.

**Les textes propre aux pages** utilisent la syntaxe Thymeleaf : `#{my.code}`, les fichiers `.properties` doivent être posés à côté du fichier `.html` qui les utilise.

**Les libellés des champs** sont définis dans la définition du model. Ils utilisent le mécanisme multilingue de Vertigo via le LocalManager. Il faut alors des fichiers properties i18n avec comme clé l’identifiant du champ.

**Les règles de formatage** sont définies dans les composants Quasar

**Les messages des règles de gestion**, par la UiMessageStack il est plus simple d'utiliser le mécanisme multilingue de Vertigo via le LocalManager, mais il est possible d'utiliser les MessageSource Spring.

**Les erreurs utilisateurs** sont produites via des UserException, ces exceptions utilisent le mécanisme multilingue de Vertigo via le LocalManager.

**Les données de référence multilingue**, à implémenter dans l'appli, il y a plusieurs solutions : 
- soit via un champ multivalué (pour chaque langue), il est possible de le faire avec un SmartTypeAdapter
- soit via un champ par langue (par exemple labelFr, labelEs, labelEn, ...), il faut alors ajouter ce dynamisme sur l'attribut du composant dans la page

**Les données métier**, à implémenter dans l'appli. La donnée peut être multilingue (plusieurs langues pour une même entité) ou associée à une langue particulière (une seule langue par entité)

26/11













