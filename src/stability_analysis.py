"""Reusable helpers for HV-010 stability and drift analysis."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.static_analysis import STATIC_RELEASE_DIR, locate_project_root


def load_stability(
    project_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load stability measurements and public test matrix."""
    root = locate_project_root() if project_root is None else Path(project_root)
    raw_dir = root / STATIC_RELEASE_DIR

    stability_df = pd.read_csv(raw_dir / "stability_measurements.csv")
    test_matrix_df = pd.read_csv(raw_dir / "test_matrix.csv")

    stability_df = stability_df.loc[
        stability_df["Test_Family"].astype(str).str.upper().eq("STABILITY")
    ].copy()

    return stability_df, test_matrix_df


def load_frozen_c1_offset(project_root: Path | None = None) -> float:
    """Load frozen HV-006 C1 constant offset."""
    root = locate_project_root() if project_root is None else Path(project_root)
    record = json.loads(
        (root / "config" / "calibration_model_v1.json").read_text(encoding="utf-8")
    )
    if record["model_id"] != "C1_Constant_Offset":
        raise ValueError("Unexpected calibration model identity.")
    if record["validation_measurements_used"] is not False:
        raise ValueError("Frozen model record failed validation-use integrity check.")
    return float(record["parameters"]["offset_percent_rh"])


