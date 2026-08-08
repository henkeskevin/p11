# Audit de l'état initial

Date de la baseline : 8 août 2026. Le notebook original est conservé sous `archive/original/` avec le SHA-256 `a2c094641fbeae20bb85c5cc18a9c79b9c497624494bd92605d9c95fe971cdec`.

## Exécution de référence

L'exécution stricte du notebook original avec `nbclient` s'arrête en 5,02 s sur la première cellule de code :

```text
ModuleNotFoundError: No module named 'google.colab'
```

Après neutralisation diagnostique du montage Colab, la cellule suivante échoue sur `/content/drive/MyDrive/p6/web.xlsx`. Une exécution contrôlée avec chemins locaux a parcouru 72 cellules de code en 5,32 s et s'est ensuite arrêtée sur l'import non déclaré de seaborn. Le notebook contient 107 cellules (74 code, 33 Markdown); toutes les cellules de code ont `execution_count=None` malgré 59 cellules avec sorties stockées. Les métadonnées annoncent Python 3.8.8 alors que les sorties Colab proviennent de Python 3.12.

## Défauts reproductibles

| Zone | Défaut observé | Impact |
|---|---|---|
| Environnement | Colab, Google Drive, dépendances et noyau non déclarés | Exécution locale impossible |
| ERP | 3 prix et 2 stocks négatifs passés en valeur absolue | Correction silencieuse et perte de preuve |
| Statut stock | 4 incohérences écrasées | Audit métier impossible |
| Web | 2 ventes négatives passées en positif et 2 SKU inventés | Donnée non justifiée, ensuite supprimée par la jointure |
| Liaison | 91 `id_web` nuls décrits comme « doublons » | Diagnostic d'unicité erroné |
| Jointures | 113 lignes non appariées supprimées | 111 références ERP et 2 produits Web perdus sans règle |
| Pareto | Cumul dépendant du tri de la cellule précédente | Résultat change lors d'une réexécution isolée |
| Stock | `inf` remplacé par 0 pour zéro vente | 3 stocks dormants apparaissent comme 0 mois |
| Valorisation | Code au prix de vente, ancien CSV au coût d'achat | Résultats contradictoires : 494 682,40 € vs 277 350,37 € |
| Marge | `(PV HT − PA) / PV HT` nommé taux de marge | L'indicateur est en réalité un taux de marque |
| Corrélation | Conclusion de « gestion stable » | Causalité/conclusion non démontrée |
| Export | Commentaire Excel mais CSV avec index et écrasement | Livrable périmé et colonne parasite |

## Baseline chiffrée reconstituée

- 825 lignes ERP, clé `product_id` unique;
- 1 513 lignes Web : 716 produits, 714 pièces jointes, 83 lignes structurelles;
- 825 lignes de liaison, dont 734 `id_web` renseignés et uniques;
- 714 appariements 1–1;
- 111 références ERP non appariées : 91 sans `id_web`, 20 liens absents du Web;
- 2 produits Web sans SKU, avec ventes négatives −56 et −17;
- CA d'octobre : 143 680,10 € TTC;
- unités : 5 751;
- 435 références pour 80 % du CA;
- IQR : 31 prix signalés; z-score classique : 13;
- stock apparié brut signé : 16 739 unités et 277 305,77 € au coût;
- 3 références avec stock et aucune vente d'octobre : 14 959,40 € au coût;
- 22 références vendues mais à stock final nul;
- marge brute : 44 660,65 € HT, taux de marque pondéré 37,30 % sous hypothèse TVA 20 %.

Le CA et les unités ont été vérifiés par une seconde chaîne `openpyxl` + dictionnaires Python + `Decimal`. La différence est nulle au centime.

## Comparaison avant / après

| Critère | Initial | Version portfolio |
|---|---|---|
| Exécution stricte | Échec Colab en 5,02 s | Succès local en 20,03 s, 12 cellules de code |
| Corrections | Valeur absolue / imputation silencieuse | Brut conservé, quarantaine et registre |
| Jointures | `outer` puis suppression | clés nulles isolées, `validate`, anti-jointures exportées |
| CA | Calcul unique | calcul vectorisé + réconciliation `Decimal` |
| Stock sans vente | couverture 0 | couverture indéfinie et segment dédié |
| Valorisation | ambiguë | coût HT et valeur de vente TTC séparés |
| Outliers | IQR et z-score sans choix | 4 méthodes testées, MAD choisi sur preuves |
| Tests | Aucun | suite pytest et CI |
| Visualisation | Plotly/Colab non exporté | 8 graphiques PNG + SVG |

