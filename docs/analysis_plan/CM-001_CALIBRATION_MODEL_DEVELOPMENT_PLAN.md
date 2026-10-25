# CM-001 Calibration Model Development Plan

## Milestone Identity

- Milestone: HV-006
- Technical gate: CM-001
- Branch: `feature/hv-006-calibration-model-development`
- Notebook: `notebooks/03_calibration_model.ipynb`
- Input release: `VSM-LAB-DATA-v1.1`
- Analysis role: `STATIC / CALIBRATION`
- Downstream independent validation notebook: `notebooks/04_blind_validation.ipynb`

## Engineering Question

Can a calibration model built only from the frozen CALIBRATION subset reduce systematic RH measurement error while preserving interpretability, avoiding experimental-unit leakage, and remaining suitable for later blind independent validation?

HV-006 develops and freezes the calibration model. It does **not** evaluate performance on the VALIDATION measurements.

## Scientific Boundary

The calibration model may use only analyst-visible evidence.

Allowed:
- `STATIC / CALIBRATION` measurements;
- public test-matrix design metadata;
- DUT-observable measurement quantities;
- quantities derived only from CALIBRATION data.

Prohibited during HV-006:
- VALIDATION measurement values or validation performance metrics;
- hidden simulator truth;
- private DUT personality/configuration;
- any tuning decision informed by Notebook 04 results.

The VALIDATION design may be acknowledged only as a boundary/provenance fact. Its measured values remain blind until HV-007 / Notebook 04.

## Calibration Design Audit

The frozen test matrix defines **96 CALIBRATION Test_IDs**:

```text
4 RH setpoints
x 3 temperature setpoints
x 2 directions
x 2 days
x 2 runs
= 96 Test_IDs
```

Calibration RH setpoints:

```text
20, 40, 60, 80 %RH
```

Calibration temperature setpoints:

```text
15, 25, 35 degC
```

Other calibration factors:

- Direction: Up / Down
- Day: 1 / 2
- Run: 1 / 2
- Expected samples per Test_ID: 60
- Underlying CALIBRATION measurement rows: expected 5,760

The reserved validation design contains 36 STATIC / VALIDATION Test_IDs and is not used for model development.

## Unit of Analysis

The primary model-development unit is **one summary record per CALIBRATION Test_ID**, not individual 1 Hz samples.

Reason:

- the 60 samples inside a Test_ID are repeated measurements under one nominal experimental condition;
- treating all 5,760 rows as independent training observations would create pseudoreplication and overly optimistic model assessment;
- Test_ID-level means align model development with the experimental unit already used in HV-004 and HV-005.

For each CALIBRATION Test_ID, compute at minimum:

- `RH_DUT_Mean`
- `RH_Reference_Mean`
- `Temperature_DUT_Mean_C`
- `Temperature_Reference_Mean_C` for diagnostic/reference comparison only
- `RH_Setpoint`
- `Temperature_Setpoint_C`
- `Direction`
- `Day_ID`
- `Run_ID`
- `N_Samples`
- within-Test_ID RH standard deviation

## Calibration Target

Define the required correction as:

```text
Correction_RH = RH_Reference_Mean - RH_DUT_Mean
```

The fitted model predicts:

```text
Predicted_Correction_RH = f(DUT-observable predictors)
```

and the calibrated RH result is:

```text
RH_Calibrated = RH_DUT + Predicted_Correction_RH
```

The post-calibration residual convention is:

```text
Residual_Cal = RH_Calibrated - RH_Reference
```

Therefore a well-centered calibration should have residual MBE near zero, but MBE alone is not sufficient for model acceptance.

This correction-target formulation is preferred because the DUT and reference report the same measurand and units, making systematic error structure directly visible.

## Predictor Eligibility

### Primary deployable predictors

The main model-selection track may use only variables plausibly available from the DUT during field operation:

- `RH_DUT_Mean`
- `Temperature_DUT_Mean_C`

### Diagnostic design factor

`Direction` may be evaluated in a separate diagnostic model track because HV-004 established a substantial UP/DOWN structure.

However, Direction is not automatically considered a deployable predictor. A direction-aware model is eligible for final freeze only if a clear operational rule exists for obtaining Direction from field data.

### Excluded predictors

The following must not be used as calibration predictors:

- `RH_Reference` or any derived reference quantity;
- `Temperature_Reference_C`;
- `RH_Setpoint`;
- `Temperature_Setpoint_C`;
- `Day_ID`;
- `Run_ID`;
- `Test_ID`;
- `Sample_ID`;
- hidden simulator variables.

