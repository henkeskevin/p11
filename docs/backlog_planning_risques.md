# Backlog, planning et registre des risques — BottleNeck

**Version :** 1.0  
**Date :** 8 août 2026  
**T0 :** date d’acceptation de la version portfolio  
**Convention :** les propriétaires sont des rôles indicatifs à remplacer par des noms lors du lancement opérationnel.

## 1. Principes de pilotage

- Le dépôt analytique est livré ; les corrections des systèmes ERP, Web et liaison restent des actions métier.
- Aucun élément source n’est modifié sans data owner, justification et nouvelle version archivée.
- Une action n’est « terminée » que si son résultat est vérifié par une preuve persistante.
- Toute nouvelle source déclenche, dans cet ordre : archivage et empreinte, tests, analyse, expérience si la méthode change, notebook propre, revue des écarts et publication.
- Les échéances ci-dessous sont relatives à T0 et n’impliquent pas une date contractuelle tant que les rôles ne sont pas nommés.

## 2. Backlog livré

| ID | Élément livré | Statut | Valeur produite | Preuve |
|---|---|---|---|---|
| D01 | Préservation de l’état initial | **Terminé** | 8 fichiers copiés bit à bit et re-hachés | `archive/original/MANIFEST.md` |
| D02 | Baseline d’exécution | **Terminé** | Échec Colab reproduit en 5,02 s et diagnostic distinct documenté | `reports/tables/baseline_execution.json`; `docs/audit_initial.md` |
| D03 | Structure de projet et environnement | **Terminé** | Package `src`, dépendances bornées, chemins relatifs, scripts et CI | `pyproject.toml`; `src/bottleneck_analysis/`; `scripts/`; `.github/workflows/ci.yml` |
| D04 | Contrats de données | **Terminé** | Colonnes, types, domaines, clés vides et unicité non nulle contrôlés | `src/bottleneck_analysis/quality.py`; `src/bottleneck_analysis/pipeline.py`; `tests/test_pipeline.py` |
| D05 | Rapprochement audité | **Terminé** | 825 ERP–liaison et 714 Web rapprochés ; anti-jointures explicites | `reports/tables/audit_jointures.csv` |
| D06 | Registre qualité sans correction silencieuse | **Terminé** | 165 constats classés et données brutes conservées | `reports/tables/registre_qualite.csv`; `tests/test_pipeline.py` |
| D07 | Indicateurs réconciliés | **Terminé** | CA 143 680,10 € TTC, 5 751 unités, marge, concentration et stock ; CA réconcilié à 0,00 € | `reports/tables/indicateurs_cles.json`; `tests/test_metrics.py` |
| D08 | Expérience de sélection Web | **Terminé** | Filtre produit choisi après mesure de 5 options ; évite +10 068,00 € avec `keep='first'` | `reports/tables/comparaison_selection_lignes_web.csv`; `tests/test_experiments.py` |
| D09 | Expérience sur les prix inhabituels | **Terminé** | 4 méthodes comparées ; MAD brut retenu, 20/20 injections détectées, Jaccard 0,909 | `reports/tables/comparaison_methodes_outliers.csv`; `tests/test_experiments.py` |
| D10 | Expérience de validation | **Terminé** | pandas natif et Pandera testés sur 9 défauts ; natif retenu au runtime | `experiments/compare_validators.py`; `reports/tables/comparaison_validateurs.csv` |
| D11 | Notebook portfolio | **Terminé** | 24 cellules, 12 cellules de code exécutées sans erreur depuis un noyau propre | `notebooks/BottleNeck_analyse_portfolio.ipynb`; `scripts/execute_notebook.py` |
| D12 | Restitution graphique | **Terminé** | 11 vues décisionnelles exportées en PNG et SVG | `reports/figures/` |
| D13 | Tables d’aide à la décision | **Terminé** | top CA, qualité, jointures, stocks prioritaires, indicateurs et comparaisons exportés | `reports/tables/`; `data/processed/` |
| D14 | Documentation multi-public | **Terminé** | README, cahier, matrice, veille, registres, synthèses CODIR/recruteur et limites | `README.md`; `docs/` |
| D15 | Automatisation de la recette | **Terminé** | 17 tests de pipeline, métriques, expériences, archives et livrables ; validateur complet et journal persistant ; workflow CI configuré | `tests/`; `src/bottleneck_analysis/deliverables.py`; `scripts/validate_deliverables.py`; `reports/tables/final_validation.json`; `.github/workflows/ci.yml` |
| D16 | Présentation CODIR | **Terminé** | 12 slides livrées, inspectées visuellement ; `slides_test` et fidélité au template réussis sans issue ; 12 blocs de notes Sources contrôlés | `reports/BottleNeck_CODIR.pptx`; `reports/BottleNeck_CODIR.pptx.inspect.ndjson`; `reports/tables/final_validation.json`; `docs/registre_ameliorations.md` |

