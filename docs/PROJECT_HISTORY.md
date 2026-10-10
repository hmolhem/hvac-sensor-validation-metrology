# Project History

## HV-001 — Repository Bootstrap

**Status:** PASS  
**Branch:** `chore/hv-001-repository-bootstrap`  
**Pull Request:** #1

### Objective
Establish the independent public repository, governance rules, traceability system, project architecture, and analyst-blind boundary before importing the frozen dataset or beginning analysis.

### Key Decisions
- Repository identity is independent of any course or university branding.
- `main` is merge-only; no direct development occurs on `main`.
- All substantive work is indexed using stable `HV-###` milestone identifiers.
- Hidden simulator truth is prohibited from this repository.
- The frozen analyst-facing dataset will be imported later as immutable raw input.
- Analysis will be engineering-question-driven, with strict calibration/validation separation.

### Result
Bootstrap review PASS. Governance, project indexing, handoff indexing, project definition, engineering questions, analysis roadmap, repository architecture, and the professional README were established without introducing hidden simulator truth.

## HV-002 - Frozen Dataset Intake

**Status:** PASS  
**Branch:** `feature/hv-002-frozen-dataset-intake`  
**Pull Request:** #2

### Objective
Import the canonical frozen analyst-facing `VSM-LAB-DATA-v1.1` release as immutable raw input while preserving byte-level provenance, release commitments, and the analyst-blind boundary.

### Key Decisions
- Use `VSM-LAB-DATA-v1.1` as the canonical downstream release.
- Preserve exact committed release bytes rather than relying on Windows working-tree copies.
- Enforce canonical LF line endings for frozen raw release artifacts.
- Treat `data/raw/vsm_lab_data_v1_1/` as immutable downstream input.
- Verify provenance from committed Git blobs using `DV-001`.
- Keep hidden simulator truth and protected private configuration out of the repository.
- Perform no sensor-performance analysis during dataset intake.

### Verification
`DV-001 = PASS (10/10)`.

The gate verified required artifacts, release identity, frozen state, manifest commitment, seven CSV payload hashes, row counts, schemas, analyst/private separation, test-matrix completeness, and canonical LF committed bytes.

### Result
The canonical `VSM-LAB-DATA-v1.1` package is now imported and independently verified as the authoritative raw dataset for downstream HVAC sensor validation and metrology analysis.


## HV-003 - Dataset Qualification

**Status:** PASS WITH DOCUMENTED DESIGN CONDITIONS  
**Branch:** `feature/hv-003-dataset-qualification`  
**Pull Request:** TBD

### Objective
Qualify the frozen analyst-facing `VSM-LAB-DATA-v1.1` campaign before any substantive DUT-performance analysis by verifying structural completeness, experimental traceability, calibration/validation separation, temporal integrity, and experimental-state consistency.

### Key Decisions
- Treat dataset qualification as an engineering gate, not generic data cleaning.
- Use family-specific completeness criteria for static, step, ramp, cyclic, sinusoidal, and stability tests.
- Preserve strict calibration/validation Test_ID separation.
- Treat four `UNCERTAINTY_EVALUATION` matrix-only Test_IDs as intentional design points.
- Treat dynamic-step `STABLE` -> `TRANSIENT` state representation as non-blocking; settling behavior will be derived from response data later.
- Require a fresh-kernel Restart Kernel -> Run All verification before closing the notebook.

### Verification
`DQ-001 = PASS WITH DOCUMENTED DESIGN CONDITIONS`.

All blocking checks passed. The final notebook gate reports `DQ-001 GATE: PASS` and releases the dataset for downstream analysis.

### Result
The frozen dataset is qualified as sufficiently complete, traceable, internally consistent, and experimentally coherent for downstream sensor characterization, calibration, independent validation, dynamic-response analysis, stability assessment, and measurement-uncertainty evaluation.

The next analysis stage is Notebook 01 - Static Characterization.
