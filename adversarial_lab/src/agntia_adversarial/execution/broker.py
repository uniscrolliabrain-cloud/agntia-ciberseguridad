"""Broker guards: revocation, deadline, idempotency and bounded output."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Sequence

from ..contracts.experiment import ExperimentSpec
from .sandbox import Sandbox


class BrokerError(RuntimeError):
    pass


@dataclass
class Broker:
    experiment: ExperimentSpec
    catalog: dict[str, str]
    sandbox: Sandbox
    authorize: Callable[[], bool] | None = None
    deadline: datetime | None = None
    max_output: int = 65536
    calls: int = 0
    spent_cents: int = 0
    history: list[dict[str, object]] = field(default_factory=list)
    receipts: dict[str, dict[str, object]] = field(default_factory=dict)

    def _authorized(self) -> None:
        if self.authorize is not None and not self.authorize():
            raise BrokerError("engagement revoked or expired")
        if self.deadline is not None and datetime.now(timezone.utc) >= self.deadline:
            raise BrokerError("authorization window closed")

    def _check(self, tool: str, capability: str) -> None:
        if tool not in self.catalog:
            raise BrokerError(f"tool not in catalog: {tool}")
        if not self.experiment.requires(capability):
            raise BrokerError(f"capability not granted: {capability}")
        if self.calls >= self.experiment.limits.max_requests:
            raise BrokerError("request budget exhausted")
        if self.spent_cents > self.experiment.limits.max_cost_cents:
            raise BrokerError("cost budget exhausted")

    def invoke(
        self,
        tool: str,
        capability: str,
        argv: Sequence[str],
        cost_cents: int = 1,
        idempotency_key: str | None = None,
    ) -> dict[str, object]:
        self._authorized()
        if idempotency_key is not None and idempotency_key in self.receipts:
            cached = dict(self.receipts[idempotency_key])
            cached["deduplicated"] = True
            return cached
        self._check(tool, capability)
        self.calls += 1
        self.spent_cents += cost_cents
        result = self.sandbox.run(argv)
        for stream in ("stdout", "stderr"):
            if isinstance(result.get(stream), str) and len(result[stream]) > self.max_output:
                result[stream] = result[stream][: self.max_output] + "\n[truncated]"
        record = {"tool": tool, "argv": list(argv), "cost_cents": cost_cents, "calls": self.calls, **result}
        self.history.append(record)
        if idempotency_key is not None:
            self.receipts[idempotency_key] = dict(record)
        return record
