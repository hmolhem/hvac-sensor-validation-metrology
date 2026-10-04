from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path


RELEASE_ID = "VSM-LAB-DATA-v1.1"
RAW_DIR = "data/raw/vsm_lab_data_v1_1"

CSV_FILES = [
    "static_measurements.csv",
    "dynamic_step_measurements.csv",
    "ramp_measurements.csv",
    "cyclic_measurements.csv",
    "sinusoidal_measurements.csv",
    "stability_measurements.csv",
    "test_matrix.csv",
]

REQUIRED_FILES = {
    "README.md",
    "dataset_manifest.json",
    "release_commitment_v1_1.json",
    *CSV_FILES,
}

REPORT_PATH = Path(
    "verification/DV-001_Frozen_Dataset_Intake/"
    "dv001_verification_report.csv"
)


def git_bytes(path: str) -> bytes:
    """Return exact committed blob bytes from HEAD."""
    return subprocess.check_output(
        ["git", "show", f"HEAD:{path}"]
    )


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tracked_paths(prefix: str | None = None) -> list[str]:
    cmd = ["git", "ls-tree", "-r", "--name-only", "HEAD"]
    if prefix:
        cmd += ["--", prefix]

    output = subprocess.check_output(cmd, text=True)
    return [line.strip() for line in output.splitlines() if line.strip()]


def read_csv_blob(path: str):
    data = git_bytes(path)

    stream = io.TextIOWrapper(
        io.BytesIO(data),
        encoding="utf-8",
        newline="",
    )

    reader = csv.reader(stream)
    header = next(reader)
    rows = sum(1 for _ in reader)

    return header, rows


results = []


def record(check_id: str, name: str, passed: bool, details: str):
    results.append(
        {
            "check_id": check_id,
            "check": name,
            "status": "PASS" if passed else "FAIL",
            "details": details,
        }
    )


# ------------------------------------------------------------
# A — Required release artifacts
# ------------------------------------------------------------

raw_paths = tracked_paths(RAW_DIR)
raw_names = {Path(p).name for p in raw_paths}

passed = raw_names == REQUIRED_FILES

record(
    "A",
    "Required release artifacts",
    passed,
    (
        "Canonical raw package contains exactly the required "
        f"{len(REQUIRED_FILES)} files."
        if passed
        else
        f"Observed={sorted(raw_names)}"
    ),
)


# ------------------------------------------------------------
# Load committed manifest and release commitment
# ------------------------------------------------------------

manifest_bytes = git_bytes(f"{RAW_DIR}/dataset_manifest.json")
commitment_bytes = git_bytes(
    f"{RAW_DIR}/release_commitment_v1_1.json"
)

manifest = json.loads(manifest_bytes.decode("utf-8"))
commitment = json.loads(commitment_bytes.decode("utf-8"))


# ------------------------------------------------------------
# B — Release identity
# ------------------------------------------------------------

passed = (
    manifest.get("release_id") == RELEASE_ID
    and commitment.get("release_id") == RELEASE_ID
)

record(
    "B",
    "Release identity",
    passed,
    f"Expected release_id={RELEASE_ID}",
)


# ------------------------------------------------------------
# C — Frozen upstream release state
# ------------------------------------------------------------

passed = (
    commitment.get("freeze_status") == "FROZEN"
    and commitment.get("verification_gate") == "DR-002"
    and commitment.get("verification_status") == "PASS (11/11)"
    and commitment.get("measurement_payload_changed") is False
)

record(
    "C",
    "Frozen upstream release state",
    passed,
    (
        "FROZEN; DR-002 PASS (11/11); "
        "measurement_payload_changed=false"
    ),
)


# ------------------------------------------------------------
# D — Manifest SHA-256 commitment
# ------------------------------------------------------------

observed_manifest_sha = sha256(manifest_bytes)
expected_manifest_sha = commitment.get("dataset_manifest_sha256")

passed = observed_manifest_sha == expected_manifest_sha

record(
    "D",
    "Committed manifest SHA-256",
    passed,
    f"Observed={observed_manifest_sha}",
)


# ------------------------------------------------------------
# E — Seven CSV payload commitments
# ------------------------------------------------------------

csv_hash_failures = []

for name in CSV_FILES:
    observed = sha256(git_bytes(f"{RAW_DIR}/{name}"))
    expected = manifest["files"][name]["sha256"]

    if observed != expected:
        csv_hash_failures.append(name)

passed = not csv_hash_failures

record(
    "E",
    "CSV payload SHA-256 commitments",
    passed,
    (
        "All seven committed CSV blobs match the manifest."
        if passed
        else f"Mismatches={csv_hash_failures}"
    ),
)


