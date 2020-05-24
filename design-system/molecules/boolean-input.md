# Saisie booléenne

Une saisie booléenne représente une valeur binaire vraie ou fausse.
Pour ces types de données il est très important de choisir une méthode de rendu qui ne soit pas ambigüe pour les utilisateurs.

Ansi nous avons fait le choix de privilégier une unique manière de saisir ce type d'information via une case à cocher (checkbox)
Ce choix est motivé par trois raisons principales :

- c'est le choix historique du web, celui donc qui destabilisera le moins les utilisateurs quelles que soient leurs compétences en informatique
- c'est celui qui est le moins équivoque et donc le plus accessible
- il fonctionne de manière identique sur mobile et sur bureau via une pression/clic

# Bonnes pratiques

- Une valeur booléenne doit toujours être pré-initialisée. Certains langages de programmation autorise d'autres états (par exemple en utilisant la nullité). Nous déconseillons cette pratique.
- Lorsqu'une différence doit être faite entre une donnée non saisie et une valeur nulle, privilégiez un autre composant de selection non ambigu, par exemple un "radio" 


# Design

<iframe src="/design-system/iframes/molecules/boolean-input.html" height="300px" scrolling="no" style="border:none;" ></iframe>