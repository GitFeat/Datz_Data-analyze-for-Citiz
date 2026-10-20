# Hackathon Mobility : de l'open data aux décisions d'implantation

Projet Epitech MSc 1, en partenariat avec **Citiz** (réseau coopératif d'autopartage) et **Microsoft** (Fabric).
Sujet complet : [`sujet/hackathon_mobility-project.pdf`](sujet/hackathon_mobility-project.pdf).

**Question posée** : qui a réellement accès à une option de mobilité près de chez lui, et où faut-il en ajouter ?

## Objectifs du sujet

1. **Cartographier l'accès à la mobilité** : colorer chaque zone selon le nombre d'options de transport accessibles à 5 min à pied, rapporté au nombre d'habitants.
2. **Montrer qui est concerné** : afficher les stations et arrêts par type, avec la population desservie par chacun.
3. **Proposer où s'implanter** (cœur du projet) : un outil de prédiction et d'optimisation qui estime la valeur d'un emplacement candidat, intègre un coût par type d'équipement et classe les emplacements sous contrainte de budget.

## Avancement

| Étape | Statut | Où |
|---|---|---|
| Extraction des stations Citiz (GBFS, 15 flux régionaux) | ✅ fait | `notebook/citiz_gbfs_extraction.ipynb` |
| Carte des stations Citiz en France + comptage par région / département | ✅ fait | `notebook/citiz_carte.ipynb` |
| Préparation des données pour le Lakehouse Fabric (8 tables typées et contrôlées) | ✅ fait en local, 🟡 à charger dans Fabric | `notebook/lakehouse_preparation.ipynb` |
| Choix de la zone d'étude | ✅ proposé : département du Rhône (voir ci-dessous) | — |
| Recherche des coûts d'une station Citiz | 🟡 premières sources trouvées (voir ci-dessous) | — |
| Population INSEE carreaux 200 m (Filosofi) | ⬜ à faire | — |
| Offre concurrente / complémentaire : Vélo'v, Dott, Leo&Go (GBFS), TCL (GTFS) | ⬜ à faire | — |
| Objectif 1 : indicateur « options à 400 m / habitant » par carreau | ⬜ à faire | — |
| Objectif 2 : population desservie par station / arrêt | ⬜ à faire | — |
| Objectif 3 : modèle prédictif + modèle de coût + optimisation sous budget | ⬜ à faire | — |
| Coûts d'un arrêt de bus et d'une station de vélos | ⬜ à faire | — |
| Slides + liste des sources | ⬜ à faire | — |

### Premiers résultats (extraction du 19/10/2026)

- **1 614 stations Citiz** uniques, réparties sur 15 réseaux régionaux, toutes en France métropolitaine.
- **47 départements** ont au moins une station, **49 n'en ont aucune**.
- **Aucune station en Outre-mer (DROM)** : argument pour l'objectif 3 (où et comment Citiz pourrait s'y implanter).
- Départements les plus équipés : Isère (218), Rhône (208), Bas-Rhin (205), Haute-Garonne (122), Gironde (100).

## Notebooks

Les deux notebooks tournent dans Microsoft Fabric **ou** en local. Hors Fabric, ils lisent et écrivent des CSV dans `output/`.
À lancer dans l'ordre :

### 1. `notebook/citiz_gbfs_extraction.ipynb` : extraction des stations Citiz

1. Interroge l'API de transport.data.gouv.fr (`/api/datasets`) et garde les jeux de données Citiz au format GBFS.
2. Lit le `gbfs.json` de chaque flux (gère GBFS 2.x et 3.0) pour trouver les sous-flux publiés.
3. Lit `station_information`, `station_status` et `vehicle_types`.
4. Nettoie : retire les coordonnées absentes ou hors France et DROM, et supprime les doublons entre flux qui se recoupent (AURA / Métropole de Lyon).
5. Écrit 4 CSV bruts, dans `Files/raw/citiz/` du Lakehouse (Fabric) ou dans `output/` (local). Les tables Delta sont créées ensuite par `lakehouse_preparation.ipynb`.

| Fichier | Contenu | Mode d'écriture |
|---|---|---|
| `output/citiz_flux.csv` | un flux GBFS par ligne (réseau, URL, version) | remplacé |
| `output/citiz_stations.csv` | une station par ligne : position, adresse, capacité, `geometry_wkt` | remplacé |
| `output/citiz_station_status.csv` | véhicules disponibles par station à l'instant de l'extraction | **ajouté** à chaque exécution |
| `output/citiz_vehicle_types.csv` | modèles de voitures par réseau (thermique / électrique) | remplacé |

> GBFS ne donne que l'état instantané. Relancer ce notebook régulièrement (toutes les 5 à 15 min, via la planification Fabric) accumule un historique de disponibilité, seul moyen d'obtenir un indicateur approché d'usage des stations.

