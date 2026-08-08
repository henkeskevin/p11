# Registre des expériences réalisées avec l'IA

**Version :** 1.0  
**Période couverte :** 8 août 2026  
**IA réellement utilisée :** Codex et ses sous-agents Codex.  
**Autres IA :** aucune. ImageGen n'a pas été utilisé.  
**Autres outils :** Python, pandas, NumPy, openpyxl, Matplotlib, nbclient, pytest, Pandera et un accès Internet limité à la consultation de sources officielles ou primaires. Ces outils ne sont pas présentés comme des IA.

## 1. Règles de preuve

L'IA a été utilisée pour explorer, proposer, comparer et rédiger. Elle n'est ni la source des données métier, ni une preuve d'exactitude. Une proposition n'est qualifiée de « retenue » que si elle est reliée à au moins un élément vérifiable : code exécuté, test, export mesuré, source primaire ou inspection du fichier concerné.

Les formulations de prompts ci-dessous sont des résumés fidèles des axes donnés aux agents; elles ne prétendent pas reproduire les instructions système internes. Toute durée mentionnée est une observation locale indicative, dépendante de la machine et de la charge. Les chronométrages des expériences ne sont pas figés dans ce registre : la dernière mesure régénérée prévaut dans `reports/tables/comparaison_validateurs.csv` et `reports/tables/comparaison_methodes_outliers.csv`.

Statuts employés :

- **conservé** : proposition adoptée sans changement substantiel;
- **modifié** : idée utile, mais périmètre ou implémentation corrigé après vérification;
- **rejeté** : proposition non justifiée ou contredite par les preuves;
- **en cours** : production non finalisée et donc non revendiquée comme livrée.

## 2. Vue synthétique

| ID | Agent ou axe Codex | Variante de prompt / question testée | Résultat de la proposition | Statut |
|---|---|---|---|---|
| IA-01 | Agent principal | Inspecter, exécuter, améliorer, tester et documenter sans surdévelopper. | Découpage entre baseline, audit indépendant, code, expériences et livrables. | Conservé |
| IA-02 | `baseline_notebook` | Exécution stricte, puis neutralisation diagnostique séparée. | Baseline stricte en échec; défauts suivants localisés sans confondre diagnostic et exécution valide. | Conservé avec séparation stricte |
| IA-03 | `data_audit` | Audit pandas, puis seconde chaîne openpyxl + dictionnaires + Decimal. | Rapprochement et CA vérifiés indépendamment; problèmes de clés et de corrections silencieuses confirmés. | Conservé |
| IA-04 | `veille_sources` | Sources officielles; comparer pandas/Pandera/GX et IQR/z/MAD, sans imposer un outil. | Options sérieuses identifiées, puis décisions soumises aux expériences locales. | Modifié après mesures |
| IA-05 | Agent principal | Transformer le notebook en pipeline testable; préserver le nom métier sans collision Python. | Paquet `bottleneck_analysis`, scripts, tests et exports reproductibles. | Conservé |
| IA-06 | Agent principal | Tester plusieurs façons de sélectionner les lignes Web. | Filtre sémantique `post_type == "product"` retenu; ordre et double comptage rejetés. | Conservé/rejeté selon option |
| IA-07 | Agent principal | Comparer quatre détecteurs de prix sur cas réels et contaminés. | MAD brute retenue comme signal de revue; aucune correction automatique. | Modifié et conservé |
| IA-08 | Agent principal | Comparer validation pandas native et Pandera sur neuf mutations. | pandas natif retenu au runtime; Pandera facultatif; Great Expectations rejeté par revue d'architecture, non benchmarké. | Modifié |
| IA-09 | `deck_audit` | Inventorier les 18 slides et proposer une restitution CODIR de 10 à 12 slides sans modifier la source. | Carte de gabarit conservée; présentation finale de 12 slides livrée et contrôlée. | Conservé et finalisé |
| IA-10 | `docs_governance` | Produire exigences, matrice de preuves, backlog/planning/risques. | Lot rédactionnel séparé, vérifié contre les artefacts locaux par l'agent principal. | En cours au moment de cette entrée |
| IA-11 | `docs_research` | Produire veille, registre IA et registre d'améliorations à partir des preuves et sources primaires. | Les trois présents documents, sans extrapolation d'usage d'une autre IA. | Conservé |
| IA-12 | `docs_summaries` | Adapter les mêmes résultats au CODIR et au recruteur, sans changer les chiffres. | Deux synthèses aux niveaux de langage distincts. | Conservé après contrôle croisé |

