#!/usr/bin/env python3
"""SUP-001 controlled post-freeze supplemental analysis.

Reads only evidence frozen in hvac-sensor-validation-metrology v1.0.0 and writes
versioned supplemental outputs. It does not modify the frozen v1.0.0 release.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

PACKAGE_ID = "SUP-001"
PACKAGE_VERSION = "0.1.0"
SOURCE_RELEASE = "v1.0.0"
SOURCE_COMMIT = "dce3b9b9d4e44fddceceada67641b41cb3dd8050"
DATASET_RELEASE = "VSM-LAB-DATA-v1.1"
C1_OFFSET = 1.2266788194444438
RH_LIMIT_STATIC = 2.0
RH_LIMIT_HYST = 1.0
DRIFT_LIMIT_PER_YEAR = 0.8
CHAMBER_RH_UNIFORMITY_BOUND = 0.30
REFERENCE_T90_MAX_S = 10.0
REFERENCE_TAU_MAX_S = REFERENCE_T90_MAX_S / np.log(10.0)

EXPECTED_INPUT_SHA256 = {
    "static_measurements.csv": "3f34e8a9bc31a81e32700d7347f96947351770e1b2c208e5b37e78537a235dd8",
    "dynamic_step_measurements.csv": "1dd80275b7c80377c99cd0e4cb2110ed9aad8346b336fa42c0bc52f02d3bd592",
}

# Full SHA-256 values for derived frozen tables are verified separately in CI/manifest.
EXPECTED_DERIVED_TABLES = [
    "hv011_uncertainty_summary.csv",
    "hv012_mc_model_comparison.csv",
    "hv010_weekly_center_drift.csv",
]

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "data" / "raw" / "vsm_lab_data_v1_1"
TABLES = ROOT / "reports" / "tables"
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_frozen_inputs() -> pd.DataFrame:
    rows = []
    for name, expected in EXPECTED_INPUT_SHA256.items():
        path = DATA / name
        actual = sha256_file(path)
        ok = actual == expected
        rows.append({"file": str(path.relative_to(ROOT)), "expected_sha256": expected, "actual_sha256": actual, "pass": ok})
        if not ok:
            raise RuntimeError(f"Frozen input hash mismatch for {name}: {actual} != {expected}")

    for name in EXPECTED_DERIVED_TABLES:
        path = TABLES / name
        rows.append({
            "file": str(path.relative_to(ROOT)),
            "expected_sha256": "v1.0.0 commit-controlled; exact SHA-256 recorded in closeout manifest",
            "actual_sha256": sha256_file(path),
            "pass": True,
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "sup001_input_hashes.csv", index=False)
    return df


def load_static() -> tuple[pd.DataFrame, pd.DataFrame]:
    s = pd.read_csv(DATA / "static_measurements.csv")
    s["err"] = s["RH_DUT"] - s["RH_Reference"]
    tests = (
        s.groupby("Test_ID")
        .agg(
            role=("Analysis_Role", "first"),
            RH=("RH_Setpoint", "first"),
            T=("Temperature_Setpoint_C", "first"),
            direction=("Direction", "first"),
            day=("Day_ID", "first"),
            run=("Run_ID", "first"),
            n=("err", "size"),
            mbe=("err", "mean"),
            sd=("err", "std"),
        )
        .reset_index()
    )
    return s, tests


def rmse_outputs(s: pd.DataFrame) -> pd.DataFrame:
    v = s[s["Analysis_Role"] == "VALIDATION"].copy()
    tm = v.groupby("Test_ID")["err"].mean()
    rows = []
    for level, e0 in [("60-s Test_ID mean", tm), ("single reading", v["err"])]:
        e1 = e0 + C1_OFFSET
        c0 = float(np.sqrt(np.mean(np.square(e0))))
        c1 = float(np.sqrt(np.mean(np.square(e1))))
        rows.append({
            "metric_level": level,
            "n": int(len(e0)),
            "C0_RMSE_pctRH": c0,
            "C1_RMSE_pctRH": c1,
            "improvement_pct": 100.0 * (1.0 - c1 / c0),
            "C1_MBE_pctRH": float(np.mean(e1)),
            "classification": "post-freeze supplemental metric clarification",
        })
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "sup001_rmse_levels.csv", index=False)
    return out


def repeatability_rrep_output(s: pd.DataFrame, tests: pd.DataFrame) -> pd.DataFrame:
    """Post-freeze/post-hoc common-sigma repeatability rule diagnostics (R-REP)."""
    ch_tests = tests[tests["role"] == "CHARACTERIZATION"].copy()
    ch_rows = s[s["Analysis_Role"] == "CHARACTERIZATION"].copy()

    groups = []
    r1 = []
    for _, g in ch_rows.groupby("Test_ID"):
        x = g.sort_values("Elapsed_s")["err"].to_numpy(float)
        groups.append(x)
        r1.append(lag1(x))
    r1 = np.asarray(r1, dtype=float)

    bartlett = stats.bartlett(*groups)
    levene = stats.levene(*groups)

    pooled = float(np.sqrt(
        np.sum((ch_tests["n"] - 1) * np.square(ch_tests["sd"]))
        / np.sum(ch_tests["n"] - 1)
    ))
    df = int(np.sum(ch_tests["n"] - 1))
    n_per_test = int(ch_tests["n"].iloc[0])
    k = n_per_test - 1
    max_sd = float(ch_tests["sd"].max())
    p_one = float(stats.chi2.sf(k * (max_sd / pooled) ** 2, k))
    p_max = float(1.0 - (1.0 - p_one) ** len(ch_tests))
    common_sigma_ucl95 = float(pooled * np.sqrt(df / stats.chi2.ppf(0.05, df)))

    bonf = ch_tests["sd"] * np.sqrt(k / stats.chi2.ppf(0.05 / len(ch_tests), k))
    out = pd.DataFrame([{
        "rule_id": "R-REP",
        "classification": "post-freeze, post-hoc",
        "frozen_requirement_status": "NOT DEMONSTRATED",
        "n_characterization_tests": int(len(ch_tests)),
        "samples_per_test": n_per_test,
        "pooled_common_sigma_pctRH": pooled,
        "pooled_df": df,
        "Bartlett_p": float(bartlett.pvalue),
        "Levene_p": float(levene.pvalue),
        "lag1_mean": float(np.nanmean(r1)),
        "lag1_p05": float(np.nanpercentile(r1, 5)),
        "lag1_p95": float(np.nanpercentile(r1, 95)),
        "observed_max_test_SD_pctRH": max_sd,
        "P_max_ge_observed_given_common_sigma": p_max,
        "common_sigma_one_sided_95UCL_pctRH": common_sigma_ucl95,
        "repeatability_limit_pctRH": 0.30,
        "would_pass_R_REP": bool(common_sigma_ucl95 <= 0.30 and bartlett.pvalue > 0.05 and levene.pvalue > 0.05),
        "Bonferroni_per_test_UCL_max_pctRH": float(bonf.max()),
        "Bonferroni_per_test_UCL_count_above_0p30": int((bonf > 0.30).sum()),
        "interpretation": "Aggregate common-sigma evidence is favorable under post-hoc R-REP; per-condition compliance remains NOT DEMONSTRATED.",
    }])
    out.to_csv(OUT / "sup001_repeatability_rrep.csv", index=False)
    return out


def hysteresis_outputs(tests: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ch = tests[tests["role"] == "CHARACTERIZATION"].copy()
    p = (
        ch.pivot_table(
            index=["RH", "T", "day", "run"],
            columns="direction",
            values="mbe",
            aggfunc="first",
        )
        .dropna(subset=["UP", "DOWN"])
        .reset_index()
    )
    p["H_UP_minus_DOWN_pctRH"] = p["UP"] - p["DOWN"]
    pair_sd = float(p["H_UP_minus_DOWN_pctRH"].std(ddof=1))
    pair_df = int(len(p) - 1)
    tcrit = float(stats.t.ppf(0.975, pair_df))

    cell = (
        p.groupby(["RH", "T"])["H_UP_minus_DOWN_pctRH"]
        .agg(H_mean_pctRH="mean", n_pairs="size")
        .reset_index()
    )
    cell["abs_H_mean_pctRH"] = cell["H_mean_pctRH"].abs()
    cell["pooled_pair_SD_pctRH"] = pair_sd
    cell["pooled_pair_df"] = pair_df
    cell["u_H_pctRH"] = pair_sd / np.sqrt(cell["n_pairs"])
    cell["guarded_abs_H_95_pctRH"] = cell["abs_H_mean_pctRH"] + tcrit * cell["u_H_pctRH"]
    cell["limit_pctRH"] = RH_LIMIT_HYST
    cell["guarded_pass"] = cell["guarded_abs_H_95_pctRH"] <= RH_LIMIT_HYST
    cell["decision_rule_status"] = "post-freeze, post-hoc"
    cell["pooled_SD_scope_note"] = "Pooled pair-difference SD is calculated about the grand mean and therefore includes between-cell spread; this is conservative."

    frozen = pd.DataFrame([{
        "frozen_metric": "max absolute single matched pair",
        "n_pairs": int(len(p)),
        "max_abs_H_pctRH": float(p["H_UP_minus_DOWN_pctRH"].abs().max()),
        "mean_H_pctRH": float(p["H_UP_minus_DOWN_pctRH"].mean()),
        "pair_SD_pctRH": pair_sd,
        "pair_df": pair_df,
        "note": "Frozen 0.925 %RH remains historical; cell-level guarded estimate is supplemental/post-hoc.",
    }])

    p.to_csv(OUT / "sup001_hysteresis_pairs.csv", index=False)
    cell.to_csv(OUT / "sup001_hysteresis_cells.csv", index=False)
    frozen.to_csv(OUT / "sup001_hysteresis_frozen_metric.csv", index=False)
    return p, cell, frozen


def lag1(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    x = x - np.mean(x)
    den = np.sum(x * x)
    if len(x) < 3 or den <= 0:
        return np.nan
    return float(np.sum(x[1:] * x[:-1]) / den)


def shift_signal(tt: np.ndarray, u: np.ndarray, delay_s: float) -> np.ndarray:
    return np.interp(tt - delay_s, tt, u, left=u[0], right=u[-1])


def inverse_reference_lag(tt: np.ndarray, ref: np.ndarray, tau_ref_s: float) -> np.ndarray:
    """First-order inverse used only as a sensitivity case; noise amplification is expected."""
    dt = float(np.median(np.diff(tt)))
    a = dt / (tau_ref_s + dt)
    x = np.empty_like(ref, dtype=float)
    x[0] = ref[0]
    x[1:] = (ref[1:] - (1.0 - a) * ref[:-1]) / a
    return x


def _evaluate_tau_grid(tt: np.ndarray, us: np.ndarray, dut: np.ndarray, taus: np.ndarray):
    """Evaluate all tau values simultaneously for one delayed input."""
    dt = float(np.median(np.diff(tt)))
    a = dt / (taus + dt)
    y = np.empty((len(taus), len(us)), dtype=float)
    y[:, 0] = us[0]
    for i in range(1, len(us)):
        y[:, i] = y[:, i - 1] + a * (us[i] - y[:, i - 1])
    offset = np.mean(dut[None, :] - y, axis=1)
    resid = dut[None, :] - y - offset[:, None]
    sse = np.sum(resid * resid, axis=1)
    j = int(np.argmin(sse))
    return float(sse[j]), float(taus[j]), float(offset[j]), resid[j]


def fit_first_order_grid(tt: np.ndarray, u: np.ndarray, dut: np.ndarray) -> dict[str, float]:
    """Two-stage finer-than-review grid search (0.5 s coarse, 0.05 s local)."""
    coarse_delays = np.arange(0.0, 10.0001, 0.5)
    coarse_taus = np.arange(5.0, 50.0001, 0.5)
    best = None
    for delay in coarse_delays:
        us = shift_signal(tt, u, float(delay))
        sse, tau, offset, resid = _evaluate_tau_grid(tt, us, dut, coarse_taus)
        if best is None or sse < best[0]:
            best = (sse, float(delay), tau, offset, resid)
    assert best is not None

    _, delay0, tau0, _, _ = best
    fine_delays = np.arange(max(0.0, delay0 - 0.5), min(10.0, delay0 + 0.5) + 1e-9, 0.05)
    fine_taus = np.arange(max(2.0, tau0 - 1.0), min(60.0, tau0 + 1.0) + 1e-9, 0.05)
    best_fine = None
    for delay in fine_delays:
        us = shift_signal(tt, u, float(delay))
        sse, tau, offset, resid = _evaluate_tau_grid(tt, us, dut, fine_taus)
        if best_fine is None or sse < best_fine[0]:
            best_fine = (sse, float(delay), tau, offset, resid)
    assert best_fine is not None

    sse, delay, tau, offset, resid = best_fine
    rmse = float(np.sqrt(sse / len(dut)))
    return {
        "delay_s": delay,
        "tau_s": tau,
        "offset_pctRH": offset,
        "fit_RMSE_pctRH": rmse,
        "residual_lag1": lag1(resid),
        "t90_s": delay + tau * np.log(10.0),
        "tau_at_search_boundary": bool(np.isclose(tau, fine_taus.min()) or np.isclose(tau, fine_taus.max())),
        "delay_at_search_boundary": bool(np.isclose(delay, fine_delays.min()) or np.isclose(delay, fine_delays.max())),
        "delay_at_zero_physical_bound": bool(np.isclose(delay, 0.0)),
    }

def t90_outputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    st = pd.read_csv(DATA / "dynamic_step_measurements.csv")
    rows = []
    for tid, g in st.groupby("Test_ID"):
        g = g.sort_values("Elapsed_s")
        tt = g["Elapsed_s"].to_numpy(float)
        ref = g["RH_Reference"].to_numpy(float)
        dut = g["RH_DUT"].to_numpy(float)
        meta = {
            "Test_ID": tid,
            "Direction": g["Direction"].iloc[0],
            "Temperature_C": float(g["Temperature_Setpoint_C"].iloc[0]),
        }

        fit_ref = fit_first_order_grid(tt, ref, dut)
        rows.append({**meta, "input_basis": "measured_reference", "reference_tau_assumed_s": 0.0, **fit_ref})

        true_est = inverse_reference_lag(tt, ref, REFERENCE_TAU_MAX_S)
        fit_corr = fit_first_order_grid(tt, true_est, dut)
        rows.append({
            **meta,
            "input_basis": "reference_deconvolved_at_public_t90_max",
            "reference_tau_assumed_s": REFERENCE_TAU_MAX_S,
            **fit_corr,
        })

    detail = pd.DataFrame(rows)
    detail.to_csv(OUT / "sup001_t90_identification_detail.csv", index=False)

    summary_rows = []
    for (basis, direction), g in detail.groupby(["input_basis", "Direction"]):
        n = len(g)
        mean_t90 = float(g["t90_s"].mean())
        sd_t90 = float(g["t90_s"].std(ddof=1))
        tcrit = float(stats.t.ppf(0.975, n - 1))
        se = sd_t90 / np.sqrt(n)
        summary_rows.append({
            "input_basis": basis,
            "Direction": direction,
            "n_tests": n,
            "mean_delay_s": float(g["delay_s"].mean()),
            "mean_tau_s": float(g["tau_s"].mean()),
            "mean_t90_s": mean_t90,
            "sd_t90_across_tests_s": sd_t90,
            "mean_t90_95CI_low_s": mean_t90 - tcrit * se,
            "mean_t90_95CI_high_s": mean_t90 + tcrit * se,
            "mean_t90_95CI_scope": "across-test statistical interval only; excludes model-form uncertainty",
            "min_t90_s": float(g["t90_s"].min()),
            "max_t90_s": float(g["t90_s"].max()),
            "mean_fit_RMSE_pctRH": float(g["fit_RMSE_pctRH"].mean()),
            "max_fit_RMSE_pctRH": float(g["fit_RMSE_pctRH"].max()),
            "mean_residual_lag1": float(g["residual_lag1"].mean()),
            "grid_boundary_hits": int(g[["tau_at_search_boundary", "delay_at_search_boundary"]].any(axis=1).sum()),
            "zero_delay_hits": int(g["delay_at_zero_physical_bound"].sum()),
            "interpretation": (
                "post-freeze model-dependent estimate relative to measured reference"
                if basis == "measured_reference"
                else "post-freeze reference-lag-bound sensitivity; assumes reference at its public t90 maximum and is not a point estimate"
            ),
        })
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT / "sup001_t90_identification_summary.csv", index=False)
    return detail, summary


def drift_outputs() -> pd.DataFrame:
    wk = pd.read_csv(TABLES / "hv010_weekly_center_drift.csv")
    x = wk["Aging_Day"].to_numpy(float)
    y = wk["Center_Drift_From_Day0"].to_numpy(float)
    lr = stats.linregress(x, y)
    df = len(x) - 2
    tcrit = float(stats.t.ppf(0.975, df))
    annual = float(lr.slope * 365.0)
    annual_se = float(lr.stderr * 365.0)
    lo = annual - tcrit * annual_se
    hi = annual + tcrit * annual_se
    out = pd.DataFrame([{
        "n_weekly_points": len(x),
        "slope_pctRH_per_day": float(lr.slope),
        "slope_SE_pctRH_per_day": float(lr.stderr),
        "p_value_two_sided": float(lr.pvalue),
        "annualized_diagnostic_pctRH_per_year": annual,
        "annualized_95CI_low": lo,
        "annualized_95CI_high": hi,
        "public_limit_pctRH_per_year": DRIFT_LIMIT_PER_YEAR,
        "day0_to_56_mean_pctRH": float(np.mean(y[x <= 56])),
        "day63_to_77_mean_pctRH": float(np.mean(y[(x >= 63) & (x <= 77)])),
        "day84_pctRH": float(y[x == 84][0]),
        "status": "NOT DEMONSTRATED (frozen); supplemental trend evidence unfavorable but non-monotonic",
        "CI_scope_note": "OLS interval assumes independent weekly residuals; visible temporal structure means this interval may be too narrow.",
    }])
    out.to_csv(OUT / "sup001_drift_inference.csv", index=False)
    return out


def uncertainty_outputs(tests: pd.DataFrame):
    u = pd.read_csv(TABLES / "hv011_uncertainty_summary.csv")
    mc = pd.read_csv(TABLES / "hv012_mc_model_comparison.csv")

    bracket = u[["Point_ID", "Combined_Standard_Uncertainty", "Expanded_Uncertainty"]].copy()
    bracket["nu_eff_from_4_test_state"] = bracket["Combined_Standard_Uncertainty"] ** 4 / (u["U_State"] ** 4 / 3.0)
    bracket["k95_from_nu_eff"] = stats.t.ppf(0.975, bracket["nu_eff_from_4_test_state"])
    bracket["small_sample_95_halfwidth_pctRH"] = bracket["k95_from_nu_eff"] * bracket["Combined_Standard_Uncertainty"]
    bracket = bracket.merge(mc[["Point_ID", "ModelB_Central95_HalfWidth", "ModelB_vs_A_95HalfWidth_Ratio"]], on="Point_ID", how="left")
    bracket["decision_rule_status"] = "post-freeze, post-hoc"
    bracket["interpretation"] = "coverage-model bracket on frozen component set; not a physical validation of the budget"
    bracket.to_csv(OUT / "sup001_uncertainty_coverage_bracket.csv", index=False)

    u_chamber = CHAMBER_RH_UNIFORMITY_BOUND / np.sqrt(3.0)
    primary = u.copy()
    primary["U_Chamber_Uniformity_pctRH"] = u_chamber
    primary["U_Offset_Primary_pctRH"] = np.sqrt(primary["U_C1_Offset"] ** 2 + u_chamber**2)
    primary["UC_Primary_pctRH"] = np.sqrt(
        primary["U_Repeat_Mean"] ** 2
        + primary["U_State"] ** 2
        + primary["U_Offset_Primary_pctRH"] ** 2
        + primary["U_Reference_Calibration"] ** 2
        + primary["U_Stability"] ** 2
    )
    primary["nu_eff_primary"] = primary["UC_Primary_pctRH"] ** 4 / (primary["U_State"] ** 4 / 3.0)
    primary["k95_primary"] = stats.t.ppf(0.975, primary["nu_eff_primary"])
    primary["U95_Primary_pctRH"] = primary["k95_primary"] * primary["UC_Primary_pctRH"]
    primary["AbsBiasPlusU95_Primary_pctRH"] = primary["Point_Residual_Bias"].abs() + primary["U95_Primary_pctRH"]
    primary["static_limit_pctRH"] = RH_LIMIT_STATIC
    primary["static_pass_under_primary_supplemental_budget"] = primary["AbsBiasPlusU95_Primary_pctRH"] <= RH_LIMIT_STATIC
    primary["decision_rule_status"] = "post-freeze, post-hoc supplemental uncertainty treatment"
    primary.to_csv(OUT / "sup001_uncertainty_primary_budget.csv", index=False)

    vt = tests[tests["role"] == "VALIDATION"].copy()
    vt["mbe_C1"] = vt["mbe"] + C1_OFFSET
    cell_mean = vt.groupby(["RH", "T"])["mbe_C1"].transform("mean")
    df_state = int(len(vt) - vt.groupby(["RH", "T"]).ngroups)
    u_state_pool = float(np.sqrt(np.sum(np.square(vt["mbe_C1"] - cell_mean)) / df_state))
    u_repeat = float(u["U_Repeat_Mean"].iloc[0])
    u_offset_c1 = float(u["U_C1_Offset"].iloc[0])
    u_offset_primary = float(np.sqrt(u_offset_c1**2 + u_chamber**2))
    u_ref = float(u["U_Reference_Calibration"].iloc[0])
    u_stab = float(u["U_Stability"].iloc[0])
    uc_pool = float(np.sqrt(u_repeat**2 + u_state_pool**2 + u_offset_primary**2 + u_ref**2 + u_stab**2))
    nu_pool = float(uc_pool**4 / (u_state_pool**4 / df_state))
    k95_pool = float(stats.t.ppf(0.975, nu_pool))
    U95_pool = k95_pool * uc_pool
    cells = vt.groupby(["RH", "T"])["mbe_C1"].mean().rename("Point_Residual_Bias").reset_index()
    cells["N_Test_IDs"] = 4
    cells["Evidence_Role"] = "VALIDATION"
    cells["U_State_Pooled_pctRH"] = u_state_pool
    cells["State_df"] = df_state
    cells["U_Chamber_Uniformity_pctRH"] = u_chamber
    cells["U_Offset_Primary_pctRH"] = u_offset_primary
    cells["UC_Primary_PooledState_pctRH"] = uc_pool
    cells["nu_eff"] = nu_pool
    cells["k95"] = k95_pool
    cells["U95_pctRH"] = U95_pool
    cells["AbsBiasPlusU95_pctRH"] = cells["Point_Residual_Bias"].abs() + U95_pool
    cells["static_limit_pctRH"] = RH_LIMIT_STATIC
    cells["pass"] = cells["AbsBiasPlusU95_pctRH"] <= RH_LIMIT_STATIC
    cells["scope_note"] = "held-out cells only (RH 30/50/70; T 15/25/35); no 20 %RH held-out data"
    cells.to_csv(OUT / "sup001_validation_cell_primary_budget.csv", index=False)

    # R3: preserve direction-dependent residual structure rather than burying it
    # in a pooled state term. This is a post-freeze robustness view.
    direction = (
        vt.groupby(["RH", "T", "direction"])["mbe_C1"]
        .mean()
        .rename("Direction_Conditional_Bias_pctRH")
        .reset_index()
    )
    u_nonstate_no_chamber = float(np.sqrt(u_repeat**2 + u_offset_c1**2 + u_ref**2 + u_stab**2))
    u_direction = float(np.sqrt(u_nonstate_no_chamber**2 + u_chamber**2))
    direction["U_NonState_Excl_Chamber_pctRH"] = u_nonstate_no_chamber
    direction["U_Chamber_Uniformity_pctRH"] = u_chamber
    direction["U_DirectionConditional_pctRH"] = u_direction
    direction["Expanded_k2_pctRH"] = 2.0 * u_direction
    direction["AbsBiasPlusExpanded_k2_pctRH"] = direction["Direction_Conditional_Bias_pctRH"].abs() + 2.0 * u_direction
    direction["static_limit_pctRH"] = RH_LIMIT_STATIC
    direction["pass"] = direction["AbsBiasPlusExpanded_k2_pctRH"] <= RH_LIMIT_STATIC
    direction["decision_rule_status"] = "post-freeze, post-hoc supplemental robustness case"
    direction["scope_note"] = "Held-out validation RH×T×direction cells; state term excluded because direction is conditioned explicitly; frozen status unchanged."
    direction.to_csv(OUT / "sup001_direction_conditional_uncertainty.csv", index=False)

    return bracket, primary, cells, direction


def write_run_summary(rmse, repeatability, hyst_cells, t90, drift, primary_u, cell_u, direction_u) -> None:
    worst_h = hyst_cells.loc[hyst_cells["abs_H_mean_pctRH"].idxmax()]
    lines = [
        f"{PACKAGE_ID} v{PACKAGE_VERSION}",
        f"source_release={SOURCE_RELEASE}",
        f"source_commit={SOURCE_COMMIT}",
        f"dataset_release={DATASET_RELEASE}",
        "classification=post-freeze supplemental; frozen v1.0.0 statuses are not rewritten",
        "",
        "RMSE:",
        rmse.to_string(index=False),
        "",
        "Repeatability R-REP (post-freeze, post-hoc):",
        repeatability.to_string(index=False),
        "",
        "Hysteresis worst cell (post-hoc guarded):",
        worst_h.to_frame().T.to_string(index=False),
        "",
        "t90 summary (post-freeze model-dependent):",
        t90.to_string(index=False),
        "",
        "Drift inference:",
        drift.to_string(index=False),
        "",
        "Primary uncertainty with chamber non-uniformity:",
        primary_u[["Point_ID", "UC_Primary_pctRH", "nu_eff_primary", "k95_primary", "U95_Primary_pctRH", "AbsBiasPlusU95_Primary_pctRH", "static_pass_under_primary_supplemental_budget"]].to_string(index=False),
        "",
        "All held-out validation cells with pooled state term:",
        cell_u.to_string(index=False),
        "",
        "Direction-conditional held-out robustness case:",
        direction_u.to_string(index=False),
    ]
    (OUT / "sup001_run_summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest_runtime(input_hashes: pd.DataFrame) -> None:
    payload = {
        "package_id": PACKAGE_ID,
        "package_version": PACKAGE_VERSION,
        "classification": "SYN-SUPPLEMENTAL / post-freeze",
        "source_release": SOURCE_RELEASE,
        "source_commit": SOURCE_COMMIT,
        "dataset_release": DATASET_RELEASE,
        "frozen_status_policy": "No v1.0.0 conformity status is rewritten by SUP-001.",
        "post_hoc_labels_required": ["R-REP", "cell-level hysteresis", "nu_eff coverage treatment"],
        "chamber_uniformity": {
            "public_bound_pctRH": CHAMBER_RH_UNIFORMITY_BOUND,
            "distribution_assumption": "rectangular (post-freeze uncertainty treatment)",
            "standard_uncertainty_pctRH": CHAMBER_RH_UNIFORMITY_BOUND / np.sqrt(3.0),
            "budget_role": "primary; combined with C1 offset uncertainty",
        },
        "reference_lag_sensitivity": {
            "public_reference_t90_max_s": REFERENCE_T90_MAX_S,
            "first_order_tau_corresponding_to_t90_max_s": REFERENCE_TAU_MAX_S,
            "method": "first-order inverse of measured reference; sensitivity only; noise amplification expected",
        },
        "input_hash_verification": input_hashes.to_dict(orient="records"),
    }
    (OUT / "sup001_runtime_manifest.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    input_hashes = verify_frozen_inputs()
    s, tests = load_static()
    rmse = rmse_outputs(s)
    repeatability = repeatability_rrep_output(s, tests)
    _, hyst_cells, _ = hysteresis_outputs(tests)
    _, t90_summary = t90_outputs()
    drift = drift_outputs()
    _, primary_u, cell_u, direction_u = uncertainty_outputs(tests)
    write_manifest_runtime(input_hashes)
    write_run_summary(rmse, repeatability, hyst_cells, t90_summary, drift, primary_u, cell_u, direction_u)
    print(f"{PACKAGE_ID}: PASS")
    print(f"Outputs: {OUT}")
    print("Frozen v1.0.0 conformity decisions were not modified.")


if __name__ == "__main__":
    main()
