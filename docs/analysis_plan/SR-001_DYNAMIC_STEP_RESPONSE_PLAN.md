# SR-001 — Dynamic Step Response Analysis Plan

## Milestone

- Project milestone: HV-008 — Dynamic Step Response
- Technical gate: SR-001
- Notebook: `notebooks/05_step_response.ipynb`
- Frozen dataset release: `VSM-LAB-DATA-v1.1`

## Engineering Question

> How quickly and consistently does the RH DUT respond to a commanded 30↔70 %RH transition across temperature, direction, and repetition, and how much dynamic lag does the DUT exhibit relative to the reference sensor?

This milestone characterizes step-response dynamics only.

It does not make the final HVAC suitability decision.

## Data Boundary

Use only:

```text
data/raw/vsm_lab_data_v1_1/dynamic_step_measurements.csv
```

Expected design:

- 30 Test_IDs;
- 9,030 rows;
- 301 samples/Test_ID;
- sample rate: 1 Hz;
- elapsed time: 0–300 s;
- baseline: 60 s;
- transient window: 240 s;
- temperatures: 15, 25, 35 °C;
- directions: UP, DOWN;
- repetitions: 1–5;
- UP command: 30 → 70 %RH;
- DOWN command: 70 → 30 %RH.

The public test matrix identifies primary metrics:

```text
dead_time; tau; t90; settling_time; overshoot
```

## Measurement Interpretation

`RH_Command` is the chamber command, not the physical RH actually seen by the DUT.

`RH_Reference` is the analyst-visible measured reference response and is treated as the best available measured stimulus trajectory, not exact truth.

Therefore the analysis must separate:

1. **timing from command transition**, and
2. **DUT lag relative to the measured reference response**.

This prevents chamber actuation delay from being silently attributed to the DUT.

## Step Transition Time

For each Test_ID:

```text
t_command = first Elapsed_s where RH_Command differs from the initial command
```

Expected:

```text
t_command = 60 s
```

Do not hard-code 60 s as the only detection mechanism; detect it from the data and verify it equals the test-matrix design.

## Baseline and Final Levels

For each signal separately (`RH_Reference`, `RH_DUT`):

Initial level:

```text
median of the final 20 s before t_command
```

Final level:

```text
median of the final 30 s of the record
```

These robust plateau estimates reduce sensitivity to individual noisy samples.

## Direction-Invariant Normalized Progress

For signal y:

```text
A = y_final - y_initial
progress(t) = (y(t) - y_initial) / A
```

This maps both UP and DOWN transitions to approximately:

```text
0 -> 1
```

and enables the same threshold logic for both directions.

## Frozen Timing Metrics

### Dead time

Operational definition:

```text
dead_time = t10 - t_command
```

where `t10` is the first interpolated crossing of 10% normalized progress after the command change.

The 10% criterion is used as a reproducible onset definition rather than attempting to identify motion from noise.

### Time constant proxy

```text
tau = t63.2 - t_command
```

where the threshold is:

```text
1 - exp(-1) = 0.6321205588
```

This is a first-order-equivalent timing metric. It does not assert that the chamber + sensor chain is exactly first-order.

### t90

```text
t90 = first interpolated time reaching 90% normalized progress - t_command
```

### Settling time

Use a ±2% band relative to the measured response amplitude:

```text
|y(t) - y_final| <= 0.02 * |A|
```

Settling time is the earliest post-command time after which all remaining samples stay inside the band.

If the response never remains inside the band through the end of the record:

```text
settling_time = NaN
```

Do not force a finite value.

### Overshoot

Direction-normalized overshoot:

```text
overshoot_pct =
100 * max(direction_sign * (y - y_final), 0) / |A|
```

where:

- direction_sign = +1 for an increasing step;
- direction_sign = -1 for a decreasing step.

## Reference and DUT Metrics

Compute the full metric set separately for:

- RH_Reference;
- RH_DUT.

Then compute DUT-relative-to-reference lag:

```text
lag_t10 = t10_DUT - t10_Reference
lag_tau = t63_DUT - t63_Reference
lag_t90 = t90_DUT - t90_Reference
```

Positive lag means the DUT responds later than the measured reference.

## Calibration Relationship

The frozen C1 model from HV-006 is a constant additive offset.

A constant additive correction changes neither normalized progress nor threshold-crossing times because it shifts both initial and final DUT plateaus equally.

Therefore:

- step-response timing metrics are calculated from the raw DUT response;
- no refitting or dynamic retuning of C1 occurs here;
- static calibration remains frozen.

Dynamic tracking error is addressed separately in HV-009.

## Primary Analysis Unit

Each DYNAMIC_STEP Test_ID is one dynamic experiment.

Repeated 1 Hz samples within a Test_ID describe the time response and are not treated as independent replicate experiments.

The 5 repetitions at each Temperature × Direction condition are the replicate experiments for repeatability of dynamic metrics.

## Required Summaries

Report per Test_ID:

- temperature;
- direction;
- repetition;
- command transition time;
- reference and DUT initial/final levels;
- response amplitudes;
- dead time;
- tau;
- t90;
- settling time;
- overshoot;
- lag_t10;
- lag_tau;
- lag_t90.

Aggregate by:

```text
Temperature × Direction
```

using:

- N;
- mean;
- SD;
- median;
- min;
- max.

Also report overall UP versus DOWN and temperature trends.

## Diagnostic Questions

The notebook must answer:

1. Is the DUT consistently slower than the reference?
2. Does DUT lag change with temperature?
3. Does response speed differ between UP and DOWN transitions?
4. How repeatable are t10, tau, t90, and settling time across 5 repetitions?
5. Is overshoot material or negligible?
6. Does the 300 s record allow settling to be observed for all tests?
7. Are reference dynamics themselves temperature/direction dependent?

## Planned Curated Outputs

Tables:

```text
reports/tables/hv008_step_test_metrics.csv
reports/tables/hv008_step_summary_by_condition.csv
reports/tables/hv008_step_overall_summary.csv
```

Figures:

```text
reports/figures/hv008_representative_step_response.png
reports/figures/hv008_t90_by_condition.png
```

## SR-001 Completion Criteria

| Criterion | Requirement |
|---|---|
| S01 | 30 DYNAMIC_STEP Test_IDs and 9,030 rows verified |
| S02 | 301 samples/Test_ID and 1 Hz sampling verified |
| S03 | command transition detected from data and verified at 60 s |
| S04 | reference and DUT plateau estimates audited |
| S05 | t10/dead-time, tau, t90, settling, overshoot extracted for reference and DUT |
| S06 | DUT-minus-reference lag metrics computed |
| S07 | Temperature × Direction × repetition structure preserved |
| S08 | repeatability of dynamic metrics summarized across five repetitions |
| S09 | temperature and direction effects reviewed descriptively |
| S10 | unresolved/non-settling cases explicitly retained as NaN rather than forced |
| S11 | curated tables and figures exported |
| S12 | notebook reproduces from Restart Kernel → Run All |

## Gate Outcomes

- **PASS** — the complete dynamic-step design is analyzable and response metrics are physically coherent with no material analysis limitation.
- **PASS WITH DOCUMENTED CONDITIONS** — the analysis is complete, but meaningful direction/temperature asymmetry, non-settling behavior, or other limitations must be carried forward.
- **FAIL** — the step-response data or metric definitions do not support reliable characterization.

No HVAC pass/fail specification is invented in this milestone.

## Next Stage

After SR-001 closure:

```text
HV-009 — Dynamic Tracking
```
