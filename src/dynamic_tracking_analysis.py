"""Reusable helpers for HV-009 dynamic tracking analysis."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.static_analysis import STATIC_RELEASE_DIR, locate_project_root


def load_dynamic_tracking(
    project_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load ramp, cyclic, sinusoidal measurements and public test matrix."""
    root = locate_project_root() if project_root is None else Path(project_root)
    raw_dir = root / STATIC_RELEASE_DIR

    ramp_df = pd.read_csv(raw_dir / "ramp_measurements.csv")
    cyclic_df = pd.read_csv(raw_dir / "cyclic_measurements.csv")
    sinusoidal_df = pd.read_csv(raw_dir / "sinusoidal_measurements.csv")
    test_matrix_df = pd.read_csv(raw_dir / "test_matrix.csv")

    return ramp_df, cyclic_df, sinusoidal_df, test_matrix_df


def load_frozen_c1_offset(project_root: Path | None = None) -> float:
    """Load the frozen HV-006 C1 constant offset from JSON."""
    root = locate_project_root() if project_root is None else Path(project_root)
    record = json.loads(
        (root / "config" / "calibration_model_v1.json").read_text(encoding="utf-8")
    )
    if record["model_id"] != "C1_Constant_Offset":
        raise ValueError("Unexpected calibration model identity.")
    if record["validation_measurements_used"] is not False:
        raise ValueError("Frozen model record failed validation-use integrity check.")
    return float(record["parameters"]["offset_percent_rh"])


def error_metrics(error: pd.Series | np.ndarray) -> dict[str, float]:
    """Return standard dynamic error metrics."""
    e = np.asarray(error, dtype=float)
    return {
        "N": int(e.size),
        "MBE": float(np.mean(e)),
        "MAE": float(np.mean(np.abs(e))),
        "RMSE": float(np.sqrt(np.mean(e**2))),
        "Max_Abs_Error": float(np.max(np.abs(e))),
    }


