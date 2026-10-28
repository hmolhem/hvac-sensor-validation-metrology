# MC-001 — Monte Carlo Uncertainty Validation Plan

## Milestone

- Project milestone: HV-012 — Monte Carlo Uncertainty
- Technical gate: MC-001
- Notebook: `notebooks/09_monte_carlo.ipynb`
- Analytical baseline: HV-011 / MU-001
- Frozen dataset release: `VSM-LAB-DATA-v1.1`

## Engineering Question

> Does Monte Carlo propagation reproduce the HV-011 analytical uncertainty budget, and how does the output distribution change when point-specific empirical Direction/Run state structure is preserved rather than approximated as Gaussian?

## Scope

This milestone validates and stress-tests the HV-011 static uncertainty model.

It does **not**:

- refit C1;
- alter the HV-011 uncertainty budget;
- use hidden simulator truth;
- model dynamic/transient tracking error;
- make the final product-suitability decision.

## Reproducibility

Frozen Monte Carlo controls:

```text
master RNG seed = 7140
trials per point per model = 250,000
```

All reported quantiles and coverage values must reproduce from a clean-kernel Run All.

## Input Points

Use the four HV-011 declared uncertainty-evaluation points:

- UNC-001: 30 %RH / 25 °C
- UNC-002: 50 %RH / 25 °C
- UNC-003: 70 %RH / 25 °C
- UNC-004: 80 %RH / 35 °C

Use the frozen HV-011 tables:

- `reports/tables/hv011_uncertainty_summary.csv`
- `reports/tables/hv011_uncertainty_budget.csv`
- `reports/tables/hv011_uncertainty_point_evidence.csv`

## Common Components

For each point, propagate independent zero-centered components:

### Repeatability of the 60-s mean

```text
R ~ Normal(0, u_repeat_mean)
```

### Reference calibration

```text
C_ref ~ Normal(0, u_ref_cal)
```

The public reference specification gives expanded uncertainty with k=2 but does not publish a full probability distribution. A zero-centered normal distribution with standard deviation `U/k` is therefore an explicit Monte Carlo modeling assumption, not hidden truth.

### Stability

HV-011 treats the observed stability excursion as a bounded rectangular effect:

```text
D ~ Uniform(-a_stability, +a_stability)
```

with:

```text
a_stability = 0.5025 %RH
```

This reproduces:

```text
u_stability = a_stability / sqrt(3)
```

## Model A — Analytical-Equivalent Monte Carlo

For point-specific state variability:

```text
S_A ~ Normal(0, u_state)
```

Total zero-centered uncertainty error:

```text
E_A = R + S_A + C_ref + D
```

This model is designed to validate the root-sum-of-squares analytical standard uncertainty:

```text
u_c = sqrt(
    u_repeat_mean²
  + u_state²
  + u_ref_cal²
  + u_stability²
)
```

## Model B — Empirical-State Monte Carlo

The four point-specific Test_ID C1 MBE values contain observable Direction × Run structure.

For each point:

1. subtract the point mean residual bias;
2. compute centered empirical deviations;
3. rescale those four deviations so their equal-probability population standard deviation equals the frozen HV-011 `u_state`;
4. bootstrap one of the four rescaled centered state values with equal probability.

Then:

```text
S_B ~ EmpiricalBootstrap(rescaled centered Test_ID states)
```

and:

```text
E_B = R + S_B + C_ref + D
```

This preserves the observed finite Direction/Run state structure while matching the same state variance used in HV-011.

Important limitation:

> Four Test_ID states per point are insufficient to infer a general population PDF. Model B is a structure-preserving sensitivity model, not a claim that the empirical four-point distribution is the true field distribution.

## Residual Bias

Residual bias remains separate, consistent with HV-011.

For descriptive total-error distributions only:

```text
Total_Error_A = Point_Residual_Bias + E_A
Total_Error_B = Point_Residual_Bias + E_B
```

No post-validation correction is introduced.

## Monte Carlo Outputs

For each Point × Model report:

- Monte Carlo mean;
- Monte Carlo standard deviation;
- relative difference from analytical `u_c`;
- 2.5th percentile;
- median;
- 97.5th percentile;
- central 95% interval width;
- lower and upper 95% half-widths;
- coverage probability inside analytical interval `[-2u_c, +2u_c]`;
- skewness;
- excess kurtosis.

## Validation Criteria

### Model A

For every point:

```text
|MC_SD - u_c| / u_c <= 1%
```

and:

```text
|MC_Mean| <= 0.01 %RH
```

The central 95% interval need not equal exactly ±2u_c because one component is rectangular, but should be close.

### Model B

For every point:

```text
|MC_SD - u_c| / u_c <= 1.5%
```

This verifies that empirical-state rescaling preserves the HV-011 variance budget.

No requirement is imposed that Model B's 95% interval equal ±2u_c because the state PDF is deliberately non-Gaussian/discrete.

## Interpretation Questions

1. Does Model A reproduce the analytical combined standard uncertainty?
2. How close is its central 95% interval to the HV-011 k=2 interval?
3. Does empirical-state propagation materially change standard deviation?
4. Does empirical-state propagation materially change 95% coverage shape?
5. Is the HV-011 k=2 interval conservative or non-conservative under Model B?
6. How much does the observed Direction/Run bimodality matter beyond variance alone?
7. What limitations must carry into the final assessment?

## Planned Curated Outputs

Tables:

```text
reports/tables/hv012_mc_summary.csv
reports/tables/hv012_mc_state_support.csv
reports/tables/hv012_mc_model_comparison.csv
```

Figures:

```text
reports/figures/hv012_mc_interval_comparison.png
reports/figures/hv012_mc_representative_distribution.png
```

## MC-001 Completion Criteria

| Criterion | Requirement |
|---|---|
| M01 | HV-011 inputs verified |
| M02 | RNG seed and trial count frozen |
| M03 | Model A distributions documented |
| M04 | Model B empirical-state support constructed and variance-matched |
| M05 | Model A executed for all four points |
| M06 | Model B executed for all four points |
| M07 | MC means/SD/quantiles/coverage computed |
| M08 | Model A SD agrees with analytical u_c within 1% |
| M09 | Model B SD agrees with analytical u_c within 1.5% |
| M10 | analytical k=2 interval compared with MC central 95% intervals |
| M11 | distribution-shape diagnostics reported |
| M12 | curated tables/figures exported |
| M13 | Notebook reproduces from Restart Kernel → Run All |

## Gate Outcomes

- **PASS** — Monte Carlo validates analytical propagation and empirical-state stress results are interpretable.
- **PASS WITH DOCUMENTED CONDITIONS** — variance propagation validates, but distributional assumptions or limited empirical state support materially constrain interpretation.
- **FAIL** — Monte Carlo does not reproduce the analytical budget or reveals an unresolved implementation/model inconsistency.

## Next Stage

After MC-001 closure:

```text
HV-013 — Final Engineering Assessment
```
