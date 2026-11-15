"""Fail-closed configuration for the adversarial lab."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes"}


@dataclass(frozen=True)
class LabConfig:
    data_dir: Path
    allow_network: bool = False
    allow_subprocess_providers: bool = False
    max_evidence_bytes: int = 2 * 1024 * 1024
    default_budget_cents: int = 100
    max_runs_per_day: int = 5

    @classmethod
    def from_env(cls) -> "LabConfig":
        return cls(
            data_dir=Path(os.environ.get("ADVLAB_DATA_DIR", "./adversarial_lab/var")),
            allow_network=_flag("ADVLAB_ALLOW_NETWORK"),
            allow_subprocess_providers=_flag("ADVLAB_ALLOW_SUBPROCESS_PROVIDERS"),
            max_evidence_bytes=int(os.environ.get("ADVLAB_MAX_EVIDENCE_BYTES", "2097152")),
            default_budget_cents=int(os.environ.get("ADVLAB_BUDGET_CENTS", "100")),
            max_runs_per_day=int(os.environ.get("ADVLAB_MAX_RUNS_PER_DAY", "5")),
        )

    def validate(self) -> None:
        if self.allow_network:
            raise ValueError("network egress must stay disabled for lab v1")
        if self.max_evidence_bytes <= 0:
            raise ValueError("max_evidence_bytes must be positive")