def ramp_metrics_table(ramp_df: pd.DataFrame, c1_offset: float) -> pd.DataFrame:
    """Create one raw/C1 tracking-metric record per ramp Test_ID."""
    rows: list[dict[str, object]] = []

    for test_id, group in ramp_df.groupby("Test_ID", sort=True):
        g = group.sort_values("Elapsed_s").copy()
        raw_error = g["RH_DUT"] - g["RH_Reference"]
        c1_error = raw_error + c1_offset

        raw = error_metrics(raw_error)
        c1 = error_metrics(c1_error)

        row0 = g.iloc[0]
        rows.append(
            {
                "Test_ID": str(test_id),
                "Temperature_Setpoint_C": float(row0["Temperature_Setpoint_C"]),
                "Direction": str(row0["Direction"]).upper(),
                "Repetition": int(row0["Repetition"]),
                **{f"Raw_{k}": v for k, v in raw.items()},
                **{f"C1_{k}": v for k, v in c1.items()},
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values(["Temperature_Setpoint_C", "Direction", "Repetition"])
        .reset_index(drop=True)
    )


def cyclic_cycle_metrics(
    cyclic_df: pd.DataFrame,
    c1_offset: float,
) -> pd.DataFrame:
    """Create one metric record per Session × Cycle_Index."""
    df = cyclic_df.copy()
    df["Direction"] = df["Direction"].astype(str).str.upper()
    df["Error_Raw"] = df["RH_DUT"] - df["RH_Reference"]
    df["Error_C1"] = df["Error_Raw"] + c1_offset

    rows: list[dict[str, object]] = []

    for (session, cycle), group in df.groupby(["Session", "Cycle_Index"], sort=True):
        raw = error_metrics(group["Error_Raw"])
        c1 = error_metrics(group["Error_C1"])

        up = group.loc[group["Direction"].eq("UP"), "Error_C1"]
        down = group.loc[group["Direction"].eq("DOWN"), "Error_C1"]

        up_mean = float(up.mean()) if len(up) else float("nan")
        down_mean = float(down.mean()) if len(down) else float("nan")

        rows.append(
            {
                "Session": int(session),
                "Cycle_Index": int(cycle),
                **{f"Raw_{k}": v for k, v in raw.items()},
                **{f"C1_{k}": v for k, v in c1.items()},
                "C1_Error_UP_Mean": up_mean,
                "C1_Error_DOWN_Mean": down_mean,
                "C1_Direction_Gap": up_mean - down_mean,
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values(["Session", "Cycle_Index"])
        .reset_index(drop=True)
    )


def cyclic_session_summary(cycle_metrics_df: pd.DataFrame) -> pd.DataFrame:
    """Summarize cycle repeatability and descriptive drift per session."""
    rows: list[dict[str, float | int]] = []

    for session, group in cycle_metrics_df.groupby("Session", sort=True):
        g = group.sort_values("Cycle_Index")
        x = g["Cycle_Index"].to_numpy(dtype=float)

        def slope(column: str) -> float:
            y = g[column].to_numpy(dtype=float)
            valid = np.isfinite(x) & np.isfinite(y)
            if valid.sum() < 2:
                return float("nan")
            return float(np.polyfit(x[valid], y[valid], deg=1)[0])

        rows.append(
            {
                "Session": int(session),
                "N_Cycles": int(len(g)),
                "C1_MBE_Mean": float(g["C1_MBE"].mean()),
                "C1_MBE_SD": float(g["C1_MBE"].std(ddof=1)),
                "C1_RMSE_Mean": float(g["C1_RMSE"].mean()),
                "C1_RMSE_SD": float(g["C1_RMSE"].std(ddof=1)),
                "Direction_Gap_Mean": float(g["C1_Direction_Gap"].mean()),
                "Direction_Gap_SD": float(g["C1_Direction_Gap"].std(ddof=1)),
                "C1_MBE_Drift_per_Cycle": slope("C1_MBE"),
                "C1_RMSE_Drift_per_Cycle": slope("C1_RMSE"),
            }
        )

    return pd.DataFrame(rows)


def _harmonic_fit(
    time_s: np.ndarray,
    signal: np.ndarray,
    frequency_hz: float,
) -> dict[str, float]:
    """Fit y = c + a sin(wt) + b cos(wt) at a known frequency."""
    t = np.asarray(time_s, dtype=float)
    y = np.asarray(signal, dtype=float)
    w = 2.0 * np.pi * float(frequency_hz)

    X = np.column_stack(
        [
            np.ones_like(t),
            np.sin(w * t),
            np.cos(w * t),
        ]
    )
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    c, a, b = coef

    fitted = X @ coef
    residual = y - fitted

    amplitude = float(np.hypot(a, b))
    phase_rad = float(np.arctan2(b, a))

    return {
        "Offset": float(c),
        "Amplitude": amplitude,
        "Phase_Rad": phase_rad,
        "Fit_RMSE": float(np.sqrt(np.mean(residual**2))),
    }


def _wrap_pi(angle: float) -> float:
    return float((angle + np.pi) % (2.0 * np.pi) - np.pi)


def sinusoidal_frequency_response(
    sinusoidal_df: pd.DataFrame,
) -> pd.DataFrame:
    """Fit reference and DUT first harmonics and compute gain/phase lag."""
    rows: list[dict[str, float | str]] = []

    for test_id, group in sinusoidal_df.groupby("Test_ID", sort=True):
        g = group.sort_values("Elapsed_s")
        row0 = g.iloc[0]
        frequency = float(row0["Frequency_Hz"])
        period = float(row0["Period_s"])

        ref = _harmonic_fit(
            g["Elapsed_s"].to_numpy(),
            g["RH_Reference"].to_numpy(),
            frequency,
        )
        dut = _harmonic_fit(
            g["Elapsed_s"].to_numpy(),
            g["RH_DUT"].to_numpy(),
            frequency,
        )

        phase_lag = _wrap_pi(ref["Phase_Rad"] - dut["Phase_Rad"])
        omega = 2.0 * np.pi * frequency

        rows.append(
            {
                "Test_ID": str(test_id),
                "Period_s": period,
                "Frequency_Hz": frequency,
                "Reference_Amplitude": ref["Amplitude"],
                "DUT_Amplitude": dut["Amplitude"],
                "Gain": dut["Amplitude"] / ref["Amplitude"],
                "Reference_Phase_Rad": ref["Phase_Rad"],
                "DUT_Phase_Rad": dut["Phase_Rad"],
                "Phase_Lag_Rad": phase_lag,
                "Phase_Lag_Deg": float(np.degrees(phase_lag)),
                "Equivalent_Time_Lag_s": float(phase_lag / omega),
                "Reference_Fit_RMSE": ref["Fit_RMSE"],
                "DUT_Fit_RMSE": dut["Fit_RMSE"],
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values("Frequency_Hz")
        .reset_index(drop=True)
    )
