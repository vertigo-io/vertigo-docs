# Quarto

**Quarto** est le module de **conversion, export et publication documentaire** de la plateforme Vertigo.

Il fournit trois sous-systèmes indépendants :

- **Publisher** : Fusion de données métier dans des modèles de documents bureautiques (ODT, DOCX). Les modèles sont éditables depuis OpenOffice ou Microsoft Word.
- **Converter** : Conversion de documents d'un format vers un autre (ODT, DOC, DOCX, RTF, TXT vers PDF, …) grâce à OpenOffice (local ou distant) ou XDocReport.
- **Exporter** : Export de collections d'objets métier vers des formats utilitaires : CSV, PDF, RTF, XLS, XLSX, ODS.

## Publisher

### Présentation

**Publisher** a été conçu pour :

- Faciliter la création de documents type courrier au format bureautique : ODT, DOC, PDF
- Donner aux utilisateurs la possibilité de modifier les modèles en utilisant un logiciel bureautique (OpenOffice, Microsoft Word)

Publisher n'est pas prévu pour :

- Créer un export brut des données → utiliser le module **Exporter**
- Créer des rapports normalisés (Cerfa, …) → utiliser iText ou PDFBox
- Créer des rapports BI → utiliser Jasper, Birt, SSRS

### Principes

**Publisher** est basé sur le principe de la **fusion de documents** : il insère les données métier dans un document servant de modèle via une grammaire de tags (script).

  ![](./images/publisher-1.png)

!> Le document en sortie de fusion est donc dans le même format que le modèle. Ce document peut être converti dans un autre format grâce au module **Converter**.

### Création du modèle — OpenOffice

Les champs de fusion apparaissent surlignés en gris dans le document ODT.

![](./images/publisher_odt_1.png)

Pour modifier le champ il faut faire : Clic droit puis Champs et on obtient un navigateur nous permettant d'éditer tous les champs du modèle.

![](./images/publisher_odt_2.png)

Pour créer un champ : **Insertion → Champs → Autres** (ou Ctrl + F2), se placer dans l'onglet Fonctions :

![](./images/publisher_odt3.png)

Remplir le champ Annotation avec le nom du champ à fusionner puis cliquer sur Insérer :

![](./images/publisher_odt_4.png)

Pour ajouter un mot clé de type « opération », on utilise une insertion de script : **Insertion → Script** :

![](./images/publisher_odt_5.png)

### Création du modèle — Microsoft Word 2010

Ces mots clés et fonctions sont insérés dans le document word sous forme de champs, il n'y a pas de différence entre champs de fusion et opérations.
L'insertion de ces champs peut se faire par la commande « **Insertion / QuickPart / Champ** ».

Des raccourcis claviers peuvent aussi être utilisés :

- `Ctrl-F9` : Ajout d'un champ
- `Alt-F9` : Affiche/masque le contenu des champs

### Installation et mise en place

* Ajouter les dépendances quarto dans pom.xml et lancer mvn install :

```xml
<dependency>
	<groupId>io.vertigo</groupId>
	<artifactId>vertigo-quarto</artifactId>
	<version>${vertigo.version}</version>
</dependency>
```

Pour l'utilisation du plugin XDocReportConverterPlugin (gestion du DOCX) :
```xml
<dependency>
    <groupId>fr.opensagres.xdocreport</groupId>
    <artifactId>fr.opensagres.xdocreport.converter.docx.xwpf</artifactId>
    <version>2.1.0</version>
</dependency>
```

Pour l'utilisation du plugin OpenOfficeLocalConverterPlugin (gestion de l'ODT en local) :
```xml
<dependency>
	<groupId>fr.opensagres.xdocreport</groupId>
	<artifactId>fr.opensagres.xdocreport.converter.odt.odfdom</artifactId>
	<version>2.1.0</version>
</dependency>
```

* Définir le provider Java qui contiendra les fichiers de définition du modèle :

```xml
<module name="myApp-ressources">
	<definitions>
            <provider class="fr.projet.appli.MyPublisherDefinitionProvider" />
	</definitions>
</module>
```

* Ajouter le module dans foundation.xml :

```xml
<module name="vertigo-quarto">
	<component api="PublisherManager" class="io.vertigo.quarto.publisher.impl.PublisherManagerImpl">
		<plugin class="io.vertigo.quarto.plugins.publisher.odt.OpenOfficeMergerPlugin"/>
	</component>
</module>
```

### Syntaxe des modèles

Deux implémentations existent : **ODT** (OpenOffice) et **DOCX** (Microsoft Word). La syntaxe des mots clés diffère légèrement :

