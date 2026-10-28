"""Reusable helpers for HV-013 final engineering assessment."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.static_analysis import STATIC_RELEASE_DIR, locate_project_root


def load_public_spec(project_root: Path | None = None) -> dict:
    root = locate_project_root() if project_root is None else Path(project_root)
    return json.loads(
        (root / "config" / "public" / "lab_spec_v1.json").read_text(
            encoding="utf-8"
        )
    )


def load_static_characterization(
    project_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    root = locate_project_root() if project_root is None else Path(project_root)
    raw_dir = root / STATIC_RELEASE_DIR
    static_df = pd.read_csv(raw_dir / "static_measurements.csv")
    matrix_df = pd.read_csv(raw_dir / "test_matrix.csv")

    matrix = matrix_df.loc[
        matrix_df["Test_Family"].astype(str).str.upper().eq("STATIC")
        & matrix_df["Analysis_Role"].astype(str).str.upper().eq("CHARACTERIZATION")
    ].copy()

    char_ids = set(matrix["Test_ID"].astype(str))
    char_df = static_df.loc[
        static_df["Test_ID"].astype(str).isin(char_ids)
    ].copy()

    return char_df, matrix


def load_frozen_c1_offset(project_root: Path | None = None) -> float:
    root = locate_project_root() if project_root is None else Path(project_root)
    record = json.loads(
        (root / "config" / "calibration_model_v1.json").read_text(encoding="utf-8")
    )
    if record["model_id"] != "C1_Constant_Offset":
        raise ValueError("Unexpected calibration model identity.")
    return float(record["parameters"]["offset_percent_rh"])


def summarize_characterization_tests(
    char_df: pd.DataFrame,
    matrix_df: pd.DataFrame,
    c1_offset: float,
) -> pd.DataFrame:
    """Return one characterization row per Test_ID."""
    meta_cols = [
        "Test_ID",
        "RH_Setpoint",
        "Temperature_Setpoint_C",
        "Direction",
        "Day_ID",
        "Run_ID",
    ]
    meta = matrix_df[meta_cols].drop_duplicates("Test_ID")

    rows: list[dict[str, object]] = []
    for test_id, group in char_df.groupby("Test_ID", sort=True):
        err_raw = (
            group["RH_DUT"].to_numpy(dtype=float)
            - group["RH_Reference"].to_numpy(dtype=float)
        )
        err_c1 = err_raw + c1_offset
        rows.append(
            {
                "Test_ID": str(test_id),
                "N": int(len(group)),
                "Raw_MBE": float(np.mean(err_raw)),
                "C1_MBE": float(np.mean(err_c1)),
                "Error_SD": float(np.std(err_raw, ddof=1)),
            }
        )

    summary = pd.DataFrame(rows).merge(
        meta, on="Test_ID", how="left", validate="one_to_one"
    )
    summary["Direction"] = summary["Direction"].astype(str).str.upper()
    return summary.sort_values(
        ["RH_Setpoint", "Temperature_Setpoint_C", "Direction", "Day_ID", "Run_ID"]
    ).reset_index(drop=True)


def matched_static_hysteresis(test_summary_df: pd.DataFrame) -> pd.DataFrame:
    """Pair UP/DOWN Test_ID means at matched RH, Temp, Day, Run."""
    keys = ["RH_Setpoint", "Temperature_Setpoint_C", "Day_ID", "Run_ID"]

    up = test_summary_df.loc[
        test_summary_df["Direction"].eq("UP"), keys + ["C1_MBE"]
    ].rename(columns={"C1_MBE": "C1_MBE_UP"})

    down = test_summary_df.loc[
        test_summary_df["Direction"].eq("DOWN"), keys + ["C1_MBE"]
    ].rename(columns={"C1_MBE": "C1_MBE_DOWN"})

    paired = up.merge(down, on=keys, how="inner", validate="one_to_one")
    paired["UP_Minus_DOWN"] = paired["C1_MBE_UP"] - paired["C1_MBE_DOWN"]
    paired["Hysteresis_Abs"] = paired["UP_Minus_DOWN"].abs()
    return paired.sort_values(keys).reset_index(drop=True)


def linearity_metric(test_summary_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    """Project-defined best-fit linearity on RH-level mean residuals."""
    rh = (
        test_summary_df.groupby("RH_Setpoint", as_index=False)
        .agg(Mean_C1_Residual=("C1_MBE", "mean"), N_Test_IDs=("Test_ID", "size"))
        .sort_values("RH_Setpoint")
        .reset_index(drop=True)
    )

    x = rh["RH_Setpoint"].to_numpy(dtype=float)
    y = rh["Mean_C1_Residual"].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, deg=1)
    fitted = intercept + slope * x
    deviation = y - fitted

    rh["Fitted_Residual"] = fitted
    rh["Linearity_Deviation"] = deviation
    rh["Linearity_Abs_Deviation"] = np.abs(deviation)

    metrics = {
        "Slope_Per_RH": float(slope),
        "Intercept": float(intercept),
        "Max_Abs_Deviation": float(np.max(np.abs(deviation))),
        "RMS_Deviation": float(np.sqrt(np.mean(deviation**2))),
    }
    return rh, metrics


def temperature_influence_metric(
    test_summary_df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Compute RH-conditioned temperature influence slopes by direction."""
    cell = (
        test_summary_df.groupby(
            ["RH_Setpoint", "Temperature_Setpoint_C", "Direction"],
            as_index=False,
        )
        .agg(
            Mean_C1_Residual=("C1_MBE", "mean"),
            N_Test_IDs=("Test_ID", "size"),
        )
        .sort_values(["RH_Setpoint", "Direction", "Temperature_Setpoint_C"])
    )

    rows: list[dict[str, object]] = []
    for (rh, direction), group in cell.groupby(
        ["RH_Setpoint", "Direction"], sort=True
    ):
        g = group.sort_values("Temperature_Setpoint_C")
        x = g["Temperature_Setpoint_C"].to_numpy(dtype=float)
        y = g["Mean_C1_Residual"].to_numpy(dtype=float)

        if len(g) != 3:
            raise ValueError(
                f"Expected 3 temperatures at RH={rh}, Direction={direction}; "
                f"found {len(g)}."
            )

        slope, intercept = np.polyfit(x, y, deg=1)
        fitted = intercept + slope * x
        ss_res = float(np.sum((y - fitted) ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

        rows.append(
            {
                "RH_Setpoint": float(rh),
                "Direction": str(direction),
                "Slope_RH_per_C": float(slope),
                "Abs_Slope_RH_per_C": float(abs(slope)),
                "Intercept": float(intercept),
                "R2": float(r2),
                "Error_15C": float(y[x.argmin()]),
                "Error_35C": float(y[x.argmax()]),
                "Delta_35_minus_15": float(y[x.argmax()] - y[x.argmin()]),
            }
        )

    slopes = pd.DataFrame(rows).sort_values(
        ["RH_Setpoint", "Direction"]
    ).reset_index(drop=True)

    max_idx = slopes["Abs_Slope_RH_per_C"].idxmax()
    max_row = slopes.loc[max_idx]

    metrics = {
        "Max_Abs_Slope_RH_per_C": float(max_row["Abs_Slope_RH_per_C"]),
        "Worst_RH_Setpoint": float(max_row["RH_Setpoint"]),
        "Worst_Direction": str(max_row["Direction"]),
    }
    return slopes, metrics


def load_final_evidence(project_root: Path | None = None) -> dict[str, pd.DataFrame]:
    """Load curated milestone evidence used in the final matrix."""
    root = locate_project_root() if project_root is None else Path(project_root)
    t = root / "reports" / "tables"

    paths = {
        "rr_summary": "hv005_rr_summary.csv",
        "repeatability_detail": "hv005_test_id_repeatability_summary.csv",
        "validation_models": "hv007_validation_model_comparison.csv",
        "validation_direction": "hv007_validation_residual_by_direction.csv",
        "step_metrics": "hv008_step_test_metrics.csv",
        "step_overall": "hv008_step_overall_summary.csv",
        "ramp_summary": "hv009_ramp_summary_by_condition.csv",
        "cyclic_summary": "hv009_cyclic_session_summary.csv",
        "sinusoidal": "hv009_sinusoidal_frequency_response.csv",
        "weekly_drift": "hv010_weekly_center_drift.csv",
        "weekly_trend": "hv010_weekly_trend_summary.csv",
        "monthly_span": "hv010_monthly_span_change.csv",
        "uncertainty": "hv011_uncertainty_summary.csv",
        "mc_summary": "hv012_mc_summary.csv",
    }

    return {key: pd.read_csv(t / filename) for key, filename in paths.items()}


def build_compliance_matrix(
    public_spec: dict,
    static_test_summary: pd.DataFrame,
    hysteresis_df: pd.DataFrame,
    linearity_metrics: dict[str, float],
    temp_metrics: dict[str, float],
    evidence: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Build frozen final public-requirement compliance matrix."""
    limits = public_spec["dut_public_spec"]["acceptance_limits"]

    uncertainty = evidence["uncertainty"]
    repeat_detail = evidence["repeatability_detail"]
    step_metrics = evidence["step_metrics"]
    weekly = evidence["weekly_drift"]

    static_accuracy_metric = float(
        uncertainty["Abs_Bias_Plus_Expanded_Uncertainty"].max()
    )
    repeat_max = float(repeat_detail["Std_Error_RH"].max())
    repeat_pooled = float(
        evidence["rr_summary"].loc[
            evidence["rr_summary"]["Component"].eq("Within-Test Repeatability"),
            "Value_RH",
        ].iloc[0]
    )
    hysteresis_max = float(hysteresis_df["Hysteresis_Abs"].max())

    dut_t90_max = float(step_metrics["DUT_t90_s"].max())
    dut_t90_mean = float(step_metrics["DUT_t90_s"].mean())
    ref_t90_mean = float(step_metrics["Reference_t90_s"].mean())
    lag_t90_mean = float(step_metrics["Lag_t90_s"].mean())

    max_drift_excursion = float(
        weekly["Center_Drift_From_Day0"].abs().max()
    )
    drift_slope = float(
        evidence["weekly_trend"].loc[
            evidence["weekly_trend"]["Metric"].eq("Center_Drift_From_Day0"),
            "Slope_per_Day",
        ].iloc[0]
    )
    drift_annualized_diagnostic = abs(drift_slope) * 365.0

    rows = [
        {
            "Requirement": "Static accuracy",
            "Public_Limit": f"±{limits['static_accuracy_abs_rh_percent']:.2f} %RH",
            "Metric": "max(|residual bias| + U_k2) at declared uncertainty points",
            "Observed": static_accuracy_metric,
            "Units": "%RH",
            "Status": (
                "PASS"
                if static_accuracy_metric
                <= limits["static_accuracy_abs_rh_percent"]
                else "FAIL"
            ),
            "Evidence": "HV-011",
            "Notes": "Applies to four declared uncertainty-evaluation points.",
        },
        {
            "Requirement": "Repeatability sigma",
            "Public_Limit": f"≤ {limits['repeatability_sigma_max_rh_percent']:.2f} %RH",
            "Metric": "maximum Test_ID within-hold error SD",
            "Observed": repeat_max,
            "Units": "%RH",
            "Status": (
                "PASS"
                if repeat_max <= limits["repeatability_sigma_max_rh_percent"]
                else "FAIL"
            ),
            "Evidence": "HV-005",
            "Notes": f"Pooled SD = {repeat_pooled:.4f} %RH; strict max used for compliance.",
        },
        {
            "Requirement": "Static hysteresis",
            "Public_Limit": f"≤ {limits['hysteresis_max_rh_percent']:.2f} %RH",
            "Metric": "maximum matched |UP mean error - DOWN mean error|",
            "Observed": hysteresis_max,
            "Units": "%RH",
            "Status": (
                "PASS"
                if hysteresis_max <= limits["hysteresis_max_rh_percent"]
                else "FAIL"
            ),
            "Evidence": "HV-004/HV-007",
            "Notes": "C1 offset cancels in matched direction difference.",
        },
        {
            "Requirement": "Linearity",
            "Public_Limit": f"≤ {limits['linearity_max_rh_percent']:.2f} %RH",
            "Metric": "max RH-level mean residual deviation from best-fit line",
            "Observed": float(linearity_metrics["Max_Abs_Deviation"]),
            "Units": "%RH",
            "Status": (
                "PASS"
                if linearity_metrics["Max_Abs_Deviation"]
                <= limits["linearity_max_rh_percent"]
                else "FAIL"
            ),
            "Evidence": "HV-004/HV-013",
            "Notes": "METHOD-DEFINED: public spec does not define endpoint vs best-fit linearity.",
        },
        {
            "Requirement": "Temperature influence",
            "Public_Limit": (
                f"≤ {limits['temperature_influence_max_rh_percent_per_c']:.3f} "
                "%RH/°C"
            ),
            "Metric": "max |residual-vs-temperature slope| over RH × Direction",
            "Observed": float(temp_metrics["Max_Abs_Slope_RH_per_C"]),
            "Units": "%RH/°C",
            "Status": (
                "PASS"
                if temp_metrics["Max_Abs_Slope_RH_per_C"]
                <= limits["temperature_influence_max_rh_percent_per_c"]
                else "FAIL"
            ),
            "Evidence": "HV-004/HV-013",
            "Notes": (
                f"Worst cell: RH={temp_metrics['Worst_RH_Setpoint']:.0f} %RH, "
                f"{temp_metrics['Worst_Direction']}."
            ),
        },
        {
            "Requirement": "t90",
            "Public_Limit": f"≤ {limits['t90_max_s']:.1f} s",
            "Metric": "command-to-DUT t90 with reference adequacy check",
            "Observed": dut_t90_mean,
            "Units": "s",
            "Status": "NOT_DEMONSTRATED",
            "Evidence": "HV-008",
            "Notes": (
                f"DUT mean t90={dut_t90_mean:.1f}s, max={dut_t90_max:.1f}s; "
                f"reference mean t90={ref_t90_mean:.1f}s; mean DUT-reference lag="
                f"{lag_t90_mean:.1f}s. Reference/chamber stimulus itself is slower "
                "than the 60s DUT limit."
            ),
        },
        {
            "Requirement": "Settling band",
            "Public_Limit": f"±{limits['settling_band_abs_rh_percent']:.1f} %RH",
            "Metric": "public absolute band only; no maximum settling time specified",
            "Observed": np.nan,
            "Units": "%RH",
            "Status": "INFORMATIONAL",
            "Evidence": "Public spec/HV-008",
            "Notes": "No binary time-to-settle acceptance criterion is publicly defined.",
        },
        {
            "Requirement": "Drift",
            "Public_Limit": f"≤ {limits['drift_max_rh_percent_per_year']:.2f} %RH/year",
            "Metric": "90-day stability evidence; annualized slope diagnostic only",
            "Observed": drift_annualized_diagnostic,
            "Units": "%RH/year diagnostic",
            "Status": "NOT_DEMONSTRATED",
            "Evidence": "HV-010",
            "Notes": (
                f"90-day campaign; non-monotonic maximum center excursion="
                f"{max_drift_excursion:.4f} %RH. Annualized slope is not used "
                "as a compliance extrapolation."
            ),
        },
    ]

    return pd.DataFrame(rows)


def build_application_risk_matrix(
    evidence: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Summarize application-level risks beyond direct binary spec limits."""
    validation_dir = evidence["validation_direction"]
    ramp = evidence["ramp_summary"]
    cyclic = evidence["cyclic_summary"]
    sinus = evidence["sinusoidal"]

    down = float(
        validation_dir.loc[
            validation_dir["Direction"].astype(str).str.upper().eq("DOWN"),
            "C1_MBE",
        ].iloc[0]
    )
    up = float(
        validation_dir.loc[
            validation_dir["Direction"].astype(str).str.upper().eq("UP"),
            "C1_MBE",
        ].iloc[0]
    )
    static_dir_split = abs(down - up)

    ramp_dir = (
        ramp.groupby("Direction", as_index=False)
        .agg(C1_MBE=("C1_MBE_Mean", "mean"), C1_RMSE=("C1_RMSE_Mean", "mean"))
    )
    ramp_down = float(
        ramp_dir.loc[ramp_dir["Direction"].eq("DOWN"), "C1_MBE"].iloc[0]
    )
    ramp_up = float(
        ramp_dir.loc[ramp_dir["Direction"].eq("UP"), "C1_MBE"].iloc[0]
    )

    cyclic_gap = float(cyclic["Direction_Gap_Mean"].abs().mean())
    min_gain = float(sinus["Gain"].min())
    max_phase = float(sinus["Phase_Lag_Deg"].abs().max())

    rows = [
        {
            "Risk": "Static direction/state dependence",
            "Observed": static_dir_split,
            "Units": "%RH",
            "Severity": "MODERATE",
            "Evidence": "HV-007",
            "Interpretation": "Frozen C1 leaves a reproducible UP/DOWN residual split.",
        },
        {
            "Risk": "Ramp direction bias",
            "Observed": abs(ramp_down - ramp_up),
            "Units": "%RH separation",
            "Severity": "HIGH",
            "Evidence": "HV-009",
            "Interpretation": (
                f"C1 ramp MBE DOWN={ramp_down:+.3f}, UP={ramp_up:+.3f} %RH."
            ),
        },
        {
            "Risk": "Cyclic dynamic hysteresis",
            "Observed": cyclic_gap,
            "Units": "%RH",
            "Severity": "HIGH",
            "Evidence": "HV-009",
            "Interpretation": "Large highly repeatable dynamic direction/state gap.",
        },
        {
            "Risk": "High-frequency attenuation",
            "Observed": min_gain,
            "Units": "gain",
            "Severity": "HIGH",
            "Evidence": "HV-009",
            "Interpretation": "Minimum measured-reference-relative gain at fastest sinusoid.",
        },
        {
            "Risk": "Phase lag",
            "Observed": max_phase,
            "Units": "deg",
            "Severity": "MODERATE",
            "Evidence": "HV-009",
            "Interpretation": "Substantial phase lag at faster RH variation.",
        },
    ]
    return pd.DataFrame(rows)
