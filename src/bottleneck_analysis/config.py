from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    """Return the nearest parent containing ``pyproject.toml``."""

    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate
    raise FileNotFoundError(
        "Racine du projet introuvable : pyproject.toml absent des répertoires parents."
    )


@dataclass(frozen=True)
class AnalysisConfig:
    project_root: Path
    vat_rate: float = 0.20
    sales_period: str = "octobre"
    stock_snapshot_date: str = "31 octobre"

    @property
    def raw_dir(self) -> Path:
        return self.project_root / "data" / "raw"

    @property
    def processed_dir(self) -> Path:
        return self.project_root / "data" / "processed"

    @property
    def figures_dir(self) -> Path:
        return self.project_root / "reports" / "figures"

    @property
    def tables_dir(self) -> Path:
        return self.project_root / "reports" / "tables"

    @classmethod
    def default(cls, start: Path | None = None) -> "AnalysisConfig":
        return cls(project_root=find_project_root(start))

