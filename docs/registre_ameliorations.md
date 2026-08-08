# Registre continu des améliorations

**Version :** 1.0  
**Séquence couverte :** travaux du 8 août 2026  
**Convention :** les entrées sont ordonnées selon la séquence de travail, pas selon l'importance. Une amélioration n'est marquée « réalisée » que si elle est implémentée et reliée à une preuve. Toute durée est une observation locale indicative, dépendante de la machine et de la charge. Les benchmarks sont régénérés par la recette complète : les valeurs courantes se lisent dans `reports/tables/comparaison_validateurs.csv` et `reports/tables/comparaison_methodes_outliers.csv`, pas dans ce registre.

## A-001 — Préservation bit à bit de l'état initial

**Statut : réalisée.**

**Problème ou opportunité.** Le dépôt ne permettait pas de distinguer sans ambiguïté les fichiers d'origine des livrables améliorés. Toute modification directe aurait supprimé la baseline et rendu les comparaisons invérifiables.

**Amélioration proposée.** Archiver les huit fichiers présents à la racine avant modification et calculer leur empreinte.

**Options examinées.** S'appuyer uniquement sur Git; copier seulement le notebook; copier toutes les sources avec leur taille et SHA-256.

**Décision et justification.** Copie complète avec SHA-256. Le dépôt n'avait pas encore d'historique utile pour représenter cet état et les classeurs comme la présentation font partie de la preuve initiale.

**Implémentation.** Création de `archive/original/` et de `archive/original/MANIFEST.md`; re-hachage après copie. Les trois classeurs de travail sont aussi placés dans `data/raw/`.

**Résultat.** Huit copies correspondent exactement aux fichiers sources. Exemples : notebook `a2c094641fbeae20bb85c5cc18a9c79b9c497624494bd92605d9c95fe971cdec`; ERP `1179ffa647941447f497026e9e0c16e0b49490ef791f02f541c74df1300b0771`; Web `24f3ecdb4ea97cbc027f18d6b16ea1c9a97ffcbb0c9c50a43b9348ca4b1c9d48`; liaison `b3af2411c59789b3cdcced6abad74c00ed4dbae74184215a89b00dfb8a682c02`.

**Preuve de vérification.** `archive/original/MANIFEST.md` et `test_raw_sources_are_exact_preserved_copies`.

**Limite restante.** Une empreinte prouve l'identité binaire, pas l'origine métier ni la qualité du contenu.

## A-002 — Baseline exécutable et diagnostic de reproductibilité

**Statut : réalisée.**

**Problème ou opportunité.** Le notebook initial contenait des sorties historiques, mais aucune de ses 74 cellules de code n'avait de compteur d'exécution. Il dépendait de Colab, Google Drive, chemins absolus et dépendances non déclarées.

**Amélioration proposée.** Distinguer une exécution stricte de référence d'une exécution diagnostique permettant de découvrir les blocages suivants.

**Options examinées.** Lire seulement le notebook; modifier l'original pour le faire passer; exécuter l'archive intacte puis neutraliser séparément les dépendances externes à des fins de diagnostic.

**Décision et justification.** Troisième option. Modifier avant de mesurer aurait effacé la preuve de non-reproductibilité.

**Implémentation.** Exécution stricte avec `scripts/execute_notebook.py` vers `.tmp/baseline-executed.ipynb`; diagnostic séparé avec montage Colab et chemins absolus neutralisés sans écrire dans l'archive.

**Résultat.** Baseline stricte : échec sur `ModuleNotFoundError: No module named 'google.colab'`. Diagnostic : chemin `/content/drive/MyDrive/p6/`, puis seaborn absent après 72 cellules parcourues. Les passages diagnostiques froid/chaud ont une empreinte finale identique. Leurs durées historiques restent dans `docs/audit_initial.md`; elles sont indicatives, dépendantes de la machine et ne constituent pas un objectif de performance.