## 3. Journal détaillé

### IA-01 — Cadrage général et découpage de la mission

**Prompt ou axe.** Travailler directement dans le dépôt; préserver l'initial; établir une baseline; proposer plusieurs options; implémenter seulement ce qui apporte une amélioration démontrable; exécuter les tests et le notebook; produire des livrables utiles.

**Propositions de Codex.** Séparer l'exploration de l'implémentation, paralléliser les audits indépendants, sortir la logique métier du notebook, créer des expériences reproductibles et conserver un registre de décisions.

**Vérification.** Chaque lot a été rapproché du dépôt avant intégration. Les fichiers de données n'ont pas été réécrits; l'archive a été re-hachée; le chemin final a été soumis à pytest et à une exécution de notebook propre.

**Décision.** Découpage conservé. La consigne « utiliser l'IA » a été interprétée comme une obligation de critique et de preuve, pas comme une obligation d'ajouter du machine learning ou une autre IA.

**Gain observé.** Exploration simultanée de la baseline, des sources, des données, de la présentation et de la gouvernance; contre-vérification entre agents spécialisés.

**Limite.** Plusieurs agents peuvent répéter une hypothèse ou lire le même artefact. L'agent principal reste responsable de résoudre les contradictions et de ne pas assimiler un consensus d'agents à une preuve.

### IA-02 — Baseline stricte puis diagnostic contrôlé

**Agent.** `baseline_notebook`, en lecture seule pour l'original.

**Variante A — stricte.** Exécuter le notebook archivé tel quel avec :

```powershell
.\.venv\Scripts\python.exe scripts\execute_notebook.py archive\original\Henkes_Kevin_1_notebook_012026.ipynb --output .tmp\baseline-executed.ipynb
```

**Résultat.** Code de sortie 1 avec `CellExecutionError` sur `ModuleNotFoundError: No module named 'google.colab'` dès la première cellule de code. La durée historique, purement indicative et dépendante de la machine, reste consignée dans `docs/audit_initial.md`.

**Variante B — diagnostique.** Neutraliser uniquement le montage Colab, substituer des chemins locaux et poursuivre pour découvrir les défauts suivants sans modifier l'archive.

**Propositions et constats.** Le diagnostic a rencontré le chemin absolu `/content/drive/MyDrive/p6/`, puis un import seaborn non déclaré après avoir parcouru 72 cellules de code. Les passages diagnostiques froid et chaud ont produit une empreinte finale identique. Leurs durées locales sont documentées dans `docs/audit_initial.md`, mais ne constituent ni une référence de performance ni un seuil figé.

**Vérification.** Inspection JSON du notebook : 107 cellules, dont 74 de code; 74/74 ont `execution_count=None`, alors que des sorties historiques sont stockées. L'original reste sous `archive/original/`.

**Décision.** La variante stricte est la seule baseline d'exécution. La variante diagnostique est conservée comme outil d'audit, jamais présentée comme une exécution réussie de l'original.

**Gain observé.** Le premier blocage reproductible est distingué des défauts qui auraient été masqués par ce blocage.

**Limite.** Toute neutralisation change le programme exécuté. Ses durées n'évaluent donc pas fidèlement une exécution normale de l'original.

### IA-03 — Audit des données par deux chaînes indépendantes

**Agent.** `data_audit`.

**Variante A.** Explorer avec pandas les trois classeurs, les clés, les cardinalités, les signes et les indicateurs.

**Variante B.** Recalculer le rapprochement et le CA avec `openpyxl`, des dictionnaires Python et `Decimal`, sans réutiliser les agrégations pandas du pipeline.

**Propositions.** Isoler les valeurs négatives au lieu d'appliquer `abs()`, distinguer les clés nulles des doublons, auditer les anti-jointures et vérifier le CA au centime.

**Vérification.** Les deux chaînes convergent vers **714** produits rapprochés, **5 751** unités et **143 680,10 € TTC** de CA d'octobre. La différence de réconciliation est **0,00 €**. Les 91 identifiants Web absents et les 20 liens sans produit Web restent visibles.

**Décision.** Propositions conservées et intégrées dans les contrats, les exports et les tests. La seconde chaîne ne réutilise pas la fonction de calcul principale.

