# Project Definition

## Working Title

**Data-Driven Validation and Calibration of an HVAC Relative-Humidity Sensor Using a Synthetic Metrology Dataset**

## Core Problem

Manufacturer specifications alone do not establish how a sensor actually performs across humidity, temperature, repeated measurements, direction of environmental change, dynamic conditions, or operating time.

This project evaluates whether a relative-humidity device under test (DUT) can be reliably characterized, calibrated, and independently validated using only analyst-visible measurement data.

## Final Engineering Question

**Is the sensor suitable for the intended HVAC measurement application, under the tested operating conditions, after calibration and with quantified measurement uncertainty?**

## Analyst-Visible Evidence

The downstream analyst may use:
- frozen measurement files
- public test design and metadata
- public DUT/reference/chamber/DAQ specifications
- derived quantities computed from analyst-visible measurements

The analyst may not use hidden simulator truth.

## Scope

Included:
- dataset qualification
- static measurement error and bias
- repeatability and reproducibility
- hysteresis
- temperature influence
- calibration model development
- independent validation
- step-response characterization
- ramp/cyclic/sinusoidal dynamic tracking
- stability and drift
- uncertainty evaluation
- final engineering assessment

Excluded from this repository:
- physical chamber construction
- PCB/electronics design
- embedded firmware implementation
- closed-loop HVAC controller design
- hidden simulator truth or private simulator personality parameters

## Guiding Principle

This is a sensor-metrology and validation study first, and a Python/data-science implementation second. Python is the analytical tool, not the subject of the project.
