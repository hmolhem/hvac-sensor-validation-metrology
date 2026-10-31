# HV-012 Handoff — Monte Carlo Uncertainty

## Milestone Identity

- Milestone: HV-012
- Branch: `feature/hv-012-monte-carlo-uncertainty`
- Technical gate: MC-001
- Notebook: `notebooks/09_monte_carlo.ipynb`
- Analytical baseline: HV-011 / MU-001
- Outcome: **PASS WITH DOCUMENTED CONDITIONS**

## Objective

Validate the HV-011 analytical uncertainty budget numerically and determine how uncertainty-interval shape changes when the dominant point-state component preserves observed Direction × Run structure instead of using a Gaussian approximation.

## Frozen Controls

```text
master RNG seed = 7140
trials per point per model = 250,000
```

Four evaluation points:

- UNC-001: 30 %RH / 25 °C
- UNC-002: 50 %RH / 25 °C
- UNC-003: 70 %RH / 25 °C
- UNC-004: 80 %RH / 35 °C

## Model A — Analytical-Equivalent

Components:

- repeatability of 60-s mean: Normal
- C1 offset-estimation uncertainty: Normal
- point-state residual: Normal
- reference calibration: Normal
- stability excursion: Uniform over ±0.5025 %RH

This model mirrors the HV-011 analytical variance budget.

## Model B — Empirical-State Sensitivity

The point-state component is replaced with a four-state equal-probability bootstrap constructed from the observed Direction × Run Test_ID residual means.

The four states are:

1. centered by subtracting the point mean;
2. rescaled so population SD equals the frozen HV-011 `u_state`;
3. sampled with equal probability.

This preserves state structure while matching the same variance budget.

## Numerical Validation

### Model A

Relative MC SD error versus analytical `u_c`:

- UNC-001: +0.036%
- UNC-002: -0.106%
- UNC-003: -0.166%
- UNC-004: -0.002%

Worst magnitude:

```text
0.166%
```

This is well inside the frozen 1% criterion.

### Model B

Relative MC SD error magnitude is at most approximately:

```text
0.146%
```

This is well inside the frozen 1.5% criterion.

Monte Carlo means for both models satisfy:

```text
|mean| <= 0.00159 %RH
```

## Interval / Coverage Findings

### Model A

Central 95% half-widths:

- UNC-001: 1.2058 %RH
- UNC-002: 1.1590 %RH
- UNC-003: 1.1564 %RH
- UNC-004: 1.1991 %RH

HV-011 analytical `2u_c` values:

- UNC-001: 1.2331 %RH
- UNC-002: 1.1858 %RH
- UNC-003: 1.1866 %RH
- UNC-004: 1.2250 %RH

Coverage inside `±2u_c` is approximately 95.49–95.59%.

Interpretation: analytical k=2 intervals are slightly conservative relative to the exact mixed Normal + Uniform Model A central 95% interval.

### Model B

Central 95% half-widths:

- UNC-001: 1.0894 %RH
- UNC-002: 1.0541 %RH
- UNC-003: 1.0595 %RH
- UNC-004: 1.0847 %RH

These are approximately 90.4–91.6% of the corresponding Model A half-widths.

Coverage inside `±2u_c` rises to approximately:

```text
98.15–98.41%
```

## Distribution Shape

Model B remains nearly symmetric but is strongly platykurtic:

```text
excess kurtosis ≈ -0.85 to -0.91
```

The finite balanced UP/DOWN state support produces lighter/bounded tails compared with the Gaussian state approximation.

Thus:

```text
same variance != same coverage interval
```

## Residual-Bias Total-Error Sensitivity

After adding frozen point residual bias, Model A central 95% total-error intervals are approximately:

- UNC-001: [-1.109, +1.290] %RH
- UNC-002: [-0.926, +1.376] %RH
- UNC-003: [-0.981, +1.331] %RH
- UNC-004: [-1.350, +1.039] %RH

Model B intervals are narrower.

Model-based probability of total error lying inside the public static ±2 %RH accuracy limit is above 99.8% for all points under Model A and approximately 100% under Model B.

These values are sensitivity diagnostics only, not formal compliance probabilities.

## Engineering Interpretation

Monte Carlo validates the **scale** of the HV-011 analytical uncertainty budget.

The principal remaining uncertainty is not numerical propagation but the probability model assigned to state/history dependence.

HV-011 therefore remains the primary traceable uncertainty statement:

```text
u_c ≈ 0.593–0.617 %RH
U(k=2) ≈ 1.186–1.233 %RH
```

HV-012 adds distribution-shape sensitivity and confirms that Direction/Run structure matters beyond variance alone.

## MC-001 Gate

**MC-001 = PASS WITH DOCUMENTED CONDITIONS**

Documented conditions:

1. Model B has only four empirical Test_ID states per point.
2. Model A uses explicit Normal assumptions for reference calibration and point-state effects.
3. Model B is a structure-preserving sensitivity model, not an inferred population PDF.
4. Coverage inside `±2u_c` is model-sensitive: about 95.5% in Model A and 98.1–98.4% in Model B.
5. Scope remains the 60-s stable static result.
6. Probability-within-±2 %RH results are not formal product reliability probabilities.

## Curated Evidence

Notebook 09 exports:

- `reports/tables/hv012_mc_summary.csv`
- `reports/tables/hv012_mc_state_support.csv`
- `reports/tables/hv012_mc_model_comparison.csv`
- `reports/figures/hv012_mc_interval_comparison.png`
- `reports/figures/hv012_mc_representative_distribution.png`

## Next Engineering Stage

HV-013 — Final Engineering Assessment.
