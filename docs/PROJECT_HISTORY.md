# Project History

## HV-001 — Repository Bootstrap

**Status:** PASS  
**Branch:** `chore/hv-001-repository-bootstrap`  
**Pull Request:** #1

### Objective
Establish the independent public repository, governance rules, traceability system, project architecture, and analyst-blind boundary before importing the frozen dataset or beginning analysis.

### Key Decisions
- Repository identity is independent of any course or university branding.
- `main` is merge-only; no direct development occurs on `main`.
- All substantive work is indexed using stable `HV-###` milestone identifiers.
- Hidden simulator truth is prohibited from this repository.
- The frozen analyst-facing dataset will be imported later as immutable raw input.
- Analysis will be engineering-question-driven, with strict calibration/validation separation.

### Result
Bootstrap review PASS. Governance, project indexing, handoff indexing, project definition, engineering questions, analysis roadmap, repository architecture, and the professional README were established without introducing hidden simulator truth.

## HV-002 - Frozen Dataset Intake

**Status:** PASS  
**Branch:** `feature/hv-002-frozen-dataset-intake`  
**Pull Request:** #2

### Objective
Import the canonical frozen analyst-facing `VSM-LAB-DATA-v1.1` release as immutable raw input while preserving byte-level provenance, release commitments, and the analyst-blind boundary.

### Key Decisions
- Use `VSM-LAB-DATA-v1.1` as the canonical downstream release.
- Preserve exact committed release bytes rather than relying on Windows working-tree copies.
- Enforce canonical LF line endings for frozen raw release artifacts.
- Treat `data/raw/vsm_lab_data_v1_1/` as immutable downstream input.
- Verify provenance from committed Git blobs using `DV-001`.
- Keep hidden simulator truth and protected private configuration out of the repository.
- Perform no sensor-performance analysis during dataset intake.

### Verification
`DV-001 = PASS (10/10)`.

The gate verified required artifacts, release identity, frozen state, manifest commitment, seven CSV payload hashes, row counts, schemas, analyst/private separation, test-matrix completeness, and canonical LF committed bytes.

### Result
The canonical `VSM-LAB-DATA-v1.1` package is now imported and independently verified as the authoritative raw dataset for downstream HVAC sensor validation and metrology analysis.


## HV-003 - Dataset Qualification

**Status:** PASS WITH DOCUMENTED DESIGN CONDITIONS  
**Branch:** `feature/hv-003-dataset-qualification`  
**Pull Request:** #3

### Objective
Qualify the frozen analyst-facing `VSM-LAB-DATA-v1.1` campaign before any substantive DUT-performance analysis by verifying structural completeness, experimental traceability, calibration/validation separation, temporal integrity, and experimental-state consistency.

### Key Decisions
- Treat dataset qualification as an engineering gate, not generic data cleaning.
- Use family-specific completeness criteria for static, step, ramp, cyclic, sinusoidal, and stability tests.
- Preserve strict calibration/validation Test_ID separation.
- Treat four `UNCERTAINTY_EVALUATION` matrix-only Test_IDs as intentional design points.
- Treat dynamic-step `STABLE` -> `TRANSIENT` state representation as non-blocking; settling behavior will be derived from response data later.
- Require a fresh-kernel Restart Kernel -> Run All verification before closing the notebook.

### Verification
`DQ-001 = PASS WITH DOCUMENTED DESIGN CONDITIONS`.

All blocking checks passed. The final notebook gate reports `DQ-001 GATE: PASS` and releases the dataset for downstream analysis.

### Result
The frozen dataset is qualified as sufficiently complete, traceable, internally consistent, and experimentally coherent for downstream sensor characterization, calibration, independent validation, dynamic-response analysis, stability assessment, and measurement-uncertainty evaluation.

The next analysis stage is Notebook 01 - Static Characterization.

## HV-004 - Static Characterization

