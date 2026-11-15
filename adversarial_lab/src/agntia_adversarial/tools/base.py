"""Tool adapters: closed catalog, argv-only, honest BLOCKED when unavailable."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from typing import Sequence

from ..execution.sandbox import Sandbox


@dataclass
class ToolResult:
    tool: str
    status: str
    exit: int | None = None
    stdout: str = ""
    stderr: str = ""
    reason: str = ""
    metadata: dict[str, object] = field(default_factory=dict)


class ToolAdapter:
    name = "tool"
    binary = ""
    capability = "sandbox.test"

    def available(self) -> bool:
        return bool(self.binary) and shutil.which(self.binary) is not None

    def run(self, sandbox: Sandbox, argv: Sequence[str]) -> ToolResult:
        if not self.available():
            return ToolResult(
                tool=self.name,
                status="BLOCKED",
                reason=f"binary not installed or not verified: {self.binary or 'n/a'}",
            )
        result = sandbox.run([self.binary, *argv])
        return ToolResult(
            tool=self.name,
            status=str(result.get("status", "FAIL")),
            exit=result.get("exit"),  # type: ignore[arg-type]
            stdout=str(result.get("stdout", "")),
            stderr=str(result.get("stderr", "")),
            reason=str(result.get("reason", "")),
        )
