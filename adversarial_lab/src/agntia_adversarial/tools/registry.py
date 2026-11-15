"""Closed catalog: nothing outside this registry can be invoked."""

from __future__ import annotations

from .base import ToolAdapter


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolAdapter] = {}

    def register(self, adapter: ToolAdapter) -> None:
        self._tools[adapter.name] = adapter

    def get(self, name: str) -> ToolAdapter:
        if name not in self._tools:
            raise KeyError(f"tool not in closed catalog: {name}")
        return self._tools[name]

    def catalog(self) -> dict[str, str]:
        return {name: adapter.capability for name, adapter in self._tools.items()}

    def status(self) -> dict[str, str]:
        return {
            name: ("AVAILABLE" if adapter.available() else "BLOCKED")
            for name, adapter in self._tools.items()
        }


def default_catalog() -> ToolRegistry:
    from .faults import FaultInjector
    from .fuzz import FuzzProbe
    from .garak import GarakAdapter
    from .osv import OsvAdapter
    from .pyrit import PyritAdapter
    from .schemathesis import SchemathesisAdapter
    from .semgrep import SemgrepAdapter
    from .syft import SyftAdapter
    from .zap import ZapAdapter

    registry = ToolRegistry()
    for adapter in (
        SemgrepAdapter(),
        OsvAdapter(),
        SyftAdapter(),
        SchemathesisAdapter(),
        ZapAdapter(),
        PyritAdapter(),
        GarakAdapter(),
        FuzzProbe(),
        FaultInjector(),
    ):
        registry.register(adapter)
    return registry
