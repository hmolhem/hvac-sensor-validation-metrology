# FA-001 — Final Engineering Assessment Plan

## Milestone

- Project milestone: HV-013 — Final Engineering Assessment
- Technical gate: FA-001
- Notebook: `notebooks/10_final_validation.ipynb`
- Frozen calibration: HV-006 C1
- Primary uncertainty statement: HV-011 MU-001
- Monte Carlo validation: HV-012 MC-001

## Final Engineering Question

> Is the sensor suitable for the intended HVAC measurement application, under the tested operating conditions, after calibration and with quantified measurement uncertainty?

## Decision Vocabulary

Every public requirement receives exactly one of:

- **PASS** — direct evidence supports compliance under the frozen project metric.
- **FAIL** — direct evidence exceeds the public limit under the frozen project metric.
- **NOT_DEMONSTRATED** — available evidence cannot support a defensible direct compliance decision.
- **INFORMATIONAL** — the public value is a test/interpretation parameter rather than a standalone binary acceptance criterion.

No new acceptance threshold is invented.

## Public DUT Limits

From `config/public/lab_spec_v1.json`:

- static accuracy: ±2.0 %RH
- repeatability sigma max: 0.30 %RH
- hysteresis max: 1.0 %RH
- linearity max: 1.0 %RH
- temperature influence max: 0.05 %RH/°C
- t90 max: 60 s
- settling band: ±1.0 %RH
- drift max: 0.8 %RH/year

## Frozen Compliance Metrics

### Static accuracy

Primary uncertainty-aware metric:

```text
max over declared uncertainty-evaluation points of:
|point residual bias| + U(k=2)
```

PASS if:

```text
max(|bias| + U) <= 2.0 %RH
```

Scope is limited to the four declared uncertainty-evaluation points.

### Repeatability

Because the public field is named `repeatability_sigma_max_rh_percent`, the strict compliance metric is:

```text
max observed Test_ID within-hold error SD
```

from HV-005 STATIC/CHARACTERIZATION data.

The pooled repeatability SD is reported as secondary context.

PASS if:

```text
max Test_ID SD <= 0.30 %RH
```

### Static hysteresis

Use matched STATIC/CHARACTERIZATION Test_ID mean errors with RH, Temperature, Day, and Run matched and Direction paired.

For each pair:

```text
H = |Mean_Error_UP - Mean_Error_DOWN|
```

Strict metric:

```text
H_max = max(H)
```

PASS if:

```text
H_max <= 1.0 %RH
```

The blind-validation aggregate Direction split is reported as independent confirmation.

### Linearity

The public specification provides a limit but no formal linearity test method.

Project-defined transparent metric:

1. use STATIC/CHARACTERIZATION Test_ID mean C1 residual error;
2. average residual error at each RH setpoint across available temperatures, directions, days, and runs;
3. fit an ordinary least-squares straight line:
   ```text
   mean residual = a + b * RH
   ```
4. calculate maximum absolute deviation of the RH-level mean residuals from the fitted line.

```text
Linearity_Deviation_Max =
    max |Mean_Residual_RH - Fitted_Line_RH|
```

PASS if <= 1.0 %RH, but the result is labeled **METHOD-DEFINED** because the public specification does not define endpoint vs best-fit linearity.

### Temperature influence

Use STATIC/CHARACTERIZATION C1 Test_ID mean residuals.

For each RH × Direction combination:

1. average over available Day/Run repetitions at each temperature;
2. fit residual error versus Temperature across 15/25/35 °C;
3. use absolute slope in %RH/°C.

Strict metric:

```text
Temperature_Influence_Max =
    max over RH × Direction of |slope|
```

PASS if <= 0.05 %RH/°C.

This preserves RH interaction rather than relying only on a pooled temperature average.

### t90

Report:

- observed DUT command-to-t90;
- measured-reference command-to-t90;
- DUT-minus-reference t90 lag.

A direct public t90 compliance decision requires a stimulus/reference response sufficiently fast to isolate DUT response under the intended t90 definition.

Because the measured reference itself has command-to-t90 around 75–81 s, greater than the public DUT limit of 60 s, the current chamber step does not provide an ideal/direct t90 compliance stimulus.

Therefore frozen final status is:

```text
NOT_DEMONSTRATED
```

unless evidence contradicts this condition.

Direct observed DUT t90 values are still reported and are substantially above 60 s.

### Settling band

The public `settling_band_abs_rh_percent = 1.0` defines an absolute band but provides no maximum allowed settling time.

