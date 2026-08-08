# Synthèse recruteur — projet BottleNeck

## Positionnement

Ce projet transforme trois extractions métier — ERP, site Web et table de liaison — en une analyse reproductible des ventes, des marges, du stock et de la qualité des données. L’objectif n’est pas de montrer un notebook isolé, mais une chaîne vérifiable : sources préservées, règles explicites, rapprochements audités, calculs testés et résultats exportés.

## Architecture et méthode

- `archive/original/` et `data/raw/` conservent les sources ; leurs empreintes sont contrôlées par les tests.
- `src/bottleneck_analysis/` sépare configuration, contrôles qualité, pipeline, indicateurs, expériences, graphiques et export.
- `scripts/` fournit des points d’entrée pour relancer l’analyse, construire le notebook et l’exécuter.
- `data/processed/` et `reports/` contiennent les sorties tabulaires et graphiques ; le notebook sert de restitution lisible, pas de source cachée de logique.
- `tests/` vérifie les contrats de colonnes et de clés, les cardinalités de jointure, l’absence de correction silencieuse, les calculs métier et les choix expérimentaux.

Le pipeline conserve les valeurs sources problématiques, les classe puis les met en quarantaine seulement dans les agrégats concernés. Il distingue **7 erreurs certaines**, **125 anomalies probables** et **33 valeurs inhabituelles mais plausibles**. Côté rapprochement, les **714 produits Web dotés d’un SKU valide** sont tous reliés, tandis que la couverture de la table de liaison côté ERP reste de **88,97 %** ; ces deux mesures ne sont pas confondues.

Sources : [indicateurs clés](../reports/tables/indicateurs_cles.json), [registre qualité](../reports/tables/registre_qualite.csv), [audit des rapprochements](../reports/tables/audit_jointures.csv).

## Choix comparés avec des preuves

| Sujet | Expérience réelle | Décision argumentée |
|---|---|---|
| Sélection des lignes Web | Le filtre métier sur les lignes produit donne **5 751 unités** et **143 680,10 € TTC**. Prendre les pièces jointes ou garder la première ligne par SKU donne **153 748,10 € TTC**, soit **10 068,00 €** de plus ; sommer toutes les lignes de l’export donne **297 428,20 € TTC**, soit **107,01 %** de plus. | Filtrer selon le type d’entité. Les dédoublonnages dépendant de l’ordre et la somme qui double compte sont rejetés. |
| Validation des données | Sur **9 cas**, le contrôle Pandas natif et Pandera détectent tous les cas. Le contrôle natif localise **9 cas sur 9**, contre **7 sur 9** pour Pandera ; les temps du dernier passage, indicatifs et dépendants de la machine, restent dans le CSV d'expérience. | Garder les contrôles Pandas explicites dans le fonctionnement courant ; conserver Pandera comme contrôle additionnel facultatif. |
| Prix inhabituels | La méthode robuste sur les prix bruts détecte **20 cas injectés sur 20**, conserve un score de stabilité de **90,91 %** et signale **33 prix** dans les données de départ. Les autres méthodes testées détectent de **0 à 19 cas injectés sur 20**. | Retenir cette méthode pour prioriser une revue humaine ; ne jamais transformer automatiquement une alerte statistique en erreur. |

Sources : [comparaison de sélection Web](../reports/tables/comparaison_selection_lignes_web.csv), [comparaison des validateurs](../reports/tables/comparaison_validateurs.csv), [comparaison des méthodes de détection](../reports/tables/comparaison_methodes_outliers.csv).

## Preuves de fiabilité

La suite `python -m pytest -q` a été exécutée avec succès sur l’état courant. Elle contrôle notamment :

- la préservation exacte des sources ;
- l’unicité des clés et le rapprochement des lignes ;
- la mise en quarantaine sans changement silencieux des signes ou des statuts ;
- le chiffre d’affaires d’octobre, recalculé indépendamment avec une arithmétique décimale et réconcilié à **0,00 €** ;
- la séparation entre stock brut signé et stock hors anomalies ;
- la reproductibilité des comparaisons de méthodes.

Le résultat métier principal est un chiffre d’affaires d’octobre de **143 680,10 € TTC** pour une marge brute de **44 660,65 € HT**, cette dernière reposant sur une TVA supposée à **20 %**. Les unités fiscales et les périmètres sont affichés avec les indicateurs pour éviter une comparaison trompeuse ; l'année et l'horodatage d'extraction, absents des sources, restent explicitement à confirmer.

Source : [indicateurs clés](../reports/tables/indicateurs_cles.json).

## Usage critique de l’IA

L’IA a servi d’assistant pour proposer des options, challenger la structure, produire des variantes et accélérer la rédaction. Elle n’est pas utilisée comme source de vérité métier. Une proposition n’est conservée que lorsqu’elle peut être reliée au code exécuté, à un test ou à un export mesuré ; les choix dépendant de l’ordre, les doubles comptages et les interprétations non démontrées sont rejetés. Les indicateurs métier restent produits par un pipeline déterministe et révisables par un humain ; les temps d’exécution sont, eux, des mesures locales.

Ce projet ne revendique ni prévision annuelle ni causalité. Sa valeur de portfolio tient à la traçabilité des décisions, aux expériences comparatives et à la capacité à exposer honnêtement ce que les données ne permettent pas de conclure.
