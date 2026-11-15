"""Fidelity is measured, not asserted."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def fidelity_report(twin_root: Path, expected_fields: Iterable[str]) -> dict[str, object]:
    data_dir = Path(twin_root) / "data"
    present: set[str] = set()
    for path in sorted(data_dir.glob("*.json")):
        records = json.loads(path.read_text(encoding="utf-8"))
        for record in records:
            present.update(record.keys())
    expected = sorted(set(expected_fields))
    covered = [field for field in expected if field in present]
    missing = [field for field in expected if field not in present]
    ratio = round(len(covered) / len(expected), 4) if expected else 0.0
    return {
        "expected": expected,
        "covered": covered,
        "missing": missing,
        "coverage": ratio,
        "claim": "synthetic_structural_only",
    }
