"""Versioned experiment contract shared by planner, broker and providers."""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class TargetRef(BaseModel):
    kind: str
    ref: str
    fingerprint: str


class Limits(BaseModel):
    max_duration_seconds: int = Field(default=900, gt=0, le=7200)
    max_requests: int = Field(default=200, gt=0, le=10000)
    max_cost_cents: int = Field(default=100, ge=0, le=100000)
    network_egress: str = "deny"


class ExperimentSpec(BaseModel):
    schema_version: int = 1
    id: str
    campaign_id: str
    mission_id: str
    tenant_id: str
    engagement_id: str
    scope_id: str
    targets: List[TargetRef]
    capabilities: List[str]
    limits: Limits = Limits()
    stop_conditions: List[str] = Field(default_factory=list)
    created_at: datetime

    def requires(self, capability: str) -> bool:
        return capability in self.capabilities
