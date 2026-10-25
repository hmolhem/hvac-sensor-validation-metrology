# RR-001 Repeatability and Reproducibility Analysis Plan

## Milestone Identity

- Milestone: HV-005
- Technical gate: RR-001
- Notebook: `notebooks/02_repeatability_reproducibility.ipynb`
- Input release: `VSM-LAB-DATA-v1.1`
- Analysis role: `STATIC / CHARACTERIZATION`

## Engineering Question

How much of the observed static measurement variation is associated with:

1. short-term within-test repeatability;
2. run-to-run differences under matched conditions; and
3. day-to-day differences where the experimental design provides genuinely matched day coverage?

The analysis must distinguish measurement-system variation from variation caused by RH, temperature, direction, and other operating conditions.

## Why This Is Not Treated as a Classical Gage R&R by Default

The campaign does not use the classical Part × Operator × Repeat structure of a standard crossed AIAG Gage R&R study.

The available factors are:

- RH setpoint;
- temperature setpoint;
- direction;
- day;
- run; and
- repeated samples within each Test_ID.

Therefore HV-005 is framed as a **Repeatability and Reproducibility Variance-Structure Analysis** with a Gage R&R / Measurement System Analysis interpretation where the design supports it.

No unsupported equivalence to a classical operator-based Gage R&R study will be claimed.

## Experimental-Design Audit

The STATIC / CHARACTERIZATION design contains:

- 120 Test_IDs;
- 60 samples per Test_ID;
- 7 RH setpoints;
- 3 temperature setpoints;
- 2 directions;
- 3 day identifiers;
- 2 run identifiers.

### Run structure

Run 1 and Run 2 are present within every available RH × Temperature × Direction × Day condition.

Therefore run-to-run comparison can be performed using complete matched pairs:

`RH × Temperature × Direction × Day`

Expected matched run pairs: **60**.

### Day structure

Day is not fully crossed with RH.

- RH 30, 50, and 70 %RH occur on Days 1 and 2.
- RH 20, 40, 60, and 80 %RH occur on Day 3.

Therefore a three-day marginal comparison is confounded with RH composition.

Day-to-day reproducibility will be evaluated only on the genuinely matched Day 1 vs Day 2 subset:

`RH ∈ {30, 50, 70} × Temperature × Direction`

Run 1 and Run 2 will first be averaged within each day-condition before matched Day 2 − Day 1 differences are formed.

Expected matched day-condition pairs: **18**.

Day 3 is retained as valid characterization evidence but is not used to estimate an independent day effect because no same-RH Day 1/2 counterpart exists.

## Measurement Quantity

The observed RH error remains:

`Error_RH = RH_DUT - RH_Reference`

The reference indication is not treated as exact physical truth.

## Unit of Analysis

Three levels are intentionally separated.

### Sample level

Repeated 1 Hz measurements within a 60 s stable hold.

Used to quantify short-term within-test scatter.

### Test_ID level

One traceable static test execution.

Used for matched run comparisons.

### Day-condition level

The average of Run 1 and Run 2 for the same RH × Temperature × Direction × Day condition.

Used for matched Day 1 vs Day 2 comparison.

## Analysis Strategy

### RR-01 — Analysis boundary and design audit

- load frozen static data and test matrix;
- isolate STATIC / CHARACTERIZATION only;
- verify 120 Test_IDs and 60 samples/Test_ID;
- verify factor coverage;
- verify run and day matching structure;
- prevent CALIBRATION / VALIDATION leakage.

### RR-02 — Within-test repeatability

For each Test_ID, calculate:

- mean error;
- standard deviation of error;
- range;
- sample count.

Calculate the pooled within-test standard deviation:

[
s_{repeat} =
\sqrt{
\frac{
\sum_i (n_i-1)s_i^2
}{
\sum_i (n_i-1)
}
}
]

This quantity describes short-term scatter of individual readings under nominally stable conditions.

The standard deviation of a 60-sample mean is not automatically set equal to `s_repeat / sqrt(60)`; serial correlation must be considered before making an independence assumption.

### RR-03 — Run-to-run matched analysis

Match Test_ID means on:

- RH setpoint;
- temperature setpoint;
- direction;
- day.

Define:

[
\Delta e_{run}
=
\bar e_{Run2}
-
\bar e_{Run1}
]

Report:

- number of matched pairs;
- mean paired shift;
- median paired shift;
- standard deviation of paired differences;
- RMS paired difference;
- minimum / maximum;
- condition dependence of the paired shift.

A consistent non-zero paired mean is interpreted as a systematic run shift, not merely random variance.

### RR-04 — Day-to-day matched analysis

Restrict to the fully comparable Day 1 / Day 2 subset at RH 30, 50, and 70 %RH.

Average Run 1 and Run 2 within each day-condition, then match on:

- RH setpoint;
- temperature setpoint;
- direction.

Define:

[
\Delta e_{day}
=
\bar e_{Day2}
-
\bar e_{Day1}
]

Report the same paired statistics used for run analysis.

No independent Day 3 component will be estimated.

### RR-05 — R&R synthesis

Synthesize:

- within-test short-term scatter;
- run-to-run systematic shift and paired scatter;
- Day 1 / Day 2 systematic shift and paired scatter;
- design limitations;
- implications for later calibration and uncertainty analysis.

Formal variance components will be estimated only where identifiable from the actual design.

## Interpretation Rules

1. Do not treat repeated within-Test_ID samples as independent test replications.
2. Do not compare marginal day means as if Day were independent of RH.
3. Separate systematic paired shifts from random paired scatter.
4. Do not convert every observed effect directly into an uncertainty component.
5. Do not use CALIBRATION or VALIDATION observations.
6. Do not use hidden simulator truth.
7. Do not claim classical AIAG Gage R&R equivalence unless the design supports the claim.

## RR-001 Completion Criteria

| Criterion | Requirement |
|---|---|
| C01 | STATIC / CHARACTERIZATION data only |
| C02 | 120 Test_IDs and 60 samples/Test_ID verified |
| C03 | Partial-crossing structure documented and verified |
| C04 | Pooled within-test repeatability quantified |
| C05 | Complete matched Run 1 / Run 2 structure verified |
| C06 | Run paired shift and scatter quantified |
| C07 | Matched Day 1 / Day 2 subset explicitly isolated |
| C08 | Day paired shift and scatter quantified without Day 3/RH confounding |
| C09 | Calibration / validation leakage prevented |
| C10 | Systematic shift separated from random scatter in interpretation |
| C11 | No hidden simulator truth used |
| C12 | Notebook reproduces from a clean kernel |

## Gate Outcomes

- **PASS** — all completion criteria satisfied.
- **PASS WITH DOCUMENTED CONDITIONS** — analysis complete with explicit non-blocking design limitations.
- **FAIL** — one or more blocking criteria not satisfied.

The expected design limitation is the partial crossing of Day and RH. This limitation is not hidden or averaged away; it is part of the engineering interpretation.
