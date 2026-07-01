# Sélection

Les composants de sélection permettent de saisir une valeur parmi une liste de choix possibles.
La saisie par l'utilisateur est alors parfaitement cadrée.

Ce type de composant de sélection intervient lorsque les choix sont mutuellement exclusifs et que l'utilisateur ne doit en choisir qu'une seule valeur parmi les alternatives proposées.

Nous avons sélectionné trois types de sélection

- les boutons "radio"
- la liste déroulante
- l'autocomplete 


Ces différents modes de sélection sont tous utilisables au clavier uniquement pour améliorer l'accessibilité.
Bon à savoir : le composant liste déroulante permet à l'utilisateur de taper les premières lettres afin de naviguer plus vite dans la liste.

# Bonnes pratiques

Le critère de choix principal d'un composant plutôt qu'un autre est la volumétrie des options possibles.
- Pour un nombre d'options restreint (<7) : privilégiez les boutons radio car ils permettent de voir l'ensemble des valeurs
- Pour un nombre d'options moyen (>7 et <100) : privilégiez la liste déroulante car c'est la plus simple d'utilisation et celle qui améliore la densité de l'écran
- Pour un nombre d'options très grand (>100) : privilégiez l'autocomplete car c'est le seul qui permette d'assurer de bonnes performances. Ce composant permet nativement une recherche de type "commence par" sur un gros volume de données
- L'ordre des options doit être reproductible et compréhensible. Nous privilégions l'ordre alphabétique.
- S'il n'y a pas d'intérêt particulier à utiliser une liste "radio", préférez, même dans le cas d'un nombre restreint d'options, la liste déroulante afin de densifier l'information.


# Design & Try me

<iframe src="/vertigo-docs/design-system/iframes/molecules/select-input.html" height="700px" scrolling="no" style="border:none;" ></iframe>