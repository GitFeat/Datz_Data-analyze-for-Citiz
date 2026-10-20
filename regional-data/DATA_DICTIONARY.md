# Dictionnaire du tableau par station

Clé de jointure : `station_uid`, conservée depuis le CSV Citiz de l'équipe. Une ligne correspond à une station positionnée dans la région IGN. `latitude` / `longitude` sont des coordonnées WGS84 en degrés. Les cellules vides du CSV représentent des valeurs inconnues ou non calculées.

## Variables demandées

| Colonne | Définition et état |
|---|---|
| `irve_count_500m` | Non calculée : unité « borne » / « point de recharge » à définir, source adaptée à intégrer. Ne pas confondre avec les sites OSM. |
| `amenities_count_500m` | Nombre d'objets OSM comptables de la liste d'équipements/services accessibles par le réseau piéton à distance ≤ 500 m. |
| `bike_parking_count_300m` | Nombre d'objets `amenity=bicycle_parking` accessibles par le réseau à distance ≤ 300 m. Ce n'est pas une capacité en vélos. |
| `transit_departures_peak_hour` | Non calculée : GTFS, jour de service, arrêts à considérer et heure de pointe à définir. |
| `public_parking_spaces_300m` | Somme des capacités des parkings OSM à accès `yes` ou `permissive` accessibles par le réseau à distance ≤ 300 m, uniquement si aucun parking proche n'a un accès inconnu et si toutes les capacités publiques recensées sont connues. Sinon vide. |
| `pedestrian_network_distance_m` | Non calculée : origines, destinations, agrégation et réseau régional à définir. |
| `tourism_sites_count_1km` | Nombre d'objets OSM comptables de la liste touristique accessibles par le réseau à distance ≤ 1 000 m. |
| `accidents_count_500m` | Non calculée : source d'accidents, période et règles de localisation absentes. |

La liste d'équipements comprend restauration, enseignement, culture, santé, services financiers/postaux, marché, mairie, police, pompiers, services sociaux et lieux de culte. La liste exacte des valeurs `amenity` est dans le notebook 02. Parkings, stationnements vélo et recharges en sont exclus.

La liste touristique est `attraction`, `museum`, `gallery`, `viewpoint`, `zoo`, `aquarium`, `theme_park`, `artwork`. Elle exclut les hôtels et panneaux d'information. Un même objet portant un équipement et une catégorie touristique peut contribuer à chacun des deux indicateurs, une seule fois par catégorie.

## Compléments et qualité

| Colonne | Signification |
|---|---|
| `osm_charging_sites_count_500m` | Nombre de sites `amenity=charging_station` atteignables par le réseau dans les 500 m ; ni nombre de bornes ni inventaire IRVE exhaustif. |
| `*_straight_line` | Valeur de comparaison calculée à vol d'oiseau ; l'indicateur principal suit le réseau piéton OSM. |
| `*_unreachable_or_unsnapped_*` | Objets impossibles à raccorder ou non atteints dans le rayon réseau. Les examiner avant interprétation. |
| `walking_station_snap_distance_m` | Distance directe station-chemin utilisée pour raccorder la station au graphe, au maximum 100 m. |
| `walking_network_status` | Indique si la station a été raccordée à un chemin dans la limite de 100 m. |
| `public_parking_spaces_known_300m` | Somme des capacités renseignées des parkings publics identifiés ; total partiel, pas estimation des capacités manquantes. |
| `public_parking_sites_300m` | Nombre de parkings à accès public explicite selon notre profil. |
| `parking_sites_unknown_access_300m` | Nombre de parkings proches dont l'accès public ne peut pas être établi par nos règles. |
| `public_parking_sites_unknown_capacity_300m` | Parkings à accès public retenu mais capacité non interprétable. |
| `*_status` | Raison d'indisponibilité ou périmètre d'interprétation de la variable. |
| `osm_count_status` | Les comptages concernent les objets recensés, pas un inventaire exhaustif. |
| `osm_extraction_has_geometry_issues` | Des géométries sources n'ont pas été reconstruites ou étaient invalides ; leur localisation n'est pas toujours connue. |
| `radius_300m_inside_ign_region`, `radius_500m_inside_ign_region`, `radius_1000m_inside_ign_region` | Le carré englobant le rayon est entièrement dans le contour IGN : test conservateur, pas preuve d'exhaustivité OSM. |
| `boundary_coverage_status` | Les stations proches des frontières demandent une vérification de la couverture des extraits historiques. |

## Couche d'objets OSM

`osm_uid` combine le type et l'identifiant (`node/123`, `way/456`, `relation/789`). `categories` contient les catégories séparées par des virgules. `capacity_raw` conserve le tag original ; `capacity` ne contient que les entiers interprétables. `source_files` conserve les extraits contenant cet objet. `inside_region` distingue les objets touchant la région de ceux retenus seulement dans la marge.

`countable=False` signifie qu'un point a été rapproché d'une surface de mêmes nom non vide et tags : il est livré pour audit, mais exclu des comptages. `duplicate_of` donne la surface retenue. Les objets sans nom ou décrits différemment peuvent encore représenter un même lieu physique.
