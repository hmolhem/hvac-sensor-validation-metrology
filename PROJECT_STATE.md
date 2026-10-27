# PROJECT_STATE — HVAC Sensor Validation & Metrology

> **Purpose:** This is the operational continuity snapshot for the project.  
> A new ChatGPT conversation, collaborator, or future work session should read this file first before continuing technical work.

## 1. Repository Identity

- Repository: `hmolhem/hvac-sensor-validation-metrology`
- Default branch: `main`
- Development policy: **merge-only main**
- State snapshot date: **2026-10-27**
- Snapshot baseline commit on `main`: `b86722d975c0155b7d46eed72e98bb34a9fd2e95`
- Baseline commit message: `HV-006: Finalize post-merge project state (#9)`
- Current development branch: none; HV-009 is complete and HV-010 has not yet started

## 2. Project Mission

Working title:

**Data-Driven Validation and Calibration of an HVAC Relative-Humidity Sensor Using a Synthetic Metrology Dataset**

Final engineering question:

> **Is the sensor suitable for the intended HVAC measurement application, under the tested operating conditions, after calibration and with quantified measurement uncertainty?**

This is a **sensor-metrology and validation study first** and a Python/data-science implementation second.

## 3. Source-of-Truth Hierarchy

Use the following hierarchy when resuming work:

1. `PROJECT_STATE.md` — current operational state and next action.
2. `docs/PROJECT_INDEX.md` — canonical milestone registry and formal status.
3. `docs/handoffs/HV-###_*.md` — milestone-boundary technical state and frozen decisions.
4. `docs/PROJECT_HISTORY.md` — chronological project history and engineering rationale.
5. `docs/analysis_plan/*.md` — formal technical analysis/gate plans.
6. Notebook narrative and exported evidence — executable analytical record.
7. Git commit / PR history — implementation provenance.

If a closed milestone is summarized differently in a chat, the repository documents above take precedence.

## 4. Continuity Rule

A substantive milestone is not considered fully closed until:

```text
Develop
  ->
Verify
  ->
Technical Gate
  ->
Handoff / Index / History update
  ->
Pull Request
  ->
Merge to main
  ->
PROJECT_STATE.md updated
  ->
Milestone closed for future work
```

A new conversation should **not reconstruct prior decisions from memory** when the repository contains the authoritative record.

## 5. Frozen Governance Rules

The following rules remain active unless deliberately changed through a traceable project decision:

- No direct development on `main`.
- Every substantive technical milestone receives a stable `HV-###` identifier.
- Hidden simulator truth is prohibited from the analyst repository.
- Frozen raw release `VSM-LAB-DATA-v1.1` is immutable analytical input.
- Calibration and validation observations remain strictly separated.
- Validation data must not be used to tune or refit the calibration model after model freeze.
- Engineering conclusions must use analyst-visible measurement evidence, uncertainty, and stated requirements.
- `RH_Reference` is a reference measurement, **not exact physical truth**.

## 6. Core Measurement Conventions

Observed RH error:

```text
Error_RH = RH_DUT - RH_Reference
```

Interpretation:

- positive error: DUT reads high relative to the reference;
- negative error: DUT reads low relative to the reference.

Important metrology distinction:

```text
Systematic shift != random scatter
```

Observed non-zero Run/Day center shifts must not automatically be converted into independent random uncertainty components.

## 7. Frozen Dataset State

Canonical raw release:

```text
VSM-LAB-DATA-v1.1
```

Canonical location:

```text
data/raw/vsm_lab_data_v1_1/
```

Qualified dataset facts:

- Test-matrix Test_IDs: **333**
- Measurement-producing Test_IDs: **329**
- Measurement rows: **61,495**
- Matrix-only design points: **4**
- Untraceable measurement Test_IDs: **0**
- Calibration / validation Test_ID overlap: **0**
- Blocking DQ-001 checks failed: **0**

The four matrix-only Test_IDs are intentional `UNCERTAINTY_EVALUATION` design points.

## 8. Milestone State

| ID | Milestone | Gate | Status |
|---|---|---|---|
| HV-001 | Repository Bootstrap | Bootstrap review | **PASS** |
| HV-002 | Frozen Dataset Intake | DV-001 | **PASS** |
| HV-003 | Dataset Qualification | DQ-001 | **PASS WITH DOCUMENTED DESIGN CONDITIONS** |
| HV-004 | Static Characterization | SC-001 | **PASS** |
| HV-005 | Repeatability & Reproducibility | RR-001 | **PASS WITH DOCUMENTED CONDITIONS** |
| HV-006 | Calibration Model Development | CM-001 | **PASS WITH DOCUMENTED CONDITIONS** |

Closed HV-001 through HV-005 should not be reopened or redesigned casually. A later correction requires traceable evidence and a deliberate project decision.

## 9. Notebook State

