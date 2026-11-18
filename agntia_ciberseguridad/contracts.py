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
    # Same vocabulary as jobs/store.py and the SDK; 'succeeded' never existed at runtime.
    state: Literal['pending','running','completed','partial','failed','cancelled','blocked','reconciliation_required']
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


# One vocabulary for one fact: a second copy of this enum is a second place to drift.
Exposure = Literal['unknown','internal','public','restricted']


class FindingContext(Model):
    exposure: Exposure
    sensitivity: Literal['unknown','ordinary','sensitive']
    source: Literal['human_declared']
    evidence_ids: list[ResourceId] = Field(default_factory=list, max_length=100)


class FindingException(Model):
    expires_at: AwareDatetime | None = None
    evidence_ids: list[ResourceId] = Field(default_factory=list, max_length=100)
    proposal_id: ResourceId


class RiskIntelligence(Model):
    kev: Literal['unknown'] = 'unknown'
    epss: float | None = None
    cvss: float | None = None
    source_date: str | None = None


class FindingRisk(Model):
    policy_version: Literal['triage-v1']
    score: StrictInt | None = None
    priority: Literal['P0', 'P1', 'P2', 'P3', 'needs_context']
    context_complete: bool
    exposure: Exposure
    exploitation: Literal['unknown'] = 'unknown'
    intelligence: RiskIntelligence
    # Bounded label, not free text: a provider string must never become the field value.
    source: str = Field(min_length=1, max_length=100, pattern=r'^[a-z][a-z0-9_]{0,99}$')


class Finding(Model):
    """Current projection returned by findings.list/history after triage."""
    schema_version: Literal[1] = 1
    id: Hash
    asset_id: ResourceId
    tool: Literal['gitleaks', 'osv', 'semgrep', 'trivy']
    rule_id: str = Field(min_length=1, max_length=200)
    path: str = Field(min_length=1, max_length=512)
    revision: StrictInt = Field(ge=0)
    state: Literal['suspected', 'confirmed', 'false_positive', 'remediated', 'verified_fixed', 'accepted_risk', 'suppressed']
    severity: Literal['info', 'low', 'medium', 'high', 'critical', 'unknown']
    confidence: Literal['tool_reported', 'unknown']
    first_seen: AwareDatetime
    last_seen: AwareDatetime
    observation_count: StrictInt = Field(ge=1)
    reappeared: bool
    last_job_id: ResourceId
    last_snapshot_id: ResourceId
    relation_id: Hash | None = None
    exposure: Exposure = 'unknown'
    exception: FindingException | None = None
    context: FindingContext | None = None
    exception_expired: bool
    risk: FindingRisk
    reviewed_at: AwareDatetime | None = None
    reviewed_by: OpaqueId | None = None
    last_decision_id: ResourceId | None = None
    owner_ref: OpaqueId | None = None
    due_at: AwareDatetime | None = None


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
