# Sources de données du projet

Liste unique des sources utilisées dans le dépôt (livrable demandé par le sujet). Les versions exactes, empreintes et limites sont détaillées dans le `SOURCES.md` du module indiqué.

| Source | Producteur | Version utilisée | Licence | Module | Détails |
|---|---|---|---|---|---|
| Flux GBFS Citiz, 15 réseaux régionaux, via l'API du Point d'accès national | Citiz, transport.data.gouv.fr | GBFS 3.0, instantanés du 19 et du 20/10/2026 | Licence Ouverte v2.0 (`lov2`, colonne `licence` de `output/citiz_flux.csv`) | `citiz/` | [citiz/SOURCES.md](citiz/SOURCES.md) |
| Contours simplifiés des régions et départements (`gregoiredavid/france-geojson`) | Dérivés d'IGN Admin Express | Branche `main` | À vérifier sur le dépôt source | `citiz/`, `lakehouse/` | [citiz/SOURCES.md](citiz/SOURCES.md) |
| ADMIN EXPRESS COG, régions et communes | IGN | Édition du 01/01/2026, récupérée le 19/10/2026 | À confirmer dans les métadonnées IGN | `ign-osm/`, `regional-data/` | [ign-osm/sources.csv](ign-osm/sources.csv), [regional-data/SOURCES.md](regional-data/SOURCES.md) |
| OpenStreetMap, extraits Auvergne et Rhône-Alpes | Geofabrik, contributeurs OpenStreetMap | Archives `261016`, récupérées le 19/10/2026 | ODbL 1.0, © OpenStreetMap contributors | `ign-osm/`, `regional-data/` | [ign-osm/sources.csv](ign-osm/sources.csv), [regional-data/SOURCES.md](regional-data/SOURCES.md) |
| Filosofi 2021, données carroyées à 200 m | INSEE | Édition 2021, extrait Auvergne-Rhône-Alpes | Conditions de réutilisation de l'INSEE (citer la source) | `population/`, `lakehouse/` | [population/SOURCES.md](population/SOURCES.md) |
| Projections de population 2021-2070, Omphale 2022 | INSEE | Fichiers du 07/12/2022, 11 scénarios | Conditions de réutilisation de l'INSEE (citer la source) | `population/` | [population/SOURCES.md](population/SOURCES.md) |
| Convention type Genevois français / Citiz Alpes-Loire | Genevois français | Projet du 20/07/2021 | Document public | `citiz/`, `lakehouse/` (`cost_parameter`) | [citiz/SOURCES.md](citiz/SOURCES.md) |
| Livre blanc Citiz | Citiz | Février 2026 | Document public | `citiz/` | [citiz/SOURCES.md](citiz/SOURCES.md) |

Les licences marquées « à vérifier » ou « à confirmer » doivent l'être avant toute redistribution publique.

## Repérées, pas encore utilisées

Vélo'v (GBFS), Dott (GBFS), Leo&Go (GBFS), TCL (GTFS) pour la Métropole de Lyon : voir [citiz/README.md](citiz/README.md#sources-repérées-pas-encore-exploitées). Les arrêts de transport en commun, les accidents et les points de recharge IRVE ne sont pas récupérés ; leurs colonnes restent vides dans `regional-data/`.
