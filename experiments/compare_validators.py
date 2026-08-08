from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
import statistics
import sys
from time import perf_counter
from typing import Callable

import pandas as pd
import pandera.pandas as pa
from pandera.errors import SchemaErrors


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


REQUIRED = [
    "product_id",
    "onsale_web",
    "price",
    "stock_quantity",
    "stock_status",
    "purchase_price",
]


def fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "product_id": pd.Series(["100", "101", "102"], dtype="string"),
            "onsale_web": [1, 1, 0],
            "price": [20.0, 30.0, 40.0],
            "stock_quantity": [2, 0, 3],
            "stock_status": pd.Series(
                ["instock", "outofstock", "instock"], dtype="string"
            ),
            "purchase_price": [10.0, 12.0, 20.0],
        }
    )


def native_validate(frame: pd.DataFrame) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    missing = [column for column in REQUIRED if column not in frame]
    for column in missing:
        issues.append({"column": column, "index": None, "rule": "required"})
    if missing:
        return issues

    if not isinstance(frame["product_id"].dtype, pd.StringDtype):
        issues.append({"column": "product_id", "index": None, "rule": "dtype"})
    for index in frame.index[frame["product_id"].isna()]:
        issues.append({"column": "product_id", "index": int(index), "rule": "not_null"})
    for index in frame.index[frame["product_id"].duplicated(keep=False)]:
        issues.append({"column": "product_id", "index": int(index), "rule": "unique"})
    checks = {
        "onsale_web": ~frame["onsale_web"].isin([0, 1]),
        "price": frame["price"].isna() | (frame["price"] <= 0),
        "stock_quantity": frame["stock_quantity"].isna()
        | (frame["stock_quantity"] < 0),
        "purchase_price": frame["purchase_price"].isna()
        | (frame["purchase_price"] <= 0),
        "stock_status": ~frame["stock_status"].isin(["instock", "outofstock"]),
    }
    for column, mask in checks.items():
        for index in frame.index[mask.fillna(True)]:
            issues.append({"column": column, "index": int(index), "rule": "domain"})
    expected = pd.Series(
        frame["stock_quantity"].where(frame["stock_quantity"] == 0, 1)
        .map({0: "outofstock", 1: "instock"}),
        index=frame.index,
        dtype="string",
    )
    for index in frame.index[frame["stock_status"] != expected]:
        issues.append(
            {"column": "stock_status", "index": int(index), "rule": "cross_column"}
        )
    return issues


def build_pandera_schema() -> pa.DataFrameSchema:
    return pa.DataFrameSchema(
        {
            "product_id": pa.Column(pa.String, nullable=False, unique=True),
            "onsale_web": pa.Column(int, pa.Check.isin([0, 1])),
            "price": pa.Column(float, pa.Check.gt(0)),
            "stock_quantity": pa.Column(int, pa.Check.ge(0)),
            "stock_status": pa.Column(
                pa.String, pa.Check.isin(["instock", "outofstock"])
            ),
            "purchase_price": pa.Column(float, pa.Check.gt(0)),
        },
        checks=pa.Check(
            lambda data: (
                ((data["stock_quantity"] == 0) & (data["stock_status"] == "outofstock"))
                | ((data["stock_quantity"] > 0) & (data["stock_status"] == "instock"))
            ).all(),
            error="stock_status coherent with stock_quantity",
        ),
        strict=True,
        coerce=False,
    )


PANDERA_SCHEMA = build_pandera_schema()


def pandera_validate(frame: pd.DataFrame) -> list[dict[str, object]]:
    try:
        PANDERA_SCHEMA.validate(frame, lazy=True)
        return []
    except SchemaErrors as error:
        cases = error.failure_cases
        return [
            {
                "column": None if pd.isna(row.column) else str(row.column),
                "index": None if pd.isna(row.index) else row.index,
                "rule": str(row.check),
            }
            for row in cases.itertuples(index=False)
        ]


