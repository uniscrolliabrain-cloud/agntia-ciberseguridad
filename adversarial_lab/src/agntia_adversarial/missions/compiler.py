"""Mission -> ExperimentSpec, gated by deterministic authorization."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ..contracts.experiment import ExperimentSpec, Limits, TargetRef
from ..domain.engagement import Engagement
from ..domain.scope import Scope
from ..policy.authorization import Authorizer


class MissionError(RuntimeError):
    pass


def compile_experiment(
    mission: dict,
    engagement: Engagement,
    scope: Scope,
    target_ref: str,
    authorizer: Authorizer | None = None,
) -> ExperimentSpec:
    if target_ref not in {target.ref for target in scope.targets}:
        raise MissionError(f"target outside scope: {target_ref}")
    missing = [cap for cap in mission["required_capabilities"] if not scope.allows_capability(cap)]
    if missing:
        raise MissionError(f"scope misses capabilities: {missing}")
    target = scope.targets[[t.ref for t in scope.targets].index(target_ref)]
    decision = (authorizer or Authorizer()).decide(
        engagement=engagement,
        scope=scope,
        tenant_id=engagement.tenant_id,
        target_ref=target_ref,
        capability=mission["required_capabilities"][0],
        expected_fingerprint=target.fingerprint,
    )
    if not decision.allowed:
        raise MissionError(f"authorization denied: {decision.reasons}")
    limits = mission["limits"]
    return ExperimentSpec(
        id=f"exp-{uuid.uuid4().hex[:12]}",
        campaign_id=mission.get("campaign_id", "ADVLAB"),
        mission_id=mission["id"],
        tenant_id=engagement.tenant_id,
        engagement_id=engagement.id,
        scope_id=scope.id,
        targets=[TargetRef(kind=target.kind, ref=target.ref, fingerprint=target.fingerprint)],
        capabilities=list(mission["required_capabilities"]),
        limits=Limits(
            max_duration_seconds=limits["max_duration_seconds"],
            max_requests=limits.get("max_requests", 50),
            max_cost_cents=limits.get("max_cost_cents", 100),
            network_egress="deny",
        ),
        stop_conditions=list(mission["stop_conditions"]),
        created_at=datetime.now(timezone.utc),
    )
