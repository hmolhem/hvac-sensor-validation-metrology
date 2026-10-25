# HV-005 Handoff — Repeatability & Reproducibility

## Milestone Identity

- Milestone: HV-005
- Branch: `feature/hv-005-repeatability-reproducibility`
- Technical gate: RR-001
- Notebook: `notebooks/02_repeatability_reproducibility.ipynb`
- Input release: `VSM-LAB-DATA-v1.1`
- Outcome: **PASS WITH DOCUMENTED CONDITIONS**

## Objective

Quantify the measurement-system variation structure in the qualified
STATIC / CHARACTERIZATION dataset while separating:

- short-term within-Test_ID repeatability;
- matched Run 1 / Run 2 intermediate-precision effects; and
- matched Day 1 / Day 2 intermediate-precision effects.

The analysis intentionally avoids treating the campaign as a classical fully
crossed Part × Operator × Repeat Gage R&R study.

## Experimental-Design Finding

The Run structure is fully matched across all available static conditions:

- 60 RH × Temperature × Direction × Day conditions;
- Run 1 and Run 2 present in every condition.

The Day structure is only partially crossed with RH:

- Days 1 and 2 contain RH = 30, 50, 70 %RH;
- Day 3 contains RH = 20, 40, 60, 80 %RH.

Therefore Day 3 cannot be used to estimate an independent day effect without
confounding Day and RH.

Day analysis is restricted to the genuinely matched Day 1 / Day 2 subset.

## Verified Data Boundary

- 7,200 STATIC / CHARACTERIZATION rows;
- 120 Test_IDs;
- 60 samples per Test_ID;
- 0 CALIBRATION rows;
- 0 VALIDATION rows;
- analyst-visible evidence only;
- hidden simulator truth not used.

## RR-02 — Short-Term Repeatability

Pooled within-Test_ID standard deviation:

[
s_{repeat} = 0.259265\ \%RH
]

Distribution of Test_ID-level SD:

- median: 0.259309 %RH;
- 5th percentile: 0.219386 %RH;
- 95th percentile: 0.300547 %RH;
- minimum: 0.188233 %RH;
- maximum: 0.319236 %RH.

Lag-1 autocorrelation across Test_IDs:

- mean: -0.0210;
- median: -0.0199;
- range: approximately -0.306 to +0.245.

Under an independence assumption only:

[
s_{mean} \approx \frac{0.259265}{\sqrt{60}}
= 0.033471\ \%RH
]

This is retained as an approximation, not an unconditional uncertainty result.

## RR-03 — Run 1 / Run 2 Intermediate Precision

Matched pairs: 60.

For:

[
\Delta e_{run} = \bar e_{Run2} - \bar e_{Run1}
]

the results are:

- mean: -0.085128 %RH;
- median: -0.081583 %RH;
- SD of paired differences: 0.048747 %RH;
- RMS difference: 0.097895 %RH;
- minimum: -0.186167 %RH;
- maximum: +0.010167 %RH;
- mean absolute difference: 0.085778 %RH;
- negative pairs: 58;
- positive pairs: 2.

Interpretation: a small but persistent systematic Run 2 negative shift is
present in addition to paired scatter.

## RR-04 — Day 1 / Day 2 Intermediate Precision

Matched Day 1 / Day 2 pairs: 18.

The comparison uses only RH = 30, 50, 70 %RH, with Temperature and Direction
matched and Run 1 / Run 2 averaged within each day-condition.

For:

[
\Delta e_{day} = \bar e_{Day2} - \bar e_{Day1}
]

the results are:

- mean: -0.090148 %RH;
- median: -0.079000 %RH;
- SD of paired differences: 0.034539 %RH;
- RMS difference: 0.096194 %RH;
- minimum: -0.148750 %RH;
- maximum: -0.042083 %RH;
- mean absolute difference: 0.090148 %RH;
- negative pairs: 18;
- positive pairs: 0.

Mean Day 2 − Day 1 shift by RH:

- 30 %RH: -0.086111 %RH;
- 50 %RH: -0.089861 %RH;
- 70 %RH: -0.094472 %RH.

Interpretation: a modest, highly consistent Day 2 negative shift exists within
the matched Day 1 / Day 2 subset.

## Metrology Interpretation

HV-005 separates systematic center shifts from random scatter.

Observed Run and Day effects are not automatically converted into independent
uncertainty components because both contain non-zero systematic shifts.

The roadmap label remains Repeatability & Reproducibility, but Run and Day are
described more precisely as **intermediate precision** factors. Full
interlaboratory reproducibility is not estimated.

## RR-001 Gate

C01 through C12 all passed after a clean-kernel Run All.

Final decision:

**RR-001 = PASS WITH DOCUMENTED CONDITIONS**

Documented condition:

> Day × RH is partially crossed; therefore the independent day comparison is
> restricted to the matched Day 1 / Day 2 subset at RH = 30, 50, 70 %RH.

## Reusable Analysis Infrastructure

HV-005 introduced analyst-side reusable logic in:

`src/static_analysis.py`

including:

- project-root discovery;
- static-characterization loading;
- RH error-column creation;
- Test_ID summarization;
- pooled within-test SD calculation;
- matched-level pairing;
- paired-difference metrics.

Notebook narrative remains the engineering record; reusable numerical logic is
progressively moved into `src/`.

## Exported Evidence

Notebook 02 writes curated poster/report evidence to:

- `reports/figures/hv005_*.png`
- `reports/tables/hv005_*.csv`

The repository ignore policy was updated so these curated HV-005 artifacts can
be versioned while unrelated generated outputs remain ignored.

## Next Engineering Stage

HV-006 — Calibration Model Development.

Calibration model selection must use CALIBRATION data only and preserve the
VALIDATION set as blind independent evidence.
