"""Local sandbox: argv-only execution, allowlisted binaries, bounded output."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Sequence


class SandboxError(RuntimeError):
    pass


class Sandbox:
    def __init__(self, allowlist: Sequence[str], timeout_seconds: int = 60, max_output: int = 65536) -> None:
        self.allowlist = set(allowlist)
        self.timeout_seconds = timeout_seconds
        self.max_output = max_output

    def __enter__(self) -> "Sandbox":
        self._tmp = tempfile.TemporaryDirectory(prefix="advlab-")
        self.root = Path(self._tmp.name)
        return self

    def __exit__(self, *exc: object) -> None:
        self._tmp.cleanup()

    def available(self, binary: str) -> bool:
        return binary in self.allowlist and shutil.which(binary) is not None

    def run(self, argv: Sequence[str], cwd: Path | None = None) -> dict[str, object]:
        if not argv:
            raise SandboxError("empty argv")
        binary = argv[0]
        if binary not in self.allowlist:
            raise SandboxError(f"binary not allowed: {binary}")
        if shutil.which(binary) is None:
            return {"status": "BLOCKED", "reason": f"binary missing: {binary}", "exit": None}
        try:
            completed = subprocess.run(
                list(argv),
                cwd=str(cwd or self.root),
                shell=False,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
                env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(self.root)},
            )
        except subprocess.TimeoutExpired:
            return {"status": "FAIL", "reason": "timeout", "exit": None}
        return {
            "status": "PASS" if completed.returncode == 0 else "FAIL",
            "exit": completed.returncode,
            "stdout": completed.stdout[: self.max_output].decode("utf-8", "replace"),
            "stderr": completed.stderr[: self.max_output].decode("utf-8", "replace"),
        }
