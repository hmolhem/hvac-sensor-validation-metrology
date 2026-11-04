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
- `outputs/sup001_t90_identification_detail.csv`
- `outputs/sup001_t90_identification_summary.csv`
- `outputs/sup001_drift_inference.csv`
- `outputs/sup001_uncertainty_coverage_bracket.csv`
- `outputs/sup001_uncertainty_primary_budget.csv`
- `outputs/sup001_validation_cell_primary_budget.csv`
- `outputs/sup001_input_hashes.csv`
- `outputs/sup001_runtime_manifest.json`
- `outputs/sup001_run_summary.txt`
- `SHA256SUMS.txt`

## Key controls

1. The frozen raw static and dynamic-step CSV hashes are verified before analysis.
2. The environment is pinned in `requirements.txt` and the workflow pins Python.
3. t90 identification uses a finer delay/tau grid than the review prototype and includes residual lag-1 diagnostics.
4. A reference-lag sensitivity uses the public reference limit `t90 <= 10 s`, corresponding to `tau_ref <= 10/ln(10) ≈ 4.343 s` under a first-order model.
5. Chamber RH uniformity `±0.30 %RH` is converted to a rectangular Type-B standard uncertainty `0.30/sqrt(3)` and included in the primary supplemental uncertainty budget.
6. Held-out cell uncertainty uses only the 9 validation cells (RH 30/50/70 × T 15/25/35). No held-out claim is made at 20 %RH.
7. All generated files are SHA-256 hashed.

## Interpretation boundary

- Frozen v1.0.0 statuses remain the historical record.
- SUP-001 may strengthen or qualify interpretation, but it does not silently change the frozen release.
- Chapters 12, 14 and 16 may cite SUP-001 only after its workflow completes successfully and its outputs/hashes are archived.
