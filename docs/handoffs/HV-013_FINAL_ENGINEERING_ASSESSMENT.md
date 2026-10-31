# HV-013 Handoff — Final Engineering Assessment

## Milestone Identity

- Milestone: HV-013
- Branch: `feature/hv-013-final-engineering-assessment`
- Technical gate: FA-001
- Notebook: `notebooks/10_final_validation.ipynb`
- Outcome: **PASS WITH DOCUMENTED CONDITIONS**

## Final Engineering Question

> Is the sensor suitable for the intended HVAC measurement application, under the tested operating conditions, after calibration and with quantified measurement uncertainty?

## Public-Requirement Matrix

| Requirement | Public limit | Observed | Status |
|---|---:|---:|---|
| Static accuracy | ±2.0 %RH | max(|bias|+U) = 1.4094 %RH | PASS |
| Repeatability sigma | ≤0.30 %RH | max Test_ID SD = 0.319236 %RH | FAIL |
| Static hysteresis | ≤1.0 %RH | max matched = 0.9250 %RH | PASS |
| Linearity | ≤1.0 %RH | max best-fit deviation = 0.120865 %RH | PASS |
| Temperature influence | ≤0.05 %RH/°C | max slope = 0.022608 %RH/°C | PASS |
| t90 | ≤60 s | DUT mean ≈112.0 s; reference itself ≈75–81 s | NOT_DEMONSTRATED |
| Settling band | ±1.0 %RH | no public maximum settling time | INFORMATIONAL |
| Drift | ≤0.8 %RH/year | 90-day non-monotonic campaign only | NOT_DEMONSTRATED |

Status count:

- PASS = 4
- FAIL = 1
- NOT_DEMONSTRATED = 2
- INFORMATIONAL = 1

## Static Accuracy

HV-011 uncertainty-aware result:

```text
max(|residual bias| + U_k2) = 1.4094 %RH
limit = 2.0 %RH
```

Result:

```text
PASS
```

The statement applies to the four declared uncertainty-evaluation points.

## Repeatability

HV-005:

```text
pooled within-Test_ID SD = 0.2593 %RH
maximum Test_ID SD       = 0.319236 %RH
public sigma limit       = 0.300000 %RH
```

The strict maximum exceeds the limit by approximately 0.01924 %RH, or 6.4%.

Result:

```text
FAIL
```

Typical pooled repeatability remains acceptable, but strict worst observed hold does not.

## Static Hysteresis

Maximum matched UP/DOWN static separation:

```text
0.9250 %RH
```

against:

```text
1.0 %RH
```

Result:

```text
PASS
```

Margin is only 0.075 %RH.

Independent blind validation also shows a persistent direction split of approximately 0.8078 %RH.

## Linearity

Project-defined best-fit-line metric:

```text
maximum RH-level mean residual deviation = 0.120865 %RH
limit = 1.0 %RH
```

Result:

```text
PASS
```

Condition: public spec does not define endpoint vs best-fit linearity; result is method-defined.

## Temperature Influence

Worst RH-conditioned absolute slope:

```text
0.022608 %RH/°C
```

at:

```text
80 %RH, DOWN
```

against:

```text
0.050 %RH/°C
```

Result:

```text
PASS
```

## t90

Observed DUT command-to-t90:

```text
mean ≈ 112.0 s
max ≈ 122.9 s
```

The measured reference itself requires approximately 75–81 s to reach t90.

Because the stimulus/reference is slower than the public 60-s DUT limit, the test does not provide a clean direct compliance stimulus.

Result:

```text
NOT_DEMONSTRATED
```

The DUT nevertheless shows substantial additional lag relative to the measured reference.

## Drift

Public requirement:

```text
≤0.8 %RH/year
```

Available evidence:

- campaign duration: 90 days;
- non-monotonic center behavior;
- max center excursion ≈0.5025 %RH;
- Day-84 drift ≈+0.0472 %RH;
- span/shape change ≈-0.151 %RH.

The descriptive weekly linear slope would annualize mechanically to about 1.62 %RH/year, but that extrapolation is not accepted as a valid one-year drift estimate.

Result:

```text
NOT_DEMONSTRATED
```

## Dynamic Application-Risk Evidence

Key findings:

- blind static Direction split: ≈0.8078 %RH;
- ramp C1 Direction separation: ≈2.3654 %RH;
- cyclic Direction/state gap: ≈4.6920 %RH;
- fastest sinusoidal gain: ≈0.4741;
- maximum measured phase lag: ≈43.94°.

The frozen C1 calibration is a useful global static bias correction but is not a dynamic compensation model.

## Final Classification

### Full public-spec compliance

```text
NOT FULLY DEMONSTRATED
```

because:

- repeatability has one direct FAIL;
- t90 is NOT_DEMONSTRATED;
- annual drift is NOT_DEMONSTRATED.

### Steady-state/static HVAC suitability

```text
CONDITIONALLY SUITABLE
```

because uncertainty-aware static accuracy, static hysteresis, linearity, and temperature influence pass, but strict maximum repeatability slightly exceeds its public limit and long-term drift remains unresolved.

### Dynamic HVAC suitability

```text
NOT RECOMMENDED AS-IS
```

for applications requiring fast, direction-neutral RH tracking.

## Final Answer

The frozen C1-calibrated DUT is **conditionally suitable for slow or steady HVAC monitoring under the tested conditions**.

It is not appropriate to claim full public-spec compliance, and it is not recommended as-is for fast dynamic RH tracking without additional dynamic compensation, improved state awareness, or a different sensor response characteristic.

## FA-001 Gate

**FA-001 = PASS WITH DOCUMENTED CONDITIONS**

The gate confirms that the final assessment is complete, traceable, reproducible, uncertainty-aware, and technically defensible. It does not mean every DUT requirement passes.

## Curated Evidence

Notebook 10 exports:

- `reports/tables/hv013_compliance_matrix.csv`
- `reports/tables/hv013_static_metric_details.csv`
- `reports/tables/hv013_application_risk_matrix.csv`
- `reports/tables/hv013_final_decision_summary.csv`
- `reports/figures/hv013_compliance_status.png`
- `reports/figures/hv013_final_evidence_summary.png`

## Project Status After Merge

After final artifact capture and merge:

```text
HV-001 through HV-013 = complete
Core analytical project = complete
Next activity = technical reporting, communication, and future scoped extensions
```
