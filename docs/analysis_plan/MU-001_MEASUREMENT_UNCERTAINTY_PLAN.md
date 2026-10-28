# MU-001 — Measurement Uncertainty Budget Plan

## Milestone

- Project milestone: HV-011 — Measurement Uncertainty Budget
- Technical gate: MU-001
- Notebook: `notebooks/08_uncertainty_budget.ipynb`
- Frozen dataset release: `VSM-LAB-DATA-v1.1`
- Public specification: `config/public/lab_spec_v1.json`

## Engineering Question

> What combined and expanded uncertainty is associated with a calibrated 60-second stable RH result at the four declared uncertainty-evaluation points, using only analyst-visible evidence and public specifications?

Declared evaluation points:

- 30 %RH, 25 °C
- 50 %RH, 25 °C
- 70 %RH, 25 °C
- 80 %RH, 35 °C (worst-case point)

## Reported Measurement Result

The primary reported result is the frozen-C1 calibrated mean over one 60-second stable hold:

```text
Y = mean(RH_DUT over 60 s) + C1
```

with:

```text
C1 = +1.2266788194 %RH
```

Dynamic measurements are outside this uncertainty model.

## Public Reference Specification

From the imported analyst-visible public lab specification:

- reference expanded calibration uncertainty: 0.40 %RH
- coverage factor: k = 2
- reference resolution: 0.01 %RH
- reference repeatability sigma max: 0.05 %RH
- reference drift limit: 0.15 %RH/year
- DUT resolution: 0.1 %RH
- DAQ DUT quantization: 0.1 %RH
- DAQ reference quantization: 0.01 %RH

Therefore the standard reference calibration uncertainty is:

```text
u_ref_cal = 0.40 / 2 = 0.20 %RH
```

## Primary Uncertainty Components

### 1. Repeatability of the 60-s mean

From HV-005:

```text
s_repeat = 0.259265 %RH
n = 60
u_repeat_mean = s_repeat / sqrt(60)
              ≈ 0.03347 %RH
```

This empirical repeatability already contains observable DUT/reference quantization and short-term sample scatter.

Therefore DUT resolution, reference resolution, DAQ quantization, and reference repeatability are **not separately added** to the primary budget.

### 2. Point-specific residual/state variability

At each declared uncertainty point, summarize the frozen-C1 Test_ID mean residuals across the available matched Run × Direction tests.

Let:

```text
s_point = SD(Test_ID-level C1 MBE)
```

Because each Test_ID mean already contains repeatability-of-mean noise, remove that contribution before combining:

```text
u_state = sqrt(max(s_point² - u_repeat_mean², 0))
```

This component represents observable between-Test_ID state/run/direction variability at the point without double-counting short-term mean noise.

### 3. Reference calibration uncertainty

```text
u_ref_cal = 0.20 %RH
```

This is independent external metrological information and is not contained in the DUT-reference residual spread.

### 4. Stability / temporal excursion

HV-010 found a maximum observed weekly Day-0-referenced center excursion of:

```text
a_stability = 0.5025 %RH
```

The effect is systematic/time-dependent and not normally distributed by evidence.

For a bounded-use primary budget, use a rectangular model:

```text
u_stability = a_stability / sqrt(3)
```

This is a conservative uncertainty representation over the tested stability interval, not a claim that the observed drift process is random.

## Residual Bias Treatment

At each evaluation point:

```text
b_point = mean(Test_ID-level C1 MBE)
```

Residual bias is reported separately.

It is **not silently absorbed into standard uncertainty** and no post-validation correction is applied.

Final compliance interpretation must consider both:

- residual bias;
- expanded uncertainty.

## Combined Standard Uncertainty

Primary model:

```text
u_c = sqrt(
    u_repeat_mean²
  + u_state²
  + u_ref_cal²
  + u_stability²
)
```

Expanded uncertainty:

```text
U = k * u_c
k = 2
```

## Explicit Non-Double-Counting Rules

The primary budget does not separately add:

- DUT resolution / DAQ DUT quantization;
- reference resolution / DAQ reference quantization;
- reference repeatability;
- HV-005 Run/Day paired shifts;
- HV-010 short-term scatter;
- reference drift limit.

Rationale:

- quantization and short-term scatter are already present in empirical repeatability;
- point-specific state variability already captures Run/Direction structure at the evaluation point;
- HV-010 short-term scatter overlaps repeatability;
- observed DUT-reference stability drift already contains whatever analyst-visible reference drift is present.

## Sensitivity Cases

### Reference drift specification

For a 90-day campaign, if the public annual reference drift limit were separately modeled as a rectangular bound:

```text
a_ref_drift_90 = 0.15 * 90 / 365
u_ref_drift_90 = a_ref_drift_90 / sqrt(3)
```

This is reported only as a sensitivity case because adding it to the primary stability component may double-count reference contribution already present in observed stability data.

### Chamber uniformity

Public chamber RH uniformity is:

```text
±0.30 %RH
```

However, the public configuration does not specify the DUT/reference spatial placement or a defensible differential-uniformity model.

Therefore chamber uniformity is **not included in the primary budget**.

A conservative sensitivity case may use:

```text
u_chamber_sens = 0.30 / sqrt(3)
```

but must be labeled a sensitivity assumption, not a measured component.

## Span / Shape Change

HV-010 observed approximately 0.151 %RH span/shape change.

This is not added independently to the primary budget because it comes from the same stability campaign as the center-drift evidence and may be dependent.

It is carried forward as a documented model-form/stability condition for the final assessment.

## Required Outputs

Tables:

```text
reports/tables/hv011_uncertainty_point_evidence.csv
reports/tables/hv011_uncertainty_budget.csv
reports/tables/hv011_uncertainty_summary.csv
reports/tables/hv011_uncertainty_sensitivity.csv
```

Figures:

```text
reports/figures/hv011_uncertainty_components.png
reports/figures/hv011_expanded_uncertainty_by_point.png
```

## MU-001 Completion Criteria

| Criterion | Requirement |
|---|---|
| U01 | public lab spec provenance verified |
| U02 | four declared evaluation points verified |
| U03 | frozen C1 loaded unchanged |
| U04 | 60-s mean measurand/reporting model frozen |
| U05 | repeatability-of-mean computed from HV-005 |
| U06 | point-specific residual/state variability computed without double counting |
| U07 | reference calibration uncertainty converted to standard uncertainty |
| U08 | stability excursion treatment documented and computed |
| U09 | residual bias reported separately |
| U10 | primary combined and expanded uncertainty computed |
| U11 | reference-drift and chamber-uniformity sensitivity cases reported separately |
| U12 | double-counting exclusions documented |
| U13 | curated tables and figures exported |
| U14 | Notebook reproduces from Restart Kernel → Run All |

## Gate Outcomes

- **PASS** — uncertainty model is traceable, reproducible, and complete for the stated 60-s stable-result measurand.
- **PASS WITH DOCUMENTED CONDITIONS** — budget is usable, but important modeling assumptions or missing public geometry/placement information constrain interpretation.
- **FAIL** — uncertainty cannot be defensibly quantified from available analyst-visible evidence.

## Next Stage

After MU-001 closure:

```text
HV-012 — Monte Carlo Uncertainty
```