**Preuve de vérification.** `docs/audit_initial.md`, notebook archivé et sortie de la commande baseline.

**Limite restante.** Les mesures diagnostiques portent sur un programme neutralisé; seule l'erreur de l'exécution stricte appartient à la baseline contractuelle.

## A-003 — Structure de paquet et prévention de la collision pandas/`bottleneck`

**Statut : réalisée.**

**Problème ou opportunité.** Toute la logique était enfermée dans un notebook et le nom métier BottleNeck pouvait inciter à créer un module `bottleneck`, nom déjà utilisé par une dépendance de performance optionnelle de pandas.

**Amélioration proposée.** Créer un paquet installable au nom non ambigu, des scripts d'entrée et des dépendances déclarées.

**Options examinées.** Laisser le code dans le notebook; créer `bottleneck.py`; utiliser une distribution descriptive et un module distinct.

**Décision et justification.** Distribution `bottleneck-portfolio` et module `bottleneck_analysis`. Le nom métier est conservé sans pouvoir masquer le paquet tiers `bottleneck` lors d'un import pandas.

**Implémentation.** `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `src/bottleneck_analysis/` et scripts dans `scripts/`. La plage Python est `>=3.12,<3.14`; pandas est borné à la série 3.0.

**Résultat.** `import bottleneck_analysis` résout vers `src/bottleneck_analysis/`; pandas s'importe normalement; aucun paquet local `bottleneck` n'est présent dans l'environnement contrôlé.

**Preuve de vérification.** `pyproject.toml`, `src/bottleneck_analysis/__init__.py` et test d'import local.

**Limite restante.** L'environnement observé utilise pandas 3.0.3 alors que 3.0.5 est la version courante au 8 août 2026. La plage autorise la mise à jour, mais aucun lockfile ne fige l'ensemble résolu.

## A-004 — Chargement relatif, immuable et auditable

**Statut : réalisée.**

**Problème ou opportunité.** Les chemins Colab empêchaient une exécution locale; les avertissements Excel étaient noyés; aucune vérification de colonnes obligatoires n'arrêtait un schéma incompatible.

**Amélioration proposée.** Centraliser les chemins relatifs, préserver les frames brutes, contrôler les colonnes et capturer les avertissements.

**Options examinées.** Chemins absolus configurables à la main; copie implicite depuis la racine; racine de projet détectée et répertoires `data/raw`, `data/processed`, `reports` explicites.

**Décision et justification.** Troisième option, car elle est reproductible depuis la racine et sépare entrées immuables et sorties régénérées.

**Implémentation.** `AnalysisConfig`, `_read_excel`, `require_columns`, copies profondes avant normalisation et export de `avertissements_chargement.csv`.

**Résultat.** Les trois sources sont lues par chemins relatifs. Trois `UserWarning` openpyxl « Unknown extension is not supported and will be removed » sont capturés, un par classeur, au lieu d'être ignorés.

**Preuve de vérification.** `src/bottleneck_analysis/config.py`, `pipeline.py`, `reports/tables/avertissements_chargement.csv`.

**Limite restante.** Capturer un avertissement ne le résout pas; les extensions Excel doivent être identifiées avec le propriétaire du fichier si leur conservation est importante.

## A-005 — Clés nulles pandas, cardinalités et anti-jointures

**Statut : réalisée.**

**Problème ou opportunité.** pandas apparie deux clés nulles lors d'un `merge`, contrairement à la sémantique SQL habituelle. Le notebook initial inventait des identifiants, fusionnait puis supprimait des non-correspondances, et décrivait 91 clés nulles comme des doublons.

**Amélioration proposée.** Normaliser seulement la représentation, isoler les nulls, certifier l'unicité non nulle et rendre les anti-jointures visibles.

**Options examinées.** Laisser le rapprochement null-null; remplacer les nulls par `id_inconnu`; exclure les nulls du rapprochement tout en les conservant dans le registre.

**Décision et justification.** Troisième option. Une clé absente ne doit ni correspondre à une autre absence, ni devenir une identité inventée.

**Implémentation.** `normalize_identifier`, `assert_unique_non_null`, filtres `.notna()` avant jointure, `validate="one_to_one"`/`"many_to_one"`, `indicator` et export d'un audit par statut.

**Résultat.** 825 ERP sont reliés 1–1 aux 825 lignes de liaison; 734 identifiants Web non nuls sont uniques; 714 produits Web valides sont rapprochés; 20 liens restent `left_only`; deux produits sans SKU ne sont ni appariés ni renommés.

**Preuve de vérification.** `reports/tables/audit_jointures.csv`, `test_source_contracts_and_cardinalities`, `test_join_audit_reconciles_all_rows`, `test_null_skus_are_not_matched_or_invented`.

**Limite restante.** Les 91 identifiants absents et les 20 liens orphelins nécessitent une résolution dans les systèmes sources; le pipeline ne peut pas déduire leur bonne correspondance.

## A-006 — Suppression des corrections silencieuses et typologie des constats

**Statut : réalisée.**

**Problème ou opportunité.** Le notebook appliquait notamment des valeurs absolues à trois prix, deux stocks et deux ventes négatifs, inventait deux SKU et écrasait quatre incohérences de statut. Ces transformations produisaient des chiffres propres mais non traçables.

**Amélioration proposée.** Conserver les valeurs brutes, journaliser les écarts et n'exclure une valeur que de l'indicateur qu'elle invalide.

**Options examinées.** Corriger automatiquement; arrêter toute l'analyse au premier écart; conserver, classifier et mettre en quarantaine de façon ciblée.

**Décision et justification.** Troisième option. Les doublons ou colonnes absentes bloquent le pipeline, mais une valeur métier douteuse doit rester visible pour permettre l'analyse du reste du catalogue.

**Implémentation.** Registre à neuf colonnes (`rule_id`, source, clé, colonne, valeur brute, sévérité, catégorie, description, action); masques explicites par métrique; trois catégories de décision.

**Résultat.** **165 constats** : 7 erreurs certaines, 125 anomalies probables et 33 valeurs inhabituelles mais plausibles. Le prix −20 de la référence 4233, les stocks −10/−1 et les statuts d'origine restent inchangés; la référence 5700 est classée `quarantaine` pour le stock.

**Preuve de vérification.** `reports/tables/registre_qualite.csv` et `test_no_silent_sign_or_status_correction`.

**Limite restante.** La classification initiale est une règle analytique; les propriétaires ERP/Web doivent confirmer et corriger la source.

## A-007 — Expérience de sélection des lignes Web

**Statut : réalisée.**

**Problème ou opportunité.** Le fichier Web contient lignes produit, pièces jointes et lignes structurelles. Un `drop_duplicates` dépend de l'ordre et une somme peut compter deux fois la même vente.

**Amélioration proposée.** Comparer les choix sur le CA réel selon des critères définis avant calcul : sens métier, une ligne par SKU, invariance à l'ordre et absence de double comptage.

**Options examinées.** `post_type="product"`; `attachment`; garder la première ligne; garder la dernière; sommer toutes les lignes.

**Décision et justification.** Filtre sémantique `product`. La dernière occurrence donne ici le même CA par accident, mais ne satisfait pas l'invariance à l'ordre.

**Implémentation.** `compare_web_selection_methods` avec jointure 1–1 sur les prix et écarts absolus/relatifs exportés.

**Résultat.** Produit : **5 751 unités**, **143 680,10 € TTC**. Attachment et première ligne : **+10 068,00 € (+7,01 %)**. Somme : **+153 748,10 € (+107,01 %)**.

**Preuve de vérification.** `reports/tables/comparaison_selection_lignes_web.csv` et `test_web_selection_experiment_proves_order_risk`.

**Limite restante.** La sémantique de `post_type` dépend du contrat de l'export WordPress/WooCommerce; un changement amont impose de rejouer l'expérience.

## A-008 — Recalcul indépendant du CA et séparation des unités financières

**Statut : réalisée.**

**Problème ou opportunité.** Le CA n'avait qu'un chemin de calcul et le notebook mélangeait parfois prix TTC, coût HT, valeur de stock et taux de marge/marque.

**Amélioration proposée.** Recalculer le CA avec une seconde chaîne, publier les unités et séparer taux de marque et taux de marge sur coût.

**Options examinées.** Assertions sur le même agrégat pandas; second calcul pandas; chaîne `openpyxl` + dictionnaires + `Decimal`.

**Décision et justification.** Troisième option pour limiter le risque d'erreur commune. Le taux `(PV HT - coût) / PV HT` est nommé taux de marque; `(PV HT - coût) / coût` reste distinct.

**Implémentation.** `independent_ca_decimal`, métriques séparées TTC/HT, hypothèse de TVA centralisée à 20 % et tests numériques.

**Résultat.** CA **143 680,10 € TTC**, **5 751 unités**, marge brute d'octobre **44 660,65 € HT**, taux de marque pondéré **37,30 %**, écart de réconciliation **0,00 €**.

**Preuve de vérification.** `reports/tables/indicateurs_cles.json`, `test_revenue_is_reconciled_by_decimal_method`, `test_margin_semantics_and_values`.

**Limite restante.** TVA 20 %, prix de vente TTC et coût d'achat HT sont des hypothèses à confirmer. Le recalcul indépendant ne valide pas ces conventions.

## A-009 — Stock, couverture et décisions métier prudentes

**Statut : réalisée.**

**Problème ou opportunité.** Remplacer l'infini par zéro faisait apparaître trois références avec stock mais sans vente comme ayant zéro mois de couverture. La valorisation au prix de vente était confondue avec la valeur au coût.

**Amélioration proposée.** Conserver une couverture indéfinie quand les ventes sont nulles, distinguer stock brut et hors anomalies et segmenter selon le besoin d'action.

**Options examinées.** Couverture zéro; valeur arbitraire haute; `NaN` avec segment explicite. Valorisation unique au prix de vente; séparation coût HT/vente TTC.

**Décision et justification.** `NaN` + `stock_sans_vente_octobre`, et deux valorisations clairement nommées. Une division impossible ne doit pas devenir un zéro métier.

**Implémentation.** Segments de stock, agrégats bruts signés et valides, tableau `priorites_stock.csv` et tests dédiés.

**Résultat.** Catalogue rapproché hors stock négatif : **16 740 unités**, **277 328,07 € au coût HT**. Trois références sans vente : **14 959,40 €**; 24 au-delà de douze mois au rythme d'octobre : **95 011,92 €**; 22 vendues avec stock final nul.

**Preuve de vérification.** `reports/tables/priorites_stock.csv`, `indicateurs_cles.json`, `test_zero_sales_stock_has_undefined_coverage_not_zero`, `test_stock_reports_raw_and_quarantine_excluded_views`.

**Limite restante.** Le stock est une photo au 31 octobre et les ventes ne couvrent qu'octobre. Les segments ordonnent une revue; ils ne prévoient ni demande annuelle ni délai de réapprovisionnement.

## A-010 — Expérience comparative des prix inhabituels

**Statut : réalisée.**

**Problème ou opportunité.** Le notebook initial présentait IQR et z-score sans protocole de choix et risquait d'assimiler un prix élevé à une erreur.

**Amélioration proposée.** Comparer quatre méthodes sur la liste réelle et sur une contamination reproductible, avec critères préalables.

**Options examinées.** IQR brut, z-score brut, MAD brute, MAD logarithmique; medcouple et modèles ML étudiés mais non retenus faute de bénéfice justifié.

**Décision et justification.** MAD brute, seuil NIST 3,5, uniquement sur prix positifs. Elle est la seule méthode testée à satisfaire rappel 100 %, taux d'alerte inférieur à 5 % et Jaccard supérieur à 0,90.

**Implémentation.** Graine 42, 20 prix du cœur de distribution multipliés par six, 30 répétitions; export des alertes, rappel, stabilité et temps.

**Résultat.** MAD : **33 alertes (4,62 %)**, rappel **100 %**, Jaccard **0,9091**. IQR : 95 %/0,8387; z-score : 55 %/0,4615; MAD log : 0 %/1,0.

**Preuve de vérification.** `src/bottleneck_analysis/outliers.py`, `reports/tables/comparaison_methodes_outliers.csv`, `test_mad_wins_predefined_outlier_experiment`. Le CSV régénéré porte la mesure de temps indicative courante; le registre ne la duplique pas.

**Limite restante.** Les injections ne sont pas des erreurs réelles étiquetées. Les 33 signaux restent `inhabituel_plausible` jusqu'à revue métier.

## A-011 — Expérience pandas natif contre Pandera

**Statut : réalisée.**

**Problème ou opportunité.** Un framework de validation pouvait améliorer la lisibilité, mais ajouter une dépendance sans gain mesuré aurait été du surdéveloppement.

**Amélioration proposée.** Comparer sur les mêmes neuf mutations, selon une pondération écrite avant décision.

**Options examinées.** Contrôles pandas explicites; Pandera 0.32.x `lazy=True`; Great Expectations 1.20.0 examiné sur documentation seulement.

**Décision et justification.** pandas natif au runtime; Pandera comme outil de développement facultatif. Great Expectations rejeté pour ce petit pipeline local et non présenté comme benchmarké.

**Implémentation.** `experiments/compare_validators.py`, neuf fixtures fautives, empreinte avant/après, 30 répétitions, score pondéré détection/localisation/non-mutation/intégration/temps/complexité.

**Résultat.** Détection 9/9 pour les deux; localisation 9/9 pandas contre 7/9 Pandera; entrées inchangées. Le choix pandas natif repose sur ces résultats, ses diagnostics métier et la dépendance minimale, sans ratio ni temps figé dans le registre.

**Preuve de vérification.** `reports/tables/comparaison_validateurs.csv` et script reproductible. Le CSV contient le dernier chronométrage indicatif régénéré.

**Limite restante.** Les temps sont indicatifs et dépendants de la machine; seuls les résultats de détection/localisation et le choix courant sont consignés ici. Une architecture multi-sources ou multi-backends pourrait inverser le compromis de maintenabilité.

## A-012 — Tests automatisés et intégration continue

**Statut : réalisée localement; CI configurée.**

**Problème ou opportunité.** Aucun test ne protégeait les sources, cardinalités, calculs ou choix expérimentaux.

**Amélioration proposée.** Tester les contrats critiques et relancer analyse, expérience de validation et notebook en CI.

**Options examinées.** Tests de cellules de notebook; tests unitaires isolés; tests de pipeline avec vraies sources et contrôles ciblés.

**Décision et justification.** Combiner tests unitaires et tests d'intégration sur les sources préservées. Le notebook reste une restitution, pas le seul support de logique.

**Implémentation.** `tests/` pour empreintes, clés, jointures, non-correction, CA, marge, stock et expériences; `.github/workflows/ci.yml` sous Python 3.12.

**Résultat.** **17 tests réussis** dans l'environnement local contrôlé, dont deux contrôles dédiés aux livrables et à l'archive. La durée d'un passage varie selon la machine et n'est pas un critère contractuel.

**Preuve de vérification.** `reports/tables/final_validation.json`, fichiers `tests/`, workflow `validation`.

**Limite restante.** La CI est configurée mais son exécution distante n'est pas prouvée tant qu'un run GitHub Actions n'a pas abouti. Les tests ne couvrent pas toute modification future.

## A-013 — Notebook court, généré et exécuté depuis un noyau propre

**Statut : réalisée.**

**Problème ou opportunité.** Le notebook initial de 107 cellules était long, dépendant de l'ordre, non exécutable localement et mélangeait exploration, correction et restitution.

**Amélioration proposée.** Générer un notebook narratif qui appelle le même pipeline testé, affiche les expériences et expose clairement hypothèses et limites.

**Options examinées.** Corriger les 107 cellules une par une; produire un script sans notebook; générer un notebook portfolio compact à partir d'un script versionnable.

**Décision et justification.** Troisième option. Elle conserve un livrable pédagogique tout en évitant une logique divergente cachée dans les cellules.

**Implémentation.** `scripts/build_notebook.py` produit `notebooks/BottleNeck_analyse_portfolio.ipynb`; `scripts/execute_notebook.py` impose un noyau propre, le répertoire racine, un timeout et `allow_errors=False`.

**Résultat.** **24 cellules**, dont **12 de code**, toutes exécutées; exécution propre, aucune sortie `error`. Les chemins sont relatifs et les versions de l'environnement sont affichées; la durée dépend de la machine et du rendu des figures.

**Preuve de vérification.** Notebook exécuté, métadonnées d'exécution et sortie de `scripts/execute_notebook.py`.

**Limite restante.** Le notebook régénère les rapports et son temps dépend du rendu des figures. Il doit être reconstruit après toute modification du script générateur.

## A-014 — Figures décisionnelles et exports ouverts

**Statut : réalisée.**

**Problème ou opportunité.** Les visualisations initiales dépendaient de Plotly/Colab, n'étaient pas exportées de façon stable et certaines conclusions dépassaient les données.

**Amélioration proposée.** Produire un petit ensemble de graphiques CODIR, avec titres-message, unités, palette cohérente et alternative tabulaire.

**Options examinées.** Dashboard interactif; figures seulement dans le notebook; exports statiques PNG et SVG avec CSV associés.

**Décision et justification.** Troisième option. Un dashboard n'est pas justifié par un instantané non récurrent; SVG permet le redimensionnement et PNG facilite la réutilisation.

**Implémentation.** `src/bottleneck_analysis/visuals.py` et onze thèmes : rapprochement, top 10, Pareto, prix inhabituels, segments de stock, marge pondérée, corrélations Spearman, typologie des alertes, stock sans vente d'octobre, anomalie de marge de la référence 4355 et prix face aux ventes d'octobre.

**Résultat.** **22 fichiers graphiques**, soit onze figures en PNG et SVG, régénérés par le pipeline.

**Preuve de vérification.** `reports/figures/01_...` à `11_...`, dont `09_stock_sans_vente_octobre`, `10_anomalie_marge_reference_4355` et `11_prix_vs_ventes_octobre`; tables correspondantes dans `reports/tables/`; comptage du run final.

**Limite restante.** Aucun test utilisateur ni audit d'accessibilité complet n'a été réalisé; les graphiques doivent rester accompagnés de texte et de données tabulaires.

## A-015 — Documentation orientée preuves et plusieurs publics

**Statut : réalisée et consolidée.**

**Problème ou opportunité.** Le README initial faisait six octets et le projet ne documentait ni baseline, décisions, limites, expériences IA ni responsabilités métier.

**Amélioration proposée.** Produire des documents non redondants, chacun relié à des artefacts régénérables.

**Options examinées.** Un rapport unique très long; commentaires dispersés dans le notebook; README de reproduction plus documents ciblés.

**Décision et justification.** Troisième option pour adapter le niveau de détail au développeur, au CODIR, au recruteur et à l'évaluateur.

**Implémentation.** Audit initial; veille sourcée; présents registres d'IA et d'améliorations; synthèses CODIR et recruteur; documents de gouvernance distribués dans `docs/`; README enrichi par le lot principal.

**Résultat.** Les chiffres narratifs renvoient aux CSV/JSON, les options rejetées restent visibles et les limites temporelles sont répétées aux points de décision.

**Preuve de vérification.** `docs/`, liens relatifs vers `reports/`, `docs/matrice_exigences_preuves.md` et `reports/tables/final_validation.json`.

**Limite restante.** La documentation est un instantané. Après régénération sur une nouvelle période, les nombres et statuts doivent être resynchronisés; les documents annoncés mais absents ne doivent pas être considérés livrés.

## A-016 — Présentation CODIR professionnelle

**Statut : réalisée et vérifiée.**

**Problème ou opportunité.** La présentation initiale de 18 slides reprend des analyses et chiffres fragiles. Elle offre cependant un gabarit visuel et fait partie des livrables attendus.

**Amélioration proposée.** Construire une narration de 10 à 12 slides centrée sur décisions, qualité, CA, stock, marge et limites, avec identifiants exacts et chiffres issus des exports.

**Options examinées.** Conserver l'ancien deck; le modifier sans audit; inspecter le paquet, cartographier les 18 slides puis générer et rendre la nouvelle version.

**Décision et justification.** Troisième option. La source est préservée et son langage visuel peut être réutilisé sans conserver ses erreurs analytiques.

**Implémentation.** Audit structurel et rendus sous `.tmp/presentation/template-inspect/`; carte des mises en page et des médias; création de la présentation finale `reports/BottleNeck_CODIR.pptx`.

**Résultat.** Présentation CODIR finale de **12 slides** livrée. Chaque slide a été inspectée visuellement; `slides_test` est **PASS**, sans débordement; la fidélité au template est **PASS**, avec **0 issue**.

**Preuve de vérification.** Source préservée `archive/original/Henkes_Kevin_2_presentation_012026.pptx`, SHA-256 `56954665b14b6aeb555be449e2fcfe71d8732a1314eb8a3c70cda610b714a54e`; livrable `reports/BottleNeck_CODIR.pptx`; inspection visuelle slide par slide; résultats `slides_test: PASS` sans débordement et `template fidelity: PASS` avec 0 issue.

**Limite restante.** Les contrôles couvrent le rendu, les débordements et la fidélité visuelle du fichier actuel. Ils ne valident pas les hypothèses métier sous-jacentes et devront être rejoués après toute modification du deck ou actualisation des données.

## A-017 — Validation intégrée de l'état courant

**Statut : réalisée sur l'état contrôlé; à rejouer après toute modification.**

**Problème ou opportunité.** Des composants corrects séparément peuvent diverger après régénération ou modification documentaire.

**Amélioration proposée.** Exécuter tests, pipeline et notebook; contrôler les sorties d'erreur, les volumes, les indicateurs et les exports.

**Options examinées.** Vérification visuelle seulement; tests seulement; matrice de contrôles techniques et métier.

**Décision et justification.** Troisième option, proportionnée au risque de calcul et de restitution.

**Implémentation.** `pytest`, `scripts/run_analysis.py`, `experiments/compare_validators.py`, construction puis exécution du notebook; contrôles de fichiers et rapprochement des métriques.

**Résultat.** 17 tests réussis; 714 lignes analytiques; CA 143 680,10 €; 5 751 unités; 165 constats; onze figures dans deux formats, soit 22 fichiers; notebook sans sortie d'erreur; présentation de 12 slides contrôlée.

**Preuve de vérification.** `reports/tables/final_validation.json` : 5/5 commandes et 7/7 contrôles réussis; `reports/tables/indicateurs_cles.json`, notebook exécuté et répertoires d'exports.

**Limite restante.** La présentation finale a fait l'objet de ses propres contrôles réussis (`slides_test` et fidélité au template). La validation intégrée ne remplace toujours pas une recette métier des données sources et doit être rejouée après toute actualisation analytique.

## Règle de mise à jour du registre

Toute nouvelle amélioration doit ajouter une entrée datée et conserver : problème, options, décision, implémentation, résultat, preuve et limite. Une idée non implémentée reste une proposition ou un travail en cours; elle ne doit pas être comptée parmi les améliorations réalisées.
