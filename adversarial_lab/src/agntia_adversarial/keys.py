"""Internal keys: generated locally, stored 0600, never printed.

These are lab-owned keys (evidence encryption, release manifest signing). External provider
credentials are not handled here: they arrive from the environment or a secret manager.
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

NAME = re.compile(r"^[a-z][a-z0-9-]{1,31}$")


class KeyFormatError(RuntimeError):
    pass


class KeyRing:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def path(self, name: str) -> Path:
        if not NAME.match(name):
            raise KeyFormatError(f"invalid key name: {name}")
        return self.root / f"{name}.key"

    def ensure(self, name: str, size: int = 32) -> bytes:
        path = self.path(name)
        if path.exists():
            data = path.read_bytes()
            if len(data) != size:
                raise KeyFormatError(f"key {name} has unexpected size")
            path.chmod(0o600)
            return data
        self.root.mkdir(parents=True, exist_ok=True)
        data = os.urandom(size)
        path.write_bytes(data)
        path.chmod(0o600)
        return data

    def fingerprint(self, name: str) -> str:
        return hashlib.sha256(self.path(name).read_bytes()).hexdigest()[:16]

    def rotate(self, name: str, size: int = 32) -> str:
        path = self.path(name)
        if path.exists():
            path.replace(path.with_suffix(".key.old"))
        self.ensure(name, size)
        return self.fingerprint(name)

    def describe(self) -> dict[str, dict[str, object]]:
        if not self.root.exists():
            return {}
        described: dict[str, dict[str, object]] = {}
        for path in sorted(self.root.glob("*.key")):
            mode = oct(path.stat().st_mode & 0o777)
            described[path.stem] = {
                "path": str(path),
                "bytes": path.stat().st_size,
                "mode": mode,
                "fingerprint": hashlib.sha256(path.read_bytes()).hexdigest()[:16],
            }
        return described
