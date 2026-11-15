"""Triage: dedupe by fingerprint and never promote unreproduced noise to confirmed."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..contracts.result import Observation
from ..provenance.manifest import sha256_bytes

SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


@dataclass
class TriageItem:
    fingerprint: str
    observation: Observation
    confirmed: bool
    duplicates: int = 0


def triage(observations: Iterable[Observation]) -> list[TriageItem]:
    items: dict[str, TriageItem] = {}
    for observation in observations:
        fingerprint = sha256_bytes(
            f"{observation.target_ref}|{observation.kind}|{observation.summary}".encode("utf-8")
        )
        if fingerprint in items:
            items[fingerprint].duplicates += 1
            continue
        items[fingerprint] = TriageItem(
            fingerprint=fingerprint,
            observation=observation,
            confirmed=observation.reproduced and SEVERITY_ORDER.get(observation.severity, 0) >= 1,
        )
    return sorted(
        items.values(),
        key=lambda item: (-SEVERITY_ORDER.get(item.observation.severity, 0), item.fingerprint),
    )
