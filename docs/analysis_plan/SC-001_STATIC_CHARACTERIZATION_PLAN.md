# SC-001 Static Characterization Plan

## Milestone Identity

- Project: HVAC Sensor Validation & Metrology
- Milestone: HV-004
- Branch: `feature/hv-004-static-characterization`
- Primary notebook: `notebooks/01_static_characterization.ipynb`
- Technical gate: `SC-001`
- Primary engineering question: `EQ-02 - Static Measurement Performance`
- Secondary engineering question: `EQ-04 - Hysteresis / Direction Dependence`

## Purpose

Characterize the analyst-visible static measurement behavior of the DUT after the frozen dataset has passed DQ-001.

HV-004 changes the project question from:

`Can the measurement evidence be trusted?`

to:

`What does the qualified static evidence reveal about DUT measurement performance?`

The milestone establishes the pre-calibration static error structure without fitting a calibration model and without using independent validation observations for performance tuning.

## Primary Engineering Questions

### EQ-02 - Static Measurement Performance

How large is the DUT measurement error, and how does it vary with relative humidity and temperature?

Primary error convention:

`e = RH_DUT - RH_Reference`

Interpretation:

- `e > 0`: DUT reads high relative to the reference.
- `e < 0`: DUT reads low relative to the reference.
- `e = 0`: DUT and reference indications agree at the reported resolution.

### EQ-04 - Direction Dependence

Does the static error differ between increasing and decreasing humidity directions under matched conditions?

Direction dependence is evaluated here as part of static characterization because the static test design contains matched Up/Down conditions.

This milestone may quantify matched directional differences, but it does not make a final uncertainty-aware compliance decision.

## Input Data

Primary file:

`data/raw/vsm_lab_data_v1_1/static_measurements.csv`

Supporting design file:

`data/raw/vsm_lab_data_v1_1/test_matrix.csv`

Frozen release:

`VSM-LAB-DATA-v1.1`

## Analysis-Role Boundary

HV-004 uses only:

`Test_Family == "STATIC"`

and:

`Analysis_Role == "CHARACTERIZATION"`

The following rows are excluded from performance analysis in this milestone:

- `CALIBRATION`
- `VALIDATION`

Rationale:

- Calibration observations are reserved for later model development.
- Validation observations remain blind until the calibration model is frozen.
- Static characterization must not leak validation performance into model-development decisions.

Metadata may be used only as required for traceability and role verification.

## Measurement Model

The primary observed error is:

`e_i = RH_DUT,i - RH_Reference,i`

The reference indication is not treated as exact physical truth. The observed DUT-reference difference is a measurement result affected by both DUT behavior and the finite uncertainty of the reference measurement system.

No hidden simulator truth or latent injected error component may be used.

## Unit of Analysis

The static dataset contains multiple time samples within each Test_ID.

Two analysis levels are therefore distinguished.

### Sample level

Sample-level data may be used for:

- descriptive distributions
- within-test time-series inspection
- raw error histograms
- detection of obvious sample-level anomalies

### Test_ID level

The primary experimental unit for condition-level characterization is the Test_ID.

Each Test_ID should be summarized using quantities such as:

- mean RH_Reference
- mean RH_DUT
- mean error
- median error
- standard deviation of error
- minimum and maximum error
- sample count

Condition-level comparisons must not treat all time samples inside a Test_ID as independent experimental replicates.

This guardrail prevents pseudoreplication and keeps repeated samples within a test distinct from independent test conditions or repetitions.

## Analysis Sequence

### SC-01 - Load qualified static data

- Load the frozen static measurement file.
- Confirm the expected release path.
- Confirm `Test_Family == STATIC`.
- Filter to `Analysis_Role == CHARACTERIZATION`.
- Report row count and Test_ID count.
- Confirm that calibration and validation rows are absent from the working analysis frame.

### SC-02 - Create measurement-error variables

Create:

`Error_RH = RH_DUT - RH_Reference`

Preserve the explicit sign convention in notebook Markdown and code comments.

Where useful, also create:

`Abs_Error_RH = abs(Error_RH)`

No corrected or calibrated RH variable is created in HV-004.

### SC-03 - Establish Test_ID-level summaries

Create one summary row per Test_ID containing the design condition and descriptive measurement statistics.

Verify that design factors are constant within each Test_ID where required:

- RH setpoint
- temperature setpoint
- direction
- day
- run
- chamber state

### SC-04 - Overall pre-calibration error characterization

Report descriptive metrics for the characterization subset.

At minimum:

- count
- mean error / MBE
- median error
- MAE
- RMSE
- standard deviation
- minimum error
- maximum error
- maximum absolute error

These are descriptive pre-calibration metrics, not a final compliance decision.

### SC-05 - Error distribution

Inspect the static error distribution using appropriate plots and summary statistics.

Potential displays:

- histogram
- empirical distribution or box plot
- error-versus-reference scatter plot

The goal is to identify skew, multimodality, outliers, or condition-dependent structure before modeling.

### SC-06 - Relative-humidity dependence

Evaluate how Test_ID-level mean error changes across RH conditions.

At minimum:

- summarize error by RH setpoint
- visualize mean error versus RH
- preserve temperature and direction information in stratified views where useful

