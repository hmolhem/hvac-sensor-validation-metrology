"""Reusable helpers for HV-007 independent blind validation.

This module loads only analyst-visible STATIC / VALIDATION measurements and
applies already-frozen model parameters. It does not fit or tune calibration
models.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.static_analysis import STATIC_RELEASE_DIR, locate_project_root


def load_static_validation(
    project_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load STATIC / VALIDATION rows and the public test matrix."""
    root = locate_project_root() if project_root is None else Path(project_root)
    raw_dir = root / STATIC_RELEASE_DIR

    static_df = pd.read_csv(raw_dir / "static_measurements.csv")
    test_matrix_df = pd.read_csv(raw_dir / "test_matrix.csv")

    validation_df = static_df.loc[
        (static_df["Test_Family"] == "STATIC")
        & (static_df["Analysis_Role"] == "VALIDATION")
    ].copy()

    return validation_df, test_matrix_df


def load_frozen_calibration_records(
    project_root: Path | None = None,
) -> tuple[dict, dict]:
    """Load frozen deployable C1 and diagnostic C5 JSON records."""
    root = locate_project_root() if project_root is None else Path(project_root)
    config_dir = root / "config"

    c1 = json.loads(
        (config_dir / "calibration_model_v1.json").read_text(encoding="utf-8")
    )
    c5 = json.loads(
        (
            config_dir / "calibration_model_direction_diagnostic_v1.json"
        ).read_text(encoding="utf-8")
    )

    return c1, c5


def summarize_validation_test_ids(df: pd.DataFrame) -> pd.DataFrame:
    """Create one independent-validation record per VALIDATION Test_ID."""
    required = {
        "Test_ID",
        "Test_Family",
        "Analysis_Role",
        "Day_ID",
        "Run_ID",
        "RH_Setpoint",
        "Temperature_Setpoint_C",
        "Direction",
        "Chamber_State",
        "RH_Reference",
        "RH_DUT",
        "Temperature_Reference_C",
        "Temperature_DUT_C",
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
            N_Samples=("RH_DUT", "size"),
            RH_Reference_Mean=("RH_Reference", "mean"),
            RH_DUT_Mean=("RH_DUT", "mean"),
            Temperature_Reference_Mean_C=("Temperature_Reference_C", "mean"),
            Temperature_DUT_Mean_C=("Temperature_DUT_C", "mean"),
            RH_DUT_SD=("RH_DUT", "std"),
            RH_Reference_SD=("RH_Reference", "std"),
        )
    )

    summary["Error_RH_Pre"] = (
        summary["RH_DUT_Mean"] - summary["RH_Reference_Mean"]
    )

    return summary.sort_values(
        [
            "RH_Setpoint",
            "Temperature_Setpoint_C",
            "Direction",
            "Run_ID",
            "Test_ID",
        ]
    ).reset_index(drop=True)
