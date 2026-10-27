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


## HV-006 - Calibration Model Development

**Status:** PASS WITH DOCUMENTED CONDITIONS  
**Branch:** `feature/hv-006-calibration-model-development`  
**Technical Gate:** CM-001

### Objective
Develop and freeze a calibration model using STATIC / CALIBRATION evidence only while preserving the reserved VALIDATION measurements as blind independent evidence.

### Key Decisions
- Use one Test_ID summary as the primary modeling unit.
- Prohibit sample-level random splitting and use group-aware cross-validation by RH × Temperature × Direction condition.
- Compare C0-C4 as baseline/deployable candidates and retain C5 separately as a Direction/state diagnostic.
- Use leave-one-RH and leave-one-day stress tests before model freeze.
- Select the simplest deployable model supported by out-of-fold performance, residual structure, robustness, and operational availability of predictors.
- Keep VALIDATION measurements untouched through model selection and freeze.

### Verification
`CM-001 = PASS WITH DOCUMENTED CONDITIONS`.

The selected deployable model is C1, a constant additive RH correction.

Frozen C1 correction:

```text
+1.2266788194 %RH
```

Primary GroupCV RMSE is 0.5216 %RH, compared with 1.3045 %RH for the uncalibrated baseline.

C2 adds no meaningful improvement, while C3 and C4 perform worse.

C5, a Direction-augmented diagnostic model, reduces GroupCV RMSE to 0.1779 %RH and removes the dominant UP/DOWN residual split, demonstrating that Direction/hysteresis is the principal unresolved systematic structure.

Frozen C5 diagnostic parameters:

- DOWN correction: +0.8164583333 %RH
- UP increment: +0.8204409722 %RH
- UP correction: +1.6368993056 %RH

### Robustness
C1 remains stable under leave-one-RH and leave-one-day stress tests.

C5 remains strongly superior and its Direction increment remains approximately 0.82 %RH across stress-test fits.

### Documented Condition
The memoryless C1 calibration does not eliminate Direction/hysteresis. C5 is therefore retained as a state-aware diagnostic model, but it is not treated as deployable until Direction can be defined as a reliable operational field input.

### Result
HV-006 freezes the calibration model before any independent VALIDATION measurement is evaluated.

The next stage is HV-007 - Independent Blind Validation.


## HV-007 - Independent Blind Validation

**Status:** PASS WITH DOCUMENTED CONDITIONS  
**Branch:** `feature/hv-007-independent-blind-validation`  
**Technical Gate:** IV-001

### Objective
Apply the frozen C1 calibration model to reserved STATIC / VALIDATION data without refitting, retuning, or model replacement.

### Blind-Validation Results
- VALIDATION Test_IDs: 36;
- C0 RMSE: 1.1403 %RH;
- frozen C1 RMSE: 0.4566 %RH;
- C1 RMSE improvement versus C0: 59.96%;
- C0 MAE: 1.0583 %RH;
- frozen C1 MAE: 0.4046 %RH;
- C1 MAE improvement versus C0: 61.77%;
- C1 MBE: +0.1683 %RH;
- C1 maximum absolute error: 0.8275 %RH.

The blind-validation C1 RMSE closely matches the pre-validation HV-006 robustness evidence:
- GroupCV: 0.5216 %RH;
- LOO-RH: 0.4535 %RH;
- LOO-Day: 0.4505 %RH;
- Blind validation: 0.4566 %RH.

### Independent Direction Finding
After frozen C1:
- DOWN MBE: +0.5722 %RH;
- UP MBE: -0.2356 %RH;
- Direction residual separation: approximately 0.8078 %RH.

Frozen C5 diagnostic:
- RMSE: 0.2131 %RH;
- MAE: 0.1792 %RH;
- DOWN MBE: +0.1620 %RH;
- UP MBE: +0.1746 %RH.

This independently reproduces the Direction/hysteresis structure identified in HV-006.

### Governance
No validation result has been used to alter the C1 model identity or coefficient. C5 remains diagnostic only.

### Temperature Residual Review
C1 MBE decreases from +0.2353 %RH at 15 °C to +0.1069 %RH at 35 °C, while C1 MAE remains essentially stable at approximately 0.40 %RH across all three temperatures.

Interpretation: a mild temperature-related residual-center trend exists, but there is no material temperature-dependent degradation in absolute validation error.

### Result
IV-001 = PASS WITH DOCUMENTED CONDITIONS.

The next stage is HV-008 - Dynamic Step Response.


## HV-008 - Dynamic Step Response

**Status:** PASS WITH DOCUMENTED CONDITIONS — repository closure pending final curated artifact capture  
**Branch:** `feature/hv-008-dynamic-step-response`  
**Technical Gate:** SR-001

### Verified Design
- 30 DYNAMIC_STEP Test_IDs;
- 9,030 measurement rows;
- 301 samples/Test_ID at 1 Hz;
- command transition detected at 60 s;
- temperatures 15/25/35 °C;
- UP/DOWN;
- five repetitions per Temperature × Direction.

### Main Dynamic Finding
DOWN: reference t90 75.317 s, DUT t90 104.182 s, DUT lag 28.865 s.

UP: reference t90 81.384 s, DUT t90 119.861 s, DUT lag 38.478 s.

The measured reference is approximately 6.07 s slower for UP than DOWN, while the DUT is approximately 15.68 s slower. The DUT-relative-to-reference lag therefore differs by approximately 9.61 s between directions.

This confirms a DUT-specific direction-dependent dynamic asymmetry beyond chamber/reference dynamics.

### Temperature
Mean DUT t90 remains approximately 111.6–112.8 s over 15–35 °C, indicating comparatively weak temperature dependence.

### Repeatability
DUT t90 SD across Temperature × Direction cells is approximately 0.75–1.69 s.

### Settling and Overshoot
Mean DUT ±2% settling time is approximately 174–199 s. Mean overshoot is small at approximately 1.26–1.43%.

### Gate
SR-001 = PASS WITH DOCUMENTED CONDITIONS.

Final closure requires the final clean-kernel run and curated CSV/PNG capture.


## HV-009 - Dynamic Tracking

**Status:** PASS WITH DOCUMENTED CONDITIONS — final artifact capture pending  
**Branch:** `feature/hv-009-dynamic-tracking`  
**Technical Gate:** DT-001

### Ramp
C1 improves UP dynamic tracking but materially worsens DOWN tracking. Mean C1 RMSE is 1.1248 %RH UP and 1.3175 %RH DOWN. Remaining mean biases are -1.0833 %RH UP and +1.2821 %RH DOWN.

### Cyclic
Mean dynamic Direction gap is approximately -4.69 %RH across all three sessions. After cycle-1 conditioning, cycles 2–5 are extremely repeatable.

### Sinusoidal
DUT/reference gain falls from 0.9996 at 0.001667 Hz to 0.4741 at 0.016667 Hz, with substantial phase lag.

### Gate
DT-001 = PASS WITH DOCUMENTED CONDITIONS.

HV-010 will address long-term Stability & Drift.
