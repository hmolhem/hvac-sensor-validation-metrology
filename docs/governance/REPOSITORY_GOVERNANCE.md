# Repository Governance

## Project Identity

Repository: `hmolhem/hvac-sensor-validation-metrology`

This repository is an independent engineering case study focused on HVAC relative-humidity sensor characterization, calibration, validation, dynamic-response analysis, stability, measurement uncertainty, and compliance assessment.

## G-01 — Main Branch Is Merge-Only

No development work is performed directly on `main`.

Prohibited on `main`:
- direct file creation
- direct edits
- direct deletions
- direct development commits

Required workflow:

`main` → task-specific branch → implementation and verification → handoff and index update → pull request → squash merge → `main`

## G-02 — Indexed and Traceable Work

Every substantive project milestone is assigned a stable identifier:

`HV-001`, `HV-002`, `HV-003`, ...

Each milestone must record, when applicable:
- milestone ID
- objective
- task branch
- verification gate or evidence
- handoff document
- project-history entry
- pull request
- final status

## G-03 — Analyst-Blind Boundary

This repository may contain only analyst-facing artifacts required for the downstream validation study.

The following must never be introduced:
- hidden simulator truth
- private DUT personality/configuration
- latent truth variables
- hidden injected error components
- hidden true bias, drift, time constants, or other simulator-only parameters
- private source artifacts that disclose the simulator truth model

## G-04 — Frozen Raw Data

The imported release `VSM-LAB-DATA-v1` is treated as immutable analytical input.

Files under `data/raw/vsm_lab_data_v1/` must not be overwritten by notebooks or analysis scripts. Derived artifacts belong under `data/processed/`, `reports/tables/`, or `reports/figures/`.

## G-05 — Engineering-Question-Driven Analysis

Every notebook must answer a defined engineering question. Python is the analytical tool; the project subject is sensor metrology and validation.

## G-06 — Calibration/Validation Separation

Calibration observations and validation observations must remain strictly separated. Validation observations are not used to tune or refit the calibration model after model freeze.

## G-07 — Evidence-Based Conclusions

Engineering decisions must be based on measurement evidence, uncertainty, and stated requirements. A specification is not equivalent to observed performance, and the reference instrument is not treated as exact physical truth.
