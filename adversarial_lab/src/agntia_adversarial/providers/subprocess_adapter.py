"""Generic CLI bridge. Disabled by default: an arbitrary binary is not a trust boundary."""

from __future__ import annotations

from .base import ProviderBlocked, ProviderResult


class SubprocessProvider:
    name = "subprocess"
    capabilities: set[str] = set()

    def __init__(self, executable: str, allow: bool = False) -> None:
        self.executable = executable
        self.allow = allow

    def _guard(self) -> None:
        if not self.allow:
            raise ProviderBlocked(
                "subprocess provider disabled: set ADVLAB_ALLOW_SUBPROCESS_PROVIDERS only after "
                "verifying binary, license and isolation"
            )

    def plan(self, experiment_id: str, hypotheses: list[str]) -> list[str]:
        self._guard()
        return []

    def execute(self, experiment_id: str, plan: list[str]) -> ProviderResult:
        self._guard()
        raise ProviderBlocked("subprocess execution not implemented in lab v1")
