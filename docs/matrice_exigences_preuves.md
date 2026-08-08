# Matrice des exigences et des preuves

**Date de gel documentaire :** 8 août 2026  
**Objet :** relier les demandes de la mission BottleNeck à des artefacts et vérifications reproductibles.

## Lecture des statuts

- **Réalisé** : une implémentation et une preuve persistante sont présentes dans le dépôt ; lorsque l’exigence est exécutable, une vérification a réussi.
- **Partiel** : une part substantielle est livrée, mais une validation métier, une action externe ou la réponse finale reste nécessaire.
- **Non réalisé** : aucune preuve suffisante n’est disponible. Une exigence hors périmètre ne devient pas « réalisée » par simple déclaration.

Les chemins sont relatifs à la racine du dépôt. Les valeurs chiffrées se rapportent au jeu fourni : ventes d’octobre, stock au 31 octobre.

## 1. Mission, diagnostic et démarche d’amélioration

| ID | Demande du prompt | Statut | Implémentation / résultat | Preuve exacte |
|---|---|---|---|---|
| E01 | Inspecter tout le dépôt et préserver la version initiale | **Réalisé** | Huit fichiers initiaux copiés bit à bit, tailles et SHA-256 consignés ; le validateur recalcule les huit empreintes et compare les trois paires archive/`data/raw/` | `archive/original/MANIFEST.md`; `src/bottleneck_analysis/deliverables.py::_validate_archive`; `src/bottleneck_analysis/deliverables.py::_validate_raw_sources`; `tests/test_deliverables.py::test_archive_manifest_covers_every_preserved_file`; `reports/tables/final_validation.json` |
| E02 | Exécuter le notebook existant de bout en bout pour établir une baseline | **Réalisé** | L’exécution stricte est tentée sans masquer l’échec : code 1 en 5,02 s, cellule 5, `ModuleNotFoundError: google.colab`. Un diagnostic neutralisé séparé atteint 72 cellules puis échoue sur `seaborn` | `reports/tables/baseline_execution.json`; `docs/audit_initial.md`; commande baseline reproduite en section 6 |
| E03 | Relever erreurs, avertissements, durée et reproductibilité de l’existant | **Réalisé** | Dépendance Colab, chemin Drive absolu, import manquant, métadonnées incohérentes et cellules non exécutées documentés | `docs/audit_initial.md`; `reports/tables/baseline_execution.json` |
| E04 | Relever incohérences, calculs fragiles, défauts de structure, d’analyse et de visualisation | **Réalisé** | Valeurs absolues silencieuses, SKU inventés, jointures destructrices, Pareto dépendant de l’ordre, couverture nulle erronée, marge mal nommée, valorisation contradictoire et causalité abusive recensés | `docs/audit_initial.md` |
| E05 | Ne pas s’arrêter à un audit ; modifier, exécuter, tester et livrer un projet fonctionnel | **Réalisé** | Package sous `src/`, scripts, notebook portfolio, tests, CI, exports et documentation ajoutés | `src/bottleneck_analysis/`; `scripts/`; `notebooks/BottleNeck_analyse_portfolio.ipynb`; `tests/`; `.github/workflows/ci.yml` |
| E06 | Être force de proposition à partir du dépôt, des données, du métier et de la grille | **Réalisé** | Ajouts démontrés : HHI, double sémantique de marge, vues de stock brute/valide, segments d’action, expérience de sélection Web, comparaison de validateurs et graphiques décisionnels complémentaires | `docs/registre_ameliorations.md`; `reports/tables/indicateurs_cles.json`; `reports/figures/` |
| E07 | Examiner plusieurs options et évaluer valeur, fiabilité, complexité et intérêt portfolio | **Réalisé** | Trois comparaisons exécutées : 5 sélections Web, 4 méthodes d’outliers, pandas natif contre Pandera | `reports/tables/comparaison_selection_lignes_web.csv`; `reports/tables/comparaison_methodes_outliers.csv`; `reports/tables/comparaison_validateurs.csv` |
| E08 | Définir les critères avant expérience, mesurer et justifier le choix | **Réalisé** | Critères codés : exactitude métier et CA ; rappel, stabilité, taux d’alerte, runtime ; détection, localisation, non-mutation, testabilité, runtime et complexité | `src/bottleneck_analysis/experiments.py`; `src/bottleneck_analysis/outliers.py`; `experiments/compare_validators.py`; `docs/registre_experiences_ia.md` |
| E09 | Intégrer, exécuter et vérifier une amélioration avant de la déclarer réalisée | **Réalisé** | Chaque amélioration livrée renvoie à du code, un export et/ou un test ; les limites résiduelles restent explicitement ouvertes | `docs/registre_ameliorations.md`; `tests/` |
| E10 | Revenir sur un mauvais choix si une découverte ultérieure le contredit | **Réalisé** | Le filtre par ordre, la somme de toutes les lignes et la correction silencieuse sont rejetés après mesure ; la logique finale utilise `post_type='product'` et la quarantaine | `reports/tables/comparaison_selection_lignes_web.csv`; `src/bottleneck_analysis/pipeline.py` |
| E11 | Éviter le surdéveloppement et le ML décoratif | **Réalisé** | Pandera est comparé mais non imposé au runtime ; aucun ML n’est ajouté sans historique adapté | `reports/tables/comparaison_validateurs.csv`; `pyproject.toml`; `docs/limites_biais.md` |
| E12 | Alimenter un registre continu des améliorations | **Réalisé** | Problème, options, décision, implémentation, résultat, preuve et limite sont consignés par entrée | `docs/registre_ameliorations.md` |

