"""Reusable helpers for HV-011 measurement-uncertainty analysis."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.static_analysis import STATIC_RELEASE_DIR, locate_project_root


def load_public_lab_spec(project_root: Path | None = None) -> dict:
    """Load analyst-visible public lab specification."""
    root = locate_project_root() if project_root is None else Path(project_root)
    return json.loads(
        (root / "config" / "public" / "lab_spec_v1.json").read_text(
            encoding="utf-8"
        )
    )


def load_frozen_c1_offset(project_root: Path | None = None) -> float:
    """Load the frozen HV-006 C1 constant offset."""
    root = locate_project_root() if project_root is None else Path(project_root)
    record = json.loads(
        (root / "config" / "calibration_model_v1.json").read_text(encoding="utf-8")
    )
    if record["model_id"] != "C1_Constant_Offset":
        raise ValueError("Unexpected calibration model identity.")
    if record["validation_measurements_used"] is not False:
        raise ValueError("Frozen model record failed validation-use integrity check.")
    return float(record["parameters"]["offset_percent_rh"])


def load_static_and_matrix(
    project_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load static measurements and public test matrix."""
    root = locate_project_root() if project_root is None else Path(project_root)
    raw_dir = root / STATIC_RELEASE_DIR
    return (
        pd.read_csv(raw_dir / "static_measurements.csv"),
        pd.read_csv(raw_dir / "test_matrix.csv"),
    )


def load_repeatability_sd(project_root: Path | None = None) -> float:
    """Load pooled within-Test_ID repeatability SD from HV-005 evidence."""
    root = locate_project_root() if project_root is None else Path(project_root)
    table = pd.read_csv(root / "reports" / "tables" / "hv005_rr_summary.csv")
    row = table.loc[
        table["Component"].eq("Within-Test Repeatability")
        & table["Statistic"].eq("Pooled SD")
    ]
    if len(row) != 1:
        raise ValueError("Could not identify unique HV-005 pooled repeatability SD.")
    return float(row["Value_RH"].iloc[0])


def load_stability_excursion(project_root: Path | None = None) -> float:
    """Load maximum observed absolute weekly center drift from HV-010."""
    root = locate_project_root() if project_root is None else Path(project_root)
    table = pd.read_csv(
        root / "reports" / "tables" / "hv010_weekly_center_drift.csv"
    )
    return float(table["Center_Drift_From_Day0"].abs().max())


def _point_role(rh: float, temp: float) -> str:
    """Frozen evidence-role rule for uncertainty evaluation."""
    if temp == 25.0 and rh in {30.0, 50.0, 70.0}:
        return "VALIDATION"
    if rh == 80.0 and temp == 35.0:
        return "CHARACTERIZATION"
    raise ValueError(f"No frozen evidence-role rule for point ({rh}, {temp}).")


