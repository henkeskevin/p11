from __future__ import annotations

from pathlib import Path

import nbformat as nbf


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "notebooks" / "BottleNeck_analyse_portfolio.ipynb"


def markdown(text: str):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text: str):
    return nbf.v4.new_code_cell(text.strip())


def build() -> None:
    cells = [
        markdown(
            """
# BottleNeck — décisions ventes, stocks et marge

Analyse reproductible des extractions ERP, Web et de leur table de liaison.

**Périmètre temporel.** Les ventes couvrent uniquement **octobre** et les stocks sont un état au **31 octobre**. L'année et l'horodatage d'extraction ne figurent pas dans les sources et restent à confirmer. Les couvertures de stock sont donc des scénarios au rythme d'octobre, pas des prévisions ni une rotation comptable.

**Objectif décisionnel.** Fiabiliser le rapprochement, mesurer la performance d'octobre et prioriser les contrôles de marge et de stock sans corriger silencieusement les données sources.
"""
        ),
        markdown(
            """
## 1. Pipeline et traçabilité

Le notebook appelle le même code testé que l'exécution en ligne de commande. Les sources restent immuables; toutes les alertes sont écrites dans un registre avec trois niveaux : **erreur certaine**, **anomalie probable**, **inhabituel mais plausible**.
"""
        ),
        code(
            """
from pathlib import Path
import hashlib
import platform
import sys

import matplotlib
import numpy as np
import pandas as pd
from IPython.display import Image, Markdown, display

ROOT = Path.cwd().resolve()
if not (ROOT / "pyproject.toml").exists():
    raise RuntimeError("Exécuter ce notebook depuis la racine du dépôt.")
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bottleneck_analysis.config import AnalysisConfig
from bottleneck_analysis.metrics import top_products_table
from bottleneck_analysis.reporting import export_analysis

run = export_analysis(AnalysisConfig(project_root=ROOT))
result = run.result
metrics = run.metrics

print(f"Python {platform.python_version()} | pandas {pd.__version__} | numpy {np.__version__} | matplotlib {matplotlib.__version__}")
print(f"Pipeline exécuté : {len(result.analytic)} produits Web rapprochés, {len(run.figures)} exports graphiques PNG/SVG.")
"""
        ),
        code(
            """
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

source_manifest = pd.DataFrame([
    {"source": name, "lignes": len(frame), "colonnes": len(frame.columns), "sha256": sha256(ROOT / "data" / "raw" / name)}
    for name, frame in [
        ("erp.xlsx", result.erp_raw),
        ("web.xlsx", result.web_raw),
        ("liaison.xlsx", result.liaison_raw),
    ]
])
display(source_manifest)
print(f"Avertissements de lecture capturés et exportés : {len(result.loading_warnings)}")
"""
        ),
        markdown(
            """
## 2. Qualité et rapprochement

Les clés nulles sont retirées du côté Web **avant** jointure : pandas apparie autrement les valeurs nulles entre elles, contrairement à la sémantique SQL habituelle. Les cardinalités attendues sont ensuite certifiées et les non-correspondances restent visibles.
"""
        ),
        code(
            """
display(result.join_audit)
quality_summary = (
    result.quality_issues.groupby(["category", "severity"], as_index=False)
    .size()
    .rename(columns={"size": "constats"})
)
display(quality_summary)
display(Image(filename=str(ROOT / "reports" / "figures" / "01_rapprochement_sources.png"), width=900))
"""
        ),
        code(
            """
priority_rules = [
    "erp_price_non_positive",
    "erp_stock_negative",
    "web_sales_invalid",
    "web_product_sku_missing",
    "web_product_attachment_sales_mismatch",
    "erp_marked_online_but_web_missing",
    "web_sales_while_erp_offline",
    "margin_negative",
]
priority_issues = result.quality_issues.loc[
    result.quality_issues["rule_id"].isin(priority_rules),
    ["rule_id", "source", "key", "raw_value", "category", "description", "action"],
]
display(priority_issues)
"""
        ),
        markdown(
            """
### Expérience 1 — choisir les lignes Web par leur sens métier

Critère fixé avant calcul : préserver une ligne par SKU sans dépendre de l'ordre de l'export. Le filtre `post_type == "product"` est comparé aux pièces jointes, au dédoublonnage premier/dernier et à la somme de toutes les lignes.
"""
        ),
        code(
            """
display(run.web_selection_comparison.style.format({
    "units": "{:,.0f}",
    "revenue_ttc": "{:,.2f} €",
    "revenue_difference_vs_product": "{:+,.2f} €",
    "relative_difference_vs_product": "{:+.2%}",
}))
print("Décision : filtre sémantique 'product'. Un simple keep='first' surévalue ici le CA de 10 068 €, soit 7,01 %.")
"""
        ),
        markdown(
            """
## 3. Performance commerciale d'octobre

Le CA est calculé ligne à ligne puis recalculé indépendamment avec `Decimal`. La différence de réconciliation doit rester nulle au centime.
"""
        ),
        code(
            """
kpis = pd.DataFrame([
    ["CA TTC d'octobre", metrics["sales"]["revenue_october_ttc"], "€"],
    ["Unités vendues", metrics["sales"]["units_sold_october"], "unités"],
    ["Références vendues", metrics["sales"]["references_with_sales"], "références"],
    ["Marge brute d'octobre", metrics["margin"]["gross_margin_october_ht"], "€ HT"],
    ["Taux de marque pondéré", metrics["margin"]["weighted_markup_rate_on_sales"], "%"],
    ["Écart du recalcul indépendant", metrics["sales"]["reconciliation_difference"], "€"],
], columns=["indicateur", "valeur", "unité"])
display(kpis)
"""
        ),
        code(
            """
display(top_products_table(result, 10))
display(Image(filename=str(ROOT / "reports" / "figures" / "02_top10_ca_octobre.png"), width=900))
display(Image(filename=str(ROOT / "reports" / "figures" / "03_pareto_ca_octobre.png"), width=900))
print(
    f"Les 20 premières références représentent {metrics['sales']['top_20_revenue_share']:.1%} du CA. "
    f"Il faut {metrics['sales']['references_for_80pct_revenue']} références "
    f"({metrics['sales']['catalogue_share_for_80pct_revenue']:.1%} du catalogue rapproché) pour atteindre 80 % : pas de Pareto 20/80."
)
"""
        ),
        markdown(
            """
## 4. Prix : comparer avant de qualifier

Un prix négatif est une erreur de validité. Un prix élevé est seulement un signal de revue. Quatre méthodes sont testées sur les données réelles et sur 20 anomalies multiplicatives injectées de façon reproductible. Critères : rappel, moins de 5 % d'alertes de base, stabilité de la liste et temps d'exécution.
"""
        ),
        code(
            """
display(run.outlier_comparison.style.format({
    "baseline_alert_rate": "{:.2%}",
    "injected_recall": "{:.0%}",
    "stability_jaccard": "{:.2f}",
    "median_runtime_ms": "{:.3f} ms",
}))
print("Décision : MAD sur le prix brut (33 alertes, rappel 100 %, stabilité > 0,90). Les alertes restent dans la catégorie 'inhabituel mais plausible'.")
display(Image(filename=str(ROOT / "reports" / "figures" / "04_prix_inhabituels.png"), width=900))
display(Image(filename=str(ROOT / "reports" / "figures" / "08_typologie_alertes.png"), width=850))
"""
        ),
        markdown(
            """
## 5. Stock au 31 octobre

La valeur comptable indicative est calculée au **coût d'achat HT**. La valeur au prix de vente TTC est conservée séparément et ne doit pas être appelée valorisation comptable. Une référence sans vente en octobre conserve une couverture indéfinie — jamais zéro.
"""
        ),
        code(
            """
stock = metrics["stock"]
stock_summary = pd.DataFrame([
    ["Stock apparié brut signé", stock["matched_stock_units_raw_signed"], "unités"],
    ["Valeur brute signée au coût", stock["matched_stock_value_cost_ht_raw_signed"], "€ HT"],
    ["Valeur après exclusion de la quantité négative", stock["matched_stock_value_cost_ht"], "€ HT"],
    ["Stock sans vente observée", stock["stock_without_october_sales_value_cost_ht"], "€ HT"],
    ["Couverture > 12 mois au rythme d'octobre", stock["over_12_months_value_cost_ht"], "€ HT"],
    ["Références vendues avec stock final nul", stock["potential_stockout_references"], "références"],
], columns=["indicateur", "valeur", "unité"])
display(stock_summary)
display(Image(filename=str(ROOT / "reports" / "figures" / "05_segments_stock.png"), width=900))
"""
        ),
        code(
            """
stock_priorities = result.analytic.loc[
    result.analytic["segment_stock"].isin(["stock_sans_vente_octobre", "surstock_gt_12_mois", "rupture_potentielle"]),
    ["product_id", "id_web", "product_type", "total_sales", "stock_quantity", "couverture_au_rythme_octobre_mois", "valeur_stock_cout_ht", "segment_stock"],
].sort_values("valeur_stock_cout_ht", ascending=False)
display(stock_priorities.head(15))
"""
        ),
        markdown(
            """
## 6. Marge

Sous hypothèse d'un prix de vente TTC et d'une TVA de 20 %, la formule `(PV HT − coût) / PV HT` est un **taux de marque**. Le taux de marge sur coût est publié séparément. Le coût d'achat aberrant de la référence 4355 est isolé au lieu d'être dilué dans une moyenne de catégorie.
"""
        ),
        code(
            """
display(pd.DataFrame([
    ["Marge brute d'octobre", metrics["margin"]["gross_margin_october_ht"]],
    ["Taux de marque pondéré", metrics["margin"]["weighted_markup_rate_on_sales"]],
    ["Taux de marge sur coût", metrics["margin"]["margin_rate_on_cost"]],
], columns=["indicateur", "valeur"]))
display(result.analytic.loc[result.analytic["taux_marque"] < 0, [
    "product_id", "price", "purchase_price", "total_sales", "stock_quantity", "taux_marque", "valeur_stock_cout_ht"
]])
display(Image(filename=str(ROOT / "reports" / "figures" / "06_marge_ponderee_type.png"), width=900))
"""
        ),
        markdown(
            """
## 7. Relations quantitatives

La corrélation de Spearman limite la sensibilité aux valeurs extrêmes, mais elle ne démontre aucune causalité. Avec un seul mois, elle ne permet ni prévision, ni effet prix, ni recommandation généralisée de baisse de prix.
"""
        ),
        code(
            """
display(Image(filename=str(ROOT / "reports" / "figures" / "07_correlations_spearman.png"), width=800))
"""
        ),
        markdown(
            """
## 8. Décisions recommandées

1. **Corriger la qualité avant toute automatisation** : confirmer les 3 prix négatifs, 2 stocks négatifs, 2 ventes négatives sans SKU et la référence 4355.
2. **Réconcilier les statuts ERP/Web** : traiter les 3 références marquées en ligne mais absentes du Web et le produit 4200 vendu malgré `onsale_web=0`.
3. **Piloter le cash immobilisé** : revoir d'abord les 24 références au-delà de 12 mois au rythme d'octobre (95 011,92 € au coût) et les 3 références avec stock mais aucune vente observée (14 959,40 €).
4. **Sécuriser la disponibilité** : examiner les 22 références vendues avec stock final nul.

Les propriétaires, échéances et preuves attendues sont détaillés dans `docs/synthese_codir.md` et `docs/backlog_planning_risques.md`.
"""
        ),
        markdown(
            """
## 9. Limites et biais

- Ventes d'un seul mois; aucune tendance ni saisonnalité observable.
- Stock final, pas stock moyen : la « couverture au rythme d'octobre » n'est pas une rotation comptable.
- TVA fixée à 20 % et prix d'achat supposé HT; ces conventions doivent être confirmées.
- Les ventes Web sans SKU sont en quarantaine; le rapprochement par GUID est un candidat, pas une correction automatique.
- Les produits non rapprochés n'ont pas de ventes Web observables dans ce jeu : absence de donnée ne signifie pas zéro vente.
- Les prix signalés par MAD peuvent être des vins premium valides; aucune suppression statistique automatique.

Les détails complets figurent dans `docs/limites_biais.md`.
"""
        ),
        markdown(
            r"""
## 10. Reproduction

Depuis la racine du dépôt :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\run_analysis.py
.\.venv\Scripts\python.exe scripts\execute_notebook.py
```

Le notebook, les CSV, le JSON d'indicateurs et les figures sont régénérés à partir des trois classeurs placés dans `data/raw/`.
"""
        ),
    ]

    notebook = nbf.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "Python 3 (BottleNeck)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.12",
                "mimetype": "text/x-python",
                "codemirror_mode": {"name": "ipython", "version": 3},
                "pygments_lexer": "ipython3",
                "nbconvert_exporter": "python",
                "file_extension": ".py",
            },
        },
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, OUTPUT)
    print(f"Notebook généré : {OUTPUT}")


if __name__ == "__main__":
    build()
