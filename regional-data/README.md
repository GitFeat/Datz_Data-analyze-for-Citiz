# Données IGN / OSM pour l'équipe Citiz

Ce dossier prépare un **livrable régional réutilisable**. Il conserve le travail pédagogique de `ign-osm/` et réutilise ses fichiers sources sans les retélécharger.

Le périmètre est toute l'**Auvergne-Rhône-Alpes**, avec une marge de 1 km pour conserver les objets proches des frontières. Les points de référence sont les stations Citiz déjà présentes dans le dépôt. Les équipements restent livrés séparément pour permettre des calculs autour de futurs emplacements.

## Ouvrir les notebooks

Dans VS Code, utiliser le noyau existant **Python (IGN / OSM)**, associé à `ign-osm/.venv/bin/python`. Ne pas créer un nouvel environnement. Si des dépendances manquent sur une autre machine, les installer dans le noyau choisi depuis `requirements.txt`.

Exécuter les notebooks dans l'ordre, en lisant les explications avant les cellules :

1. [Préparer les références](notebooks/01_prepare_reference_data.ipynb) : stations du dépôt, filtre spatial IGN, communes, contour régional et marge.
2. [Extraire les objets OSM](notebooks/02_extract_osm_objects.ipynb) : points, lignes, surfaces et multipolygones ; catégories, dédoublonnage et erreurs consignées.
3. [Calculer les indicateurs](notebooks/03_compute_station_features.ipynb) : distances sur les chemins piétons OSM, comparaison avec les rayons à vol d'oiseau, capacités connues et aperçu régional.
4. [Explorer le catalogue des lieux OSM](notebooks/05_osm_places_catalog.ipynb) : objets géographiques et établissements, catégorie OSM précise, grande famille, tags d'origine et exports filtrables.
5. [Exporter un tableau OSM pour AURA](notebooks/06_osm_aura_table.ipynb) : crée un CSV filtrable avec une ligne par objet, sa catégorie précise, sa grande famille et ses coordonnées.
6. [Exporter la table finale de release](notebooks/07_release_final_table.ipynb) : croise les indicateurs régionaux et le référentiel Citiz par `station_uid`, contrôle la jointure et exporte le CSV accompagné de sa documentation et de son manifeste.
7. [Lister les colonnes et modalités de la table finale](notebooks/08_citiz_aura_columns_modalities.ipynb) : inventaire des types, bornes numériques, modalités avec effectifs et pourcentages, valeurs manquantes et colonnes constantes. Exécuté sur 612 stations et 50 colonnes : 5 colonnes entièrement vides et 555 valeurs manquantes pour le total strict des places publiques. Une cellule permet de consulter toutes les modalités d'une colonne au choix, sans modifier les sources.

### Table finale pour la release

Le notebook 07 a été exécuté depuis un noyau neuf : **612 lignes, 50 colonnes**, identifiants uniques et toutes les références Citiz retrouvées. Le CSV a été relu et comparé au tableau avant écriture, y compris ses valeurs manquantes.

Le fichier final est [`data/release/citiz_aura_final.csv`](data/release/citiz_aura_final.csv). Il correspond à la table croisée du dashboard : une ligne par station AURA, avec indicateurs OSM, département, réseau, capacité et instantané Citiz extrait le **19 octobre 2026**. Les fichiers de qualité, le manifeste SHA-256, le dictionnaire, les sources et le guide sont livrés dans le même dossier. L'encodage est UTF-8 avec BOM, le séparateur est la virgule et les cellules inconnues restent vides.

Le dossier `data/release/` est exclu de Git comme les autres données ; joindre ses fichiers à la release séparément. Ce notebook prépare les fichiers localement, sans publication externe.

Un notebook est un document exécutable. Les cellules de code doivent être lancées dans l'ordre. Redémarrer le noyau puis tout exécuter permet de vérifier la reproductibilité.

## Entrées

| Données | Chemin dans le dépôt |
|---|---|
| Stations Citiz enrichies par l'équipe | `output/citiz_stations_geo.csv` |
| Région et communes IGN déjà préparées | `ign-osm/data/processed/region_84.geojson`, `municipalities_84.geojson` |
| Extrait OSM Auvergne | `ign-osm/data/raw/osm/auvergne-261016.osm.pbf` |
| Extrait OSM Rhône-Alpes | `ign-osm/data/raw/osm/rhone-alpes-261016.osm.pbf` |

