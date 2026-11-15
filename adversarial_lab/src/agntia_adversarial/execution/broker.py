"""Deterministic broker: every tool call is allowlisted, authorized and metered."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Sequence

from ..contracts.experiment import ExperimentSpec
from .sandbox import Sandbox


class BrokerError(RuntimeError):
    pass


@dataclass
class Broker:
    experiment: ExperimentSpec
    catalog: Dict[str, str]
    sandbox: Sandbox
    calls: int = 0
    spent_cents: int = 0
    history: list[dict[str, object]] = field(default_factory=list)

    def _check(self, tool: str, capability: str) -> None:
        if tool not in self.catalog:
            raise BrokerError(f"tool not in catalog: {tool}")
        if not self.experiment.requires(capability):
            raise BrokerError(f"capability not granted: {capability}")
        if self.calls >= self.experiment.limits.max_requests:
            raise BrokerError("request budget exhausted")
        if self.spent_cents > self.experiment.limits.max_cost_cents:
            raise BrokerError("cost budget exhausted")

    def invoke(self, tool: str, capability: str, argv: Sequence[str], cost_cents: int = 1) -> dict[str, object]:
        self._check(tool, capability)
        self.calls += 1
        self.spent_cents += cost_cents
        result = self.sandbox.run(argv)
        record = {"tool": tool, "argv": list(argv), "cost_cents": cost_cents, **result}
        self.history.append(record)
        return record
