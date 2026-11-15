"""Deterministic provider for offline execution. It never calls a model."""

from __future__ import annotations

from .base import ProviderResult


class MockProvider:
    name = "mock"
    capabilities = {"plan", "execute", "observe", "report"}

    def plan(self, experiment_id: str, hypotheses: list[str]) -> list[str]:
        return [f"{experiment_id}:{index}:verify" for index, _ in enumerate(hypotheses, start=1)]

    def execute(self, experiment_id: str, plan: list[str]) -> ProviderResult:
        return ProviderResult(
            status="PARTIAL",
            summary=f"mock provider executed {len(plan)} steps without model access",
            actions=list(plan),
        )

    def observe(self, experiment_id: str) -> list[dict[str, object]]:
        return [{"kind": "provider_limit", "detail": "mock provider: no model invoked"}]

    def report(self, experiment_id: str) -> dict[str, object]:
        return {"experiment_id": experiment_id, "provider": self.name, "model_calls": 0}
