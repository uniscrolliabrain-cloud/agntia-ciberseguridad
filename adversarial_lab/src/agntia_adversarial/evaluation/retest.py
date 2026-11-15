"""Retest: a fix is only accepted when the original finding no longer reproduces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..contracts.result import Observation


@dataclass
class RetestResult:
    status: str
    reason: str
    still_present: list[str]


def retest(original_ids: Iterable[str], observations: Iterable[Observation]) -> RetestResult:
    original = list(original_ids)
    present = [item.id for item in observations if item.id in original and item.reproduced]
    if not original:
        return RetestResult("NOT_RUN", "no original finding to retest", [])
    if present:
        return RetestResult("FAIL", "finding still reproduces", present)
    return RetestResult("PASS", "original finding no longer reproduces", [])
