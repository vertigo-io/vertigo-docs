# Quarto

**Quarto** est le module de **conversion, export et publication documentaire** de Vertigo.

Il fournit trois sous-systèmes indépendants :

- **Publisher** : Fusion de données métier dans des modèles de documents bureautiques (ODT, DOCX). Les modèles sont éditables depuis OpenOffice ou Microsoft Word.
- **Converter** : Conversion de documents d'un format vers un autre (ODT, DOC, DOCX, RTF, TXT → PDF, … ) grâce à OpenOffice (local ou remote) ou XDocReport.
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

Le document en sortie est dans le même format que le modèle. Pour obtenir un autre format (ex. PDF), utiliser le module **Converter**.

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
| Boucle sur liste | `<#loop var : collection#>` … `<#endloop#>` | `{loop var : collection}` … `{endloop}` |
| Parcours objet | `<#var var : objet#>` … `<#endvar#>` | Non implémenté |
| Image | `<#image nomImage#>` | Non implémenté |

### Sous OpenOffice

Les champs de fusion apparaissent surlignés en gris. Pour créer un champ : **Insertion → Champs → Autres** (Ctrl+F2) → onglet Fonctions → remplir le champ Annotation.

Pour les tags opérationnels (if, loop, …) : **Insertion → Script**.

Pour les images : placer une image dans le modèle, puis clic droit → Propriétés → Options → Nom : `<#image IMAGE_FIELD_NAME>`.

### Sous Microsoft Word

Les champs s'insèrent via **Insertion → QuickPart → Champ** (`Ctrl+F9`), affichage `Alt+F9`.

### Définition du dictionnaire

Les champs du modèle doivent correspondre à un `PublisherDataDefinition` constitué d'un `PublisherNode` racine. Types de champs :

| Type de champ | Description |
|---|---|
| `stringField` | Chaîne de caractères |
| `booleanField` | Booléen |
| `nodeField` (`dataField`) | Sous-nœud de type `PublisherNode` |
| `listField` | Liste de `PublisherNode` |
| `imageField` | Image (`VFile`) |

#### Exemple de définition

```java
final PublisherNodeDefinition ville = new PublisherNodeDefinitionBuilder()
        .addStringField("nom")
        .addStringField("codePostal")
        .build();

final PublisherNodeDefinition address = new PublisherNodeDefinitionBuilder()
        .addStringField("rue")
        .addNodeField("ville", ville)
        .build();

final PublisherDataDefinition pubDef = new PublisherDataDefinition("PuEnquete",
    new PublisherNodeDefinitionBuilder()
        .addBooleanField("enqueteTerminee")
        .addStringField("codeEnquete")
        .addNodeField("enqueteur", enqueteur)
        .addListField("misEnCause", misEnCause)
        .build()
);
```

### Utilisation

```java
final PublisherData publisherData = createPublisherData("PuMyPublish");
PublisherDataUtil.populateData(myData, publisherData.getRootNode());
final URL modelFileURL = resourceManager.resolve("MyModel.odt");
final VFile result = publisherManager.publish("MyPublish.odt", modelFileURL, publisherData);
```

## Converter

Le **Converter** permet de convertir un document d'un format vers un autre.

### Plugins disponibles

| Plugin | Activé par | Description |
|---|---|---|
| `OpenOfficeLocalConverterPlugin` | `converter.localOpenOffice` | Conversion via OpenOffice installé localement |
| `OpenOfficeRemoteConverterPlugin` | `converter.remoteOpenOffice` | Conversion via un serveur OpenOffice distant |
| `XDocReportConverterPlugin` | `converter.xDocReport` | Conversion via XDocReport (formats supportés : DOC, DOCX, ODT, RTF, TXT → PDF) |

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
    "Catalogue",    // titre du feuillet
    fields,         // colonnes
    null,           // single DataObject (XOR avec DtList)
    articlesDtList  // DtList à exporter
);

final Export export = new Export(
    ExportFormat.CSV,       // format
    "articles.csv",         // nom de fichier
    "Export des articles",  // titre
    "MonApp",               // auteur
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
| `ConverterManager` (`ConverterManagerImpl`) | Conversion de documents entre formats | `converter` |
| `ExporterManager` (`ExporterManagerImpl`) | Export de données vers fichiers tabulaires/documents | `exporter` |
| `PublisherManager` (`PublisherManagerImpl`) | Fusion de données dans modèles de documents | `publisher` |

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

### Model Converter

| Classe | Description |
|---|---|
| `ConverterPlugin` | Interface des plugins de conversion |
| `MimeTypesFileTypeDetector` | Détection du type de fichier par MIME |

### Features (@Feature)

| Flag | Composants |
|---|---|
| `converter` | `ConverterManager` + `ConverterManagerImpl` |
| `converter.localOpenOffice` | `OpenOfficeLocalConverterPlugin` |
| `converter.remoteOpenOffice` | `OpenOfficeRemoteConverterPlugin` |
| `converter.xDocReport` | `XDocReportConverterPlugin` |
| `exporter` | `ExporterManager` + `ExporterManagerImpl` |
| `exporter.csv` | `CSVExporterPlugin` |
| `exporter.pdf` | `PDFExporterPlugin` |
| `exporter.rtf` | `RTFExporterPlugin` |
| `exporter.xls` | `XLSExporterPlugin` (@Deprecated) |
| `exporter.xlsx` | `XLSXExporterPlugin` |
| `exporter.ods` | `ODSExporterPlugin` |
| `publisher` | `PublisherManager` + `PublisherManagerImpl` |
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
