# Saisie de date

Saisir une date peut sembler trivial au premier abord mais cela peut se réveler très complexe si les concepts afférents ne sont pas maitrisés.
Tentons de présenter cela de manière concise.
Il existe deux grandes familles de données qui apportent des informations temporelles :

- les dates : qui sont issues d'un calendrier. Un calendrier est une représentation logique et humaine du temps qui dépend (entre autres) d'une localisation spatiale.
- les horodatages (timestamp ou instant en anglais) : qui représente de manière universelle un point sur l'échelle du temps

Il est possible de "projeter" un horodatage en date en lui adjoignant une zone de temps (timezone en anglais)
Cette projection est toujours un choix métier : le choix de la zone à utiliser peut être la zone de l'utilisateur qui consulte la donnée ou une information portée par le contexte métier.

Une saisie utilisateur se fait à deux niveaux de précision :

- le jour
- la minute

Une précision à la seconde ou inférieure sera en général uniquement nécessaire en consultation.

Ainsi nous avons selectionné deux composants de saisie de données temporelles :

- date : qui permet de saisir une date au format jour/mois/année
- datetime : qui permet de saisir une heure et une date au format jour/mois/annee heure:minutes

Ces deux composants permettent la saisie selon deux modalités complémentaires :

- via une saisie texte pour les utilisateurs les plus avertis ou lorsque la date est connue à l'avance
- via un widget de selection 

Lorsqu'il est nécessaire d'un point de vue métier de saisir une information de zone de temps (timezone) nous privilégions de saisir cette information dans un autre champ.

Ces différents choix permettent de gérer les informations temporelles de manière cohérente et fiable sur toute la chaine, qui va de la saisie à la visualisation en passant par le transfert et le stockage.

# Bonnes pratiques

- Par défaut une date (précision au jour) est non zonée et doit etre considérée comme locale
- Par défaut une datetime (précision à la minute) est non zonée et doit etre considérée comme locale
- Lorsqu'une datetime (précision à la minute) doit être zonée c'est le serveur qui effectue la conversion en s'appuyant sur la logique métier.
- L'interface utilisateur manipule le concept de zone de temps (timezone) exclusivement dans des champs spécifiques indépendants des composants date et datetime


# Design

<iframe src="/design-system/iframes/molecules/date-input.html" height="700px" scrolling="no" style="border:none;" ></iframe>