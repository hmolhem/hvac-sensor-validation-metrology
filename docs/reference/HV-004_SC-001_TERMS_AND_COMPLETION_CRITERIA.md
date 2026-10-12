# HV-004 / SC-001 Terms and Completion Criteria

## Purpose

This reference defines the terminology and completion logic used in HV-004 so that the static-characterization workflow is technically precise, reproducible, and easy to resume or review.

It complements:

- `docs/analysis_plan/SC-001_STATIC_CHARACTERIZATION_PLAN.md`
- `docs/analysis_plan/ENGINEERING_QUESTIONS.md`

## Identifier Vocabulary

### HV

`HV` is the project-specific milestone prefix for the HVAC Sensor Validation & Metrology repository.

Example:

`HV-004 = Static Characterization milestone`

HV identifiers track project work packages and are not intended as universal metrology abbreviations.

### SC

`SC` means **Static Characterization** in this project.

`SC-001` is the technical completion gate associated with HV-004.

This is a project-specific identifier, not a universal industry-standard abbreviation. In external technical communication, spell out "Static Characterization" before using `SC`.

### Gate

A **gate** is a formal checkpoint used to determine whether a stage of work is complete enough, reproducible enough, and sufficiently controlled to proceed to the next stage.

A gate asks:

`Is this analysis stage complete and trustworthy enough to close?`

A gate does not automatically ask:

`Does the DUT pass its product specification?`

### Completion

**Completion** means that the planned work for a milestone has been performed, verified, documented, and reproduced according to its predefined criteria.

For HV-004, completion means that the static-characterization workflow has been executed correctly and the required evidence exists.

Completion does **not** mean that the DUT has passed a product requirement.

### Completion criterion

A **completion criterion** is one explicit requirement that must be satisfied before the technical gate can pass.

SC-001 contains twelve completion criteria.

Prefer the term **criterion** rather than **condition** when referring to gate requirements, because "condition" has a separate experimental meaning in measurement engineering.

## Experimental-Design Vocabulary

### Factor

A **factor** is a variable whose value may define or influence a test condition.

Examples in the static campaign include:

- RH setpoint
- temperature setpoint
- direction
- day
- run

### Level

A **level** is a specific value of a factor.

Examples:

- RH setpoint = 20 %RH
- temperature setpoint = 25 degC
- direction = Up

### Experimental condition / test condition

An **experimental condition** is a defined combination of factor levels under which a measurement is acquired.

Example from the frozen test matrix:

`ST-005`

- Test family: STATIC
- Analysis role: CHARACTERIZATION
- RH setpoint: 20 %RH
- Temperature setpoint: 25 degC
- Direction: Up
- Day: 3
- Run: 1
- Chamber state: STABLE

The combination of those values defines the test context for that Test_ID.

### Operating condition

An **operating condition** is the physical or environmental state under which the DUT operates.

In this project, RH, temperature, and chamber state are direct operating-condition variables.

Day and run are better treated as test-organization / replication factors rather than physical operating conditions.

`Analysis_Role` is a data-use designation, not a physical operating condition.

### Matched condition

A **matched condition** is a comparison in which the relevant factors are held the same except for the factor intentionally being compared.

For static direction dependence, a useful matched pair is:

`ST-005: RH=20 %RH, T=25 degC, Day=3, Run=1, Direction=Up`

versus

`ST-007: RH=20 %RH, T=25 degC, Day=3, Run=1, Direction=Down`

The pair is matched on RH, temperature, day, and run while direction changes.

A matched direction difference can then be defined as:

`Direction_Difference = Mean_Error_Up - Mean_Error_Down`

Matching reduces the risk that an observed directional difference is actually caused by a different RH, temperature, day, or run.

### Documented condition

A **documented condition** is a known design feature, limitation, or non-blocking caveat that has been explicitly reviewed and accepted.

This meaning was used in DQ-001 for the outcome:

`PASS WITH DOCUMENTED DESIGN CONDITIONS`

A documented design condition is different from an experimental condition and different from a completion criterion.

## SC-001 Completion Criteria

SC-001 is an **analysis-completion gate**, not a DUT-compliance gate.

### C01 - Qualified characterization data only

**Requirement:** The working data are restricted to qualified `STATIC / CHARACTERIZATION` observations.

**Meaning:** HV-004 must analyze the intended static characterization evidence only.

**What it protects against:** mixing calibration or validation observations into the descriptive characterization stage.

**Evidence:** explicit filtering plus row/Test_ID counts and role checks.

### C02 - Error convention is explicit and correct

**Requirement:** The measurement-error convention is implemented and documented as:

`Error_RH = RH_DUT - RH_Reference`

**Meaning:** every sign, plot, metric, and interpretation must use the same definition.

**What it protects against:** reversing the physical meaning of positive and negative error.

