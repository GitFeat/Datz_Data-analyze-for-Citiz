# Dictionnaire des tables Lakehouse

Tables produites par le notebook 04. Toutes ont une colonne `_loaded_at` (date du chargement, UTC). Le schéma réel (types, valeurs manquantes) est aussi exporté dans `data/lakehouse/Files/clean/_data_dictionary.csv`.

Conventions : noms en anglais, minuscules, sans accent ; identifiants en texte ; dates en UTC ; géométries en texte WKT, accompagnées de coordonnées WGS84 en degrés.

## Tables

| Table | Clé | Lignes (20/10/2026) | Contenu |
|---|---|---|---|
| `geo_region` | `code` | 13 | Régions métropolitaines : `name`, centroïde, contour WKT |
| `geo_department` | `code` | 96 | Départements métropolitains : `name`, `region_code`, centroïde, contour WKT |
| `citiz_network` | `source` | 15 | Flux GBFS régionaux : `network_name`, URL, version, licence |
| `citiz_station` | `station_uid` | 1 615 | Stations : position, adresse, capacité, `dep_code`, `region_code` |
| `citiz_vehicle_type` | `vehicle_type_uid` | 337 | Modèles : marque, modèle, `form_factor`, `propulsion_type` |
| `citiz_station_status` | `station_uid`, `snapshot_ts` | 3 229 | Disponibilités par station et par instantané |
| `citiz_station_status_vehicle` | `station_uid`, `snapshot_ts`, `vehicle_type_uid` | 5 028 | Voitures disponibles par modèle |
| `cost_parameter` | `facility`, `parameter` | 9 | Paramètres de coût, avec statut et source |

## Liens entre tables

- `citiz_station.source` → `citiz_network.source`
- `citiz_station.dep_code` → `geo_department.code`
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
| `capacity` | Nombre de places déclarées. Exclure les pseudo-stations internes (voir README). |
| `snapshot_ts` | Date de l'extraction qui a produit la ligne de statut. |
| `last_reported` | Dernière mise à jour du statut par l'opérateur. Souvent ancienne : ne pas l'utiliser comme mesure d'activité. |
| `num_vehicles_available` | Voitures disponibles à `snapshot_ts`. |
| `vehicle_type_uid` | `source:vehicle_type_id`. |
| `propulsion_type` | `combustion`, `hybrid`, `electric`, `human`. |
| `cost_parameter.status` | `sourced` (document public), `derived` (calculé), `assumption` (à fixer ; valeur vide). |

## Colonnes source renommées

| Source | Table | Avant | Après |
|---|---|---|---|
| GeoJSON régions / départements | `geo_region`, `geo_department` | `nom` | `name` |
| `citiz_flux.csv` | `citiz_network` | (dérivé de `dataset_title`) | `network_name` |

## Colonnes source non reprises

- `max_range_meters` : 0 pour 96 % des modèles.
- `num_vehicles_available`, `is_renting` dans `citiz_station` : état instantané, déjà présent dans `citiz_station_status`.
- `vehicle_types_available` (JSON) : dépliée dans `citiz_station_status_vehicle`.
