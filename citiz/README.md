# Citiz : exploration des données d'autopartage

## Objectif

Établir quelles données Citiz sont **exploitables** pour le hackathon, et lesquelles ne le sont pas.

Citiz publie ses stations au format **GBFS** sur le Point d'accès national (transport.data.gouv.fr), avec un flux par réseau régional. Ce module récupère ces flux, mesure leur qualité colonne par colonne, cartographie les stations et prépare des tables propres pour le Lakehouse Microsoft Fabric.

Statut : **exploration**. Les conclusions ci-dessous portent sur les données réellement téléchargées, pas sur des données prévues.

## Ouvrir les notebooks

Dans VS Code, choisir le noyau Python de l'environnement `.venv` situé à la racine du dépôt. Pour le recréer sur une autre machine, depuis la racine :

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r citiz/requirements.txt
```

Exécuter les notebooks dans l'ordre. Après une modification, **redémarrer le noyau puis tout exécuter** pour vérifier qu'aucune variable d'une ancienne exécution n'est nécessaire.

1. [Extraire les stations Citiz](notebooks/01_citiz_gbfs_extraction.ipynb) : interroge l'API du Point d'accès national, lit les 15 flux GBFS, nettoie, dédoublonne et écrit 4 CSV bruts. Chaque exécution **ajoute** un instantané à l'historique des disponibilités.
2. [Mesurer la qualité des données](notebooks/02_citiz_data_quality.ipynb) : taux de remplissage, couverture géographique, pseudo-stations, fraîcheur des statuts, flotte, verdict par colonne.
3. [Cartographier les stations](notebooks/03_citiz_stations_map.ipynb) : carte statique, carte interactive, rattachement de chaque station à son département et sa région.
4. [Préparer le Lakehouse](notebooks/04_lakehouse_preparation.ipynb) : 8 tables typées et contrôlées. **Préparatoire** : exécuté en local, pas encore dans Fabric.

Le notebook 01 nécessite Internet. Les suivants n'utilisent que les fichiers locaux, sauf au premier téléchargement des contours.

## Fichiers

Chemins relatifs à `citiz/`. Le dossier `data/` est exclu de Git : il est recréé en exécutant les notebooks.

| Fichier | Produit par | Rôle |
|---|---|---|
| `data/raw/gbfs/citiz_flux.csv` | 01 | Un flux GBFS régional par ligne : URL, version, licence |
| `data/raw/gbfs/citiz_stations.csv` | 01 | Une station par ligne : position, adresse, capacité |
| `data/raw/gbfs/citiz_station_status.csv` | 01 | Disponibilités, une ligne par station et par instantané (historique) |
| `data/raw/gbfs/citiz_vehicle_types.csv` | 01 | Modèles de véhicules par réseau |
| `data/raw/boundaries/*.geojson` | 03 | Contours simplifiés des régions et départements |
| `data/processed/data_quality_report.csv` | 02 | Verdict par colonne, avec justification |
| `data/processed/citiz_stations_map.png` / `.html` | 03 | Carte statique (slides) / interactive (démo) |
| `data/processed/citiz_stations_by_department.png` | 03 | Nombre de stations par département |
| `data/processed/citiz_stations_geo.csv` | 03 | Stations avec département et région |
| `data/lakehouse/Files/...` | 04 | Miroir local du Lakehouse : CSV bruts, Parquet propres, dictionnaire |

### Référence partagée avec l'équipe

`output/citiz_stations_geo.csv` et `output/citiz_flux.csv`, **à la racine du dépôt**, sont l'instantané du 19/10/2026 utilisé par `regional-data/`, qui vérifie leur empreinte SHA-256. Ils ne sont pas remplacés automatiquement : la dernière cellule du notebook 03 les met à jour seulement si `PUBLISH_TO_TEAM = True`, après accord de l'équipe.

## Résultats de l'exploration

Exécution du 20/10/2026, 3 instantanés de disponibilité (19/10 et 20/10).

### Couverture

- **1 615 stations**, réparties sur **15 réseaux régionaux**, toutes en GBFS 3.0. La référence partagée du 19/10 en compte 1 614.
- **Aucune station en Outre-mer (DROM)**, alors que le sujet les inclut.
- **47 départements** ont au moins une station, **49 n'en ont aucune**.
- Régions les plus équipées : Auvergne-Rhône-Alpes (613), Grand Est (291), Nouvelle-Aquitaine (160), Occitanie (142).
- Départements les plus équipés : Isère (219), Rhône (208), Bas-Rhin (205), Haute-Garonne (122).
- Aucune station n'apparaît dans deux flux : les flux AURA et Métropole de Lyon ne se recoupent pas.

### Ce qui est exploitable

| Donnée | Pourquoi |
|---|---|
| Position (`lat`, `lon`), nom, `station_uid` | Toujours renseignés ; `station_uid` est unique et sert de clé de jointure |
| `capacity` | Toujours renseignée, après exclusion des pseudo-stations internes |
| `is_virtual_station` | Distingue 57 zones sans place physique |
| Motorisation (`propulsion_type`) | Renseignée pour les 337 modèles : 182 thermiques, 87 hybrides, 58 électriques, 10 vélos cargo / autres |
| Voitures disponibles par modèle (`vehicle_types_available`) | Renseigné pour 93 % des statuts |

### Ce qui ne l'est pas, ou pas encore

| Donnée | Constat | Conséquence |
|---|---|---|
| `last_reported` | **95 %** des statuts ont plus de 30 jours, **57 %** plus d'un an | Le flux ne reflète pas les mouvements réels des voitures : **pas de mesure de fréquentation fiable à partir de GBFS seul** |
| Historique de disponibilité | 3 instantanés seulement | À accumuler (planification), puis à valider au vu du point précédent |
| `address` | Absente pour 33 % des stations | À compléter par géocodage inverse si nécessaire |
| `num_docks_available`, `is_renting` | Constantes (0, vrai) | Aucune information |
| `max_range_meters` | 0 pour 96 % des modèles | Autonomie inconnue |
| `short_name`, `post_code`, `city`, `vehicle_types_capacity`, `num_vehicles_disabled`, `rider_capacity` | Vides dans tous les flux | Inutilisables |

### Points d'attention

- **3 pseudo-stations internes** à exclure des analyses : « Véhicules hors-circuit » (103 places), « DEMOBOX (Réservé Citiz) » (100 places), « ZZ_SXB LIVRAISON NE PAS RESERVER ». Elles sont repérées par leur nom dans le notebook 02 et restent dans les fichiers bruts.
- **23 stations** ont une capacité de 0.
- La fréquentation devra être estimée autrement : demander des données d'usage à Citiz, ou construire un indicateur de potentiel (population, densité, desserte) plutôt qu'un usage observé.
- Les codes de département (`01`, `2A`) doivent être lus en texte : sans `dtype=str`, pandas les convertit en nombres.

## Lakehouse Fabric (préparatoire)

Le notebook 04 produit 8 tables, décrites dans [le dictionnaire](DATA_DICTIONARY.md) : `geo_region`, `geo_department`, `citiz_network`, `citiz_station`, `citiz_vehicle_type`, `citiz_station_status`, `citiz_station_status_vehicle`, `cost_parameter`. Chaque table a une clé primaire vérifiée, et les liens entre tables sont contrôlés (aucun orphelin).

Pour charger dans Fabric :

1. Créer un Lakehouse dans l'espace de travail de l'équipe.
2. Déposer le contenu de `data/lakehouse/Files/` dans `Files/` du Lakehouse.
3. Importer le notebook 04, lui attacher le Lakehouse comme Lakehouse par défaut, puis l'exécuter : les tables apparaissent dans `Tables/`.

La partie Spark n'a pas encore été testée dans Fabric.

## Coûts d'une station (pistes)

Aucune grille tarifaire publique n'a été trouvée. Chiffres tirés de la convention type Genevois français / Citiz Alpes-Loire (2021), repris dans la table `cost_parameter` :

| Paramètre | Valeur | Statut |
|---|---|---|
| Boîtier télématique | 4 000 € HT par voiture | sourcé |
| Frais fixes d'exploitation | 250 € par mois et par voiture | sourcé |
| Recette | 0,19 € par km | sourcé |
| Taille minimale d'une station | 2 voitures | sourcé |
| Seuil de rentabilité | ≈ 1 300 km par mois et par voiture | calculé |
| Prix d'achat d'une voiture, aménagement d'une station | — | hypothèses à demander à Citiz |

## Sources repérées, pas encore exploitées

Repérées dans le catalogue du Point d'accès national pour la zone de Lyon, non téléchargées :

- Vélo'v (vélos en libre-service, GBFS) ;
- Dott (vélos et trottinettes en libre accès, GBFS) ;
- Leo&Go (autopartage concurrent, GBFS) ;
- TCL (bus, tram, métro, GTFS).

Voir [les sources](SOURCES.md).
