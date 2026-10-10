# HV-003 - Dataset Qualification Handoff

## Milestone Identity

- Project: HVAC Sensor Validation & Metrology
- Milestone: HV-003
- Branch: `feature/hv-003-dataset-qualification`
- Pull Request: TBD
- Technical Gate: `DQ-001`
- Status: PASS WITH DOCUMENTED DESIGN CONDITIONS

## Purpose

Qualify the frozen analyst-facing `VSM-LAB-DATA-v1.1` dataset before any substantive sensor-performance conclusions are made.

DQ-001 determines whether the measurement evidence is structurally complete, internally consistent, traceable to the experimental design, correctly partitioned for calibration and validation, and suitable for downstream sensor-validation analysis.

## Primary Implementation

- Qualification plan: `docs/analysis_plan/DQ-001_DATASET_QUALIFICATION_PLAN.md`
- Notebook: `notebooks/00_dataset_qualification.ipynb`
- Frozen raw input: `data/raw/vsm_lab_data_v1_1/`

The notebook was verified with a fresh kernel using Restart Kernel -> Run All and completed without execution-order failures.

## DQ-001 Qualification Evidence

The final qualification matrix reports PASS for every blocking check:

1. Dataset inventory
2. Schema integrity
3. Row-count integrity
4. Required-field completeness
5. Duplicate integrity
6. Test-ID traceability
7. Family-aware test completeness
8. Calibration / validation role mapping
9. Analysis-role isolation
10. Basic time-sequence integrity
11. Sampling-interval consistency
12. Experimental-state consistency

Documented design conditions were also reviewed and accepted.

## Traceability and Completeness

- Test-matrix Test_IDs: 333
- Measurement-producing Test_IDs: 329
- Matrix-only design points: 4
- All four matrix-only Test_IDs are `UNCERTAINTY_EVALUATION` design points.
- No measurement Test_ID is untraceable to the test matrix.
- No measurement/test-matrix family mismatch remains.
- No Test_ID contains multiple measurement-family labels.

Completeness was evaluated using family-specific engineering criteria rather than a single generic row-count rule.

## Calibration / Validation Separation

Static observations are partitioned into:

- CHARACTERIZATION
- CALIBRATION
- VALIDATION

Calibration and validation Test_ID sets are disjoint. Validation observations remain independent for later blind validation after the calibration model is frozen.

## Time, Sequence, and Experimental-State Integrity

DQ-001 verified:

- elapsed-time ordering
- absence of duplicate elapsed times within tests
- sampling-interval consistency where a design sample rate is defined
- cyclic cycle coverage
- sinusoidal period-frequency consistency
- stability schedule and aging-day integrity
- static design-state consistency
- step, ramp, cyclic, sinusoidal, and stability experimental-state consistency

No blocking temporal or state-mapping defect remains.

## Documented Design Conditions

Three non-blocking design conditions were accepted:

### DC-001 - Uncertainty evaluation design points

Four `UNCERTAINTY_EVALUATION` Test_IDs exist in the test matrix without standalone measurement rows. These are intentional design-only evaluation points.

### DC-002 - Family-specific sample completeness

`Expected_Samples` is not explicitly populated for every test family. Completeness is therefore qualified using the appropriate family-specific design evidence.

### DC-003 - Dynamic-step chamber-state representation

Dynamic-step records use `STABLE` for the baseline and `TRANSIENT` after the step without a separate `SETTLING` label. Settling behavior will be derived later from the measured response.

## Formal Decision

`DQ-001 = PASS WITH DOCUMENTED DESIGN CONDITIONS`

All blocking qualification checks passed, all documented design conditions were accepted, and the final notebook gate reports:

`DQ-001 GATE: PASS`

The frozen dataset is released for downstream analysis.

## Scope Boundary

HV-003 does not evaluate DUT accuracy, bias, calibration coefficients, repeatability performance, hysteresis magnitude, dynamic response performance, drift magnitude, uncertainty compliance, or final specification compliance.

Those conclusions belong to downstream analysis milestones.

## Next Planned Milestone

Begin Notebook 01 - Static Characterization.

The next engineering question changes from:

`Can the measurement evidence be trusted?`

to:

`What does the qualified evidence reveal about DUT measurement performance?`
