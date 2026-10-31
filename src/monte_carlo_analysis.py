"""Reusable helpers for HV-012 Monte Carlo uncertainty validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src.static_analysis import locate_project_root


@dataclass(frozen=True)
class MonteCarloConfig:
    seed: int = 7140
    trials: int = 250_000


def load_hv011_inputs(
    project_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load frozen HV-011 summary, budget, and point evidence."""
    root = locate_project_root() if project_root is None else Path(project_root)
    tables = root / "reports" / "tables"

    summary = pd.read_csv(tables / "hv011_uncertainty_summary.csv")
    budget = pd.read_csv(tables / "hv011_uncertainty_budget.csv")
    evidence = pd.read_csv(tables / "hv011_uncertainty_point_evidence.csv")

    return summary, budget, evidence


def _skewness(x: np.ndarray) -> float:
    """Population-moment skewness."""
    x = np.asarray(x, dtype=float)
    centered = x - np.mean(x)
    m2 = np.mean(centered**2)
    if m2 <= 0:
        return 0.0
    m3 = np.mean(centered**3)
    return float(m3 / (m2 ** 1.5))


def _excess_kurtosis(x: np.ndarray) -> float:
    """Population-moment excess kurtosis."""
    x = np.asarray(x, dtype=float)
    centered = x - np.mean(x)
    m2 = np.mean(centered**2)
    if m2 <= 0:
        return -3.0
    m4 = np.mean(centered**4)
    return float(m4 / (m2**2) - 3.0)