## 3. Backlog métier restant

### Priorités

- **P0** : bloque l’usage fiable d’un indicateur ou expose à une décision financière erronée.
- **P1** : anomalie importante à qualifier avant une action commerciale ou de stock.
- **P2** : améliore la couverture ou la pérennité, sans bloquer la lecture actuelle.
- **P3** : évolution conditionnée par de nouvelles données ou un choix de gouvernance.

| ID | Priorité | Action et résultat attendu | Propriétaire indicatif | Échéance relative | Dépendance / preuve de clôture |
|---|---|---|---|---|---|
| B01 | P0 | Corriger ou justifier les **3 prix ERP non positifs**, **2 ventes Web négatives** et **2 lignes produit sans SKU**. Ne pas remplacer automatiquement les signes | Data owners ERP et e-commerce | T+2 jours ouvrés | Nouvelle extraction archivée ; règles concernées absentes ou justifiées dans `reports/tables/registre_qualite.csv`; CA réconcilié |
| B02 | P0 | Valider la TVA de 20 %, le caractère HT de `purchase_price` et les définitions « taux de marque » / « taux sur coût » | Finance | T+2 jours ouvrés | Note de validation ; si hypothèse modifiée, rerun complet et mise à jour des synthèses |
| B03 | P0 | Examiner la marge négative de la référence **4355** : unité, coût d’achat, prix TTC et TVA | Finance + data owner ERP | T+2 jours ouvrés | Ticket métier clos avec décision ; `reports/figures/10_anomalie_marge_reference_4355.png` actualisé après rerun |
| B04 | P1 | Qualifier les **2 stocks négatifs** et **2 incohérences quantité/statut**, sans écraser les valeurs source | Approvisionnement + ERP | T+5 jours ouvrés | Motif métier ou correction source ; vues brute et valide à nouveau rapprochées |
| B05 | P1 | Traiter les **3 références marquées en ligne dans l’ERP mais absentes du Web**, puis la vente Web de la référence **4200** marquée hors ligne dans l’ERP | E-commerce + ERP | T+5 jours ouvrés | Publication/statut confirmés ; règles `erp_marked_online_but_web_missing` et `web_sales_while_erp_offline` soldées ou acceptées |
| B06 | P1 | Revoir les **91 clés Web manquantes** de la liaison et les **20 identifiants renseignés absents des produits Web** ; distinguer hors-ligne légitime, obsolète et défaut de mapping | Data steward référentiels | T+10 jours ouvrés | Fichier de décision par référence ; couverture recalculée ; aucune clé inventée |
| B07 | P1 | Décider les actions sur les **22 ruptures potentielles** à partir des ventes d’octobre, du délai fournisseur et des commandes en cours | Approvisionnement + commerce | T+5 jours ouvrés | Liste commander/ne pas commander avec justification et date ; ne pas utiliser octobre seul comme prévision |
| B08 | P1 | Examiner les **3 stocks sans vente d’octobre** représentant **14 959,40 € HT au coût** | Commerce + approvisionnement | T+10 jours ouvrés | Décision garder, promouvoir, transférer ou revoir ; validation de saisonnalité avant démarque |
| B09 | P1 | Examiner les **24 références à plus de 12 mois de couverture**, soit **95 011,92 € HT au coût** au rythme d’octobre | Approvisionnement + finance | T+10 jours ouvrés | Priorisation par valeur et contrainte commerciale ; action validée par référence |
| B10 | P1 | Revoir humainement les **33 prix MAD élevés** et la référence à marge négative ; ne corriger que sur preuve source | Commerce + ERP + finance | T+10 jours ouvrés | Colonne de qualification « valide / erreur / à investiguer », auteur et date |
| B11 | P2 | Résoudre les **4 divergences de ventes** entre lignes produit et pièce jointe et confirmer durablement la sémantique `post_type='product'` avec l’équipe Web | Data owner e-commerce | T+10 jours ouvrés | Règle de dictionnaire de données approuvée ; test de régression conservé |
| B12 | P0 avant publication | Vérifier les droits de diffusion des fichiers ERP/Web/liaison et anonymiser ou retirer toute donnée sensible si nécessaire | Juridique / sécurité / propriétaire du portfolio | Avant publication publique | Visa de publication archivé ; scan manuel des fichiers et métadonnées |
| B13 | P2 | Exécuter le workflow CI sur le dépôt distant et protéger la branche par un contrôle vert | Mainteneur du dépôt | T+5 jours ouvrés après push | URL ou identifiant d’un run CI vert ; règle de protection activée si disponible |
| B14 | P2 | Instituer un rerun mensuel versionné, avec comparaison au mois précédent et revue des écarts qualité | Responsable data | T+1 mois | Deux snapshots horodatés, rapport de variation et journal d’exécution |
| B15 | P3 | Constituer au moins 12 mois comparables avant de tester saisonnalité, prévision de demande ou seuil de réapprovisionnement | Commerce + data | T+12 mois au plus tôt | Historique documenté, protocole d’expérience pré-enregistré, validation hors échantillon |
| B16 | P0 | Faire confirmer l’**année**, la date/heure d’extraction et la date de situation exacte de chaque source ; les inscrire dans les métadonnées et restitutions | Data owners + responsable data | T+2 jours ouvrés | Métadonnées source signées ; remplacement des libellés « octobre » et « 31 octobre » par des dates non ambiguës |