Therefore it is:

```text
INFORMATIONAL
```

The HV-008 ±2%-of-step settling result is retained as dynamic context but is not treated as direct compliance against the ±1 %RH band.

### Drift

The public requirement is:

```text
0.8 %RH/year
```

The available campaign is 90 days and HV-010 behavior is non-monotonic.

The descriptive weekly linear slope may be annualized only as a risk diagnostic:

```text
0.004431 %RH/day * 365
```

but not as a valid one-year extrapolation.

Therefore final drift compliance is:

```text
NOT_DEMONSTRATED
```

The maximum observed 90-day center excursion and span/shape change are reported as risk evidence.

## Application-Risk Evidence Outside Binary Public Limits

The final assessment must separately report:

- HV-009 ramp Direction bias after C1;
- HV-009 cyclic dynamic hysteresis/state gap;
- sinusoidal gain attenuation and phase lag;
- first-cycle conditioning;
- C1's inability to provide direction-neutral dynamic compensation.

These findings affect application suitability even where no public numerical limit exists.

## Overall Decision Logic

Three final conclusions are required.

### 1. Full public-spec compliance

```text
FULLY DEMONSTRATED
```

only if every binary public requirement is PASS and no mandatory requirement is NOT_DEMONSTRATED.

Otherwise:

```text
NOT FULLY DEMONSTRATED
```

### 2. Steady-state/static HVAC suitability

Assess from:

- calibrated static accuracy;
- uncertainty;
- repeatability;
- static hysteresis;
- linearity;
- temperature influence;
- stability risk.

Possible final labels:

- SUITABLE
- CONDITIONALLY SUITABLE
- NOT SUITABLE

### 3. Dynamic HVAC suitability

Assess from:

- t90 evidence quality;
- step-response lag/asymmetry;
- ramp tracking;
- cyclic response;
- sinusoidal gain/phase.

Possible final labels:

- SUITABLE
- CONDITIONALLY SUITABLE
- NOT RECOMMENDED AS-IS

## Planned Curated Outputs

Tables:

```text
reports/tables/hv013_compliance_matrix.csv
reports/tables/hv013_static_metric_details.csv
reports/tables/hv013_application_risk_matrix.csv
reports/tables/hv013_final_decision_summary.csv
```

Figures:

```text
reports/figures/hv013_compliance_status.png
reports/figures/hv013_final_evidence_summary.png
```

## FA-001 Completion Criteria

| Criterion | Requirement |
|---|---|
| F01 | public acceptance limits loaded unchanged |
| F02 | static accuracy evaluated uncertainty-aware |
| F03 | strict max repeatability evaluated |
| F04 | matched static hysteresis evaluated |
| F05 | project-defined linearity metric computed and limitation labeled |
| F06 | RH-conditioned temperature influence computed |
| F07 | t90 evidence adequacy explicitly assessed |
| F08 | settling-band status handled without inventing a time limit |
| F09 | drift evidence assessed without unjustified annual extrapolation |
| F10 | dynamic application-risk evidence integrated |
| F11 | full-spec, static-use, and dynamic-use conclusions separated |
| F12 | final answer to project engineering question stated |
| F13 | curated tables/figures exported |
| F14 | clean-kernel Restart → Run All reproduces final result |

## Gate

FA-001 is an **assessment-completion gate**, not a statement that the DUT passes every requirement.

Possible gate outcomes:

- PASS
- PASS WITH DOCUMENTED CONDITIONS
- FAIL

## Project Completion

After FA-001 closure, the analytical project is complete and ready for final report assembly.


## Post-Audit Decision-Rule Correction

The original plan proposed using the maximum observed Test_ID sample SD as the strict repeatability compliance metric. External audit showed that this rule is statistically unsuitable when 120 sample SD estimates, each based on 60 samples, are compared simultaneously: the maximum is strongly biased upward by sampling variability and multiple comparisons.

The corrected final-assessment treatment is:

- report the maximum observed Test_ID sample SD descriptively;
- use pooled repeatability SD and a one-sided 95% upper confidence limit as supporting evidence for a common-sigma interpretation;
- do not classify strict worst-condition repeatability as PASS or FAIL unless the public specification defines an appropriate condition-wise or simultaneous statistical decision rule;
- final status for the strict worst-condition requirement: NOT_DEMONSTRATED.

This correction does not alter HV-005 measurements; it corrects only the downstream compliance decision rule.
