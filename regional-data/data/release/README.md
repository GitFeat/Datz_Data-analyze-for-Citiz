# Table finale Citiz AURA

Une ligne par station du référentiel régional IGN, jointe au CSV Citiz national par station_uid.
Le fichier citiz_aura_final.csv utilise UTF-8 avec BOM, une virgule comme séparateur et un point décimal.
Les cellules vides sont inconnues ou non calculées. Aucun remplacement par zéro.

## Colonnes ajoutées au dictionnaire des indicateurs

- city : commune déclarée dans le référentiel Citiz ; peut être vide.
- departement, region : rattachement du référentiel Citiz ; le périmètre régional des stations a été confirmé en amont avec IGN.
- reseau : réseau déclaré dans le référentiel Citiz.
- capacity : capacité déclarée de station, pas le nombre de véhicules actuellement présents.
- num_vehicles_available : véhicules disponibles dans l'instantané Citiz.
- is_renting : statut de location déclaré dans cet instantané.
- extracted_at : date d'extraction du référentiel Citiz, pas date de mise à jour garantie de chaque station.
- station_reference_match : both signifie qu'une référence Citiz a été retrouvée.

## Interprétation et sources

Voir DATA_DICTIONARY.md pour les unités, rayons et statuts, et SOURCES.md pour les sources et licences.
Les indicateurs principaux suivent le réseau piéton OSM ; les suffixes _straight_line indiquent le vol d'oiseau.
Un zéro OSM décrit l'absence d'objet recensé dans les données traitées, pas une absence sur le terrain.
Les équipements de plusieurs stations peuvent se recouper : leur somme n'est pas un total régional unique.
Les sites OSM de recharge ne sont pas un nombre de bornes. La disponibilité instantanée ne mesure pas la demande.
La date d'export ne rend pas les observations plus récentes.
Attribution OSM : © OpenStreetMap contributors, ODbL 1.0, extraits Geofabrik.
Les métadonnées de licences IGN et GBFS restent à confirmer avant publication publique, comme indiqué dans SOURCES.md.

## Reproduction

Exécuter regional-data/notebooks/07_release_final_table.ipynb avec le noyau Python (IGN / OSM).
Le manifeste décrit les fichiers exacts par SHA-256. citiz_aura_quality.csv décrit les valeurs manquantes par colonne.
