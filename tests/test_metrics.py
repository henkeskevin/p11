from __future__ import annotations

from decimal import Decimal

import pandas as pd
import pytest

from bottleneck_analysis.metrics import compute_metrics, independent_ca_decimal
from bottleneck_analysis.pipeline import PipelineResult


def test_revenue_is_reconciled_by_decimal_method(
    pipeline_result: PipelineResult,
) -> None:
    metrics = compute_metrics(pipeline_result)
    assert metrics["sales"]["revenue_october_ttc"] == pytest.approx(143_680.10)
    assert independent_ca_decimal(pipeline_result.analytic) == Decimal("143680.10")
    assert metrics["sales"]["reconciliation_difference"] == 0
    assert metrics["sales"]["units_sold_october"] == 5_751


def test_concentration_metrics(pipeline_result: PipelineResult) -> None:
    sales = compute_metrics(pipeline_result)["sales"]
    assert sales["references_for_80pct_revenue"] == 435
    assert sales["catalogue_share_for_80pct_revenue"] == pytest.approx(0.6092436975)
    assert sales["top_20_revenue_share"] == pytest.approx(0.1101746171)
    assert sales["hhi_revenue"] == pytest.approx(0.0022171256)


def test_margin_semantics_and_values(pipeline_result: PipelineResult) -> None:
    margin = compute_metrics(pipeline_result)["margin"]
    assert margin["gross_margin_october_ht"] == pytest.approx(44_660.6466667)
    assert margin["weighted_markup_rate_on_sales"] == pytest.approx(0.3730006869)
    assert margin["margin_rate_on_cost"] == pytest.approx(0.5948980791)
    assert margin["negative_markup_references"] == 1
    assert {"taux_marque", "taux_marge_sur_cout"}.issubset(
        pipeline_result.analytic.columns
    )


def test_zero_sales_stock_has_undefined_coverage_not_zero(
    pipeline_result: PipelineResult,
) -> None:
    analytic = pipeline_result.analytic.set_index("product_id")
    for product_id in ["4337", "4355", "5932"]:
        assert analytic.loc[product_id, "stock_quantity"] > 0
        assert analytic.loc[product_id, "total_sales"] == 0
        assert pd.isna(
            analytic.loc[product_id, "couverture_au_rythme_octobre_mois"]
        )
        assert analytic.loc[product_id, "segment_stock"] == "stock_sans_vente_octobre"


def test_stock_reports_raw_and_quarantine_excluded_views(
    pipeline_result: PipelineResult,
) -> None:
    stock = compute_metrics(pipeline_result)["stock"]
    assert stock["matched_stock_units_raw_signed"] == 16_739
    assert stock["matched_stock_value_cost_ht_raw_signed"] == pytest.approx(277_305.77)
    assert stock["matched_stock_units_valid"] == 16_740
    assert stock["matched_stock_value_cost_ht"] == pytest.approx(277_328.07)
    assert stock["stock_without_october_sales_references"] == 3
    assert stock["stock_without_october_sales_value_cost_ht"] == pytest.approx(14_959.40)
    assert stock["potential_stockout_references"] == 22
    assert stock["over_12_months_references"] == 24
    assert stock["over_12_months_value_cost_ht"] == pytest.approx(95_011.92)

