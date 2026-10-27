# Project Index

This file is the canonical milestone registry for the HVAC Sensor Validation & Metrology project.

| ID | Milestone | Branch | Verification / Gate | Handoff | PR | Status |
|---|---|---|---|---|---|---|
| HV-001 | Repository Bootstrap | `chore/hv-001-repository-bootstrap` | Bootstrap review PASS | `docs/handoffs/HV-001_REPOSITORY_BOOTSTRAP.md` | #1 | PASS |
| HV-002 | Frozen Dataset Intake | `feature/hv-002-frozen-dataset-intake` | DV-001 Dataset Intake Verification | `docs/handoffs/HV-002_FROZEN_DATASET_INTAKE.md` | #2 | PASS |
| HV-003 | Dataset Qualification | `feature/hv-003-dataset-qualification` | DQ-001 Dataset Qualification | `docs/handoffs/HV-003_DATASET_QUALIFICATION.md` | #3 | PASS WITH DOCUMENTED DESIGN CONDITIONS |
| HV-004 | Static Characterization | `feature/hv-004-static-characterization` | SC-001 Static Characterization | `docs/handoffs/HV-004_STATIC_CHARACTERIZATION.md` | #5 | PASS |
| HV-005 | Repeatability & Reproducibility | `feature/hv-005-repeatability-reproducibility` | RR-001 Repeatability & Reproducibility | `docs/handoffs/HV-005_REPEATABILITY_REPRODUCIBILITY.md` | #6 | PASS WITH DOCUMENTED CONDITIONS |

| HV-006 | Calibration Model Development | `feature/hv-006-calibration-model-development` | CM-001 Calibration Model Development | `docs/handoffs/HV-006_CALIBRATION_MODEL_DEVELOPMENT.md` | #8 | PASS WITH DOCUMENTED CONDITIONS |
| HV-007 | Independent Blind Validation | `feature/hv-007-independent-blind-validation` | IV-001 Independent Blind Validation | `docs/handoffs/HV-007_INDEPENDENT_BLIND_VALIDATION.md` | #10 | PASS WITH DOCUMENTED CONDITIONS |
| HV-008 | Dynamic Step Response | `feature/hv-008-dynamic-step-response` | SR-001 Dynamic Step Response | `docs/handoffs/HV-008_DYNAMIC_STEP_RESPONSE.md` | #11 | PASS WITH DOCUMENTED CONDITIONS |
| HV-009 | Dynamic Tracking | `feature/hv-009-dynamic-tracking` | DT-001 Dynamic Tracking | `docs/handoffs/HV-009_DYNAMIC_TRACKING.md` | #12 | PASS WITH DOCUMENTED CONDITIONS |
| HV-010 | Stability & Drift | `feature/hv-010-stability-drift` | SD-001 Stability & Drift | `docs/handoffs/HV-010_STABILITY_DRIFT.md` | TBD | PASS WITH DOCUMENTED CONDITIONS |

## Milestone-ID Policy

- IDs are stable and never reused.
- Every substantive technical milestone receives an `HV-###` identifier.
- The index is updated before a milestone is merged to `main`.
- Verification IDs such as `DV-001`, `DQ-001`, or `SC-001` are independent technical gates and are linked to the relevant milestone.
