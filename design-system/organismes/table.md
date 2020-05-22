# Tableau

Un tableau est une très bonne manière de présenter beaucoup d'information dans un espace restreint.
Ils sont très utile pour densifier l'affichage et ainsi permettre aux utilisateurs de visualiser beaucoup d'informations en peu de temps et sans "scroller" ou naviguer.
Les tableaux permettent également de facilement comparer plusieurs lignes entre elles et sont donc des facilitateurs pour le métier de vos utilisateurs.
Ils possèdent en général des fonctions de pagination et de tri.
Il est également possible de proposer des actions sur chaque ligne de manière contextuelle à l'élement.

Nous avons fait le choix de faire en sorte qu'un tableau puisse avoir un rendu similaire au bloc pour qu'ils puissent être placés à proximité (en général au-dessus ou en en-dessous) d'un bloc ou d'un autre tableau.
Ils peuvent donc avoir un titre optionnel ainsi que des actions en haut à droite.

Dans certain cas il peut être utile de pouvoir selectioner certains lignes dans ce cas une case à cocher de selection est présente dans une première colonne dédiée.


# Bonnes pratiques

- Ils ont les inconvénients de leurs avantages et sont donc a utiliser préférentiellement pour des applications utilisése massivement sur ordinateur de bureau
- Priviligiez un alignement à gauche pour toutes les données textuelles
- Priviligiez un alignement à droite pour toutes les données numériques
- Limiter le nombre d'actions disponibles en haut à droit(<3), pour les actions complexes préférez une navigation vers un écran dédié
- Limiter le nombre d'actions disponibles par ligne(<3), pour les actions complexes préférez une navigation vers un écran dédié
- Priviligiez un affichage des actions par ligne au survol de la ligne afin de ne pas surcharger l'affichage avec des éléments redondants.


# Design

<iframe src="/design-system/iframes/organismes/table.html" height="1600px" scrolling="no" style="border:none;" ></iframe>