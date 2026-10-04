# Engineering Questions

## EQ-01 — Data Qualification
Is the frozen dataset structurally complete, internally consistent, correctly mapped to the experimental design, and valid for downstream analysis?

## EQ-02 — Static Measurement Performance
How large is the DUT measurement error, and how does it vary with relative humidity and temperature?

Primary error definition:

`e = RH_DUT - RH_Reference`

Positive error means the DUT reads higher than the reference indication.

## EQ-03 — Repeatability and Reproducibility
How much variability arises within runs, between runs, and between test days?

Conceptual model:

`Y_ijk = mu + D_i + R_j(i) + epsilon_ijk`

## EQ-04 — Hysteresis / Direction Dependence
Does DUT behavior differ materially between increasing and decreasing humidity trajectories under matched conditions?

## EQ-05 — Calibration Model Development
Can a parsimonious calibration model reduce systematic error using only designated calibration observations?

Candidate model classes may include:
- linear correction
- temperature-aware correction
- nonlinear or interaction terms when justified by evidence

Model choice is based on residual behavior, prediction performance, interpretability, complexity, and physical plausibility, not R² alone.

## EQ-06 — Blind Validation
Does the frozen calibration model improve performance on independent validation observations that were not used during fitting?

Compare raw and corrected performance using metrics such as MBE, MAE, RMSE, and maximum absolute error.

## EQ-07 — Dynamic Step Response
What are the sensor's characteristic response time, time constant, settling behavior, rise/fall asymmetry, and possible dynamic bias under step changes?

A first-order-plus-delay model may be used when supported by the response shape.

## EQ-08 — Dynamic Tracking
How does the sensor track changing humidity under ramp, cyclic, and sinusoidal excitation?

Potential quantities include lag, dynamic bias, cycle-to-cycle repeatability, dynamic hysteresis, gain, and phase lag.

## EQ-09 — Stability and Drift
How does measurement error evolve with aging time, and is an engineering-significant drift trend present?

A baseline model may use:

`e(t) = beta_0 + beta_1 t + epsilon`

## EQ-10 — Measurement Uncertainty and Compliance
What is the combined measurement uncertainty at selected operating points, and how should uncertainty affect the final interpretation of sensor compliance with stated requirements?

The final decision must integrate observed performance, calibration, uncertainty, and engineering requirements.
