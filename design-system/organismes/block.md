# Bloc

Afin de structurer l'information dans une application il est très souvent utile de regrouper les informations qui sont réliées d'un point de vue métier et qui forment un ensemble cohérent.
Les blocs sont un bon moyen pour le faire.
Un bloc est constitué :

- d'un titre
- d'une zone d'actions optionelle en haut à droite
- d'une zone de contenu

Différents types de contenu peuvent être placés dans la zone prévue à cet effet : par exemple des champs de saisie ou de visualisation, des images, des graphiques, etc... 

# Bonnes pratiques

- Le titre du bloc doit être assez court et non ambigü
- Les actions placées sur un bloc doivent être contextuelles aux éléments contenues dans le bloc et doivent être en nombre limité (<3). 
- Nous déconseillons très fortement de d'utiliser les actions de bloc pour sauvegarder des modification ou passer en mode edition. En effet pour des raisons de sécurité et d'intégrité, il est préférable que ce basculement se fasse au niveau de la page car une page en édition et en consultation n'ont pas du tout la même structure technique (même si cela ne se voit pas pour l'utilisateur final). Il est tout à fait possible dans des cas exptionnels de déroger à cette règle, les impacts en terme de sécurité, de perte d'intégrité et le surcoût lié au développement sont à prendre en considération.
- La couleur du bloc doit constraster avec l'arrière plan de l'application et permettre une bonne lisibilité du contenu placé à l'intérieur. Nous préconisons le blanc.


# Design

<iframe src="/design-system/iframes/organismes/block.html" height="300px" scrolling="no" style="border:none;" ></iframe>