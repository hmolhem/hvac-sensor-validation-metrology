# HV-009 Handoff — Dynamic Tracking

## Milestone Identity

- Milestone: HV-009
- Branch: `feature/hv-009-dynamic-tracking`
- Technical gate: DT-001
- Notebook: `notebooks/06_dynamic_tracking.ipynb`
- Input release: `VSM-LAB-DATA-v1.1`
- Outcome: **PASS WITH DOCUMENTED CONDITIONS**

## Objective

Evaluate continuously varying RH behavior under ramp, cyclic, and sinusoidal excitation using the frozen HV-006 C1 calibration without refitting or retuning.

## Frozen Calibration

```text
RH_Calibrated = RH_DUT + 1.2266788194 %RH
```

C1 is a static additive correction only. It is not a dynamic compensation model.

## Ramp Tracking

Mean RMSE by Direction:

```text
DOWN:
Raw RMSE = 0.3241 %RH
C1 RMSE  = 1.3175 %RH

UP:
Raw RMSE = 2.3297 %RH
C1 RMSE  = 1.1248 %RH
```

Therefore:

- UP ramp RMSE improves by approximately **51.7%** with C1;
- DOWN ramp RMSE worsens by approximately **306.5%** with C1.

Remaining mean C1 bias:

- DOWN MBE: **+1.2821 %RH**
- UP MBE: **-1.0833 %RH**

Direction separation:

```text
approximately 2.3654 %RH
```

Temperature-pooled C1 MBE is small only because positive DOWN bias and negative UP bias partially cancel.

Temperature effect is smaller than Direction effect across 15–35 °C.

## Cyclic Response

Across sessions:

- Session 1 mean Direction gap: **-4.6900 %RH**
- Session 2 mean Direction gap: **-4.6866 %RH**
- Session 3 mean Direction gap: **-4.6995 %RH**

The dynamic hysteresis/state effect is therefore large and highly repeatable.

Cycle 1 differs from later cycles.

Across cycles 2–5 only, pooled across sessions:

- mean Direction gap: approximately **-4.5569 %RH**
- SD Direction gap: approximately **0.0125 %RH**
- mean C1 RMSE: approximately **2.9851 %RH**
- SD C1 RMSE: approximately **0.0073 %RH**

Interpretation: after first-cycle conditioning, cyclic behavior becomes extremely repeatable.

The positive MBE slopes near +0.07 %RH/cycle and small negative RMSE slopes are interpreted primarily as first-cycle conditioning effects rather than continuing monotonic drift.

Long-term stability remains the subject of HV-010.

## Sinusoidal Frequency Response

| Frequency | Period | Gain | Phase lag | Equivalent time lag |
|---:|---:|---:|---:|---:|
| 0.001667 Hz | 600 s | 0.9996 | 15.86° | 26.44 s |
| 0.003333 Hz | 300 s | 0.9390 | 26.27° | 21.89 s |
| 0.008333 Hz | 120 s | 0.6974 | 43.94° | 14.65 s |
| 0.016667 Hz | 60 s | 0.4741 | 39.83° | 6.64 s |

The DUT increasingly attenuates faster RH variation.

At the highest tested frequency, the DUT reproduces only about **47%** of the measured reference amplitude.

Equivalent time lag is not constant with frequency, so the DUT is not well represented as a pure fixed delay; it behaves as a dynamic filtering system.

The measured reference amplitude also falls with frequency, so the reported DUT gain is relative to the measured reference trajectory and isolates additional DUT attenuation.

## Consistency With HV-008

HV-008 showed:

- slower UP than DOWN step response;
- substantial DUT lag relative to the reference.

HV-009 independently shows:

- direction-dependent ramp error;
- large repeatable cyclic hysteresis;
- increasing sinusoidal attenuation and phase lag.

These results are mutually consistent.

## DT-001 Gate

**DT-001 = PASS WITH DOCUMENTED CONDITIONS**

Documented conditions:

1. C1 improves UP ramp tracking but materially degrades DOWN ramp tracking.
2. Dynamic cyclic hysteresis is large, approximately -4.69 %RH.
3. First-cycle conditioning is evident.
4. DUT/reference sinusoidal gain falls from approximately 1.00 to 0.47 over the tested frequency range.
5. Substantial phase lag remains.
6. C1 is not a dynamic compensation model and remains frozen.
7. No external HVAC dynamic-performance acceptance threshold is introduced here.

## Curated Evidence

Notebook 06 exports:

- `reports/tables/hv009_ramp_test_metrics.csv`
- `reports/tables/hv009_ramp_summary_by_condition.csv`
- `reports/tables/hv009_cyclic_cycle_metrics.csv`
- `reports/tables/hv009_cyclic_session_summary.csv`
- `reports/tables/hv009_sinusoidal_frequency_response.csv`
- `reports/figures/hv009_ramp_tracking_example.png`
- `reports/figures/hv009_cyclic_hysteresis_example.png`
- `reports/figures/hv009_sinusoidal_gain.png`
- `reports/figures/hv009_sinusoidal_phase_lag.png`

## Next Engineering Stage

HV-010 — Stability & Drift.
