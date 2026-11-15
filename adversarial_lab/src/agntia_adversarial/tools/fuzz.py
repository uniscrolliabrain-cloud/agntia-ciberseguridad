"""Deterministic fuzzing of a pure function: no FFI, no network, no shell."""

from __future__ import annotations

import random
import string
from typing import Callable

from .base import ToolResult, ToolAdapter


class FuzzProbe(ToolAdapter):
    name = "fuzz"
    binary = ""
    capability = "sandbox.test"

    def available(self) -> bool:
        return True

    def probe(self, function: Callable[[str], object], iterations: int = 100, seed: int = 3) -> ToolResult:
        rng = random.Random(seed)
        failures: list[str] = []
        alphabet = string.ascii_letters + string.digits + "{}[]<>'\";:/-_ \x00"
        for _ in range(iterations):
            payload = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 40)))
            try:
                function(payload)
            except ValueError:
                continue
            except Exception as error:  # noqa: BLE001 - unexpected crash is the finding
                failures.append(f"{type(error).__name__}: {payload[:20]!r}")
        return ToolResult(
            tool=self.name,
            status="FAIL" if failures else "PASS",
            reason="unexpected exception" if failures else "no unexpected exception",
            metadata={"iterations": iterations, "failures": failures[:5]},
        )
