# HV-001 — Repository Bootstrap Handoff

## Milestone Identity

- Project: HVAC Sensor Validation & Metrology
- Milestone: HV-001
- Branch: `chore/hv-001-repository-bootstrap`
- Pull Request: #1
- Status: PASS

## Purpose

Establish the public analyst-side repository as an independent professional engineering case study before importing data or beginning analysis.

## Frozen Governance

1. `main` is merge-only. No direct development commits are allowed.
2. Every substantive milestone is assigned a stable `HV-###` identifier and indexed.
3. Hidden simulator truth and private DUT personality artifacts are prohibited.
4. `VSM-LAB-DATA-v1` will be imported only as analyst-facing frozen input.
5. Raw imported data will be immutable.
6. Calibration and validation data remain strictly separated.
7. Analysis is driven by engineering questions and evidence-based decisions.

## Repository Role

This repository performs downstream characterization, calibration, validation, dynamic-response analysis, stability analysis, uncertainty evaluation, and engineering assessment.

It is intentionally separate from the upstream virtual sensor-metrology laboratory used to generate the synthetic measurement campaign.

## Bootstrap Review

PASS. The milestone establishes governance, traceability, project definition, engineering questions, analysis roadmap, repository architecture, and the professional project README without importing hidden simulator truth.

## Next Planned Milestone

HV-002 — Frozen Dataset Intake

Primary gate: `DV-001 Dataset Intake Verification`.
