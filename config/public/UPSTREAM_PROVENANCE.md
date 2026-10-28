# Public Lab Specification Provenance

This downstream repository imports the analyst-visible public laboratory specification from the upstream Virtual Sensor Metrology Lab for use in HV-011 and downstream engineering assessment.

## Source

- Upstream repository: `hmolhem/virtual-sensor-metrology-lab`
- Source path: `config/public/lab_spec_v1.json`
- Upstream main commit: `92fb4b756ba8d15082c6be2551fa8993c7ea3af7`
- Source blob SHA: `63f7fe4ed728b88fabda2d8f488549706b10e661`

## Information Boundary

Only the upstream **public / analyst-visible** specification is imported.

No files from:

- `config/private/`
- `data/private_truth/`
- hidden personality configuration
- latent simulator truth
- injected error-component truth

are used or imported.

The imported specification provides declared DUT, reference, chamber, DAQ, experimental-design, and uncertainty-evaluation metadata that the project definition explicitly allows the downstream analyst to use.
