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
5. Écrit 4 tables (Lakehouse Delta dans Fabric, CSV sinon) :

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
