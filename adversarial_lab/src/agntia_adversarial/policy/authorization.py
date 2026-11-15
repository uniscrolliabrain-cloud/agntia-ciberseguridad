"""Deterministic authorization. The model proposes; this module disposes."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from ..domain.engagement import Engagement
from ..domain.scope import Scope


class AuthorizationDecision(BaseModel):
    allowed: bool
    reasons: List[str]

    @classmethod
    def deny(cls, reason: str) -> "AuthorizationDecision":
        return cls(allowed=False, reasons=[reason])


class Authorizer:
    """Deny-by-default checks shared by planner, broker and providers."""

    def decide(
        self,
        *,
        engagement: Engagement,
        scope: Scope,
        tenant_id: str,
        target_ref: str,
        capability: str,
        now: Optional[datetime] = None,
        expected_fingerprint: Optional[str] = None,
    ) -> AuthorizationDecision:
        reasons: List[str] = []
        if engagement.tenant_id != tenant_id:
            reasons.append("tenant_mismatch")
        if scope.tenant_id != tenant_id:
            reasons.append("scope_tenant_mismatch")
        if scope.engagement_id != engagement.id:
            reasons.append("scope_engagement_mismatch")
        if not engagement.is_active(now):
            reasons.append("engagement_not_active")
        if not scope.allows_target(target_ref):
            reasons.append("target_out_of_scope")
        if not scope.allows_capability(capability):
            reasons.append("capability_not_granted")
        if scope.network_egress != "deny":
            reasons.append("egress_must_be_denied")
        if expected_fingerprint is not None:
            actual = scope.fingerprint_for(target_ref)
            if actual != expected_fingerprint:
                reasons.append("target_fingerprint_changed")
        return AuthorizationDecision(allowed=not reasons, reasons=reasons)
