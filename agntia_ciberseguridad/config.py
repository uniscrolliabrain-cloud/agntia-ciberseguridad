"""Server-admin configuration: references only; token values stay in the environment."""
import json
import os
from pathlib import Path
from typing import Annotated

from pydantic import AwareDatetime, ConfigDict, Field, StrictInt, field_validator, model_validator

from .contracts import AssetKind, Model, OpaqueId, Profile, Role

EnvRef = Annotated[str, Field(pattern=r"^[A-Z][A-Z0-9_]{2,100}$")]


class PrincipalBinding(Model):
    id: OpaqueId
    actor_id: OpaqueId
    role: Role
    tenants: list[OpaqueId] = Field(min_length=1, max_length=100)
    token_env: EnvRef
    expires_at: AwareDatetime | None = None
    enabled: bool = True

    @field_validator("tenants")
    @classmethod
    def unique(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Duplicate tenant binding")
        return value


class TargetConfig(Model):
    tenant_id: OpaqueId
    kind: AssetKind
    location: str = Field(min_length=1, max_length=2048)
    allowed_networks: list[str] = Field(default_factory=list, max_length=32)
    allowed_ports: list[Annotated[StrictInt, Field(ge=1, le=65535)]] = Field(default_factory=lambda: [443], max_length=10)
    allowed_path_prefixes: list[str] = Field(default_factory=list, max_length=32)
    allow_insecure_lab: bool = False
    allow_loopback_lab: bool = False


class ConsentConfig(Model):
    tenant_id: OpaqueId
    target_refs: list[OpaqueId] = Field(min_length=1, max_length=100)
    profiles: list[Profile] = Field(min_length=1, max_length=3)
    evidence_ref: str = Field(min_length=5, max_length=160)
    emergency_contact_ref: OpaqueId | None = None
    authority_actor_id: OpaqueId
    starts_at: AwareDatetime
    expires_at: AwareDatetime
    max_requests: Annotated[StrictInt, Field(ge=1, le=10_000)] = 100
    max_cost_cents: Annotated[StrictInt, Field(ge=0, le=30_000)] = 0

    @model_validator(mode="after")
    def interval(self):
        if self.starts_at >= self.expires_at:
            raise ValueError("Invalid consent interval")
        return self


class Settings(Model):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=False)
    data_dir: Path
    principals: list[PrincipalBinding] = Field(min_length=1, max_length=1000)
    targets: dict[OpaqueId, TargetConfig] = Field(default_factory=dict)
    consents: dict[OpaqueId, ConsentConfig] = Field(default_factory=dict)
    approved_workspace_roots: list[Path] = Field(default_factory=list, max_length=32)
    lab_mode: bool = False
    max_request_bytes: Annotated[StrictInt, Field(ge=1024, le=1024 * 1024)] = 64 * 1024
    db_timeout_seconds: float = Field(default=1.0, ge=0.05, le=10)

    @model_validator(mode="after")
    def bindings(self):
        for field in ("id", "actor_id", "token_env"):
            values = [getattr(p, field) for p in self.principals]
            if len(values) != len(set(values)):
                raise ValueError("Ambiguous principal registry")
        tenants = {t for p in self.principals for t in p.tenants}
        for target in self.targets.values():
            if target.tenant_id not in tenants:
                raise ValueError("Target has no provisioned tenant")
            if target.kind == AssetKind.web and not target.allowed_networks:
                raise ValueError("Network targets require approved networks")
        for consent in self.consents.values():
            owners = [p for p in self.principals if p.actor_id == consent.authority_actor_id and p.role in (Role.owner, Role.reviewer) and consent.tenant_id in p.tenants]
            if len(owners) != 1:
                raise ValueError("Consent authority not provisioned")
            for ref in consent.target_refs:
                if ref not in self.targets or self.targets[ref].tenant_id != consent.tenant_id:
                    raise ValueError("Consent target scope differs")
        return self

    @classmethod
    def from_env(cls):
        # No implicit owner, default token, secret value or dynamic URL is accepted.
        ref = os.getenv("AGNTIA_CYBER_CONFIG_FILE", "")
        if not ref:
            raise ValueError("AGNTIA_CYBER_CONFIG_FILE must reference server configuration")
        try:
            return cls.model_validate_json(Path(ref).read_text())
        except Exception:
            raise ValueError("Invalid server configuration") from None
