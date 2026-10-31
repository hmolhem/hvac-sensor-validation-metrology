# HV-011 Handoff — Measurement Uncertainty Budget

## Milestone Identity

- Milestone: HV-011
- Branch: `feature/hv-011-measurement-uncertainty`
- Technical gate: MU-001
- Notebook: `notebooks/08_uncertainty_budget.ipynb`
- Input release: `VSM-LAB-DATA-v1.1`
- Public specification: `config/public/lab_spec_v1.json`
- Outcome: **PASS WITH DOCUMENTED CONDITIONS**

## Objective

Quantify combined and expanded uncertainty for a frozen-C1 calibrated 60-second stable RH result at the four declared public uncertainty-evaluation points, using only analyst-visible evidence and public specifications.

## Public Specification Provenance

Public laboratory specifications were imported from:

- upstream repository: `hmolhem/virtual-sensor-metrology-lab`
- source path: `config/public/lab_spec_v1.json`
- upstream main commit: `92fb4b756ba8d15082c6be2551fa8993c7ea3af7`
- source blob SHA: `63f7fe4ed728b88fabda2d8f488549706b10e661`

No private simulator truth is used.

## Reported Result Model

```text
Y = mean(RH_DUT over 60 s) + C1
```

with frozen:

```text
C1 = +1.2266788194 %RH
```

The budget applies to stable static results only, not dynamic/transient tracking.

## Primary Component Inputs

### Repeatability of 60-s mean

From HV-005:

```text
s_repeat = 0.259265 %RH
u_repeat_mean = 0.259265 / sqrt(60)
              = 0.033471 %RH
```

### Reference calibration

Public specification:

```text
U_ref = 0.40 %RH
k = 2
u_ref = 0.20 %RH
```

### Stability

HV-010 maximum observed center excursion:

```text
a_stability = 0.5025 %RH
u_stability = 0.5025 / sqrt(3)
            = 0.290119 %RH
```

### Point-specific residual/state variability

Between-Test_ID C1 MBE variability is estimated at each declared point after removing the repeatability-of-mean contribution:

```text
u_state = sqrt(max(s_point² - u_repeat_mean², 0))
```

## Point Evidence

| Point | RH | Temp | Role | Residual Bias | u_state |
|---|---:|---:|---|---:|---:|
| UNC-001 | 30 %RH | 25 °C | VALIDATION | +0.0892 %RH | 0.5027 %RH |
| UNC-002 | 50 %RH | 25 °C | VALIDATION | +0.2271 %RH | 0.4735 %RH |
| UNC-003 | 70 %RH | 25 °C | VALIDATION | +0.1720 %RH | 0.4740 %RH |
| UNC-004 | 80 %RH | 35 °C | CHARACTERIZATION | -0.1577 %RH | 0.4978 %RH |

Each point contains four Test_ID means corresponding to Direction × Run structure.

## Primary Combined Uncertainty

```text
u_c = sqrt(
    u_repeat_mean²
  + u_state²
  + u_C1²
  + u_ref_cal²
  + u_stability²
)
```

Results:

| Point | u_c | U(k=2) |
|---|---:|---:|
| UNC-001 | 0.6165 %RH | 1.2331 %RH |
| UNC-002 | 0.5929 %RH | 1.1858 %RH |
| UNC-003 | 0.5933 %RH | 1.1866 %RH |
| UNC-004 | 0.6125 %RH | 1.2250 %RH |

Overall:

```text
u_c ≈ 0.593–0.617 %RH
U(k=2) ≈ 1.186–1.233 %RH
```

## Variance Contribution

Approximate contribution ranges remain dominated by point-state residual variability. The C1 offset-estimation term is small (standard uncertainty ≈ **0.0455 %RH**) and does not change the dominant-source interpretation.

Thus the dominant uncertainty is state/history dependence, not short-term random noise.

## Residual Bias Treatment

Residual bias is kept separate from uncertainty.

Bias-plus-expanded-uncertainty envelope:

- UNC-001: approximately 1.3222 %RH
- UNC-002: approximately 1.4129 %RH
- UNC-003: approximately 1.3586 %RH
- UNC-004: approximately 1.3828 %RH

No post-validation correction is applied.

## Double-Counting Exclusions

The primary budget does not separately add:

- DUT resolution / DUT quantization;
- reference resolution / reference quantization;
- reference repeatability;
- HV-005 Run/Day paired shifts;
- HV-010 short-term scatter;
- public reference drift limit;
- HV-010 span/shape change.

These are excluded because they overlap with empirical repeatability/state/stability evidence or are dependent effects.

## Sensitivity Cases

### Reference drift

Public reference drift limit:

```text
0.15 %RH/year
```

90-day sensitivity:

```text
bound ≈ 0.0370 %RH
u ≈ 0.0214 %RH
```

This changes expanded uncertainty negligibly.

### Chamber uniformity

Public chamber RH uniformity:

```text
±0.30 %RH
```

Sensitivity-only standard uncertainty:

```text
u ≈ 0.1732 %RH
```

Including it raises U to approximately 1.235–1.281 %RH.

It remains sensitivity-only because public DUT/reference spatial placement is not defined.

## Static Accuracy Comparison

Public DUT static accuracy requirement:

```text
±2.0 %RH
```

At all four declared evaluation points:

```text
|residual bias| + U < 2.0 %RH
```

Therefore the available stable-static evidence is compatible with the public ±2 %RH accuracy requirement at these four points when k=2 uncertainty is included.

This is not the final overall product suitability decision; dynamic response, hysteresis, and drift requirements remain separate.

## MU-001 Gate

**MU-001 = PASS WITH DOCUMENTED CONDITIONS**

Documented conditions:

1. The budget is dominated by Direction/Run/state variability.
2. Stability is represented conservatively as a rectangular bound.
3. Each evaluation point has four Test_ID means.
4. UNC-004 uses CHARACTERIZATION evidence because blind VALIDATION does not include 80 %RH.
5. Chamber uniformity is sensitivity-only because public spatial placement is unspecified.
6. Residual bias remains explicit and separate from uncertainty.
7. The C1 offset-estimation uncertainty is explicitly included.
8. The budget applies only to a 60-s stable static result.

## Curated Evidence

Notebook 08 exports:

- `reports/tables/hv011_uncertainty_point_evidence.csv`
- `reports/tables/hv011_uncertainty_budget.csv`
- `reports/tables/hv011_uncertainty_summary.csv`
- `reports/tables/hv011_uncertainty_sensitivity.csv`
- `reports/figures/hv011_uncertainty_components.png`
- `reports/figures/hv011_expanded_uncertainty_by_point.png`

## Next Engineering Stage

HV-012 — Monte Carlo Uncertainty.