def build_empirical_state_support(
    summary_df: pd.DataFrame,
    evidence_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build variance-matched empirical state support per point.

    The four observed Test_ID residual means are centered, then rescaled so
    their equal-probability population standard deviation equals the frozen
    HV-011 U_State value.
    """
    rows: list[dict[str, object]] = []

    for _, summary_row in summary_df.iterrows():
        point_id = str(summary_row["Point_ID"])
        target_sd = float(summary_row["U_State"])

        point = evidence_df.loc[evidence_df["Point_ID"].eq(point_id)].copy()
        if len(point) != 4:
            raise ValueError(f"{point_id}: expected exactly four Test_ID states.")

        raw = point["C1_MBE"].to_numpy(dtype=float)
        centered = raw - np.mean(raw)
        empirical_pop_sd = float(np.std(centered, ddof=0))

        if empirical_pop_sd <= 0:
            if target_sd > 0:
                raise ValueError(
                    f"{point_id}: zero empirical state spread with nonzero target."
                )
            scale = 1.0
        else:
            scale = target_sd / empirical_pop_sd

        support = centered * scale

        if not np.isclose(np.mean(support), 0.0, atol=1e-12):
            raise ValueError(f"{point_id}: empirical support is not centered.")
        if not np.isclose(np.std(support, ddof=0), target_sd, rtol=1e-12):
            raise ValueError(f"{point_id}: empirical support variance mismatch.")

        for (_, evidence_row), raw_centered, state_value in zip(
            point.iterrows(), centered, support
        ):
            rows.append(
                {
                    "Point_ID": point_id,
                    "Test_ID": str(evidence_row["Test_ID"]),
                    "Direction": str(evidence_row["Direction"]),
                    "Run_ID": int(evidence_row["Run_ID"]),
                    "Original_C1_MBE": float(evidence_row["C1_MBE"]),
                    "Original_Centered_State": float(raw_centered),
                    "State_Scale_Factor": float(scale),
                    "MC_State_Support": float(state_value),
                    "Target_U_State": target_sd,
                }
            )

    return pd.DataFrame(rows)


def _simulate_point(
    summary_row: pd.Series,
    state_support: np.ndarray | None,
    rng: np.random.Generator,
    trials: int,
    model: str,
) -> tuple[np.ndarray, dict[str, float]]:
    """Simulate one point under one frozen MC model."""
    u_repeat = float(summary_row["U_Repeat_Mean"])
    u_state = float(summary_row["U_State"])
    u_c1 = float(summary_row["U_C1_Offset"])
    u_ref = float(summary_row["U_Reference_Calibration"])
    stability_bound = float(summary_row["Stability_Excursion_Bound"])
    analytical_uc = float(summary_row["Combined_Standard_Uncertainty"])

    repeat = rng.normal(0.0, u_repeat, size=trials)
    c1_offset = rng.normal(0.0, u_c1, size=trials)
    reference = rng.normal(0.0, u_ref, size=trials)
    stability = rng.uniform(-stability_bound, stability_bound, size=trials)

    if model == "A_ANALYTICAL_EQUIVALENT":
        state = rng.normal(0.0, u_state, size=trials)
    elif model == "B_EMPIRICAL_STATE":
        if state_support is None or len(state_support) != 4:
            raise ValueError("Model B requires four empirical state support values.")
        state = rng.choice(state_support, size=trials, replace=True)
    else:
        raise ValueError(f"Unknown Monte Carlo model: {model}")

    uncertainty_error = repeat + state + c1_offset + reference + stability

    q025, median, q975 = np.quantile(
        uncertainty_error, [0.025, 0.50, 0.975]
    )
    mc_mean = float(np.mean(uncertainty_error))
    mc_sd = float(np.std(uncertainty_error, ddof=1))

    metrics = {
        "MC_Mean": mc_mean,
        "MC_SD": mc_sd,
        "Relative_SD_Error_vs_Analytical": float(
            (mc_sd - analytical_uc) / analytical_uc
        ),
        "Q025": float(q025),
        "Median": float(median),
        "Q975": float(q975),
        "Central95_Width": float(q975 - q025),
        "Lower95_HalfWidth": float(median - q025),
        "Upper95_HalfWidth": float(q975 - median),
        "Central95_Symmetric_HalfWidth": float((q975 - q025) / 2.0),
        "Analytical_2uc": float(2.0 * analytical_uc),
        "Coverage_Inside_PlusMinus_2uc": float(
            np.mean(np.abs(uncertainty_error) <= 2.0 * analytical_uc)
        ),
        "Skewness": _skewness(uncertainty_error),
        "Excess_Kurtosis": _excess_kurtosis(uncertainty_error),
    }

    return uncertainty_error, metrics


def run_monte_carlo(
    summary_df: pd.DataFrame,
    state_support_df: pd.DataFrame,
    config: MonteCarloConfig = MonteCarloConfig(),
) -> tuple[pd.DataFrame, dict[tuple[str, str], np.ndarray]]:
    """Run both frozen MC models at all HV-011 evaluation points."""
    master_rng = np.random.default_rng(config.seed)

    rows: list[dict[str, object]] = []
    samples: dict[tuple[str, str], np.ndarray] = {}

    for _, summary_row in summary_df.sort_values("Point_ID").iterrows():
        point_id = str(summary_row["Point_ID"])

        support = (
            state_support_df.loc[
                state_support_df["Point_ID"].eq(point_id),
                "MC_State_Support",
            ]
            .to_numpy(dtype=float)
        )

        for model in ["A_ANALYTICAL_EQUIVALENT", "B_EMPIRICAL_STATE"]:
            # A fresh deterministic child seed avoids model-order dependence.
            child_seed = int(master_rng.integers(0, np.iinfo(np.uint32).max))
            rng = np.random.default_rng(child_seed)

            mc_values, metrics = _simulate_point(
                summary_row=summary_row,
                state_support=support if model == "B_EMPIRICAL_STATE" else None,
                rng=rng,
                trials=config.trials,
                model=model,
            )

            samples[(point_id, model)] = mc_values

            rows.append(
                {
                    "Point_ID": point_id,
                    "RH_Percent": float(summary_row["RH_Percent"]),
                    "Temperature_C": float(summary_row["Temperature_C"]),
                    "Model": model,
                    "Trials": int(config.trials),
                    "Child_Seed": child_seed,
                    "Analytical_uc": float(
                        summary_row["Combined_Standard_Uncertainty"]
                    ),
                    "Point_Residual_Bias": float(
                        summary_row["Point_Residual_Bias"]
                    ),
                    **metrics,
                }
            )

    return pd.DataFrame(rows), samples


def build_model_comparison(mc_summary_df: pd.DataFrame) -> pd.DataFrame:
    """Compare Model B distribution metrics against Model A point by point."""
    a = mc_summary_df.loc[
        mc_summary_df["Model"].eq("A_ANALYTICAL_EQUIVALENT")
    ].set_index("Point_ID")
    b = mc_summary_df.loc[
        mc_summary_df["Model"].eq("B_EMPIRICAL_STATE")
    ].set_index("Point_ID")

    rows: list[dict[str, object]] = []

    for point_id in sorted(set(a.index) & set(b.index)):
        ra = a.loc[point_id]
        rb = b.loc[point_id]

        rows.append(
            {
                "Point_ID": point_id,
                "Analytical_uc": float(ra["Analytical_uc"]),
                "ModelA_MC_SD": float(ra["MC_SD"]),
                "ModelB_MC_SD": float(rb["MC_SD"]),
                "ModelA_Central95_HalfWidth": float(
                    ra["Central95_Symmetric_HalfWidth"]
                ),
                "ModelB_Central95_HalfWidth": float(
                    rb["Central95_Symmetric_HalfWidth"]
                ),
                "ModelA_Coverage_Inside_2uc": float(
                    ra["Coverage_Inside_PlusMinus_2uc"]
                ),
                "ModelB_Coverage_Inside_2uc": float(
                    rb["Coverage_Inside_PlusMinus_2uc"]
                ),
                "ModelA_Skewness": float(ra["Skewness"]),
                "ModelB_Skewness": float(rb["Skewness"]),
                "ModelA_Excess_Kurtosis": float(ra["Excess_Kurtosis"]),
                "ModelB_Excess_Kurtosis": float(rb["Excess_Kurtosis"]),
                "ModelB_vs_A_95HalfWidth_Ratio": float(
                    rb["Central95_Symmetric_HalfWidth"]
                    / ra["Central95_Symmetric_HalfWidth"]
                ),
            }
        )

    return pd.DataFrame(rows)


def validate_mc_gate(mc_summary_df: pd.DataFrame) -> pd.DataFrame:
    """Return explicit numerical gate checks for Model A and Model B."""
    rows: list[dict[str, object]] = []

    for _, row in mc_summary_df.iterrows():
        model = str(row["Model"])
        sd_limit = 0.01 if model == "A_ANALYTICAL_EQUIVALENT" else 0.015

        mean_pass = abs(float(row["MC_Mean"])) <= 0.01
        sd_pass = abs(float(row["Relative_SD_Error_vs_Analytical"])) <= sd_limit

        rows.append(
            {
                "Point_ID": row["Point_ID"],
                "Model": model,
                "Mean_Abs_Limit": 0.01,
                "Mean_Abs_Observed": abs(float(row["MC_Mean"])),
                "Mean_Check_PASS": bool(mean_pass),
                "Relative_SD_Error_Limit": sd_limit,
                "Relative_SD_Error_Abs": abs(
                    float(row["Relative_SD_Error_vs_Analytical"])
                ),
                "SD_Check_PASS": bool(sd_pass),
                "Gate_Check_PASS": bool(mean_pass and sd_pass),
            }
        )

    return pd.DataFrame(rows)
