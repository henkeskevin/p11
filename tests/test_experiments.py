from __future__ import annotations

import pytest

from bottleneck_analysis.experiments import compare_web_selection_methods
from bottleneck_analysis.outliers import compare_outlier_methods, mad_upper_flags
from bottleneck_analysis.pipeline import PipelineResult


def test_web_selection_experiment_proves_order_risk(
    pipeline_result: PipelineResult,
) -> None:
    comparison = compare_web_selection_methods(pipeline_result).set_index("method")
    assert comparison.loc["filtre_semantique_product", "revenue_ttc"] == pytest.approx(
        143_680.10
    )
    assert comparison.loc["filtre_attachment", "revenue_ttc"] == pytest.approx(
        153_748.10
    )
    assert comparison.loc[
        "dedoublonnage_garder_premiere_ligne", "revenue_difference_vs_product"
    ] == pytest.approx(10_068.00)
    assert comparison.loc[
        "somme_de_toutes_les_lignes", "relative_difference_vs_product"
    ] == pytest.approx(1.0700723384)


def test_mad_wins_predefined_outlier_experiment(
    pipeline_result: PipelineResult,
) -> None:
    comparison = compare_outlier_methods(pipeline_result.analytic["price"]).set_index(
        "method"
    )
    assert comparison.loc["mad_prix_brut", "baseline_alerts"] == 33
    assert comparison.loc["mad_prix_brut", "baseline_alert_rate"] < 0.05
    assert comparison.loc["mad_prix_brut", "injected_recall"] == 1.0
    assert comparison.loc["mad_prix_brut", "stability_jaccard"] > 0.90
    assert comparison.loc["mad_prix_brut", "injected_recall"] > comparison.loc[
        "iqr_prix_brut", "injected_recall"
    ]


def test_statistical_price_flags_never_include_invalid_non_positive_prices(
    pipeline_result: PipelineResult,
) -> None:
    flags = mad_upper_flags(pipeline_result.erp["price"])
    assert not flags[pipeline_result.erp["price"] <= 0].any()
    assert (pipeline_result.erp.loc[flags, "price"] > 0).all()

