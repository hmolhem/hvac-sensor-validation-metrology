# DQ-001 - Dataset Qualification Plan

## Purpose

Determine whether the frozen analyst-facing dataset is structurally complete, internally consistent, correctly mapped to the experimental design, and suitable for downstream sensor-validation analysis.

This gate does not evaluate DUT performance. It qualifies the measurement campaign before substantive analysis begins.

## Engineering Question

**EQ-01 - Data Qualification**

Is the frozen dataset structurally complete, internally consistent, correctly mapped to the experimental design, and valid for downstream analysis?

## Scope

DQ-001 evaluates:

1. Dataset inventory and file-family coverage
2. Required schema and field availability
3. Missing-value patterns in required fields
4. Duplicate-record and duplicate-key integrity
5. Test_ID traceability against `test_matrix.csv`
6. Test-family consistency between measurements and test matrix
7. Expected-versus-observed sample completeness where applicable
8. Calibration/validation role separation
9. Elapsed-time, ordering, and sampling-interval consistency
10. Experimental-state and metadata consistency
11. Known design exceptions, including uncertainty-evaluation points that do not have standalone measurement CSV rows

## Inputs

Frozen release:

`data/raw/vsm_lab_data_v1_1/`

Primary design contract:

`data/raw/vsm_lab_data_v1_1/test_matrix.csv`

Measurement families:

- `static_measurements.csv`
- `dynamic_step_measurements.csv`
- `ramp_measurements.csv`
- `cyclic_measurements.csv`
- `sinusoidal_measurements.csv`
- `stability_measurements.csv`

Release metadata:

- `dataset_manifest.json`
- `release_commitment_v1_1.json`

## Known Design Note

The test matrix contains 333 rows. The measurement files collectively represent 329 measurement-producing Test_IDs. Four rows are `UNCERTAINTY_EVALUATION` design points and do not have standalone measurement CSV rows. This is a documented design condition, not automatically a data-loss failure.

## Decision Logic

DQ-001 passes only if no unresolved defect blocks trustworthy downstream analysis.

Possible outcomes:

- `PASS` - dataset is qualified for downstream analysis.
- `PASS WITH DOCUMENTED EXCEPTIONS` - dataset is usable and all exceptions are understood and non-blocking.
- `FAIL` - one or more unresolved defects invalidate or materially compromise downstream analysis.

## Notebook

Implementation notebook:

`notebooks/00_dataset_qualification.ipynb`

The notebook should conclude with a qualification matrix and a formal DQ-001 decision.
