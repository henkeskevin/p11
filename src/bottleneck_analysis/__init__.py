"""Pipeline reproductible d'analyse BottleNeck."""

from .config import AnalysisConfig, find_project_root
from .metrics import compute_metrics
from .pipeline import PipelineResult, run_pipeline

__all__ = [
    "AnalysisConfig",
    "PipelineResult",
    "compute_metrics",
    "find_project_root",
    "run_pipeline",
]

