# Veille métier et technologique — BottleNeck

**Version :** 1.0  
**État de la veille :** 8 août 2026  
**Périmètre :** qualité et rapprochement de données, validation, détection de prix inhabituels, visualisation décisionnelle et prévision.  
**Règle de sélection :** priorité aux sources officielles, aux documentations des éditeurs et aux publications scientifiques primaires. Les pages ont été consultées le 8 août 2026.

## 1. Conséquences immédiates pour BottleNeck

Cette veille n'est pas une liste d'outils à ajouter. Elle sert à justifier des choix vérifiables sur le jeu de données réel.

| Sujet | Décision BottleNeck | Statut | Preuve locale |
|---|---|---|---|
| Qualité des données | Mesurer la complétude, l'unicité, la cohérence, l'actualité, la validité et l'exactitude; journaliser les problèmes au lieu de les masquer. | Retenu | `reports/tables/registre_qualite.csv`, `audit_jointures.csv`, `indicateurs_cles.json` |
| Jointures | Écarter les clés nulles avant rapprochement, certifier la cardinalité et exporter les non-correspondances. | Retenu | `src/bottleneck_analysis/pipeline.py`, tests de jointure et de SKU nul |
| Validation | Garder des contrôles pandas explicites dans le pipeline; conserver Pandera comme contrôle additionnel facultatif. | Retenu après expérience | `reports/tables/comparaison_validateurs.csv` |
| Great Expectations | Ne pas introduire son contexte, ses assets, suites et checkpoints dans un projet local à trois sources. | Rejeté pour ce périmètre | Revue de l'architecture officielle; aucune prétention de benchmark local |
| Prix inhabituels | Utiliser le z-score modifié fondé sur la MAD pour prioriser une revue humaine; ne supprimer ni corriger automatiquement un prix. | Retenu après expérience | `reports/tables/comparaison_methodes_outliers.csv` |
| Détection multivariée/ML | Ne pas ajouter LOF ou Isolation Forest sans variables explicatives, labels ou besoin métier supplémentaire. | Rejeté pour ce périmètre | Complexité non justifiée face à l'expérience univariée déjà concluante |
| Restitution | Fournir un notebook narratif et onze graphiques statiques en PNG et SVG, accompagnés de tables. | Retenu | `notebooks/`, `reports/figures/`, `reports/tables/` |
| Dashboard interactif | Ne pas construire un dashboard pour un instantané d'octobre non alimenté régulièrement. | Rejeté à ce stade | Absence de flux fréquent et de besoin d'exploration récurrent documenté |
| Prévision | Limiter l'analyse à octobre et aux scénarios « au rythme d'octobre »; ne pas produire de prévision annuelle. | Rejeté avec les données actuelles | Un mois de ventes et un stock au 31 octobre |

## 2. Qualité des données : traiter la cause et rendre l'incertitude visible

