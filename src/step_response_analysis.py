"""Reusable helpers for HV-008 dynamic step-response analysis.

The functions use analyst-visible measured data only. RH_Command is treated as
the commanded chamber transition, while RH_Reference is the measured reference
trajectory. No simulator-only truth is accessed.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.static_analysis import STATIC_RELEASE_DIR, locate_project_root


STEP_FILE = "dynamic_step_measurements.csv"


def load_dynamic_step(
    project_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load DYNAMIC_STEP measurements and the public test matrix."""
    root = locate_project_root() if project_root is None else Path(project_root)
    raw_dir = root / STATIC_RELEASE_DIR

    step_df = pd.read_csv(raw_dir / STEP_FILE)
    test_matrix_df = pd.read_csv(raw_dir / "test_matrix.csv")

    step_df = step_df.loc[
        step_df["Test_Family"].astype(str).str.upper().eq("DYNAMIC_STEP")
    ].copy()

    return step_df, test_matrix_df


def detect_command_transition(test_df: pd.DataFrame) -> float:
    """Return first elapsed time at which RH_Command changes from its initial value."""
    df = test_df.sort_values("Elapsed_s")
    initial = float(df["RH_Command"].iloc[0])

    changed = ~np.isclose(
        df["RH_Command"].to_numpy(dtype=float),
        initial,
        rtol=0.0,
        atol=1e-12,
    )
    indices = np.flatnonzero(changed)

    if indices.size == 0:
        raise ValueError("No RH_Command transition detected.")

    return float(df["Elapsed_s"].iloc[indices[0]])


def _linear_crossing_time(
    time: np.ndarray,
    progress: np.ndarray,
    threshold: float,
    start_time: float,
) -> float:
    """Return first linearly interpolated post-start threshold crossing."""
    valid = np.isfinite(time) & np.isfinite(progress) & (time >= start_time)
    t = time[valid]
    p = progress[valid]

    if t.size == 0:
        return float("nan")

    reached = np.flatnonzero(p >= threshold)
    if reached.size == 0:
        return float("nan")

    j = int(reached[0])

    if j == 0:
        return float(t[0])

    t0, t1 = float(t[j - 1]), float(t[j])
    p0, p1 = float(p[j - 1]), float(p[j])

    if np.isclose(p1, p0):
        return t1

    fraction = (threshold - p0) / (p1 - p0)
    return t0 + float(fraction) * (t1 - t0)


def response_metrics(
    test_df: pd.DataFrame,
    signal_column: str,
    baseline_tail_s: float = 20.0,
    final_tail_s: float = 30.0,
    settling_fraction: float = 0.02,
) -> dict[str, float]:
    """Extract robust, direction-invariant step-response metrics for one signal."""
    df = test_df.sort_values("Elapsed_s").reset_index(drop=True)

    time = df["Elapsed_s"].to_numpy(dtype=float)
    signal = df[signal_column].to_numpy(dtype=float)
    t_command = detect_command_transition(df)

    pre = df.loc[df["Elapsed_s"] < t_command].copy()
    if pre.empty:
        raise ValueError("No pre-transition samples available.")

    baseline_start = max(
        float(pre["Elapsed_s"].min()),
        t_command - baseline_tail_s,
    )
    initial_mask = (
        (df["Elapsed_s"] >= baseline_start)
        & (df["Elapsed_s"] < t_command)
    )

    t_end = float(df["Elapsed_s"].max())
    final_start = t_end - final_tail_s + 1.0
    final_mask = df["Elapsed_s"] >= final_start

    initial_level = float(df.loc[initial_mask, signal_column].median())
    final_level = float(df.loc[final_mask, signal_column].median())
    amplitude = final_level - initial_level

    if np.isclose(amplitude, 0.0):
        raise ValueError(
            f"{signal_column}: response amplitude is approximately zero."
        )

    progress = (signal - initial_level) / amplitude

    t10_abs = _linear_crossing_time(
        time,
        progress,
        threshold=0.10,
        start_time=t_command,
    )
    t63_abs = _linear_crossing_time(
        time,
        progress,
        threshold=1.0 - np.exp(-1.0),
        start_time=t_command,
    )
    t90_abs = _linear_crossing_time(
        time,
        progress,
        threshold=0.90,
        start_time=t_command,
    )

    tolerance = settling_fraction * abs(amplitude)
    post_idx = np.flatnonzero(time >= t_command)
    settling_abs = float("nan")

    for idx in post_idx:
        if np.all(np.abs(signal[idx:] - final_level) <= tolerance):
            settling_abs = float(time[idx])
            break

    direction_sign = 1.0 if amplitude > 0 else -1.0
    post_signal = signal[time >= t_command]
    overshoot_amount = np.max(
        np.maximum(
            direction_sign * (post_signal - final_level),
            0.0,
        )
    )
    overshoot_pct = 100.0 * float(overshoot_amount) / abs(amplitude)

    return {
        "t_command_s": t_command,
        "initial_level": initial_level,
        "final_level": final_level,
        "amplitude": float(amplitude),
        "t10_abs_s": t10_abs,
        "t63_abs_s": t63_abs,
        "t90_abs_s": t90_abs,
        "dead_time_s": t10_abs - t_command,
        "tau_s": t63_abs - t_command,
        "t90_s": t90_abs - t_command,
        "settling_abs_s": settling_abs,
        "settling_time_s": (
            settling_abs - t_command
            if np.isfinite(settling_abs)
            else float("nan")
        ),
        "overshoot_pct": overshoot_pct,
    }


def summarize_step_test(test_df: pd.DataFrame) -> dict[str, object]:
    """Extract reference, DUT, and relative-lag metrics for one Test_ID."""
    if test_df["Test_ID"].nunique() != 1:
        raise ValueError("summarize_step_test expects exactly one Test_ID.")

    row0 = test_df.sort_values("Elapsed_s").iloc[0]

    ref = response_metrics(test_df, "RH_Reference")
    dut = response_metrics(test_df, "RH_DUT")

    result: dict[str, object] = {
        "Test_ID": str(row0["Test_ID"]),
        "Temperature_Setpoint_C": float(row0["Temperature_Setpoint_C"]),
        "Direction": str(row0["Direction"]).upper(),
        "Repetition": int(row0["Repetition"]),
        "N_Samples": int(len(test_df)),
        "t_command_s": float(ref["t_command_s"]),
    }

    for prefix, metrics in (("Reference", ref), ("DUT", dut)):
        for key, value in metrics.items():
            if key == "t_command_s":
                continue
            result[f"{prefix}_{key}"] = value

    result["Lag_t10_s"] = float(dut["t10_abs_s"] - ref["t10_abs_s"])
    result["Lag_tau_s"] = float(dut["t63_abs_s"] - ref["t63_abs_s"])
    result["Lag_t90_s"] = float(dut["t90_abs_s"] - ref["t90_abs_s"])

    return result


def build_step_metrics_table(step_df: pd.DataFrame) -> pd.DataFrame:
    """Return one dynamic-step metric row per Test_ID."""
    rows = [
        summarize_step_test(group)
        for _, group in step_df.groupby("Test_ID", sort=True)
    ]

    return (
        pd.DataFrame(rows)
        .sort_values(
            ["Temperature_Setpoint_C", "Direction", "Repetition", "Test_ID"]
        )
        .reset_index(drop=True)
    )
