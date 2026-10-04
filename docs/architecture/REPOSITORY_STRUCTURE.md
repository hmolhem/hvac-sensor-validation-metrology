# Repository Structure

```text
hvac-sensor-validation-metrology/
├── README.md
├── .gitignore
├── data/
│   ├── raw/
│   │   └── vsm_lab_data_v1/
│   └── processed/
├── config/
│   └── public/
├── notebooks/
├── src/
├── verification/
├── reports/
│   ├── figures/
│   └── tables/
├── report/
└── docs/
    ├── PROJECT_INDEX.md
    ├── PROJECT_HISTORY.md
    ├── governance/
    ├── project_definition/
    ├── analysis_plan/
    ├── architecture/
    └── handoffs/
```

## Directory Roles

- `data/raw/vsm_lab_data_v1/`: immutable frozen analyst-facing release.
- `data/processed/`: derived datasets and analysis-ready tables.
- `config/public/`: public specifications and analysis configuration.
- `notebooks/`: engineering-question-driven analyses.
- `src/`: reusable analysis utilities.
- `verification/`: formal intake and analysis verification gates.
- `reports/figures/`: generated figures for reporting.
- `reports/tables/`: generated tables for reporting.
- `report/`: engineering-report source and publication artifacts.
- `docs/`: governance, planning, handoffs, project history, and traceability records.

The upstream simulator implementation and private simulator truth do not belong in this repository.
