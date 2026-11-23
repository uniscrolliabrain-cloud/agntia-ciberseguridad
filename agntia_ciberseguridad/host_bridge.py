"""Strict host-to-child identity boundary. No LLM-originated identity is trusted.

Host verification (signature/session/RLS) MUST occur in the parent before calling
this pure adapter. This module cannot attest the parent has done so.
"""
from dataclasses import dataclass
from typing import Literal
from .errors import reject

_ALLOWED = frozenset({"assets.read", "findings.read", "jobs.read", "reports.read"})


@dataclass(frozen=True)
class HostIdentity:
    tenant_id: str
    principal_binding_id: str
    host_actor_id: str
    assurance: Literal["verified_host"]
    correlation_id: str

    def __post_init__(self):
        for value in (self.tenant_id, self.principal_binding_id,
                      self.host_actor_id, self.correlation_id):
            if not isinstance(value, str) or not value or len(value) > 128:
                raise ValueError("Invalid host identity field")
        if self.assurance != "verified_host":
            raise ValueError("Host identity must be verified upstream")


def resolve_host_read(service, identity: HostIdentity | None, capability: str):
    """Return a current child principal only if both identities and scope agree.

    The parent must construct HostIdentity from its authenticated server context,
    never from a chat payload or a client-supplied header alone.
    """
    if identity is None:
        reject("HOST_IDENTITY_NOT_CONFIGURED", "Host identity is required", 424)
    if not isinstance(identity, HostIdentity):
        reject("HOST_IDENTITY_NOT_CONFIGURED", "Host identity is invalid", 424)
    if capability not in _ALLOWED:
        reject("forbidden", "Host bridge only permits read capabilities", 403)
    principal = service.auth.current(identity.principal_binding_id)
    if principal.actor_id != identity.host_actor_id:
        reject("HOST_IDENTITY_MISMATCH", "Host and child principal differ", 403)
    service.authorize(principal, identity.tenant_id, capability)
    return principal
