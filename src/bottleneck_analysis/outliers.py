from __future__ import annotations

from collections.abc import Callable
from time import perf_counter

import numpy as np
import pandas as pd


def _positive_numeric(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce").astype(float)
    return numeric.where(numeric > 0)


def iqr_upper_flags(values: pd.Series) -> pd.Series:
    numeric = _positive_numeric(values)
    q1, q3 = numeric.quantile([0.25, 0.75])
    threshold = q3 + 1.5 * (q3 - q1)
    return (numeric > threshold).fillna(False)


def zscore_upper_flags(values: pd.Series) -> pd.Series:
    numeric = _positive_numeric(values)
    standard_deviation = numeric.std(ddof=1)
    if not np.isfinite(standard_deviation) or standard_deviation == 0:
        return pd.Series(False, index=values.index)
    score = (numeric - numeric.mean()) / standard_deviation
    return (score > 3.0).fillna(False)


def log_mad_upper_flags(values: pd.Series) -> pd.Series:
    """Flag high multiplicative deviations using a robust log-price score."""

    numeric = _positive_numeric(values)
    logged = np.log(numeric)
    median = logged.median()
    mad = (logged - median).abs().median()
    if not np.isfinite(mad) or mad == 0:
        return pd.Series(False, index=values.index)
    modified_z = 0.6744897501960817 * (logged - median) / mad
    return (modified_z > 3.5).fillna(False)


def mad_upper_flags(values: pd.Series) -> pd.Series:
    """NIST-style modified z-score on the raw positive prices."""

    numeric = _positive_numeric(values)
    median = numeric.median()
    mad = (numeric - median).abs().median()
    if not np.isfinite(mad) or mad == 0:
        return pd.Series(False, index=values.index)
    modified_z = 0.6744897501960817 * (numeric - median) / mad
    return (modified_z > 3.5).fillna(False)


OUTLIER_METHODS: dict[str, Callable[[pd.Series], pd.Series]] = {
    "iqr_prix_brut": iqr_upper_flags,
    "zscore_prix_brut": zscore_upper_flags,
    "mad_prix_brut": mad_upper_flags,
    "mad_log_prix": log_mad_upper_flags,
}


def compare_outlier_methods(
    prices: pd.Series,
    *,
    seed: int = 42,
    injected_count: int = 20,
    multiplier: float = 6.0,
    repetitions: int = 30,
) -> pd.DataFrame:
    """Run a reproducible contamination experiment on representative prices."""

    clean = _positive_numeric(prices).dropna()
    q1, q3 = clean.quantile([0.25, 0.75])
    candidates = clean[(clean >= q1) & (clean <= q3)]
    sample_size = min(injected_count, len(candidates))
    injected_index = candidates.sample(n=sample_size, random_state=seed).index
    contaminated = clean.copy()
    contaminated.loc[injected_index] *= multiplier

    rows: list[dict[str, float | int | str]] = []
    for name, method in OUTLIER_METHODS.items():
        baseline_flags = method(clean)
        contaminated_flags = method(contaminated)
        detected = int(contaminated_flags.reindex(injected_index).sum())
        baseline_set = set(clean.index[baseline_flags])
        stable_contaminated_set = set(
            contaminated.index[contaminated_flags]
        ) - set(injected_index)
        union = baseline_set | stable_contaminated_set
        stability = (
            len(baseline_set & stable_contaminated_set) / len(union) if union else 1.0
        )

        timings: list[float] = []
        for _ in range(repetitions):
            start = perf_counter()
            method(contaminated)
            timings.append((perf_counter() - start) * 1000)

        rows.append(
            {
                "method": name,
                "baseline_alerts": int(baseline_flags.sum()),
                "baseline_alert_rate": float(baseline_flags.mean()),
                "injected_cases": sample_size,
                "injected_detected": detected,
                "injected_recall": detected / sample_size if sample_size else 0.0,
                "stability_jaccard": stability,
                "median_runtime_ms": float(np.median(timings)),
            }
        )
    return pd.DataFrame(rows).sort_values("method").reset_index(drop=True)
