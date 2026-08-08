from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Callable
from zipfile import BadZipFile, ZipFile

import pandas as pd


EXPECTED_ARCHIVE_HASHES = {
    "README.md": "b6d554863a810ec69cc74b245258c57051194ff54e452a8b9e633d4983a2394e",
    "Henkes_Kevin_1_notebook_012026.ipynb": "a2c094641fbeae20bb85c5cc18a9c79b9c497624494bd92605d9c95fe971cdec",
    "Henkes_Kevin_2_presentation_012026.pptx": "56954665b14b6aeb555be449e2fcfe71d8732a1314eb8a3c70cda610b714a54e",
    "prompt.docx": "c3cc4c0904fcf1df03dbdc676edd70b6856ee41f62bd113b8adeaf4df6aa056d",
    "df_merge.csv": "0d89e91d086b8e3c776050486cdf2916b4dbbcd1e5478ccfda6aea3b2bee417c",
    "erp.xlsx": "1179ffa647941447f497026e9e0c16e0b49490ef791f02f541c74df1300b0771",
    "liaison.xlsx": "b3af2411c59789b3cdcced6abad74c00ed4dbae74184215a89b00dfb8a682c02",
    "web.xlsx": "24f3ecdb4ea97cbc027f18d6b16ea1c9a97ffcbb0c9c50a43b9348ca4b1c9d48",
}

EXPECTED_FIGURE_STEMS = {
    "01_rapprochement_sources",
    "02_top10_ca_octobre",
    "03_pareto_ca_octobre",
    "04_prix_inhabituels",
    "05_segments_stock",
    "06_marge_ponderee_type",
    "07_correlations_spearman",
    "08_typologie_alertes",
    "09_stock_sans_vente_octobre",
    "10_anomalie_marge_reference_4355",
    "11_prix_vs_ventes_octobre",
}

EXPECTED_DOCS = {
    "audit_initial.md",
    "cahier_des_charges.md",
    "matrice_exigences_preuves.md",
    "backlog_planning_risques.md",
    "veille_metier_technologique.md",
    "registre_experiences_ia.md",
    "registre_ameliorations.md",
    "synthese_codir.md",
    "synthese_recruteur.md",
    "limites_biais.md",
}


@dataclass(frozen=True)
class Check:
    check_id: str
    status: str
    detail: str
    evidence: str


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check(
    check_id: str,
    evidence: str,
    validator: Callable[[], str],
) -> Check:
    try:
        detail = validator()
    except Exception as exc:  # noqa: BLE001 - each failure belongs in the audit log
        return Check(check_id, "fail", f"{type(exc).__name__}: {exc}", evidence)
    return Check(check_id, "pass", detail, evidence)


def _validate_archive(root: Path) -> str:
    archive = root / "archive" / "original"
    mismatches = []
    for name, expected in EXPECTED_ARCHIVE_HASHES.items():
        path = archive / name
        if not path.is_file():
            mismatches.append(f"missing:{name}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            mismatches.append(f"hash:{name}:{actual}")
    if mismatches:
        raise AssertionError("; ".join(mismatches))
    return f"{len(EXPECTED_ARCHIVE_HASHES)} copies bit-à-bit conformes"


def _validate_raw_sources(root: Path) -> str:
    for name in ["erp.xlsx", "liaison.xlsx", "web.xlsx"]:
        expected = EXPECTED_ARCHIVE_HASHES[name]
        for folder in [root / "data" / "raw", root / "archive" / "original"]:
            actual = sha256_file(folder / name)
            if actual != expected:
                raise AssertionError(f"{folder / name}: {actual} != {expected}")
    return "3 sources structurées et archivées sans modification"


def _validate_notebook(root: Path) -> str:
    path = root / "notebooks" / "BottleNeck_analyse_portfolio.ipynb"
    notebook = json.loads(path.read_text(encoding="utf-8"))
    cells = notebook.get("cells", [])
    code_cells = [cell for cell in cells if cell.get("cell_type") == "code"]
    counts = [cell.get("execution_count") for cell in code_cells]
    errors = [
        output
        for cell in code_cells
        for output in cell.get("outputs", [])
        if output.get("output_type") == "error"
    ]
    if len(cells) != 24 or len(code_cells) != 12:
        raise AssertionError(f"structure inattendue: {len(cells)} cellules, {len(code_cells)} code")
    if any(count is None for count in counts):
        raise AssertionError(f"cellules non exécutées: {counts}")
    if errors:
        raise AssertionError(f"{len(errors)} sortie(s) d'erreur")
    return f"24 cellules, 12 cellules code exécutées, 0 erreur"


def _validate_metrics(root: Path) -> str:
    path = root / "reports" / "tables" / "indicateurs_cles.json"
    metrics = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        ("data_quality", "matched_web_products"): 714,
        ("sales", "revenue_october_ttc"): 143680.10,
        ("sales", "units_sold_october"): 5751.0,
        ("sales", "references_for_80pct_revenue"): 435,
        ("margin", "gross_margin_october_ht"): 44660.64666666667,
        ("stock", "over_12_months_references"): 24,
    }
    for keys, value in expected.items():
        actual: Any = metrics
        for key in keys:
            actual = actual[key]
        if isinstance(value, float):
            if abs(float(actual) - value) > 1e-6:
                raise AssertionError(f"{'.'.join(keys)}={actual}, attendu {value}")
        elif actual != value:
            raise AssertionError(f"{'.'.join(keys)}={actual}, attendu {value}")
    if metrics["sales"]["reconciliation_difference"] != 0:
        raise AssertionError("le recalcul indépendant du CA ne se réconcilie pas")
    return "KPI clés réconciliés, écart CA indépendant = 0,00 €"


