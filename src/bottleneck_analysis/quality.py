from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd


ISSUE_COLUMNS = [
    "rule_id",
    "source",
    "key",
    "column",
    "raw_value",
    "severity",
    "category",
    "description",
    "action",
]


class DataContractError(ValueError):
    """Raised when a structural contract makes a safe analysis impossible."""


def require_columns(frame: pd.DataFrame, required: Iterable[str], source: str) -> None:
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise DataContractError(f"{source}: colonnes obligatoires absentes: {missing}")


def normalize_identifier(series: pd.Series) -> pd.Series:
    """Normalize key representation without guessing or repairing its meaning."""

    def normalize(value: Any) -> Any:
        if pd.isna(value):
            return pd.NA
        if isinstance(value, (int, np.integer)):
            return str(int(value))
        if isinstance(value, (float, np.floating)) and float(value).is_integer():
            return str(int(value))
        text = str(value).strip()
        return text if text else pd.NA

    return series.map(normalize).astype("string")


def assert_unique_non_null(frame: pd.DataFrame, key: str, source: str) -> None:
    non_null = frame[key].dropna()
    duplicated = non_null[non_null.duplicated(keep=False)]
    if not duplicated.empty:
        examples = sorted(duplicated.astype(str).unique().tolist())[:10]
        raise DataContractError(
            f"{source}: clé {key!r} non unique; exemples={examples}"
        )


def add_row_issues(
    issues: list[dict[str, Any]],
    frame: pd.DataFrame,
    mask: pd.Series,
    *,
    rule_id: str,
    source: str,
    key_column: str,
    value_column: str,
    severity: str,
    category: str,
    description: str,
    action: str,
) -> None:
    selected = frame.loc[mask.fillna(False), [key_column, value_column]]
    for key, value in selected.itertuples(index=False, name=None):
        issues.append(
            {
                "rule_id": rule_id,
                "source": source,
                "key": None if pd.isna(key) else str(key),
                "column": value_column,
                "raw_value": None if pd.isna(value) else str(value),
                "severity": severity,
                "category": category,
                "description": description,
                "action": action,
            }
        )


def add_aggregate_issue(
    issues: list[dict[str, Any]],
    *,
    rule_id: str,
    source: str,
    column: str,
    value: Any,
    severity: str,
    category: str,
    description: str,
    action: str,
) -> None:
    issues.append(
        {
            "rule_id": rule_id,
            "source": source,
            "key": "*",
            "column": column,
            "raw_value": str(value),
            "severity": severity,
            "category": category,
            "description": description,
            "action": action,
        }
    )


def issues_frame(issues: list[dict[str, Any]]) -> pd.DataFrame:
    if not issues:
        return pd.DataFrame(columns=ISSUE_COLUMNS)
    return pd.DataFrame(issues, columns=ISSUE_COLUMNS).sort_values(
        ["severity", "rule_id", "source", "key"], kind="stable"
    ).reset_index(drop=True)