**Gain observé.** Réduction du risque d'une erreur commune à un seul enchaînement pandas; découverte de corrections silencieuses que le notebook initial rendait invisibles.

**Limite.** Deux implémentations cohérentes peuvent reproduire la même mauvaise hypothèse métier, par exemple la TVA à 20 %. Les conventions doivent encore être confirmées par Finance et les responsables des sources.

### IA-04 — Veille officielle et options technologiques

**Agent.** `veille_sources`.

**Prompt ou axe.** Rechercher uniquement des sources officielles ou primaires et dater les versions; comparer des options sérieuses au contexte plutôt que recommander l'outil le plus riche.

**Axes demandés.** pandas/Pandera/Great Expectations; IQR, z-score, MAD et options robustes; règles de visualisation et conditions minimales d'une prévision.

**Propositions.** Tester Pandera contre des contrôles natifs; examiner Great Expectations; comparer plusieurs règles d'outliers; envisager medcouple, LOF/Isolation Forest, dashboard et méthodes temporelles.

**Vérification.** Les recommandations qui pouvaient être testées dans le périmètre l'ont été par code (`compare_validators.py`, `compare_web_selection_methods`, `compare_outlier_methods`). Les autres ont été confrontées à leurs prérequis officiels et au périmètre réel.

**Décision.** Contrôles pandas natifs et MAD brute conservés. Pandera réduit au rôle facultatif. Great Expectations, medcouple, détecteurs ML, dashboard et prévision rejetés à ce stade. Les rejets de veille non benchmarkés sont explicitement qualifiés de décisions d'architecture, pas de résultats expérimentaux.

**Gain observé.** Les choix du dépôt sont reliés à des références datées sans ajouter mécaniquement de dépendances.

**Limite.** La veille est un instantané au 8 août 2026; versions et recommandations peuvent évoluer.

### IA-05 — Architecture du code et risque de collision de paquet

**Agent.** Agent principal Codex.

**Prompt ou axe.** Sortir la logique cachée du notebook, rendre les chemins relatifs et préserver l'identité BottleNeck sans masquer une dépendance Python.

**Options proposées.** Garder toute la logique dans le notebook; créer un module `bottleneck`; ou créer une distribution distincte et un module sans collision.

**Vérification.** La documentation pandas identifie `bottleneck` comme dépendance optionnelle de performance. Un test d'import local a confirmé que `bottleneck_analysis` résout vers `src/bottleneck_analysis/` et qu'aucun module projet nommé `bottleneck` n'est importé.

**Décision.** Distribution `bottleneck-portfolio`, module `bottleneck_analysis`, scripts fins et notebook consommateur du même pipeline. Le nom importable `bottleneck` est rejeté.

**Gain observé.** Code testable et réutilisable sans dépendre de l'ordre d'exécution des cellules; réduction d'un risque subtil de résolution d'import.

**Limite.** Le risque pourrait être réintroduit plus tard par un fichier `bottleneck.py`; aucun outil ne remplace une revue des nouveaux noms de modules.

### IA-06 — Expérience de sélection des lignes Web

**Prompt ou axe.** Ne pas choisir arbitrairement entre lignes `product`, pièces jointes, première/dernière occurrence ou somme; fixer d'abord les critères métier.

**Critères préalables.** Une ligne par SKU, choix stable à l'ordre, type représentant l'entité vendue et absence de double comptage.

**Propositions testées.** Filtre `post_type == "product"`; filtre `attachment`; dédoublonnage première ligne; dernière ligne; somme de toutes les lignes.

**Vérification par code.** `src/bottleneck_analysis/experiments.py`, `reports/tables/comparaison_selection_lignes_web.csv` et `test_web_selection_experiment_proves_order_risk`.

**Résultats.** Le filtre produit donne **143 680,10 €**. La pièce jointe et `keep="first"` donnent **153 748,10 €**, soit **+10 068,00 € (+7,01 %)**. `keep="last"` tombe ici sur le même total que le filtre produit, mais reste dépendant de l'ordre. La somme donne **297 428,20 €**, soit **+107,01 %**.

**Décision.** Filtre sémantique conservé; quatre autres options rejetées.

**Gain observé.** Élimination d'un résultat accidentel dépendant de l'ordre et d'un double comptage majeur.

**Limite.** La règle suppose que `post_type="product"` reste la définition source de l'entité vendue; un changement d'export devra déclencher une nouvelle validation.

