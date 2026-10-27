# HV-008 Handoff — Dynamic Step Response

## Milestone Identity

- Milestone: HV-008
- Branch: `feature/hv-008-dynamic-step-response`
- Technical gate: SR-001
- Notebook: `notebooks/05_step_response.ipynb`
- Input release: `VSM-LAB-DATA-v1.1`
- Outcome: **PASS WITH DOCUMENTED CONDITIONS**

## Objective

Characterize the DUT response to commanded 30↔70 %RH step transitions across temperature, direction, and repetition, while separating chamber/reference dynamics from DUT-specific dynamic lag.

## Verified Step-Test Boundary

- DYNAMIC_STEP Test_IDs: **30**
- measurement rows: **9,030**
- samples/Test_ID: **301**
- sampling: **1 Hz**
- elapsed time: **0–300 s**
- command transition: **60 s**
- baseline: **60 s**
- transient: **240 s**
- temperatures: **15, 25, 35 °C**
- directions: **UP, DOWN**
- repetitions: **1–5 per Temperature × Direction**

## Frozen Metric Definitions

- dead time: t10 − command time;
- tau: t63.2 − command time;
- t90: t90 crossing − command time;
- settling time: earliest time after which response remains within ±2% of the robust final plateau;
- overshoot: direction-normalized excursion beyond the final plateau;
- DUT lag: DUT threshold time minus measured reference threshold time.

Initial and final response plateaus use robust medians of the late baseline and final record segments.

## Core Result — Direction Effect

Overall DOWN:

- Reference t90: **75.317 s**
- DUT t90: **104.182 s**
- DUT lag relative to reference: **28.865 s**
- DUT settling time: **183.133 s**
- DUT overshoot: **1.299%**

Overall UP:

- Reference t90: **81.384 s**
- DUT t90: **119.861 s**
- DUT lag relative to reference: **38.478 s**
- DUT settling time: **191.733 s**
- DUT overshoot: **1.331%**

Therefore:

- reference UP is slower than reference DOWN by approximately **6.07 s**;
- DUT UP is slower than DUT DOWN by approximately **15.68 s**;
- DUT-relative-to-reference lag differs by approximately **9.61 s** between UP and DOWN.

Interpretation: the UP/DOWN dynamic asymmetry is not explained solely by chamber/reference dynamics. A meaningful direction-dependent dynamic effect remains in the DUT response.

## Temperature Result

Averaged across direction:

| Temperature | Reference t90 | DUT t90 | DUT lag | DUT settling | DUT overshoot |
|---|---:|---:|---:|---:|---:|
| 15 °C | 78.313 s | 111.677 s | 33.365 s | 181.8 s | 1.332% |
| 25 °C | 78.164 s | 112.772 s | 34.608 s | 194.4 s | 1.353% |
| 35 °C | 78.575 s | 111.615 s | 33.041 s | 186.1 s | 1.259% |

The mean DUT t90 changes by only about **1.2 s** over 15–35 °C.

Temperature therefore has a much smaller effect on response speed than Direction within the tested range.

## Repeatability

Across the six Temperature × Direction cells, DUT t90 SD ranges approximately:

```text
0.75 to 1.69 s
```

for mean t90 values around 104–121 s.

The dynamic response time is therefore highly repeatable across the five repetitions.

## Settling and Overshoot

Mean DUT settling time under the strict ±2% criterion is approximately:

```text
174–199 s
```

after the command transition.

Mean DUT overshoot is small:

```text
approximately 1.26–1.43%
```

No material overshoot instability is evident.

## SR-001 Gate

Final scientific decision:

**SR-001 = PASS WITH DOCUMENTED CONDITIONS**

Documented conditions:

1. UP response is materially slower than DOWN response.
2. The direction difference remains after subtracting measured reference timing.
3. Strict ±2% settling requires roughly 174–199 s on average, substantially longer than t90.
4. No external HVAC response-time acceptance criterion is introduced in this milestone.
5. Dynamic tracking under ramps/cycles/sinusoids remains deferred to HV-009.

## Curated Evidence

Notebook 05 exports:

- `reports/tables/hv008_step_test_metrics.csv`
- `reports/tables/hv008_step_summary_by_condition.csv`
- `reports/tables/hv008_step_overall_summary.csv`
- `reports/figures/hv008_representative_step_response.png`
- `reports/figures/hv008_t90_by_condition.png`

## Next Engineering Stage

HV-009 — Dynamic Tracking.