def point_evidence_table(
    static_df: pd.DataFrame,
    test_matrix_df: pd.DataFrame,
    public_spec: dict,
    c1_offset: float,
    repeatability_sd: float,
    samples_per_result: int = 60,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build Test_ID and point-level evidence for declared uncertainty points."""
    points = public_spec["experimental_design"]["uncertainty_evaluation_points"]

    matrix_cols = [
        "Test_ID",
        "Analysis_Role",
        "RH_Setpoint",
        "Temperature_Setpoint_C",
        "Direction",
        "Day_ID",
        "Run_ID",
    ]
    matrix = test_matrix_df.loc[
        test_matrix_df["Test_Family"].astype(str).str.upper().eq("STATIC"),
        matrix_cols,
    ].copy()

    merged = static_df.merge(
        matrix,
        on="Test_ID",
        how="left",
        suffixes=("_Data", "_Matrix"),
        validate="many_to_one",
    )

    u_repeat_mean = float(repeatability_sd / np.sqrt(samples_per_result))

    test_rows: list[dict[str, object]] = []
    point_rows: list[dict[str, object]] = []

    for idx, point in enumerate(points, start=1):
        rh = float(point["rh_percent"])
        temp = float(point["temperature_c"])
        role = _point_role(rh, temp)

        mask = (
            merged["Analysis_Role_Matrix"].astype(str).str.upper().eq(role)
            & np.isclose(merged["RH_Setpoint_Matrix"], rh)
            & np.isclose(merged["Temperature_Setpoint_C_Matrix"], temp)
        )
        subset = merged.loc[mask].copy()

        expected_ids = (
            matrix.loc[
                matrix["Analysis_Role"].astype(str).str.upper().eq(role)
                & np.isclose(matrix["RH_Setpoint"], rh)
                & np.isclose(matrix["Temperature_Setpoint_C"], temp),
                "Test_ID",
            ]
            .drop_duplicates()
            .sort_values()
            .tolist()
        )

        if len(expected_ids) != 4:
            raise ValueError(
                f"Expected 4 independent Test_IDs at {rh}%RH/{temp}C "
                f"for role {role}; found {len(expected_ids)}."
            )

        if subset["Test_ID"].nunique() != 4:
            raise ValueError(
                f"Measurement evidence mismatch at {rh}%RH/{temp}C."
            )

        point_id = f"UNC-{idx:03d}"
        mbes: list[float] = []

        for test_id, group in subset.groupby("Test_ID", sort=True):
            error = (
                group["RH_DUT"].to_numpy(dtype=float)
                + c1_offset
                - group["RH_Reference"].to_numpy(dtype=float)
            )
            mbe = float(np.mean(error))
            mbes.append(mbe)

            row0 = group.iloc[0]
            test_rows.append(
                {
                    "Point_ID": point_id,
                    "RH_Percent": rh,
                    "Temperature_C": temp,
                    "Evidence_Role": role,
                    "Test_ID": str(test_id),
                    "Direction": str(row0["Direction_Matrix"]).upper(),
                    "Day_ID": int(row0["Day_ID_Matrix"]),
                    "Run_ID": int(row0["Run_ID_Matrix"]),
                    "N_Samples": int(len(group)),
                    "C1_MBE": mbe,
                    "Within_Test_Error_SD": float(np.std(error, ddof=1)),
                }
            )

        mbes_arr = np.asarray(mbes, dtype=float)
        s_point = float(np.std(mbes_arr, ddof=1))
        u_state = float(
            np.sqrt(max(s_point**2 - u_repeat_mean**2, 0.0))
        )

        point_rows.append(
            {
                "Point_ID": point_id,
                "RH_Percent": rh,
                "Temperature_C": temp,
                "Evidence_Role": role,
                "N_Test_IDs": int(len(mbes_arr)),
                "Point_Residual_Bias": float(np.mean(mbes_arr)),
                "Point_MBE_SD": s_point,
                "U_Repeat_Mean": u_repeat_mean,
                "U_State": u_state,
                "Max_Abs_TestID_MBE": float(np.max(np.abs(mbes_arr))),
            }
        )

    return pd.DataFrame(test_rows), pd.DataFrame(point_rows)


def build_uncertainty_budget(
    point_summary_df: pd.DataFrame,
    public_spec: dict,
    stability_excursion: float,
    coverage_factor: float = 2.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build primary standard-uncertainty budget and point summary."""
    ref = public_spec["reference_public_spec"]

    u_ref_cal = float(
        ref["expanded_calibration_uncertainty_rh_percent"]
        / ref["coverage_factor_k"]
    )
    u_stability = float(stability_excursion / np.sqrt(3.0))

    component_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for _, row in point_summary_df.iterrows():
        components = {
            "Repeatability_of_60s_Mean": float(row["U_Repeat_Mean"]),
            "Point_State_Residual": float(row["U_State"]),
            "Reference_Calibration": u_ref_cal,
            "Stability_Bounded_Excursion": u_stability,
        }

        uc = float(np.sqrt(sum(v**2 for v in components.values())))
        expanded = float(coverage_factor * uc)

        for name, value in components.items():
            component_rows.append(
                {
                    "Point_ID": row["Point_ID"],
                    "RH_Percent": row["RH_Percent"],
                    "Temperature_C": row["Temperature_C"],
                    "Component": name,
                    "Standard_Uncertainty": value,
                    "Sensitivity_Coefficient": 1.0,
                    "Variance_Contribution": value**2,
                }
            )

        bias = float(row["Point_Residual_Bias"])
        summary_rows.append(
            {
                **row.to_dict(),
                "U_Reference_Calibration": u_ref_cal,
                "Stability_Excursion_Bound": float(stability_excursion),
                "U_Stability": u_stability,
                "Combined_Standard_Uncertainty": uc,
                "Coverage_Factor": float(coverage_factor),
                "Expanded_Uncertainty": expanded,
                "Abs_Bias_Plus_Expanded_Uncertainty": abs(bias) + expanded,
            }
        )

    return pd.DataFrame(component_rows), pd.DataFrame(summary_rows)


def build_sensitivity_table(
    summary_df: pd.DataFrame,
    public_spec: dict,
) -> pd.DataFrame:
    """Build non-primary reference-drift and chamber-uniformity sensitivity cases."""
    ref = public_spec["reference_public_spec"]
    chamber = public_spec["chamber_public_spec"]

    ref_drift_90_bound = float(
        ref["drift_max_rh_percent_per_year"] * 90.0 / 365.0
    )
    u_ref_drift_90 = float(ref_drift_90_bound / np.sqrt(3.0))

    chamber_bound = float(chamber["rh_uniformity_abs_percent"])
    u_chamber = float(chamber_bound / np.sqrt(3.0))

    rows: list[dict[str, object]] = []

    for _, row in summary_df.iterrows():
        uc = float(row["Combined_Standard_Uncertainty"])

        cases = {
            "Primary": uc,
            "Primary_plus_reference_drift_sensitivity": float(
                np.sqrt(uc**2 + u_ref_drift_90**2)
            ),
            "Primary_plus_chamber_uniformity_sensitivity": float(
                np.sqrt(uc**2 + u_chamber**2)
            ),
            "Primary_plus_both_sensitivities": float(
                np.sqrt(uc**2 + u_ref_drift_90**2 + u_chamber**2)
            ),
        }

        for case, uc_case in cases.items():
            rows.append(
                {
                    "Point_ID": row["Point_ID"],
                    "RH_Percent": row["RH_Percent"],
                    "Temperature_C": row["Temperature_C"],
                    "Case": case,
                    "Combined_Standard_Uncertainty": uc_case,
                    "Expanded_Uncertainty_k2": 2.0 * uc_case,
                    "Reference_Drift_90d_Bound": ref_drift_90_bound,
                    "U_Reference_Drift_90d": u_ref_drift_90,
                    "Chamber_Uniformity_Bound": chamber_bound,
                    "U_Chamber_Uniformity_Sensitivity": u_chamber,
                }
            )

    return pd.DataFrame(rows)
