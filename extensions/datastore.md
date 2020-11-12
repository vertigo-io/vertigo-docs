
- **Cache** : Propose une abstraction vers la solution de cache pour les autres composants


- **cache.redis** : Utilise le `RedisConnector` pour mettre en place un cache partagé *(Nécessite le composant Redis)*
- **cache.memory** : Utilise la mémoire locale comme implémentation du cache *(comme les autres implé, l'éviction en TTL définit par le module consommateur)*
- **cache.eh** : Utilise la librairie EhCache *(Necessite le fichier de paramétrage `ehcache.xml`)*