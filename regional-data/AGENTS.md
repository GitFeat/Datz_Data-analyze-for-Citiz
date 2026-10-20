# Instructions pour le livrable régional

Ces règles s'appliquent à `regional-data/` et ses sous-dossiers.

- L'utilisateur est développeur et débute en données géographiques : expliquer les concepts dans les cellules Markdown avant le code.
- Utiliser les notebooks comme parcours principal et mettre à jour la documentation avec les résultats réels.
- Le code, les identifiants, commentaires et messages techniques sont en anglais ; la documentation pédagogique est en français.
- Privilégier des fonctions simples avec un rôle clair et des noms explicites.
- Utiliser le noyau existant Python (IGN / OSM), fourni par `ign-osm/.venv`, sans créer d'environnement supplémentaire ni installer JupyterLab.
- Préserver les fichiers de l'équipe et les notebooks pédagogiques du dossier `ign-osm/`.
- Le périmètre du livrable est toute l'Auvergne-Rhône-Alpes, avec une marge de 1 km pour les comptages autour des stations proches des frontières.
- Conserver les identifiants `station_uid` et les identifiants OSM pour les jointures et la traçabilité.
- Ne jamais remplacer une donnée manquante par zéro. Distinguer les objets OSM recensés des capacités, bornes ou places réelles.
- Documenter les catégories, rayons, règles de dédoublonnage, sources, dates et limites.
- Exécuter les notebooks depuis un noyau neuf et vérifier les exports avant de déclarer le livrable terminé.
