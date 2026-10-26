# HV-006 Handoff — Calibration Model Development

## Milestone Identity

- Milestone: HV-006
- Branch: `feature/hv-006-calibration-model-development`
- Technical gate: CM-001
- Notebook: `notebooks/03_calibration_model.ipynb`
- Input release: `VSM-LAB-DATA-v1.1`
- Outcome: **PASS WITH DOCUMENTED CONDITIONS**

## Objective

Develop and freeze an RH calibration model using CALIBRATION evidence only, while preserving the reserved VALIDATION measurements as blind independent evidence.

The engineering objective was to determine the simplest deployable correction that improves DUT agreement with the reference without leaking validation information or relying on non-operational variables.

## Verified Calibration Boundary

- STATIC / CALIBRATION Test_IDs: **96**
- samples per Test_ID: **60**
- measurement rows: **5,760**
- RH setpoints: **20, 40, 60, 80 %RH**
- temperature setpoints: **15, 25, 35 °C**
- directions: **UP, DOWN**
- days: **1, 2**
- runs: **1, 2**
- RH × Temperature × Direction condition groups: **24**
- modeling unit: **one summary row per Test_ID**
- reserved VALIDATION measurement values used: **0**

The calibration target was:

```text
Correction_RH = RH_Reference_Mean - RH_DUT_Mean
```

with post-calibration residual:

```text
Residual_Cal = RH_Calibrated - RH_Reference
```

## Leakage-Control and Validation Design

Sample-level random splitting was prohibited.

Primary internal assessment used group-aware cross-validation with:

```text
Condition_ID = RH_Setpoint × Temperature_Setpoint_C × Direction
```

All Day × Run repetitions of a condition remained in the same fold.

Additional robustness checks:

- leave-one-RH-setpoint-out;
- leave-one-day-out.

The reserved VALIDATION measurements were not used for fitting, tuning, candidate selection, robustness analysis, or model freeze.

## Candidate Models

- C0 — uncalibrated baseline;
- C1 — constant-offset correction;
- C2 — RH-only linear correction;
- C3 — RH + DUT-temperature linear correction;
- C4 — degree-2 RH/temperature polynomial Ridge correction;
- C5 — Direction-augmented diagnostic model.

## Primary Out-of-Fold Results

| Model | Role | RMSE (%RH) | MAE (%RH) | MBE (%RH) |
|---|---|---:|---:|---:|
| C0 Uncalibrated | Baseline | 1.3045 | 1.2267 | -1.2267 |
| C1 Constant Offset | Deployable | 0.5216 | 0.4923 | 0.0000 |
| C2 RH Linear | Deployable | 0.5243 | 0.4914 | 0.0000 |
| C3 RH + Temperature Linear | Deployable | 0.6622 | 0.6316 | 0.0015 |
| C4 Polynomial Ridge | Deployable | 0.6509 | 0.6249 | 0.0080 |
| C5 Direction Diagnostic | Diagnostic | 0.1779 | 0.1449 | 0.0000 |

C1 reduces RMSE by approximately **60%** relative to C0.

C2 does not materially improve on C1.

C3 and C4 perform materially worse than C1 under group-aware assessment.

## Dominant Residual Structure

After C1, mean residual by Direction remained approximately:

- DOWN: **+0.4923 %RH**
- UP: **-0.4923 %RH**

After C5, the Direction-conditioned mean residuals collapse to approximately zero.

This identifies **Direction / hysteresis / state dependence** as the dominant remaining systematic structure.

## Robustness Results

### C1

- Primary GroupCV RMSE: **0.5216 %RH**
- Leave-one-RH RMSE: **0.4535 %RH**
- Leave-one-day RMSE: **0.4505 %RH**

Held-out RH fold RMSE remained approximately **0.44–0.47 %RH**, including edge conditions 20 and 80 %RH.

### C5 Diagnostic

- Primary GroupCV RMSE: **0.1779 %RH**
- Leave-one-RH RMSE: **0.1933 %RH**
- Leave-one-day RMSE: **0.1862 %RH**

Held-out RH fold RMSE remained approximately **0.13–0.22 %RH**.

The fitted UP increment remained highly stable at approximately **0.82 %RH** across robustness checks.

## Frozen Models

### Canonical deployable model — C1

Frozen equation:

```text
RH_Calibrated = RH_DUT + 1.2266788194 %RH
```

Canonical artifact:

```text
config/calibration_model_v1.json
```

### State-aware diagnostic model — C5

Frozen parameters:

- DOWN correction: **+0.8164583333 %RH**
- UP increment: **+0.8204409722 %RH**
- UP correction: **+1.6368993056 %RH**

Equivalent equations:

```text
DOWN:
RH_Calibrated = RH_DUT + 0.8164583333

UP:
RH_Calibrated = RH_DUT + 1.6368993056
```

Diagnostic artifact:

```text
config/calibration_model_direction_diagnostic_v1.json
```

C5 is **not** the default deployable field model unless Direction can be operationally and reliably determined in service.

## CM-001 Gate

Final decision:

**CM-001 = PASS WITH DOCUMENTED CONDITIONS**

Documented condition:

> The selected memoryless deployable model C1 substantially reduces global calibration bias but does not remove the dominant Direction/hysteresis effect. A state-aware Direction model produces much lower residual error, but it is retained as diagnostic evidence until Direction can be defined as a reliable operational field input.

## Curated Evidence

HV-006 exports:

- `reports/tables/hv006_calibration_design_summary.csv`
- `reports/tables/hv006_cv_fold_metrics.csv`
- `reports/tables/hv006_model_comparison.csv`
- `reports/tables/hv006_selected_model_coefficients.csv`
- `reports/tables/hv006_selected_model_residual_summary.csv`

## Reusable Analysis Infrastructure

HV-006 introduced:

- `src/calibration_analysis.py`
- CALIBRATION-only loading;
- Test_ID-level calibration summarization;
- calibration-design auditing;
- group-aware model comparison;
- robustness stress testing;
- canonical JSON model freeze records.

## Next Engineering Stage

HV-007 — Independent Blind Validation.

The frozen C1 model must be applied to the reserved VALIDATION measurements without refitting or tuning.

C5 may be evaluated separately as a diagnostic/state-aware comparator, but must not replace the frozen deployable C1 model after looking at validation results.