Le [Government Data Quality Framework](https://www.gov.uk/government/publications/the-government-data-quality-framework/the-government-data-quality-framework), publié le **3 décembre 2020**, définit la qualité comme l'aptitude à l'usage et retient six dimensions centrales : complétude, unicité, cohérence, actualité, validité et exactitude. Il recommande une gestion continue sur tout le cycle de vie, la documentation des problèmes et le traitement à la source plutôt que le contournement.

Le guide officiel [Implementing a data quality action plan](https://www.gov.uk/government/publications/implement-a-data-quality-action-plan/data-quality-action-plan-implementation-guide), mis à jour le **16 avril 2026**, propose une boucle en sept étapes : identifier les données critiques et les règles, mesurer, prioriser, rechercher les causes, agir, rendre compte, puis mesurer à nouveau.

### Application au projet

| Dimension | Mesure ou contrôle BottleNeck | Limite explicitée |
|---|---|---|
| Complétude | 91 identifiants Web manquants dans la liaison; 20 identifiants renseignés sans produit Web correspondant; 2 produits sans SKU. | Une absence de correspondance ne signifie pas une vente nulle. |
| Unicité | Unicité exigée sur `product_id`, `id_web` non nul et `sku` non nul; échec rapide en cas de doublon. | Les valeurs nulles sont évaluées séparément de l'unicité. |
| Cohérence | Quantité confrontée à `stock_status`; `onsale_web` confronté à la présence et aux ventes Web. | Une incohérence est une anomalie à confirmer, pas nécessairement une erreur certaine. |
| Actualité | Ventes limitées à octobre et stock daté du 31 octobre dans chaque restitution. | Aucune tendance ni saisonnalité ne peut être estimée. |
| Validité | Domaines, types, prix et coûts strictement positifs, ventes non négatives. | Les valeurs invalides sont conservées dans la source et mises en quarantaine dans les agrégats concernés. |
| Exactitude | CA recalculé par une seconde chaîne `openpyxl` + dictionnaires + `Decimal`. | L'accord entre deux calculs ne remplace pas une confirmation par les systèmes sources. |

**Décision.** Le registre qualité à trois catégories — `erreur_certaine`, `anomalie_probable`, `inhabituel_plausible` — est retenu. Il évite de traiter de la même manière un prix négatif, une incohérence de statut et un vin premium. La prochaine boucle métier doit attribuer un responsable et une résolution aux problèmes de source; le pipeline ne doit pas inventer cette résolution.

## 3. pandas, jointures et dépendances

### 3.1 Sémantique des clés nulles et cardinalités

La documentation officielle de [`pandas.merge`](https://pandas.pydata.org/docs/reference/api/pandas.merge.html), version **3.0.5**, avertit que deux clés nulles sont appariées entre elles, contrairement au comportement SQL habituel. Elle documente aussi `validate="one_to_one"`, `"one_to_many"` et `"many_to_one"`, ainsi que `indicator` pour distinguer `left_only`, `right_only` et `both`.

**Options examinées.** Laisser pandas apparier les valeurs nulles; remplacer les clés absentes par un identifiant artificiel; ou isoler les clés nulles puis certifier les seules clés réelles.

**Décision.** La troisième option est retenue. Les deux produits sans SKU restent en quarantaine et aucun `id_inconnu` n'est créé. Les jointures utilisent `validate` et les anti-correspondances sont exportées. Cette règle est vérifiée par `test_null_skus_are_not_matched_or_invented` et `test_join_audit_reconciles_all_rows`.

### 3.2 Version pandas et collision du nom `bottleneck`

La version courante publiée sur [PyPI, pandas 3.0.5](https://pypi.org/project/pandas/3.0.5/), date du **22 juillet 2026**. PyPI indique que la version **3.0.4**, publiée puis retirée le 28 juin 2026, a été retirée en raison de défauts de segmentation liés aux dates. Le projet épingle **pandas 3.0.3** dans `pyproject.toml`, conformément à l'environnement local audité. Une montée vers 3.0.5 doit donc être explicite et rejouer toute la recette ; l'absence de lockfile avec empreintes laisse par ailleurs les dépendances transitives susceptibles d'évoluer.

La [documentation d'installation de pandas](https://pandas.pydata.org/docs/getting_started/install.html#performance-dependencies-recommended) répertorie par ailleurs `bottleneck` comme dépendance de performance optionnelle. Un module local appelé `bottleneck.py` ou un paquet local `bottleneck` pourrait donc masquer ce paquet tiers lors de la résolution des imports.

**Décision.** Le nom métier reste BottleNeck, mais la distribution est `bottleneck-portfolio` et le module importable est `bottleneck_analysis`. L'option de créer un module Python nommé `bottleneck` est rejetée. Le contrôle effectué dans l'environnement local confirme que `bottleneck_analysis` pointe vers `src/bottleneck_analysis/` et qu'aucun faux paquet local `bottleneck` n'est importé.

**Point de veille.** Recréer périodiquement l'environnement, contrôler la version effectivement résolue et envisager un verrouillage avec empreintes si le projet devient un livrable de production.

## 4. Contrats de données : pandas natif, Pandera ou Great Expectations

### Sources et versions

- [Pandera — DataFrame Schemas](https://pandera.readthedocs.io/en/stable/dataframe_schemas.html) décrit les schémas de colonnes, les contraintes d'unicité, les contrôles de DataFrame et la collecte des erreurs avec `lazy=True`. La version publiée au moment de la veille est [**0.32.1**, 29 juin 2026](https://pypi.org/project/pandera/).
- [Great Expectations — Validation Definition](https://docs.greatexpectations.io/docs/core/run_validations/create_a_validation_definition/) décrit, en version **1.20.0**, une définition reliant un batch à une suite d'attentes, éventuellement orchestrée par un checkpoint. La version [**1.20.0** a été publiée le 7 août 2026](https://pypi.org/project/great-expectations/).

### Comparaison réellement exécutée

Pandera et des contrôles pandas natifs ont été comparés sur neuf mutations définies avant le chronométrage : colonne absente, type de clé erroné, clé nulle, doublon, prix négatif, coût négatif, stock négatif, indicateur Web hors domaine et incohérence quantité/statut.

| Critère | pandas natif | Pandera 0.32.x |
|---|---:|---:|
| Cas détectés | 9/9 | 9/9 |
| Cas localisés sur une colonne | 9/9 | 7/9 |
| Entrées laissées inchangées | Oui | Oui |
| Temps médian local pour 9 cas | Mesure courante dans le CSV | Mesure courante dans le CSV |
| Lignes d'implémentation mesurées | 36 | 36 |
| Score pondéré prédéfini | Voir le CSV | Voir le CSV |

Les temps et le score qui en dépend varient d'un passage à l'autre : ils sont propres à cette machine et ne constituent pas un contrat de performance. Le détail du dernier passage est dans `experiments/compare_validators.py` et `reports/tables/comparaison_validateurs.csv`.

**Décision.** Les contrôles pandas natifs sont retenus dans le chemin courant : ils produisent des diagnostics adaptés au métier, n'ajoutent pas de dépendance d'exécution et ont mieux localisé les deux contrôles globaux dans ce test. Pandera reste dans les dépendances de développement et peut être ajouté comme seconde barrière à une interface de données plus large.

**Option rejetée sans benchmark local.** Great Expectations est documenté mais n'a pas été installé ni comparé en temps d'exécution. Son modèle `Data Context` + source/asset/batch + suite + définition est pertinent pour plusieurs pipelines et un historique de validations; il est disproportionné ici face à trois fichiers locaux et une suite pytest compacte. Il pourra être réévalué si BottleNeck devient un flux récurrent multi-équipe. Cette décision d'architecture ne doit pas être présentée comme une victoire empirique contre Great Expectations.

## 5. Prix inhabituels : comparer les signaux, ne pas fabriquer des erreurs

### Références méthodologiques

- Le [NIST e-Handbook — IQR et boxplot](https://www.itl.nist.gov/div898/handbook/prc/section1/prc16.htm) définit les bornes internes `Q1 - 1,5 IQR` et `Q3 + 1,5 IQR` et rappelle qu'une valeur extrême peut contenir une information importante.
- Le [NIST e-Handbook — modified z-score](https://itl.nist.gov/div898/handbook/eda/section3/eda35h.htm) donne `0,6745 × (x - médiane) / MAD` et le seuil absolu **3,5** proposé par Iglewicz et Hoaglin. Il distingue étiquetage, accommodation robuste et identification formelle.
- La documentation [SciPy 1.17.0 — `median_abs_deviation`](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.stats.median_abs_deviation.html) confirme que la MAD est moins sensible aux extrêmes que l'écart-type. BottleNeck réimplémente la formule simple avec pandas/NumPy afin de ne pas ajouter SciPy au runtime.
- L'article primaire de Hubert et Vandervieren, [*An adjusted boxplot for skewed distributions*](https://doi.org/10.1016/j.csda.2007.11.008), publié en **2008**, propose une boîte ajustée par le medcouple pour les distributions asymétriques. [`statsmodels.stats.stattools.medcouple`](https://www.statsmodels.org/stable/generated/statsmodels.stats.stattools.medcouple.html), documentation **0.14.6**, fournit cet estimateur mais signale une allocation mémoire en O(n²).
- L'exemple officiel [scikit-learn 1.9.0 — Evaluation of outlier detection estimators](https://scikit-learn.org/stable/auto_examples/miscellaneous/plot_outlier_detection_bench.html) montre que LOF et Isolation Forest se comportent différemment selon les jeux de données et sont sensibles au prétraitement et aux hyperparamètres.

### Expérience BottleNeck

Quatre méthodes univariées ont été exécutées sur les prix positifs rapprochés : IQR brut, z-score classique brut, MAD brute et MAD après logarithme. Vingt prix pris dans les 50 % centraux ont été multipliés par six, avec graine 42. Les critères fixés avant résultat étaient le rappel des cas injectés, moins de 5 % d'alertes initiales, la stabilité Jaccard des alertes non injectées et le temps d'exécution.

| Méthode | Alertes initiales | Rappel injecté | Stabilité Jaccard | Décision |
|---|---:|---:|---:|---|
| IQR brut | 31 (4,34 %) | 95 % | 0,8387 | Rejeté face à la MAD sur les critères fixés |
| z-score classique | 13 (1,82 %) | 55 % | 0,4615 | Rejeté, trop sensible à la moyenne et à l'écart-type |
| MAD brute | 33 (4,62 %) | 100 % | 0,9091 | Retenu |
| MAD logarithmique | 0 | 0 % | 1,0000 | Rejeté : stabilité triviale sans détection |

**Interprétation.** Le signal MAD désigne 33 prix à examiner; il ne prouve pas 33 erreurs. Les prix élevés restent classés `inhabituel_plausible`, aucune ligne n'est supprimée, et les valeurs non positives sont traitées séparément comme erreurs de validité.

**Options non retenues.** L'ajustement par medcouple est méthodologiquement pertinent pour l'asymétrie, mais il ajouterait une dépendance et une règle plus difficile à expliquer sans bénéfice mesuré ici. LOF et Isolation Forest ajouteraient prétraitement, hyperparamètres et besoin de vérité terrain pour un problème actuellement univarié. Ils ne seront testés que si de nouvelles variables fiables permettent une détection multivariée et si le coût des faux positifs est défini.

**Limite de l'expérience.** Les anomalies injectées évaluent une sensibilité contrôlée, pas la vérité métier. Un œnologue, les achats ou le référentiel fournisseur doivent confirmer les prix réellement erronés.

## 6. Restitution à un public de direction

Le guide [Data visualisation: building and managing dashboards](https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-building-and-managing-dashboards/), publié le **6 février 2026**, recommande de justifier un dashboard par un besoin utilisateur, des mises à jour fréquentes et automatisables et un usage interactif récurrent. Il souligne aussi le besoin d'un format alternatif accessible.

La checklist officielle [Accessible charts: a checklist of the basics](https://analysisfunction.civilservice.gov.uk/policy-store/charts-a-checklist/), publiée le **2 mai 2023**, recommande notamment de réduire le bruit graphique, hiérarchiser les barres, expliciter période et source, fournir une alternative textuelle et publier du SVG. Le manuel ONS [Using colours in charts](https://service-manual.ons.gov.uk/data-visualisation/colours/using-colours-in-charts) recommande contraste, cohérence d'une figure à l'autre et usage limité de la couleur pour mettre en évidence l'information.

**Décision.** Un dashboard est rejeté pour l'instant : les données ne forment pas un flux fréquent et le besoin principal est une décision CODIR sur un instantané. Onze graphiques ont été exportés en PNG et SVG, avec titres-message, unités et période dans la narration, tandis que les CSV fournissent l'alternative tabulaire. Les trois ajouts finaux isolent le stock sans vente d'octobre, l'anomalie de marge de la référence 4355 et la relation prix–ventes d'octobre. Une palette cohérente et un orange d'accent distinguent les signaux sans dépendre exclusivement d'un code couleur.

**Limite.** Les principes ont guidé la conception, mais aucune certification d'accessibilité utilisateur n'a été réalisée. Un test avec lecteurs d'écran, contrastes mesurés et utilisateurs réels serait nécessaire avant publication publique.

## 7. Prévision et saisonnalité : seuil minimal non atteint

La documentation [`statsmodels.tsa.seasonal.seasonal_decompose`](https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.seasonal_decompose.html), version **0.14.6**, exige au moins deux cycles complets. *Forecasting: Principles and Practice*, [3e édition](https://otexts.com/fpp3/), recommande une [validation croisée temporelle à origine glissante](https://otexts.com/fpp3/tscv.html) qui n'utilise jamais le futur pour entraîner un modèle, ainsi que des [intervalles de prédiction](https://otexts.com/fpp3/prediction-intervals.html) pour rendre l'incertitude visible.

BottleNeck ne possède qu'un total de ventes d'octobre et un stock final au 31 octobre. Il n'existe ni série temporelle, ni second cycle, ni fenêtre de test. Une extrapolation annuelle, une décomposition saisonnière ou un modèle de machine learning seraient donc invérifiables.

**Décision.** La couverture de stock est nommée « couverture au rythme d'octobre » et sert uniquement à ordonner une revue. Une vraie prévision ne sera envisagée qu'après collecte de plusieurs périodes comparables; elle devra alors être confrontée à des références naïves et saisonnières par origine glissante et publier des intervalles, pas seulement un point estimé.

## 8. Cadence de veille proposée

- **À chaque nouvel export mensuel :** rejouer les contrats, les anti-jointures et le registre qualité; comparer les taux de problèmes à la période précédente.
- **À chaque changement de schéma ou de système :** revalider les cardinalités et les règles métier avant tout calcul.
- **Trimestriellement :** contrôler les versions pandas, Pandera et nbclient, les versions retirées et les changements de sémantique.
- **Quand au moins deux cycles complets sont disponibles :** réévaluer les méthodes temporelles et définir un protocole de validation avant de choisir un modèle.
- **Quand le suivi devient fréquent et multi-utilisateur :** réexaminer dashboard, Pandera au runtime ou Great Expectations à partir d'un besoin et d'un coût d'exploitation explicites.

Cette veille est un état daté. Les métriques locales priment sur la popularité d'un outil, et toute recommandation future doit être testée sur les données BottleNeck avant d'être annoncée comme une amélioration.
