# Instructions pour le module Lakehouse

Ces règles s'appliquent à `lakehouse/` et à ses sous-dossiers.

- Ce module assemble le travail des autres modules en tables pour Microsoft Fabric. Il ne télécharge ni ne recalcule rien qui soit déjà produit ailleurs : il lit les sorties de `citiz/`, `regional-data/` et `population/`.
- Le code, les identifiants, commentaires et messages techniques sont en anglais ; la documentation est en français.
- Chaque table a une clé primaire vérifiée et ses clés étrangères contrôlées avant écriture.
- Ne reprendre que les colonnes exploitables ; documenter chaque colonne écartée dans `DATA_DICTIONARY.md`.
- Ne jamais remplacer une donnée manquante par zéro.
- Exécuter le notebook depuis un noyau neuf et mettre à jour le README avec les résultats réels.