Rationale:

- reference quantities are target-side information unavailable during deployment;
- chamber setpoints are experiment controls, not general field observables;
- Day/Run/Test_ID identify experimental execution rather than physical sensor inputs.

## Candidate Model Hierarchy

The model hierarchy intentionally starts simple and increases complexity only when calibration-only evidence supports it.

### C0 — Uncalibrated baseline

```text
Predicted_Correction_RH = 0
```

Purpose: quantify the improvement achieved by calibration.

### C1 — Constant offset correction

```text
Predicted_Correction_RH = mean training correction
```

Purpose: test whether a single offset is sufficient.

HV-004 already suggests this will be inadequate, but it remains an important baseline.

### C2 — RH-only linear correction

```text
Correction_RH = beta0 + beta1 * RH_DUT
```

Purpose: simplest slope/offset correction.

### C3 — RH + DUT-temperature linear correction

```text
Correction_RH =
    beta0
  + beta1 * RH_DUT
  + beta2 * Temperature_DUT
```

Purpose: account for systematic temperature sensitivity using an operationally available predictor.

### C4 — Low-order nonlinear deployable correction

Use second-order polynomial / interaction features derived from:

```text
RH_DUT
Temperature_DUT
```

Candidate terms may include:

```text
RH_DUT
Temperature_DUT
RH_DUT^2
RH_DUT * Temperature_DUT
Temperature_DUT^2
```

Use regularized linear regression where appropriate to control coefficient instability.

No polynomial degree above 2 is allowed in CM-001 unless a documented calibration-only residual pattern demonstrates a specific need.

### C5 — Direction-augmented diagnostic model

Evaluate whether adding Direction materially removes residual hysteresis structure.

This model is diagnostic by default and is not automatically eligible as the frozen deployable calibration.

## Model-Development Principle

Model complexity must be earned by calibration-only evidence.

A more complex model is not preferred merely because its in-sample fit is better.

The selected calibration must balance:

- cross-validated error;
- residual structure;
- coefficient/model stability;
- physical interpretability;
- deployability;
- parsimony.

## Internal Validation Strategy

### Prohibition on sample-level random splitting

Random train/test splitting of the 5,760 individual samples is prohibited because repeated samples from the same Test_ID would leak nearly identical experimental conditions across folds.

### Primary grouped cross-validation

Create a physical-condition group:

```text
Condition_ID =
RH_Setpoint x Temperature_Setpoint_C x Direction
```

There are 24 physical-condition groups, each represented by Day x Run repetitions.

Use grouped cross-validation so all repetitions of a condition remain together in either training or assessment data for a fold.

Primary model-comparison statistics are computed from out-of-fold predictions only.

### Calibration-only stress tests

After the primary grouped comparison, perform additional robustness checks without using VALIDATION measurements:

1. **Leave-one-RH-setpoint-out**
   - 4 folds using calibration RH = 20, 40, 60, 80 %RH.
   - Tests sensitivity to RH-level generalization and exposes fragile high-order fits.

2. **Leave-one-day-out**
   - Day 1 vs Day 2.
   - Tests sensitivity to the intermediate-precision shift identified in HV-005.

3. **Residual structure checks**
   - residual vs predicted correction;
   - residual vs RH_DUT;
   - residual vs Temperature_DUT;
   - residual grouped by RH setpoint;
   - residual grouped by temperature;
   - residual grouped by Direction;
   - residual grouped by Day and Run for diagnosis only.

## Evaluation Metrics

Primary model-selection metric:

- cross-validated RMSE of `Residual_Cal`.

Secondary metrics:

- MAE;
- MBE;
- median error;
- maximum absolute error;
- residual standard deviation;
- R-squared, reported as a descriptive model metric but **not** used alone to select the calibration.

Metrics must be calculated from out-of-fold predictions during model comparison.

In-sample fit metrics may be reported separately but must not be presented as model-validation evidence.

## Residual Analysis

Residual analysis is mandatory.

A candidate model must be examined for:

- non-zero center;
- RH-dependent structure;
- temperature-dependent structure;
- Direction-dependent structure;
- heteroscedasticity;
- influential/extreme Test_IDs;
- Day/Run structure that remains after calibration.

Outliers are not automatically deleted. Any exclusion requires a traceable engineering reason.

## Model Selection Rule

1. Compare C0-C4 using the primary grouped cross-validation.
2. Rank deployable candidates primarily by mean CV RMSE.
3. Examine MAE, absolute MBE, residual SD, and maximum absolute error.
4. Apply a parsimony rule:
   - if a simpler deployable model performs within approximately one cross-validation standard error of the best deployable model and has no materially worse residual structure, prefer the simpler model.