## 4. Planning de fermeture

| Phase | Fenêtre | Objectif | Entrée | Sortie / jalon |
|---|---|---|---|---|
| 0 — Livraison analytique | **T0 — terminé** | Mettre le dépôt sous contrôle et produire la baseline portfolio | Trois extractions, notebook et présentation initiaux | Pipeline, notebook, tests, 11 figures × 2 formats, présentation CODIR de 12 slides, documentation et backlog |
| 1 — Sécurisation financière et temporelle | **T0 à T+2 jours ouvrés** | Fermer les erreurs certaines qui touchent CA/marge, confirmer les hypothèses et dater sans ambiguïté les sources | B01 à B03, B16 | **Jalon G1 :** finance autorise l’usage interne des indicateurs ou demande un recalcul ; les dates sont certifiées |
| 2 — Référentiels et statuts | **T+3 à T+10 jours ouvrés** | Qualifier stocks négatifs, mapping et statuts croisés | B04 à B06, B11 | **Jalon G2 :** nouvelle extraction versionnée ; rapport de qualité comparatif |
| 3 — Décisions commerciales | **T+5 à T+10 jours ouvrés** | Transformer segments stock/prix en décisions humaines | B07 à B10 | **Jalon G3 :** liste d’actions nominative et validée, sans automatisme statistique |
| 4 — Publication et exploitation | **Avant publication à T+1 mois** | Sécuriser confidentialité, CI et récurrence | B12 à B14 | **Jalon G4 :** publication autorisée, CI verte, deuxième exécution comparable |
| 5 — Extension longitudinale | **Après 12 mois comparables** | Décider si prévision/saisonnalité apporte une valeur démontrable | B15 | **Jalon G5 :** go/no-go méthodologique fondé sur validation hors échantillon |

### Chemin critique

`B01 ∧ B02 ∧ B16` → rerun des indicateurs → `B03` → décision finance G1 → `B07–B10` → G3. En parallèle, `B12 ∧ B13 ∧ B14` est obligatoire pour atteindre la publication contrôlée G4.

Les actions de mapping B06 peuvent avancer en parallèle, mais une modification des correspondances impose un rerun complet avant toute reprise des chiffres dans la restitution.

## 5. Registre des risques

Échelle : probabilité et impact sont évalués **Faible / Moyenne / Élevée** sur l’usage décisionnel du jeu actuel. Le risque résiduel suppose l’application de la mitigation.

