"""Provider registry. Unverified providers are listed as BLOCKED, not used."""

from __future__ import annotations

from .base import Provider, ProviderBlocked
from .mock import MockProvider


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}

    def register(self, provider: Provider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> Provider:
        if name not in self._providers:
            raise ProviderBlocked(f"provider not configured: {name}")
        return self._providers[name]

    def available(self) -> list[str]:
        return sorted(self._providers)

    def status(self) -> dict[str, str]:
        status = {name: "AVAILABLE" for name in self._providers}
        for name in ("codex", "antigravity", "cline", "freebuff"):
            status.setdefault(name, "BLOCKED: no verified API/CLI contract")
        return status


def default_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register(MockProvider())
    return registry