| Notebook | Engineering Stage | Status |
|---|---|---|
| `00_dataset_qualification.ipynb` | Dataset Qualification | **COMPLETE** |
| `01_static_characterization.ipynb` | Static Measurement Performance | **COMPLETE** |
| `02_repeatability_reproducibility.ipynb` | Repeatability & Reproducibility | **COMPLETE** |
| `03_calibration_model.ipynb` | Calibration Model Development | **COMPLETE — CM-001 PASS WITH DOCUMENTED CONDITIONS** |
| `04_blind_validation.ipynb` | Independent Blind Validation | **COMPLETE — IV-001 PASS WITH DOCUMENTED CONDITIONS** |
| `05_step_response.ipynb` | Dynamic Step Response | **COMPLETE SCIENTIFICALLY — SR-001 PASS WITH DOCUMENTED CONDITIONS; ARTIFACT CAPTURE PENDING** |
| `06_dynamic_tracking.ipynb` | Ramp / Cyclic / Sinusoidal Tracking | **COMPLETE SCIENTIFICALLY — DT-001 PASS WITH DOCUMENTED CONDITIONS; ARTIFACT CAPTURE PENDING** |
| `07_stability_and_drift.ipynb` | Stability & Drift | Planned |
| `08_uncertainty_budget.ipynb` | Measurement Uncertainty | Planned |
| `09_monte_carlo.ipynb` | Monte Carlo Uncertainty Analysis | Planned |
| `10_final_validation.ipynb` | Final Engineering Assessment | Planned |

## 10. Frozen HV-003 / Dataset-Qualification Conditions

DQ-001 concluded:

```text
DQ-001 = PASS WITH DOCUMENTED DESIGN CONDITIONS
DQ-001 GATE: PASS
```

Important retained conditions:

- qualification is an engineering gate, not generic cleaning;
- calibration / validation Test_ID separation is strict;
- dynamic-step `STABLE -> TRANSIENT` representation is non-blocking and settling behavior will be derived from response data later;
- clean-kernel `Restart Kernel -> Run All` is required before notebook closure.

## 11. Frozen HV-004 / Static-Characterization Baseline

Primary experimental-unit rule:

- **Test_ID** is the primary unit for condition-level static comparisons;
- repeated time samples within a Test_ID are not treated as independent experimental replications.

Verified pre-calibration findings include:

- overall Test_ID-level MBE: approximately **-1.1412 %RH**;
- all **120** Test_ID mean errors were negative;
- matched UP − DOWN direction difference: approximately **-0.8304 %RH** across **60 matched pairs**;
- temperature behavior changes with RH context;
- error is not adequately represented by one constant offset.

These results are the pre-calibration baseline and should remain available for comparison after calibration.

## 12. Frozen HV-005 / RR-001 Design

HV-005 is complete:

```text
RR-001 = PASS WITH DOCUMENTED CONDITIONS
```

### Static R&R analysis boundary

- STATIC / CHARACTERIZATION rows: **7,200**
- Test_IDs: **120**
- samples per Test_ID: **60**
- CALIBRATION rows used: **0**
- VALIDATION rows used: **0**

### Run structure

Run is fully matched on:

```text
RH x Temperature x Direction x Day
             ->
        Run 1 / Run 2
```

Matched Run pairs: **60**

### Day structure — critical design condition

Day and RH are **partially crossed**:

```text
Day 1 & Day 2 -> RH = 30, 50, 70 %RH
Day 3         -> RH = 20, 40, 60, 80 %RH
```

Therefore:

```text
A marginal Day 1 / Day 2 / Day 3 comparison would confound Day with RH.
```

Independent day analysis is restricted to:

```text
Day 1 vs Day 2
RH = 30, 50, 70 %RH
Temperature = matched
Direction = matched
Run 1 / Run 2 = averaged first
```

Matched day-condition pairs: **18**

Day 3 remains valid characterization evidence but is not used to estimate an independent day effect.

### Terminology

The roadmap label remains **Repeatability & Reproducibility**, but the technically precise description of Run and Day effects is **intermediate precision**, not full interlaboratory reproducibility.

## 13. Frozen HV-005 Numerical Results

### Short-term repeatability

Pooled within-Test_ID SD:

```text
s_repeat = 0.259265 %RH
```

Distribution of Test_ID-level SD:

- median: **0.259309 %RH**
- 5th percentile: **0.219386 %RH**
- 95th percentile: **0.300547 %RH**
- minimum: **0.188233 %RH**
- maximum: **0.319236 %RH**

Lag-1 autocorrelation:

- mean: **-0.0210**
- median: **-0.0199**
- range: approximately **-0.306 to +0.245**

Independence-based approximation only:

```text
s_mean ~= 0.259265 / sqrt(60) = 0.033471 %RH
```

This is **not** an unconditional uncertainty result.

### Run 2 − Run 1

