"""Coding agents are interchangeable workers, never authorities."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class ProviderBlocked(RuntimeError):
    """Raised when the provider needs an API, binary or license we do not have."""


class ProviderResult(BaseModel):
    status: str
    summary: str
    actions: list[str] = Field(default_factory=list)
    observations: list[dict[str, object]] = Field(default_factory=list)


@runtime_checkable
class Provider(Protocol):
    name: str
    capabilities: set[str]

    def plan(self, experiment_id: str, hypotheses: list[str]) -> list[str]: ...

    def execute(self, experiment_id: str, plan: list[str]) -> ProviderResult: ...

    def observe(self, experiment_id: str) -> list[dict[str, object]]: ...

    def report(self, experiment_id: str) -> dict[str, object]: ...