def summarize_stability_tests(
    stability_df: pd.DataFrame,
    c1_offset: float,
) -> pd.DataFrame:
    """Return one stability summary row per Test_ID."""
    df = stability_df.copy()
    df["Error_Raw"] = df["RH_DUT"] - df["RH_Reference"]
    df["Error_C1"] = df["Error_Raw"] + c1_offset

    rows: list[dict[str, object]] = []

    for test_id, group in df.groupby("Test_ID", sort=True):
        g = group.sort_values("Elapsed_s")
        row0 = g.iloc[0]

        raw = g["Error_Raw"].to_numpy(dtype=float)
        c1 = g["Error_C1"].to_numpy(dtype=float)

        rows.append(
            {
                "Test_ID": str(test_id),
                "Schedule_Type": str(row0["Schedule_Type"]),
                "Aging_Day": float(row0["Aging_Day"]),
                "RH_Setpoint": float(row0["RH_Setpoint"]),
                "Temperature_Setpoint_C": float(row0["Temperature_Setpoint_C"]),
                "Direction": str(row0["Direction"]).upper(),
                "N": int(len(g)),
                "Reference_Mean": float(g["RH_Reference"].mean()),
                "DUT_Mean": float(g["RH_DUT"].mean()),
                "Raw_MBE": float(np.mean(raw)),
                "Raw_MAE": float(np.mean(np.abs(raw))),
                "Raw_RMSE": float(np.sqrt(np.mean(raw**2))),
                "C1_MBE": float(np.mean(c1)),
                "C1_MAE": float(np.mean(np.abs(c1))),
                "C1_RMSE": float(np.sqrt(np.mean(c1**2))),
                "Error_SD": float(np.std(c1, ddof=1)),
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values(["Schedule_Type", "Aging_Day", "RH_Setpoint", "Test_ID"])
        .reset_index(drop=True)
    )


def linear_trend(x: pd.Series | np.ndarray, y: pd.Series | np.ndarray) -> dict[str, float]:
    """Return ordinary least-squares linear trend and R²."""
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)

    valid = np.isfinite(x_arr) & np.isfinite(y_arr)
    x_arr = x_arr[valid]
    y_arr = y_arr[valid]

    if x_arr.size < 2:
        return {
            "Intercept": float("nan"),
            "Slope_per_Day": float("nan"),
            "Slope_per_30_Days": float("nan"),
            "R2": float("nan"),
        }

    slope, intercept = np.polyfit(x_arr, y_arr, deg=1)
    fitted = intercept + slope * x_arr

    ss_res = float(np.sum((y_arr - fitted) ** 2))
    ss_tot = float(np.sum((y_arr - np.mean(y_arr)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    return {
        "Intercept": float(intercept),
        "Slope_per_Day": float(slope),
        "Slope_per_30_Days": float(30.0 * slope),
        "R2": float(r2),
    }


def weekly_center_drift(test_summary_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute weekly Day-0-referenced center drift and trend summary."""
    weekly = test_summary_df.loc[
        test_summary_df["Schedule_Type"].eq("WEEKLY_CENTER_CHECK")
    ].copy().sort_values("Aging_Day")

    if len(weekly) != 13:
        raise ValueError("Expected 13 weekly center checks.")

    baseline = weekly.loc[np.isclose(weekly["Aging_Day"], 0.0), "C1_MBE"]
    if len(baseline) != 1:
        raise ValueError("Expected exactly one Day-0 weekly baseline.")

    baseline_error = float(baseline.iloc[0])
    weekly["Center_Drift_From_Day0"] = weekly["C1_MBE"] - baseline_error

    drift_trend = linear_trend(
        weekly["Aging_Day"],
        weekly["Center_Drift_From_Day0"],
    )
    scatter_trend = linear_trend(
        weekly["Aging_Day"],
        weekly["Error_SD"],
    )

    day84 = weekly.loc[np.isclose(weekly["Aging_Day"], 84.0)]
    if len(day84) != 1:
        raise ValueError("Expected exactly one Day-84 weekly checkpoint.")

    trend_summary = pd.DataFrame(
        [
            {
                "Metric": "Center_Drift_From_Day0",
                **drift_trend,
                "Day84_Value": float(day84["Center_Drift_From_Day0"].iloc[0]),
                "Max_Abs_Observed": float(
                    weekly["Center_Drift_From_Day0"].abs().max()
                ),
            },
            {
                "Metric": "Within_Test_Error_SD",
                **scatter_trend,
                "Day84_Value": float(day84["Error_SD"].iloc[0]),
                "Max_Abs_Observed": float(weekly["Error_SD"].max()),
            },
        ]
    )

    return weekly.reset_index(drop=True), trend_summary


def monthly_point_drift(
    test_summary_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute Day-30-referenced point drift and monthly span change."""
    monthly = test_summary_df.loc[
        test_summary_df["Schedule_Type"].eq("MONTHLY_MULTI_POINT")
    ].copy().sort_values(["Aging_Day", "RH_Setpoint"])

    if len(monthly) != 9:
        raise ValueError("Expected 9 monthly multi-point tests.")

    baseline = monthly.loc[np.isclose(monthly["Aging_Day"], 30.0), [
        "RH_Setpoint",
        "C1_MBE",
    ]].rename(columns={"C1_MBE": "C1_MBE_Day30"})

    point = monthly.merge(baseline, on="RH_Setpoint", how="left", validate="many_to_one")
    point["Point_Drift_From_Day30"] = point["C1_MBE"] - point["C1_MBE_Day30"]

    span_rows: list[dict[str, float]] = []
    for day, group in monthly.groupby("Aging_Day", sort=True):
        low = group.loc[np.isclose(group["RH_Setpoint"], 30.0), "C1_MBE"]
        high = group.loc[np.isclose(group["RH_Setpoint"], 70.0), "C1_MBE"]
        if len(low) != 1 or len(high) != 1:
            raise ValueError(f"Day {day}: expected one 30 and one 70 %RH point.")
        span_rows.append(
            {
                "Aging_Day": float(day),
                "Span_Error": float(high.iloc[0] - low.iloc[0]),
            }
        )

    span_df = pd.DataFrame(span_rows).sort_values("Aging_Day").reset_index(drop=True)
    baseline_span = float(
        span_df.loc[np.isclose(span_df["Aging_Day"], 30.0), "Span_Error"].iloc[0]
    )
    span_df["Span_Change_From_Day30"] = span_df["Span_Error"] - baseline_span

    return point.reset_index(drop=True), span_df
