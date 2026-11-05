# SUP-001 — Controlled Supplemental Analysis

Status: **SYN-SUPPLEMENTAL / post-freeze**

This package contains controlled post-freeze analyses requested by the Technical Evidence Review and its second-pass reconciliation review. It is based on the immutable analytical baseline:

- Source release: `v1.0.0`
- Source commit: `dce3b9b9d4e44fddceceada67641b41cb3dd8050`
- Frozen dataset: `VSM-LAB-DATA-v1.1`

SUP-001 **does not rewrite any frozen v1.0.0 conformity status**. Supplemental results must be labeled post-freeze; any decision rule introduced after v1.0.0 must also be labeled post-hoc.

## Reviewer disposition carried into SUP-001

| Finding | Disposition | SUP-001 control |
|---|---|---|
| F1 t90 | ACCEPT WITH MODIFICATION | Fine-grid identification, residual diagnostics, reference-lag sensitivity; estimates remain model-dependent and relative to reference |
| F2 drift | ACCEPT | Add 95% CI to the 90-day slope/annualized diagnostic |
| F3 blindness terminology | ACCEPT | Report terminology is “parameter-blind held-out validation” |
| F4 decision rules | ACCEPT | Cell-level hysteresis rule is explicitly post-freeze/post-hoc |
| F5 repeatability | ACCEPT WITH MODIFICATION | Any method-defined PASS is post-freeze/post-hoc; frozen headline status remains NOT DEMONSTRATED |
| F6 effective DOF / k | ACCEPT | Compute effective DOF and 95% coverage sensitivity |
| F7 uncertainty scope | ACCEPT WITH MODIFICATION | Chamber RH non-uniformity is included in the **primary** supplemental budget; 20% RH has no held-out evidence |
| F8 Monte Carlo framing | ACCEPT | MC is propagation/implementation verification, not physical-model validation |
| F9 RMSE definition | ACCEPT | Report Test_ID-mean and per-reading RMSE separately |
| F10 offset transfer | ACCEPT | Preserve held-out residual-bias evidence |
| F11 traceability wording | ACCEPT | Synthetic reference has assumed calibration attributes only |
| F12 realism limits | ACCEPT | Retained as model-realism limitations |
| F13 lag wording | ACCEPT | “Intrinsic” reserved for explicit model parameters |

## Outputs

The workflow generates and archives:

- `outputs/sup001_rmse_levels.csv`
- `outputs/sup001_hysteresis_pairs.csv`
- `outputs/sup001_hysteresis_cells.csv`
- `outputs/sup001_hysteresis_frozen_metric.csv`
- `outputs/sup001_repeatability_rrep.csv`
- `outputs/sup001_t90_identification_detail.csv`
- `outputs/sup001_t90_identification_summary.csv`
- `outputs/sup001_drift_inference.csv`
- `outputs/sup001_uncertainty_coverage_bracket.csv`
- `outputs/sup001_uncertainty_primary_budget.csv`
- `outputs/sup001_validation_cell_primary_budget.csv`
- `outputs/sup001_direction_conditional_uncertainty.csv`
- `outputs/sup001_input_hashes.csv`
- `outputs/sup001_runtime_manifest.json`
- `outputs/sup001_run_summary.txt`
- `SHA256SUMS.txt`

## Key controls

1. The frozen raw static and dynamic-step CSV hashes are verified before analysis.
2. The environment is pinned in `requirements.txt` and the workflow pins Python.
3. t90 identification uses a finer delay/tau grid than the review prototype and includes residual lag-1 diagnostics. The first-order-plus-delay model mirrors the public generator structure; this is part of the parameter-blind framing and is not independent model discovery.
4. A reference-lag sensitivity uses the public reference limit `t90 <= 10 s`, corresponding to `tau_ref <= 10/ln(10) ≈ 4.343 s` under a first-order model.
5. Chamber RH uniformity `±0.30 %RH` is converted to a rectangular Type-B standard uncertainty `0.30/sqrt(3)` and included in the primary supplemental uncertainty budget.
6. Held-out cell uncertainty uses only the 9 validation cells (RH 30/50/70 × T 15/25/35). No held-out claim is made at 20 %RH.
7. All generated files are SHA-256 hashed.
8. R-REP repeatability evidence is emitted as a controlled post-freeze/post-hoc output.
9. Direction-conditional RH × T × direction uncertainty is emitted as a robustness case so direction structure is not buried in the pooled state term.
10. t90 mean confidence intervals are across-test statistical intervals only and do not represent model-form uncertainty.
11. The reference-lag-corrected t90 result is a sensitivity bound based on the public reference t90 maximum, not a point estimate.

## Interpretation boundary

- Frozen v1.0.0 statuses remain the historical record.
- SUP-001 may strengthen or qualify interpretation, but it does not silently change the frozen release.
- Chapters 12, 14 and 16 may cite SUP-001 only after its workflow completes successfully and its outputs/hashes are archived.


## REVIEW-008 close-out changes

This package incorporates the blocking items identified in 08_SUP001_TARGETED_VERIFICATION:

- **R2**: adds `sup001_repeatability_rrep.csv` with Bartlett/Levene homogeneity tests, lag-1 autocorrelation, common-sigma UCL, max-SD probability, and Bonferroni per-test UCL count. It is explicitly labelled post-freeze/post-hoc.
- **R3**: adds `sup001_direction_conditional_uncertainty.csv` using RH × T × direction conditional bias with the state term excluded and chamber non-uniformity retained.
- Coverage-bracket outputs now carry an explicit post-freeze/post-hoc label.
- Drift CI includes the OLS residual-independence caveat.
- Hysteresis notes that the pooled pair-difference SD includes between-cell spread and is therefore conservative.
- t90 intervals are labelled as across-test statistical intervals only, not model-form uncertainty.
- Delay=0 is tracked as the physical non-negativity bound.

## REVIEW-009 closeout hardening

- Frozen derived tables and `config/calibration_model_v1.json` are now verified by exact SHA-256 and fail closed.
- The C1 offset is loaded from the verified frozen calibration JSON rather than hard-coded in the supplemental code.
- Direction-conditional uncertainty includes between-test day/run dispersion for the two-Test_ID cells and uses an effective-DOF 95% coverage factor.
- Drift is reported as **inconclusive** after serial-correlation sensitivity; OLS-only language is not used as the final interpretation.
- SUP-001 t90 and frozen command-to-DUT t90 are explicitly treated as different quantities.
- Delay-at-zero-bound counts are reported as an identifiability warning.
- CI protects frozen `docs/` content as well as data/reports/notebooks/src/config/tests/scripts and also runs on `main` after merge.

R1 remains open until generated outputs plus `SHA256SUMS.txt` are committed, the PR is merged, and immutable tag `sup001-v0.1.0` exists.
