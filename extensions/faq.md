# FAQ

Nous présentons ici les questions les plus courantes.
N'hésitez pas à nous contacter à support@vertigo.io ou sur notre discord 

## [DataStore] Mon projet stocke des pièces jointes, quel type de stockage choisir ?
Vertigo propose plusieurs types de stockage.
Le choix dépendra de la volumétrie et des contraintes de l'hébergeur.
Si le volume est faible, un stockage en base de données est possible.
Sinon, préférer un stockage metadonnées en base de données et fichier sur FileSystem
En cas de gros volume, un stockage objet (type min.io) peut être préférable

## [Ui] Les composants ne semblent pas fonctionner
Pour activer les composants, il faut le faire dans le config de SpringMvc : le fichier de config de ton projet doit hériter du VSpringWebConfig de VertigoUi, il met toute la conf Spring nécessaire.
Regarde l'exemple de la config de Mars : https://github.com/vertigo-io/vertigo-mars/blob/master/src/main/java/io/mars/support/boot/MarsVSpringWebConfig.java
Normalement l'archetype Maven le pose déjà comme il faut.

## [Ui] La page refuse de s'afficher et reste blanche
Si la page contient `layout:decorate="~{templates/MonLayout}"`, alors il faut que la page respecte la structure de MonLayout
Un layout c'est la page complète avec des trous
Pour faire une page on indique quel layout prendre et ce que l'on met dans les trous.
Il est possible de faire plusieurs niveaux de layout mais ça n'aide pas la lisibilité alors il n'en faut pas trop
En principe, un layout général, un layout pour les pages de recherche, d'accueil ou autre, un layout pour les pages de détail

## [Studio] Quel outil de modélisation de données utiliser ?
Vertigo studio est nativement compatible avec PowerDesigner et Enterprise Architect.
PowerDesigner est préconisé car plus complète, Enterprise Architect passe par le XMI
La dernière version de Vertigo, propose un rendu html de la modélisation (via mermaid-js). Il est alors possible de se passer d’outils couteux.

