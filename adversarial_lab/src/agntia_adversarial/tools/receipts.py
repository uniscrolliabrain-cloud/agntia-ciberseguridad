"""Receipts bind a tool invocation to its arguments and output hash."""

from __future__ import annotations

from ..provenance.manifest import canonical_json, sha256_bytes
from .base import ToolResult


def build_receipt(result: ToolResult, argv: list[str]) -> dict[str, object]:
    body = {
        "tool": result.tool,
        "status": result.status,
        "exit": result.exit,
        "argv": argv,
        "stdout_sha256": sha256_bytes(result.stdout.encode("utf-8")),
        "stderr_sha256": sha256_bytes(result.stderr.encode("utf-8")),
    }
    return {**body, "receipt_sha256": sha256_bytes(canonical_json(body).encode("utf-8"))}
