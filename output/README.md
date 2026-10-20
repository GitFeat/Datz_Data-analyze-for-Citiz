# Référence Citiz partagée

Instantané des stations Citiz du **19/10/2026**, produit par les notebooks de [`citiz/`](../citiz/README.md) et lu par les autres modules. C'est le seul dossier de données versionné du dépôt : il garantit que tous les modules travaillent sur les mêmes stations.

| Fichier | Contenu | Utilisé par |
|---|---|---|
| `citiz_stations_geo.csv` | 1 614 stations : position, capacité, réseau, département, région, clé `station_uid` | `regional-data/` (empreinte SHA-256 vérifiée), `dashboard/` |
| `citiz_station_status.csv` | Disponibilités au moment de l'extraction | `dashboard/` |
| `citiz_flux.csv` | Les 15 flux GBFS régionaux, avec leur licence | `regional-data/SOURCES.md` |

## Mettre à jour

Ne pas modifier ces fichiers à la main. Pour publier un nouvel instantané :

1. Prévenir l'équipe : `regional-data/` devra être réexécuté.
2. Exécuter les notebooks 01 et 03 de `citiz/`.
3. Dans la dernière cellule du notebook 03, passer `PUBLISH_TO_TEAM = True` et l'exécuter.

Le notebook 03 met à jour `citiz_stations_geo.csv` et `citiz_flux.csv`. `citiz_station_status.csv` se copie depuis `citiz/data/raw/gbfs/`.