## [Ui] Où sont les classes css du genre : `col-md-3 col-xs-12 q-jumbotron bg-white`
Ce sont des classes fournies par la librairie de composant Quasar (https://quasar.dev/layout/grid/introduction-to-flexbox#Responsive-Design)

## [Ui] Comment debuger les écrans vue.js/quasar ?
Il existe une extension navigateur pour vueJs qui aide au debug : `Vue.js devtools`. Pour l'utiliser il faut vue.js en version non minifiée (à ajouter au début de la page)
Sinon la vue développeur et le débug peuvent être utilisée.

## [Ui] Une partie de ma page disparait, ou un `v-if` s'applique à trop d'éléments
Vérifiez qu'aucun composant Vue/Quasar n'est autofermé : il ne faut jamais écrire `<q-btn ... />` dans une page vertigo-ui, toujours fermer explicitement `<q-btn ...></q-btn>`.
En HTML5, l'autofermeture n'existe pas pour les éléments non-void : le navigateur ignore le `/` et traite la balise comme une simple balise ouvrante. Tout le contenu qui suit devient alors enfant du composant : un `v-if` étend son périmètre, des blocs entiers disparaissent (avalés comme slot du composant).
La cause est le parsing des templates *in-DOM* par le navigateur (cf. doc Vue « DOM Template Parsing Caveats » : l'autofermeture n'est valable que dans les SFC).
Les balises traitées côté serveur (`th:*`, `vu:*`) ne sont pas concernées : elles sont expansées par Thymeleaf avant d'arriver au navigateur. L'autofermeture reste donc possible pour `th:block`, les composants `vu:*` et les éléments void HTML (`<br>`, `<img>`, ...).

?> À partir de vertigo-ui 4.5.0, les balises autofermées sont refermées automatiquement au rendu (le filtre servlet historique `UnAutoCloseTagsFilter`, réparation partielle à déclarer dans le web.xml, est déprécié).

## [Ui] Comment modifier mes pages Thymeleaf sans redémarrer le serveur ?
Le paramètre Spring Boot `spring.thymeleaf.cache=false` est sans effet en vertigo-ui : le cache des templates est piloté par la méthode `isDevMode()` de `VSpringWebConfig` (`setCacheable(!isDevMode())`).
`isDevMode()` retourne `true` par défaut (cache désactivé) : c'est la surcharge dans le `VSpringWebConfig` du projet qui active le cache en production. En dev, il suffit donc de ne pas surcharger `isDevMode()` à `false`.
Pensez aussi à désactiver l'auto-reload du module web dans le Tomcat d'Eclipse, sinon chaque modification de ressource redémarre la webapp.

## [Ui] Les boutons `<vu:button-link>` ne fonctionnent que si ils sont placés à l'intérieur de balises `<section>`
La balise section est liée aux layout thymeleaf.
Tous codes html hors des balises qui sont effectivement inclus dans la page sont gardés, le reste est perdu.

## [Ui] Coté IHM comment accéder dans la page aux données mises dans le context ?
Les données coté client sont accessible dans le VUiPage.vueData
Seules les données demandées lors du rendu coté serveur sont accessibles coté client afin d'améliorer la sécurité de l'application
Le mieux est tout de même de privilégier au maximum le rendu coté serveur
Ainsi pour afficher des informations statiques le mieux est de le faire avec une balise thymeleaf directement coté serveur

## [Ui] Comment mettre une liste de référence dans le context ?
Une liste de référence est ajoutée dans le context avec la méthode `publishMdl`
Il faut au préalable déclarer la liste de référence :
Il faut un DefinitionProvider, par exemple : `MarsMasterDataDefinitionProvider`
Le définitionProvider doit être ajouté dans la configuration du module, par exemple `io.mars.support.SupportFeatures`
StaticMasterData permettent d'avoir des enums pour les listes de référence statique donc non administrables via ihm

## [Ui] A quoi sert le tag `<vu:include-data>` dans certains écrans de la démo mars ?
Ce tag permet d'inclure la donnée du context serveur dans le vueData client.
Normalement le composant d'affichage s'occupe du include-data et il n'y a rien à faire.
Dans certains cas, il n'y a pas de composant d'affichage (ni vu:textfield, ni vu:column, ...) mais on en a besoin coté client (pour construire un lien par exemple), il faut alors l'inclure manuellement.

Piège fréquent : publier la donnée (`publishDto`, `publishMdl`, ...) ne suffit pas, une expression `{{...}}` ou un binding purement client (`:color`, `openModal(...)`, construction d'un lien) affichera « undefined » si aucun composant `vu:` ne rend effectivement ce champ. Il faut alors l'inclure explicitement avec `<vu:include-data .../>`. Piège invisible en test HTTP/curl : le symptôme n'apparaît que dans un vrai navigateur.

## [Ui] J'ai un `<vu:select>` dans mon formulaire, il permet d'afficher le libellé et non l'id, comment reproduire le comportement dans une liste avec le `<vu:column>` ?
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

## [Ui] Comment rendre les éléments d'une liste sélectionnable ?
Il suffit de poser l'attribut `selectable` sur la `vu:table`.
On peut utiliser une autorisation pour le proposer si l'utilisateur à les droits : `selectable="${authz.hasAuthorization('Equipment$delete')}"`

Cela active un binding de la selection dans `componentStates.${componentId}.selected`.
Pour émettre la selection coté serveur, il faut ajouter du code spécifique.
Il faut que le développeur l'utilise pour l'envoyer au serveur sous la forme qu'il souhaite.

Coté UI, on peut afficher certain bouton lorsqu'il y a des éléments sélectionnés avec un `v-if="componentStates.equipmentsTable.selected.length > 0"`

Voici un exemple, où nous envoyons la liste des ids dans un appel Ajax (pour supprimer ces éléments)
```Javascript
VUiExtensions.methods.deleteSelectedEquipment = function(deleteEquipmentUrl)  { 
 var formParams = this.vueDataParams(['deleteEquipmentMessage']);
 formParams.append('vContext[deletedEquipmentIds]', JSON.stringify(VertigoUi.componentStates.equipmentsTable.selected.map(row => row.equId)));
  
 this.httpPostAjax(deleteEquipmentUrl, formParams, {
    onSuccess: function(response) {
       this.$data.componentStates.equipmentsTable.selected = [];
    }.bind(this)
  });
};
```

Coté Controller, on a besoin d'un élément dans le contexte pour le réceptionner (à noter que dans cet exemple, le Controller n'a pas de présélection, ce qui nécessiterai de préparer le componentStates):

```Java
private static final ViewContextKey<Long[]> deletedEquipmentIdsKey = ViewContextKey.of("deletedEquipmentIds");

public void initContext(final ViewContext viewContext) {
  //...
  viewContext.publishTypedRef(deletedEquipmentIdsKey, new Long[0], Long[].class);
  //...
 }

@PostMapping("/_deleteEquipments")
public ViewContext deleteEquipments(final ViewContext viewContext,
   @ViewAttribute("deleteEquipmentMessage") final DeleteEquipmentMessage deleteEquipmentMessage,
   @ViewAttribute("deletedEquipmentIds") final Long[] equipmentIds,
   final UiMessageStack uiMessageStack) {
   final var equUids = Stream.of(equipmentIds).map(equId -> UID.of(Equipment.class, equId)).toList();
   equipmentServices.deleteEquipments(equUids, deleteEquipmentMessage, uiMessageStack);
   return viewContext;
}
```

## [Ui] Comment rendre un champ obligatoire en fonction d'un autre ?
Il faut utiliser un DtObjectValidator
Voici le code à mettre dans la méthode de controleur pour lancer le contrôle du validateur sur l'objet
```java
viewContext.getUiObject(contextKey).mergeAndCheckInput(Collections.singletonList(new YourCustomDtObjectValidator()), uiMessageStack);
if (uiMessageStack.hasErrors()) {
            throw new ValidationUserException();
 }
```
Pour récupérer l'uiMessageStack il suffit de l'inclure dans la signature de la méthode du controlleur (comme le ViewContext)

## [Mail] Comment envoyer un mail ?
Le MailManager aide pour l'envoi de mail. (https://github.com/vertigo-io/vertigo-libs/blob/master/vertigo-social/src/test/java/io/vertigo/social/mail/MailManagerTest.java)


## [Ui] Peux-t-on avoir 2 balises `<vu:messages>` dans une page ?
Non il faut une seule
Le plus simple est que le `<vu:message>` soit dans le template parent

## [Core] L'implémentation d'un Manager vertigo est introuvable (Components or params not found)
Il faut penser à activer la fonctionnalité dans le fichier de configuration yaml de l'appli (https://vertigo-io.github.io/vertigo-docs/#/basic/configuration)

## [Core] Comment rendre un paramètre du fichier de configuration yaml modifiable par l'hébergeur ?
Les paramètres peuvent être externalisés avec une balise de type : ${myParamName}
La valeur est alors résolue par le paramManager.

## [Core] Comment lancer un traitement asynchrone ou récurrent ?
Deux mécanismes selon le besoin :
- `@DaemonScheduled(name = "DmnMyTask", periodInSeconds = 60)` (io.vertigo.core.daemon) pour les tâches techniques récurrentes non vitales (purge, rafraîchissement de cache, ...). Simple, mais sans reprise ni suivi : une exécution manquée est perdue ;
- **Orchestra** pour les jobs métier critiques : planification, suivi des exécutions en base, reprise sur erreur, multi-nœuds.

!> Créer son propre `ExecutorService` est un anti-pattern : les threads échappent au cycle de vie du nœud (arrêt propre, supervision) et aux transactions.

## [Core] Comment fonctionnent les Aspects (et pourquoi le mien ne s'applique pas) ?
Les aspects sont **globaux** : ils s'appliquent à tous les composants du nœud, il n'y a pas de scope par module.
L'ordre de chargement compte en revanche : un aspect doit être déclaré dans un module chargé **avant** les modules des composants qui l'utilisent (et au sein d'un même module, les composants sont enregistrés avant les aspects). Déclaré trop tard, l'aspect ne s'applique pas aux composants déjà chargés.
Autre limite : l'aspect est porté par un **proxy** (sous-classe javassist) qui délègue à l'instance réelle. Il ne s'applique donc que sur les appels qui passent par la référence injectée du composant : un **appel interne** (`this.maMethode()`, ou appel implicite entre deux méthodes de la même classe) ne déclenche pas l'aspect. Et seules les méthodes **publiques** sont interceptées — jamais les méthodes privées.
Pour bénéficier d'un aspect (par exemple `@Transactional`) sur un sous-traitement, il faut soit porter l'annotation sur la méthode publique d'entrée, soit déplacer le sous-traitement dans un autre composant injecté.
?> `@Transactional` est un aspect comme les autres, avec une sémantique REQUIRED : il rejoint la transaction courante s'il y en a une, sinon il en crée une.

## [Studio] J'essaye de faire une double association dans un .ksp vers le même DtObject, mais studio génère deux méthodes avec le même nom.
Il faut donner un rôle à chaque association (`roleA` et `roleB`), ce rôle est utilisé pour nommer l'accessor de navigation.
En KSP, une association se déclare avec `roleA`/`roleB`, `labelA`/`labelB` et `fkFieldName` (obligatoire, en lowerCamelCase) ; le raccourci `type : "*>1"` porte cardinalités et navigabilité :

```
create Association ADosUtiDestinataire {
	fkFieldName : "utiIdDestinataire"
	dtDefinitionA : DtDossier
	type : "*>1"
	dtDefinitionB : DtUtilisateur
	roleA : "Dossier"
	labelA : "Dossier"
	roleB : "Destinataire"
	labelB : "Destinataire"
}
```

Le rôle donne son nom à l'accessor généré : ici `dossier.destinataire()`, qui retourne un `StoreVAccessor` (`StoreListVAccessor` côté multiple), à utiliser via `.load()` puis `.get()`.
En modélisation XMI/OOM, le suffixe de la FK vient du nom de l'association (cf. l'entrée Enterprise Architect ci-dessous) ; ce suffixe est obligatoire pour une auto-jointure (sinon exception « AutoJointure »).

?> Cas particulier : une association NN réflexive (entité liée à elle-même) est impossible par construction — les colonnes de la table de jointure sont les PK des deux nœuds (pas de `fkFieldName` en NN), on aurait donc deux colonnes de même nom. Contournements : une entité porteuse (PK propre + 2 FK) ou une colonne JSON.

## [Studio] Comment renseigner les noms de champs, libellés et clés étrangères dans Enterprise Architect (XMI) ?
Au niveau **attribut** : le *Name* devient le code de la colonne et l'*Alias* le libellé métier (utilisé notamment dans les messages d'erreur).
Au niveau **association** : le *Role* devient le nom de l'accessor de navigation (l'*Alias* du rôle n'est pas lu).
Le nom de la colonne FK est déduit de la PK cible plus un suffixe extrait du **nom de l'association**, au format `{TriA}{TriB}{Suffixe}` : une association nommée `DosUtiDestinataire` entre DOSSIER et UTILISATEUR génère la FK `UTI_ID_DESTINATAIRE`.
Le paramètre `constFieldName` du loader existe toujours (défaut `true` : le modèle est attendu en CONST_CASE).

