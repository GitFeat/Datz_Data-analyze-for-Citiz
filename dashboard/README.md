# Explorer les données Citiz

L’interface d’analyse est fournie par [PyGWalker](https://docs.kanaries.net/pygwalker), intégré à Streamlit. Aucun frontend spécifique à maintenir. L’explorateur permet de créer des graphiques et tableaux par glisser-déposer, de filtrer et de comparer les variables.

Depuis la racine du dépôt, utiliser l’environnement Python déjà présent :

```bash
ign-osm/.venv/bin/python -m pip install -r dashboard/requirements.txt
ign-osm/.venv/bin/python -m streamlit run dashboard/app.py --server.address 127.0.0.1
```

Ouvrir http://localhost:8501. Arrêter avec Ctrl+C. Les données sources ne sont pas modifiées. Les graphiques en cours restent en session ; ils ne sont pas automatiquement sauvegardés entre deux lancements.

## Données proposées

- **Stations et équipements croisés (AURA)** : la table finale de la release, `regional-data/data/release/citiz_aura_final.csv` : les indicateurs OSM par station, enrichis avec le département, le réseau, la capacité et l’instantané de disponibilité Citiz. La jointure `station_uid` est faite et contrôlée une seule fois, par `regional-data/notebooks/07_release_final_table.ipynb` ; `station_reference_match` indique si la référence a été retrouvée.
- **Stations Citiz (France)** : référentiel national enrichi.
- **Disponibilité Citiz** : instantané avec ses dates, sans reconstruction d’un historique.
- **Catalogue OSM** : lieux, familles, catégories et coordonnées. Table complète, sans échantillonnage ; son ouverture peut prendre davantage de temps. Les colonnes `countable`, `inside_region` et `duplicate_of` doivent guider les filtres avant un comptage.

Les fichiers absents sont signalés. Pour les produire, suivre les notebooks du dépôt. Les contours et les graphes IGN/OSM restent décrits dans les README des modules ; cet explorateur est destiné aux tables CSV.

## Parcours débutant

1. Ouvrir la table croisée et consulter « Aperçu et qualité des colonnes ».
2. Comparer les **moyennes** de `amenities_count_500m` par `departement` dans un graphique en barres. Ajouter le nombre de stations pour juger la taille des groupes.
3. Explorer `capacity` face à `amenities_count_500m` dans un nuage de points avec `station_uid` en détail, sans agréger les stations.
4. Filtrer par réseau et comparer les indicateurs piétons aux colonnes `_straight_line`.

Les noms des champs sont conservés pour correspondre au dictionnaire consultable dans la page. X et Y désignent les axes ; une dimension est une catégorie, une mesure est une valeur numérique. Pour comparer des stations moyennes, sélectionner mean/moyenne plutôt que sum/somme.

## Interpréter

Les blancs ne deviennent jamais des zéros. Un objet OSM de recharge n’est pas un nombre de bornes. Les stations partagent parfois les mêmes équipements : sommer leurs décomptes double-compte ces lieux. Les données de disponibilité sont datées (`extracted_at`, `snapshot_ts`, `last_reported`) : elles ne mesurent ni les réservations ni la demande. Une corrélation suggère une hypothèse à vérifier avec des données d’usage et une période adaptée.

Voir aussi [le dictionnaire](../regional-data/DATA_DICTIONARY.md) et [les sources et limites](../regional-data/SOURCES.md).
