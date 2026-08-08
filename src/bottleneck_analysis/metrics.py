from __future__ import annotations

from decimal import Decimal
from typing import Any

import numpy as np
import pandas as pd

from .pipeline import PipelineResult


def _share(series: pd.Series, n: int) -> float:
    total = float(series.sum())
    return float(series.nlargest(n).sum() / total) if total else 0.0


def _count_for_share(series: pd.Series, target: float = 0.80) -> int:
    ordered = series.sort_values(ascending=False)
    total = ordered.sum()
    if total <= 0:
        return 0
    return int((ordered.cumsum() < target * total).sum() + 1)


def independent_ca_decimal(analytic: pd.DataFrame) -> Decimal:
    total = Decimal("0")
    valid = analytic.loc[
        analytic["price"].notna()
        & (analytic["price"] > 0)
        & analytic["total_sales"].notna()
        & (analytic["total_sales"] >= 0),
        ["price", "total_sales"],
    ]
    for price, quantity in valid.itertuples(index=False, name=None):
        total += Decimal(str(price)) * Decimal(str(quantity))
    return total.quantize(Decimal("0.01"))


def compute_metrics(result: PipelineResult) -> dict[str, Any]:
    analytic = result.analytic
    ca = analytic["ca_octobre_ttc"].dropna()
    ca_total = float(ca.sum())
    ca_decimal = independent_ca_decimal(analytic)
    net_sales_ht = (
        analytic["prix_vente_ht"] * analytic["total_sales"]
    ).where(analytic["marge_octobre_ht"].notna())
    gross_margin = analytic["marge_octobre_ht"].sum(min_count=1)
    weighted_margin_rate = (
        float(gross_margin / net_sales_ht.sum())
        if net_sales_ht.sum() and pd.notna(gross_margin)
        else np.nan
    )

    valid_erp_stock = result.erp.loc[
        result.erp["stock_quantity"].notna()
        & (result.erp["stock_quantity"] >= 0)
        & result.erp["purchase_price"].notna()
        & (result.erp["purchase_price"] > 0)
    ]
    full_stock_cost = float(
        (valid_erp_stock["stock_quantity"] * valid_erp_stock["purchase_price"]).sum()
    )
    full_stock_units = float(valid_erp_stock["stock_quantity"].sum())

    raw_erp_stock = result.erp.loc[
        result.erp["stock_quantity"].notna()
        & result.erp["purchase_price"].notna()
        & (result.erp["purchase_price"] > 0)
    ]
    raw_matched_stock = analytic.loc[
        analytic["stock_quantity"].notna()
        & analytic["purchase_price"].notna()
        & (analytic["purchase_price"] > 0)
    ]

    quality_counts = (
        result.quality_issues.groupby(["category", "severity"])
        .size()
        .rename("count")
        .reset_index()
    )
    quality_by_category = {
        row.category: int(row.count)
        for row in quality_counts.groupby("category", as_index=False)["count"].sum().itertuples()
    }

    matched_web_products = int((result.catalogue["web_match_status"] == "both").sum())
    web_valid_sku = int(result.web_products["sku"].notna().sum())
    metrics: dict[str, Any] = {
        "period": {
            "sales": "octobre uniquement",
            "stock": "état au 31 octobre",
        },
        "source_rows": {
            "erp": int(len(result.erp_raw)),
            "web_raw": int(len(result.web_raw)),
            "web_products": int(len(result.web_products)),
            "liaison": int(len(result.liaison_raw)),
        },
        "data_quality": {
            "erp_unique_product_ids": int(result.erp["product_id"].nunique()),
            "liaison_non_null_web_ids": int(result.liaison["id_web"].notna().sum()),
            "liaison_missing_web_ids": int(result.liaison["id_web"].isna().sum()),
            "web_products_valid_sku": web_valid_sku,
            "matched_web_products": matched_web_products,
            "web_sku_match_rate": matched_web_products / web_valid_sku if web_valid_sku else 0.0,
            "erp_mapping_coverage": float(result.liaison["id_web"].notna().mean()),
            "loading_warnings": int(len(result.loading_warnings)),
            "issues_by_category": quality_by_category,
        },
        "sales": {
            "revenue_october_ttc": ca_total,
            "revenue_october_ttc_decimal_check": float(ca_decimal),
            "reconciliation_difference": float(Decimal(str(round(ca_total, 2))) - ca_decimal),
            "units_sold_october": float(analytic["total_sales"].sum()),
            "references_with_sales": int((analytic["total_sales"] > 0).sum()),
            "top_10_revenue_share": _share(ca, 10),
            "top_20_revenue_share": _share(ca, 20),
            "top_100_revenue_share": _share(ca, 100),
            "references_for_80pct_revenue": _count_for_share(ca),
            "catalogue_share_for_80pct_revenue": _count_for_share(ca) / len(ca) if len(ca) else 0.0,
            "hhi_revenue": float(((ca / ca_total) ** 2).sum()) if ca_total else 0.0,
        },
        "margin": {
            "vat_assumption": 0.20,
            "gross_margin_october_ht": float(gross_margin),
            "weighted_markup_rate_on_sales": weighted_margin_rate,
            "margin_rate_on_cost": float(
                gross_margin
                / (analytic["purchase_price"] * analytic["total_sales"])
                .where(analytic["marge_octobre_ht"].notna())
                .sum()
            ),
            "negative_markup_references": int((analytic["taux_marque"] < 0).sum()),
        },
        "stock": {
            "full_erp_stock_units_raw_signed": float(raw_erp_stock["stock_quantity"].sum()),
            "full_erp_stock_value_cost_ht_raw_signed": float(
                (raw_erp_stock["stock_quantity"] * raw_erp_stock["purchase_price"]).sum()
            ),
            "full_erp_stock_units_valid": full_stock_units,
            "full_erp_stock_value_cost_ht": full_stock_cost,
            "matched_stock_units_raw_signed": float(raw_matched_stock["stock_quantity"].sum()),
            "matched_stock_value_cost_ht_raw_signed": float(
                (raw_matched_stock["stock_quantity"] * raw_matched_stock["purchase_price"]).sum()
            ),
            "matched_stock_units_valid": float(
                analytic.loc[analytic["stock_quantity"] >= 0, "stock_quantity"].sum()
            ),
            "matched_stock_value_cost_ht": float(analytic["valeur_stock_cout_ht"].sum()),
            "matched_stock_value_retail_ttc": float(
                analytic["valeur_stock_vente_ttc"].sum()
            ),
            "stock_without_october_sales_references": int(
                (analytic["segment_stock"] == "stock_sans_vente_octobre").sum()
            ),
            "stock_without_october_sales_value_cost_ht": float(
                analytic.loc[
                    analytic["segment_stock"] == "stock_sans_vente_octobre",
                    "valeur_stock_cout_ht",
                ].sum()
            ),
            "potential_stockout_references": int(
                (analytic["segment_stock"] == "rupture_potentielle").sum()
            ),
            "over_12_months_references": int(
                (analytic["segment_stock"] == "surstock_gt_12_mois").sum()
            ),
            "over_12_months_value_cost_ht": float(
                analytic.loc[
                    analytic["segment_stock"] == "surstock_gt_12_mois",
                    "valeur_stock_cout_ht",
                ].sum()
            ),
        },
    }
    return metrics


def top_products_table(result: PipelineResult, n: int = 15) -> pd.DataFrame:
    columns = [
        "product_id",
        "id_web",
        "post_title",
        "product_type",
        "price",
        "total_sales",
        "ca_octobre_ttc",
        "marge_octobre_ht",
        "taux_marque",
        "taux_marge_sur_cout",
        "stock_quantity",
        "segment_stock",
    ]
    return (
        result.analytic[columns]
        .sort_values("ca_octobre_ttc", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )
