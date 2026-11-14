"""Stable public failures; internal/provider exception strings are never exposed."""
from uuid import uuid4


class DomainError(Exception):
    def __init__(self, code: str, message: str, status: int = 400, *, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.retryable = retryable

    def public(self, correlation_id: str | None = None) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "correlation_id": correlation_id or str(uuid4()),
            "retryable": self.retryable,
            "reconciliation_required": False,
        }


def reject(code: str, message: str, status: int = 400, *, retryable: bool = False):
    raise DomainError(code, message, status, retryable=retryable)


def not_found():
    reject("not_found", "Recurso no encontrado", 404)
