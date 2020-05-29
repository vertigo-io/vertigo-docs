# Saisie texte

Saisir du texte dans une application de gestion est assez fréquent.
Ce type de saisie est utilisée lorsque l'information concernée ne peut pas être standardisé et donc choisie par l'utilisateur dans une liste pré-établie.

Une saisie textuelle est donc une saisie libre de l'utilisateur. En revanche cela ne signifie pas qu'elle est dénuée de contrôles.
Nous avons selectionné trois type de saisie textuelle :

- la saisie sur une ligne
- la saisie sur plusieurs lignes
- la saisie dans un éditeur texte-riche (WYSYWYG)

Les controles qui peuvent s'appliquer peuvent-être de nature très diverses mais on peut en citer quelques uns :

- longueur maximale
- longueur minimale
- format imposé (majuscule, minucule, expression régulière...)
- caractères interdits

Ces champs supportent le copier/coller.

# Bonnes pratiques

- La saisie sur une ligne doit être le choix par défaut
- Lorsque vous utilisez une saisie sur plusieurs lignes prévoyez une nombre de ligne suffisant par rapport à la quantité d'information attendue. (3-4 lignes pour une zone de commentaires, ~10 lignes pour une saisie plus conséquente)
- N'utilisez l'éditeur texte-riche qu'en cas de réelle nécessité car la structure de stockage de l'information la rend plus difficilement exploitable
- Lorsqu'un format doit être respecté et qu'il n'est pas trivial fournissez à l'utilisateur la règles à respecter (via un masque de saisie, un placeholder ou un "hint")
- Lorsque vous souhaitez donner accès à une information textuelle en lecture, priviligiez l'utilisation du composant en mode "consultation" plutôt que sur le composant en mode "edition" desactivé.
- Quand il existe une option navitement supportée par HTML5 pour votre besoin priviligiez là toujours par rapport à du code specifique ou une fonction fournie par la bibliotèque de composants afin d'améliorer la sécurité et la compatibilité de votre application.


# Design & Try me

<iframe src="/design-system/iframes/molecules/text-input.html" height="1000px" scrolling="no" style="border:none;" ></iframe>