**Status:** PASS  
**Branch:** `feature/hv-004-static-characterization`  
**Pull Request:** #5

### Objective
Establish the DUT pre-calibration static-performance baseline using only qualified `STATIC / CHARACTERIZATION` evidence while preserving calibration/validation isolation and the analyst-blind boundary.

### Key Decisions
- Define observed RH error as `RH_DUT - RH_Reference`.
- Treat Test_ID, not individual time samples, as the primary experimental unit for condition-level comparisons.
- Preserve sample-level information for within-test behavior without pseudoreplication.
- Retain statistically extreme observations unless a traceable engineering reason justifies exclusion.
- Evaluate RH and temperature dependence without assuming a constant-offset model.
- Evaluate direction using matched UP/DOWN conditions with RH, temperature, day, and run held fixed.
- Treat day/run findings as contextual evidence; defer formal variance-component decomposition to Notebook 02.
- Require Restart Kernel -> Run All before closing SC-001.

### Verification
`SC-001 = PASS`.

All twelve static-characterization completion criteria passed, including role isolation, error-definition verification, Test_ID summary integrity, RH/temperature/direction/day-run analyses, analyst-visible evidence only, documented engineering interpretation, and clean-kernel reproducibility.

### Result
The DUT exhibits a persistent negative pre-calibration error with an overall Test_ID-level MBE of approximately -1.1412 %RH. The error is not adequately described by a single constant offset.

The strongest static structure is matched direction dependence: the mean UP - DOWN difference is approximately -0.8304 %RH across 60 matched pairs. Temperature behavior also changes with RH context, while a smaller run-related shift remains for later R&R analysis.

HV-004 establishes the static pre-calibration baseline required for downstream repeatability/reproducibility analysis and calibration-model development.

The next analysis stage is Notebook 02 - Repeatability & Reproducibility.


## HV-005 - Repeatability & Reproducibility

**Status:** PASS WITH DOCUMENTED CONDITIONS  
**Branch:** `feature/hv-005-repeatability-reproducibility`  
**Technical Gate:** RR-001

### Objective
Quantify short-term repeatability and higher-level Run/Day measurement
variation using only qualified STATIC / CHARACTERIZATION evidence.

### Key Decisions
- Preserve Test_ID as the experimental unit for condition-level comparisons.
- Treat the 60 samples within each Test_ID as repeated time samples, not
  independent experimental replications.
- Use pooled within-Test_ID SD for short-term repeatability.
- Match Run 1 and Run 2 on RH, temperature, direction, and day.
- Restrict the day analysis to the genuinely matched Day 1 / Day 2 subset at
  RH 30, 50, and 70 %RH.
- Exclude Day 3 from independent day-effect estimation because Day and RH are
  partially crossed.
- Separate systematic paired shifts from paired scatter.
- Use intermediate-precision terminology for Run and Day effects rather than
  claiming full reproducibility.
- Add reusable analyst-side helpers in `src/static_analysis.py`.
- Export curated HV-005 figures and tables for reporting and poster use.

### Verification
`RR-001 = PASS WITH DOCUMENTED CONDITIONS`.

All twelve completion criteria passed after a clean-kernel Run All.

### Results
- pooled within-Test_ID repeatability SD: 0.259265 %RH;
- mean Run 2 − Run 1 shift: -0.085128 %RH;
- SD of run paired differences: 0.048747 %RH;
- 58/60 run differences negative;
- mean Day 2 − Day 1 shift: -0.090148 %RH;
- SD of day paired differences: 0.034539 %RH;
- 18/18 matched day differences negative.

### Result
The measurement system shows a stable short-term repeatability baseline
together with smaller but persistent Run- and Day-related center shifts.

The day result is explicitly limited to the matched Day 1 / Day 2 subset
because the campaign is partially crossed in Day × RH.

HV-005 provides the measurement-variation baseline required before calibration
model development and later uncertainty analysis.