## 2. Fiabilité des données et analyses métier

| ID | Demande du prompt | Statut | Implémentation / résultat | Preuve exacte |
|---|---|---|---|---|
| E13 | Fiabiliser le chargement | **Réalisé** | Sources relatives, présence vérifiée, avertissements capturés. Trois avertissements Excel sont conservés | `src/bottleneck_analysis/config.py`; `src/bottleneck_analysis/pipeline.py::_read_excel`; `reports/tables/avertissements_chargement.csv` |
| E14 | Contrôler colonnes, clés, types, valeurs manquantes et domaines | **Réalisé** | Contrats ERP/Web/liaison, conversion numérique auditée, clés vides et domaines contrôlés | `src/bottleneck_analysis/quality.py`; `src/bottleneck_analysis/pipeline.py`; `tests/test_pipeline.py` |
| E15 | Contrôler doublons et cardinalités de jointure | **Réalisé** | Unicité non nulle exigée ; jointures `one_to_one` ou `many_to_one` déclarées ; un doublon de clé provoque un échec | `src/bottleneck_analysis/quality.py::assert_unique_non_null`; `src/bottleneck_analysis/pipeline.py`; `tests/test_pipeline.py::test_duplicate_non_null_key_fails_fast` |
| E16 | Rapprocher ERP, Web et liaison avec audit | **Réalisé** | 825 ERP ↔ liaison ; 714 correspondances Web ; 20 clés de liaison absentes des produits Web ; 91 clés Web nulles distinguées | `reports/tables/audit_jointures.csv`; `reports/tables/indicateurs_cles.json`; `tests/test_pipeline.py::test_join_audit_reconciles_all_rows` |
| E17 | Empêcher les corrections silencieuses | **Réalisé** | Prix −20, stocks −10/−1 et statuts source restent inchangés ; aucune clé inconnue n’est inventée | `tests/test_pipeline.py::test_no_silent_sign_or_status_correction`; `tests/test_pipeline.py::test_null_skus_are_not_matched_or_invented`; `reports/tables/registre_qualite.csv` |
| E18 | Distinguer erreur certaine, anomalie probable et inhabituel plausible | **Réalisé** | 7 erreurs certaines, 125 anomalies probables et 33 prix inhabituels plausibles dans un schéma commun | `reports/tables/registre_qualite.csv`; `reports/tables/indicateurs_cles.json`; `src/bottleneck_analysis/quality.py` |
| E19 | Vérifier indépendamment les calculs principaux | **Réalisé** | CA vectorisé 143 680,10 € et seconde boucle `Decimal` : écart 0,00 € | `src/bottleneck_analysis/metrics.py::independent_ca_decimal`; `tests/test_metrics.py::test_revenue_is_reconciled_by_decimal_method`; `reports/tables/indicateurs_cles.json` |
| E20 | Calculer le CA et les unités | **Réalisé** | 143 680,10 € TTC et 5 751 unités en octobre | `reports/tables/indicateurs_cles.json`; `reports/tables/top20_ca_octobre.csv`; `tests/test_metrics.py` |
| E21 | Analyser meilleures références et concentration | **Réalisé** | Top 20 = 11,02 % ; 435 références (60,92 %) pour 80 % ; HHI 0,002217 ; absence de Pareto 20/80 mise en évidence | `reports/tables/top20_ca_octobre.csv`; `reports/tables/indicateurs_cles.json`; `reports/figures/02_top10_ca_octobre.png`; `reports/figures/03_pareto_ca_octobre.png`; `tests/test_metrics.py::test_concentration_metrics` |
| E22 | Étudier les prix potentiellement aberrants sans les confondre avec des erreurs | **Réalisé** | MAD brut retenu : 33 alertes, rappel 20/20, Jaccard 0,909 ; aucune exclusion automatique | `reports/tables/comparaison_methodes_outliers.csv`; `src/bottleneck_analysis/outliers.py`; `tests/test_experiments.py` |
| E23 | Analyser marge | **Réalisé** | Marge brute 44 660,65 € HT, taux de marque pondéré 37,30 %, taux sur coût 59,49 %, une référence négative à revoir ; TVA 20 % explicitée | `reports/tables/indicateurs_cles.json`; `src/bottleneck_analysis/metrics.py`; `reports/figures/06_marge_ponderee_type.png`; `reports/figures/10_anomalie_marge_reference_4355.png`; `tests/test_metrics.py::test_margin_semantics_and_values` |
| E24 | Analyser stocks et rotation | **Réalisé** | Vues brute signée et hors stock négatif ; 22 ruptures potentielles, 3 stocks sans vente (14 959,40 € HT), 24 références >12 mois (95 011,92 € HT) | `reports/tables/indicateurs_cles.json`; `reports/tables/priorites_stock.csv`; `reports/figures/05_segments_stock.png`; `reports/figures/09_stock_sans_vente_octobre.png`; `tests/test_metrics.py::test_zero_sales_stock_has_undefined_coverage_not_zero`; `tests/test_metrics.py::test_stock_reports_raw_and_quarantine_excluded_views` |
| E25 | Étudier les relations quantitatives | **Réalisé** | Corrélations de Spearman prix, ventes, stock et taux de marque ; le titre exclut toute inférence causale | `src/bottleneck_analysis/visuals.py`; `reports/figures/07_correlations_spearman.png`; `docs/limites_biais.md` |
| E26 | Ajouter des analyses complémentaires réellement utiles | **Réalisé** | HHI, typologie des alertes, statut ERP/Web croisé, valeurs de stock coût/vente, action sur stock dormant, cas de marge négative et dispersion prix–ventes | `reports/tables/indicateurs_cles.json`; `reports/figures/08_typologie_alertes.png`; `reports/figures/09_stock_sans_vente_octobre.png`; `reports/figures/10_anomalie_marge_reference_4355.png`; `reports/figures/11_prix_vs_ventes_octobre.png`; `docs/registre_ameliorations.md` |
| E27 | Limiter projections et généralisations liées au seul mois d’octobre | **Réalisé** | Période encodée dans la configuration et les exports ; couverture qualifiée de scénario ; aucune annualisation | `src/bottleneck_analysis/config.py`; `reports/tables/indicateurs_cles.json`; `docs/limites_biais.md`; `notebooks/BottleNeck_analyse_portfolio.ipynb` |

