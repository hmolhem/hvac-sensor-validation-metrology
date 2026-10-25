"""Reusable analyst-side helpers for calibration-model development.

These functions operate only on analyst-visible repository data.
They do not access simulator-only truth or blind validation measurements.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.static_analysis import STATIC_RELEASE_DIR, locate_project_root


def load_static_calibration(
    project_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load only STATIC / CALIBRATION rows plus the public test matrix."""
    root = locate_project_root() if project_root is None else Path(project_root)

    raw_dir = root / STATIC_RELEASE_DIR
    static_df = pd.read_csv(raw_dir / "static_measurements.csv")
    test_matrix_df = pd.read_csv(raw_dir / "test_matrix.csv")

    calibration_df = static_df.loc[
        (static_df["Test_Family"] == "STATIC")
        & (static_df["Analysis_Role"] == "CALIBRATION")
    ].copy()

    return calibration_df, test_matrix_df


def summarize_calibration_test_ids(df: pd.DataFrame) -> pd.DataFrame:
    """Create one calibration-modeling record per CALIBRATION Test_ID."""
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
    summary["Correction_RH"] = -summary["Error_RH_Pre"]

    summary["Condition_ID"] = (
        "RH"
        + summary["RH_Setpoint"].map(lambda x: f"{x:g}")
        + "_T"
        + summary["Temperature_Setpoint_C"].map(lambda x: f"{x:g}")
        + "_"
        + summary["Direction"].astype(str)
    )

    return summary.sort_values(
        [
            "RH_Setpoint",
            "Temperature_Setpoint_C",
            "Direction",
            "Day_ID",
            "Run_ID",
            "Test_ID",
        ]
    ).reset_index(drop=True)


def calibration_design_summary(
    calibration_summary_df: pd.DataFrame,
) -> dict[str, object]:
    """Return the expected CM-001 calibration-design audit quantities."""
    df = calibration_summary_df

    return {
        "N_Test_IDs": int(df["Test_ID"].nunique()),
        "N_RH_Levels": int(df["RH_Setpoint"].nunique()),
        "RH_Levels": sorted(df["RH_Setpoint"].unique().tolist()),
        "N_Temperature_Levels": int(df["Temperature_Setpoint_C"].nunique()),
        "Temperature_Levels_C": sorted(
            df["Temperature_Setpoint_C"].unique().tolist()
        ),
        "Directions": sorted(df["Direction"].astype(str).unique().tolist()),
        "Days": sorted(df["Day_ID"].unique().tolist()),
        "Runs": sorted(df["Run_ID"].unique().tolist()),
        "N_Condition_Groups": int(df["Condition_ID"].nunique()),
        "Samples_Per_Test_ID_Unique": sorted(df["N_Samples"].unique().tolist()),
    }
