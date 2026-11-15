"""Deterministic hashing so evidence and reports can be reproduced."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable


def canonical_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(paths: Iterable[Path], base: Path | None = None) -> dict[str, object]:
    entries = []
    for path in sorted(paths):
        label = str(path.relative_to(base)) if base is not None else str(path)
        entries.append(
            {
                "path": label,
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
        )
    return {
        "schema_version": 1,
        "algorithm": "sha256",
        "files": entries,
        "digest": sha256_bytes(canonical_json(entries).encode("utf-8")),
    }
