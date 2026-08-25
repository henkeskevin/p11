# Cahier des charges fonctionnel — BottleNeck

**Version :** 1.1  
**Date :** 25 août 2026  
**Périmètre de données :** ventes du mois d’octobre et stock arrêté au 31 octobre  
**Destinataires :** direction générale, directions commerciale, e-commerce, finance et approvisionnement, équipe data, recruteurs évaluant le portfolio

## 1. Finalité

BottleNeck doit disposer d’une analyse reproductible et contrôlable de ses données ERP, Web et de leur table de liaison. Le produit attendu doit permettre de :

- fiabiliser le rapprochement des références sans masquer les défauts des sources ;
- calculer et vérifier les indicateurs commerciaux, de marge et de stock ;
- transformer les constats en décisions compréhensibles par un comité de direction ;
- démontrer, dans un portfolio, une utilisation mesurée et vérifiée de l’IA ;
- permettre à un tiers de reproduire l’analyse à partir du dépôt.

Le livrable de référence est le dépôt exécutable. Le notebook, les documents et les graphiques en sont des vues ; ils ne doivent pas contenir de logique métier divergente.

### 1.1 Pilotage et supports de la partie 1

Le pilotage détaillé est suivi dans le tableau Trello [P11 — Partie 1](https://trello.com/b/swp5d7fb/p11-partie-1). Il contient quatre listes (`Backlog`, `Todo`, `In progress`, `Done`) et douze cartes E01 à E12. À la date de mise à jour, les douze cartes sont dans `Done` et chacune renvoie à une preuve du dépôt.

Deux supports complètent ce cadrage :

- la note formelle `docs/Note_de_cadrage_P11_Partie_1.docx`, qui intègre le Trello, les preuves et le plan de restitution ;
- le PowerPoint `reports/P11_Partie_1_Explication_12_slides.pptx`, qui explique en douze slides le travail réalisé pendant la partie 1.

## 2. Contexte, sources et règles d’interprétation

### 2.1 Sources autorisées

| Source | Emplacement de travail | Rôle | Grain attendu |
|---|---|---|---|
| ERP | `data/raw/erp.xlsx` | Référence produit, prix, prix d’achat, stock, statut de vente Web | une ligne par `product_id` |
| Web | `data/raw/web.xlsx` | SKU, type de ligne, type de produit et ventes d’octobre | une ligne produit par `sku`, les pièces jointes étant une autre entité |
| Liaison | `data/raw/liaison.xlsx` | Correspondance ERP–Web | une ligne par `product_id`, au plus une clé Web non nulle |

Les fichiers racine d’origine sont conservés, avec leurs empreintes SHA-256, sous `archive/original/`. Les fichiers de `data/raw/` sont des copies de travail exactes et ne doivent pas être corrigés par le pipeline.

### 2.2 Conventions métier

- `price` est interprété comme un prix de vente TTC.
- `purchase_price` est interprété comme un coût d’achat HT.
- Le taux de TVA est une **hypothèse de 20 %**, à confirmer par la finance avant usage comptable.
- Le chiffre d’affaires et les unités vendues portent sur **octobre uniquement**.
- Le stock est un **instantané au 31 octobre**.
- L’année de cet octobre, l’horodatage des extractions et la date de situation certifiée ne figurent pas dans le contrat source fourni. Ils doivent être confirmés par les data owners ; la date 8 août 2026 de ce document n’est pas l’année de la période analysée.
- Une couverture en mois est le ratio `stock au 31 octobre / ventes d’octobre`. C’est un scénario au rythme d’octobre, non une prévision.
- Une valeur source invalide reste disponible dans la vue brute. Son exclusion d’un indicateur doit être explicite et traçable.
- Un prix statistiquement élevé est un signal de revue et non la preuve d’une erreur.

## 3. Parties prenantes et responsabilités

| Rôle | Responsabilité principale |
|---|---|
| Sponsor / CODIR | Valider l’usage décisionnel et arbitrer les priorités commerciales |
| Responsable data / analyste | Maintenir les contrats de données, exécuter l’analyse et publier les preuves |
| Data owner ERP | Corriger ou expliquer les prix, stocks et statuts ERP signalés |
| Data owner e-commerce | Corriger les SKU, ventes, types de lignes et écarts de publication Web |
| Référentiels / data steward | Résoudre les clés de liaison absentes ou obsolètes |
| Finance | Valider la TVA et la définition des indicateurs de marge et de valorisation |
| Approvisionnement | Qualifier les ruptures potentielles, stocks dormants et surstocks |

## 4. Exigences fonctionnelles

| ID | Exigence | Résultat attendu |
|---|---|---|
| F01 | Préserver l’état initial | Les huit fichiers initiaux sont copiés bit à bit dans `archive/original/` et référencés par taille et SHA-256. |
| F02 | Charger les sources de façon portable | La racine est détectée par `pyproject.toml`; toutes les entrées et sorties utilisent des chemins relatifs à cette racine. Les avertissements de lecture sont capturés, pas supprimés. |
| F03 | Appliquer des contrats de données | Les colonnes obligatoires, types numériques, clés vides, domaines, doublons et unicités non nulles sont contrôlés. Une violation structurelle empêchant une analyse sûre arrête le pipeline. |
| F04 | Auditer le rapprochement | Les jointures ERP–liaison et liaison–Web déclarent leur cardinalité avec `validate=...`; les correspondances, anti-jointures et clés nulles sont comptées séparément. |
| F05 | Ne pas corriger silencieusement | Les valeurs brutes sont conservées. Aucune valeur absolue, clé inventée, imputation implicite ou correction de statut ne doit être appliquée. Les valeurs non exploitables sont mises en quarantaine au niveau de l’indicateur concerné. |
| F06 | Qualifier la qualité des données | Chaque constat comporte règle, source, clé, colonne, valeur brute, gravité, catégorie, description et action. Les catégories sont `erreur_certaine`, `anomalie_probable` et `inhabituel_plausible`. |
| F07 | Calculer et réconcilier les ventes | Le CA TTC d’octobre et les unités sont calculés sur les lignes Web `post_type='product'` rapprochées, en excluant explicitement les valeurs invalides. Le CA est recalculé par une seconde méthode `Decimal`. |
| F08 | Mesurer la concentration commerciale | Les top 10, top 20 et top 100, le nombre de références nécessaire pour atteindre 80 % du CA et l’indice HHI sont produits. La conclusion ne doit pas présupposer un Pareto 20/80. |
| F09 | Analyser les prix avec prudence | Au moins deux méthodes sérieuses de détection sont comparées sur la couverture, le rappel sur contaminations contrôlées, la stabilité et le temps. La méthode retenue ne corrige ni n’exclut automatiquement un prix. |
| F10 | Calculer les marges sans ambiguïté | La marge brute HT, le taux de marque sur ventes et le taux de marge sur coût sont nommés séparément. Les calculs n’utilisent que les prix et coûts valides, sous hypothèse de TVA documentée. |
| F11 | Analyser le stock et la rotation | Les vues brutes signées et hors anomalie sont séparées. Les références sont segmentées en rupture potentielle, niveaux de couverture, surstock, stock sans vente et quarantaine. Une vente nulle donne une couverture indéfinie, pas zéro. |
| F12 | Étudier les relations quantitatives | Une matrice de corrélation de Spearman est produite sur les variables pertinentes, avec une mise en garde explicite contre toute conclusion causale. |
| F13 | Comparer les options avant décision | Pour les choix méthodologiques significatifs, les critères sont fixés dans le code, les alternatives sont exécutées sur des cas représentatifs, les résultats sont exportés et le choix est justifié. |
| F14 | Produire des sorties réutilisables | Le pipeline exporte les jeux traités, les audits, indicateurs, priorités, comparaisons et graphiques dans `data/processed/` et `reports/`, sans index CSV parasite. |
| F15 | Fournir un notebook exécuté et narratif | Le notebook appelle le même package que le pipeline, s’exécute depuis un noyau propre, présente les décisions avant le détail, affiche les preuves utiles et termine par limites et commandes de reproduction. |
| F16 | Adapter la restitution aux publics | Des synthèses distinctes sont fournies au CODIR et au recruteur. Une présentation CODIR courte est générée et contrôlée visuellement. Les graphiques donnent des titres interprétables, unités, périmètres temporels et avertissements adaptés à la décision. |
| F17 | Documenter l’amélioration continue et l’IA | Les problèmes, options, choix, implémentations, résultats, vérifications et limites sont consignés. L’usage de l’IA distingue ce qui a été proposé, contrôlé, retenu, modifié ou rejeté. |
| F18 | Automatiser les vérifications | Les invariants de conservation, contrats, jointures, absence de corrections silencieuses, indicateurs, expériences et livrables sont testés automatiquement. |
| F19 | Rendre le projet transmissible | Le README décrit l’installation, les commandes, l’architecture, les résultats, les limites et les artefacts. La documentation de gouvernance relie chaque exigence à une preuve. |

## 5. Exigences non fonctionnelles

| ID | Exigence | Critère mesurable |
|---|---|---|
| NF01 | Reproductibilité | Installation dans un environnement Python `>=3.12,<3.14`; une seule commande reconstruit les sorties et une autre exécute le notebook depuis un noyau propre. |
| NF02 | Intégrité des sources | Les empreintes des trois sources `data/raw/` correspondent aux valeurs attendues et sont vérifiées par test. |
| NF03 | Fiabilité | Toute la suite `pytest` doit réussir. Une clé non nulle dupliquée ou une colonne obligatoire absente provoque un échec explicite. |
| NF04 | Traçabilité | Chaque nombre de synthèse renvoie à `reports/tables/indicateurs_cles.json`, à un tableau exporté ou à un test ; chaque règle qualité conserve la valeur brute et la clé concernée. |
| NF05 | Cohérence | Le CA vectorisé et le recalcul `Decimal` diffèrent de 0,00 €. Notebook, synthèses et exports reprennent la même source de vérité. |
| NF06 | Performance raisonnable | Dans l’environnement de référence local, l’exécution propre du notebook doit rester inférieure à 60 secondes. Cette cible n’est pas une garantie sur un autre matériel. |
| NF07 | Lisibilité direction | Un graphique doit porter un message métier, une unité et le bon horizon temporel ; les tableaux détaillés restent accessibles séparément. |
| NF08 | Maintenabilité | La logique est isolée sous `src/bottleneck_analysis/`; notebook et scripts l’importent sans dupliquer les formules. Les dépendances runtime sont bornées dans `pyproject.toml`. |
| NF09 | Sobriété méthodologique | Une nouvelle dépendance ou méthode n’est conservée que si l’expérience démontre un gain pertinent. Le machine learning n’est pas une fin en soi. |
| NF10 | Transparence temporelle | Aucune annualisation, tendance ou prévision n’est présentée comme mesurée avec le seul mois d’octobre. L’année et l’horodatage non certifiés sont signalés, jamais déduits du nom ou de la date des fichiers. |
| NF11 | Honnêteté de l’IA | Aucun outil, essai, résultat ou validation ne peut être déclaré sans artefact ou commande reproductible. Toute proposition IA reste soumise aux tests et à une revue humaine. |

## 6. Critères d’acceptation

| ID | Vérification d’acceptation | Seuil ou valeur attendue | Preuve de référence |
|---|---|---|---|
| A01 | État initial préservé | 8 fichiers archivés et re-hachés sans différence | `archive/original/MANIFEST.md`, `src/bottleneck_analysis/deliverables.py`, `reports/tables/final_validation.json` |
| A02 | Exécution de référence documentée | L’échec strict du notebook original, son temps, sa cellule et sa cause sont enregistrés ; les essais diagnostiques sont distingués | `reports/tables/baseline_execution.json`, `docs/audit_initial.md` |
| A03 | Conservation des sources analytiques | SHA-256 ERP `1179ffa647941447f497026e9e0c16e0b49490ef791f02f541c74df1300b0771`, Web `24f3ecdb4ea97cbc027f18d6b16ea1c9a97ffcbb0c9c50a43b9348ca4b1c9d48`, liaison `b3af2411c59789b3cdcced6abad74c00ed4dbae74184215a89b00dfb8a682c02` | `tests/test_pipeline.py` |
| A04 | Rapprochement réconcilié | 825 ERP ↔ liaison ; 714 clés Web rapprochées ; 20 liens Web absents ; aucune ligne Web valide orpheline | `reports/tables/audit_jointures.csv` |
| A05 | Qualité explicitée | 165 constats : 7 erreurs certaines, 125 anomalies probables, 33 valeurs inhabituelles plausibles | `reports/tables/registre_qualite.csv`, `reports/tables/indicateurs_cles.json` |
| A06 | Ventes vérifiées | 143 680,10 € TTC, 5 751 unités, différence de réconciliation 0,00 € | `reports/tables/indicateurs_cles.json`, `tests/test_metrics.py` |
| A07 | Concentration calculée | top 20 = 11,02 % ; 435 références, soit 60,92 % du catalogue rapproché, atteignent 80 % ; HHI = 0,002217 | `reports/tables/indicateurs_cles.json`, `tests/test_metrics.py` |
| A08 | Marge définie | marge brute 44 660,65 € HT ; taux de marque pondéré 37,30 % ; une marge négative signalée | `reports/tables/indicateurs_cles.json`, `tests/test_metrics.py` |
| A09 | Stock différencié | vue ERP brute signée 17 811 unités / 298 555,76 € HT ; vue valide 17 822 / 298 627,66 € ; 22 ruptures potentielles ; 24 références à plus de 12 mois | `reports/tables/indicateurs_cles.json`, `tests/test_metrics.py` |
| A10 | Sélection Web expérimentée | au moins 2 options ; filtre `product` retenu ; `keep='first'` ajoute à tort 10 068,00 €, soit 7,01 % | `reports/tables/comparaison_selection_lignes_web.csv`, `tests/test_experiments.py` |
| A11 | Détection de prix expérimentée | au moins 2 options ; MAD brut détecte 20/20 injections, alerte 33 prix et garde une stabilité Jaccard > 0,90 | `reports/tables/comparaison_methodes_outliers.csv`, `tests/test_experiments.py` |
| A12 | Validation technique comparée | pandas natif et Pandera détectent 9/9 cas ; le choix runtime est justifié par localisation, coût et dépendances | `reports/tables/comparaison_validateurs.csv`, `experiments/compare_validators.py` |
| A13 | Suite automatisée saine | tous les tests collectés réussissent avec code retour 0 ; baseline de livraison : 17/17 réussis | `tests/`, `reports/tables/final_validation.json` |
| A14 | Notebook propre | 24 cellules dont 12 de code, 12 exécutées, aucune erreur ; temps < 60 s ; observation finale : 20,74 s | `scripts/execute_notebook.py`, `notebooks/BottleNeck_analyse_portfolio.ipynb`, `reports/tables/final_validation.json` |
| A15 | Sorties complètes | 2 CSV traités, tableaux d’audit et d’aide à la décision, 11 figures en PNG et SVG, soit 22 fichiers graphiques, et une présentation CODIR contrôlée de 12 slides | `src/bottleneck_analysis/reporting.py`, `reports/figures/`, `reports/BottleNeck_CODIR.pptx`, `reports/BottleNeck_CODIR.pptx.inspect.ndjson` |
| A16 | Documentation de gouvernance | cahier des charges, veille, matrice, backlog/planning/risques, registres IA et amélioration, synthèses CODIR/recruteur, limites et biais | `docs/` |
| A17 | Reproductibilité documentaire | les commandes README fonctionnent depuis la racine et n’imposent ni Colab ni chemin absolu | `README.md`, `src/bottleneck_analysis/config.py` |
| A18 | Limites visibles | octobre et 31 octobre sont mentionnés dans les indicateurs, le notebook, les graphiques et les synthèses ; aucune projection n’est affirmée ; l’année et l’horodatage restent explicitement à confirmer | `reports/tables/indicateurs_cles.json`, `docs/limites_biais.md`, `docs/backlog_planning_risques.md` |

La recette finale est acceptée lorsque A01 à A18 sont satisfaits simultanément. Si une valeur métier change après remplacement d’une source, les exports et les preuves doivent être régénérés ; les valeurs chiffrées ci-dessus constituent la baseline du jeu fourni, pas des constantes applicatives.

## 7. Hors périmètre

Les éléments suivants ne font pas partie de cette livraison :

- correction ou écriture en retour dans l’ERP, le site Web ou le fichier de liaison ;
- certification comptable ou fiscale des prix, achats, stocks, marges ou de la TVA ;
- prévision de demande, saisonnalité, annualisation du CA d’octobre ou estimation d’un stock « optimal » ;
- conclusion causale à partir des corrélations observées ;
- décision automatique de suppression, remise tarifaire, réassort ou déréférencement ;
- qualification automatique d’un prix élevé comme erreur ;
- déploiement temps réel, API, entrepôt de données, dashboard BI ou ordonnanceur de production ;
- enrichissement par des données clients, personnelles ou de marché non présentes dans le dépôt ;
- ajout de machine learning sans historique multi-périodes ni critère métier démontré ;
- garantie de performance sur un poste autre que l’environnement local mesuré.

## 8. Conditions d’usage des résultats

Les recommandations issues du stock et de la marge doivent être traitées comme une file de revue. Avant action, les propriétaires métier doivent confirmer : la validité des prix et coûts, la définition de la TVA, le statut des produits, les reliquats ou conventions de stock négatif, ainsi que la saisonnalité éventuelle. Toute diffusion doit conserver la mention « ventes d’octobre uniquement — stock au 31 octobre ».
