"""Explicit principal binding; no local-owner or role-from-prompt fallback."""
import hashlib
import hmac
import os
from dataclasses import dataclass

from .config import Settings
from .contracts import Role
from .errors import not_found, reject
from .util import utcnow

READ = frozenset({"assets.read", "grants.read", "audits.preview", "audit.read", "jobs.read", "findings.read", "evidence.read", "reports.read", "risk.read", "logs.read", "events.read", "agents.read"})
ROLE_CAPABILITIES = {
    Role.viewer: READ - {"audits.preview"},
    Role.analyst: READ | {"assets.register", "grants.propose", "jobs.submit", "jobs.cancel", "evidence.create", "reviews.propose", "reports.create"},
    Role.operator: READ | {"assets.register", "grants.propose", "jobs.submit", "jobs.cancel", "evidence.create", "reviews.propose", "reports.create"},
    Role.reviewer: READ | {"assets.register", "grants.propose", "grants.approve", "grants.revoke", "jobs.submit", "jobs.cancel", "jobs.reconcile", "evidence.create", "evidence.original", "evidence.manage", "evidence.review", "reviews.propose", "reviews.approve", "reports.create", "logs.manage", "events.ack", "agents.manage", "agents.delegate"},
    Role.owner: READ | {"assets.register", "grants.propose", "grants.approve", "grants.revoke", "jobs.submit", "jobs.cancel", "jobs.reconcile", "evidence.create", "evidence.original", "evidence.manage", "evidence.review", "reviews.propose", "reviews.approve", "reports.create", "logs.manage", "events.ack", "agents.manage", "agents.delegate"},
}


@dataclass(frozen=True)
class Principal:
    binding_id: str
    actor_id: str
    role: Role
    tenants: tuple[str, ...]
    credential_fingerprint: str


class Authenticator:
    def __init__(self, settings: Settings):
        self.settings = settings

    def current(self, binding_id: str) -> Principal:
        candidates = [p for p in self.settings.principals if p.id == binding_id]
        if len(candidates) != 1:
            reject("principal_revoked", "Principal no disponible", 403)
        p = candidates[0]
        if not p.enabled or (p.expires_at and p.expires_at <= utcnow()):
            reject("principal_revoked", "Principal no disponible", 403)
        value = os.getenv(p.token_env, "")
        if not 24 <= len(value) <= 512:
            reject("principal_revoked", "Principal no disponible", 403)
        return Principal(p.id, p.actor_id, p.role, tuple(p.tenants), hashlib.sha256(value.encode()).hexdigest())

    def authenticate(self, header: str | None) -> Principal:
        if not header or not header.startswith("Bearer ") or not 24 <= len(header[7:]) <= 512:
            reject("auth", "Autenticación necesaria", 401)
        supplied = hashlib.sha256(header[7:].encode()).hexdigest()
        matches = []
        for p in self.settings.principals:
            try:
                candidate = self.current(p.id)
            except Exception as exc:
                from .errors import DomainError
                if not isinstance(exc, DomainError):
                    raise
                continue
            if hmac.compare_digest(supplied, candidate.credential_fingerprint):
                matches.append(candidate)
        if len(matches) != 1:
            reject("auth", "Autenticación necesaria", 401)
        return matches[0]

    def authorize(self, principal: Principal, tenant: str, capability: str) -> Principal:
        if self.current(principal.binding_id) != principal:
            reject("principal_revoked", "Principal revocado o modificado", 403)
        if tenant not in principal.tenants:
            not_found()
        if capability not in ROLE_CAPABILITIES[principal.role]:
            reject("forbidden", "Capacidad no autorizada", 403)
        return principal


def require_human(service,actor,tenant,capability):
    service.authorize(actor,tenant,capability)
    binding=next(p for p in service.settings.principals if p.id==actor.binding_id)
    if binding.kind!='human':reject('human_required','Se requiere un principal humano autorizado',403)
