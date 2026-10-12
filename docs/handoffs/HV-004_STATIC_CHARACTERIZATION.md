# HV-004 - Static Characterization Handoff

## Milestone Identity

- Project: HVAC Sensor Validation & Metrology
- Milestone: HV-004
- Branch: `feature/hv-004-static-characterization`
- Pull Request: #5
- Technical Gate: `SC-001`
- Status: PASS

## Purpose

Characterize the pre-calibration static RH measurement behavior of the DUT using only qualified analyst-visible evidence from the frozen `VSM-LAB-DATA-v1.1` release.

The milestone answers the primary engineering question:

`How large is the DUT measurement error, and how does it vary with RH and temperature?`

It also screens the secondary question:

`Does static error differ between increasing and decreasing humidity directions under matched conditions?`

## Primary Implementation

- Analysis plan: `docs/analysis_plan/SC-001_STATIC_CHARACTERIZATION_PLAN.md`
- Terms and completion criteria: `docs/reference/HV-004_SC-001_TERMS_AND_COMPLETION_CRITERIA.md`
- Notebook: `notebooks/01_static_characterization.ipynb`
- Frozen raw input: `data/raw/vsm_lab_data_v1_1/`

The notebook was verified with Restart Kernel -> Run All and completed with `SC-001 FINAL GATE DECISION : PASS`.

## Analysis Boundary

HV-004 uses only:

- `Test_Family == STATIC`
- `Analysis_Role == CHARACTERIZATION`

The working frame contains:

- 7,200 measurement rows
- 120 Test_IDs
- 60 samples per Test_ID
- 0 CALIBRATION rows
- 0 VALIDATION rows

Calibration and validation evidence remain reserved for later milestones.

## Error Convention

The observed RH error is defined as:

`Error_RH = RH_DUT - RH_Reference`

The reference indication is not treated as exact physical truth.

## Principal Results

At the Test_ID level:

- MBE: -1.1412 %RH
- MAE: 1.1412 %RH
- RMSE: 1.2228 %RH
- Error standard deviation: 0.4411 %RH
- Test-level mean errors were all negative
- Test-level mean-error range: -1.8967 to -0.4557 %RH

The static error is therefore persistently negative but is not adequately described by one constant offset.

### RH dependence

The net endpoint change from 20 to 80 %RH was +0.1087 %RH, but the internal RH pattern was non-monotonic. Endpoint comparison alone therefore does not represent the full RH-dependent structure.

### Temperature dependence

The 35 °C minus 15 °C mean-error change varied across RH from +0.2325 %RH to -0.4422 %RH. The change in both magnitude and sign is evidence of condition-dependent temperature behavior and is consistent with an RH × Temperature interaction structure.

### Direction dependence

All 60 matched UP/DOWN pairs were complete.

- Mean matched UP - DOWN difference: -0.8304 %RH
- Median matched difference: -0.8273 %RH
- Standard deviation of matched differences: 0.0469 %RH
- Range: -0.9250 to -0.6985 %RH

All matched differences were negative. UP-direction error was consistently more negative than matched DOWN-direction error. This is treated as static direction-dependence / hysteresis screening, not final hysteresis compliance.

### Day / run context

Run 2 showed an overall mean-error shift of approximately -0.0851 %RH relative to Run 1, with the same ordering across all three test days.

This remains descriptive context. Formal repeatability/reproducibility variance decomposition is deferred to Notebook 02.

## Data Preparation and Outlier Policy

No observation was removed solely because it appeared statistically extreme.

Potential anomalies are retained unless a traceable technical reason supports exclusion, such as confirmed acquisition failure, invalid chamber state, corrupted record, or another documented test anomaly.

Repeated samples within one Test_ID are not treated as independent experimental replications. Test_ID is the primary experimental unit for condition-level interpretation.

## SC-001 Completion Gate

All twelve completion criteria were satisfied:

1. Qualified characterization data only
2. Error convention explicit and correct
3. Test_ID-level summaries used for condition interpretation
4. Overall pre-calibration metrics reproduced
5. RH dependence evaluated
6. Temperature dependence evaluated with RH context preserved
7. Matched direction dependence evaluated
8. Day/run context inspected
9. Calibration/validation leakage prevented
10. No hidden simulator truth used
11. Engineering interpretation separated from numerical output
12. Clean-kernel reproducibility verified

Formal decision:

`SC-001 = PASS`

## Scope Boundary

HV-004 does not perform:

- formal R&R variance decomposition
- calibration-model fitting or freeze
- blind validation
- dynamic characterization
- drift/stability analysis
- final uncertainty-budget calculation
- final specification-compliance decision

## Next Planned Milestone

Proceed to Notebook 02 - Repeatability & Reproducibility.

The next engineering question changes from:

`What does the qualified static evidence reveal about DUT measurement performance?`

to:

`How much of the observed measurement variation is attributable to within-run repeatability and between-run/day reproducibility?`
