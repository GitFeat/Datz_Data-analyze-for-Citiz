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
| [`citiz/`](citiz/README.md) | Stations Citiz (GBFS) : extraction, qualité des données, cartes, préparation Lakehouse Fabric | exploration terminée pour les flux Citiz |
| [`ign-osm/`](ign-osm/README.md) | Parcours d'apprentissage : contours IGN, données OpenStreetMap, réseau piéton, 5 min de marche autour d'un point | parcours pédagogique, exemples sur Clermont-Ferrand |
| [`regional-data/`](regional-data/README.md) | Livrable régional Auvergne-Rhône-Alpes : équipements OSM et distances à pied autour de chaque station Citiz | table finale disponible (`data/release/`) |
| [`dashboard/`](dashboard/README.md) | Exploration interactive des tables CSV (Streamlit + PyGWalker) | outil d'exploration |

### Principaux constats

- **1 615 stations Citiz** sur 15 réseaux régionaux, **aucune en Outre-mer**. Auvergne-Rhône-Alpes est la région la plus équipée (613 stations).
- Les flux GBFS Citiz décrivent bien **où** sont les stations (position, capacité, motorisation des voitures), mais **pas leur usage** : la date de dernière mise à jour des statuts a plus d'un an pour 57 % des stations. Détails dans [`citiz/`](citiz/README.md#résultats-de-lexploration).
- La population d'Auvergne-Rhône-Alpes est disponible par carreau de 200 m (312 143 carreaux, 7,7 millions d'habitants) avec 11 scénarios de projection jusqu'en 2070 ([`population/`](population/README.md)).
- Le réseau piéton OSM permet de calculer des distances à pied réelles autour des stations ([`regional-data/`](regional-data/README.md)).

### Données pas encore intégrées

Arrêts de transport en commun (GTFS), autres services partagés (Vélo'v, Dott, Leo&Go). La population fine et les projections sont chargées mais pas encore croisées avec les stations ([`population/`](population/README.md)).

## Périmètre géographique

- **Données régionales** : Auvergne-Rhône-Alpes, la région où Citiz a le plus de stations ([`regional-data/`](regional-data/README.md)).
- **Zone de démonstration proposée** : le département du Rhône (Métropole de Lyon). C'est le seul territoire où tous les types de transport demandés sont publiés en open data (TCL, Vélo'v, Dott), ainsi qu'un autopartage concurrent (Leo&Go). Choix à valider en équipe.
- **Outre-mer** : Citiz n'y est pas présent ; à traiter dans l'objectif 3 (où et comment s'y implanter).

## Organisation du dépôt

```
.
├── sujet/            énoncé du hackathon
├── citiz/            module stations Citiz
├── ign-osm/          module d'apprentissage IGN / OpenStreetMap
├── regional-data/    livrable régional Auvergne-Rhône-Alpes
├── population/       population INSEE Auvergne-Rhône-Alpes (carreaux 200 m, projections)
├── dashboard/        explorateur interactif
└── output/           référence Citiz partagée entre les modules (versionnée)
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
| `data/` | Données téléchargées et produites, **non versionnées**, recréées par les notebooks |

## Conventions communes

- Documentation en français ; code, noms de fichiers, variables et commentaires en anglais.
- Explications en Markdown avant chaque cellule de code.
- Notebooks exécutés dans l'ordre depuis un noyau neuf avant d'être poussés ; les README décrivent les résultats obtenus, pas les résultats prévus.
- `station_uid` (`source:station_id`) est la clé de jointure entre modules.
- Une donnée manquante n'est jamais remplacée par zéro.
- Les données ne sont pas versionnées, sauf la référence partagée de `output/`.

## Référence partagée : `output/`

Trois fichiers Citiz, instantané du 19/10/2026, lus par les autres modules. Voir [`output/README.md`](output/README.md). Ils ne sont remplacés qu'après accord de l'équipe, car `regional-data/` vérifie leur empreinte.

## Livrables attendus

- [ ] Code du projet sur le dépôt Git
- [ ] Slides de la présentation, sur le même dépôt
- [ ] Liste des sources de données (voir les `SOURCES.md` de chaque module)
