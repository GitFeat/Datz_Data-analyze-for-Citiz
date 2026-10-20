# Sources et traçabilité

| Source | Version utilisée | Rôle |
|---|---|---|
| Point d'accès national aux données de transport, API `GET /api/datasets` | Interrogée le 20/10/2026 | Liste des jeux Citiz et URL de leurs flux GBFS |
| 15 flux GBFS Citiz (un par réseau régional) | GBFS 3.0, instantanés des 19 et 20/10/2026 | Stations, disponibilités, types de véhicules |
| Contours simplifiés régions / départements (`gregoiredavid/france-geojson`) | Branche `master`, dérivés d'IGN Admin Express | Fond de carte national et rattachement des stations |
| Convention type Genevois français / Citiz Alpes-Loire | Projet envoyé en préfecture le 20/07/2021 | Coûts d'exploitation et d'équipement |
| Livre blanc Citiz | Février 2026 | Modèle économique de l'autopartage (qualitatif) |

## Liens

- [Jeux Citiz sur le Point d'accès national](https://transport.data.gouv.fr/datasets?type=vehicles-sharing&q=citiz). La liste exacte des flux, avec leur licence, est dans `data/raw/gbfs/citiz_flux.csv` (licence `lov2` : Licence Ouverte v2.0).
- [Spécification GBFS](https://gbfs.org/).
- [france-geojson](https://github.com/gregoiredavid/france-geojson). Les contours officiels détaillés de l'IGN (ADMIN EXPRESS COG 2026) sont préparés dans `ign-osm/`.
- [Convention Genevois français / Citiz Alpes-Loire (PDF)](https://genevoisfrancais.org/wp-content/uploads/CS2021_23.2-AUTOPARTAGE_Convention-cadreAnnexe.pdf) : articles 2.2, 4.2, 5.3 et 6.4.
- [Livre blanc Citiz 2026 (PDF)](https://www.citiz.coop/uploads/2026/02/2026-CITIZ-livre_blanc.pdf).

## Limites

- GBFS ne donne que l'état instantané. L'historique n'existe que si le notebook 01 est exécuté régulièrement.
- Les montants de la convention datent de 2021 et concernent le réseau Alpes-Loire : ce sont des ordres de grandeur, à confirmer auprès de Citiz.
- Les contours simplifiés suffisent pour une carte nationale, pas pour un calcul fin aux frontières.