## 3. Livrables attendus

| ID | Livrable demandé | Statut | Preuve exacte |
|---|---|---|---|
| E28 | Notebook amélioré et exécuté | **Réalisé** | `notebooks/BottleNeck_analyse_portfolio.ipynb` — 24 cellules, 12 code toutes exécutées, aucune sortie d’erreur ; `reports/tables/final_validation.json` |
| E29 | README de reproduction | **Réalisé** | `README.md` — installation, commandes, architecture, résultats, décisions et confidentialité |
| E30 | Cahier des charges fonctionnel | **Réalisé** | `docs/cahier_des_charges.md` |
| E31 | Veille métier et technologique sourcée | **Réalisé** | `docs/veille_metier_technologique.md` |
| E32 | Matrice exigences–preuves | **Réalisé** | `docs/matrice_exigences_preuves.md` |
| E33 | Backlog, planning et registre des risques | **Réalisé** | `docs/backlog_planning_risques.md` |
| E34 | Registre des expériences réalisées avec l’IA | **Réalisé** | `docs/registre_experiences_ia.md` |
| E35 | Registre continu des améliorations | **Réalisé** | `docs/registre_ameliorations.md` |
| E36 | Synthèse destinée au CODIR | **Réalisé** | `docs/synthese_codir.md`; présentation finale de 12 slides `reports/BottleNeck_CODIR.pptx`; inspection `reports/BottleNeck_CODIR.pptx.inspect.ndjson`; contrôle présentation dans `reports/tables/final_validation.json`; `reports/figures/` |
| E37 | Synthèse destinée à un recruteur | **Réalisé** | `docs/synthese_recruteur.md` |
| E38 | Documentation des limites, hypothèses et biais | **Réalisé** | `docs/limites_biais.md` |
| E39 | Tests automatisés | **Réalisé** | 17 tests couvrent pipeline, métriques, expériences, archives et livrables : `tests/test_pipeline.py`; `tests/test_metrics.py`; `tests/test_experiments.py`; `tests/test_deliverables.py`. `reports/tables/final_validation.json` en prouve 17 réussis en 2,11 s. Le workflow est configuré dans `.github/workflows/ci.yml` ; son exécution distante reste ouverte en section 7 |
| E40 | Principaux résultats et graphiques exportés | **Réalisé** | `data/processed/`; `reports/tables/`; 11 figures en PNG et SVG sous `reports/figures/`; contrôle `exports` réussi dans `reports/tables/final_validation.json` |
| E41 | Restitution direction professionnelle | **Réalisé** | `docs/synthese_codir.md`; `reports/BottleNeck_CODIR.pptx`; `reports/BottleNeck_CODIR.pptx.inspect.ndjson`; `reports/figures/01_rapprochement_sources.png`; `reports/figures/03_pareto_ca_octobre.png`; `reports/figures/05_segments_stock.png`; `reports/figures/09_stock_sans_vente_octobre.png`; `reports/figures/10_anomalie_marge_reference_4355.png`; `reports/figures/11_prix_vs_ventes_octobre.png` |

