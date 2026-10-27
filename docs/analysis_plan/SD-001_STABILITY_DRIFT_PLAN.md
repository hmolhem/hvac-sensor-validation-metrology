# SD-001 — Stability & Drift Analysis Plan

## Milestone

- Project milestone: HV-010 — Stability & Drift
- Technical gate: SD-001
- Notebook: `notebooks/07_stability_and_drift.ipynb`
- Frozen dataset release: `VSM-LAB-DATA-v1.1`

## Engineering Question

> How does DUT error relative to the measured reference evolve with aging time, and is there evidence of center drift, span/shape drift, or degradation of short-term stability over the tested aging interval?

This milestone evaluates aging stability only. It does not make the final HVAC suitability decision.

## Frozen Calibration Rule

The frozen deployable calibration remains:

```text
RH_Calibrated = RH_DUT + 1.2266788194 %RH
```

No stability data may be used to refit or retune C1.

Because C1 is a constant additive offset:

- absolute bias changes after C1;
- within-Test_ID scatter does not change;
- drift relative to a baseline does not change;
- span change does not change.

## Data Boundary

Use only:

```text
data/raw/vsm_lab_data_v1_1/stability_measurements.csv
```

Expected design:

- 22 Test_IDs;
- 1,320 rows;
- 60 samples/Test_ID;
- temperature: 25 °C;
- direction: UP;
- chamber state: STABLE.

### Weekly center-check schedule

```text
Schedule_Type = WEEKLY_CENTER_CHECK
RH_Setpoint   = 50 %RH
Aging_Day     = 0, 7, 14, ..., 84
```

Expected:

- 13 Test_IDs;
- 780 rows.

Primary matrix metrics:

```text
bias; drift_from_baseline
```

### Monthly multi-point schedule

```text
Schedule_Type = MONTHLY_MULTI_POINT
RH_Setpoint   = 30, 50, 70 %RH
Aging_Day     = 30, 60, 90
```

Expected:

- 9 Test_IDs;
- 540 rows.

Primary matrix metrics:

```text
bias; span_change; drift_from_baseline
```

## Measurement Error

Raw error:

```text
Error_Raw = RH_DUT - RH_Reference
```

Frozen-C1 calibrated error:

```text
Error_C1 = RH_DUT + C1_Offset - RH_Reference
```

`RH_Reference` remains a measured reference, not exact truth.

## Primary Experimental Unit

Each STABILITY Test_ID is one stability checkpoint.

The 60 repeated samples within each Test_ID quantify short-term scatter at that checkpoint and are not treated as 60 independent aging experiments.

## Per-Test_ID Summary

For every stability Test_ID report:

- Schedule_Type;
- Aging_Day;
- RH_Setpoint;
- Temperature_Setpoint_C;
- Direction;
- N samples;
- Reference mean;
- DUT mean;
- raw MBE;
- C1 MBE;
- raw/C1 MAE;
- raw/C1 RMSE;
- within-Test_ID error SD.

The within-Test_ID error SD is unchanged by C1.

## Weekly Center Drift

Use the weekly Day-0 C1 MBE as the center-check baseline:

```text
Baseline_Center_Error = C1_MBE at Aging_Day 0
```

For every weekly checkpoint:

```text
Center_Drift_From_Day0 =
    C1_MBE(day) - C1_MBE(day 0)
```

Because C1 is constant, this drift is identical for raw and C1 error.

Fit a descriptive linear model:

```text
Center_Drift = beta0 + beta1 * Aging_Day
```

Report:

- slope in %RH/day;
- slope in %RH/30 days;
- R²;
- maximum absolute drift from Day 0;
- Day-84 drift from Day 0.

The linear slope is a descriptive aging trend over the tested interval, not an extrapolation model beyond the data.

## Weekly Short-Term Stability

At each weekly checkpoint, use:

```text
s_error = SD(Error_C1 within Test_ID)
```

Review whether short-term scatter changes systematically with Aging_Day.