5. Use the leave-one-RH and leave-one-day stress tests as robustness checks.
6. Evaluate C5 separately to quantify the value of explicit Direction information.
7. Do not choose the final model using any VALIDATION measurement result.

The selected model must have a documented engineering rationale, not only a numerical rank.

## Final Model Freeze

After candidate selection:

1. refit the selected model using all 96 CALIBRATION Test_ID summaries;
2. freeze the model before any VALIDATION measurement is analyzed;
3. export machine-readable model metadata.

Canonical freeze artifact:

```text
config/calibration_model_v1.json
```

The artifact should include at minimum:

- model ID and version;
- source dataset release;
- HV/CM identifiers;
- target definition;
- predictor list;
- preprocessing definitions;
- feature names after transformation;
- fitted intercept and coefficients or equivalent model parameters;
- regularization parameter if used;
- calibration Test_ID count;
- code/library version information;
- model-selection summary;
- statement that VALIDATION measurements were not used.

A binary serialized estimator may be created for convenience only if needed; the JSON specification remains the human-auditable canonical freeze record.

## Planned Curated Outputs

Tables:

```text
reports/tables/hv006_calibration_design_summary.csv
reports/tables/hv006_model_comparison.csv
reports/tables/hv006_cv_fold_metrics.csv
reports/tables/hv006_selected_model_residual_summary.csv
reports/tables/hv006_selected_model_coefficients.csv
```

Figures:

```text
reports/figures/hv006_calibration_error_structure.png
reports/figures/hv006_model_comparison.png
reports/figures/hv006_residual_vs_rh.png
reports/figures/hv006_residual_vs_temperature.png
reports/figures/hv006_pre_post_calibration.png
```

## Relationship to HV-004 and HV-005

HV-004 established the pre-calibration static-performance baseline:

- persistent negative error;
- substantial Direction dependence;
- temperature response dependent on RH context;
- constant offset not sufficient.

HV-005 established the measurement-variation baseline:

- pooled repeatability SD ≈ 0.259265 %RH;
- small persistent Run shift;
- small persistent Day 2 vs Day 1 shift;
- systematic shifts must not be confused with random scatter.

HV-006 must preserve these findings when interpreting residuals. Calibration may reduce systematic bias, but it does not automatically improve underlying measurement precision.

## CM-001 Completion Criteria

| Criterion | Requirement |
|---|---|
| C01 | STATIC / CALIBRATION data only for model development |
| C02 | 96 CALIBRATION Test_IDs and expected 60 samples/Test_ID verified |
| C03 | VALIDATION measurement values not used in fitting, tuning, or model selection |
| C04 | Test_ID-level summary used as the primary modeling unit |
| C05 | Correction target and post-calibration residual sign convention verified |
| C06 | Predictor eligibility/leakage rules enforced |
| C07 | C0-C4 candidate hierarchy evaluated |
| C08 | Group-aware internal cross-validation used; no sample-level random leakage |
| C09 | RMSE, MAE, MBE, residual SD, max absolute error, and R-squared reported appropriately |
| C10 | Leave-one-RH and leave-one-day robustness checks completed |
| C11 | Residual structure evaluated versus RH, temperature, Direction, Day, and Run |
| C12 | Selected model justified by performance, residuals, parsimony, and deployability |
| C13 | Final model refit on all CALIBRATION Test_ID summaries and frozen to `config/calibration_model_v1.json` |
| C14 | Notebook reproduces from Restart Kernel -> Run All with no hidden simulator truth |

## Gate Outcomes

- **PASS** — all blocking CM-001 criteria satisfied and model frozen.
- **PASS WITH DOCUMENTED CONDITIONS** — model is frozen but a non-blocking calibration limitation is explicitly documented.
- **FAIL** — one or more blocking criteria are not satisfied.

No VALIDATION performance claim is permitted at CM-001. That question belongs to the next independent-validation milestone.

## Methodological References

- NIST/SEMATECH Engineering Statistics Handbook, instrument calibration over a regime: calibration-data analysis should begin with graphical examination, linear calibration should be considered, same-unit difference plots are informative, and residual structure must be checked.
- NIST/SEMATECH Engineering Statistics Handbook: day-to-day effects and poor precision can compromise calibration; calibration does not itself improve measurement precision.
- scikit-learn `GroupKFold`: non-overlapping groups are kept out of both train and test portions of the same fold, supporting the Test_ID/condition leakage-control strategy used here.