**Evidence:** Markdown definition, code implementation, and a simple consistency check.

### C03 - Test_ID-level summaries are used for condition-level interpretation

**Requirement:** Condition-level characterization uses Test_ID-level summaries.

**Meaning:** repeated samples within one test are not treated as independent experiments.

**What it protects against:** pseudoreplication and artificially inflated evidence.

**Evidence:** one summary row per Test_ID with verified design factors and descriptive statistics.

### C04 - Overall pre-calibration metrics are reproducible

**Requirement:** Overall descriptive error metrics are calculated reproducibly.

**Minimum metrics:** MBE, median error, MAE, RMSE, standard deviation, minimum, maximum, and maximum absolute error.

**Meaning:** the baseline static performance is numerically summarized before calibration.

**What it protects against:** relying only on plots or qualitative impressions.

### C05 - RH dependence is evaluated

**Requirement:** Static error is examined across relative-humidity levels.

**Meaning:** the analysis determines whether error behavior changes across the RH operating range.

**What it protects against:** assuming one global bias adequately represents the DUT.

**Evidence:** grouped summaries and condition-level plots versus RH.

### C06 - Temperature dependence is evaluated

**Requirement:** Static error is examined across temperature levels with RH context preserved.

**Meaning:** the analysis checks whether the observed DUT-reference difference changes with temperature.

**What it protects against:** confusing temperature sensitivity with RH dependence.

**Evidence:** stratified summaries/plots and, when justified, a descriptive temperature-effect estimate.

### C07 - Static direction dependence is evaluated using matched comparisons

**Requirement:** Up and Down directions are compared under matched conditions where supported by the design.

**Meaning:** the analysis screens for static hysteresis / direction dependence while controlling the main comparison factors.

**What it protects against:** attributing differences to direction when RH, temperature, day, or run also changed.

**Evidence:** matched-pair construction and `Mean_Error_Up - Mean_Error_Down` summaries.

### C08 - Day and run context is inspected

**Requirement:** Day_ID and Run_ID structure is inspected for obvious systematic differences.

**Meaning:** the analyst checks whether static patterns appear to shift across repeated test organization.

**What it protects against:** hiding possible between-day or between-run structure inside an overall average.

**Boundary:** formal repeatability/reproducibility variance decomposition remains in Notebook 02.

### C09 - Calibration and validation leakage is prevented

**Requirement:** Calibration and validation observations remain outside the HV-004 performance-analysis frame.

**Meaning:** later model development and independent validation remain methodologically protected.

**What it protects against:** optimistic model decisions caused by data leakage.

**Evidence:** role isolation checks and zero CALIBRATION/VALIDATION rows in the characterization frame.

### C10 - Hidden simulator truth is not used

**Requirement:** All conclusions use analyst-visible measurement evidence only.

**Meaning:** the analysis must behave like a real measurement-engineering study in which the exact latent DUT truth is unknown.

**What it protects against:** circular validation against simulator-only information unavailable to a real analyst.

### C11 - Engineering interpretation is separated from numerical output

**Requirement:** The notebook contains an explicit engineering-interpretation section.

**Meaning:** calculations must be translated into measurement behavior, limitations, and implications without overstating what the evidence proves.

**What it protects against:** treating a computed number as a complete engineering conclusion.

### C12 - Clean-kernel reproducibility is demonstrated

**Requirement:** The final notebook completes successfully using `Restart Kernel -> Run All`.

**Meaning:** results do not depend on hidden notebook state, stale variables, or execution order.

**What it protects against:** non-reproducible analysis caused by interactive notebook state.

**Evidence:** successful clean execution with all gate outputs reproduced.

## Gate Outcomes

Possible SC-001 outcomes are:

- `PASS`
- `PASS WITH DOCUMENTED CONDITIONS`
- `FAIL`

### PASS

All blocking completion criteria are satisfied and no unresolved condition changes the validity of the milestone conclusion.

### PASS WITH DOCUMENTED CONDITIONS

All blocking criteria are satisfied, but one or more reviewed non-blocking limitations, assumptions, or design conditions must remain visible in the handoff and downstream interpretation.

### FAIL

At least one blocking criterion is not satisfied, or the evidence is not sufficient to support closure of the milestone.

## Completion Gate vs Performance / Compliance Decision

These concepts must remain separate.

**SC-001 completion gate:**

`Did we perform and verify the static-characterization analysis correctly?`

**Performance assessment:**

`What static measurement behavior does the DUT exhibit?`

**Compliance decision:**

`Does the measurement evidence, together with uncertainty and the applicable requirement, justify a PASS/FAIL decision for the DUT?`

The first belongs to HV-004.

The final compliance decision belongs to a later project stage after calibration, validation, and uncertainty evaluation.