Fit a descriptive slope:

```text
s_error = alpha0 + alpha1 * Aging_Day
```

Also report min/median/max checkpoint SD.

## Monthly Multi-Point Drift

The first monthly multi-point campaign at Day 30 is the schedule-specific baseline for pointwise drift.

For each RH point:

```text
Point_Drift(day, RH) =
    C1_MBE(day, RH) - C1_MBE(day 30, RH)
```

Report Day-60 and Day-90 point drift for:

- 30 %RH;
- 50 %RH;
- 70 %RH.

This distinguishes common-mode drift from RH-dependent shape change.

## Monthly Span Error and Span Change

Define the calibrated error span at each monthly aging day:

```text
Span_Error(day) =
    C1_MBE(day, 70 %RH) - C1_MBE(day, 30 %RH)
```

Then:

```text
Span_Change_From_Day30(day) =
    Span_Error(day) - Span_Error(day 30)
```

A constant additive calibration offset cancels from this metric.

Interpretation:

- near-zero span change: mostly common-mode shift;
- material span change: RH-dependent aging/shape change.

## Cross-Schedule Center Check

At RH = 50 %RH:

- weekly schedule provides dense Day 0–84 trend;
- monthly schedule provides independent checkpoints at Day 30/60/90.

Compare monthly 50 %RH C1 MBE against the weekly linear trend at the same aging day.

This is a consistency diagnostic, not a pooled refit.

## Required Diagnostics

The notebook must answer:

1. Is there a monotonic center-error drift over 0–84 days?
2. What is the observed Day-84 center drift from Day 0?
3. Does short-term scatter increase with aging time?
4. Are Day-60/90 monthly point drifts similar across 30/50/70 %RH?
5. Does span error change materially from Day 30 to Day 90?
6. Are monthly center checks consistent with the weekly trend?
7. Which stability quantities should carry forward into the uncertainty budget?

## Planned Curated Outputs

Tables:

```text
reports/tables/hv010_stability_test_summary.csv
reports/tables/hv010_weekly_center_drift.csv
reports/tables/hv010_weekly_trend_summary.csv
reports/tables/hv010_monthly_point_drift.csv
reports/tables/hv010_monthly_span_change.csv
```

Figures:

```text
reports/figures/hv010_weekly_center_drift.png
reports/figures/hv010_weekly_scatter_vs_age.png
reports/figures/hv010_monthly_point_drift.png
reports/figures/hv010_monthly_span_change.png
```

## SD-001 Completion Criteria

| Criterion | Requirement |
|---|---|
| S01 | 22 stability Test_IDs and 1,320 rows verified |
| S02 | 60 samples/Test_ID verified |
| S03 | weekly and monthly schedule structures verified |
| S04 | frozen C1 loaded unchanged |
| S05 | per-Test_ID bias/scatter summary computed |
| S06 | weekly Day-0 center baseline frozen |
| S07 | weekly center drift and linear trend quantified |
| S08 | weekly short-term scatter trend reviewed |
| S09 | monthly point drift relative to Day 30 computed |
| S10 | monthly span error/change quantified |
| S11 | weekly/monthly center consistency reviewed |
| S12 | curated tables and figures exported |
| S13 | Notebook reproduces from Restart Kernel → Run All |

## Gate Outcomes

- **PASS** — stability data are analyzable and no material undocumented instability is present.
- **PASS WITH DOCUMENTED CONDITIONS** — analysis is complete, but measurable drift, span change, or stability limitations must be carried forward.
- **FAIL** — data integrity or stability behavior prevents reliable characterization.

No external drift acceptance threshold is invented here.

## Uncertainty-Budget Handoff

HV-010 must explicitly identify which observed stability quantities are candidates for HV-011 uncertainty treatment.

Systematic aging drift must not automatically be converted into an independent random standard uncertainty without a justified model.

## Next Stage

After SD-001 closure:

```text
HV-011 — Measurement Uncertainty Budget
```
