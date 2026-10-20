# IGN et OpenStreetMap — Auvergne-Rhône-Alpes

## Objectif

Préparer les données permettant de calculer quels habitants peuvent rejoindre une station de mobilité en cinq minutes à pied.

- IGN fournit les contours de la région et des communes.
- OpenStreetMap fournit les rues et chemins du futur réseau piéton.
- La population et les stations proviendront des autres sources de l'équipe.

## Livrable de données pour l'équipe

L'objectif du module est de fournir des données réutilisables, pas seulement des démonstrations de marche. Les notebooks Clermont-Ferrand 04 à 08 servent à apprendre et vérifier une méthode locale ; ils ne constituent pas une extraction de réseau piéton pour toute la région.

Le dépôt contient déjà `output/citiz_stations_geo.csv`, produit par les notebooks Citiz de l'équipe. Lors de son inspection, il contient 1 614 lignes nationales, dont **612 classées en Auvergne-Rhône-Alpes**, avec des `station_uid` distincts et des colonnes `lat` / `lon`. Le rattachement régional de ces lignes reste à vérifier avec notre contour IGN avant un export dédié. Leurs identifiants devront être conservés pour permettre les jointures avec le travail de l'équipe.

Le livrable prévu comprend :

1. Les contours IGN régionaux et communaux déjà préparés.
2. Des couches OSM régionales d'équipements/services, stationnements vélo, parkings et sites touristiques, avec identifiants, catégories, géométries et capacités lorsqu'elles sont renseignées. Ces couches restent à extraire.
3. Un tableau d'indicateurs autour des stations Citiz disponibles, joint par `station_uid`, en commençant par les comptages OSM. Les définitions des catégories et des rayons seront explicites.
4. Les sources, dates, règles de calcul et limites, notamment la distinction entre une valeur inconnue et un vrai zéro.

Les variables de recharge doivent distinguer les sites, les bornes et les points de recharge : un objet OSM `amenity=charging_station` ne donne pas automatiquement un nombre de bornes. Les places publiques de parking demandent une capacité connue et une règle d'accès ; le nombre de parkings ne peut pas être substitué au nombre de places.

Les départs en heure de pointe demandent des horaires GTFS et une définition du jour et de l'heure. Les accidents demandent une source dédiée et une période. Aucun fichier correspondant n'a été trouvé lors de l'inventaire du dépôt. Ces indicateurs ne seront pas remplacés par des zéros.

La variable `pedestrian_network_distance_m` demande de définir les origines et les destinations. Un réseau seul ne donne pas une distance unique par station. Les données de population et les arrêts nécessaires à certains usages de cette variable restent à intégrer.

## Commencer dans VS Code

Le parcours utilise désormais des notebooks : les explications en français, le code Python en anglais et les résultats sont réunis dans un même document.

Le noyau doit utiliser l'environnement local `ign-osm/.venv`, qui contient les dépendances du projet. L'extension Jupyter de VS Code sert d'interface ; JupyterLab n'est pas nécessaire.

1. Ouvrir [01_ign_region.ipynb](notebooks/01_ign_region.ipynb).
2. En haut à droite, cliquer sur **Sélectionner le noyau / Select Kernel**, puis **Sélectionner un autre noyau / Select Another Kernel** et **Environnements Python / Python Environments**.
3. Choisir `ign-osm/.venv/bin/python` ou le noyau enregistré **Python (IGN / OSM)**. Si nécessaire, utiliser **Entrer le chemin de l'interpréteur / Enter interpreter path** via la commande **Python: Select Interpreter** pour indiquer ce fichier, puis revenir au choix du noyau du notebook.
4. Lire l'explication puis exécuter la cellule correspondante avec `Maj + Entrée`.

Si VS Code utilise `/usr/bin/python3` et échoue à installer `ipykernel`, vérifier le noyau sélectionné : ce Python système ne contient pas les dépendances du projet. Le noyau du notebook et l'interpréteur choisi pour les fichiers Python peuvent être différents.