def cases() -> dict[str, pd.DataFrame]:
    datasets: dict[str, pd.DataFrame] = {}
    value = fixture().drop(columns="purchase_price")
    datasets["missing_column"] = value
    value = fixture()
    value["product_id"] = [100, 101, 102]
    datasets["wrong_key_type"] = value
    value = fixture()
    value.loc[1, "product_id"] = pd.NA
    datasets["null_key"] = value
    value = fixture()
    value.loc[1, "product_id"] = "100"
    datasets["duplicate_key"] = value
    value = fixture()
    value.loc[1, "price"] = -1.0
    datasets["negative_price"] = value
    value = fixture()
    value.loc[1, "purchase_price"] = -1.0
    datasets["negative_purchase_price"] = value
    value = fixture()
    value.loc[1, "stock_quantity"] = -1
    datasets["negative_stock"] = value
    value = fixture()
    value.loc[1, "onsale_web"] = 2
    datasets["invalid_online_flag"] = value
    value = fixture()
    value.loc[0, "stock_status"] = "outofstock"
    datasets["cross_column_status"] = value
    return datasets


def fingerprint(frame: pd.DataFrame) -> str:
    hashed = pd.util.hash_pandas_object(frame, index=True).values.tobytes()
    return hashlib.sha256(hashed).hexdigest()


def evaluate(
    name: str,
    validator: Callable[[pd.DataFrame], list[dict[str, object]]],
    *,
    repetitions: int = 30,
) -> dict[str, object]:
    datasets = cases()
    detected = 0
    localized = 0
    unchanged = True
    for frame in datasets.values():
        before = fingerprint(frame)
        issues = validator(frame)
        unchanged = unchanged and before == fingerprint(frame)
        if issues:
            detected += 1
            if any(issue.get("column") is not None for issue in issues):
                localized += 1
    timings: list[float] = []
    for _ in range(repetitions):
        start = perf_counter()
        for frame in datasets.values():
            validator(frame)
        timings.append((perf_counter() - start) * 1000)

    implementation = (
        inspect.getsource(native_validate)
        if name == "pandas_natif"
        else inspect.getsource(build_pandera_schema) + inspect.getsource(pandera_validate)
    )
    return {
        "option": name,
        "cases": len(datasets),
        "detected_cases": detected,
        "detection_rate": detected / len(datasets),
        "localized_cases": localized,
        "localization_rate": localized / len(datasets),
        "input_unchanged": unchanged,
        "pytest_ready": True,
        "median_runtime_ms_for_9_cases": statistics.median(timings),
        "implementation_lines": len(
            [line for line in implementation.splitlines() if line.strip()]
        ),
    }


def add_weighted_scores(comparison: pd.DataFrame) -> pd.DataFrame:
    runtime = comparison["median_runtime_ms_for_9_cases"]
    lines = comparison["implementation_lines"]
    runtime_score = runtime.min() / runtime
    complexity_score = lines.min() / lines
    comparison = comparison.copy()
    comparison["weighted_score"] = (
        0.40 * comparison["detection_rate"]
        + 0.20 * comparison["localization_rate"]
        + 0.15 * comparison["input_unchanged"].astype(float)
        + 0.10 * comparison["pytest_ready"].astype(float)
        + 0.10 * runtime_score
        + 0.05 * complexity_score
    )
    comparison["decision"] = comparison["option"].map(
        {
            "pandas_natif": "retenu pour le pipeline: diagnostics métier et dépendances minimales",
            "pandera": "conservé comme option de contrôle additionnel, non requis au runtime",
        }
    )
    return comparison.sort_values("weighted_score", ascending=False).reset_index(drop=True)


def main() -> None:
    output = PROJECT_ROOT / "reports" / "tables" / "comparaison_validateurs.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    comparison = pd.DataFrame(
        [
            evaluate("pandas_natif", native_validate),
            evaluate("pandera", pandera_validate),
        ]
    )
    comparison = add_weighted_scores(comparison)
    comparison.to_csv(output, index=False, encoding="utf-8-sig")
    print(comparison.to_json(orient="records", force_ascii=False, indent=2))
    print(json.dumps({"output": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