## [Studio] Comment partager des DTO entre plusieurs projets (module commun) ?
Les définitions générées par Studio dans le module partagé (classe `DtDefinitions` + SmartTypes) se déclarent chez le consommateur via un `DefinitionProviderConfig` :
```java
getModuleConfigBuilder()
	.addDefinitionProvider(DefinitionProviderConfig.builder(ModelDefinitionProvider.class)
		.addDefinitionResource("smarttypes", "commons.domain.CommonsSmartTypes")
		.addDefinitionResource("dtobjects", "commons.domain.DtDefinitions")
		.build());
```
!> La configuration YAML ne sait pas déclarer de definition resources : ce code doit être porté par une classe `Features` Java (celle du module partagé), elle-même référencée dans le YAML du projet consommateur.


## [Ui] Je souhaite faire apparaitre une notification à l'utilisateur, comment faire ?
Il faut utiliser l'api Notify de Quasar (cf : https://quasar.dev/quasar-plugins/notify#Notify-API)
Attention, si c'est après un appel Ajax, pour récupérer le `$q`de Quasar, il faut :
- soit binder la fonction sur this pour pouvoir utiliser `$`q : `function(response){ this.$q.notify({message : 'TEST', type : 'positive'}).bind(this)`
- soit passer par l'instance Globale de `VUiPage.$q.notify`


## [Ui] Quel est l'api pour faire des appels Ajax ?
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

## [Ui] Comment proposer à un utilisateur de sélectionner plusieurs choix parmi les éléments d'une liste de référence  ?
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


## [Ui] Je n'arrive pas à faire fonctionner l'upload de fichier en Ajax

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

## [DataStore] Comment choisir mon plugin de stockage de fichier ?
Vertigo propose plusieurs types de stockage.
Le choix dépendra de la volumétrie et des contraintes de l'hébergeur.
Si le volume est faible, un stockage en base de données est possible (avec `DbFileStorePlugin`).
Il faut alors un objet de mapping avec un champ `FILE_DATA` de type Blob (ou `bytea` sur PostgreSQL)

Sinon, préférer un stockage métadonnées en base de données et fichier sur FileSystem (avec `FsFileStorePlugin`).
Il faut alors un objet de mapping avec un champ `FILE_PATH` de type String dans lequel on stocke le path vers le fichier physique. 
Ce path doit pointer vers un espace adapté au contexte du projet (par exemple un NAS)

## [Ui] Comment ajouter un paramètre en plus au tag `input` de mon composant `<vu:text-field>` ?
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


## [DataStore] Est ce que lorsque utilise une liste de référence, on peut utiliser un filtrer pour ne récupérer que certains éléments ?
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

## [DataStore] A quoi correspond le paramètre `isReloadedByList` de `AbstractMasterDataDefinitionProvider.registerDtMasterDatas` ?

Ce paramètre défini le mode de rechargement de la liste lors de l'expiration du cache, soit il recharge la liste entière et redispach en id, value, soit il fait ligne par ligne. 
Le mode liste est préconisé pour la plupart des cas.
Le mode unitaire, est utilisé pour les grosses listes, comme la liste des communes par exemple

## [DataStore] Ma grosse liste de référence n'est pas mise en cache (limite de compression)
Le cache sérialise et compresse les éléments par défaut, avec une taille maximale de **20 Mo** après sérialisation (`CompressionCodec.MAX_SIZE_FOR_COMPRESSION`) : au-delà, la mise en cache échoue.
Pour les grosses listes non modifiables, désactivez la sérialisation en passant le paramètre `serializeElements` de la `CacheDefinition` à `false` : la liste est conservée telle quelle en mémoire (attention : les objets sont alors partagés, ils ne doivent pas être modifiés).

## [Ui] Le composant `vu:autocomplete` n'affiche pas le libellé de la donnée mais son identifiant
Le composant autocomplete ne s'attend pas à recevoir un ViewContext en type de retour, mais un autre format plus spécifique.
Pour inspiration voir comment est faire le controller générique qui gère les autocomplete
`io.vertigo.ui.controllers.ListAutocompleteController`

Le problème peut apparaitre si le composant sous-jacent (QSelect) n'a pas la map pour associer l'identifiant en libellé. 
Normalement cette opération est effectuée coté serveur dans le template thymeleaf, en Ajax il faut alors un traitement particulier.

## [Ui] J'ai une 404 pour ma page, pourtant l'url semble bonne
Avec une 404 c'est sans doute que le controller n'est pas enregistré dans Spring
A vérifier :
- les annotations du controlleur (il doit y avoir unicité des `@RequestMapping(...)` )
- la configuration de spring (*Projet*`SpringWebConfig`) (notamment les packages à scanner)

## [Ui] J'ai besoin de faire de l'ajax sur ma page car j'ai une carte et je ne dois pas la perdre
Il est possible de créer le postAjax "à la main" pour des besoins particuliers. Mais dans ce cas, vous perdez les accélérateurs, assurez-vous que votre cas est pertinent.
`httpPostAjax` poste en ajax sur une route (le premier argument), avec des paramètres (le second argument) et gère le retour et les erreurs

```java
httpPostAjax('_saveMyData', {
  'vContext[myDataForm][field1]' : vueData.myDataForm.field1,
  'vContext[myDataForm][field2]' : vueData.myDataForm.field2,
  'vContext[myDataForm][field3]' : vueData.myDataForm.field3
})
```

## [Ui] J'ai besoin de proposer une liste éditable dans mon écran, mais je ne reçois pas les données coté serveur
L'object DtList est un objet qui ne permet pas de modification par le client pour des raisons de sécurité.
Pour avoir une liste éditable dans le context, il faut utiliser le `context.publishDtListModifiable`
Le composant de tableau `<vu:table>` nécessite un identifiant de ligne, il faut soit que l'objet soit une entité (stockable en base), soit définir le `rowKey` sur le `<vu:table>`


## [Vega] Comment activer la consultation des WebServices avec Swagger ?
La documentation est ici : https://vertigo-io.github.io/vertigo-docs/#/basic/webservices?id=swaggerapi
A partir de la version 2.1.0, le catalogue swagger est activé par défaut.
Il suffit d'aller sur la page `/swaggerUi`
Si vous avez mis un prefix d'api dans la configuration de vega vous devez l'utiliser.
Par exemple `_apiPrefix_/swaggerUi`


## [Vega] Un champ calculé de mon entité n'apparaît pas dans le JSON de mon WebService
C'est le comportement nominal : la sérialisation Vega (Gson + `DtObjectJsonAdapter`) parcourt les champs de la définition de l'entité et **exclut explicitement les champs `computed`** (elle ajoute en revanche les accessors chargés). Un getter Java ad hoc n'est jamais sérialisé non plus : seuls les champs de la définition comptent. La désérialisation applique le même filtre : un champ `computed` envoyé dans le JSON d'entrée est ignoré.
Solution : déclarer le champ dans le modèle comme champ **non persisté** et le renseigner via le SQL de la Task ou dans le service — présent dans la définition, il est sérialisé normalement.

## [Ui] Je voudrais ajouter un contrôle automatique sur un objet en entrée de mon webservice
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


