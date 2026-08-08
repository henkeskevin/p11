from __future__ import annotations

from pathlib import Path
import sys

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bottleneck_analysis.config import AnalysisConfig  # noqa: E402
from bottleneck_analysis.pipeline import PipelineResult, run_pipeline  # noqa: E402


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def pipeline_result(project_root: Path) -> PipelineResult:
    return run_pipeline(AnalysisConfig(project_root=project_root))

