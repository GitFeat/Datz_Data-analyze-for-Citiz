# Lakehouse Microsoft Fabric

## Objectif

Assembler le travail de l'équipe en **tables typées et contrôlées**, prêtes pour un Lakehouse Microsoft Fabric : stations Citiz, indicateurs OSM autour des stations, population par carreau de 200 m, référentiel géographique et paramètres de coût. Ce module ne télécharge ni ne recalcule rien : il lit les sorties des autres modules.

Statut : **préparatoire**. Le notebook a été exécuté en local le 20/10/2026 ; la partie Spark n'a pas encore été testée dans Fabric.

## Entrées

| Fichier | Produit par |
|---|---|
| `citiz/data/raw/gbfs/*.csv` (4 fichiers) | `citiz` 01 |
| `citiz/data/raw/boundaries/*.geojson` | `citiz` 03 (téléchargés s'ils manquent) |
| `citiz/data/processed/citiz_stations_geo.csv` | `citiz` 03 |
| `regional-data/data/release/citiz_aura_final.csv` | `regional-data` 07 (versionné) |
| `population/reference/filosofi_2021_aura/carreaux_200m_aura.csv` | `population/` (versionné) |

Exécuter d'abord `citiz` 01 puis 03, ensuite [le notebook](notebooks/01_build_lakehouse_tables.ipynb) depuis un noyau neuf, avec le `.venv` racine :

```bash
.venv/bin/python -m pip install -r lakehouse/requirements.txt
```

## Tables produites

Description des colonnes, liens entre tables et colonnes écartées : [le dictionnaire](DATA_DICTIONARY.md). Chaque table a une clé primaire vérifiée ; les 9 clés étrangères sont contrôlées (aucun orphelin à l'exécution du 20/10/2026).

| Table | Rôle | Lignes | Colonnes | Usage pour le sujet |
|---|---|---|---|---|
| `population_grid_aura` | principale | 312 143 | 24 | Zones à colorer (objectif 1), population desservie (objectif 2) |
| `citiz_station` | principale | 1 615 | 16 | Offre Citiz existante ; filtrer `is_internal` |
| `station_feature_aura` | principale | 612 | 28 | Équipements accessibles à pied autour des stations AURA |
| `citiz_vehicle_type` | principale | 337 | 9 | Motorisation de la flotte (impact carbone) |
| `geo_department` | principale | 96 | 7 | Référentiel et filtres géographiques |
| `citiz_network` | principale | 15 | 12 | Réseaux régionaux, URL et licence des flux |
| `geo_region` | principale | 13 | 6 | Référentiel géographique |
| `cost_parameter` | principale | 9 | 7 | Coûts d'une station (objectif 3), sourcés ou à fixer |
| `citiz_station_status` | annexe | 6 459 | 11 | Historique de disponibilité : **pas une mesure d'usage** |
| `citiz_station_status_vehicle` | annexe | 10 056 | 5 | Voitures disponibles par modèle et par relevé |

Chaque table a aussi une colonne `_loaded_at`. Les nombres de colonnes l'incluent.

## Fichiers à déposer dans Fabric

Tout est dans `lakehouse/data/Files/` (65 Mo), recréé par le notebook et exclu de Git. Deux façons de charger :

1. **Sans Spark, recommandée tant que le notebook n'est pas testé dans Fabric** : déposer `clean/*.parquet` dans `Files/clean/` du Lakehouse, puis sur chaque fichier, menu **Load to Tables**.
2. **Avec le notebook** : déposer `raw/` dans `Files/raw/`, importer le notebook dans Fabric, lui attacher le Lakehouse par défaut et l'exécuter. Il écrit `Files/clean/` puis les tables Delta. GeoPandas devra peut-être être installé dans l'environnement Fabric (non vérifié).

| Fichier | Taille | Table ou rôle |
|---|---|---|
| `clean/population_grid_aura.parquet` | 27 Mo | `population_grid_aura` |
| `clean/geo_department.parquet` | 204 Ko | `geo_department` |
| `clean/citiz_station.parquet` | 136 Ko | `citiz_station` |
| `clean/geo_region.parquet` | 84 Ko | `geo_region` |
| `clean/citiz_station_status.parquet` | 76 Ko | `citiz_station_status` (annexe) |
| `clean/station_feature_aura.parquet` | 52 Ko | `station_feature_aura` |
| `clean/citiz_station_status_vehicle.parquet` | 40 Ko | `citiz_station_status_vehicle` (annexe) |
| `clean/citiz_vehicle_type.parquet` | 16 Ko | `citiz_vehicle_type` |
| `clean/citiz_network.parquet` | 12 Ko | `citiz_network` |
| `clean/cost_parameter.parquet` | 8 Ko | `cost_parameter` |
| `clean/_data_dictionary.csv` | 7 Ko | Schéma réel : rôle, type et valeurs manquantes par colonne |
| `raw/gbfs/*.csv` | 1,8 Mo | Entrées du notebook (option 2) |
| `raw/boundaries/*.geojson` | 784 Ko | Entrées du notebook (option 2) |
| `raw/citiz/citiz_stations_geo.csv` | 460 Ko | Entrées du notebook (option 2) |
| `raw/regional/citiz_aura_final.csv` | 344 Ko | Entrées du notebook (option 2) |
| `raw/population/carreaux_200m_aura.csv` | 34 Mo | Entrées du notebook (option 2) |

Conventions : noms en anglais et en minuscules, identifiants en texte, dates UTC à la microseconde, géométries en texte WKT (Delta n'a pas de type géométrique), données manquantes laissées vides.

## Limites

- `station_feature_aura` ne couvre que les 612 stations d'Auvergne-Rhône-Alpes, et `population_grid_aura` que cette région.
- La population n'est pas encore croisée avec les stations : la population desservie à 5 min à pied reste à calculer (`regional-data`).
- L'historique de disponibilité a 4 relevés ; 95 % des statuts ont plus de 30 jours (`is_stale`).
- `cost_parameter` contient 4 valeurs sourcées, 1 calculée et 4 hypothèses vides, à fixer avec Citiz.
