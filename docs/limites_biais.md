# Limites, hypothèses et biais

## Périmètre temporel

- Les ventes couvrent **octobre uniquement** ; le stock est une photographie au **31 octobre**. L'année et l'horodatage d'extraction ne sont pas renseignés dans les sources : ils doivent être confirmés avant tout rapprochement avec une autre période.
- Il n’existe pas de série temporelle dans le périmètre analysé. L’analyse ne mesure donc ni tendance, ni saisonnalité, ni croissance, ni demande annuelle.
- La couverture de stock divise le stock du 31 octobre par les ventes d’octobre. Les catégories supérieures à douze mois supposent que le rythme d’octobre se répète ; elles priorisent une revue mais ne constituent pas une prévision.
- Une référence sans vente en octobre n’est pas nécessairement invendable, et une référence à zéro stock après avoir vendu en octobre n’est pas la preuve d’une vente perdue.

Source : [indicateurs clés](../reports/tables/indicateurs_cles.json).

## Périmètres de stock et unités monétaires

Les vues suivantes répondent à des questions différentes et ne doivent pas être mélangées :

| Vue au 31 octobre | Unités | Valorisation | Interprétation |
|---|---:|---:|---|
| ERP complet, brut signé | **17 811** | **298 555,76 € au coût d’achat HT** | Conserve les stocks négatifs tels que fournis. |
| ERP complet, hors stocks négatifs | **17 822** | **298 627,66 € au coût d’achat HT** | Vue de pilotage après exclusion des anomalies de stock négatif, sans corriger les sources. |
| Catalogue rapproché, brut signé | **16 739** | **277 305,77 € au coût d’achat HT** | Périmètre limité aux références ERP reliées à un produit Web. |
| Catalogue rapproché, hors stocks négatifs | **16 740** | **277 328,07 € au coût d’achat HT** | Vue utilisée pour les segments de stock. |
| Catalogue rapproché, hors stocks négatifs | — | **494 637,90 € au prix de vente TTC** | Valeur théorique si tout le stock était vendu au tarif observé ; ce n’est ni une valeur comptable, ni du chiffre d’affaires acquis. |

La valeur au coût d’achat HT et la valeur au prix de vente TTC ont des bases fiscales, des périmètres et des usages différents. Leur écart n’est pas une marge réalisable : il ne tient pas compte des invendus, remises, retours ni coûts absents des sources.

Source : [indicateurs clés](../reports/tables/indicateurs_cles.json).

## Hypothèses de prix et de marge

- Le prix de vente est interprété TTC, le prix d’achat comme un coût HT et la TVA comme uniforme à **20 %**. Cette hypothèse n’a pas été vérifiée référence par référence.
- La marge calculée est une marge brute : prix de vente ramené en HT moins prix d’achat. Elle ne représente pas le résultat net et n’intègre pas les charges qui ne figurent pas dans les extractions.
- La marge brute d’octobre de **44 660,65 € HT** et le taux de marque pondéré de **37,30 %** changeraient si les conventions de prix ou de TVA étaient différentes.
- **Une référence** présente une marge négative sous ces hypothèses ; elle doit être vérifiée dans les systèmes sources avant toute correction ou décision commerciale.

Sources : [indicateurs clés](../reports/tables/indicateurs_cles.json), [registre qualité](../reports/tables/registre_qualite.csv).

## Quarantaine, SKU et retours

- Le registre contient **7 erreurs certaines** : **3 prix de vente non positifs**, **2 lignes produit sans SKU valide** et **2 ventes négatives ou invalides**. Ces lignes sont exclues uniquement des calculs qu’elles rendent invalides ; les valeurs brutes restent visibles.
- Les **2 stocks négatifs** sont classés comme anomalies probables, pas comme erreurs certaines. Ils sont conservés dans la vue brute signée et exclus de la vue de stock valide en attente d’une revue métier.
- Une vente négative peut représenter un retour, une annulation, une correction ou une erreur de saisie. L’export ne permet pas de trancher. Les valeurs négatives sont mises en quarantaine ; le chiffre d’affaires calculé ne doit donc pas être présenté comme un indicateur certifié net de retours.
- Aucun SKU manquant n’est inventé. Cette prudence évite un faux rapprochement mais réduit le périmètre analysable.

