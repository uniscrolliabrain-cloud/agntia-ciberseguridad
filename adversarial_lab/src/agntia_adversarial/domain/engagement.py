"""Engagement and authorization window contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EngagementStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Engagement(BaseModel):
    """Signed authorization to test a tenant's synthetic or real assets."""

    schema_version: int = 1
    id: str
    tenant_id: str
    authorized_by: str
    signature_ref: str
    starts_at: datetime
    ends_at: datetime
    status: EngagementStatus = EngagementStatus.DRAFT
    max_risk_level: str = "low"
    mode: str = "lab_clone"

    def is_active(self, now: Optional[datetime] = None) -> bool:
        moment = now or utcnow()
        if self.status is not EngagementStatus.ACTIVE:
            return False
        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None:
            return False
        return self.starts_at <= moment <= self.ends_at

    def revoke(self) -> "Engagement":
        return self.model_copy(update={"status": EngagementStatus.REVOKED})

    def expire(self) -> "Engagement":
        return self.model_copy(update={"status": EngagementStatus.EXPIRED})
