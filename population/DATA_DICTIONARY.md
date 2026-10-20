# Dictionnaire des données

## `reference/filosofi_2021_aura/carreaux_200m_aura.csv`

Un carreau de 200 m × 200 m par ligne. 312 143 lignes. Les valeurs sont des **totaux par carreau**, pas des moyennes.

| Colonne | Contenu |
|---|---|
| `idcar_200m` | Identifiant du carreau, de la forme `CRS3035RES200mN<nord>E<est>`. Contient les coordonnées du **coin sud-ouest**, en mètres (EPSG:3035) |
| `lon`, `lat` | **Centre du carreau** en degrés (WGS84, EPSG:4326), arrondi à 6 décimales. Colonnes ajoutées : absentes du fichier INSEE d'origine |
| `lcog_geo` | Code(s) commune. Plusieurs codes séparés par une virgule si le carreau chevauche plusieurs communes (`84120,26135`). Les 2 premiers caractères donnent le département |
| `i_est_200` | Indicateur de valeurs ajustées par l'INSEE pour la confidentialité |
| `ind` | Nombre d'habitants |
| `men` | Nombre de ménages |
| `men_pauv` | Ménages pauvres |
| `men_coll` | Ménages en logement collectif |
| `ind_snv` | Somme des niveaux de vie des habitants, en euros. Niveau de vie moyen = `ind_snv / ind` |
| `ind_0_3`, `ind_4_5`, `ind_6_10`, `ind_11_17`, `ind_18_24`, `ind_25_39`, `ind_40_54`, `ind_55_64`, `ind_65_79`, `ind_80p` | Habitants par tranche d'âge |

Les décimales (0,6 ménage…) viennent des ajustements de confidentialité de l'INSEE.

**Calcul de `lon` et `lat`** : 100 m ajoutés au nord et à l'est du coin sud-ouest donné par l'identifiant, puis conversion de EPSG:3035 vers EPSG:4326 (voir le notebook 01, qui refait ce calcul). Le code EPSG est lu dans l'identifiant.

## `reference/projections_omphale_aura/*.xlsx`

Un fichier par scénario : `scenario_central`, `population_basse`, `population_haute`, `population_jeune`, `population_agee`, `fecondite_basse`, `fecondite_haute`, `migrations_basses`, `migrations_hautes`, `esperance_de_vie_basse`, `esperance_de_vie_haute`.

L'en-tête de chaque tableau est à la **ligne 6**. Les codes `DEP` sont des textes (`01`) ; la région a le code `84`.

| Onglet | Contenu |
|---|---|
| `Population_DEP`, `Population_REG` | Population en **milliers d'habitants**, une colonne par année (`POP_2021` … `POP_2070`) |
| `Structure_Age_DEP`, `Structure_Age_REG` | Population, âge moyen et part en % de chaque tranche de 5 ans, en 2018 et en 2070 (`[0,5)_2018`, `AGE_MOY_2070`…) |
| `TCAM_contrib_DEP`, `TCAM_contrib_REG` | Taux de croissance annuel moyen 2018-2070 (`TCAM_2018_2070`), avec la contribution du solde migratoire (`Contrib_SM`) et du solde naturel (`Contrib_SN`), en points de % par an |

Dans les onglets `TCAM_contrib_DEP`, les colonnes de code et de libellé s'appellent `REG` et `LIBREG` bien qu'elles contiennent des départements : c'est le nommage de l'INSEE.
