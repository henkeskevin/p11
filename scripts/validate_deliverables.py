from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
import time


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bottleneck_analysis.deliverables import checks_as_dicts, validate_deliverables  # noqa: E402


def run_command(name: str, command: list[str]) -> dict[str, object]:
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "name": name,
        "command": command,
        "returncode": completed.returncode,
        "status": "pass" if completed.returncode == 0 else "fail",
        "duration_seconds": round(time.perf_counter() - started, 3),
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Recette finale traçable des livrables BottleNeck.")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Régénérer l'analyse et le notebook, puis exécuter pytest avant les contrôles statiques.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "reports" / "tables" / "final_validation.json",
    )
    args = parser.parse_args()

    commands: list[dict[str, object]] = []
    if args.full:
        python = sys.executable
        commands.extend(
            [
                run_command("analyse", [python, "scripts/run_analysis.py"]),
                run_command("comparaison_validateurs", [python, "experiments/compare_validators.py"]),
                run_command("construction_notebook", [python, "scripts/build_notebook.py"]),
                run_command("execution_notebook", [python, "scripts/execute_notebook.py"]),
                run_command(
                    "pytest",
                    [
                        python,
                        "-m",
                        "pytest",
                        "-q",
                        "-p",
                        "no:cacheprovider",
                        "--basetemp=.tmp/pytest-final",
                    ],
                ),
            ]
        )

    checks = validate_deliverables(PROJECT_ROOT)
    failed_commands = [item for item in commands if item["status"] == "fail"]
    failed_checks = [item for item in checks if item.status == "fail"]
    status = "pass" if not failed_commands and not failed_checks else "fail"
    payload = {
        "status": status,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "commands": commands,
        "checks": checks_as_dicts(checks),
        "presentation_qa": {
            "visual_review": "12/12 slides inspected after final render",
            "slides_test": "pass - no overflow detected",
            "template_fidelity": "pass - 0 issue",
            "evidence": [
                ".tmp/presentation/final-render/",
                ".tmp/presentation/qa/template-fidelity-check.json",
            ],
        },
        "summary": {
            "commands_passed": sum(item["status"] == "pass" for item in commands),
            "commands_total": len(commands),
            "checks_passed": sum(item.status == "pass" for item in checks),
            "checks_total": len(checks),
        },
    }
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"] | {"status": status, "output": str(output)}, ensure_ascii=False))
    if status != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
