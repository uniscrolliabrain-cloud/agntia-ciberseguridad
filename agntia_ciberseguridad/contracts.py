from datetime import datetime
from enum import Enum
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StrictInt, field_validator, model_validator

OpaqueId = Annotated[str, Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$")]
ResourceId = Annotated[str, Field(pattern=r"^[a-f0-9]{32}$")]
Hash = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
Cents = Annotated[StrictInt, Field(ge=0, le=1_000_000)]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Role(str, Enum):
    viewer = "viewer"
    analyst = "analyst"
    reviewer = "reviewer"
    operator = "operator"
    owner = "owner"


class AssetKind(str, Enum):
    repository = "repository"
    directory = "directory"
    image = "image"
    web = "web"


class Profile(str, Enum):
    static_read = "static_read"
    passive_web = "passive_web"
    active_lab = "active_lab"


class AssetCreate(Model):
    target_ref: OpaqueId
    kind: AssetKind
    display_name: str = Field(min_length=2, max_length=160)

    @field_validator("display_name")
    @classmethod
    def no_controls(cls, value):
        if any(ord(c) < 32 or ord(c) == 127 for c in value):
            raise ValueError("Control characters are not allowed")
        return value


class Revision(Model):
    expected_revision: Annotated[StrictInt, Field(ge=0)]


class GrantCreate(Model):
    asset_id: ResourceId
    consent_ref: OpaqueId
    profile: Profile
    starts_at: AwareDatetime
    expires_at: AwareDatetime
    max_requests: Annotated[StrictInt, Field(ge=1, le=10_000)] = 100
    max_cost_cents: Cents = 0
    purpose: str = Field(min_length=5, max_length=1000)

    @model_validator(mode="after")
    def interval(self):
        if self.starts_at >= self.expires_at:
            raise ValueError("Invalid authorization interval")
        if (self.expires_at - self.starts_at).total_seconds() > 30 * 86400:
            raise ValueError("Authorization interval exceeds thirty days")
        return self


class GrantApproval(Revision):
    proposal_hash: Hash
    notes: str = Field(min_length=5, max_length=1000)


class GrantRevocation(Revision):
    notes: str = Field(min_length=5, max_length=1000)


class AuditPreview(Model):
    asset_id: ResourceId
    grant_id: ResourceId
    profile: Profile
    requests: Annotated[StrictInt, Field(ge=1, le=10_000)] = 1
    maximum_cost_cents: Cents = 0


class AssetPublic(Model):
    schema_version: Literal[1] = 1
    id: ResourceId
    tenant_id: OpaqueId
    target_ref: OpaqueId
    kind: AssetKind
    display_name: str
    state: Literal["registered", "disabled"]
    revision: int = Field(ge=0)
    created_at: AwareDatetime


class Tenant(Model):
    schema_version: Literal[1] = 1
    id: OpaqueId
    name: str = Field(min_length=1, max_length=160)
    timezone: str = Field(default='UTC', max_length=64)


class PrincipalPublic(Model):
    actor_id: OpaqueId
    role: Role
    tenants: list[OpaqueId] = Field(min_length=1, max_length=100)
    expires_at: AwareDatetime | None = None


class Job(Model):
    """Versioned future worker contract; no execution endpoint enabled in foundation."""
    schema_version: Literal[1] = 1
    id: ResourceId
    tenant_id: OpaqueId
    asset_id: ResourceId
    grant_id: ResourceId
    actor_id: OpaqueId
    state: Literal['pending','running','succeeded','failed','cancelled','blocked','reconciliation_required']
    revision: Annotated[StrictInt, Field(ge=0)] = 0
    correlation_id: str = Field(min_length=1, max_length=64)
    created_at: AwareDatetime


class Evidence(Model):
    schema_version: Literal[1] = 1
    id: ResourceId
    tenant_id: OpaqueId
    job_id: ResourceId
    sha256: Hash
    storage_ref: OpaqueId
    size_bytes: Annotated[StrictInt, Field(ge=0, le=100_000_000)]
    media_type: str = Field(min_length=1,max_length=128)
    created_at: AwareDatetime


class Finding(Model):
    schema_version: Literal[1] = 1
    id: ResourceId
    tenant_id: OpaqueId
    job_id: ResourceId
    fingerprint: Hash
    rule_id: str = Field(min_length=1, max_length=200)
    tool_id: OpaqueId
    tool_version: str = Field(min_length=1, max_length=100)
    severity: Literal['info','low','medium','high','critical','unknown']
    title: str = Field(min_length=1, max_length=300)
    evidence_ids: list[ResourceId] = Field(default_factory=list,max_length=100)
    state: Literal['unverified','confirmed','false_positive','resolved'] = 'unverified'


class Approval(Model):
    schema_version: Literal[1] = 1
    id: ResourceId
    tenant_id: OpaqueId
    proposal_hash: Hash
    actor_id: OpaqueId
    expires_at: AwareDatetime
    state: Literal['approved','revoked','expired']


class BudgetReservation(Model):
    """Wire contract only; reservation ledger/enforcement belongs to D6P6."""
    schema_version: Literal[1] = 1
    id: ResourceId
    tenant_id: OpaqueId
    job_id: ResourceId
    amount_cents: Cents
    state: Literal['reserved','settled','released','reconciliation_required']
    idempotency_key: OpaqueId
    revision: Annotated[StrictInt, Field(ge=0)] = 0
