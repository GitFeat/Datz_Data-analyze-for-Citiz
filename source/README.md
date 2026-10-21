# Sources brutes : Métropole de Lyon

Données **brutes** pour peupler le Lakehouse : valeurs telles que publiées, seulement **filtrées sur la Métropole de Lyon** (EPCI `200046977`, 58 communes et les 9 arrondissements de Lyon) et converties en CSV. Récupérées le 20/10/2026 par [`fetch_sources.py`](fetch_sources.py), qui écrit dans `raw/`. Chaque fichier est tracé dans [`manifest.csv`](manifest.csv) : URL, licence, date, lignes, empreinte SHA-256. Les fichiers d'origine sont dans `_archives/`, non versionné.

Seules les sources retenues pour le projet sont conservées ici et récupérées par le script :

```bash
.venv/bin/python source/fetch_sources.py              # toutes les sources
.venv/bin/python source/fetch_sources.py gbfs lyon    # parmi : geography, gbfs, public_transit, population, lyon
```

Attention : `gbfs` télécharge un **nouvel instantané** et écrase les fichiers Citiz et concurrents du 20/10/2026.

Les géométries Grand Lyon (`the_geom`) sont en WKT, EPSG:4326, ordre `longitude latitude`. Celles de l'IGN (`geometrie`) sont en WKT EPSG:4326, mais dans l'ordre **`latitude longitude`** : à inverser avant usage.

## `raw/geography(lyon metropole)/` : périmètre et découpages (IGN)

| Fichier | Ce que retrace le CSV | Lignes |
|---|---|---|
| `ign_adminexpress_epci_lyon.csv` | Contour officiel de la Métropole de Lyon (ADMIN EXPRESS) et liste de ses communes | 1 |
| `ign_contours_iris_lyon.csv` | Contours des 512 IRIS (quartiers INSEE d'environ 2 000 habitants) | 512 |
| `ign_adminexpress_communes_lyon.csv` | Contours, codes et population des 58 communes | 58 |
| `ign_adminexpress_arrondissements_lyon.csv` | Contours des 9 arrondissements de Lyon (codes INSEE 69381 à 69389) | 9 |

## `raw/citiz/` : Citiz, flux GBFS

Un flux GBFS est un **instantané** pris au moment de la collecte (20/10/2026 vers 15 h 40).

| Fichier | Ce que retrace le CSV | Lignes |
|---|---|---|
| `station_information.csv` | Les 200 stations Citiz de la Métropole : position, adresse, **capacité**, type de parking | 200 |
| `vehicle_status.csv` | Les 460 voitures : station de rattachement, type, autonomie | 460 |
| `vehicle_types.csv` | Modèles de véhicules (gabarit, motorisation) | 21 |
| `system_pricing_plans.csv` | Grilles tarifaires (prix au km et à l'heure, avec ou sans abonnement) | 10 |

## `raw/concurence/` : autopartage concurrent, flux GBFS

| Fichier | Ce que retrace le CSV | Lignes |
|---|---|---|
| `leodango/free_bike_status.csv` | Position des voitures Leo&Go, autopartage en libre-service | 272 |
| `leodango/geofencing_zones.csv` | Zone de service et zones interdites Leo&Go | 78 |
| `getaround_lyon/vehicle_status.csv` | Voitures de particuliers en location Getaround | 289 |

## `raw/public_transit/` : trains SNCF

Le réseau **TCL** (métro, tram, bus) n'est pas inclus : ses données exigent un compte data.grandlyon.com.

| Fichier | Ce que retrace le CSV | Lignes |
|---|---|---|
| `stops.csv` | Arrêts SNCF (TER, TGV, Intercités) de la Métropole et leurs gares parentes, issus du GTFS SNCF | 121 |
| `sncf_gares_de_voyageurs_lyon.csv` | Les 35 gares de voyageurs : position, code UIC, segment (national, régional, local) | 35 |
| `sncf_frequentation_gares_lyon.csv` | Voyageurs annuels par gare, 2015 à 2024 | 35 |

## `raw/population/` : population et revenus (INSEE)

| Fichier | Ce que retrace le CSV | Lignes |
|---|---|---|
| `insee_filosofi2021_carreaux_200m_lyon.csv` | Population par carreau de 200 m (Filosofi 2021) : habitants par âge, ménages, ménages pauvres, niveau de vie, logements sociaux, logements collectifs | 8 032 |

## `raw/lyon/` : couches de la Métropole (data.grandlyon.com)

| Fichier | Ce que retrace le CSV | Lignes |
|---|---|---|
| `parkings.csv` | Parkings recensés par la Métropole : type, gestionnaire, capacité totale, autopartage, PMR, vélos | 1 047 |
| `zfe_perimetre.csv` | Périmètre et règles de la Zone à Faibles Émissions | 1 |
| `bornes_irve.csv` | Bornes de recharge pour véhicules électriques : puissance, nombre de points de charge | 2 558 |
| `quartiers_prioritaires_2024_2030.csv` | Contours des quartiers prioritaires de la politique de la ville | 71 |