Les deux PBF sont nécessaires : Geofabrik conserve ce découpage par anciennes régions. Si les entrées sont absentes sur une autre machine, reprendre les notebooks 01 à 03 de `ign-osm/` et les notebooks Citiz de l'équipe. Aucun résultat d'accessibilité locale de Clermont-Ferrand n'est présenté comme un réseau régional.

## Fichiers à transmettre

Les sorties sont écrites dans `data/processed/`, relativement à ce dossier.

| Fichier | Utilisation |
|---|---|
| `station_features.csv` | Une ligne par station, clé `station_uid`, variables et indicateurs de qualité |
| `station_features.geojson` | Même table avec les coordonnées pour une carte |
| `station_features_preview.html` | Vue régionale hors connexion, panneau au survol/clic et liste de sélection des stations |
| `citiz_stations_aura.csv` et `.geojson` | Référentiel régional des stations |
| `osm_objects.gpkg` | Objets OSM, catégories, géométries, accès, capacités et provenance |
| `osm_layers.gpkg` | Cinq couches directement sélectionnables : `amenities`, `bike_parking`, `parking`, `charging_sites`, `tourism_sites` |
| `osm_places_catalog.gpkg` et `osm_places_catalog.csv` | Catalogue régional élargi : équipements, commerces, transports, loisirs, nature, eau, repères, grandes familles et catégories précises |
| `osm_aura_table.csv` | Tableau CSV simplifié, trié par famille et catégorie, prêt à ouvrir dans un tableur |
| `osm_places_taxonomy.csv` | Correspondance des familles et catégories OSM rencontrées |
| `walking_network.gpkg` | Segments des chemins OSM utilisés pour les distances de marche autour des stations, fichier volumineux (environ 214 Mo) |
| `walking_network_manifest.json` | Sources, nombres de nœuds et segments et statut du réseau |
| `walking_blocked_nodes.csv`, `walking_network_incomplete_ways.csv` | Accès/barrières écartés et chemins incomplets consignés |
| `osm_extraction_errors.csv` | Erreurs ou géométries non reconstruites, avec identifiants |
| `osm_extraction_manifest.json` | Entrées, règles, volumes et dédoublonnages |
| `aura_region.geojson` | Contour IGN régional |
| `aura_counting_area.geojson` | Région avec marge de 1 km |
| `aura_municipalities.gpkg` | Les communes IGN, avec leurs codes |
| `reference_summary.json`, `delivery_summary.json` | Compteurs et état du livrable |

Un **GeoPackage** (`.gpkg`) est un fichier de données géographiques, lisible avec GeoPandas ou QGIS. Il conserve les contours et leurs attributs de façon plus compacte qu'un GeoJSON volumineux.

Ouvrir l'aperçu HTML dans un navigateur : survoler ou cliquer sur un point affiche le nom, l'identifiant et le nombre d'équipements recensés dans les 500 m dans un panneau au-dessus de la carte. La liste permet de sélectionner les stations superposées. Le clavier fonctionne également avec Tab et Entrée. Ces interactions JavaScript peuvent être bloquées dans l'aperçu intégré au notebook ; utiliser le fichier HTML dans un navigateur. Le survol, le clic, le focus, le clavier et la liste ont été vérifiés dans Chrome.