Pour recréer l'environnement sur une autre machine, depuis la racine du dépôt :

```bash
python3 -m venv ign-osm/.venv
ign-osm/.venv/bin/python -m pip install -r ign-osm/requirements.txt
```

L'environnement a déjà été préparé sur la machine actuelle : il suffit de le sélectionner dans VS Code.

Le noyau conserve les variables entre les cellules. Après une modification, **redémarrer le noyau puis tout exécuter** permet de vérifier qu'aucune variable d'une ancienne exécution n'est nécessaire.

## Premier notebook : limites régionales IGN

Le notebook contient six étapes :

1. Préparer les chemins.
2. Télécharger le fichier des régions s'il n'existe pas déjà.
3. Explorer les colonnes et le système de coordonnées.
4. Sélectionner l'Auvergne-Rhône-Alpes avec le code INSEE `84`.
5. Exporter le contour en GeoJSON et relire le résultat.
6. Afficher un aperçu dans le notebook et l'enregistrer en HTML.

Le code est directement visible dans les cellules. Il remplace les trois scripts initiaux de téléchargement, d'extraction et de prévisualisation.

## Source et fichiers

Source du sujet : IGN **ADMIN EXPRESS**. Déclinaison choisie : **ADMIN EXPRESS COG**, édition du 1er janvier 2026, format FlatGeobuf.