### IA-07 — Expérience de prix inhabituels

**Prompt ou axe.** Comparer des méthodes simples et robustes sur des cas représentatifs, avec critères définis avant l'observation du résultat.

**Propositions testées.** IQR brut, z-score classique, z-score modifié MAD sur prix brut, z-score modifié MAD sur logarithme. Graine 42; 20 prix centraux multipliés par six; 30 répétitions de chronométrage.

**Vérification par code.** `src/bottleneck_analysis/outliers.py`, `reports/tables/comparaison_methodes_outliers.csv` et `test_mad_wins_predefined_outlier_experiment`. Le CSV est régénéré par la recette complète et constitue la source courante pour les temps indicatifs; aucun temps n'est figé dans ce registre.

**Résultats.** MAD brute : **33** alertes (**4,62 %**), rappel injecté **100 %**, Jaccard **0,9091**. IQR : 31 alertes, rappel 95 %, Jaccard 0,8387. Z-score : rappel 55 %. MAD logarithmique : rappel nul.

**Décision.** La proposition « détecter des anomalies » a été modifiée en « produire un signal de revue ». MAD brute conservée; aucune suppression ni correction automatisée. LOF, Isolation Forest et boîte ajustée non implémentés faute de bénéfice démontré dans ce périmètre.

**Gain observé.** Choix fondé sur une expérience reproductible plutôt que sur l'habitude du notebook initial.

**Limite.** Les cas injectés sont synthétiques. Le rappel mesuré ne constitue pas une précision métier, car aucune vérité terrain des vins premium n'est disponible.

### IA-08 — Expérience pandas natif contre Pandera

**Prompt ou axe.** Comparer au moins deux validateurs sur les mêmes erreurs, avec pondération définie dans le script.

**Propositions testées.** Contrôles pandas explicites et schéma Pandera `lazy=True`. Les neuf mutations et les critères de détection, localisation, non-mutation, intégration pytest, temps et complexité sont communs.

**Vérification par code.** `experiments/compare_validators.py` et `reports/tables/comparaison_validateurs.csv`.

**Résultats.** Les deux détectent 9/9 cas et ne modifient pas l'entrée. pandas localise 9/9 contre 7/9 pour Pandera dans ce protocole. Ces résultats stables, les diagnostics métier et la dépendance minimale justifient le choix; aucun ratio ni temps de benchmark n'est figé ici.

**Décision.** pandas natif conservé dans le pipeline; Pandera modifié en option de développement. Great Expectations rejeté après revue de ses prérequis, sans fausse affirmation de benchmark.

**Gain observé.** Dépendances d'exécution minimales et messages directement alignés sur les actions métier.

**Limite.** Neuf cas synthétiques ne couvrent pas l'évolution complète d'un schéma réel. Les temps sont indicatifs, dépendants de la machine et régénérés dans `reports/tables/comparaison_validateurs.csv`; Pandera pourrait devenir préférable si le nombre de tables, d'équipes ou de backends augmente.

### IA-09 — Audit de la présentation

**Agent.** `deck_audit`.

**Prompt ou axe.** Inventorier la présentation initiale de 18 slides, extraire une carte de gabarit et proposer une version CODIR de 10 à 12 slides avec les identifiants produits exacts, sans modifier la source pendant l'audit.

**Propositions.** Raccourcir la narration, séparer décisions et limites, remplacer les anciens chiffres par les exports vérifiés et réutiliser la structure graphique lorsqu'elle reste lisible.

**Vérification.** Inspection du paquet PowerPoint et rendu des 18 slides sources dans `.tmp/presentation/template-inspect/`; présentation originale préservée sous `archive/original/` avec SHA-256. Le livrable final `reports/BottleNeck_CODIR.pptx` contient 12 slides, toutes inspectées visuellement une par une. Le contrôle `slides_test` est **PASS**, sans débordement, et le contrôle de fidélité au template est **PASS**, avec **0 issue**.

**Décision.** Carte du gabarit conservée et proposition concrétisée en une présentation CODIR finale de 12 slides, livrée dans `reports/BottleNeck_CODIR.pptx`. Le statut finalisé n'a été attribué qu'après le rendu et les contrôles visuels réussis.

**Gain observé.** Réutilisation des conventions visuelles sans recopier les erreurs analytiques de l'ancien support.

