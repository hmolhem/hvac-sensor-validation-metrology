# HV-007 Handoff — Independent Blind Validation

## Milestone Identity

- Milestone: HV-007
- Branch: `feature/hv-007-independent-blind-validation`
- Technical gate: IV-001
- Notebook: `notebooks/04_blind_validation.ipynb`
- Input release: `VSM-LAB-DATA-v1.1`
- Outcome: **PASS WITH DOCUMENTED CONDITIONS**

## Objective

Evaluate the frozen C1 calibration model on the reserved STATIC / VALIDATION dataset without refitting, retuning, or replacing the model.

## Verified Validation Boundary

- VALIDATION Test_IDs: **36**
- measurement rows: **2,160**
- samples per Test_ID: **60**
- RH setpoints: **30, 50, 70 %RH**
- temperature setpoints: **15, 25, 35 °C**
- Direction: **UP, DOWN**
- Day: **3**
- Runs: **1, 2**
- modeling unit: **one summary row per VALIDATION Test_ID**

## Frozen Models

Primary deployable C1:

```text
RH_Calibrated = RH_DUT + 1.2266788194 %RH
```

Diagnostic C5:

- DOWN correction: +0.8164583333 %RH
- UP correction: +1.6368993056 %RH

No coefficient was altered after VALIDATION exposure.

## Blind-Validation Results

| Model | Role | RMSE (%RH) | MAE (%RH) | MBE (%RH) | Max Abs Error (%RH) |
|---|---|---:|---:|---:|---:|
| C0 Uncalibrated | Baseline | 1.1403 | 1.0583 | -1.0583 | 1.6960 |
| C1 Frozen Deployable | Primary | 0.4566 | 0.4046 | +0.1683 | 0.8275 |
| C5 Frozen Diagnostic | Diagnostic | 0.2131 | 0.1792 | +0.1683 | 0.4236 |

C1 improves RMSE by approximately **59.96%** and MAE by approximately **61.77%** relative to C0.

## Consistency With HV-006 Development Evidence

Frozen C1 RMSE:

- HV-006 Primary GroupCV: 0.5216 %RH
- HV-006 LOO-RH: 0.4535 %RH
- HV-006 LOO-Day: 0.4505 %RH
- HV-007 Blind Validation: 0.4566 %RH

The independent validation RMSE is therefore highly consistent with the pre-validation robustness evidence.

## Residual Structure

### RH

C1 MBE:
- 30 %RH: +0.0926 %RH
- 50 %RH: +0.2421 %RH
- 70 %RH: +0.1703 %RH

### Temperature

C1 MBE:
- 15 °C: +0.2353 %RH
- 25 °C: +0.1628 %RH
- 35 °C: +0.1069 %RH

C1 MAE remains stable:
- 15 °C: 0.4016 %RH
- 25 °C: 0.4156 %RH
- 35 °C: 0.3968 %RH

Interpretation: a mild temperature-related residual-center trend is visible, but no material temperature-dependent degradation in absolute error is observed over 15–35 °C.

### Direction

After C1:
- DOWN MBE: +0.5722 %RH
- UP MBE: -0.2356 %RH
- residual separation: approximately **0.8078 %RH**

This independently reproduces the Direction/hysteresis effect identified in HV-006.

After frozen C5:
- DOWN MBE: +0.1620 %RH
- UP MBE: +0.1746 %RH

C5 largely collapses the Direction split, confirming the state-dependent interpretation.

### Run

C1 MBE:
- Run 1: +0.2252 %RH
- Run 2: +0.1115 %RH

The Run difference is secondary relative to Direction.

## IV-001 Gate

Final decision:

**IV-001 = PASS WITH DOCUMENTED CONDITIONS**

Documented conditions:

1. Frozen C1 leaves a small positive validation-wide residual bias of approximately +0.1683 %RH.
2. Memoryless C1 retains a substantial Direction/hysteresis residual structure of approximately 0.8078 %RH.
3. A mild temperature-related center trend is observed, but C1 MAE remains stable across 15–35 °C.
4. C5 remains diagnostic/state-aware and cannot replace C1 unless Direction is operationally available.
5. HV-007 validates independent static generalization only; final sensor suitability remains open pending dynamic response, stability/drift, and uncertainty analysis.

## Curated Evidence

Notebook 04 exports:

- `reports/tables/hv007_validation_design_summary.csv`
- `reports/tables/hv007_validation_model_comparison.csv`
- `reports/tables/hv007_validation_residual_by_rh.csv`
- `reports/tables/hv007_validation_residual_by_temperature.csv`
- `reports/tables/hv007_validation_residual_by_direction.csv`
- `reports/tables/hv007_validation_residual_by_run.csv`

## Next Engineering Stage

HV-008 — Dynamic Step Response.
