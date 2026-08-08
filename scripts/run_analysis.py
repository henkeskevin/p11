from __future__ import annotations

import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bottleneck_analysis.config import AnalysisConfig  # noqa: E402
from bottleneck_analysis.reporting import export_analysis  # noqa: E402


def main() -> None:
    run = export_analysis(AnalysisConfig(project_root=PROJECT_ROOT))
    summary = {
        "analytic_rows": len(run.result.analytic),
        "revenue_october_ttc": run.metrics["sales"]["revenue_october_ttc"],
        "units_sold_october": run.metrics["sales"]["units_sold_october"],
        "quality_issues": len(run.result.quality_issues),
        "figures_written": len(run.figures),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

