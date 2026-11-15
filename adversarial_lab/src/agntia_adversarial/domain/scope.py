"""Scope manifest: what may be tested, with which capability, and against which fingerprint."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class Target(BaseModel):
    kind: str = Field(pattern="^(repo|api|container|model|host)$")
    ref: str
    fingerprint: str = Field(min_length=8)


class Scope(BaseModel):
    schema_version: int = 1
    id: str
    engagement_id: str
    tenant_id: str
    targets: List[Target]
    capabilities: List[str]
    max_requests: int = 200
    network_egress: str = "deny"

    def allows_target(self, ref: str) -> bool:
        return any(target.ref == ref for target in self.targets)

    def fingerprint_for(self, ref: str) -> str | None:
        for target in self.targets:
            if target.ref == ref:
                return target.fingerprint
        return None

    def allows_capability(self, capability: str) -> bool:
        return capability in self.capabilities
