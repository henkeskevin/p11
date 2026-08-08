from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import pandas as pd

from .config import AnalysisConfig
from .experiments import compare_web_selection_methods
from .metrics import compute_metrics, top_products_table
from .outliers import compare_outlier_methods
from .pipeline import PipelineResult, run_pipeline
from .visuals import generate_figures


@dataclass
class AnalysisRun:
    result: PipelineResult
    metrics: dict[str, object]
    outlier_comparison: pd.DataFrame
    web_selection_comparison: pd.DataFrame
    figures: list[Path]


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def export_analysis(config: AnalysisConfig) -> AnalysisRun:
    config.processed_dir.mkdir(parents=True, exist_ok=True)
    config.tables_dir.mkdir(parents=True, exist_ok=True)
    result = run_pipeline(config)
    metrics = compute_metrics(result)
    outlier_comparison = compare_outlier_methods(result.analytic["price"])
    web_selection_comparison = compare_web_selection_methods(result)

    _write_csv(result.analytic, config.processed_dir / "catalogue_web_analyse.csv")
    _write_csv(result.catalogue, config.processed_dir / "catalogue_erp_rapproche.csv")
    _write_csv(result.quality_issues, config.tables_dir / "registre_qualite.csv")
    _write_csv(result.join_audit, config.tables_dir / "audit_jointures.csv")
    _write_csv(result.loading_warnings, config.tables_dir / "avertissements_chargement.csv")
    _write_csv(top_products_table(result, 20), config.tables_dir / "top20_ca_octobre.csv")
    _write_csv(
        result.analytic[
            [
                "product_id",
                "id_web",
                "product_type",
                "total_sales",
                "stock_quantity",
                "couverture_au_rythme_octobre_mois",
                "valeur_stock_cout_ht",
                "segment_stock",
            ]
        ].sort_values(["segment_stock", "valeur_stock_cout_ht"], ascending=[True, False]),
        config.tables_dir / "priorites_stock.csv",
    )
    _write_csv(outlier_comparison, config.tables_dir / "comparaison_methodes_outliers.csv")
    _write_csv(
        web_selection_comparison,
        config.tables_dir / "comparaison_selection_lignes_web.csv",
    )
    with (config.tables_dir / "indicateurs_cles.json").open("w", encoding="utf-8") as stream:
        json.dump(metrics, stream, ensure_ascii=False, indent=2, allow_nan=False)

    figures = generate_figures(result, config.figures_dir)
    return AnalysisRun(
        result=result,
        metrics=metrics,
        outlier_comparison=outlier_comparison,
        web_selection_comparison=web_selection_comparison,
        figures=figures,
    )

