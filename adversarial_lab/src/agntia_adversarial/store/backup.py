"""Backup and restore for the lab database and evidence vault.

Backups are verified file by file before restore. A corrupt copy is refused, not partially applied.
"""

from __future__ import annotations

import json
import shutil
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

from ..provenance.manifest import sha256_file


class BackupCorrupt(RuntimeError):
    pass


def _files(root: Path) -> dict[str, dict[str, object]]:
    manifest: dict[str, dict[str, object]] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "manifest.json":
            continue
        manifest[str(path.relative_to(root))] = {
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
    return manifest


def backup(store_path: Path, evidence_root: Path, destination: Path) -> dict[str, object]:
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / "lab.sqlite"
    source = sqlite3.connect(store_path)
    try:
        sink = sqlite3.connect(target)
        try:
            source.backup(sink)
        finally:
            sink.close()
    finally:
        source.close()
    evidence_root = Path(evidence_root)
    if evidence_root.exists():
        shutil.copytree(evidence_root, destination / "evidence", dirs_exist_ok=True)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": _files(destination),
    }
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def restore(destination: Path, store_path: Path, evidence_root: Path) -> dict[str, object]:
    destination = Path(destination)
    manifest_path = destination / "manifest.json"
    if not manifest_path.is_file():
        raise BackupCorrupt("manifest missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    started = time.monotonic()
    for relative, expected in manifest["files"].items():
        path = destination / relative
        if not path.is_file():
            raise BackupCorrupt(f"missing file: {relative}")
        if sha256_file(path) != expected["sha256"]:
            raise BackupCorrupt(f"hash mismatch: {relative}")
    store_path = Path(store_path)
    store_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(destination / "lab.sqlite", store_path)
    evidence = destination / "evidence"
    if evidence.exists():
        Path(evidence_root).mkdir(parents=True, exist_ok=True)
        shutil.copytree(evidence, evidence_root, dirs_exist_ok=True)
    return {
        "files_verified": len(manifest["files"]),
        "rto_ms_measured": round((time.monotonic() - started) * 1000, 3),
        "created_at": manifest["created_at"],
    }
