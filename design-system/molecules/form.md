# Formulaire

Dans les applications de gestion, les données occupent une place très importante.
Par extension, les formulaires de saisie sont très nombreux dans ce type d'application. Ils doivent permettre une saisie d'information :

- fiable
- fluide et ergonomique
- cohérente

Pour atteindre ces objectifs nous avons fait certains choix structurants.
Tout d'abord l'ensemble des composants de saisies (molécules) partagent des fonctionnalités communes : un libellé fixe, une gestion des messages d'erreur, d'aide à la saisie ainsi que deux modes de rendu : un rendu en mode edition et un rendu en mode consultation.

La capacité de chaque molécule à s'afficher selon les deux modes de rendu permet une cohérence maximale entre les page de saisie et les pages de consultation, l'utilisateur est ainsi parfaitement guidé dans son parcours. 

D'autre part l'intégralité des composants que nous avons selectionnés peuvent fonctionner uniquement avec le clavier pour une accessibilité améliorée.

# Bonnes pratiques

- Placez toujours à proximité les champs proches d'un point de vue fonctionnel
- Privilégiez les controles globaux côté serveur qui sont les seuls à même de garantir l'intégrité de l'application. Utilisez les contrôles de surface côté client en complément.
- Essayez de densifier au maximum l'affichage vous éviterez alors à vos utilisateurs des "scrolls" superflus.
- Le libellé doit être court et précis, toujours sur une seule ligne
- Privilégiez des aides à la saisie courte, sur une ligne ou placez les en dehors du champs de saisie
- Mentionnez toujours le caractère obligatoire d'un champ (ceci est géré automatiquement dans Vertigo, en cohérence avec le modèle) 

# Design & Try me

<iframe src="/vertigo-docs/design-system/iframes/molecules/form.html" height="1000px" scrolling="no" style="border:none;" ></iframe>