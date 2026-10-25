"""Reusable analyst-side helpers for static sensor-metrology analysis.

These functions operate only on analyst-visible repository data.
They do not access simulator-only truth.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


STATIC_RELEASE_DIR = Path("data/raw/vsm_lab_data_v1_1")


def locate_project_root(start: Path | None = None) -> Path:
    """Locate the repository root from the current directory or its parents."""
    current = Path.cwd() if start is None else Path(start).resolve()

    candidates = [current, *current.parents]

    for candidate in candidates:
        if (candidate / STATIC_RELEASE_DIR).exists():
            return candidate

    raise FileNotFoundError(
        "Could not locate repository root containing "
        "'data/raw/vsm_lab_data_v1_1'."
    )


def load_static_characterization(
    project_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load frozen static data and return CHARACTERIZATION rows plus test matrix."""
    root = locate_project_root() if project_root is None else Path(project_root)

    raw_dir = root / STATIC_RELEASE_DIR
    static_df = pd.read_csv(raw_dir / "static_measurements.csv")
    test_matrix_df = pd.read_csv(raw_dir / "test_matrix.csv")

    characterization_df = static_df.loc[
        (static_df["Test_Family"] == "STATIC")
        & (static_df["Analysis_Role"] == "CHARACTERIZATION")
    ].copy()

    return characterization_df, test_matrix_df


def add_rh_error_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with signed and absolute DUT-reference RH error."""
    result = df.copy()
    result["Error_RH"] = result["RH_DUT"] - result["RH_Reference"]
    result["Abs_Error_RH"] = result["Error_RH"].abs()
    return result


def summarize_test_ids(df: pd.DataFrame) -> pd.DataFrame:
    """Create one static summary record per Test_ID."""
    required = {
        "Test_ID",
        "Test_Family",
        "Analysis_Role",
        "RH_Setpoint",
        "Temperature_Setpoint_C",
        "Direction",
        "Day_ID",
        "Run_ID",
        "Chamber_State",
        "RH_Reference",
        "RH_DUT",
        "Error_RH",
    }
    missing = sorted(required.difference(df.columns))
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    summary = (
        df.groupby("Test_ID", as_index=False)
        .agg(
            Test_Family=("Test_Family", "first"),
            Analysis_Role=("Analysis_Role", "first"),
            RH_Setpoint=("RH_Setpoint", "first"),
            Temperature_Setpoint_C=("Temperature_Setpoint_C", "first"),
            Direction=("Direction", "first"),
            Day_ID=("Day_ID", "first"),
            Run_ID=("Run_ID", "first"),
            Chamber_State=("Chamber_State", "first"),
            N_Samples=("Error_RH", "size"),
            RH_Reference_Mean=("RH_Reference", "mean"),
            RH_DUT_Mean=("RH_DUT", "mean"),
            Mean_Error_RH=("Error_RH", "mean"),
            Median_Error_RH=("Error_RH", "median"),
            Std_Error_RH=("Error_RH", "std"),
            Min_Error_RH=("Error_RH", "min"),
            Max_Error_RH=("Error_RH", "max"),
        )
    )

    summary["Range_Error_RH"] = (
        summary["Max_Error_RH"] - summary["Min_Error_RH"]
    )

    return summary


def pooled_within_test_sd(
    test_summary_df: pd.DataFrame,
    sd_column: str = "Std_Error_RH",
    n_column: str = "N_Samples",
) -> float:
    """Calculate pooled within-Test_ID standard deviation."""
    valid = test_summary_df[[sd_column, n_column]].dropna().copy()

    dof = valid[n_column] - 1
    numerator = (dof * valid[sd_column] ** 2).sum()
    denominator = dof.sum()

    if denominator <= 0:
        raise ValueError("Insufficient degrees of freedom for pooled SD.")

    return float(np.sqrt(numerator / denominator))


def matched_level_pairs(
    df: pd.DataFrame,
    match_keys: Iterable[str],
    level_column: str,
    level_a,
    level_b,
    value_column: str,
    label_a: str,
    label_b: str,
) -> pd.DataFrame:
    """Create matched pairs for two levels of one factor.

    The returned difference is always level_b minus level_a.
    """
    keys = list(match_keys)

    a = (
        df.loc[df[level_column] == level_a, keys + [value_column]]
        .rename(columns={value_column: label_a})
    )
    b = (
        df.loc[df[level_column] == level_b, keys + [value_column]]
        .rename(columns={value_column: label_b})
    )

    paired = a.merge(
        b,
        on=keys,
        how="outer",
        indicator=True,
        validate="one_to_one",
    )

    paired["Pair_Complete"] = paired["_merge"].eq("both")
    paired["Difference"] = paired[label_b] - paired[label_a]

    return paired.sort_values(keys).reset_index(drop=True)


def paired_difference_metrics(
    paired_df: pd.DataFrame,
    difference_column: str = "Difference",
) -> dict[str, float]:
    """Summarize complete paired differences."""
    values = paired_df.loc[
        paired_df["Pair_Complete"], difference_column
    ].dropna()

    if values.empty:
        raise ValueError("No complete matched pairs available.")

    return {
        "N_Matched_Pairs": int(values.size),
        "Mean_Difference": float(values.mean()),
        "Median_Difference": float(values.median()),
        "Std_Difference": float(values.std(ddof=1)),
        "RMS_Difference": float(np.sqrt(np.mean(values**2))),
        "Min_Difference": float(values.min()),
        "Max_Difference": float(values.max()),
        "Mean_Abs_Difference": float(values.abs().mean()),
    }
