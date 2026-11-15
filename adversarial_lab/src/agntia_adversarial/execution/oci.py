"""OCI sandbox: pinned digest, no network, read-only root, dropped capabilities.

The runtime is never assumed. Without a verified binary the sandbox returns BLOCKED.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Sequence

DIGEST = re.compile(r"@sha256:[a-f0-9]{64}$")


class SandboxError(RuntimeError):
    pass


@dataclass(frozen=True)
class RuntimeSpec:
    image: str
    runtime: str = "docker"
    memory: str = "512m"
    pids_limit: int = 128
    timeout_seconds: int = 60
    workspace: str = "/work"

    def validate(self) -> None:
        if not DIGEST.search(self.image):
            raise SandboxError("image must be pinned by @sha256 digest")
        if not re.fullmatch(r"\d+[mg]", self.memory):
            raise SandboxError("memory must look like 256m or 1g")
        if not 8 <= self.pids_limit <= 512:
            raise SandboxError("pids_limit out of bounds")


@dataclass
class OCISandbox:
    spec: RuntimeSpec
    runner: Callable[[Sequence[str]], dict] | None = None
    audit: list[list[str]] = field(default_factory=list)

    def available(self) -> bool:
        return self.runner is not None or shutil.which(self.spec.runtime) is not None

    def command(self, argv: Sequence[str], mount: Path | None = None) -> list[str]:
        self.spec.validate()
        if not argv:
            raise SandboxError("empty argv")
        command = [
            self.spec.runtime,
            "run",
            "--rm",
            "--network=none",
            "--read-only",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges",
            f"--pids-limit={self.spec.pids_limit}",
            f"--memory={self.spec.memory}",
            "--tmpfs=/tmp:rw,noexec,nosuid,size=64m",
            "-w",
            self.spec.workspace,
        ]
        if mount is not None:
            command += ["-v", f"{Path(mount).resolve()}:{self.spec.workspace}:ro"]
        command += [self.spec.image, *argv]
        return command

    def run(self, argv: Sequence[str], mount: Path | None = None) -> dict[str, object]:
        command = self.command(argv, mount)
        self.audit.append(command)
        if not self.available():
            return {"status": "BLOCKED", "reason": f"OCI runtime missing: {self.spec.runtime}"}
        if self.runner is not None:
            result = self.runner(command)
            return {
                "status": "PASS" if result.get("returncode", 1) == 0 else "FAIL",
                "exit": result.get("returncode"),
                "stdout": str(result.get("stdout", ""))[:65536],
                "stderr": str(result.get("stderr", ""))[:65536],
            }
        completed = subprocess.run(
            list(command), capture_output=True, timeout=self.spec.timeout_seconds, check=False
        )
        return {
            "status": "PASS" if completed.returncode == 0 else "FAIL",
            "exit": completed.returncode,
            "stdout": completed.stdout[:65536].decode("utf-8", "replace"),
            "stderr": completed.stderr[:65536].decode("utf-8", "replace"),
        }
