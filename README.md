# Hackathon Mobility : de l'open data aux décisions d'implantation

Projet Epitech MSc 1, en partenariat avec **Citiz** (réseau coopératif d'autopartage) et **Microsoft** (Fabric).
Sujet complet : [`sujet/hackathon_mobility-project.pdf`](sujet/hackathon_mobility-project.pdf).

**Question posée** : qui a réellement accès à une option de mobilité près de chez lui, et où faut-il en ajouter ?

## Objectifs du sujet

1. **Cartographier l'accès à la mobilité** : colorer chaque zone selon le nombre d'options de transport accessibles à 5 min à pied, rapporté au nombre d'habitants.
2. **Montrer qui est concerné** : afficher les stations et arrêts par type, avec la population desservie par chacun.
3. **Proposer où s'implanter** (cœur du projet) : un outil de prédiction et d'optimisation qui estime la valeur d'un emplacement candidat, intègre un coût par type d'équipement et classe les emplacements sous contrainte de budget.

## Où en est-on ?

Phase actuelle : **exploration**. Chaque module établit quelles données sont exploitables, et le documente avec les résultats réellement obtenus.

| Module | Contenu | Statut |
|---|---|---|
| [`citiz/`](citiz/README.md) | Stations Citiz (GBFS) : extraction, qualité des données, rattachement au département, cartes | exploration terminée pour les flux Citiz |
| [`ign-osm/`](ign-osm/README.md) | Contours IGN et extraits OpenStreetMap (notebooks 01 à 03) ; parcours pédagogique du réseau piéton dans `notebooks/learning/` | entrées de `regional-data/` |
| [`regional-data/`](regional-data/README.md) | Livrable régional Auvergne-Rhône-Alpes : équipements OSM et distances à pied autour de chaque station Citiz | table finale disponible (`data/release/`) |
| [`population/`](population/README.md) | Population INSEE par carreau de 200 m et projections 2021-2070 | carreaux avec coordonnées, pas encore croisés avec les stations |
| [`lakehouse/`](lakehouse/README.md) | Tables typées et contrôlées pour Microsoft Fabric, assemblées depuis les modules ci-dessus | 10 tables, exécuté en local, pas encore dans Fabric |
| [`dashboard/`](dashboard/README.md) | Exploration interactive des tables CSV (Streamlit + PyGWalker) | outil d'exploration |

## Pipeline de l'équipe

Chaque module produit une étape ; `lakehouse/` les assemble. Les notebooks d'analyse (`citiz` 02, `regional-data` 08 et 09) et le parcours pédagogique d'`ign-osm` ne sont pas sur ce chemin.

1. `citiz` 01 → 03 : stations Citiz, nettoyées et rattachées à leur département.
2. `ign-osm` 01 → 03 : contours IGN et extraits OSM d'Auvergne-Rhône-Alpes.
3. `regional-data` 01 → 03, puis 07 : indicateurs à pied autour de chaque station, table finale `data/release/citiz_aura_final.csv`.
4. `population/reference/` : carreaux de 200 m avec leurs coordonnées (fichier versionné).
5. `lakehouse` 01 : 10 tables pour Fabric, dans `lakehouse/data/Files/`. La liste des fichiers à déposer est dans [`lakehouse/README.md`](lakehouse/README.md#fichiers-à-déposer-dans-fabric).

Reste à faire : la population desservie par station (à 400 m, soit 5 min à pied) et les arrêts de transport en commun.

### Principaux constats

- **1 615 stations Citiz** sur 15 réseaux régionaux, **aucune en Outre-mer**. Auvergne-Rhône-Alpes est la région la plus équipée (613 stations).
- Les flux GBFS Citiz décrivent bien **où** sont les stations (position, capacité, motorisation des voitures), mais **pas leur usage** : la date de dernière mise à jour des statuts a plus d'un an pour 57 % des stations. Détails dans [`citiz/`](citiz/README.md#résultats-de-lexploration).
- La population d'Auvergne-Rhône-Alpes est disponible par carreau de 200 m (312 143 carreaux, 7,7 millions d'habitants) avec 11 scénarios de projection jusqu'en 2070 ([`population/`](population/README.md)).
- Le réseau piéton OSM permet de calculer des distances à pied réelles autour des stations ([`regional-data/`](regional-data/README.md)).

### Données pas encore intégrées

Arrêts de transport en commun (GTFS), autres services partagés (Vélo'v, Dott, Leo&Go). Les carreaux de population sont dans le Lakehouse mais pas encore croisés avec les stations ([`population/`](population/README.md)).

## Périmètre géographique

- **Données régionales** : Auvergne-Rhône-Alpes, la région où Citiz a le plus de stations ([`regional-data/`](regional-data/README.md)).
- **Zone de démonstration proposée** : le département du Rhône (Métropole de Lyon). C'est le seul territoire où tous les types de transport demandés sont publiés en open data (TCL, Vélo'v, Dott), ainsi qu'un autopartage concurrent (Leo&Go). Choix à valider en équipe.
- **Outre-mer** : Citiz n'y est pas présent ; à traiter dans l'objectif 3 (où et comment s'y implanter).

## Organisation du dépôt

```
.
├── sujet/            énoncé du hackathon
├── citiz/            module stations Citiz
├── ign-osm/          contours IGN, extraits OSM et parcours pédagogique
├── regional-data/    livrable régional Auvergne-Rhône-Alpes
├── population/       population INSEE Auvergne-Rhône-Alpes (carreaux 200 m, projections)
├── lakehouse/        tables pour Microsoft Fabric, assemblées depuis les modules
├── dashboard/        explorateur interactif
├── output/           référence Citiz partagée entre les modules (versionnée)
└── SOURCES.md        liste unique des sources de données
```

Chaque module suit la même organisation :

| Élément | Rôle |
|---|---|
| `README.md` | Objectif, procédure, fichiers produits, résultats réels et limites |
| `notebooks/` | Parcours principal, numéroté dans l'ordre d'exécution |
| `SOURCES.md` | Sources, versions, dates et licences |
| `DATA_DICTIONARY.md` | Signification des colonnes produites |
| `requirements.txt` | Dépendances Python, versions figées |
| `AGENTS.md` | Consignes pour les assistants de code |
| `data/` | Données téléchargées et produites, recréées par les notebooks ; non versionnées sauf exceptions ci-dessous |

## Environnements Python

| Environnement | Modules | Remarque |
|---|---|---|
| `.venv` à la racine | `citiz/`, `lakehouse/`, `population/`, `regional-data` 08 et 09 | pandas 3.0 ; installer `citiz/requirements.txt`, `lakehouse/requirements.txt` et `population/requirements.txt` |
| `ign-osm/.venv` (noyau « Python (IGN / OSM) ») | `ign-osm/`, `regional-data` 01 à 07 | PyOsmium, NetworkX |
| à part | `dashboard/` | exige `pandas<3`, incompatible avec le `.venv` racine |

## Conventions communes

- Documentation en français ; code, noms de fichiers, variables et commentaires en anglais.
- Explications en Markdown avant chaque cellule de code.
- Notebooks exécutés dans l'ordre depuis un noyau neuf avant d'être poussés ; les README décrivent les résultats obtenus, pas les résultats prévus.
- `station_uid` (`source:station_id`) est la clé de jointure entre modules.
- Une donnée manquante n'est jamais remplacée par zéro.
- Les données ne sont pas versionnées, sauf la référence partagée de `output/`, les extraits INSEE de `population/reference/` et `regional-data/data/` (hors GeoPackage).

## Référence partagée : `output/`

Trois fichiers Citiz, instantané du 19/10/2026, lus par les autres modules. Voir [`output/README.md`](output/README.md). Ils ne sont remplacés qu'après accord de l'équipe, car `regional-data/` vérifie leur empreinte.

## Livrables attendus

- [ ] Code du projet sur le dépôt Git
- [ ] Slides de la présentation, sur le même dépôt
- [x] Liste des sources de données : [`SOURCES.md`](SOURCES.md)