## [DataStore] Y a-t-il un moyen de `load()` tous les `accessors` d'un objet donné en une fois
Non, car le load est une opération qu'il ne faut pas prendre à la légère (1 accès base). Il faut charger les données en fonction du process que le service est entrain de dérouler.
De cette règle découle le fait que la granularité du service doit être adapté, il faut éviter les services qui font tous les cas métier de l'appli 
=> pour 2 process relativement distincts il faut 2 services métiers différents.
Il reste le cas de l'affichage d'une entité complète, dans ce cas il est assez rare de devoir tout afficher d'un coup : 
- soit on a un DTO dédié à l'affichage avec un select SQL qui à permis de le remplir en une fois, 
- soit on a un découpage en onglet qui présente des informations différentes (et c'est plutôt le controller qui charge les données)

## [DataStore] J'ai l'erreur « Accessor is not loaded, you must load it before calling get method »
Les accessors de navigation (`StoreVAccessor` / `StoreListVAccessor`) ne chargent rien automatiquement : il faut appeler explicitement `load()` avant `get()`.
```java
dossier.destinataire().load();
final Utilisateur destinataire = dossier.destinataire().get();
```
Le `load()` fait un accès SQL : il doit donc être exécuté **dans un service `@Transactional`** — le contrôleur ne fait ensuite que publier l'entité chargée dans le ViewContext.
Échappatoires :
- `loadIfAbsent()` : ne charge que si l'accessor ne l'est pas déjà (utile dans un service appelé depuis plusieurs chemins) ;
- `lazyGet()` : fait le `load()` si nécessaire, mais est marqué `@deprecated` dès son ajout (4.3.0) — une facilité de transition, à ne pas généraliser.

## [DataStore] Comment charger une entité avec toutes ses associations (fetch join à la JPA) ?
Il n'y a pas d'équivalent, et c'est un choix : le chargement de grappes d'objets est une source classique de problèmes de performance (chargements incontrôlés, N+1) et rend le coût des services difficile à raisonner. Vertigo impose de charger explicitement ce dont le traitement a besoin.
Trois patterns selon le cas :
1. **Liste d'affichage** : un DTO dédié rempli en une requête par un SELECT avec les jointures ad hoc (Task) ;
2. **Traitement métier** : deux requêtes — les entités principales, puis leurs enfants via un `WHERE IN` ;
3. **Index de recherche** : une seule requête avec `GROUP BY` + `string_agg` pour aplatir les sous-entités (cf. l'entrée sur la facette à partir d'une liste de tags).

## [DataStore] Comment insérer un grand nombre d'entités efficacement (et récupérer les clés générées) ?
`DAO.createList(DtList<E>)` insère en batch (moteur `TaskEngineInsertBatch`) **et** repositionne les clés générées sur les entités : après l'appel, chaque élément de la liste porte sa PK.
Pour un graphe parent/enfant à insérer dans une Task custom, il reste possible de pré-tirer les valeurs de séquence en lot (`SELECT nextval(...)`) afin d'affecter les PK des parents et de renseigner les FK des enfants avant les deux insertions batch.

## [DataStore] Comment gérer une contrainte d'unicité avec un message utilisateur propre ?
La contrainte se pose en SQL :
```sql
ALTER TABLE UTILISATEUR ADD CONSTRAINT UNQ_UTILISATEUR_EMAIL UNIQUE (EMAIL);
```
En cas de violation, Vertigo (`AbstractSqlExceptionHandler`, branché pour H2, Oracle, PostgreSQL et SQL Server) traduit l'exception SQL en `VUserException` en utilisant **le nom de la contrainte comme clé de message**.
Il suffit donc de déclarer une ressource avec cette clé (`UNQ_UTILISATEUR_EMAIL=Cet email est déjà utilisé`) ; à défaut, le message générique (`DYNAMO_SQL_CONSTRAINT_ALREADY_REGISTERED`) est affiché.

## [DataStore] Comment garantir qu'un même élément n'est pas traité par deux traitements concurrents ?
Utilisez `EntityStoreManager.readOneForUpdate(uid)` (ou le `getForUpdate` du DAO) : un `SELECT ... FOR UPDATE` est généré selon le dialecte de la base (SQL Server : `WITH (UPDLOCK, INDEX(PK_...))`). Le verrou est posé sur la ligne et libéré au commit ou rollback de la transaction.
!> Ne comptez pas sur `synchronized` : un verrou JVM ne protège pas en multi-nœuds. Le verrou base de données est le seul point de synchronisation commun à tous les nœuds.

## [Transaction] Comment exécuter une écriture qui survit au rollback (journalisation, traçabilité) ?
`VTransactionManager.createAutonomousTransaction()` (vertigo-commons) ouvre une transaction indépendante de la transaction courante :
```java
try (VTransactionWritable tx = transactionManager.createAutonomousTransaction()) {
	journalDAO.create(journal);
	tx.commit();
}
```
Elle est commitée même si la transaction englobante est ensuite rollbackée — cas d'usage typique : journaliser une tentative qui a échoué.
À l'inverse, pour déclencher une action seulement si la transaction principale aboutit, utilisez `VTransaction.addAfterCompletion(...)` : le callback `afterCompletion(boolean txCommitted)` permet de tester l'issue de la transaction.

## [DataStore] Pourquoi ne peut-on pas créer un VFile directement depuis un InputStream ?
Parce qu'un `VFile` est un **fournisseur de flux paresseux** : le flux doit pouvoir être (re)créé à la demande, et c'est le consommateur qui l'ouvre et le ferme (envoi HTTP, stockage, ...). Un `InputStream` déjà ouvert ne se lit qu'une fois et poserait la question de qui le ferme.
Les fabriques reflètent ce principe :
- `FSFile.of(path)` pour un fichier présent sur le filesystem ;
- `StreamFile.of(...)` qui prend un `DataStream` (io.vertigo.core.lang), c'est-à-dire une lambda capable d'ouvrir un nouveau flux à chaque appel : `() -> new ByteArrayInputStream(bytes)` par exemple.

## [DataStore] Berkeley (KVStore) : comment sont purgées les données, et pourquoi mes écritures sont refusées (DiskLimitException) ?
La purge des éléments expirés est assurée par un daemon dédié qui passe toutes les 60 s. Le TTL se définit **par collection** dans le paramètre `collections` du plugin : `maCollection;TTL=3600` (en secondes ; `;inMemory` possible ; défaut -1 = éternel). Le paramètre `purgeVersion` (V1/V2/V3, défaut V3) sélectionne l'algorithme de purge.
Côté disque, Berkeley exige **1 Go d'espace libre minimum** (seuil `je.freeDisk`, fixé en dur, non paramétrable) : sous ce seuil, toute écriture est refusée avec une `DiskLimitException`. À prévoir au dimensionnement, d'autant que les fichiers Berkeley ne rétrécissent jamais : l'espace libéré par la purge est réutilisé, pas rendu au filesystem.

## [Ui] Comment faire pour transférer des fichiers (pdf, word, ...) via des webservices ?
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
   final String fullPath = fileService.saveMyFile(vFile);
   final String protectedPath = ProtectedValueUtil.generateProtectedValue(fullPath);
   return new FileInfoURI(new FileInfoDefinition("FiDummy", "none"), protectedPath);
}
```

## [Ui] Comment afficher un PDF généré suite au POST d'un formulaire ?
Cas simple d'abord : si la page n'a pas besoin d'être mise à jour (ni vueData, ni messages d'erreur à afficher), un contrôleur POST peut retourner directement le `VFile`. Vertigo-ui l'envoie en `Content-Disposition: attachment` (`VFileReturnValueHandler`) : le navigateur reste sur la page et propose le téléchargement.
La problématique vient des POST **Ajax** — le mode habituel des écrans vertigo-ui, nécessaire dès qu'il faut mettre à jour le vueData ou afficher les erreurs de saisie : la réponse d'un XHR n'est pas « affichée » par le navigateur, un binaire reçu en Ajax ne déclenche ni téléchargement ni ouverture de document. Même contrainte pour ouvrir le PDF dans un **nouvel onglet** : il faut une URL GET.
Dans ces cas, le pattern est en deux temps, entièrement outillé par vertigo-ui :
1. le POST génère le PDF, le stocke temporairement et retourne un `FileInfoURI` : retourné par un contrôleur SpringMVC, il part automatiquement vers le client sous forme de valeur **protégée**, et est re-résolu quand il revient en paramètre ;
2. le client déclenche un GET avec cette valeur ; le contrôleur retourne un `VFile`, envoyé en `Content-Disposition: attachment`.

Pour le stockage temporaire, utilisez la feature `filestore.fullFilesystem` (`FsFullFileStorePlugin`) : le fichier complet (contenu + métadonnées) va sur le filesystem, et le paramètre `purgeDelayMinutes` active un daemon de purge des fichiers obsolètes.

?> La protection des valeurs s'appuie sur `ProtectedValueUtil` (vertigo-ui), qui nécessite un KVStore avec une collection `protected-value`.

## [Ui] Comment faire pour passer un paramètre d'une page à une autre coté serveur ? (par FlashAttribute ?)
**Le plus simple est de passer les données par l'url.**
Il est possible de "protéger" les données avec un utilitaire Vertigo `ProtectedValueUtil`.
La sécurité des données doit être réalisé sur les pages lors du chargement des données : faire apparaitre un identifiant dans l'url n'est pas un problème si la sécurité est correctement appliquée.

**Pour un passage coté serveur**
Le plus simple est de passer le paramètre par la session.
Sinon, il est possible de faire un *forward* coté serveur en passant un `ModelAndView`

## [Vega] Pourquoi actuellement `securityManager.getCurrentUserSession();` retourne un Option vide ?
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

## [Ui] Comment changer le comportement landscape de mon composant `vu:date` ou `vu:datetime` ?
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

## [Ui] Comment rendre mon application multilingue ?
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

## [Search] Comment préselectionner des facettes lorsque l'utilisateur arrive sur l'écran de recherche ?
L'api du composant de recherche prend un paramètre pour les facettes sélectionnées, il suffit d'initialiser cet objet `SelectedFacetValues`, il y a pour cela un Builder.

Exemple:
```Java
final SelectedFacetValues initialSelectedFacetValues = SelectedFacetValues.empty()
     .add("FctEquipmentEquipmentTypeName", "building")
     .build();
