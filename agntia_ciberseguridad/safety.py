"""Fail-closed release posture, independent of LLM arguments or phase percentages."""
from dataclasses import dataclass
from .errors import reject

@dataclass(frozen=True)
class ReleaseGates:
    independent_review_verified: bool=False
    sandbox_verified: bool=False
    identity_worker_verified: bool=False

    def require_customer_execution(self):
        if not (self.independent_review_verified and self.sandbox_verified and self.identity_worker_verified):
            reject('release_gate_blocked','Ejecución de clientes deshabilitada hasta verificar revisión, sandbox e identidad de worker',424)
