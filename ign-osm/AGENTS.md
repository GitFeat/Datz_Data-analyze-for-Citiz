# Instructions pour le module IGN / OSM

Ces instructions s'appliquent au dossier `ign-osm/` et à ses sous-dossiers.

## Accompagnement

- L'utilisateur est développeur et débute en données géographiques.
- Avancer avec lui progressivement, une étape à la fois, sans réaliser toutes les étapes suivantes d'un coup.
- Expliquer les termes géographiques et chaque nouveau concept avant de les utiliser.
- Rédiger et mettre à jour la documentation en français au fil des étapes réellement effectuées.
- Distinguer les étapes prévues des résultats effectivement obtenus.
- Utiliser les notebooks dans `notebooks/` comme parcours pédagogique principal, avec les explications en Markdown avant les cellules de code.
- Vérifier les notebooks dans l'ordre depuis un noyau neuf. L'utilisateur utilise l'extension Jupyter de VS Code ; ne pas installer JupyterLab pour ce parcours.
- Utiliser l'environnement local `.venv` du module comme noyau VS Code ; vérifier les dépendances dans cet interpréteur avant de proposer une installation. Ne pas forcer une installation dans le Python système.

## Code

- Utiliser l'anglais pour les noms de fichiers de code, variables, fonctions, classes, commentaires, docstrings et messages techniques.
- Privilégier un code simple et lisible, des noms explicites et des fonctions courtes avec un rôle clair.
- Préférer des étapes explicites aux expressions compactes difficiles à comprendre.
- Introduire uniquement les dépendances et abstractions nécessaires au besoin actuel.
- Conserver les noms propres et les valeurs des données sources ; documenter les éventuels renommages de colonnes.

## Documentation

- Garder le README centré sur l'objectif du module, les données, la procédure et les résultats.
- Placer les consignes destinées aux agents dans ce fichier.