Source : [registre qualité](../reports/tables/registre_qualite.csv).

## Couverture et biais de rapprochement

- Les **825 références ERP** sont présentes dans la table de liaison, mais **91** n’ont pas d’identifiant Web renseigné.
- Parmi les identifiants Web non vides, **714** retrouvent une ligne produit et **20** n’en retrouvent aucune. Les **714 produits Web avec SKU valide** sont tous rapprochés.
- La couverture de mapping ERP est donc de **88,97 %**. Le taux de rapprochement de **100 %** côté produits Web valides ne signifie pas que tout l’ERP est couvert.
- Les analyses de ventes, de marge et de segments portent sur le catalogue rapproché. Les références non rapprochées peuvent avoir du stock ERP, mais aucune vente Web ne leur est attribuée sans preuve.

Sources : [indicateurs clés](../reports/tables/indicateurs_cles.json), [audit des rapprochements](../reports/tables/audit_jointures.csv).

## Prix inhabituels et corrélations

- La méthode retenue signale **33 prix inhabituels mais plausibles**. Une alerte statistique n’est pas une erreur : un prix élevé peut être justifié par le produit, et les variables disponibles ne suffisent pas à l’expliquer.
- L’expérience d’injection compare la sensibilité et la stabilité sur les données présentes. Ses résultats ne garantissent pas la performance sur un autre catalogue ou une autre distribution de prix.
- Les corrélations sont descriptives, transversales et limitées à octobre. Elles peuvent refléter le type de produit, le prix, la disponibilité, les valeurs inhabituelles ou la sélection des références. Elles ne démontrent aucune causalité et ne justifient pas seules un changement de prix, de stock ou d’assortiment.

Sources : [indicateurs clés](../reports/tables/indicateurs_cles.json), [comparaison des méthodes de détection](../reports/tables/comparaison_methodes_outliers.csv).

## Environnement, outils et portée des contrôles

- L’exécution dépend de Python, Pandas, NumPy, OpenPyXL, Matplotlib et des outils Jupyter décrits dans `pyproject.toml` et les fichiers de dépendances. Les tests locaux ne constituent pas une certification sur tous les systèmes d’exploitation ou toutes les versions futures.
- Le chargement a produit **3 avertissements OpenPyXL** indiquant que des extensions Excel inconnues ont été retirées. Cela ne prouve pas une altération des cellules utilisées, mais impose de recontrôler les exports si leur format change.
- Les temps de calcul des comparaisons sont des micro-mesures locales ; ils permettent de comparer les options dans cette expérience, pas de promettre un niveau de service.
- Les tests automatisés couvrent les règles et cas connus. Ils ne remplacent pas la validation métier des conventions ERP, des retours, de la TVA, des prix d’achat, des correspondances ou des alertes.
- L’IA peut proposer du code et des interprétations, mais elle ne résout pas l’ambiguïté des sources. Seuls les résultats exécutés, les contrôles et la confirmation des responsables métier font preuve.

Sources : [avertissements de chargement](../reports/tables/avertissements_chargement.csv), [comparaison des validateurs](../reports/tables/comparaison_validateurs.csv), [comparaison des méthodes de détection](../reports/tables/comparaison_methodes_outliers.csv).

## Usage approprié

Cette analyse convient pour prioriser les contrôles qualité et préparer une revue de stock. Elle ne doit pas, sans données supplémentaires et validation métier, servir à établir des prévisions annuelles, certifier un inventaire comptable, corriger automatiquement les sources ou déclencher seule un réassort, une promotion ou un déréférencement.