| Operation | Syntaxe ODT | Syntaxe DOCX |
|---|---|---|
| Champ de fusion | `<#=nomChamp#>` | `{=nomChamp}` |
| Champ objet | `<#=nomObjet.nomChamp#>` | `{=nomObjet.nomChamp}` |
| Condition | `<#if nomChamp#>` … `<#endif#>` | `{if nomChamp}` … `{endif}` |
| Condition inverse | `<#ifnot nomChamp#>` … `<#endifnot#>` | `{ifnot nomChamp}` … `{endifnot}` |
| Condition sur code | `<#ifequals champ = "CODE"#>` … `<#endifequals#>` | `{ifequals champ = "CODE"}` … `{endifequals}` |
| Condition inverse code | `<#ifnotequals champ = "CODE"#>` … `<#endifnotequals#>` | `{ifnotequals champ = "CODE"}` … `{endifnotequals}` |
| Champ de fusion boucle | `<#loop maVariable : nomCollection#>`<br/>`  <#=nomChamp #>`<br/>`<#endloop#>` | `{loop maVariable : nomCollection}`<br/>`  {=nomChamp}`<br/>`{endloop}` |
| Parcours d'un objet seul 	| `<#var maVariable : nomObjet#>`<br/>`  <#=nomChamp #>`<br/>`<#endvar#>` | *Non implémenté* |
| Image | `<#image nomImage#>` | Non implémenté |

### Sous OpenOffice

Les champs de fusion apparaissent surlignés en gris. Pour créer un champ : **Insertion → Champs → Autres** (Ctrl+F2) → onglet Fonctions → remplir le champ Annotation.

Pour les tags opérationnels (if, loop, …) : **Insertion → Script**.

Pour les images : placer une image dans le modèle. Cette image servira pour définir la taille maximum de l'image qui sera fusionner. Le ratio de l'image fusionnée sera conservé.
Puis il faut nommer l'image : Click-droit sur l'image -> Propriétés -> Options -> Remplir le Nom : `<#image IMAGE_FIELD_NAME>`

### Sous Microsoft Word

Les champs s'insèrent via **Insertion → QuickPart → Champ** (`Ctrl+F9`), affichage `Alt+F9`.

### Définition du dictionnaire

Les champs du modèle doivent correspondre à un dictionnaire de mot prévu par le système. Ce dictionnaire est nommé PublisherDefinition.
Une PublisherDefinition est constituée d'une PublisherNode racine.

Un PublisherNode est constitué de champs et est réutilisable, dans d'autre PublisherDefinition par exemple.
Les champs peuvent être de 5 types :

| Syntaxe | Description | Exemple |
| --- 					| --- | --- |
| stringField | Champ de type chaine de caractères | `stringField nom {}` |
| booleanField | Champ de type booléen | `booleanField siGrave {}`  |
| dataField 			| Champ de type PublisherNode | `dataField emetteur { type : PnPersonne }` |
| listField 			| Champ de type liste de PublisherNode | `listField destinataires { type : PnPersonne }` |
| imageField 			| Champ de type image (doit être un VFile) | `imageField logo` |

#### Exemple de définition

```java
public final class MyPublisherDefinitionProvider implements SimpleDefinitionProvider {

    private static PublisherDataDefinition createTestEnquete() {
        final PublisherNodeDefinition ville = new PublisherNodeDefinitionBuilder()
                .addStringField("nom")
                .addStringField("codePostal")
                .build();

        final PublisherNodeDefinition address = new PublisherNodeDefinitionBuilder()
                .addStringField("rue")
                .addNodeField("ville", ville)
                .build();

        final PublisherNodeDefinition enqueteur = new PublisherNodeDefinitionBuilder()
                .addStringField("nom")
                .addStringField("prenom")
                .addNodeField("adresseRatachement", address)
                .build();

        final PublisherNodeDefinition misEnCause = new PublisherNodeDefinitionBuilder()
                .addBooleanField("siHomme")
                .addStringField("nom")
                .addStringField("prenom")
                .addListField("adresseConnues", address)
                .build();

        final PublisherNodeDefinition publisherNodeDefinition = new PublisherNodeDefinitionBuilder()
                .addBooleanField("enqueteTerminee")
                .addStringField("codeEnquete")
                .addNodeField("enqueteur", enqueteur)
                .addListField("misEnCause", misEnCause)
                .addStringField("fait")
                .addBooleanField("siGrave")
                .build();

        return new PublisherDataDefinition("PuEnquete", publisherNodeDefinition);
    }

    @Override
    public List<Definition> provideDefinitions(final DefinitionSpace definitionSpace) {
        return new ListBuilder<Definition>()
                .add(createTestEnquete())
                .build();
    }
}
```

### Utilisation

Le cas d'usage le plus simple suit les étapes suivantes :

1. Récupération des données
2. Création d'un PublisherData correspondant au modèle
3. Peuplement du PublisherData à partir des données de la base
4. Récupération du Model de document
5. Création du document à partir du modèle et des données
6. Sauvegarde du document résultat

