# Dictionnaire des tables Lakehouse

Tables produites par [`notebooks/01_build_lakehouse_tables.ipynb`](notebooks/01_build_lakehouse_tables.ipynb). Les tables **annexes** conservent l'historique de disponibilité, qui n'est pas une mesure d'usage ; les autres sont les tables **principales**. Le rôle de chaque table figure aussi dans la colonne `role` de `_data_dictionary.csv`.

Toutes les tables ont une colonne `_loaded_at` (date du chargement, UTC). Le schéma réel (types, valeurs manquantes) est aussi exporté dans `data/Files/clean/_data_dictionary.csv`.

Conventions : noms en anglais, minuscules, sans accent ; identifiants en texte ; dates en UTC ; géométries en texte WKT, accompagnées de coordonnées WGS84 en degrés.

## Tables

| Table | Clé | Lignes (20/10/2026) | Contenu |
|---|---|---|---|
| `geo_region` | `code` | 13 | Régions métropolitaines : `name`, centroïde, contour WKT |
| `geo_department` | `code` | 96 | Départements métropolitains : `name`, `region_code`, centroïde, contour WKT |
| `citiz_network` | `source` | 15 | Flux GBFS régionaux : `network_name`, URL, version, licence |
| `citiz_station` | `station_uid` | 1 615 | Stations : position, adresse, capacité, `dep_code`, `region_code`, `is_internal` |
| `citiz_vehicle_type` | `vehicle_type_uid` | 337 | Modèles : marque, modèle, `form_factor`, `propulsion_type` |
| `citiz_station_status` | `station_uid`, `snapshot_ts` | 6 459 | **Annexe.** Disponibilités par station et par instantané |
| `citiz_station_status_vehicle` | `station_uid`, `snapshot_ts`, `vehicle_type_uid` | 10 056 | **Annexe.** Voitures disponibles par modèle |
| `station_feature_aura` | `station_uid` | 612 | Indicateurs OSM autour des stations AURA (`regional-data/`) : objets accessibles à pied, à vol d'oiseau, non raccordés |
| `population_grid_aura` | `idcar_200m` | 312 143 | Carreaux INSEE Filosofi 2021 (`population/`) : centre, contour WKT, département, habitants, ménages, niveau de vie, tranches d'âge |
| `cost_parameter` | `facility`, `parameter` | 9 | Paramètres de coût, avec statut et source |

## Liens entre tables

- `citiz_station.source` → `citiz_network.source`
- `citiz_station.dep_code` → `geo_department.code` (département lu dans `citiz_stations_geo.csv`, notebook `citiz` 03)
- `citiz_station.region_code` → `geo_region.code`
- `station_feature_aura.station_uid` → `citiz_station.station_uid`
- `population_grid_aura.dep_code` → `geo_department.code`
- `geo_department.region_code` → `geo_region.code`
- `citiz_station_status.station_uid` → `citiz_station.station_uid`
- `citiz_station_status_vehicle.vehicle_type_uid` → `citiz_vehicle_type.vehicle_type_uid`
- `citiz_vehicle_type.source` → `citiz_network.source`

## Colonnes à connaître

| Colonne | Signification |
|---|---|
| `station_uid` | `source:station_id`. Un même `station_id` existe dans plusieurs réseaux : seul `station_uid` est unique. Clé de jointure avec `regional-data/`. |
| `source` | Identifiant court du flux : `provider_<n>` pour les flux Citiz, identifiant du jeu de données sinon (Métropole de Lyon). |
| `sources` | Flux dans lesquels la station a été trouvée, séparés par des virgules. |
| `is_virtual_station` | Zone de dépose sans place matérialisée. |
| `capacity` | Nombre de places déclarées. Exclure les pseudo-stations internes (`is_internal`). |
| `is_internal` | Pseudo-station interne (stockage, démonstration, livraison), repérée par son nom. À filtrer avant toute analyse. |
| `snapshot_ts` | Date de l'extraction qui a produit la ligne de statut. |
| `last_reported` | Dernière mise à jour du statut par l'opérateur. Souvent ancienne : ne pas l'utiliser comme mesure d'activité. |
| `num_vehicles_available` | Voitures disponibles à `snapshot_ts`. |
| `status_age_days` | Jours entre `snapshot_ts` et `last_reported`. |
| `is_stale` | Statut vieux de plus de 30 jours : il ne reflète pas l'état réel de la station. |
| `vehicle_type_uid` | `source:vehicle_type_id`. |
| `propulsion_type` | `combustion`, `hybrid`, `electric`, `human`. |
| `station_feature_aura` | Définitions des indicateurs (rayons, catégories, raccordement au réseau piéton) : voir `regional-data/DATA_DICTIONARY.md`. `public_parking_spaces_300m` est vide quand un accès ou une capacité est inconnu, ce n'est pas un zéro. |
| `idcar_200m` | Identifiant INSEE du carreau ; contient le coin sud-ouest en EPSG:3035. |
| `population_grid_aura.geometry_wkt` | Contour du carreau de 200 m en WGS84, recalculé depuis `idcar_200m`. `lon` / `lat` = son centre, fourni par `population/`. |
| `population_grid_aura.dep_code` | Département lu dans `lcog_geo`. Vide quand le carreau chevauche deux départements (`is_multi_department = true`). Autres colonnes : voir `population/DATA_DICTIONARY.md`. |
| `cost_parameter.status` | `sourced` (document public), `derived` (calculé), `assumption` (à fixer ; valeur vide). |

## Colonnes source renommées

| Source | Table | Avant | Après |
|---|---|---|---|
| GeoJSON régions / départements | `geo_region`, `geo_department` | `nom` | `name` |
| `citiz_flux.csv` | `citiz_network` | (dérivé de `dataset_title`) | `network_name` |

## Colonnes source non reprises

- `max_range_meters` : 0 pour 96 % des modèles.
- `short_name`, `post_code`, `city` dans `citiz_station`, `rider_capacity` dans `citiz_vehicle_type`, `num_vehicles_disabled` dans `citiz_station_status` : vides dans tous les flux.
- `num_docks_available` (toujours 0) et `is_renting` (toujours vrai) dans `citiz_station_status` : constantes, aucune information.
- `num_vehicles_available`, `is_renting` dans `citiz_station` : état instantané, déjà présent dans `citiz_station_status`.
- `vehicle_types_available` (JSON) : dépliée dans `citiz_station_status_vehicle`.
- `citiz_aura_final.csv` (`regional-data/`) : 23 des 50 colonnes ne sont pas reprises dans `station_feature_aura`. Ce sont les doublons de `citiz_station` (nom, position, département, région, réseau, capacité), les colonnes non exploitables (`city`, `is_renting`, `num_vehicles_available`, `extracted_at`, `station_reference_match`), les indicateurs pas encore calculés (`irve_count_500m`, `transit_departures_peak_hour`, `pedestrian_network_distance_m`, `accidents_count_500m`) avec leurs colonnes `_status`, et les colonnes constantes (`walking_network_status`, `osm_count_status`, `osm_extraction_has_geometry_issues`).