### 2. `notebook/citiz_carte.ipynb` : cartes des stations Citiz

1. Transforme les stations en points géographiques (`geopandas`) et ajoute le nom lisible du réseau.
2. Télécharge une fois les contours des régions et départements (GeoJSON simplifié issu d'IGN Admin Express) dans `data/`.
3. **Carte statique** en Lambert 93 (EPSG:2154, distances en mètres), pour les slides : couleur = réseau, taille = capacité.
4. **Carte interactive** `folium`, pour la démo : regroupement des points, une couche par réseau, fiche au clic (nom, adresse, capacité, véhicules disponibles).
5. Rattache chaque station à sa région et à son département, et produit une carte du nombre de stations par département.

| Fichier produit | Contenu |
|---|---|
| `output/carte_citiz_stations.png` | carte statique des stations |
| `output/carte_citiz_stations.html` | carte interactive (s'ouvre dans un navigateur) |
| `output/carte_citiz_departements.png` | nombre de stations par département |
| `output/citiz_stations_geo.csv` | stations enrichies du département et de la région |

### 3. `notebook/lakehouse_preparation.ipynb` : tables propres pour le Lakehouse

1. Rassemble les fichiers bruts dans `Files/raw/` (CSV Citiz + contours GeoJSON).
2. Type chaque colonne explicitement (identifiants en texte, dates UTC, booléens, entiers nullables).
3. Vérifie la clé primaire de chaque table et les liens entre tables (aucun orphelin).
4. Écrit chaque table en Parquet dans `Files/clean/` puis, dans Fabric, en table Delta.
5. Produit un dictionnaire de données (`Files/clean/_dictionnaire.csv`).

En local, il produit un dossier `lakehouse/` (non versionné) qui reproduit l'arborescence Fabric.

## Lakehouse Fabric

### Organisation

```
Files/
├── raw/citiz/   CSV bruts de l'extraction GBFS (archive, jamais modifiés)
├── raw/ign/     contours régions / départements
└── clean/       Parquet typés + _dictionnaire.csv
Tables/          tables Delta (SQL, Power BI)
```

Circuit : `citiz_gbfs_extraction` → `Files/raw/` → `lakehouse_preparation` → `Files/clean/` + `Tables/`.

### Modèle de données

| Table | Clé | Lignes | Contenu |
|---|---|---|---|
| `geo_region` | `code` | 13 | régions : nom, centroïde, contour WKT |
| `geo_departement` | `code` | 96 | départements : nom, `region_code`, centroïde, contour WKT |
| `citiz_reseau` | `source` | 15 | flux GBFS régionaux Citiz : nom court, URL, version, licence |
| `citiz_station` | `station_uid` | 1 614 | stations : position, adresse, capacité, `dep_code`, `region_code` |
| `citiz_vehicle_type` | `vehicle_type_uid` | 337 | modèles de voitures : marque, motorisation |
| `citiz_station_status` | `station_uid` + `snapshot_ts` | 1 614 | disponibilité par station et par instantané (historique) |
| `citiz_station_status_vehicle` | `station_uid` + `snapshot_ts` + `vehicle_type_uid` | 2 513 | détail des véhicules disponibles par type |
| `param_cout` | `equipement` + `parametre` | 9 | paramètres de coût, avec statut sourcé / calculé / hypothèse |

Liens : `citiz_station.source` → `citiz_reseau` ; `citiz_station.dep_code` → `geo_departement` ; `geo_departement.region_code` → `geo_region` ; `citiz_station_status*.station_uid` → `citiz_station` ; `*.vehicle_type_uid` → `citiz_vehicle_type`.

Conventions : noms en minuscules sans accent, identifiants composés `source:id` (un même `station_id` existe dans plusieurs réseaux), géométries en WKT + `lat` / `lon`, colonne `_loaded_at` sur chaque table.

### Charger les données dans Fabric

1. **Créer le Lakehouse** : dans l'espace de travail Fabric de l'équipe, New item > Lakehouse (ex. `lh_mobility`).
2. **Déposer les fichiers bruts** : Files > New subfolder `raw/citiz`, puis Upload > Upload files avec les 4 CSV de `output/` (ou le contenu de `lakehouse/Files/raw/citiz/`).
3. **Importer les notebooks** : dans l'espace de travail, Import > Notebook > From this computer, pour `citiz_gbfs_extraction.ipynb` et `lakehouse_preparation.ipynb`.
4. **Attacher le Lakehouse** à chaque notebook (panneau Explorer > Add data items > Existing data sources > `lh_mobility`), comme Lakehouse par défaut.
5. **Lancer `lakehouse_preparation`** : les 8 tables apparaissent dans `Tables/`. Les contrôles « OK » et la requête SQL de la dernière cellule confirment le chargement.
6. **Collecter l'historique** : planifier `citiz_gbfs_extraction` (Run > Schedule, toutes les 15 min) puis `lakehouse_preparation` (par exemple toutes les heures), ou les enchaîner dans un pipeline Fabric.
7. **Power BI** : depuis le Lakehouse, New semantic model, sélectionner les tables, puis recréer les liens ci-dessus dans la vue Modèle.

## Choix de la zone d'étude : le Rhône (Métropole de Lyon)

Le sujet autorise à se limiter à une zone si le choix est justifié. Comparaison des trois départements les mieux équipés en Citiz :

| | Rhône (Lyon) | Bas-Rhin (Strasbourg) | Isère (Grenoble) |
|---|---|---|---|
| Stations Citiz | 208 | 205 | 218 |
| Bus, tram, métro (GTFS) | ✅ TCL | ✅ CTS | ✅ TAG + cars de l'Isère |
| Vélos en libre-service (GBFS) | ✅ Vélo'v | ✅ Vélhop | ❌ |
| Trottinettes / vélos en libre accès | ✅ Dott | ❌ | ✅ Voi |
| Autopartage concurrent | ✅ Leo&Go | ❌ | ❌ |

- Lyon est le seul territoire où **tous les types de transport** demandés sont publiés, y compris un **concurrent d'autopartage** (Leo&Go) : on peut « tenir compte de l'offre existante » comme l'exige l'objectif 3.
- Le **département entier** (et non la seule métropole) inclut des zones rurales (Beaujolais, Monts du Lyonnais), indispensables pour traiter l'équité dense / peu dense.
- Le code doit rester paramétrable par liste de départements pour pouvoir être relancé ailleurs (Strasbourg, ou un territoire sans Citiz).

**Points d'attention**
- Deux flux Citiz se recoupent sur Lyon (AURA et Métropole de Lyon) : vérifier le dédoublonnage.
- GTFS des cars interurbains du Rhône non vérifié : sans lui, les zones rurales paraîtront moins desservies. Complément possible : le fichier national « Arrêts de transport en France ».

## Coûts d'une station Citiz (pistes trouvées)

Pas de grille tarifaire publique. Source la plus précise : la convention type entre le Pôle métropolitain du Genevois français et Citiz Alpes-Loire (2021).

| Poste | Montant | Statut |
|---|---|---|
| Boîtier télématique par voiture | 4 000 € HT | sourcé |
| Frais fixes d'exploitation | 250 €/mois/voiture | sourcé |
| Recette Citiz par km | 0,19 €/km | sourcé |
| Taille minimale d'une station | 2 voitures | sourcé |
| Seuil de rentabilité déduit | ≈ 1 300 km/mois/voiture | calculé (250 / 0,19) |
| Prix d'achat d'une voiture | à fixer | hypothèse |
| Aménagement de la station (marquage, totem, panneaux) | « minime » selon Citiz | hypothèse |

**À faire** : demander directement à Citiz (partenaire) le coût d'aménagement, le prix moyen d'une voiture et le seuil de rentabilité ; recouper avec des délibérations de communes du Rhône.

## Installation locale

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas geopandas matplotlib folium requests ipykernel
```

Puis ouvrir les notebooks avec le noyau Python du `.venv`, en commençant par `citiz_gbfs_extraction.ipynb`.

## Arborescence

```
.
├── notebook/   # notebooks d'extraction et d'analyse
├── output/     # tables CSV et cartes produites (versionnées : utiles pour les slides)
├── lakehouse/  # miroir local du Lakehouse Fabric (non versionné, régénéré)
├── ign-osm/    # module IGN / OpenStreetMap (contours officiels, réseau piéton, accessibilité à 5 min)
├── data/       # données brutes téléchargées (non versionnées, re-téléchargées automatiquement)
└── sujet/      # énoncé du hackathon
```

## Sources de données

| Donnée | Source |
|---|---|
| Stations Citiz (GBFS) | [transport.data.gouv.fr](https://transport.data.gouv.fr/datasets?type=vehicles-sharing&q=citiz) |
| Contours régions / départements | [gregoiredavid/france-geojson](https://github.com/gregoiredavid/france-geojson) (dérivé d'IGN Admin Express) |
| Coûts d'exploitation Citiz | [Convention Genevois français / Citiz Alpes-Loire (2021)](https://genevoisfrancais.org/wp-content/uploads/CS2021_23.2-AUTOPARTAGE_Convention-cadreAnnexe.pdf) |
| Modèle économique de l'autopartage | [Livre blanc Citiz 2026](https://www.citiz.coop/uploads/2026/02/2026-CITIZ-livre_blanc.pdf) |

À venir : carreaux INSEE 200 m (Filosofi), GTFS TCL, GBFS Vélo'v / Dott / Leo&Go, projections INSEE Omphale, réseau piéton OpenStreetMap.
