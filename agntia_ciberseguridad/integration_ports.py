"""Fail-closed provider boundary for the AgntiaPro cyber vertical slices.

Configuration is a declaration, not evidence that a provider is connected.
No credentials are accepted or serialized by this module.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class ConnectorState(str, Enum):
    DISABLED = "DISABLED"
    MISSING_CONFIG = "MISSING_CONFIG"
    CONFIGURED_UNVERIFIED = "CONFIGURED_UNVERIFIED"
    VERIFIED_SANDBOX = "VERIFIED_SANDBOX"
    VERIFIED_PRODUCTION = "VERIFIED_PRODUCTION"


class ConnectorUnavailable(RuntimeError):
    def __init__(self, code: str, provider: str):
        self.code = code
        self.provider = provider
        super().__init__(f"{provider}: {code}")


@dataclass(frozen=True)
class ConnectorSpec:
    provider: str
    enabled: bool = False
    secret_ref: str | None = None
    verified_environment: str | None = None

    def __post_init__(self):
        if not self.provider or not self.provider.replace("_", "").isalnum():
            raise ValueError("Invalid provider identifier")
        if self.secret_ref is not None and (
            not self.secret_ref.startswith("CYBER_")
            or not self.secret_ref.isascii()
            or not self.secret_ref.replace("_", "").isalnum()
            or self.secret_ref.upper() != self.secret_ref
        ):
            raise ValueError("Secret reference must be an environment variable name")
        if self.verified_environment not in (None, "sandbox", "production"):
            raise ValueError("Unknown verification environment")
        if self.verified_environment and not self.enabled:
            raise ValueError("Disabled connector cannot be verified")
        if self.verified_environment and not self.secret_ref:
            raise ValueError("Verification requires a secret reference")

    @property
    def state(self) -> ConnectorState:
        if not self.enabled:
            return ConnectorState.DISABLED
        if not self.secret_ref:
            return ConnectorState.MISSING_CONFIG
        if self.verified_environment == "sandbox":
            return ConnectorState.VERIFIED_SANDBOX
        if self.verified_environment == "production":
            return ConnectorState.VERIFIED_PRODUCTION
        return ConnectorState.CONFIGURED_UNVERIFIED


class ConnectorPort(Generic[T]):
    """Explicitly injected adapter; no automatic fallback to network access."""

    def __init__(self, spec: ConnectorSpec, operation: Callable[..., T] | None = None):
        self.spec = spec
        self._operation = operation

    def execute(self, *args, **kwargs) -> T:
        if self.spec.state not in (
            ConnectorState.VERIFIED_SANDBOX,
            ConnectorState.VERIFIED_PRODUCTION,
        ) or self._operation is None:
            raise ConnectorUnavailable("PROVIDER_NOT_CONFIGURED", self.spec.provider)
        return self._operation(*args, **kwargs)