**Limite.** Les contrôles certifient la mise en page observée, l'absence de débordement et la fidélité au template. Ils ne remplacent pas la validation métier des hypothèses ni l'actualisation des chiffres lors d'une nouvelle période.

### IA-10 à IA-12 — Lots documentaires spécialisés

**Agents.** `docs_governance`, `docs_research`, `docs_summaries`.

**Prompts ou axes.** Séparer respectivement : exigences/matrice/backlog/risques; veille et registres; synthèses CODIR/recruteur/limites. Tous les lots doivent pointer vers des preuves réelles et ne pas créer de résultats nouveaux.

**Propositions.** Adapter la profondeur et le vocabulaire au lecteur, mutualiser les chiffres via les exports et signaler les éléments encore en cours.

**Vérification.** Contrôle des nombres contre `indicateurs_cles.json` et les CSV de rapports; contrôle des statuts contre les fichiers présents; recherche de liens relatifs et de revendications sans preuve.

**Décision.** Spécialisation conservée, mais les documents ne deviennent pas des sources primaires. En cas d'écart, le code et les exports régénérés priment. Les synthèses CODIR et recruteur ont été conservées après contrôle croisé; la présentation n'a été qualifiée de terminée qu'après présence du fichier final, inspection des 12 slides et contrôles automatiques réussis.

**Gain observé.** Documentation plus lisible pour plusieurs publics sans dupliquer la logique de calcul.

**Limite.** Le texte peut devenir périmé si les exports sont régénérés après sa rédaction. Les documents doivent être revus avec chaque nouvelle période.

## 4. Recommandations de l'IA rejetées ou fortement réduites

| Proposition explorée | Motif du rejet ou de la réduction | Preuve ou règle de décision |
|---|---|---|
| Ajouter du machine learning pour les outliers | Pas de vérité terrain, problème univarié et solution robuste simple déjà concluante. | Expérience quatre méthodes; rappel et stabilité de la MAD |
| Corriger automatiquement les valeurs négatives | Détruit l'information sur l'erreur source et peut créer un faux fait métier. | Tests de non-correction silencieuse; registre qualité |
| Inventer une clé pour les SKU nuls | Peut créer des rapprochements artificiels, aggravés par l'appariement null-null de pandas. | Documentation pandas et test des SKU nuls |
| Dédupliquer le Web par première ou dernière ligne | Le résultat dépend de l'ordre; la dernière ligne ne réussit que par accident sur cet export. | Comparaison de sélection Web |
| Sommer produit et pièce jointe | Double comptage de 107,01 % par rapport au filtre métier. | Comparaison de sélection Web |
| Remplacer le pipeline par Pandera | Même détection, localisation inférieure dans ce protocole et dépendance supplémentaire. | Comparaison des validateurs |
| Ajouter Great Expectations | Architecture trop lourde pour trois fichiers locaux; option non benchmarkée. | Revue de la documentation 1.20.0 |
| Construire un dashboard | Données non récurrentes et absence de besoin interactif établi. | Guide officiel dashboards + périmètre temporel |
| Produire une prévision annuelle | Un seul mois, aucun cycle ni test temporel possible. | Limites des données et références temporelles |
| Présenter une corrélation comme causalité | Une association d'octobre ne démontre ni effet prix ni stabilité. | Analyse Spearman et limites du notebook |

## 5. Validation globale des productions assistées par l'IA

À l'état contrôlé du 8 août 2026 :

- `pytest` : **17 tests réussis**; la durée d'un passage n'est pas un critère contractuel;
- pipeline : **714 lignes analytiques**, **143 680,10 € TTC**, **5 751 unités**, **165 constats qualité**, **22 fichiers graphiques** correspondant à onze figures en deux formats;
- notebook : **24 cellules**, dont **12 cellules de code exécutées**, exécution propre et aucune sortie d'erreur; sa durée varie avec la machine et le rendu;
- CA : second calcul indépendant avec écart de **0,00 €**;
- expériences : résultats exportés pour la sélection Web, les outliers et les validateurs;
- recette intégrée : **5/5 commandes** et **7/7 contrôles** réussis dans `reports/tables/final_validation.json`.

Ces validations certifient l'état testé et les contrats couverts, pas l'exactitude des données sources ni une aptitude à la production à grande échelle. Les problèmes métier signalés restent à résoudre par leurs propriétaires.
