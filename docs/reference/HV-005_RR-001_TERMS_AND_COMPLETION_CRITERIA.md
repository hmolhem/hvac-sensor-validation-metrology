# HV-005 / RR-001 Terms and Completion Criteria

## Purpose

This reference defines the terminology and interpretation rules used in
HV-005 Repeatability and Reproducibility.

## Core Terms

### Repeatability

Short-term variation of repeated measurement indications obtained under the
same nominal test execution and operating condition.

In this project, repeatability is screened using the 60 repeated 1 Hz samples
within each static CHARACTERIZATION Test_ID.

### Reproducibility

Variation associated with changing a higher-level replication condition while
holding the intended operating condition matched.

HV-005 evaluates two reproducibility views:

- Run 1 versus Run 2 under matched RH, temperature, direction, and day.
- Day 1 versus Day 2 where RH, temperature, and direction are genuinely
  matched.

### Experimental Unit

For condition-level comparison, the Test_ID is the primary experimental unit.

Repeated samples within one Test_ID are not independent experimental
replications.

### Pseudoreplication

Treating repeated observations from the same test execution as if they were
independent test replications.

HV-005 avoids pseudoreplication by separating sample-level repeatability from
Test_ID-level run/day comparisons.

### Matched Comparison

A comparison in which all relevant experimental factors are held fixed except
the factor being evaluated.

Run matching holds constant:

- RH setpoint;
- temperature setpoint;
- direction;
- day.

Day matching holds constant:

- RH setpoint;
- temperature setpoint;
- direction.

Run 1 and Run 2 are averaged before Day 1 / Day 2 comparison.

### Partially Crossed Design

A design in which not every level of one factor appears with every level of
another factor.

In this campaign, Day and RH are partially crossed:

- Days 1 and 2 contain RH 30, 50, 70 %RH.
- Day 3 contains RH 20, 40, 60, 80 %RH.

Therefore a marginal three-day comparison cannot isolate Day from RH.

### Confounding

A situation in which the effect of one factor cannot be distinguished from
another because the experimental design does not provide the necessary
overlap.

Day 3 is confounded with its RH composition for an independent day-effect
estimate.

### Systematic Shift

A persistent non-zero mean paired difference.

Examples:

`Run 2 - Run 1`

or

`Day 2 - Day 1`

A systematic shift describes change in center and must not be confused with
random scatter.

### Paired Scatter

The standard deviation of matched differences across conditions.

This describes how consistently the paired effect appears across the matched
experimental space.

### Pooled Within-Test Standard Deviation

The pooled short-term standard deviation across Test_IDs:

[
s_p =
\sqrt{
\frac{
\sum_i (n_i-1)s_i^2
}{
\sum_i (n_i-1)
}
}
]

This preserves the within-test degrees-of-freedom weighting.

### Serial Correlation

Correlation between sequential measurements in time.

Because the 60 readings within each Test_ID are sequential 1 Hz samples,
`s / sqrt(n)` is not automatically valid for the standard deviation of the
mean. Lag-1 autocorrelation is inspected before an independence assumption is
used.

### Variance Component

A portion of total variability attributed to an identifiable random source in
a statistical model.

HV-005 does not force a variance-component estimate where the design does not
support clean identification.

### Gage R&R / Measurement System Analysis

Industry terminology for separating measurement-system variation into
repeatability and reproducibility components.

HV-005 uses this framing where appropriate but does not claim equivalence to
a classical fully crossed Part × Operator × Repeat AIAG study.

## Interpretation Rules

- Separate center shift from scatter.
- Preserve matched conditions.
- Do not infer a three-day effect from marginal day means.
- Do not treat Test_ID samples as independent replications.
- Do not use calibration or validation observations.
- Do not use hidden simulator truth.
- Do not convert observed effects directly into uncertainty components without
  defining their treatment in the measurement model.

## RR-001 Completion Criteria

| Criterion | Requirement |
|---|---|
| C01 | STATIC / CHARACTERIZATION data only |
| C02 | 120 Test_IDs and 60 samples/Test_ID verified |
| C03 | Partial Day × RH crossing documented |
| C04 | Pooled within-test repeatability quantified |
| C05 | 60 complete matched Run 1 / Run 2 pairs verified |
| C06 | Run shift and paired scatter quantified |
| C07 | Day 1 / Day 2 common-RH subset isolated |
| C08 | 18 complete matched day-condition pairs verified |
| C09 | Day 3 excluded from independent day-effect estimate |
| C10 | Systematic shifts separated from random scatter |
| C11 | Analyst-visible evidence only |
| C12 | Clean-kernel reproducibility verified |