Matched pairs: **60**

- mean shift: **-0.085128 %RH**
- median: **-0.081583 %RH**
- SD of paired differences: **0.048747 %RH**
- RMS difference: **0.097895 %RH**
- minimum: **-0.186167 %RH**
- maximum: **+0.010167 %RH**
- mean absolute difference: **0.085778 %RH**
- negative pairs: **58**
- positive pairs: **2**

Interpretation: small but persistent systematic Run 2 negative shift plus paired scatter.

### Day 2 − Day 1

Matched pairs: **18**

- mean shift: **-0.090148 %RH**
- median: **-0.079000 %RH**
- SD of paired differences: **0.034539 %RH**
- RMS difference: **0.096194 %RH**
- minimum: **-0.148750 %RH**
- maximum: **-0.042083 %RH**
- mean absolute difference: **0.090148 %RH**
- negative pairs: **18**
- positive pairs: **0**

Mean shift by RH:

- 30 %RH: **-0.086111 %RH**
- 50 %RH: **-0.089861 %RH**
- 70 %RH: **-0.094472 %RH**

Interpretation: modest, highly consistent Day 2 negative shift within the valid matched subset.

## 14. Reusable Analysis Infrastructure

HV-005 introduced reusable analyst-side logic in:

```text
src/static_analysis.py
```

including:

- project-root discovery;
- static-characterization loading;
- RH error-column creation;
- Test_ID summarization;
- pooled within-test SD calculation;
- matched-level pairing;
- paired-difference metrics.

Notebook narrative remains the engineering record; reusable numerical logic should continue moving into `src/` when it is genuinely reusable.

## 15. Curated Evidence

HV-005 exports versionable evidence under:

```text
reports/figures/hv005_*.png
reports/tables/hv005_*.csv
```

Curated report/poster evidence may be versioned even though unrelated generated outputs remain ignored.

## 16. Current Engineering Frontier

The completed chain is:

```text
HV-001 Repository Bootstrap
  ->
HV-002 Frozen Dataset Intake
  ->
HV-003 Dataset Qualification
  ->
HV-004 Static Characterization
  ->
HV-005 Repeatability & Reproducibility
  ->
HV-006 Calibration Model Development   <-- COMPLETE / MERGED
  ->
HV-007 Independent Blind Validation     <-- COMPLETE / PENDING MERGE
  ->
HV-008 Dynamic Step Response             <-- COMPLETE
  ->
HV-009 Dynamic Tracking                  <-- COMPLETE
  ->
HV-010 Stability & Drift                 <-- NEXT
```

HV-006 and HV-007 are complete. HV-008 is complete. The next engineering frontier is HV-009 Dynamic Tracking.

## 17. HV-009 — Closed State

The frozen HV-009 analysis plan is:

```text
docs/analysis_plan/DT-001_DYNAMIC_TRACKING_PLAN.md
```

HV-009 evaluates three distinct dynamic families:

- Ramp tracking: raw and frozen-C1 MBE/MAE/RMSE/max error;
- Cyclic response: cycle-to-cycle repeatability, Direction gap, and cycle-index drift;
- Sinusoidal response: gain and phase/time lag from known-frequency harmonic fits.

Frozen calibration remains:

```text
RH_Calibrated = RH_DUT + 1.2266788194 %RH
```

No dynamic refitting or retuning is permitted.

Notebook 06 has passed DT-01 through DT-06. DT-001 = PASS WITH DOCUMENTED CONDITIONS. Ramp tracking is strongly Direction-dependent; cyclic behavior shows large repeatable hysteresis; sinusoidal response shows increasing attenuation and substantial phase lag. Final clean-kernel artifact capture is complete. Curated CSV/PNG evidence is versioned and PR #12 is prepared for merge. DT-001 is closed; the next engineering stage is HV-010 Stability & Drift.

## 18. Resume Protocol for a New Chat

A new ChatGPT conversation should be given repository access and instructed:

```text
Read PROJECT_STATE.md first.
Then read docs/PROJECT_INDEX.md.
Then read the handoff for the last completed milestone.
Continue from "Current Engineering Frontier" without redesigning closed milestones.
```

For the present state, the last completed handoff is:

```text
docs/handoffs/HV-008_DYNAMIC_STEP_RESPONSE.md
```

Then continue HV-009 Dynamic Tracking from the current checkpoint.

## 19. Update Policy for This File

Update `PROJECT_STATE.md` when any of the following changes:

- a milestone passes or fails a technical gate;
- a milestone is merged to `main`;
- a major engineering interpretation becomes frozen;
- a canonical numerical result changes;
- a data-boundary or governance rule changes;
- the current/next milestone changes;
- a new chat would otherwise need prior conversational context to continue accurately.

Keep this file concise enough to read at the start of a new work session, but complete enough that the project chain does not depend on chat history.