- [Présentation officielle IGN](https://cartes.gouv.fr/aide/fr/partenaires/ign/generalites-ign/actualites/2026-06-flatgeobuf-geoparquet/)
- [Fichier officiel des régions](https://data.geopf.fr/chunk/telechargement/download/ADMIN-EXPRESS-COG-PARTIEL/ADMIN-EXPRESS-COG_4-0__FLATGEOBUF_WGS84G_FRA_2026-01-01/region.fgb)
- [Traçabilité du premier téléchargement](sources.csv) : millésime, date de récupération, URL, taille et empreinte du fichier. Ce registre décrit le téléchargement initial ; le notebook ne le réécrit pas.
- Licence : à confirmer dans les métadonnées officielles avant redistribution.

Chemins relatifs à `ign-osm/` :

| Fichier | Rôle |
|---|---|
| `data/raw/ign/regions_2026.fgb` | Source nationale IGN, conservée intacte |
| `data/processed/region_84.geojson` | Contour régional sélectionné, avec `insee_code`, `name`, `geometry` |
| `data/processed/region_84_preview.html` | Aperçu simplifié consultable hors connexion |

Les données et les sauvegardes temporaires Jupyter sont exclues de Git. Les notebooks sont versionnés. Internet est nécessaire au premier téléchargement, mais pas pour réutiliser les données locales. Les sorties GeoJSON et HTML sont remplacées à chaque exécution.

Le dessin est simplifié avec une tolérance de 100 mètres pour l'affichage seulement. Le GeoJSON conserve la géométrie originale sélectionnée. Cette vue montre le contour seul, sans fond de carte.

## Progression

- [x] Télécharger les régions IGN.
- [x] Explorer leurs attributs et sélectionner la région `84`.
- [x] Exporter et relire une géométrie valide.
- [x] Afficher le contour régional.
- [x] Récupérer les communes de la région.
- [x] Télécharger les données OSM.
- [ ] Construire et vérifier le réseau piéton.
- [ ] Calculer cinq minutes de marche autour d'un point.

Les limites IGN ne contiennent pas à elles seules les habitants ou les stations. Une géométrie valide et un affichage correct ne constituent pas une vérification indépendante de la précision des frontières.

## Deuxième notebook : communes de la région

Ouvrir [02_ign_municipalities.ipynb](notebooks/02_ign_municipalities.ipynb) avec le noyau **Python (IGN / OSM)**. Il est indépendant du premier notebook : aucune variable de celui-ci n'est nécessaire.

Le parcours télécharge le fichier national des communes de la même édition IGN 2026, explore cinq lignes, filtre le rattachement administratif à la région `84`, renomme les colonnes utiles en anglais et exporte le résultat.

- Source locale : `data/raw/ign/municipalities_2026.fgb` (456 183 416 octets).
- Résultat : `data/processed/municipalities_84.geojson` (environ 168 Mo).
- Colonnes : `insee_code`, `name`, `department_code`, `region_code`, `geometry`.
- Résultat vérifié : **4 025 communes**, réparties sur **12 codes de département**.

La première récupération nécessite Internet ; les suivantes utilisent le fichier local. Le téléchargement écrit d'abord un fichier `.part`, puis vérifie sa taille et sa signature avant de le renommer. La source n'est pas modifiée par le filtrage. La sortie GeoJSON est remplacée lors d'une nouvelle exécution.

Le notebook a été validé et exécuté dans l'ordre depuis un noyau neuf. Les codes des communes sont uniques et renseignés, les noms sont présents et les géométries sont non vides et valides. Le GeoJSON exporté a été relu avec le même nombre de lignes et les mêmes identifiants.

La section **7 — Afficher les contours des communes** affiche également les 4 025 contours directement dans le notebook et produit `data/processed/municipalities_84_preview.html`, ouvrable hors connexion. Elle utilise des coordonnées Lambert-93 et une simplification à 100 mètres uniquement pour l'affichage. Les traits sont des limites administratives, pas des routes. Les simplifications indépendantes peuvent créer de petits écarts visuels entre communes voisines.

Le fichier source IGN contient une population agrégée par commune et une date de recensement. Ces champs ne sont pas exportés à cette étape : ils ne remplacent pas les données fines nécessaires au calcul de l'accessibilité des habitants. Les populations communales ne sont pas des positions d'habitants.

## Troisième notebook : récupération OSM

Ouvrir [03_osm_download.ipynb](notebooks/03_osm_download.ipynb) avec le noyau **Python (IGN / OSM)**. Ce notebook utilise les bibliothèques déjà installées.

Geofabrik, la source OSM indiquée dans le sujet, diffuse séparément les anciennes régions [Auvergne](https://download.geofabrik.de/europe/france/auvergne.html) et [Rhône-Alpes](https://download.geofabrik.de/europe/france/rhone-alpes.html). Nous récupérons les deux archives datées `261016`, plutôt que les liens `latest` qui changent régulièrement.

| Fichier dans `data/raw/osm/` | Taille attendue |
|---|---:|
| `auvergne-261016.osm.pbf` | 156 231 713 octets |
| `rhone-alpes-261016.osm.pbf` | 531 106 658 octets |

Le format PBF contient des objets OpenStreetMap ; ce n'est pas encore un réseau piéton prêt pour les itinéraires. Le nom des archives indique une date d'extrait, pas l'horodatage précis du contenu OSM, qui reste à lire.

Le notebook télécharge par blocs dans un fichier `.part`, vérifie la taille et l'empreinte MD5 fournie par Geofabrik, puis conserve les métadonnées dans un JSON associé. Il réutilise les fichiers existants, contrôle de nouveau leur intégrité et met à jour `sources.csv` sans dupliquer leurs lignes. Les fichiers MD5 locaux évitent également de nécessiter Internet à chaque exécution.

Attribution : © OpenStreetMap contributors, données sous [licence ODbL 1.0](https://www.openstreetmap.org/copyright), extraites par Geofabrik.

Les deux extraits peuvent se chevaucher : leurs objets devront être dédoublonnés lors de la fusion. Leurs limites ne doivent pas être supposées identiques au contour IGN ; la gestion des frontières reste à traiter avant un calcul régional.

**Vérifications effectuées :** les deux fichiers ont été récupérés, leurs tailles et empreintes MD5 correspondent aux références Geofabrik. Le notebook a été exécuté entièrement depuis un noyau neuf en réutilisant les fichiers locaux ; le registre contient les deux sources sans doublons. Le contenu des objets OSM reste à explorer avant tout calcul de trajet.

**Prochaine étape pédagogique :** lire quelques objets OSM sur une petite zone et comprendre leurs attributs avant de construire un graphe piéton.

## Quatrième notebook : explorer les rues OSM

Ouvrir [04_osm_streets_exploration.ipynb](notebooks/04_osm_streets_exploration.ipynb) avec le noyau **Python (IGN / OSM)**. Ce notebook utilise **PyOsmium** (`osmium`), ajouté à `requirements.txt`, pour lire l'extrait local Auvergne. Aucun téléchargement supplémentaire de données n'est nécessaire.

Sur une autre machine, installer les dépendances mises à jour avec :

```bash
ign-osm/.venv/bin/python -m pip install -r ign-osm/requirements.txt
```

La zone d'apprentissage est un rectangle du centre de Clermont-Ferrand : longitudes de `3.07` à `3.095`, latitudes de `45.765` à `45.785`. Il ne s'agit pas de la commune entière. Le périmètre final du projet reste régional.

Le parcours explique les nœuds, voies et tags OSM, lit l'horodatage de réplication déclaré dans l'en-tête, extrait les voies portant un tag `highway`, affiche leurs attributs et produit un aperçu HTML directement dans le notebook. L'index des coordonnées des nœuds consomme de la mémoire pendant le parcours de l'extrait complet.

**Résultats vérifiés :** 3 736 voies extraites, aucune géométrie incomplète signalée dans la source pendant ce parcours et aucune intersection non linéaire écartée dans la zone. Les identifiants sont uniques et les géométries sont valides et non vides. Le fichier exporté a été relu avec le même nombre de voies et les mêmes identifiants. Le notebook a été exécuté depuis un noyau neuf.

- Horodatage OSM déclaré : `2026-10-16T20:21:21Z`.
- Données exploratoires : `data/processed/clermont_streets_sample.geojson`.
- Aperçu hors connexion : `data/processed/clermont_streets_preview.html`.
- Provenance : extrait Auvergne Geofabrik enregistré dans `sources.csv`, © OpenStreetMap contributors, licence ODbL 1.0.

`highway` ne signifie pas forcément autoroute ; ce tag décrit aussi les rues et chemins. `foot`, `access`, `sidewalk`, `surface`, `bridge`, `tunnel` et `layer` sont conservés pour comprendre les accès et les croisements. Une valeur absente signifie « non renseigné ».

Cette sortie est **exploratoire** : les voies sont découpées au rectangle et l'accès piéton n'est pas encore filtré. Elle ne constitue pas un graphe de routage. Pour construire le graphe, il faudra repartir des nœuds et voies OSM, respecter les règles d'accès et les connexions, puis calculer les longueurs. Deux traits qui se croisent sur l'aperçu ne sont pas nécessairement connectés.

**Prochaine étape :** définir un premier filtre piéton, puis construire le graphe sur cette zone test.

## Cinquième notebook : premier filtre piéton

Ouvrir [05_osm_walking_filter.ipynb](notebooks/05_osm_walking_filter.ipynb) avec **Python (IGN / OSM)**. Aucune dépendance supplémentaire n'est nécessaire. Le notebook 04 a été enrichi pour conserver les tags `motorroad`, les restrictions piétonnes conditionnelles et directionnelles, ainsi que les horaires. Relancer sa version actuelle si le notebook 05 signale des colonnes manquantes.

Le profil donne à chaque voie un statut `included`, `excluded` ou `review`, accompagné d'une raison en anglais. Les règles sont expliquées avant leur fonction Python. Les restrictions spécifiques `foot` sont prioritaires sur `access`. Les accès publics usuels sont retenus, les accès privés ou interdits sont écartés et les cas limités, horaires ou ambigus sont laissés à examiner. Les types de voie retenus par défaut sont des hypothèses explicites du prototype.

Résultat sur les 3 736 voies de la zone test :

| Statut | Nombre |
|---|---:|
| Retenues | 3 399 |
| Exclues | 195 |
| À examiner | 142 |

Parmi les voies retenues, **144** ont une autorisation piétonne explicite et **3 255** sont retenues par hypothèse liée au type de voie. Les escaliers sont inclus pour la marche générale ; cela ne constitue pas un profil PMR.

Sorties dans `data/processed/` :

- `clermont_walking_audit.geojson` : toutes les voies, avec statut et raison.
- `clermont_walking_ways.geojson` : uniquement les voies retenues.
- `clermont_walking_preview.html` : comparaison visuelle, également affichée dans le notebook (bleu : retenues, gris : exclues, orange : à examiner).

Le notebook a été exécuté depuis un noyau neuf. Dix cas d'exemple vérifient notamment la priorité de `foot`, les accès privés, les pistes cyclables et les restrictions conditionnelles. Les sorties ont été relues pour vérifier les identifiants, les statuts et la validité des géométries retenues.

Les règles suivent les conventions de tags documentées dans le [wiki OSM sur les accès](https://wiki.openstreetmap.org/wiki/Key:access?uselang=nl), avec des [hypothèses de profil par défaut](https://wiki.openstreetmap.org/wiki/Default_access_restrictions) propres au projet. Elles ne constituent pas un moteur de routage complet : les barrières sur les nœuds, les relations et les règles horaires restent à traiter. Les voies découpées ne permettent pas à elles seules de reconstruire les connexions.

**Prochaine étape :** construire le graphe à partir des identifiants des nœuds OSM sur la zone test, puis calculer les longueurs des segments.

## Sixième notebook : construire le graphe

Ouvrir [06_osm_graph.ipynb](notebooks/06_osm_graph.ipynb) avec **Python (IGN / OSM)** après les notebooks 04 et 05. La dépendance **NetworkX** a été ajoutée à `requirements.txt` et installée dans l'environnement local.

Le notebook explique un graphe comme deux tableaux : les points (**nœuds**) et les liens (**arêtes**). Il relit les 3 399 voies retenues dans le PBF source, récupère leurs identifiants de nœuds et crée un segment entre chaque paire consécutive. Les connexions reposent sur les identifiants OSM communs ; aucun lien n'est ajouté aux seuls croisements visuels des lignes.

Pour les segments touchant la zone test, les deux extrémités source sont conservées : certains nœuds sont donc légèrement à l'extérieur du rectangle. Une projection temporaire en Lambert-93 fournit les longueurs horizontales en mètres. Le graphe `MultiGraph` conserve les éventuels segments parallèles et suppose un parcours à pied dans les deux sens pour les voies retenues.

Résultats vérifiés :

- **10 101 nœuds** et **11 600 segments**.
- **42 composantes connexes**, c'est-à-dire 42 groupes séparés dans cette extraction ; le plus grand contient 9 845 nœuds.
- Aucun segment nul ni répétition consécutive d'un même nœud écarté lors de cette exécution.
- Tous les identifiants de voies sélectionnées ont été retrouvés dans le PBF.

Le notebook montre un exemple de nœud relié à au moins trois voisins, avec les identifiants et les longueurs des liens. Il ne supprime pas les petites composantes automatiquement.

Fichiers dans `data/processed/` :

| Fichier | Rôle |
|---|---|
| `clermont_graph_nodes.geojson` | Points OSM avec leurs coordonnées |
| `clermont_graph_edges.geojson` | Segments, extrémités et longueurs |
| `clermont_walking_graph.graphml` | Graphe avec connexions et attributs |
| `clermont_graph_preview.html` | Aperçu hors connexion, également dans le notebook |

L'exécution depuis un noyau neuf a réussi. Le GraphML a été relu et contrôlé sur tous les identifiants de nœuds, toutes les connexions et toutes les longueurs. Les GeoJSON ont également été relus. L'aperçu présente les segments en bleu, les points en rouge et un exemple de connexion en vert.

Ce graphe est une **structure exploratoire**, pas encore un réseau validé pour les trajets : les barrières et restrictions portées par les nœuds ou les relations ne sont pas encore appliquées. Les groupes séparés peuvent provenir des données, du filtre ou de la frontière de la zone. Une marge sera nécessaire avant un calcul d'accessibilité. Les longueurs ignorent les pentes et les durées ne sont pas encore calculées.

**Prochaine étape pédagogique :** vérifier les points de passage sensibles, puis étudier un premier trajet sur la zone test. La cible finale reste l'Auvergne-Rhône-Alpes ; Clermont-Ferrand sert à valider la méthode sur un petit périmètre.

## Septième notebook : un premier trajet concret

Ouvrir [07_osm_example_route.ipynb](notebooks/07_osm_example_route.ipynb) avec **Python (IGN / OSM)** après le notebook 06. Aucune nouvelle dépendance ni récupération de données n'est nécessaire.

Le notebook relit les tags des 10 101 nœuds du graphe dans le PBF pour contrôler les barrières et les accès. Il conserve les décisions dans un CSV, retire les nœuds exclus ou à examiner, puis cherche un chemin entre deux points d'exemple proches du centre de Clermont-Ferrand. Les points ne représentent pas des stations Citiz ou des adresses validées.

Le profil de nœuds reprend la priorité de `foot` sur `access`, retient certaines barrières supposées franchissables pour la marche générale et laisse les autres barrières sans permission piétonne explicite à examiner. Les restrictions conditionnelles, horaires et verrouillages connus sont également laissés à examiner. Les règles sont visibles dans une fonction et vérifiées sur cinq cas d'exemple. Ce retrait de nœuds entiers est conservateur et peut supprimer des passages réellement ouverts.

Résultat du contrôle des nœuds : **10 exclus**, **331 à examiner**, **9 760 conservés**, dont 9 702 sans restriction de nœud détectée. Tous les nœuds du graphe ont été retrouvés dans la source. L'absence de tag n'est pas une preuve d'absence d'obstacle sur le terrain.

Les coordonnées d'exemple sont `(3.0810, 45.7775)` et `(3.0875, 45.7795)`, dans l'ordre longitude, latitude. Elles sont rattachées aux nœuds restants les plus proches, avec des écarts d'environ **20,7 m** et **4,8 m**. Le code s'arrête si l'écart dépasse 50 m, si les deux nœuds sont identiques ou si aucun chemin ne les relie ; aucun déplacement vers une autre composante n'est fait automatiquement.

Le plus court chemin minimise la somme des `length_m`. Le résultat sur le réseau est d'environ **691,4 m**, soit **8,6 minutes** à la vitesse supposée de **4,8 km/h**. Les distances d'approche entre coordonnées libres et nœuds ne sont pas incluses : ces passages n'ont pas été validés. La durée ignore les pentes, feux et attentes.

Sorties dans `data/processed/` :

| Fichier | Contenu |
|---|---|
| `clermont_node_access_audit.csv` | Tags et décision pour chaque nœud |
| `clermont_node_filtered_graph.graphml` | Réseau après retrait des nœuds exclus ou à examiner |
| `clermont_example_route.geojson` | Segments ordonnés du trajet |
| `clermont_example_route.json` | Points, rattachements, distance, vitesse et durée |
| `clermont_route_preview.html` | Réseau gris, trajet rouge, départ vert et arrivée violette |

L'exécution depuis un noyau neuf a réussi. Le trajet ne traverse aucun nœud retiré. La somme des longueurs exportées correspond à celle calculée par NetworkX ; le GeoJSON et le GraphML ont été relus. L'aperçu est affiché dans le notebook et fonctionne également hors connexion.

Ce trajet illustre le fonctionnement du graphe ; il n'est pas un itinéraire de navigation validé. Les restrictions portées par les relations, les obstacles non cartographiés, les hypothèses d'accès par défaut et les limites du rectangle restent à considérer. Un détour plus court hors de la zone peut ne pas être représenté.

**Prochaine étape pédagogique :** montrer les portions du réseau accessibles depuis un seul point en cinq minutes, en prévoyant une marge adaptée autour de la zone et en conservant les hypothèses visibles.

## Huitième notebook : cinq minutes de marche depuis un point

Ouvrir [08_osm_five_minute_reachability.ipynb](notebooks/08_osm_five_minute_reachability.ipynb) avec **Python (IGN / OSM)** après le notebook 07. Il reprend le départ et le réseau filtré de la démonstration précédente. Aucune nouvelle dépendance ni récupération de données n'est nécessaire.

À 4,8 km/h, cinq minutes correspondent à 400 m parcourus. Le notebook utilise Dijkstra avec cette limite pour trouver les nœuds accessibles, puis découpe les segments partiellement atteignables. Un segment peut être rejoint depuis ses deux extrémités ; les portions qui se chevauchent sont fusionnées et un éventuel milieu inaccessible reste exclu.

La marge entre le départ et la frontière de l'extraction est contrôlée avant le calcul. Elle vaut environ **813,8 m**, supérieure au budget de 400 m. Aucun chemin de cette longueur horizontale ne peut donc atteindre la frontière de la zone test. Le code s'arrête si le départ ou la durée sont modifiés au point de rendre la marge insuffisante.

Résultats sur le réseau test : **928 nœuds OSM accessibles**, **1 132 portions de segments**, dont **65 portions partielles**. Ces nombres décrivent le réseau, pas une population ou un nombre de rues distinctes.

| Fichier dans `data/processed/` | Rôle |
|---|---|
| `clermont_reachable_nodes_5min.geojson` | Nœuds atteints, distance et durée depuis le départ |
| `clermont_reachable_portions_5min.geojson` | Portions de segments réellement atteignables dans le budget |
| `clermont_reachability_5min.json` | Hypothèses, départ, marge et compteurs |
| `clermont_reachability_preview.html` | Chemins bleus, départ vert et cercle orange à vol d'oiseau |

L'aperçu est aussi intégré au notebook. Le cercle de 400 m sert de comparaison visuelle ; il ne constitue pas un résultat d'accessibilité. Les espaces entre les lignes ne sont pas remplis artificiellement et ne représentent pas une surface d'habitations desservies.

L'exécution depuis un noyau neuf a réussi. Quatre exemples vérifient les découpages de segments, notamment une portion partielle et un milieu inaccessible entre deux extrémités atteintes. Les distances maximales sur les portions sont contrôlées, y compris à l'intérieur des segments. Les nœuds atteints en trois minutes sont bien inclus dans ceux atteints en cinq minutes. Les GeoJSON exportés ont été relus et leurs identifiants vérifiés.

Les cinq minutes commencent au **nœud rattaché**, pas aux coordonnées libres initiales : les 20,7 m d'approche non validée sont exclus. Les limites des profils d'accès précédents, les restrictions de relations, les pentes et les attentes restent à considérer. Ce résultat est une démonstration locale, pas encore une mesure de population desservie ou une analyse régionale.

**Prochaine étape :** appliquer le calcul à une vraie station et préparer le croisement avec les données de population de l'équipe.

## Dépannage : noyau introuvable dans VS Code

Le noyau local a été enregistré sous le nom **Python (IGN / OSM)** sur la machine actuelle. Après un rechargement de la fenêtre VS Code, le sélectionner en haut à droite du notebook. Le fichier `.vscode/settings.json` propose également l'interpréteur du module par défaut ; ce réglage ne remplace pas une sélection de noyau déjà mémorisée.

Sur une autre machine, enregistrer le noyau après avoir installé les dépendances :

```bash
ign-osm/.venv/bin/python -m ipykernel install --user --name citiz-ign-osm --display-name "Python (IGN / OSM)"
```

Cette commande ajoute une entrée à la configuration Jupyter de l'utilisateur. Elle pointe vers l'environnement local existant et ne crée pas un nouvel environnement.
