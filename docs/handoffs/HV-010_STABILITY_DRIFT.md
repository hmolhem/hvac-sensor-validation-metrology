# HV-010 Handoff — Stability & Drift

## Milestone Identity

- Milestone: HV-010
- Branch: `feature/hv-010-stability-drift`
- Technical gate: SD-001
- Notebook: `notebooks/07_stability_and_drift.ipynb`
- Input release: `VSM-LAB-DATA-v1.1`
- Outcome: **PASS WITH DOCUMENTED CONDITIONS**

## Objective

Quantify aging-related center drift, short-term stability, pointwise drift, and span/shape change using analyst-visible stability measurements and the frozen HV-006 C1 calibration.

## Verified Stability Boundary

- STABILITY Test_IDs: **22**
- rows: **1,320**
- samples/Test_ID: **60**
- temperature: **25 °C**
- direction: **UP**
- chamber state: **STABLE**

Weekly center schedule:
- 13 Test_IDs
- 50 %RH
- Aging Day 0–84 in 7-day increments

Monthly multi-point schedule:
- 9 Test_IDs
- 30/50/70 %RH
- Aging Day 30/60/90

## Frozen Calibration

```text
RH_Calibrated = RH_DUT + 1.2266788194 %RH
```

Because C1 is a constant additive offset, it changes absolute bias but does not change:

- drift from baseline;
- within-Test_ID scatter;
- span change.

## Weekly Center Drift

Descriptive linear trend:

```text
Slope           ≈ +0.004431 %RH/day
Slope × 30 days ≈ +0.13293 %RH/30 days
R²              ≈ 0.405
```

Observed trajectory is non-monotonic:

- Day 0 drift: 0.0000 %RH
- Day 63 drift: +0.5017 %RH
- Day 70 drift: +0.5025 %RH
- Day 84 drift: +0.0472 %RH
- maximum |drift|: approximately 0.5025 %RH

Interpretation: a single linear aging coefficient is not an adequate complete model. The evidence is better described as a time-dependent center excursion over the tested interval.

## Weekly Short-Term Scatter

Within-Test_ID error SD:

- minimum: approximately 0.2238 %RH
- median: approximately 0.2549 %RH
- maximum: approximately 0.3151 %RH
- Day 84: approximately 0.2642 %RH

Descriptive slope:

```text
approximately -0.0000108 %RH/day
R² ≈ 0.00014
```

There is no evidence of short-term scatter degradation over 0–84 days.

## Monthly Point Drift

Day-60 point drift relative to Day 30:

- 30 %RH: +0.0108 %RH
- 50 %RH: -0.1068 %RH
- 70 %RH: -0.1400 %RH

Day-90 point drift relative to Day 30:

- 30 %RH: +0.0487 %RH
- 50 %RH: +0.0277 %RH
- 70 %RH: -0.1025 %RH

The common-mode shift is small by Day 90, but the RH-dependent pattern remains.

## Span / Shape Change

Calibrated error span:

- Day 30: +0.1072 %RH
- Day 60: -0.0437 %RH
- Day 90: -0.0440 %RH

Therefore:

- Day 60 span change vs Day 30: approximately -0.1508 %RH
- Day 90 span change vs Day 30: approximately -0.1512 %RH

Interpretation: an RH-dependent shape/span change appears by Day 60 and remains approximately stable through Day 90.

## Weekly / Monthly Center Consistency

At 50 %RH, monthly C1 MBE minus weekly linear-trend prediction:

- Day 30: +0.0638 %RH
- Day 60: -0.1760 %RH
- Day 90: -0.1744 %RH

Because the weekly linear model has only moderate explanatory power, these residuals indicate temporal structure beyond a single linear trend rather than a definitive schedule incompatibility.

## Uncertainty-Budget Handoff

Three distinct stability quantities must be handled separately in HV-011:

1. **Short-term scatter**
   - approximately 0.25–0.32 %RH;
   - overlaps conceptually with repeatability evidence from HV-005;
   - should not be double-counted automatically.

2. **Center drift / temporal excursion**
   - maximum observed excursion approximately 0.5025 %RH;
   - systematic/time-dependent;
   - should not automatically be treated as an independent random component.

3. **RH-dependent span/shape change**
   - approximately -0.151 %RH from Day 30 to Day 60/90;
   - distinct from common-mode drift.

HV-011 must explicitly decide whether each effect is corrected, bounded, or represented probabilistically.

## SD-001 Gate

**SD-001 = PASS WITH DOCUMENTED CONDITIONS**

Documented conditions:

1. Weekly center behavior is non-monotonic with excursions up to approximately 0.50 %RH.
2. Short-term scatter does not degrade materially with aging.
3. Monthly span/shape change is approximately -0.151 %RH by Day 60 and remains similar at Day 90.
4. A simple linear aging model is not sufficient as a complete description.
5. Systematic drift and span change must not be blindly converted into independent random uncertainty components.
6. No external drift acceptance threshold is introduced here.

## Curated Evidence

Notebook 07 exports:

- `reports/tables/hv010_stability_test_summary.csv`
- `reports/tables/hv010_weekly_center_drift.csv`
- `reports/tables/hv010_weekly_trend_summary.csv`
- `reports/tables/hv010_monthly_point_drift.csv`
- `reports/tables/hv010_monthly_span_change.csv`
- `reports/figures/hv010_weekly_center_drift.png`
- `reports/figures/hv010_weekly_scatter_vs_age.png`
- `reports/figures/hv010_monthly_point_drift.png`
- `reports/figures/hv010_monthly_span_change.png`

## Next Engineering Stage

HV-011 — Measurement Uncertainty Budget.
