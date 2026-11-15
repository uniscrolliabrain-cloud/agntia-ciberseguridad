"""Operational metrics with explicit denominators."""

from __future__ import annotations

from typing import Iterable

from ..contracts.result import RunReceipt


def summarize(receipts: Iterable[RunReceipt]) -> dict[str, object]:
    items = list(receipts)
    statuses: dict[str, int] = {}
    severities: dict[str, int] = {}
    reproduced = 0
    for receipt in items:
        statuses[receipt.status.value] = statuses.get(receipt.status.value, 0) + 1
        for observation in receipt.observations:
            severities[observation.severity] = severities.get(observation.severity, 0) + 1
            reproduced += int(observation.reproduced)
    return {
        "runs": len(items),
        "statuses": statuses,
        "observations": sum(severities.values()),
        "severities": severities,
        "reproduced": reproduced,
        "reproduction_rate": round(reproduced / sum(severities.values()), 4) if severities else None,
    }
