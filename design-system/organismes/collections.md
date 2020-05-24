# Collections

Il est très fréquent de devoir afficher des collections d'éléments.

Nous avons sélectionné trois méthodes de visualisation des collections : 

- sous forme de liste de [cartes](design-system/organismes/cards.md)
- sous forme de liste de [lignes](design-system/organismes/items.md)
- sous forme de [tableau](design-system/organismes/table.md)

Ces trois méthodes de visualisation partage des fonctions communes de tri et de pagination.

Nous avons fait le choix structurant de privilégier : 

- le tri effectué par le serveur : car c'est le seul qui permette d'avoir un tri fiable et exhaustif sur des grandes collections
- la pagination effectuée par le client sur une liste de 250 éléments maximum : car c'est le seul qui permette une navigation très rapide et fluide.

Lorsque la collection concernée est petite (<250 éléments) il est possible d'effectuer le tri coté client.

Ces choix de design proviennent également de notre constat qu'un utilisateur navigue très rarement au delà du 100ème élément et que même s'il souhaite le faire cela lui fait perdre beaucoup de temps. Nous privilégions ainsi de fournir des outils à l'utilisateur pour qu'il puisse pré-filtrer les éléments, les trier par pertinence et caractéristiques et ainsi faire en sorte que l'information recherchée par l'utilisateur se situe en première page dans 90% des cas.
Ceci est notamment rendu possible par l'utilisation très simple de recherches full-text à facettes.


# Bonnes pratiques

- Toujours préférer le tri effectué par le serveur, seul tri fiable
- Ne jamais renvoyer plus de 250 éléments à l'utilisateur, les éléments supplémentaires ne seront pas lus et posent des problèmes de performance
- Avec en affichage en carte préférer l'affichage d'une page supplémentaire par appui sur un bouton de type "Voir plus"
- Avec en affichage en liste ou en tableau préférer une pagination classique par "numéro de page" et/ou  par des boutons "page précédente"/"page suivante"
- Indiquez en tete de liste le nombres d'élement totaux qui correspondent au critères renseignés


# Design

Vous pouvez trouver les différents design ici : [cartes](design-system/organismes/cards.md), [lignes](design-system/organismes/items.md), [tableau](design-system/organismes/table.md)