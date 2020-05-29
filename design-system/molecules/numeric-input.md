# Saisie numérique

Il existe plusieurs façons de saisir et représenter un format numérique sur le web.
Cette section n'a pas vocation a être exhautive ni à traiter la problématique de la visualisation de données (Dataviz, Graphiques, etc...)

Nous proposons différentes méthodes qui permettent à la fois la saisie et la consultation de données numériques unitaires.
Elles sont au nombre de trois :

- via un champ texte sur une ligne
- via un potentiomètre rotatif virtuel (knob)
- via un potentiomètre linéaire virtuel (slider)

Ces trois méthodes permettent de contrôler les valeurs minimales et maximales autorisées ainsi que la précision demandée.
Lors de la saisie textuelle d'une valeur numérique Vertigo fera automatiquement une vérification de la validité de la valeur et affichera un message d'erreur le cas échéant.

# Bonnes pratiques

- Lors de la saisie d'une donnée numérique il peut être important de préciser l'unité attendue
- Les potentiomètres nécessitent toujours la définition d'une valeur minimale et maximale
- Lors d'une saisie via un potentiomètre virtuel veillez toujours à ce que la précision soit compatible avec la capacité de saisie. Un réglage trop fin et des valeurs ne seront pas saisissables, à contrario un réglage trop grossier destabilisera l'utilisateur. Vertigo règle par défaut ces potentiomètres à partir de bornes min et max afin que 200 valeurs soit selectionnables. Ceci est évidemment surchargeable.


# Design & Try me

<iframe src="/design-system/iframes/molecules/numeric-input.html" height="1000px" scrolling="no" style="border:none;" ></iframe>