def _validate_exports(root: Path) -> str:
    tables = root / "reports" / "tables"
    required_tables = {
        "audit_jointures.csv",
        "avertissements_chargement.csv",
        "baseline_execution.json",
        "comparaison_methodes_outliers.csv",
        "comparaison_selection_lignes_web.csv",
        "comparaison_validateurs.csv",
        "indicateurs_cles.json",
        "priorites_stock.csv",
        "registre_qualite.csv",
        "top20_ca_octobre.csv",
    }
    missing_tables = sorted(name for name in required_tables if not (tables / name).is_file())
    if missing_tables:
        raise AssertionError(f"tables manquantes: {missing_tables}")
    analytic = pd.read_csv(root / "data" / "processed" / "catalogue_web_analyse.csv")
    registry = pd.read_csv(tables / "registre_qualite.csv")
    if len(analytic) != 714 or len(registry) != 165:
        raise AssertionError(f"volumes inattendus: analytique={len(analytic)}, qualité={len(registry)}")
    figures = root / "reports" / "figures"
    for stem in EXPECTED_FIGURE_STEMS:
        for suffix in ["png", "svg"]:
            path = figures / f"{stem}.{suffix}"
            if not path.is_file() or path.stat().st_size == 0:
                raise AssertionError(f"figure absente ou vide: {path.name}")
    return "714 lignes analytiques, 165 constats qualité, 11 figures PNG+SVG"


def _validate_docs(root: Path) -> str:
    missing = sorted(name for name in EXPECTED_DOCS if not (root / "docs" / name).is_file())
    if missing:
        raise AssertionError(f"documents manquants: {missing}")
    if "année et l'horodatage" not in (root / "README.md").read_text(encoding="utf-8"):
        raise AssertionError("la limite sur l'année/horodatage n'est pas visible dans le README")
    return f"README et {len(EXPECTED_DOCS)} documents de preuve présents"


def _pptx_text(xml: bytes) -> str:
    return " ".join(
        re.sub(r"<[^>]+>", "", item.decode("utf-8", errors="replace"))
        for item in re.findall(rb"<a:t>.*?</a:t>", xml, flags=re.DOTALL)
    )


def _validate_presentation(root: Path) -> str:
    path = root / "reports" / "BottleNeck_CODIR.pptx"
    if not path.is_file() or path.stat().st_size == 0:
        raise AssertionError("présentation absente ou vide")
    try:
        with ZipFile(path) as archive:
            bad = archive.testzip()
            if bad:
                raise AssertionError(f"entrée ZIP corrompue: {bad}")
            names = archive.namelist()
            slides = sorted(
                name for name in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
            )
            notes = sorted(
                name
                for name in names
                if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", name)
            )
            if len(slides) != 12 or len(notes) != 12:
                raise AssertionError(f"slides={len(slides)}, notes={len(notes)}")
            for note in notes:
                if "[Sources]" not in _pptx_text(archive.read(note)):
                    raise AssertionError(f"bloc Sources absent: {note}")
            deck_text = " ".join(_pptx_text(archive.read(slide)) for slide in slides)
            required = [
                "BottleNeck",
                "143 680 €",
                "95 012 €",
                "Prix–volumes",
                "Décisions, responsables et échéances",
            ]
            missing = [value for value in required if value not in deck_text]
            if missing:
                raise AssertionError(f"titres/KPI absents: {missing}")
    except BadZipFile as exc:
        raise AssertionError("paquet PPTX illisible") from exc
    return "12 slides, paquet lisible, 12 blocs de notes [Sources]"


def validate_deliverables(root: Path) -> list[Check]:
    return [
        _check("archive_original", "archive/original/MANIFEST.md", lambda: _validate_archive(root)),
        _check("sources_immuables", "data/raw/", lambda: _validate_raw_sources(root)),
        _check(
            "notebook_execute",
            "notebooks/BottleNeck_analyse_portfolio.ipynb",
            lambda: _validate_notebook(root),
        ),
        _check("kpi_reconcilies", "reports/tables/indicateurs_cles.json", lambda: _validate_metrics(root)),
        _check("exports", "reports/figures/ et reports/tables/", lambda: _validate_exports(root)),
        _check("documentation", "README.md et docs/", lambda: _validate_docs(root)),
        _check("presentation", "reports/BottleNeck_CODIR.pptx", lambda: _validate_presentation(root)),
    ]


def checks_as_dicts(checks: list[Check]) -> list[dict[str, str]]:
    return [asdict(check) for check in checks]
