# Contexte de reprise : pipeline Microsoft Fabric (Bronze → Silver → Gold)

Document de passation rédigé le 20/10/2026 à la fin d'une session avec Claude Code. Il résume les décisions, l'état exact de Fabric et la suite du travail. **Reprendre au point « Prochaine étape : le Gold ».**

---

## 1. Le projet en deux phrases

Hackathon Epitech MSc 1 avec Citiz (autopartage) et Microsoft. Question posée : *qui a réellement accès à une option de mobilité près de chez lui, et où faut-il en ajouter ?* (sujet : `sujet/hackathon_mobility-project.pdf`, vue d'ensemble : `README.md`).

Les trois objectifs du sujet :
1. **Cartographier l'accès** : nombre d'options de mobilité à 5 min à pied, rapporté au nombre d'habitants, par zone.
2. **Montrer qui est concerné** : stations et arrêts par type, avec la population desservie par chacun.
3. **Proposer où s'implanter** (cœur du projet) : valeur d'un emplacement candidat, coût par type d'équipement, classement sous contrainte de budget.

Zone d'étude retenue dans Fabric : **la Métropole de Lyon** (toutes les données de `Files/Raw/` sont centrées sur Lyon).

## 2. Décisions de l'utilisateur, à respecter

- **Tout se fait dans Fabric**, avec des **Dataflow Gen2** (Power Query), orchestrés plus tard par une **Data pipeline**. L'utilisateur a refusé deux fois un module local ou des notebooks PySpark : **ne rien créer dans le dépôt pour le pipeline**, sauf demande explicite.
- Architecture **medallion** demandée par un intervenant : Bronze (brut) → Silver (nettoyé, fusionné) → Gold (prêt pour Power BI).
- **Un seul Lakehouse**, tables dans le schéma `dbo` avec un préfixe de couche (`bronze_`, `silver_`, `gold_`). Le Lakehouse a les schémas activés, mais l'écriture d'un dataflow dans un autre schéma que `dbo` n'a pas été testée.
- L'utilisateur apprend Fabric : **expliquer en français, point par point**. Son interface Fabric est **en français**. Il préfère que l'assistant construise les éléments, puis il les ouvre pour voir comment ils sont faits.
- **Demander avant toute modification** dans le workspace Fabric. Ne pas supprimer d'élément créé par l'utilisateur.
- Conventions du dépôt : documentation en français ; code, noms de colonnes et identifiants en anglais. **Une donnée manquante n'est jamais remplacée par 0.** `station_uid` = `system:station_id` sert de clé entre les tables.

## 3. Ressources Fabric

Tenant Epitech (`901cb4ca-b862-4029-9306-e5cd0f6d9f86`), compte de l'utilisateur.

| Élément | Nom | ID |
|---|---|---|
| Workspace | `Datz Workspace` | `a9b6d3cb-8956-48d9-8be1-3fe5f9054b9c` |
| Lakehouse | `mobility_Lakehouse` | `73b602ba-9492-43ad-9a88-6d0258014249` |
| SQL analytics endpoint | `mobility_Lakehouse` | `d8989ba6-dbbb-490c-b253-fea513f1226f` |
| Connexion Lakehouse (OAuth2, créée à la main dans le portail) | `lh_mobility` | `f02a07a5-e0ff-47e2-b26e-fe70dce56207`, ClusterId `067dd309-283f-4053-83a2-512a95dd1b31` |
| Dataflow Gen2 Bronze | `df_01_bronze` | `110bd1ca-7b32-49ac-bf02-a67ea62eb849` |
| Dataflow Gen2 Silver | `df_02_silver` | `f5bee9b9-e084-4013-a986-393f036751d2` |
| Notebook vide (créé par l'utilisateur, inutilisé) | `01_bronze` | `52d58743-d41a-4493-93c0-afcf2d641faa` |
| Éléments de staging créés automatiquement par Fabric | `StagingLakehouseForDataflows_*`, `StagingWarehouseForDataflows_*` | **ne pas supprimer** |

Liens : workspace `https://app.fabric.microsoft.com/groups/a9b6d3cb-8956-48d9-8be1-3fe5f9054b9c`.

### Accès programmatique utilisé pendant la session
- **Azure CLI** connectée au tenant Epitech (`az login --allow-no-subscriptions`). L'API Fabric s'appelle avec `az rest --resource https://api.fabric.microsoft.com`. Les fichiers OneLake se lisent avec un jeton `https://storage.azure.com` sur `https://onelake.dfs.fabric.microsoft.com/<workspaceId>/<lakehouseId>/Files/...`.
- **Plugin Claude Code `fabric-skills`** (dépôt `microsoft/skills-for-fabric`) : le serveur MCP `fabric-sqlendpoint` exécute du T-SQL en **lecture seule** sur le SQL endpoint, et `FabricIQ` fonctionne. Le serveur `powerbi-modeling-mcp` renvoie `FeatureNotAvailable` (403), probablement parce que la fonctionnalité est désactivée dans le tenant Epitech.
- Les dataflows ont été créés par l'API REST : `POST /v1/workspaces/{ws}/dataflows`, puis `updateDefinition` avec les trois parties `mashup.pq`, `queryMetadata.json` et `.platform`. Les aperçus passaient par `executeQuery` et l'exécution par `jobs/instances?jobType=Refresh` avec `executeOption: ApplyChangesIfNeeded`. **Le code M fait foi dans Fabric** : relire une définition avec `POST .../dataflows/{id}/getDefinition`. La réponse est asynchrone (202) : suivre l'en-tête `Location`, puis lire `/result`.
- Le SQL endpoint est en lecture seule : **l'assistant ne peut pas supprimer de tables**, c'est l'utilisateur qui le fait depuis l'interface du Lakehouse.

## 4. Pièges Fabric découverts et confirmés par test

1. **Le staging des Dataflow Gen2 tronque les textes à 8 000 caractères à l'écriture.** Test : un texte de 20 000 caractères est écrit à 8 000 avec staging et en entier sans staging. Dans `queryMetadata.json`, toutes les requêtes avec destination ont donc `loadEnabled: false` (staging désactivé). Les requêtes `*_DataDestination` ont `loadEnabled: false` et `isHidden: true`. **Ne pas réactiver le staging**, sinon les contours WKT seront coupés.
2. **`Lakehouse.Contents(null)` lit les tables via le SQL endpoint, qui tronque aussi à 8 000 caractères.** Pour lire une table Lakehouse avec ses textes longs, utiliser `Lakehouse.Contents([EnableFolding = false])`.
3. Dans un Lakehouse avec schémas, les fichiers Delta sont sous `Tables/dbo/<table>/`.
4. Dans `Lakehouse.Contents`, `Files` est **hiérarchique** : chaque dossier est une ligne dont la colonne `Content` contient ses enfants.
5. Les nombres des sources utilisent le point décimal : toujours typer avec la culture `"en-US"`.
6. Une destination Lakehouse refuse les colonnes de type `any` : toutes les colonnes doivent être typées.

## 5. Données déposées par l'équipe : `Files/Raw/`

| Dossier | Fichiers | Remarques |
|---|---|---|
| `citiz/` | `station_information.csv`, `vehicle_status.csv`, `vehicle_types.csv`, `system_pricing_plans.csv` | GBFS 3.0, réseau `citiz_metropole_lyon` uniquement. Textes localisés au format `[{"text": "...", "language": "fr"}]` |
| `concurence/getaround/` | `vehicle_status.csv` | Getaround Lyon, 289 voitures |
| `concurence/leodango/` | `vehicle_status.csv` | ⚠️ **copie identique du fichier Getaround** (même MD5, `system = getaround_lyon`). Non chargé, en attente du vrai fichier Leo&Go |
| `geography/` | IGN Admin Express : arrondissements, communes, EPCI ; contours IRIS | ⚠️ contours WKT écrits **(lat lon)** au lieu de (lon lat) |
| `lyon_aglo/` | `bornes_irve.csv`, `parkings.csv`, `quartiers_prioritaires_2024_2030.csv`, `zfe_perimetre.csv` | Contours dans le bon ordre (lon lat) |
| `population/` | `insee_filosofi2021_carreaux_200m_lyon.csv` | 8 032 carreaux, sans coordonnées GPS : la position est dans l'identifiant, en EPSG:3035 |
| `public_transit/` | `stops.csv`, `sncf_gares_de_voyageurs_lyon.csv`, `sncf_frequentation_gares_lyon.csv` | ⚠️ `stops.csv` contient des **arrêts SNCF/TER**, pas les arrêts TCL (bus, tram, métro) |

## 6. Bronze : fait et vérifié

`df_01_bronze` contient une fonction `ReadRawCsv(segments, delimiter)` et une requête par fichier. Règles : **un fichier = une table**, toutes les colonnes en texte, colonnes ajoutées `_ingested_at` (UTC) et `_source_file`, mode Remplacer, aucun nettoyage. Pour chaque table, le nombre de lignes est identique à celui du CSV.

| Table | Lignes | | Table | Lignes |
|---|---|---|---|---|
| `bronze_citiz_station_information` | 200 | | `bronze_lyon_bornes_irve` | 2 558 |
| `bronze_citiz_vehicle_status` | 460 | | `bronze_lyon_parkings` | 1 047 |
| `bronze_citiz_vehicle_types` | 21 | | `bronze_lyon_qpv` | 71 |
| `bronze_citiz_system_pricing_plans` | 10 | | `bronze_lyon_zfe` | 1 |
| `bronze_concurrence_getaround_vehicle_status` | 289 | | `bronze_population_filosofi_200m` | 8 032 |
| `bronze_geography_arrondissements` | 9 | | `bronze_transit_stops` | 121 |
| `bronze_geography_communes` | 58 | | `bronze_transit_sncf_gares` | 35 |
| `bronze_geography_epci` | 1 | | `bronze_transit_sncf_frequentation` | 35 |
| `bronze_geography_iris` | 512 | | | |

Après la désactivation du staging, le Bronze a été relancé : les contours sont complets (jusqu'à 237 394 caractères).

## 7. Silver : fait et vérifié

`df_02_silver` lit le Bronze avec 6 fonctions communes :
- `LoadBronze(name)` : lecture avec `EnableFolding = false`, suppression des colonnes techniques, texte vide transformé en `null`.
- `GbfsText` : extrait le texte d'un JSON localisé, en français d'abord.
- `ToUtc` : convertit une date ISO avec décalage horaire en date UTC.
- `PointCoordinate(wkt, 0|1)` : lit la longitude ou la latitude d'un `POINT (lon lat)`.
- `SwapWkt` : inverse chaque paire de coordonnées d'un WKT.
- `Laea3035ToWgs84(E, N)` : projection inverse LAEA EPSG:3035 → WGS84. Formule vérifiée à environ 10⁻⁶ degré près.

| Table | Clé | Lignes | Traitements principaux |
|---|---|---|---|
| `silver_citiz_station` | `station_uid` | 200 | Nom extrait du JSON, lat/lon, `capacity`, `is_virtual_station`, `gbfs_last_updated_utc` |
| `silver_citiz_vehicle_type` | `vehicle_type_uid` | 21 | Nom, marque et modèle extraits ; `max_range_m` : 0 transformé en `null` (17 sur 21, valeur non renseignée dans GBFS) ; `default_pricing_plan_uid` |
| `silver_citiz_vehicle` | `vehicle_uid` | 460 | Clés `station_uid`, `home_station_uid` et `vehicle_type_uid` ; carburant, autonomie, réservé ou indisponible, `last_reported_utc`. 1 voiture a une latitude > 46,2, donc hors de Lyon, à filtrer en Gold |
| `silver_citiz_pricing_plan` | `pricing_plan_uid` | 10 | Prix fixe, tarif de la 1re tranche au km et au temps, JSON d'origine conservé |
| `silver_getaround_vehicle` | `vehicle_uid` | 289 | lat/lon, autonomie, `rental_url` |
| `silver_irve_station` | `irve_station_id` | 653 | Regroupement des points de charge par station : nombre de points, puissance maximale, gratuité, date de mise en service, lat/lon |
| `silver_parking` | `parking_id` (= `gid`) | 1 047 | `idparking` n'est pas unique, il est conservé dans `parking_code` ; capacités en entiers ; lat/lon |
| `silver_qpv` | `qpv_code` | 71 | Codes INSEE extraits du JSON, contour WKT |
| `silver_zfe` | `zfe_id` | 1 | Dates, vignettes Crit'Air minimales par type de véhicule, contour |
| `silver_transit_stop` | `stop_id` | 71 | Uniquement les points d'arrêt (`location_type = 0`) |
| `silver_sncf_station` | `uic_code` | 35 | lat/lon issus de `position_geographique` ; **fusion** avec la fréquentation 2024, 2023 et 2019 sur le code UIC (35 sur 35) |
| `silver_geo_commune` | `code_insee` | 58 | Contour remis en (lon lat), population, superficie (ha), codes EPCI |
| `silver_geo_arrondissement` | `code_insee` | 9 | Idem, plus `parent_code_insee` |
| `silver_geo_epci` | `epci_siren_code` | 1 | Contour de la Métropole |
| `silver_geo_iris` | `code_iris` | 512 | Contour remis en (lon lat), `code_insee` |
| `silver_population_grid` | `idcar_200m` | 8 032 | Centre du carreau en lat/lon, `main_code_insee`, `is_estimated`, toutes les variables Filosofi, `ind_65p`, `avg_living_standard_eur`. Total : 1 303 499 habitants, dont 220 850 de 65 ans et plus |

Contrôles SQL réussis : clés uniques sur les 16 tables ; aucune voiture sans station ou sans modèle connu, aucun modèle sans tarif, aucun IRIS sans commune ou arrondissement ; contours complets dans les fichiers Delta.

## 8. Ménage restant, côté utilisateur

- Supprimer les tables de test `zz_test_longtext_staging` et `zz_test_longtext_nostaging`.
- Supprimer les 6 tables de l'ancien Bronze, dont les sources n'existent plus : `bronze_citiz_station`, `bronze_citiz_station_status`, `bronze_citiz_vehicle_type`, `bronze_population_grid`, `bronze_station_osm_features`, `bronze_velov_station`. Les tables `citiz_aura_clean` et `filosofi_carreaux_200m_aura`, chargées à la main avant la session, ont également disparu de la liste.
- Déposer le vrai fichier Leo&Go et les arrêts TCL (GTFS du réseau TCL, transport.data.gouv.fr). Il faudra ensuite ajouter les requêtes correspondantes en Bronze et en Silver.

## 9. Prochaine étape : le Gold (point de reprise)

Objectif : un Dataflow Gen2 `df_03_gold` qui lit les tables `silver_*` avec `Lakehouse.Contents([EnableFolding = false])`, staging désactivé, et écrit des tables `gold_*` pensées pour Power BI (schéma en étoile). Proposition encore **non validée par l'utilisateur**, à lui présenter avant de construire :

- **Dimensions**
  - `gold_dim_mobility_point` : une ligne par offre de mobilité, issue de l'union des stations Citiz, voitures Getaround, gares SNCF, arrêts, stations IRVE et parkings avec places d'autopartage. Colonnes : type, opérateur, lat/lon, capacité, commune.
  - `gold_dim_commune`, `gold_dim_iris` : avec population et contour.
- **Faits et indicateurs**
  - Objectif 1 : par carreau ou par IRIS, population et nombre d'options à environ 400 m (5 min à pied).
  - Objectif 2 : population à environ 400 m de chaque point de mobilité.
  - Objectif 3 : critères d'implantation (QPV, ZFE, densité, niveau de vie, offre existante, coûts).
- **Limite connue** : Power Query ne fait pas de calcul géographique (point dans un polygone). Il faut donc soit une **approximation à vol d'oiseau** (distance haversine calculée à partir de lat/lon, avec un pré-filtrage par cellule de grille pour limiter les combinaisons), soit, si l'utilisateur l'accepte, un notebook pour ces seuls calculs. Le module local `regional-data/` calcule de vraies distances à pied (réseau OSM), mais uniquement autour des stations Citiz d'Auvergne-Rhône-Alpes.
- Coûts d'une station Citiz déjà sourcés (convention Genevois français / Citiz Alpes-Loire, 2021) : boîtier télématique 4 000 € HT par voiture ; frais fixes 250 € par mois et par voiture ; recette 0,19 €/km ; 2 voitures minimum par station ; rentabilité vers 1 300 km par mois et par voiture. Ces chiffres sont détaillés dans `README.md` et `citiz/README.md`.

Ensuite :
1. Data pipeline `pl_mobility` : `df_01_bronze` → `df_02_silver` → `df_03_gold`, chaque étape démarrant si la précédente a réussi, avec une planification.
2. Modèle sémantique Power BI sur les seules tables `gold_*`, avec relations et mesures DAX, puis les rapports et les cartes de la soutenance.
