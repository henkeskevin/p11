# BottleNeck — analyse reproductible des ventes, stocks et marges

Projet portfolio d'analyse de données rapprochant trois extractions : référentiel ERP, ventes Web et table de liaison ERP–SKU. La version actuelle transforme le notebook initial dépendant de Google Colab en un pipeline local testé, auditable et orienté décision.

> Périmètre : ventes d'**octobre uniquement** et stock observé au **31 octobre**. L'année et l'horodatage d'extraction ne figurent pas dans les sources et restent à confirmer. Une couverture `stock / ventes d'octobre` décrit un scénario au rythme d'octobre; ce n'est ni une prévision, ni une rotation comptable.

## Résultats vérifiés

| Indicateur | Résultat | Périmètre / définition |
|---|---:|---|
| Produits Web rapprochés | 714 | Relation 1–1 après filtre `post_type="product"` |
| CA TTC | 143 680,10 € | Octobre, recalcul indépendant avec `Decimal` |
| Unités vendues | 5 751 | Octobre |
| Marge brute | 44 660,65 € HT | TVA supposée à 20 %, coût d'achat supposé HT |
| Taux de marque pondéré | 37,30 % | Marge / ventes HT |
| Références nécessaires pour 80 % du CA | 435 (60,92 %) | Le catalogue ne suit pas un Pareto 20/80 |
| Stock apparié brut signé | 16 739 unités · 277 305,77 € HT | Valeur au coût, anomalie négative conservée |
| Stock sans vente observée en octobre | 14 959,40 € HT | 3 références; couverture laissée indéfinie |
| Couverture supérieure à 12 mois | 95 011,92 € HT | 24 références, scénario au rythme d'octobre |

Les résultats détaillés sont dans [la synthèse CODIR](docs/synthese_codir.md), [le notebook exécuté](notebooks/BottleNeck_analyse_portfolio.ipynb), [la présentation de décision](reports/BottleNeck_CODIR.pptx) et [les indicateurs machine-readable](reports/tables/indicateurs_cles.json).

## Ce qui a été fiabilisé

- conservation immuable des classeurs bruts et de leurs empreintes SHA-256;
- chemins relatifs, environnement Python déclaré et exécution depuis un noyau propre;
- schémas, types, domaines, clés nulles, unicité et cardinalités de jointure contrôlés;
- aucune valeur absolue, imputation de SKU ou suppression silencieuse;
- registre distinguant erreur certaine, anomalie probable et valeur inhabituelle mais plausible;
- CA réconcilié par une seconde implémentation `Decimal`;
- valeur de stock au coût séparée de la valeur potentielle au prix de vente;
- couverture non définie lorsque les ventes d'octobre sont nulles;
- taux de marque et taux de marge sur coût explicitement différenciés;
- expériences réelles sur la sélection des lignes Web, quatre méthodes d'outliers et pandas natif vs Pandera;
- graphiques statiques PNG et SVG adaptés à une restitution de direction;
- tests automatisés, notebook exécuté et présentation CODIR régénérée.

## Reproduction sous Windows / PowerShell

Prérequis : Python 3.12 et Git.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt

.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\run_analysis.py
.\.venv\Scripts\python.exe experiments\compare_validators.py
.\.venv\Scripts\python.exe scripts\build_notebook.py
.\.venv\Scripts\python.exe scripts\execute_notebook.py
.\.venv\Scripts\python.exe scripts\validate_deliverables.py --full
```

Les commandes doivent être lancées depuis la racine du dépôt. `scripts/run_analysis.py` régénère les CSV, le JSON d'indicateurs et 11 graphiques en PNG + SVG. `scripts/execute_notebook.py` exécute le notebook dans un nouveau noyau et remplace le fichier uniquement si toutes les cellules réussissent.

## Organisation

```text
archive/original/          copie exacte et manifeste SHA-256 de l'état initial
data/raw/                  sources Excel immuables
data/processed/            catalogues rapprochés générés
docs/                      cadrage, preuves, décisions, veille et limites
experiments/               comparaison exécutable pandas / Pandera
notebooks/                 notebook portfolio exécuté
reports/figures/           graphiques PNG et SVG
reports/tables/            KPI, audits, registres qualité et expériences
scripts/                   génération, analyse et exécution du notebook
src/bottleneck_analysis/   pipeline métier testable
tests/                     tests unitaires, intégration et livrables
```

Le namespace Python est `bottleneck_analysis` : le nom `bottleneck` a été écarté car il masquerait la bibliothèque d'accélération homonyme utilisée facultativement par pandas.

## Documents de preuve

- [Audit de l'état initial](docs/audit_initial.md)
- [Cahier des charges](docs/cahier_des_charges.md)
- [Matrice exigences → preuves](docs/matrice_exigences_preuves.md)
- [Backlog, planning et risques](docs/backlog_planning_risques.md)
- [Registre continu des améliorations](docs/registre_ameliorations.md)
- [Registre des expériences avec l'IA](docs/registre_experiences_ia.md)
- [Veille métier et technologique](docs/veille_metier_technologique.md)
- [Synthèse CODIR](docs/synthese_codir.md)
- [Synthèse recruteur](docs/synthese_recruteur.md)
- [Limites et biais](docs/limites_biais.md)

## Décisions méthodologiques clés

Le filtre sémantique `post_type="product"` est retenu : dédupliquer selon l'ordre peut surévaluer le CA de 10 068 € (+7,01 %) et sommer produit + pièce jointe le double pratiquement. Pour les prix, le z-score modifié MAD est retenu après injection contrôlée : 100 % de rappel sur 20 cas, 4,62 % d'alertes initiales et stabilité de Jaccard supérieure à 0,90. Ces 33 références restent des signaux de revue, jamais des erreurs automatiques.

Le pipeline pandas natif est conservé en production après une expérience sur 9 défauts injectés : pandas et Pandera détectent 9/9, mais les contrôles natifs localisent 9/9 contre 7/9 pour cette configuration Pandera. Ils sont aussi plus rapides dans les passages mesurés ; le temps dépendant de la machine reste publié dans `reports/tables/comparaison_validateurs.csv`. Pandera reste documenté comme garde additionnelle possible.

## Données et confidentialité

Les fichiers sources sont inclus pour rendre ce portfolio reproductible. Avant publication publique, vérifier les droits de diffusion des extractions et supprimer ou anonymiser toute donnée qui deviendrait sensible. Aucun appel à une API externe n'est requis par le pipeline.
