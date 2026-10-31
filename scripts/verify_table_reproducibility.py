"""Verify regenerated CSV evidence against the committed repository snapshot.

String/object columns must match exactly. Numeric columns are compared with a
tight floating-point tolerance so harmless last-bit differences across BLAS/
NumPy builds do not create false reproducibility failures.
"""

from __future__ import annotations

import io
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = ROOT / "reports" / "tables"
ATOL = 1e-12
RTOL = 1e-12


def committed_text(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    result = subprocess.run(
        ["git", "show", f"HEAD:{rel}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def compare_csv(path: Path) -> list[str]:
    expected = pd.read_csv(io.StringIO(committed_text(path)))
    actual = pd.read_csv(path)
    errors: list[str] = []

    if list(expected.columns) != list(actual.columns):
        return [f"{path.name}: column mismatch"]
    if expected.shape != actual.shape:
        return [f"{path.name}: shape {actual.shape} != committed {expected.shape}"]

    for col in expected.columns:
        e = expected[col]
        a = actual[col]
        if pd.api.types.is_numeric_dtype(e) and pd.api.types.is_numeric_dtype(a):
            ev = e.to_numpy(dtype=float)
            av = a.to_numpy(dtype=float)
            if not np.allclose(ev, av, rtol=RTOL, atol=ATOL, equal_nan=True):
                delta = np.nanmax(np.abs(ev - av))
                errors.append(
                    f"{path.name}:{col}: numeric mismatch; max abs delta={delta:.3e}"
                )
        else:
            es = e.fillna("<NA>").astype(str).to_numpy()
            ass = a.fillna("<NA>").astype(str).to_numpy()
            if not np.array_equal(es, ass):
                errors.append(f"{path.name}:{col}: text/categorical mismatch")
    return errors


def main() -> int:
    errors: list[str] = []
    for path in sorted(TABLE_DIR.glob("*.csv")):
        errors.extend(compare_csv(path))

    if errors:
        print("TABLE REPRODUCIBILITY: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "TABLE REPRODUCIBILITY: PASS "
        f"(exact text; numeric rtol={RTOL:g}, atol={ATOL:g})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