## 4. Usage critique de l’IA

| ID | Demande du prompt | Statut | Preuve exacte |
|---|---|---|---|
| E42 | Documenter prompts ou variantes testés | **Réalisé** | `docs/registre_experiences_ia.md` |
| E43 | Documenter propositions, vérifications et sort retenu/modifié/rejeté | **Réalisé** | `docs/registre_experiences_ia.md`; `docs/registre_ameliorations.md` |
| E44 | Documenter raisons, gains et limites | **Réalisé** | Registres ci-dessus et trois CSV comparatifs sous `reports/tables/` |
| E45 | Ne pas prétendre avoir utilisé un outil externe non utilisé | **Réalisé** | Le registre sépare explicitement assistance IA, recherches sourcées, exécutions locales et validation humaine ; aucune correction métier externe n’est revendiquée : `docs/registre_experiences_ia.md`; `docs/veille_metier_technologique.md` |

## 5. Vérification finale

| ID | Vérification demandée | Statut | Résultat | Preuve exacte / réserve |
|---|---|---|---|---|
| E46 | Exécuter tous les tests | **Réalisé** | Commande pytest code 0, **17 réussis en 2,11 s** | `reports/tables/final_validation.json` |
| E47 | Exécuter le notebook depuis un noyau propre | **Réalisé** | Code 0, **20,74 s**, 24 cellules dont 12 de code exécutées, 0 erreur | `scripts/execute_notebook.py`; `notebooks/BottleNeck_analyse_portfolio.ipynb`; `reports/tables/final_validation.json` |
| E48 | Vérifier les chemins relatifs | **Réalisé** | Racine détectée par `pyproject.toml`, scripts fondés sur `PROJECT_ROOT`, notebook exécuté depuis la racine | `src/bottleneck_analysis/config.py::find_project_root`; `scripts/`; `reports/tables/final_validation.json`. Le workflow Linux est configuré mais aucun run distant vert n’est encore prouvé |
| E49 | Vérifier les jointures et cardinalités | **Réalisé** | 825 rapprochements ERP–liaison, 714 Web, 20 `left_only`, cardinalités déclarées | `reports/tables/audit_jointures.csv`; `tests/test_pipeline.py::test_join_audit_reconciles_all_rows` |
| E50 | Recalculer les indicateurs principaux par une seconde méthode | **Réalisé** | CA recalculé avec `Decimal`; écart 0,00 € ; contrôle de stock brut/valide séparé | `src/bottleneck_analysis/metrics.py`; `tests/test_metrics.py` |
| E51 | Vérifier graphiques et exports | **Réalisé** | Le validateur lit les jeux traités et indicateurs, contrôle 714 lignes, 165 constats, les 11 PNG + 11 SVG, les documents et le paquet PPTX | `src/bottleneck_analysis/deliverables.py`; `tests/test_deliverables.py::test_final_deliverables_are_complete_and_auditable`; `reports/tables/final_validation.json` : 7/7 contrôles réussis |
| E52 | Vérifier que les comparaisons contiennent des résultats réels | **Réalisé** | Trois CSV générés par code ; les valeurs Web et outliers sont assertées, la comparaison des validateurs est rejouable | `reports/tables/comparaison_selection_lignes_web.csv`; `reports/tables/comparaison_methodes_outliers.csv`; `reports/tables/comparaison_validateurs.csv`; `tests/test_experiments.py`; `experiments/compare_validators.py` |
| E53 | Vérifier que les conclusions découlent des données | **Réalisé** | Synthèses bornées par indicateurs JSON, tableaux exportés et limites | `docs/synthese_codir.md`; `docs/synthese_recruteur.md`; `docs/limites_biais.md` |
| E54 | Vérifier que les limites sont clairement exposées | **Réalisé** | Période, sélection, TVA, stock, causalité, confidentialité et portée des tests documentés | `docs/limites_biais.md`; `README.md` |
| E55 | Vérifier que chaque amélioration annoncée est implémentée ou signalée non réalisée | **Réalisé** | Statuts et preuves par entrée | `docs/registre_ameliorations.md`; présente matrice |
| E56 | Corriger les défauts détectés avant conclusion | **Partiel** | Les défauts de code et de méthode ont été corrigés. Les 165 constats de données ne sont volontairement pas altérés sans autorité métier ; ils sont exportés et affectés au backlog | `reports/tables/registre_qualite.csv`; `docs/backlog_planning_risques.md` |
| E57 | Montrer une amélioration réelle et vérifiable par rapport à l’initial | **Réalisé** | Comparaison avant/après : échec Colab → exécution locale ; mutations silencieuses → quarantaine ; calcul unique → réconciliation ; aucun test → suite automatisée | `docs/audit_initial.md`; `reports/tables/baseline_execution.json`; `tests/` |
| E58 | Résumer les dix rubriques demandées dans la réponse finale | **Partiel** | Toutes les preuves nécessaires sont présentes dans le dépôt ; la réponse finale de remise reste un artefact conversationnel à produire après le dernier test, hors du dépôt | présente matrice ; `README.md`; `docs/registre_ameliorations.md`; `docs/registre_experiences_ia.md` |

