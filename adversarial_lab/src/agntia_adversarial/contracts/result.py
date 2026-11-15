"""Run results. NOT_RUN and BLOCKED never become PASS."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from .evidence import EvidenceRef


class Status(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    NOT_RUN = "NOT_RUN"


class Observation(BaseModel):
    id: str
    kind: str
    target_ref: str
    summary: str
    severity: str = "info"
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    evidence: List[EvidenceRef] = Field(default_factory=list)
    reproduced: bool = False


class RunReceipt(BaseModel):
    run_id: str
    experiment_id: str
    tenant_id: str
    status: Status
    started_at: datetime
    ended_at: datetime
    observations: List[Observation] = Field(default_factory=list)
    evidence: List[EvidenceRef] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)

    def counts(self) -> dict[str, int]:
        totals: dict[str, int] = {}
        for observation in self.observations:
            totals[observation.severity] = totals.get(observation.severity, 0) + 1
        return totals