```

## [Search] Comment filtrer sur une liste de valeurs (12 OU 13 OU ...) ?
Déclarez un critère groupé dans le DSL de recherche, par exemple `+PRO_ID:(#proIds#)`, et passez les valeurs séparées par des **espaces** (`"12 13"`) : à l'intérieur d'un groupe, l'espace vaut **OR**.
- Pour un **AND** (tous les termes obligatoires), préfixez le champ dans la référence : `+PRO_ID:(#+proIds#)` ;
- un champ de critère vide ou `null` ne génère **aucun filtre** : le bloc est ignoré, pas besoin de construire la requête dynamiquement ;
- un séparateur collé au texte du critère n'est pas re-tokenisé : c'est voulu, pour rechercher tels quels des codes, adresses IP, etc.

## [Search] Comment trier les résultats de recherche sur plusieurs champs ?
Le tri se pilote par le `DtListState` : un seul `sortFieldName` et une seule direction. Le plugin ElasticSearch splitte cependant le nom de champ sur la virgule : `"nom,prenom"` trie sur les deux champs, avec la **même direction** pour tous.
Pour privilégier les documents récents sans imposer un tri strict, préférez le boost de pertinence du builder de `SearchQuery` : `withDateBoost(dateField, numDaysOfBoostRef, mostRecentBoost)`.
Pour un vrai tri multi-colonnes avec des directions différentes, faites le tri en SQL dans une Task (hors recherche full-text).

## [Search] Comment trier une facette par ordre décroissant ?
Les ordres de facette (`FacetOrder`) sont `alpha`, `count` (défaut des facettes term) et `definition` (défaut des facettes range) — il n'y a pas d'ordre descendant.
La solution est une facette **range** : l'ordre `definition` restitue les plages dans l'ordre de déclaration, il suffit de les déclarer de la plus récente à la plus ancienne. Les bornes relatives utilisent le date-math ElasticSearch, en **minuscules** : `now-1y`, `now-10y`, ...

## [Search] À quel moment l'index est-il mis à jour après un create/update/delete ?
L'indexation est déclenchée **au commit** de la transaction, jamais avant : l'événement de store est posté dans un `addAfterCompletion` gardé par `if (txCommitted)`.
Conséquences :
- un rollback n'indexe rien : l'index reste cohérent avec la base ;
- les tests transactionnels rollbackés ne polluent pas l'index ;
- dans la transaction courante, une recherche ne voit pas encore les modifications en cours.

## [Search] Puis-je indexer une structure imbriquée (nested) dans mon index ?
Non : le mapping généré par Vertigo est **plat**, aucun type `nested` ou `object` n'est déclarable. L'index sert à retrouver des documents, pas à porter le modèle relationnel.
Deux approches :
- champ **multi-valué** plat : ElasticSearch accepte nativement les tableaux de valeurs (cf. l'entrée sur la facette à partir d'une liste de tags) ;
- **dénormalisation** : si les sous-entités doivent être recherchées individuellement, créer un document d'index par sous-entité.

## [Search] Comment faire une recherche transverse sur plusieurs types d'entités ?
Créez un index dédié qui agrège les différentes entités dans un même document « générique » :
- un KeyConcept support et un `SearchLoader` spécifique qui charge et transforme chaque type d'entité ;
- un id de document construit comme une URN (type + id) pour retrouver l'entité d'origine ;
- une facette « type » pour filtrer par type d'entité.
Alternative : une recherche par index puis agrégation des résultats via `FacetedQueryResultMerger`.

## [Search] Comment faire une recherche « contient » (sous-chaîne) ?
L'`indexType` d'un SmartType ne porte qu'**un seul analyzer** (syntaxe `monAnalyzer{:type}{:stored}{:sortable}{:facetable}`) : il n'y a pas de `search_analyzer` distinct. Un analyzer edgeNGram s'appliquerait donc aussi à la requête saisie (bruit) ; un nGram complet est de toute façon déconseillé (taille d'index).
En pratique :
- pour un « commence par », utilisez le joker dans le DSL : `#query*#` ;
- pour un vrai « contient » métier, construisez un champ calculé dans le SearchLoader avec un découpage adapté (tokens métier), plutôt que de compter sur l'analyzer.

## [Search] Comment indexer le contenu d'un fichier (PDF, Word, ...) ?
Vertigo n'embarque que `tika-core` (détection du type MIME) : ajoutez la dépendance **`tika-parsers`** au projet, puis extrayez le texte avec Tika dans le `SearchLoader` au moment de construire le document d'index.
Déclarez le champ en `notStored` : le texte extrait sert à la recherche mais n'a pas à être restitué ni à gonfler le stockage de l'index.

## [Config] Comment utiliser un plugin custom pour un manager existant (par exemple Quarto) ?
Les modules sont démarrés les uns après les autres. La configuration via leur feature doit être intègre et complète.
Dans la configuration yaml, il est possible de préciser des class de plugins spécifiques à utiliser :

Exemple:
```Yaml
modules:
  io.vertigo.core.node.config.yaml.YamlBioFeatures:
      features:
        - bio:
        - math: 
            start: 100
      plugins:
        - io.vertigo.core.node.component.data.SimpleMathPlugin: 
            factor: 20
```

