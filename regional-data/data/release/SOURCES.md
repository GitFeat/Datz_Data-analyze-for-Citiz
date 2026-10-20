# Sources et traçabilité

| Source | Version utilisée | Rôle |
|---|---|---|
| IGN ADMIN EXPRESS COG | Édition 2026-01-01, fichiers région et communes | Contours administratifs et codes INSEE |
| OpenStreetMap / Geofabrik Auvergne | Archive `auvergne-261016.osm.pbf` | Objets et attributs OSM |
| OpenStreetMap / Geofabrik Rhône-Alpes | Archive `rhone-alpes-261016.osm.pbf` | Objets et attributs OSM |
| Export Citiz GBFS du dépôt | `output/citiz_stations_geo.csv`, colonne `extracted_at` | Stations et identifiants de l'équipe |

## Liens officiels

- [IGN : présentation des fichiers ADMIN EXPRESS COG utilisés](https://cartes.gouv.fr/aide/fr/partenaires/ign/generalites-ign/actualites/2026-06-flatgeobuf-geoparquet/).
- [Geofabrik Auvergne](https://download.geofabrik.de/europe/france/auvergne.html), [Geofabrik Rhône-Alpes](https://download.geofabrik.de/europe/france/rhone-alpes.html).
- [Attribution et licence OpenStreetMap](https://www.openstreetmap.org/copyright) : © OpenStreetMap contributors, ODbL 1.0, extraits par Geofabrik.
- [Définition OSM du stationnement vélo](https://wiki.openstreetmap.org/wiki/Tag:amenity=bicycle_parking).
- [Définition OSM du parking et de sa capacité](https://wiki.openstreetmap.org/wiki/Tag:amenity=parking).
- [Définition OSM des sites de recharge](https://wiki.openstreetmap.org/wiki/Tag:amenity=charging_station).
- [PyOsmium : reconstruction des géométries](https://docs.osmcode.org/pyosmium/latest/user_manual/03-Working-with-Geometries/).

Les URL exactes, dates de récupération et SHA-256 des sources IGN / OSM figurent dans `../ign-osm/sources.csv`. Les en-têtes OSM et les métadonnées associées aux PBF permettent de distinguer la date d'archive de l'horodatage de réplication. Les objets individuels peuvent avoir été modifiés à des dates différentes.

Les informations de licences IGN et des flux GBFS doivent être confirmées dans leurs métadonnées avant redistribution publique. Les tables de flux disponibles dans `output/citiz_flux.csv` permettent de retrouver les fournisseurs et leurs licences. Le livrable local ne signifie pas que ces vérifications sont terminées.

Les fichiers `source_manifest.json` et `source_inventory.csv` du module consignent les fichiers réellement utilisés avec leurs empreintes. Le manifeste d'extraction contient aussi la définition des catégories et la signature du périmètre.

Les données GTFS, accidents et un inventaire IRVE en unités de recharge ne sont pas inventées ni récupérées à cette étape. Leur absence est décrite dans les colonnes de statut du livrable.