Voici le code résultant :

```java
public void testMergerSimple() {
    final MyData myData = loadMyData();
    final PublisherData publisherData = createPublisherData("PuMyPublish");
    PublisherDataUtil.populateData(myData, publisherData.getRootNode());
    final URL modelFileURL = resourceManager.resolve(DATA_PACKAGE + "MyModel.odt");
    final VFile result = publisherManager.publish(OUTPUT_PATH + "MyPublish.odt", modelFileURL, publisherData);
    // Ne pas oublier de sauver le fichier (c'est un fichier temporaire qui sera purgé)
    save(result);
}

private static PublisherData createPublisherData(final String definitionName) {
    final PublisherDataDefinition publisherDataDefinition = Node.getNode().getDefinitionSpace().resolve(definitionName, PublisherDataDefinition.class);
    Assert.assertNotNull(publisherDataDefinition);
    final PublisherData publisherData = new PublisherData(publisherDataDefinition);
    Assert.assertNotNull(publisherData);
    return publisherData;
}
```

## Converter

Le **Converter** permet de convertir un document d'un format vers un autre.

### Plugins disponibles

| Plugin | Activé par | Description |
|---|---|---|
| `OpenOfficeLocalConverterPlugin` | `converter.localOpenOffice` | Conversion via OpenOffice installé localement |
| `OpenOfficeRemoteConverterPlugin` | `converter.remoteOpenOffice` | Conversion via un serveur OpenOffice distant |
| `XDocReportConverterPlugin` | `converter.xDocReport` | Conversion via XDocReport (formats supportés : DOC, DOCX, ODT, RTF, TXT vers PDF) |

`MimeTypesFileTypeDetector` détecte automatiquement le type de fichier à partir du MIME type.

## Exporter

L'**Exporter** permet d'exporter des collections (`DtList`) ou objets métier vers des formats tabulaires ou document : CSV, PDF, RTF, XLS, XLSX, ODS.

### Plugins disponibles

| Plugin | Activé par | Format |
|---|---|---|
| `CSVExporterPlugin` / `CSVExporter` | `exporter.csv` | CSV |
| `PDFExporterPlugin` / `PDFExporter` | `exporter.pdf` | PDF (via iText) |
| `RTFExporterPlugin` / `RTFExporter` | `exporter.rtf` | RTF |
| `XLSExporterPlugin` | `exporter.xls` | XLS (@Deprecated) |
| `XLSXExporterPlugin` | `exporter.xlsx` | XLSX |
| `ODSExporterPlugin` | `exporter.ods` | ODS |

### Modèle d'export

```java
final List<ExportField> fields = List.of(
    new ExportField(artId, LocaleMessageText.of("ID")),
    new ExportField(title, LocaleMessageText.of("Titre")),
    new ExportField(quantity, LocaleMessageText.of("Quantité"))
);

final ExportSheet sheet = new ExportSheet(
    "Catalogue",
    fields,
    null,
    articlesDtList
);

final Export export = new Export(
    ExportFormat.CSV,
    "articles.csv",
    "Export des articles",
    "MonApp",
    Export.Orientation.Portrait,
    List.of(sheet)
);

final VFile result = exporterManager.createExportFile(export);
```

L'objet `Export` peut contenir plusieurs `ExportSheet`. Chaque colonne est un `ExportField` (ou `ExportDenormField`, `ExportCustomField`).

## Pour les experts

### Managers

| Manager | Rôle | Activé par |
|---|---|---|
| `ConverterManager` | Conversion de documents entre formats | `converter` |
| `ExporterManager` | Export de données vers fichiers tabulaires/documents | `exporter` |
| `PublisherManager` | Fusion de données dans modèles de documents | `publisher` |

### Plugins Converter

| Plugin | Usage |
|---|---|
| `OpenOfficeLocalConverterPlugin` | Conversion via OpenOffice local |
| `OpenOfficeRemoteConverterPlugin` | Conversion via serveur OpenOffice distant |
| `XDocReportConverterPlugin` | Conversion via XDocReport (`ConverterFormat` enum) |

### Plugins Exporter

| Plugin | Format |
|---|---|
| `CSVExporterPlugin` / `CSVExporter` | CSV |
| `PDFExporterPlugin` / `PDFExporter` / `PDFAdvancedPageNumberEvents` / `AbstractExporterIText` | PDF (iText) |
| `RTFExporterPlugin` / `RTFExporter` | RTF |
| `XLSExporterPlugin` | XLS (@Deprecated) |
| `XLSXExporterPlugin` | XLSX |
| `ODSExporterPlugin` | ODS |

### Plugins Publisher

