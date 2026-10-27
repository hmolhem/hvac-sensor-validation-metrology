# DT-001 — Dynamic Tracking Analysis Plan

## Milestone

- Project milestone: HV-009 — Dynamic Tracking
- Technical gate: DT-001
- Notebook: `notebooks/06_dynamic_tracking.ipynb`
- Frozen dataset release: `VSM-LAB-DATA-v1.1`

## Engineering Question

> How accurately does the RH DUT track time-varying humidity inputs under ramps, repeated cycles, and sinusoidal excitation after the frozen static C1 calibration, and what dynamic hysteresis, drift, gain attenuation, and phase lag remain?

HV-009 extends HV-008 from isolated step transitions to continuously varying inputs.

## Frozen Calibration Rule

The primary deployable calibration remains the frozen HV-006 C1 model:

```text
RH_Calibrated = RH_DUT + 1.2266788194 %RH
```

No dynamic data may be used to refit or retune this coefficient.

Because C1 is a constant additive offset:

- it can change dynamic MBE/MAE/RMSE;
- it cannot change response timing;
- it cannot change sinusoidal amplitude gain;
- it cannot change sinusoidal phase lag.

## Data Families

### Ramp

```text
ramp_measurements.csv
```

Public test-matrix design:

- 18 Test_IDs;
- temperatures: 15, 25, 35 °C;
- directions: UP, DOWN;
- repetitions: 1–3;
- RH excursion: 30↔70 %RH;
- nominal ramp rate: 2 %RH/min;
- duration: 1200 s.

Primary metrics from the test matrix:

```text
tracking_error; max_dynamic_error; rmse
```

### Cyclic

```text
cyclic_measurements.csv
```

Public test-matrix design:

- 3 sessions/Test_IDs;
- temperature: 25 °C;
- RH range: 30–70 %RH;
- 5 cycles/session.

Primary metrics:

```text
cycle_to_cycle_repeatability; hysteresis; dynamic_drift
```

### Sinusoidal

```text
sinusoidal_measurements.csv
```

Public test-matrix design:

- 4 Test_IDs;
- temperature: 25 °C;
- center: 50 %RH;
- amplitude: 10 %RH;
- periods: 600, 300, 120, 60 s;
- frequencies: 0.001667, 0.003333, 0.008333, 0.016667 Hz.

Primary metrics:

```text
gain; phase_lag
```

## Common Error Definitions

Raw dynamic error:

```text
Error_Raw = RH_DUT - RH_Reference
```

Frozen-C1 calibrated dynamic error:

```text
RH_DUT_C1 = RH_DUT + Frozen_C1_Offset
Error_C1  = RH_DUT_C1 - RH_Reference
```

`RH_Reference` is the analyst-visible measured reference trajectory, not exact physical truth.

## Ramp Metrics

For every ramp Test_ID, report for both raw and frozen-C1 DUT:

- MBE;
- MAE;
- RMSE;
- maximum absolute error.

Also preserve:

- temperature;
- direction;
- repetition.

Aggregate by Temperature × Direction using mean and SD across three repetitions.

Interpretation must distinguish:

- static residual bias;
- tracking error caused by response lag;
- direction dependence.

## Cyclic Metrics

Each `Session × Cycle_Index` is one cycle-level experimental unit.

For every cycle:

- raw and C1 MBE/MAE/RMSE;
- mean C1 error during UP samples;
- mean C1 error during DOWN samples;
- signed direction gap:

```text
Direction_Gap = Mean_Error_UP - Mean_Error_DOWN
```

A nonzero direction gap is treated as dynamic hysteresis/state-dependence evidence.

### Cycle-to-cycle repeatability

Within each session, summarize the SD across five cycles for:

- cycle RMSE;
- cycle MBE;
- direction gap.

### Dynamic drift

Within each session, estimate the linear slope versus Cycle_Index of:

- cycle MBE;
- cycle RMSE.

These are descriptive drift indicators, not long-term aging coefficients.

## Sinusoidal Harmonic Fit

For each sinusoidal Test_ID and each measured signal, fit the known-frequency first harmonic:

```text
y(t) = c + a sin(ωt) + b cos(ωt)
```

where:

```text
ω = 2π f
Amplitude = sqrt(a² + b²)
Phase = atan2(b, a)
```

Compute separately for `RH_Reference` and `RH_DUT`.

### Gain

```text
Gain = Amplitude_DUT / Amplitude_Reference
```

### Phase lag

```text
Phase_Lag = wrap(Phase_Reference - Phase_DUT)
```

Report:

- phase lag in degrees;
- equivalent time lag:

```text
Time_Lag_s = Phase_Lag_rad / ω
```

Positive lag means the DUT trails the measured reference.

Because C1 is additive only, gain and phase are identical before and after C1.

## Primary Analysis Units

- Ramp: one Test_ID per ramp experiment.
- Cyclic: one Session × Cycle_Index per cycle.
- Sinusoidal: one Test_ID per excitation frequency.

Time samples within each experiment describe the trajectory and are not independent replicate experiments.

## Required Diagnostics

The notebook must answer:

1. Does frozen C1 improve ramp tracking error relative to raw DUT?
2. Does ramp tracking depend more strongly on Direction or Temperature?
3. Is cyclic direction gap repeatable across cycles/sessions?
4. Is there material cycle-to-cycle drift?
5. How does sinusoidal gain change with frequency?
6. How does phase/time lag change with frequency?
7. Are the frequency-response results consistent with the slow step response observed in HV-008?

## Planned Curated Outputs

Tables:

```text
reports/tables/hv009_ramp_test_metrics.csv
reports/tables/hv009_ramp_summary_by_condition.csv
reports/tables/hv009_cyclic_cycle_metrics.csv
reports/tables/hv009_cyclic_session_summary.csv
reports/tables/hv009_sinusoidal_frequency_response.csv
```

Figures:

```text
reports/figures/hv009_ramp_tracking_example.png
reports/figures/hv009_cyclic_hysteresis_example.png
reports/figures/hv009_sinusoidal_gain.png
reports/figures/hv009_sinusoidal_phase_lag.png
```

## DT-001 Completion Criteria

| Criterion | Requirement |
|---|---|
| D01 | Ramp/cyclic/sinusoidal dataset boundaries verified |
| D02 | Frozen C1 artifact loaded unchanged |
| D03 | Ramp raw and C1 tracking metrics computed per Test_ID |
| D04 | Ramp Temperature × Direction summaries computed |
| D05 | Cyclic metrics computed per Session × Cycle |
| D06 | Cycle-to-cycle repeatability summarized |
| D07 | Direction-gap hysteresis metric reviewed |
| D08 | Cycle-index drift slopes reviewed |
| D09 | Sinusoidal harmonic fits computed at all four frequencies |
| D10 | Gain and phase/time lag reported versus frequency |
| D11 | Curated tables and figures exported |
| D12 | Notebook reproduces from Restart Kernel → Run All |

## Gate Outcomes

- **PASS** — all three dynamic-tracking families are analyzable and metrics are physically coherent with no material undocumented limitation.
- **PASS WITH DOCUMENTED CONDITIONS** — analysis is complete, but meaningful lag, hysteresis, attenuation, drift, or other limitations must be carried forward.
- **FAIL** — data or metric integrity is insufficient for reliable dynamic-tracking characterization.

No external HVAC dynamic acceptance threshold is invented here.

## Next Stage

After DT-001 closure:

```text
HV-010 — Stability & Drift
```