| ID | Risque | Probabilité | Impact | Signal / exposition actuelle | Mitigation et contrôle | Propriétaire | Risque résiduel |
|---|---|---|---|---|---|---|---|
| R01 | Octobre n’est pas représentatif de la demande annuelle | Élevée | Élevé | Un seul mois de ventes, aucune saisonnalité mesurable | Interdire annualisation/prévision ; collecter 12 mois ; valider hors échantillon | Commerce + data | Moyen après historique |
| R02 | Les erreurs source biaisent CA, marge ou stock | Élevée | Élevé | 7 erreurs certaines et 125 anomalies probables | Quarantaine, registre par clé, correction par data owner, rerun et tests | Data owners | Moyen |
| R03 | Le périmètre rapproché biaise la lecture du catalogue ERP | Moyenne | Élevé | 734/825 clés de liaison renseignées = 88,97 %, mais 714/825 produits effectivement rapprochés = 86,55 % ; 91 clés nulles et 20 liens absents | Publier les deux taux avec leur dénominateur et les anti-jointures ; qualifier B06 avant généralisation | Data steward | Moyen |
| R04 | La TVA ou l’unité du prix d’achat est mal interprétée | Moyenne | Élevé | Hypothèse uniforme 20 %, coût supposé HT | Visa finance B02 ; paramètre versionné ; recalcul de toutes les marges | Finance | Faible à moyen |
| R05 | Les pièces jointes Web sont comptées comme produits | Élevée sans contrôle | Élevé | Une sélection par ordre ajoute 10 068 €, la somme ajoute 107,01 % au CA de référence | Filtre sémantique `product`, cardinalité et test de régression | E-commerce + data | Faible |
| R06 | Un prix premium est corrigé à tort comme outlier | Élevée | Moyen | 33 alertes MAD sont plausibles par nature | Signal informatif seulement, revue humaine et conservation de la valeur brute | Commerce | Faible |
| R07 | La couverture de stock est prise pour une prévision | Élevée | Élevé | Ratio fondé uniquement sur octobre | Libellé « au rythme d’octobre », aucune commande automatique, intégrer délais et saisonnalité | Approvisionnement | Moyen |
| R08 | Valeur au coût et valeur de vente sont confondues | Moyenne | Élevé | Deux grandeurs monétaires coexistent | Colonnes et tableaux séparés ; unités HT/TTC dans chaque titre ; revue finance | Finance + data | Faible |
| R09 | Des exports deviennent obsolètes après changement de source ou de code | Moyenne | Élevé | Artefacts versionnés mais statiques | Une commande de génération, empreinte des sources, CI et contrôle automatisé de présence/lecture des livrables | Responsable data | Faible à moyen |
| R10 | Dérive des dépendances ou de l’environnement | Moyenne | Moyen | Python et bibliothèques évoluent | Bornes de versions, Python 3.12 en CI, noyau propre, rerun périodique | Mainteneur | Faible |
| R11 | La CI distante n’a pas réellement été exécutée | Moyenne | Moyen | Workflow local présent ; exécution dépend d’un push | Fermer B13 et conserver l’URL d’un run vert | Mainteneur | Faible |
| R12 | Publication non autorisée de données commerciales | Moyenne | Élevé | Fichiers Excel et détails produits présents dans le dépôt | Revue juridique/confidentialité B12, anonymisation ou retrait avant public | Propriétaire portfolio | Faible à moyen |
| R13 | Une proposition IA est prise pour une preuve | Moyenne | Élevé | L’IA a aidé à explorer et rédiger | Code exécutable, tests, exports mesurés, registre des décisions et revue humaine | Responsable data | Faible |
| R14 | Une correction métier non autorisée remplace la donnée brute | Moyenne | Élevé | Pression possible pour « nettoyer » les signes ou SKU | Sources immuables, SHA-256, aucune correction silencieuse, nouvelle version obligatoire | Data owners + data | Faible |
| R15 | Les responsabilités restent anonymes et les anomalies ne sont jamais closes | Moyenne | Élevé | Le dépôt ne contient pas d’organisation nominative | Remplacer chaque rôle indicatif par une personne à G1 et suivre B01–B16 | Sponsor | Moyen |
| R16 | « Octobre » et « 31 octobre » sont rattachés à la mauvaise année ou à une extraction de date inconnue | Moyenne | Élevé | Les fichiers fournis ne portent pas de métadonnée métier certifiant l’année et l’horodatage d’extraction | Fermer B16 ; ajouter année, date de situation, horodatage et propriétaire aux métadonnées puis régénérer toutes les restitutions | Data owners + responsable data | Faible |

## 6. Cadence et indicateurs de suivi

Une revue courte est recommandée à T+2, T+5 et T+10 jours ouvrés, puis mensuellement. Le tableau de bord de gouvernance minimal suit :

| Indicateur de pilotage | Baseline | Cible de fermeture |
|---|---:|---:|
| Erreurs certaines | 7 | 0 non justifiée |
| Anomalies probables | 125 | 100 % qualifiées ; le nombre peut rester non nul si accepté |
| Clés Web manquantes dans la liaison | 91 | 100 % qualifiées ; pas nécessairement 0 |
| Liens renseignés absents du Web | 20 | 0 non expliqué |
| Produits rapprochés | 714 | Stable ou variation expliquée après chaque source |
| Écart du contrôle indépendant de CA | 0,00 € | 0,00 € |
| Tests automatisés en échec | 0 | 0 |
| Notebook en erreur | 0 cellule | 0 cellule |
| Actions stock à propriétaire nommé | 0 preuve dans le jeu analytique | 100 % de B07–B09 affectées |

## 7. Règle de clôture d’une action métier

Une action B01 à B16 est close seulement si :

1. le propriétaire et la date de décision sont enregistrés ;
2. si l’action modifie des données, la donnée corrigée arrive dans une **nouvelle extraction**, l’ancienne restant archivée ;
3. `scripts/validate_deliverables.py --full` réussit, ce qui inclut analyse, expérience de validateurs, notebook et pytest ;
4. si un indicateur change, sa variation est expliquée dans le registre d’améliorations ;
5. si une donnée, une méthode ou un indicateur change, les synthèses et graphiques concernés sont régénérés ;
6. aucune nouvelle correction silencieuse n’a été introduite.

Cette règle évite qu’une anomalie disparaisse du tableau uniquement parce qu’elle a été filtrée ou écrasée.