La légende distingue les **stations rouges sans équipement OSM recensé dans les 500 m** (2 lors de l'exécution actuelle) des **stations bleues avec au moins un équipement recensé** (610). Le contour foncé marque la sélection et conserve la couleur de catégorie. Un zéro recensé n'établit pas une absence réelle d'équipements sur le terrain.

Transmettre les fichiers utiles de `data/processed/` avec ce README, [le dictionnaire](DATA_DICTIONARY.md) et [les sources](SOURCES.md). Les fichiers de données sont exclus de Git pour ne pas alourdir le dépôt ; ils existent localement après exécution. Les notebooks et la documentation sont versionnables. Relancer les calculs remplace les sorties, sans modifier les sources ni les autres dossiers de l'équipe.

## Ce que les indicateurs signifient

Les indicateurs autour des stations suivent maintenant le **réseau de chemins piétons OSM**. Chaque station et objet est raccordé au nœud de chemin le plus proche si celui-ci est à 100 m ou moins ; cette distance de raccordement est ajoutée à la plus courte distance du graphe. Les colonnes suffixées `_straight_line` conservent la mesure à vol d'oiseau pour comparaison. Les lieux sans raccordement dans la limite sont signalés et ne sont pas comptés comme accessibles.

Le réseau utilise les règles piétonnes prudentes du prototype et ne modélise pas toutes les traversées, feux, pentes, horaires ou barrières conditionnelles. Le graphe actuel traite les chemins comme non orientés. Pour les surfaces, le point représentatif sert d'accès estimé : il ne remplace pas une entrée connue. Les résultats décrivent l'accessibilité dans le réseau OSM extrait, pas un itinéraire garanti sur le terrain.

Les décomptes portent sur les objets recensés dans OSM, selon les catégories documentées. Un zéro signifie « aucun objet correspondant trouvé dans les données traitées », pas « aucun équipement n'existe réellement ».

Les objets communs aux deux extraits sont dédoublonnés par type et identifiant OSM. Certains doublons point/surface sont également marqués selon le nom et les tags, mais la détection de tous les doublons physiques n'est pas garantie. Tous les objets restent livrés avec leur statut `countable`.

Les catégories d'équipements et de tourisme sont des choix du projet, explicités dans le notebook 02. Elles peuvent être adaptées par l'équipe. Les équipements et sites touristiques ne sont pas filtrés par leur ouverture au public.

Les rayons proches des frontières sont signalés : une marge de 1 km est extraite, mais les contours exacts de couverture des PBF historiques ne sont pas validés. Les erreurs de géométrie peuvent affecter les comptages ; le CSV les signale globalement. OSM peut aussi être incomplet à l'intérieur de la région.

## Variables non calculées

- `irve_count_500m` : le nombre de bornes ou points de recharge n'est pas défini ni établi par le simple nombre de sites OSM. Le proxy explicitement nommé `osm_charging_sites_count_500m` est fourni séparément.
- `transit_departures_peak_hour` : il manque les horaires GTFS, le jour de service et la fenêtre de pointe.
- `pedestrian_network_distance_m` : l'indicateur d'origine/destination, son agrégation et le périmètre de trajets restent à définir. Les comptages d'équipements accessibles par réseau autour des stations sont calculés séparément.
- `accidents_count_500m` : il manque les données d'accidents et la période de comptage.

Ces colonnes restent **vides**, accompagnées de leur statut. Ne pas les convertir automatiquement en zéros avant un modèle. Les places publiques restent aussi vides si une capacité ou un statut d'accès proche est inconnu ; la somme des capacités publiques connues est livrée séparément.

## Résultats de l'exécution

- **612 stations** confirmées par le filtre spatial IGN et **4 025 communes** exportées.
- **192 803 objets OSM uniques** dans la région ou sa marge.
- **64 lignes communes aux deux extraits** dédoublonnées par identifiant ; **70 points** rapprochés de surfaces homonymes et exclus des comptages, tout en restant livrés pour audit.
- Objets par catégorie, avant exclusion des doublons point/surface : 67 044 équipements/services, 24 124 stationnements vélo, 87 338 parkings, 2 969 sites de recharge et 11 379 sites touristiques. Certains objets appartiennent à plusieurs catégories.
- **35 relations taguées non reconstruites**, consignées dans `osm_extraction_errors.csv`. Leur absence est signalée dans les indicateurs ; elle ne doit pas être interprétée comme un zéro.
- Le total strict des places publiques est renseigné pour **57 stations** ; pour les autres, les accès ou capacités inconnus empêchent de le conclure.
- **20 stations** ont un rayon maximal dont le carré englobant dépasse la région IGN : la couverture des extraits aux frontières doit être vérifiée pour ces cas.

Les notebooks ont été exécutés depuis des noyaux neufs et les exports relus. Les contrôles portent notamment sur les identifiants uniques, les géométries, le filtrage régional, un comptage comparé sans index spatial, les valeurs manquantes et l'absence de doublons de lignes de station. Les empreintes des PBF correspondent au registre de téléchargement.
