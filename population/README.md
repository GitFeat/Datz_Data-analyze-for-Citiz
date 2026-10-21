# Population : carreaux INSEE et projections

## Objectif

Fournir la population de la région Auvergne-Rhône-Alpes à une échelle fine, pour compter les habitants desservis autour d'une station ou d'un arrêt (objectifs 1 et 2 du sujet), et anticiper son évolution (objectif 3).

Statut : **exploration**. Les données sont chargées, converties en coordonnées GPS et visualisées. Le lien avec les stations et le calcul de la population desservie ne sont pas encore faits.

## Ouvrir les notebooks

Depuis la racine du dépôt :

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r population/requirements.txt
```

Dans VS Code, choisir le noyau Python de ce `.venv`. Les deux notebooks sont indépendants et n'utilisent que les fichiers de `reference/`, sans Internet. Ils retrouvent ces fichiers depuis la racine du dépôt : on peut les lancer depuis n'importe quel dossier.

1. [Carreaux Filosofi 200 m](notebooks/01_filosofi_population_grid.ipynb) : charge le CSV avec DuckDB, lit la latitude / longitude du centre de chaque carreau, ajoute le département, le niveau de vie moyen et la part des 65 ans et plus, puis trace distributions, cartes de densité, structure par âge et niveau de vie.
2. [Projections Omphale](notebooks/02_population_projections.ipynb) : évolution de la population par département (2021-2070), comparaison des 11 scénarios, structure par âge 2018 contre 2070, part des 65 ans et plus, moteurs de la croissance.

## Fichiers

Contrairement aux autres modules, les données sont **versionnées** : ce sont des extraits manuels de fichiers INSEE (30 Mo en tout) qu'aucun notebook ne peut recréer. Voir [`SOURCES.md`](SOURCES.md) pour le filtrage et [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) pour les colonnes.

| Fichier | Contenu |
|---|---|
| `reference/filosofi_2021_aura/carreaux_200m_aura.csv` | 312 143 carreaux de 200 m, environ 7,7 millions d'habitants |
| `reference/projections_omphale_aura/*.xlsx` | 11 scénarios de projection 2021-2070, 12 départements et la région |

## Résultats

- 312 143 carreaux, en moyenne 24,7 habitants par carreau.
- Scénario central : la région passe de 8,10 millions d'habitants en 2021 à 8,67 millions en 2050, puis 8,65 millions en 2070.
- Écart des scénarios en 2050 : de -7,8 % (population basse) à +8,1 % (population haute) par rapport au scénario central.
- L'Allier, le Cantal et la Haute-Loire perdent des habitants ; le Rhône, l'Ain et la Haute-Savoie en gagnent.
- La part des 65 ans et plus, de 17 à 28 % selon le département en 2018, atteint 23 à 38 % en 2070.

## Limites

- Le lien entre les carreaux et les projections n'est pas construit. Il passerait par le département (2 premiers caractères de `lcog_geo`), avec une évolution identique pour tous les carreaux d'un département.
- Les carreaux à cheval sur plusieurs communes ont plusieurs codes dans `lcog_geo` ; certains portent le code d'un département voisin.
- Le centre du carreau représente toute sa population : approximation d'environ 100 m.
- Notebooks testés avec Python 3.9, pandas 2.3, DuckDB 1.4 et pyproj 3.6, puis le 20/10/2026 avec le `.venv` racine (Python 3.12, pandas 3.0, DuckDB 1.5).
- Les carreaux sont chargés dans le Lakehouse (table `population_grid_aura`, voir [`lakehouse/`](../lakehouse/README.md)), avec leur contour et leur département ; ils ne sont pas encore croisés avec les stations.