| Plugin | Formats | Classes associées |
|---|---|---|
| `OpenOfficeMergerPlugin` | ODT | `ODTCleanerProcessor`, `ODTImageProcessor`, `ODTUtil`, `ODTValueEncoder` |
| `DOCXMergerPlugin` | DOCX | `DOCXCleanerProcessor`, `DOCXUtil`, `DOCXValueEncoder` |

### Modèle Publisher

| Classe | Description |
|---|---|
| `PublisherData` | Données à fusionner, liées à un `PublisherDataDefinition` |
| `PublisherNode` | Nœud contenant des champs typés |
| `PublisherDataDefinition` | Définition nommée d'un schéma de publication |
| `PublisherNodeDefinition` / `PublisherNodeDefinitionBuilder` | Définition d'un nœud |
| `PublisherField` / `PublisherFieldType` (enum) | Champ du nœud |

### Moteur de script Publisher (Merger)

| Classe | Rôle |
|---|---|
| `ScriptContext` | Contexte d'exécution du script |
| `ScriptGrammar` | Grammaire des tags |
| `ScriptHandlerImpl` | Moteur principal du merger |
| `ScriptTag` / `ScriptTagContent` / `ScriptTagDefinition` | Représentation d'un tag |
| `AbstractScriptTag` | Implémentation de base des tags |
| `ScriptGrammarUtil` | Utilitaires de grammaire |

#### Tags de la grammaire

| Tag | Classe | Description |
|---|---|---|
| `<#loop … #>` | `TagFor` | Boucle sur une collection |
| `<#var … #>` | `TagObject` | Parcours d'un objet |
| `<#if … #>` | `TagIf` | Condition booléenne |
| `<#ifequals … #>` | `TagIfEquals` | Condition sur code |
| `<#ifnot … #>` | `TagIfNot` | Condition inverse |
| `<#ifnotequals … #>` | `TagIfNotEquals` | Condition inverse sur code |
| `<#=champ#>` | `TagEncodedField` | Champ de fusion |
| `<#block#>` | `TagBlock` | Bloc de tags |

#### Processors

| Processor | Rôle |
|---|---|
| `MergerProcessor` | Orchestration du pipeline de fusion |
| `MergerScriptEvaluatorProcessor` | Evaluation des scripts/tags |
| `GrammarEvaluatorProcessor` | Evaluation de la grammaire |
| `GrammarXMLBalancerProcessor` | Equilibrage des tags XML |
| `ParserXMLHandler` | Parsing XML du document |
| `ProcessorXMLUtil` / `TagXML` / `ZipUtil` | Utilitaires de traitement |

### Modèle Exporter

| Classe | Description |
|---|---|
| `Export` (record) / `ExportBuilder` | Description d'un export (format, nom, titre, auteur, orientation, feuilles) |
| `ExportFormat` (enum) | Formats de sortie : CSV, PDF, RTF, XLS, XLSX, ODS |
| `ExportSheet` | Feuille de l'export (titre, colonnes, données) |
| `ExportField` / `ExportDenormField` / `ExportCustomField` | Colonnes de l'export |
| `ExportHelper` | Utilitaires de construction d'export |
| `ExporterUtil` | Utilitaires généraux de l'exporter |

### Modèle Converter

| Classe | Description |
|---|---|
| `ConverterPlugin` | Interface des plugins de conversion |
| `MimeTypesFileTypeDetector` | Détection du type de fichier par MIME |

### Features (@Feature)

| Flag | Composants |
|---|---|
| `converter` | `ConverterManager` |
| `converter.localOpenOffice` | `OpenOfficeLocalConverterPlugin` |
| `converter.remoteOpenOffice` | `OpenOfficeRemoteConverterPlugin` |
| `converter.xDocReport` | `XDocReportConverterPlugin` |
| `exporter` | `ExporterManager` |
| `exporter.csv` | `CSVExporterPlugin` |
| `exporter.pdf` | `PDFExporterPlugin` |
| `exporter.rtf` | `RTFExporterPlugin` |
| `exporter.xls` | `XLSExporterPlugin` (@Deprecated) |
| `exporter.xlsx` | `XLSXExporterPlugin` |
| `exporter.ods` | `ODSExporterPlugin` |
| `publisher` | `PublisherManager` |
| `publisher.odt` | `OpenOfficeMergerPlugin` |
| `publisher.docx` | `DOCXMergerPlugin` |

### Configuration YAML

```yaml
io.vertigo.quarto.QuartoFeatures:
    features:
        - converter:
        - exporter:
        - publisher:
    featuresConfig:
        - converter.localOpenOffice:
              openOfficePath: "/usr/lib/openoffice"
        - exporter.csv:
              separator: ";"
        - exporter.pdf:
        - publisher.odt:
        - publisher.docx:
```