# ------------------------------------------------------------
# F — Row counts
# ------------------------------------------------------------

row_failures = []

for name in CSV_FILES:
    _, observed_rows = read_csv_blob(f"{RAW_DIR}/{name}")
    expected_rows = manifest["files"][name]["rows"]

    if observed_rows != expected_rows:
        row_failures.append(
            f"{name}: observed={observed_rows}, expected={expected_rows}"
        )

passed = not row_failures

record(
    "F",
    "CSV row counts",
    passed,
    (
        "All committed CSV row counts match the manifest."
        if passed
        else "; ".join(row_failures)
    ),
)


# ------------------------------------------------------------
# G — Schemas
# ------------------------------------------------------------

schema_failures = []

for name in CSV_FILES:
    observed_columns, _ = read_csv_blob(f"{RAW_DIR}/{name}")
    expected_columns = manifest["files"][name]["columns"]

    if observed_columns != expected_columns:
        schema_failures.append(name)

passed = not schema_failures

record(
    "G",
    "CSV schemas",
    passed,
    (
        "All committed CSV schemas match the manifest."
        if passed
        else f"Schema mismatches={schema_failures}"
    ),
)


# ------------------------------------------------------------
# H — Analyst/private-truth boundary
# ------------------------------------------------------------

all_paths = tracked_paths()

forbidden_prefixes = (
    "data/private_truth/",
    "config/private/",
)

forbidden_tracked = [
    p
    for p in all_paths
    if p.startswith(forbidden_prefixes)
]

passed = (
    manifest.get("analyst_private_truth_included") is False
    and not forbidden_tracked
)

record(
    "H",
    "Analyst/private-truth boundary",
    passed,
    (
        "Manifest declares no private truth and no protected "
        "private-truth paths are tracked."
        if passed
        else f"Forbidden tracked paths={forbidden_tracked}"
    ),
)


# ------------------------------------------------------------
# I — Test matrix / release completeness
# ------------------------------------------------------------

matrix_meta = manifest["files"].get("test_matrix.csv", {})

passed = (
    "test_matrix.csv" in raw_names
    and matrix_meta.get("rows") == 333
    and len(manifest.get("files", {})) == 7
)

record(
    "I",
    "Test matrix and release-package completeness",
    passed,
    (
        "test_matrix.csv present with 333 rows and manifest "
        "defines exactly seven CSV payloads."
    ),
)


# ------------------------------------------------------------
# J — Canonical LF committed bytes + Git policy
# ------------------------------------------------------------

text_paths = [
    ".gitattributes",
    f"{RAW_DIR}/README.md",
    f"{RAW_DIR}/dataset_manifest.json",
    f"{RAW_DIR}/release_commitment_v1_1.json",
    *[f"{RAW_DIR}/{name}" for name in CSV_FILES],
]

cr_paths = [
    path for path in text_paths
    if b"\r" in git_bytes(path)
]

attributes = git_bytes(".gitattributes").decode("utf-8")

required_rules = [
    "data/raw/vsm_lab_data_v1_1/*.csv text eol=lf",
    "data/raw/vsm_lab_data_v1_1/*.json text eol=lf",
    "data/raw/vsm_lab_data_v1_1/README.md text eol=lf",
]

missing_rules = [
    rule for rule in required_rules
    if rule not in attributes
]

passed = not cr_paths and not missing_rules

record(
    "J",
    "Canonical LF committed-byte policy",
    passed,
    (
        "Committed release blobs contain no CR bytes and "
        ".gitattributes enforces canonical LF."
        if passed
        else f"CR paths={cr_paths}; missing rules={missing_rules}"
    ),
)


# ------------------------------------------------------------
# Report
# ------------------------------------------------------------

REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

with REPORT_PATH.open(
    "w",
    encoding="utf-8",
    newline="",
) as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["check_id", "check", "status", "details"],
    )
    writer.writeheader()
    writer.writerows(results)


passed_count = sum(r["status"] == "PASS" for r in results)
total_count = len(results)

print(f"DV-001: {passed_count}/{total_count} checks PASS")

for result in results:
    print(
        f"{result['check_id']}: "
        f"{result['status']} - "
        f"{result['check']}"
    )

if passed_count != total_count:
    print("\nDV-001 FINAL RESULT: FAIL")
    raise SystemExit(1)

print("\nDV-001 FINAL RESULT: PASS")
print(
    "Frozen VSM-LAB-DATA-v1.1 intake is verified "
    "from committed Git blobs."
)
