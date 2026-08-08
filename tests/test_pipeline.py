from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import pytest

from bottleneck_analysis.pipeline import PipelineResult
from bottleneck_analysis.quality import DataContractError, assert_unique_non_null


EXPECTED_HASHES = {
    "erp.xlsx": "1179ffa647941447f497026e9e0c16e0b49490ef791f02f541c74df1300b0771",
    "web.xlsx": "24f3ecdb4ea97cbc027f18d6b16ea1c9a97ffcbb0c9c50a43b9348ca4b1c9d48",
    "liaison.xlsx": "b3af2411c59789b3cdcced6abad74c00ed4dbae74184215a89b00dfb8a682c02",
}


def test_raw_sources_are_exact_preserved_copies(project_root: Path) -> None:
    for name, expected in EXPECTED_HASHES.items():
        payload = (project_root / "data" / "raw" / name).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == expected


def test_source_contracts_and_cardinalities(pipeline_result: PipelineResult) -> None:
    result = pipeline_result
    assert len(result.erp) == 825
    assert result.erp["product_id"].is_unique
    assert len(result.web_products) == 716
    assert result.web_products["sku"].notna().sum() == 714
    assert result.web_products["sku"].dropna().is_unique
    assert result.liaison["id_web"].notna().sum() == 734
    assert result.liaison["id_web"].dropna().is_unique
    assert len(result.analytic) == 714
    assert result.analytic["product_id"].is_unique
    assert result.analytic["id_web"].is_unique


def test_join_audit_reconciles_all_rows(pipeline_result: PipelineResult) -> None:
    audit = pipeline_result.join_audit.set_index(["join", "status"])["rows"]
    assert audit["ERP ↔ LIAISON", "both"] == 825
    assert audit["ERP ↔ LIAISON", "left_only"] == 0
    assert audit["LIAISON (clé Web non vide) ↔ WEB produits", "both"] == 714
    assert audit["LIAISON (clé Web non vide) ↔ WEB produits", "left_only"] == 20
    assert audit["LIAISON (clé Web non vide) ↔ WEB produits", "right_only"] == 0


def test_no_silent_sign_or_status_correction(pipeline_result: PipelineResult) -> None:
    erp = pipeline_result.erp.set_index("product_id")
    analytic = pipeline_result.analytic.set_index("product_id")
    assert erp.loc["4233", "price"] == -20
    assert erp.loc["4973", "stock_quantity"] == -10
    assert erp.loc["5700", "stock_quantity"] == -1
    assert erp.loc["4039", "stock_status"] == "outofstock"
    assert erp.loc["4885", "stock_status"] == "instock"
    assert analytic.loc["5700", "stock_quantity"] == -1
    assert analytic.loc["5700", "segment_stock"] == "quarantaine"


def test_null_skus_are_not_matched_or_invented(pipeline_result: PipelineResult) -> None:
    assert pipeline_result.web_products["sku"].isna().sum() == 2
    assert pipeline_result.analytic["id_web"].notna().all()
    assert not pipeline_result.analytic["id_web"].astype(str).str.startswith("id_inconnu").any()


def test_cross_source_status_mismatches_are_reported(
    pipeline_result: PipelineResult,
) -> None:
    rules = pipeline_result.quality_issues.groupby("rule_id").size().to_dict()
    assert rules["erp_marked_online_but_web_missing"] == 3
    assert rules["web_sales_while_erp_offline"] == 1
    row = pipeline_result.quality_issues.loc[
        pipeline_result.quality_issues["rule_id"] == "web_sales_while_erp_offline"
    ].iloc[0]
    assert row["key"] == "4200"


def test_duplicate_non_null_key_fails_fast() -> None:
    frame = pd.DataFrame({"id_web": ["A", "A", None]})
    with pytest.raises(DataContractError, match="non unique"):
        assert_unique_non_null(frame, "id_web", "fixture")

