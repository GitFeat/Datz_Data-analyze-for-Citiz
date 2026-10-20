# Sources et traçabilité

| Source | Version utilisée | Rôle |
|---|---|---|
| [INSEE, Filosofi 2021, données carroyées à 200 m](https://www.insee.fr/fr/statistiques/8735162) | Édition 2021, fichier métropole `carreaux_200m_met.csv` | Population et profil socio-démographique par carreau |
| [INSEE, projections de population 2021-2070 par département et région (Omphale 2022)](https://www.insee.fr/fr/statistiques/6652134) | Fichiers datés du 7 décembre 2022, 11 scénarios | Évolution de la population et de sa structure par âge |

## Filtrage appliqué

Les fichiers de `reference/` sont des **extraits** des fichiers INSEE, pas les fichiers complets :

- Filosofi : lignes dont au moins une commune appartient à Auvergne-Rhône-Alpes (départements 01, 03, 07, 15, 26, 38, 42, 43, 63, 69, 73, 74), 18 colonnes conservées sur 34. Le fichier métropole fait 468 Mo, l'extrait 30 Mo.
- Projections : lignes des 12 départements (onglets `_DEP`) et de la région, code `84` (onglets `_REG`) ; onglet `Documentation` et colonnes 2018 à 2020 de `Population_*` supprimés.

Les fichiers INSEE complets ne sont pas versionnés. Pour refaire l'extraction, les télécharger depuis les liens ci-dessus.

## Limites

- Les projections existent par département, pas par carreau. Les appliquer aux carreaux suppose que tout un département évolue de la même façon.
- Les tranches d'âge de Filosofi (10, irrégulières) ne coïncident pas avec celles des projections (tranches de 5 ans, disponibles seulement en 2018 et 2070).
- Les valeurs de Filosofi sont ajustées par l'INSEE pour la confidentialité dans les carreaux peu peuplés (`i_est_200`).
- Filosofi couvre environ 7,7 millions d'habitants pour la région, contre environ 8,1 millions selon les projections 2021 : le fichier ne couvre pas toute la population.
