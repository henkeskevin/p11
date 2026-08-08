from __future__ import annotations

from pathlib import Path

from bottleneck_analysis.deliverables import validate_deliverables


def test_final_deliverables_are_complete_and_auditable(project_root: Path) -> None:
    checks = validate_deliverables(project_root)
    failures = [check for check in checks if check.status != "pass"]
    assert not failures, failures


def test_archive_manifest_covers_every_preserved_file(project_root: Path) -> None:
    manifest = (project_root / "archive" / "original" / "MANIFEST.md").read_text(
        encoding="utf-8"
    )
    preserved = {
        path.name
        for path in (project_root / "archive" / "original").iterdir()
        if path.is_file() and path.name != "MANIFEST.md"
    }
    assert preserved
    assert all(f"`{name}`" in manifest for name in preserved)
