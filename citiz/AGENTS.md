# Instructions pour le module Citiz

Ces règles s'appliquent à `citiz/` et à ses sous-dossiers.

- Le module est au stade de l'exploration : établir quelles données Citiz sont exploitables, et le documenter.
- Utiliser les notebooks numérotés de `notebooks/` comme parcours principal, avec les explications en Markdown avant les cellules de code.
- Le code, les identifiants, commentaires et messages techniques sont en anglais ; la documentation est en français.
- Privilégier des fonctions courtes avec un rôle clair et des noms explicites.
- Conserver `station_uid` (`source:station_id`) comme clé de jointure avec le travail de l'équipe.
- Ne jamais modifier `output/citiz_stations_geo.csv` ni `output/citiz_flux.csv` sans accord de l'équipe : `regional-data/` les lit et vérifie leur empreinte.
- Ne jamais remplacer une donnée manquante par zéro. Distinguer les valeurs sourcées, calculées et les hypothèses.
- Exécuter les notebooks dans l'ordre depuis un noyau neuf et mettre à jour le README avec les résultats réels.