Interpret whether the error structure appears approximately constant, monotonic, curved, or otherwise RH-dependent.

Do not fit the final calibration model here.

### SC-07 - Temperature dependence

Evaluate whether static error changes with temperature at matched or stratified RH conditions.

At minimum:

- summarize Test_ID-level error by temperature
- compare temperature behavior across RH levels
- estimate a descriptive temperature effect only when the design supports the comparison

A temperature trend is an observed relationship, not automatically a causal or specification-compliance conclusion.

### SC-08 - Direction dependence / hysteresis screening

Compare Up and Down static conditions under matched RH and temperature conditions.

Preferred matched quantity:

`Direction_Difference = Mean_Error_Up - Mean_Error_Down`

Report the sign convention explicitly.

At minimum:

- construct matched Up/Down condition pairs
- quantify the directional difference
- visualize the difference across RH and temperature
- identify where the largest directional separation occurs

This analysis addresses static direction dependence. It does not replace a final uncertainty-aware hysteresis compliance decision.

### SC-09 - Day and run context

Day_ID and Run_ID may be used to visualize or stratify the static results so that obvious between-day or between-run structure is not hidden.

Formal repeatability and reproducibility variance decomposition is deferred to:

`Notebook 02 - Repeatability & Reproducibility`

HV-004 must not claim a completed R&R study.

### SC-10 - Engineering interpretation

Translate the statistical output into measurement-engineering language.

The notebook must distinguish:

- bias from random spread
- sample-level spread from between-test variation
- RH dependence from temperature dependence
- direction dependence from repeatability
- descriptive characterization from calibration
- observed DUT-reference disagreement from exact physical truth

## Required Figures / Tables

The final selection should remain concise and engineering-driven.

Recommended outputs:

1. Overall error distribution.
2. Test_ID-level mean error versus RH.
3. Error versus RH stratified by temperature.
4. Temperature-effect comparison.
5. Matched Up/Down direction-difference plot.
6. Compact table of overall static error metrics.
7. Compact table of condition-level summaries.

Derived figures belong under:

`reports/figures/`

Derived tables belong under:

`reports/tables/`

when they are promoted from notebook-only exploratory output to project artifacts.

## Scope Guardrails

HV-004 does not:

- fit or freeze the calibration model
- inspect validation performance
- tune model complexity
- perform blind validation
- complete formal R&R variance decomposition
- evaluate dynamic response
- estimate long-term drift
- build the final uncertainty budget
- make the final sensor compliance decision

Those conclusions belong to downstream milestones.

## SC-001 Completion Gate

SC-001 is a workflow-completion gate. It is not a statement that the DUT itself passes a product specification.

SC-001 passes when all of the following are true:

1. The working data are restricted to qualified STATIC / CHARACTERIZATION observations.
2. The measurement-error sign convention is implemented and documented correctly.
3. Test_ID-level summaries are created and used for condition-level interpretation.
4. Overall pre-calibration error metrics are calculated reproducibly.
5. RH dependence is evaluated.
6. Temperature dependence is evaluated.
7. Static direction dependence is evaluated with matched conditions where supported.
8. Day/run context is inspected without claiming completion of the later R&R study.
9. Calibration and validation observations remain protected from leakage.
10. No hidden simulator truth is used.
11. Engineering interpretation is written separately from numerical output.
12. The notebook completes successfully using Restart Kernel -> Run All.

Possible gate outcomes:

- `PASS`
- `PASS WITH DOCUMENTED CONDITIONS`
- `FAIL`

## Required Notebook Sections

The notebook should follow the project architecture:

1. Engineering Question
2. Why This Matters
3. Scope and Analysis Boundary
4. Input Data
5. Measurement Model and Error Convention
6. Unit of Analysis
7. Static Data Preparation
8. Overall Error Characterization
9. RH Dependence
10. Temperature Dependence
11. Direction Dependence
12. Day / Run Context
13. Results Summary
14. Engineering Interpretation
15. What I Learned
16. Key Metrology Concepts
17. Questions I Should Be Able to Answer
18. Connection to the Uncertainty Budget
19. Final Engineering Takeaway
20. Technical Discussion / Interview Notes
21. SC-001 Gate

## Metrology Learning Objectives

By the end of HV-004, the analyst should be able to explain:

- why `RH_DUT - RH_Reference` is an observed indication difference rather than exact sensor truth
- the difference between bias, absolute error, random spread, and RMSE
- why repeated time samples within one test are not automatically independent replicates
- why a Test_ID can be the correct experimental unit for condition-level comparison
- how RH and temperature dependence appear in residual/error structure
- what static hysteresis or direction dependence means physically
- why descriptive characterization must precede calibration
- why validation data must remain protected until model freeze
- why a characterization gate is different from a product PASS/FAIL decision

## Planned Deliverables

- `docs/analysis_plan/SC-001_STATIC_CHARACTERIZATION_PLAN.md`
- `notebooks/01_static_characterization.ipynb`
- selected derived figures and tables, if promoted
- `docs/handoffs/HV-004_STATIC_CHARACTERIZATION.md`
- updates to project index and project history before merge