Il est important de vérifier l'interface implémentée par le plugin, c'est elle qui déterminera quel *type* de plugin et comment il sera injecté dans le Manager.
Son identifiant est calculé automatiquement, si il y a plusieurs plugins dans le module les id seront suffixés par $1,$2, etc...

> Si lors du démarrage, une erreur indique que deux composants on le même id, c'est peut-être que le même plugin a été chargé dans deux modules différents.

!> **Attention** notamment aux features du projet qui sont souvent en autodiscovery, car dans ce cas tous les composants présent dans un package sont chargés (y compris les plugins custom d'autres Managers). Si c'est le cas, il est possible de déplacer le plugin dans un package non scanné **ou** d'annoter le plugin avec `@NotDiscoverable`


## [Ui] Comment ajouter un composant VueJs dans mon projet
Pour ajouter un composant VueJs dans le projet, il faut utiliser la fonction adaptée sur l'instance VueJs.

Pour que cela soit fait au bon moment, Vertigo propose un event pour le faire : 

```Javascript
window.addEventListener('vui-before-plugins', function(event) {
    let vuiApp = event.detail.vuiAppInstance;
    vuiApp.component('v-my-component', MyComponent);
});
```
> Il est aussi possible d'enregistrer des directives (`vuiApp.directive(...)`)

Pour construire le composant, il est possible de le faire dans un fichier `.vue` puis de faire le build en format compatible `umd` avec un vite, webpack ou autre.

Il est aussi possible de le créer dans un fichier javascript, via l'utilisation de `Vue.defineComponent`.

Cela resemble alors à cela : 
```Javascript
const MyComponent = Vue.defineComponent({
  name: 'MyComponent', // Nom du composant
  props: {
    message: {
      type: String,
      required: true, // La prop est obligatoire
    },
    initialCounter: {
      type: Number,
      default: 0, // Valeur par défaut
    },
  },
  data() {
    return {
      counter: this.initialCounter, // Initialise le compteur avec une prop
    };
  },
  methods: {
    increment() {
      this.counter++;
    },
    decrement() {
      if (this.counter > 0) {
        this.counter--;
      }
    },
  },
  created() {
    console.log(`Composant ${this.name} créé avec le message : "${this.message}"`);
  },
  mounted() {
    console.log('Composant monté dans le DOM.');
  },
  template: `
    <div>
      <h1>{{ message }}</h1>
      <p>Valeur actuelle du compteur : {{ counter }}</p>
      <button @click="increment">Incrémenter</button>
      <button @click="decrement">Décrémenter</button>
    </div>
  `,
});
```


## [List] Comment ne pas avoir de pagination coté client pour une liste ?

Le composant sous jacent utilise celui de Quasar. 
En se réferant à la documention de l'API (https://quasar.dev/vue-components/table#qtable-api), on voit qui faut simplement lui mettre une nombre de ligne par page à 0.
Donc :
```HTML
<vu:table ... myRowsPerPage="0" ...
```


## [List] J'ai une Internal Serveur Error (erreur 500) quand une liste dans mon écran à trop d'éléments, que dois-je faire ?

Lors d'un rendu standard de liste dans une page, l'emsemble de la liste fournit dans le viewContext est affichée.
Pour protéger le système, cette liste doit être limitée en taille, pour cela il faut déjà le traiter coté serveur dès le service de requete.

Le fait de passer la limite coté serveur, entraine des modifications du fonctionement de la liste coté client, car les opérations de navigations dans la liste doivent aussi reportés coté serveur : (tri, filtrage, ...)
*Note : La pagination peut rester coté client, car elle permet de consulter les X premiers éléments pour un tri donné. *
*Et il n'est pas possible de proposer l'ensemble des résultats à travers la pagination, car les bases de données ne peuvent pas non plus récuperer efficacement les données de pages trop lointaines*

Vous aurez certainement besoin d'un objet pour porter le filtrage adapté à votre cas : une liste déroulante, un préfix de recherche, des dates, etc...
Pour porter les critères de tri et de pagination, Vertigo propose l'object `DtListState`.

Voici les étapes à mettre en place : 

Coté service, complétez votre requête avec le dtListState : 
```Java
public DtList<Document> getAuthorizedDocuments(final DocumentFiltre documentFiltre, final DtListState dtListState) {
	//---Authz--
	final Criteria<Document> securityCriteria = authorizationManager.getCriteriaSecurity(Document.class, DocumentOperations.readDocument);
	//---
	final Criteria<Document> documentCriteria = Criterions.isEqualTo(DocumentFields.documentTypeId, DocumentTypeEnum.document.getEntityUID().getId())
				.and(Criterions.startsWith(DocumentFields.name, documentFiltre.getNamePrefix()));
	return documentDAO.findAll(securityCriteria.and(documentCriteria), dtListState);
}
```

Coté controller, il faut modifier le initContext pour ajouter le filtre et le chargement de la liste avec une limite.
Il faut surtout ajouter un WebService de rechargement qui applique le filtre et le tri (le initContext réutilise d'ailleurs cette méthode)
```Java
@GetMapping("/")
public void initContext(final ViewContext viewContext, final UiMessageStack uiMessageStack) {
	final DocumentFiltre documentFiltre = new DocumentFiltre();
	viewContext.publishDto(documentFiltreKey, documentFiltre);
	reload(documentFiltre, DtListState.of(MAX_ELEMENTS, 0, DocumentFields.name.name(), false), viewContext, uiMessageStack);
}

@PostMapping("/_reload")
public ViewContext reload(@ViewAttribute("documentFiltre") final DocumentFiltre documentFiltre, final DtListState dtListState, final ViewContext viewContext, final UiMessageStack uiMessageStack) {
	final DtList<Document> documents = documentsServices.getAuthorizedDocuments(documentFiltre, dtListState.withDefault(MAX_ELEMENTS, TemplateFields.name, false));
	if (documents.size() >= MAX_ELEMENTS) {
		uiMessageStack.info("La liste ne présente que les "+MAX_ELEMENTS+" premiers éléments, veuillez affiner votre filtre.");
	}
	viewContext.publishDtList(documentsKey, documents);
	return viewContext;
}
```

Coté page, il faut ajouter le filtre et activer le tri coté serveur sur le tableau

Pour le tri coté serveur, on ajoute l'attribut `sortUrl` sur le `vu:table`.

Exemple : `sortUrl="@{_reload}"`

Pour recharger la liste lorsque le filtre est modifié, on peut utiliser le `$watch` de vueJs :
```Javascript
VUiPage.$watch('vueData.documentFiltre', Quasar.debounce(
        (newValue, oldValue) => { VUiPage.httpPostAjax('_reload', VUiPage.vueDataParams(['documentFiltre']))}, 500
        ), { deep: true });	
```


*Note: Un exemple de ce type de liste est proposée dans la formation UI : (https://github.com/vertigo-io/vertigo-university/blob/master/sample-vertigo-ui-full/Level2.4.md#Ecran de détail - Tri coté serveur)*
*Note2 : Il est possible de récupèrer le nombre total de ligne pour l'afficher en entête de tableau. Dans ce cas le nombre total est conservé dans la liste en tant que metadata. Exemple: `list.setMetaData(DtList.TOTAL_COUNT_META, service.countByCriteria(filtre));`


## [Ui] Comment changer la page active du composant table lors du changement des critères ?
Si votre page propose un rafraichissement d'une liste en Ajax, et que l'utilisateur a changer de page active, lorsque la liste est mise à jour, il est possible que la page courante soit supérieur au nombre de page maximum et plus rien ne s'affiche.
Lorsque que vous avez un tableau paginé, et que vous rafraichissez la liste par Ajax, nous préconisons de retourner à la première page dès que l'on agit sur un critérè.
Pour cela il faut modifier l'objet `pagination`du component state sur le `onSuccess`.

Exemple: 
```Javascript
httpPostAjax('_reload', ['myCriteria'], {
	 onSuccess: function() {
		 this.$data.componentStates.maTableRef.pagination.page = 0;
		}
	}.bind(this)
})
```

Rappel: pour réagir au modification de critère, il est préférable de mettre un `watch`sur l'objet critère : 
```Javascript
VUiPage.$watch('vueData.critereDossier', () => reload('dossier'), { deep: true });
```

## [Database] Comment accéder facilement à la base de données de mon environnement ?
Tout d'abord, attention aux aspects de sécurité, dans un principe de défense en profondeur, il est normal et souhaitable que votre base de données soit pas accéssible en direct.
Cependant lors des phases de mise aux point, et en fonction du contexte de votre projet cela peut être utile.
Je partage ici, une solution parmi d'autres et qui a déjà été réalisées.

Dans votre configuration.yaml, vous pouvez ajouter un manager pour lancer une console H2 (base de données de test, mais qui inclus un client Jdbc)
Exemple : 
```yaml
  #on ajoute une feature dans le module de support du projet. On conditionne sur le mode de dev, pour le retirer des envs avec des données sensibles
  io.vertigo.mars.support.SupportFeatures: 
    features:
      - h2Console:
          __flags__: ["devMode"]

```

Dans SupportFeatures :
```java
	/**
	 * Activates h2 console.
	 * @return these features
	 */
	@Feature("h2Console")
	public SupportFeatures withH2Console(final Param... params) {
		getModuleConfigBuilder()
				.addComponent(H2ConsoleManager.class, params);
		return this;
	}
```

Le H2ConsoleManager :
```java
import org.h2.tools.Console;

public final class H2ConsoleManager implements Component, Activeable {

	private final Console console = new Console();
	private final String[] args;

	@Inject
	public H2ConsoleManager(@ParamValue("args") final Optional<String> argsOpt) {
		Assertion.check().isNotNull(argsOpt);
		//---
		args = argsOpt.map(cmdArgs -> cmdArgs.split("\\|")).orElseGet(() -> new String[] { "-web" });

	}

	@Override
	public void start() {
		try {
			console.runTool(args);
		} catch (final SQLException e) {
			throw WrappedException.wrap(e);
		}

	}

	@Override
	public void stop() {
		console.shutdown();

	}
}
```

La console est lancée au démarrage, et accéssible via l'url indiquée dans le log : 
`Web Console server running at http://127.0.0.1:8082?key=0103....bf8a (only local connections)`

Il faudra configurer la connexion en reprenant les infos de l'url Jdbc, mais vous aurez ainsi facilement accès à la base de données.


## [Task] Comment traiter une table très volumineuse sans saturer la mémoire ?
Il n'y a pas d'API de curseur ou de stream (`SqlManager.executeQuery` retourne une liste bornée par une limite). Le pattern est la **keyset pagination** : traiter par lots en repartant du dernier id lu.
```sql
SELECT ...
FROM MY_TABLE
WHERE MY_TABLE_ID > #lastId#
ORDER BY MY_TABLE_ID ASC
```
avec une limite de lot, en bouclant tant que la liste retournée n'est pas vide (le dernier id lu devient la borne du lot suivant).
Contrairement à un OFFSET, ce parcours est stable si les données bougent et reste performant (parcours d'index). Pour l'écriture en masse, utilisez `TaskEngineProcBatch`.

## [Task] Peut-on factoriser du SQL entre plusieurs Tasks KSP (include) ?
Non, il n'existe aucun mécanisme d'inclusion dans les KSP. Deux contournements :
- un **TaskEngine spécifique** qui construit la partie commune du SQL en Java ;
- passer le fragment SQL en **paramètre** de la Task avec la syntaxe `<%= monFragment %>` (injecté tel quel dans la requête : à réserver à du SQL produit par le code, jamais à une saisie utilisateur).

## [Search] Comment créer une facette à partir d'une liste de tags dans mon objet ?

*Note: Un exemple est présent sur la démo mars pour la facette des équipements par tags ([mars](https://github.com/vertigo-io/vertigo-mars/))*

Nous partons d'une colonne de notre objet d'index qui contient la liste des tags avec un séparateur.
Nous allons utiliser une facette term : les valeurs de celle-ci sera basée sur les valeurs présentent dans l'index.
Comme c'est une facette term, il est important que la facette soit construite sur une valeur non modifiée de la valeur saisie, pour cela on utilise le mode keyword. 
Pour gérer le caractère multiple, on va utiliser un séparateur, dans cet exemple nous prenons le | qui à l'avantage d'être un caractère qui peut être facilement dédié à cet usage (ce n'est pas une ponctuation 'légitime').

On commence par un analyser spéciale dans la configuration elasticsearch :

`elasticsearch.yaml`
```yaml

index :
    analysis :
        normalizer :
            code :
                type : custom
        analyzer :
            multiple_code :
                tokenizer : piped_keywords
                filter : []
        tokenizer :
            piped_keywords :
                type : pattern
                pattern : '([|,;] *)'
```

On utilise un smartype adapté qui utilise cet analyzer:
`MarsSmartTypes.java`
```Java
	@SmartTypeDefinition(String.class)
	@Formatter(clazz = FormatterDefault.class)
	@SmartTypeProperty(property = "storeType", value = "TEXT")
	@SmartTypeProperty(property = "indexType", value = "multiple_code:facetable")
	Tags,
```

Dans le ksp de search, on ajoute le champs
`searchEquipment.ksp` 
```Javascript
create DtDefinition DtEquipmentIndex {
	...
	field tags {domain: DoTags, label: "Tags" }
	...
}
```

Il faut ensuite compléter la requete de recherche pour concaténer :
`searchTasks.ksp`
```SQL
SELECT 
    equ.EQUIPMENT_ID,
    ...
    -- On récupère la colonne calculée depuis la jointure LATERAL
    COALESCE(t.TAG_LIST, '') as TAGS, 
    ...
FROM EQUIPMENT equ
JOIN BASE bas on bas.base_id = equ.base_id
LEFT JOIN LATERAL (
    SELECT STRING_AGG(tg.LABEL, '|') as TAG_LIST
    FROM TAGS tg
    WHERE tg.EQUIPMENT_ID = equ.EQUIPMENT_ID
) t ON true
WHERE equ.EQUIPMENT_ID in (#equipmentIds.rownum#);
```
*Note : Dans cette exemple, on utilise le LATERAL qui est plus performant pour PostgreSQL*

La facette est ensuite automatique. 
ElasticSearch va 'découper' la valeur de la colonne tags suivant les |. Les majuscules et les espaces seront conservés.
Il va automatiquement peupler la facette avec les valeurs.


## [Search] La concaténation SQL de mes champs multi-valués dépasse les limites de la base
Quand le `string_agg`/`LISTAGG` atteint ses limites (taille maximale, lisibilité du SQL), déplacez l'assemblage en Java : `SearchLoader.loadData(SearchChunk)` est le point de construction des documents d'index — chargez les sous-entités du chunk et construisez-y la chaîne (ou le champ multi-valué).

## [DataStore] Mon entité d'authentification (credential) doit-elle être une liste de référence ?
Non. Ne déclarez jamais l'entité de credential dans un `MasterDataDefinitionProvider` : cela casse l'authentification (le login échoue silencieusement, réponse vide ou 404).
Gardez cette entité en dehors des données de référence.

## [Orchestra] Une activité Orchestra passe en ABORTED alors que le code n'a pas échoué
**Symptôme** : L'activité se termine avec `status: "ok"` dans le workspace, mais son état en base est `ABORTED`. Message : `DbProcessExecutorPlugin - Error in activity state, activity execution N is already terminated`.

**Cause** : Un daemon long (>60s) bloque le pool de threads daemon partagé (2 threads par défaut). Le heartbeat du daemon orchestra n'est plus mis à jour, et un autre nœud considère le nœud comme mort.

**Solutions** :
1. Rechercher vos daemons longs (>60s) via le dashboard analytics (`/dashboard`, healthcheck `poolUtilization`)
2. Si nécessaire, augmenter `threadPoolSize` dans `boot.params` de `configuration.yaml` (4 recommandé minimum)
3. Sortir les traitements très longs du pool daemon (exécuter dans un thread dédié)


## [Config] Liquibase : erreur de checksum au démarrage après une régénération
Liquibase mémorise le **md5sum** de chaque `changeSet` déjà appliqué et le compare à chaque démarrage.
Ne référencez donc jamais un fichier régénérable (sortie de génération studio, `javagen/sqlgen/…`) : dès qu'il évolue, toute base déjà migrée refuse de démarrer (*checksum mismatch*).
Copiez le script de création dans un dossier **figé** et versionné (par exemple `src/main/resources/sql/`), et ne modifiez plus un `changeSet` déjà livré (créez-en un nouveau à la place).


## [Config] Certaines features doivent-elles être activées même si je ne les utilise pas directement ?
Oui, dès qu'un composant que vous utilisez injecte un manager de façon non optionnelle.
Par exemple, le contrôleur générique d'autocomplete (`io.vertigo.ui.controllers.ListAutocompleteController`) injecte le `CollectionsManager` : la feature `dataFactory` (nue, sans plugin d'index) est donc requise dès qu'un `vu:autocomplete` est présent, sans pour autant tirer Lucene ou Elasticsearch.
De même, le stockage des *Account* par le *StoreManager* (`account.store.store`) injecte un `FileStoreManager` non optionnel : la feature `filestore` (nue) est nécessaire même sans gestion de fichiers.


## [Sécurité] Comment empêcher deux sessions simultanées avec le même login ?
Rien de natif dans Vertigo. Pattern applicatif : maintenir dans un composant une `ConcurrentHashMap<String, UserSession>` login → session ; au login, invalider (`logout()`) la session précédente du même login avant d'enregistrer la nouvelle.
!> En multi-nœuds, cette map est locale à chaque JVM : il faut une affinité de session, ou externaliser cet état (base, cache partagé) pour que la règle soit globale.

## [Sécurité] Comment mettre en place un SSO Windows (l'utilisateur ne saisit pas de mot de passe) ?
Privilégiez les protocoles standards, outillés nativement dans vertigo-vega : `OIDCWebAuthenticationPlugin`, `AzureAdWebAuthenticationPlugin` et `SAML2WebAuthenticationPlugin` (features `authentication.oidc`, `authentication.aad`, `authentication.saml2`). Avec un annuaire AD / Entra ID, OIDC ou SAML2 fournit le SSO sans rien gérer côté application.
En legacy intranet pur (pas d'IdP disponible) : Kerberos/SPNEGO géré par un frontal (Apache/IIS) ou par Tomcat (`tomcatAuthentication="false"` sur le connecteur AJP), puis récupération de l'identité via `request.getRemoteUser()` dans le plugin d'authentification. NTLM est déprécié par Microsoft : ne pas construire dessus.

## [Config] Déconnexions intermittentes de la base ou d'ElasticSearch (après une période d'inactivité)
Cause classique : un firewall entre l'application et la base/ES coupe les connexions TCP inactives (souvent 10 à 20 min), alors que le keepalive TCP par défaut de l'OS est à 2 h — la connexion morte n'est détectée qu'à la première utilisation suivante.
Symptômes : erreurs IO / `ConnectException` HTTP avec le client REST ElasticSearch ; `NoNodeAvailableException` avec l'ancien TransportClient (connecteur `elasticsearch_7_17`) ; erreurs JDBC sur connexion invalide.
Remèdes :
- abaisser le keepalive TCP de l'OS sous le délai de coupure du firewall ;
- PostgreSQL : `tcp_keepalives_idle = 600` côté serveur ;
- activer la validation des connexions à l'emprunt dans le pool JDBC.

## [Config] Un audit exige que le mot de passe de la base ne soit pas stocké en clair — quelles options ?
Rappel préalable : le mot de passe ne vit de toute façon pas dans le YAML versionné — il dépend de l'environnement et est résolu par le paramManager depuis la configuration de l'hébergeur (fichier de propriétés externe, variables d'environnement via `EnvParamPlugin`).
Si l'exigence est « pas en clair sur le disque du serveur », les options dépendent du déploiement :
- la réponse robuste, valable partout : l'authentification par **certificat** (aucun mot de passe), supportée par la plupart des SGBD ; ou un coffre de secrets de l'hébergeur qui injecte la variable d'environnement au lancement ;
- en déploiement **Tomcat + JNDI** (`DataSourceConnectionProviderPlugin`, params `classname` et `source`) : la configuration de connexion vit dans le `context.xml` de Tomcat, et une `DataSourceFactory` surchargée peut décoder un mot de passe encodé ;
- en **Jetty embarqué** (le mode standard vertigo-ui), il n'y a pas de JNDI : le mot de passe arrive par la configuration externe. Encoder le fichier avec une clé posée sur la même machine n'est que de l'obfuscation — à assumer comme telle si l'audit s'en contente.

?> À garder en tête pour cadrer la discussion avec l'auditeur : dès lors que l'application démarre sans intervention humaine, tout ce qui permet de se connecter est accessible depuis la machine — aucun de ces mécanismes ne résiste à la compromission de la machine elle-même. Leur intérêt est ailleurs : éviter les fuites du fichier de configuration (sauvegardes, tickets, partages — un mot de passe en clair se copie-colle et se réutilise, pas un certificat), et limiter l'impact via rotation, credentials à courte durée de vie et révocation.

## [Config] Comment lancer un batch Vertigo en ligne de commande (hors webapp) ?
Un nœud Vertigo se démarre sans serveur web avec `AutoCloseableNode` (io.vertigo.core.node) :
```java
try (AutoCloseableNode node = new AutoCloseableNode(nodeConfig)) {
	final MyBatchServices batchServices = Node.getNode().getComponentSpace().resolve(MyBatchServices.class);
	batchServices.run(...);
}
```
La configuration YAML se charge via `YamlNodeConfigBuilder`. Packagez le batch en fat-jar Maven et utilisez picocli pour le parsing des arguments de la ligne de commande.
?> Pour un traitement récurrent planifié, préférez Orchestra à un cron externe : suivi des exécutions, reprise, et exécution portée par la webapp existante.

## [Config] Quelle convention pour nommer les loggers ?
Par défaut, un logger par classe (`LogManager.getLogger(MaClasse.class)`).
Vertigo utilise en complément des **catégories transverses** pour les préoccupations techniques : `sql` (requêtes SQL), `tasks` (exécution des Tasks), `health`, `metric`. Elles se pilotent directement dans la configuration log4j2 (par exemple passer `sql` en DEBUG pour tracer les requêtes).
?> Le plugin analytics `SmartLoggerAnalyticsConnectorPlugin` logge par catégorie et passe en ERROR au-delà du seuil `durationThreshold` (1000 ms par défaut) — pratique pour repérer les traitements lents sans noyer les logs.









