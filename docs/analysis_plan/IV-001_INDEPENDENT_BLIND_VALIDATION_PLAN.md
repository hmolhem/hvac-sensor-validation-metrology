# IV-001 — Independent Blind Validation Plan

## Milestone

- Project milestone: HV-007 — Independent Blind Validation
- Technical gate: IV-001
- Notebook: `notebooks/04_blind_validation.ipynb`
- Frozen dataset release: `VSM-LAB-DATA-v1.1`

## Engineering Question

> Does the frozen C1 calibration model improve agreement between the DUT and reference on the reserved STATIC / VALIDATION data, without refitting, retuning, or changing the frozen model?

This milestone evaluates independent static generalization only.

It does **not** make the final HVAC suitability decision. Dynamic response, stability/drift, and measurement uncertainty remain separate downstream evidence.

## Blind-Validation Governance

Before any VALIDATION measurement value is inspected:

1. The deployable model identity is frozen as C1.
2. The C1 parameter is frozen from HV-006.
3. No model coefficient may be changed after VALIDATION exposure.
4. No alternative deployable model may be selected using VALIDATION performance.
5. C5 may be evaluated only as a diagnostic/state-aware comparator.
6. VALIDATION data are not calibration data and may not be recycled into fitting.
7. Hidden simulator truth remains prohibited.

Canonical C1 artifact:

```text
config/calibration_model_v1.json
```

Frozen equation:

```text
RH_Calibrated = RH_DUT + 1.2266788194 %RH
```

Canonical C5 diagnostic artifact:

```text
config/calibration_model_direction_diagnostic_v1.json
```

## Validation Data Boundary

The public test matrix defines the reserved STATIC / VALIDATION design as:

- RH setpoints: 30, 50, 70 %RH;
- temperature setpoints: 15, 25, 35 °C;
- Direction: UP, DOWN;
- Day: 3;
- Run: 1, 2;
- 36 VALIDATION Test_IDs;
- 60 samples per Test_ID expected;
- 2,160 measurement rows expected.

The validation RH levels are interleaved between the calibration RH levels:

```text
CALIBRATION: 20, 40, 60, 80 %RH
VALIDATION : 30, 50, 70 %RH
```

This provides independent interpolation-like static validation across the tested calibration range.

## Primary Experimental Unit

The primary validation unit is one summary row per VALIDATION Test_ID.

The 60 time samples within a Test_ID are repeated samples under the same nominal condition and are not treated as 60 independent validation experiments.

## Frozen Error Definitions

Pre-calibration error:

```text
Error_RH_Pre = RH_DUT_Mean - RH_Reference_Mean
```

C1 calibrated RH:

```text
RH_Calibrated_C1 = RH_DUT_Mean + Frozen_C1_Offset
```

Post-calibration residual:

```text
Residual_C1 = RH_Calibrated_C1 - RH_Reference_Mean
```

C5 is calculated separately as diagnostic evidence using the frozen UP/DOWN corrections.

## Primary Validation Metrics

For C0 (uncalibrated) and frozen C1, report:

- N Test_IDs;
- MBE;
- MAE;
- RMSE;
- median error;
- residual SD;
- maximum absolute error;
- R².

Primary performance metric:

```text
RMSE
```

The validation report must also show absolute and percentage RMSE/MAE change from C0 to C1.

R² is descriptive only and is not sufficient evidence of calibration accuracy.

## Residual-Structure Diagnostics

Frozen C1 residuals must be summarized by:

- RH setpoint;
- temperature setpoint;
- Direction;
- Run.

Direction is especially important because HV-006 identified Direction/hysteresis as the dominant remaining systematic structure in memoryless calibration.

## Comparison With Development Evidence

The independent C1 validation metrics will be compared with the frozen HV-006 development evidence:

```text
Primary GroupCV RMSE = 0.5215597009 %RH
LOO-RH RMSE          = 0.4534672250 %RH
LOO-Day RMSE         = 0.4504817678 %RH
```

This comparison is descriptive.

No post-hoc tolerance band will be invented after viewing validation performance.

## C5 Diagnostic Comparator

The frozen C5 state-aware diagnostic may be applied to the same VALIDATION Test_ID summaries using:

```text
DOWN correction = +0.8164583333 %RH
UP correction   = +1.6368993056 %RH
```

Its purpose is to test whether the Direction/hysteresis structure identified in HV-006 independently persists in the reserved validation data.

C5 cannot replace C1 as the deployable model based on validation results.

## Interpretation Framework

The blind-validation conclusion will answer three separate questions:

1. **Did frozen C1 improve independent static validation performance relative to uncalibrated C0?**
2. **How consistent is C1 validation performance with the internal calibration-development evidence?**
3. **Does Direction/hysteresis remain the dominant residual structure, and does frozen C5 reproduce its diagnostic advantage?**

Do not conflate these questions with final product suitability.

## Planned Curated Outputs

Tables:

```text
reports/tables/hv007_validation_design_summary.csv
reports/tables/hv007_validation_model_comparison.csv
reports/tables/hv007_validation_residual_by_rh.csv
reports/tables/hv007_validation_residual_by_temperature.csv
reports/tables/hv007_validation_residual_by_direction.csv
reports/tables/hv007_validation_residual_by_run.csv
```

Figures may be added after numerical validation is reviewed.

## IV-001 Completion Criteria

| Criterion | Requirement |
|---|---|
| V01 | STATIC / VALIDATION boundary verified before analysis |
| V02 | 36 VALIDATION Test_IDs and 60 samples/Test_ID verified |
| V03 | Frozen C1 JSON artifact loaded and parameter identity verified |
| V04 | C1 applied without refitting, retuning, or coefficient changes |
| V05 | Test_ID-level summary used as primary validation unit |
| V06 | C0 and C1 MBE/MAE/RMSE/median/SD/max/R² reported |
| V07 | C1 residual structure checked versus RH, temperature, Direction, Run |
| V08 | Independent performance compared descriptively with frozen HV-006 evidence |
| V09 | Frozen C5 evaluated only as diagnostic comparator |
| V10 | No VALIDATION result used to alter C1 identity or coefficient |
| V11 | Curated validation tables exported |
| V12 | Notebook reproduces from Restart Kernel -> Run All |

## Gate Outcomes

- **PASS** — blind-validation protocol is complete and independent evidence supports the frozen C1 model without a material undocumented limitation.
- **PASS WITH DOCUMENTED CONDITIONS** — protocol is complete and C1 remains usable as frozen, but important independent residual structure or performance limitations must be carried forward.
- **FAIL** — protocol integrity is broken, the frozen model is not applied as specified, or independent validation shows a blocking calibration failure that prevents carrying C1 forward unchanged.

Any model-performance finding must be reported as observed. The gate must not be manipulated by post-hoc retuning.

## Next Stage

After IV-001 closure:

```text
HV-008 — Dynamic Step Response
```