## 6. Commandes de preuve

À exécuter depuis la racine du dépôt dans PowerShell :

```powershell
# Installer l’environnement complet de reproduction
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt

# Reproduire honnêtement l’échec de la baseline originale
.\.venv\Scripts\python.exe scripts\execute_notebook.py archive\original\Henkes_Kevin_1_notebook_012026.ipynb --output .tmp\baseline-executed.ipynb

# Vérifier code, indicateurs, contrats et livrables
.\.venv\Scripts\python.exe -m pytest -q

# Régénérer les données traitées, tableaux et 11 figures dans deux formats
.\.venv\Scripts\python.exe scripts\run_analysis.py

# Rejouer l’expérience pandas natif / Pandera
.\.venv\Scripts\python.exe experiments\compare_validators.py

# Reconstruire puis exécuter le notebook depuis un noyau propre
.\.venv\Scripts\python.exe scripts\build_notebook.py
.\.venv\Scripts\python.exe scripts\execute_notebook.py

# Rejouer toute la recette et écrire la preuve persistante finale
.\.venv\Scripts\python.exe scripts\validate_deliverables.py --full
```

L’échec attendu de la commande de baseline ne remet pas en cause la recette : il constitue la preuve du défaut initial. Toutes les commandes de la version portfolio doivent retourner un code 0. La dernière rejoue analyse, comparaison des validateurs, construction/exécution du notebook et pytest, contrôle les artefacts, puis écrit `reports/tables/final_validation.json`.

## 7. Écarts restant à fermer hors développement

| Écart | Pourquoi il reste ouvert | Clôture attendue |
|---|---|---|
| 7 erreurs certaines et 125 anomalies probables dans les sources | Le pipeline n’a pas autorité pour modifier ERP, Web ou liaison | Validation/correction par les data owners, puis remplacement contrôlé des sources et rerun |
| Hypothèse TVA 20 % et coût d’achat HT | Non certifiée par la finance | Visa écrit de la direction financière |
| Couverture calculée sur un seul mois | Absence d’historique multi-périodes | Ajouter au moins 12 mois comparables avant prévision ou cible de stock |
| Droits de publication des extractions | Le dépôt contient des données commerciales | Revue juridique/confidentialité avant publication publique |
| Résultat de CI distante | Le workflow est présent mais son exécution GitHub dépend d’un push | Vérifier un run vert sur la plateforme distante |

Ces écarts ne justifient pas de corriger ou d’inventer des données. Ils expliquent les deux statuts **Partiel** et sont repris avec responsables et échéances dans `docs/backlog_planning_risques.md`.
