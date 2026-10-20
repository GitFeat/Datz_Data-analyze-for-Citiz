# Analyse descriptive Citiz AURA après nettoyage

Reproduction : exécuter `regional-data/notebooks/clean.ipynb` depuis un noyau neuf Python (IGN / OSM), fourni par `ign-osm/.venv`.

Résultat vérifié : 612 stations, 44 colonnes après retrait des 6 colonnes ayant au moins 90 % de valeurs manquantes. Aucune suppression automatique de station ni remplacement des inconnues par zéro. Le CSV de release reste intact.

- `citiz_aura_clean.csv` : données nettoyées, UTF-8 avec BOM, séparateur virgule.
- `numeric_statistics.csv`, `categorical_statistics.csv`, `category_frequencies.csv` : statistiques descriptives et fréquences.
- `department_statistics.csv`, `network_statistics.csv`, `department_station_counts.csv` : comparaisons territoriales.
- `spearman_correlations.csv` : associations entre variables numériques non constantes, hors coordonnées ; aucune interprétation causale.
- `distributions.html` : histogrammes autonomes des capacités, disponibilités et indicateurs d’environnement.
- `citiz_aura_map.html` : carte interactive ; connexion Internet requise pour Leaflet et le fond OSM.
- `consistency_issues.csv` : 2 stations avec disponibilité supérieure à la capacité déclarée : Décines - Centre et Mairie Poisat [Station électrique]. Vérifier les conventions et la source avant correction.
- `nearby_station_pairs.csv` : 17 paires à au plus 30 m à vol d’oiseau (Haversine, rayon terrestre 6 371 008,8 m).
- `repeated_station_names.csv` : 4 stations avec noms répétés après normalisation des espaces et de la casse.
- `outliers_iqr.csv` : 1 165 signalements station-variable hors des bornes Q1 − 1,5 IQR et Q3 + 1,5 IQR. Plusieurs signalements peuvent concerner une station. Ce ne sont pas des erreurs établies.
- `constant_columns.csv`, `dropped_columns.csv` : colonnes constantes et colonnes retirées.
- `analysis_manifest.json` : paramètres, effectifs et empreinte SHA-256 du CSV source.

Les équipements comptés sont des objets OSM recensés, et non des capacités réelles ; les périmètres des stations peuvent se recouper. L’instantané Citiz du 19 octobre 2026 ne mesure pas la demande. Les statistiques ne suffisent pas à classer les futurs emplacements sans population, historique d’usage et données de transport complémentaires. Voir les sources, licences et définitions dans `../release/DATA_DICTIONARY.md` et `../release/SOURCES.md`.
