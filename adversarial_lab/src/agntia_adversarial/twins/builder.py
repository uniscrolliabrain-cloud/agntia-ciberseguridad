"""Build a synthetic twin on disk. No cloning of real systems."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ..provenance.manifest import build_manifest
from .synthetic import generate_orders, generate_users


@dataclass
class Twin:
    root: Path
    manifest: dict[str, object]


def build_twin(root: Path, users: int = 12, orders: int = 30) -> Twin:
    root = Path(root)
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "users.json": generate_users(users),
        "orders.json": generate_orders(orders, users),
    }
    for name, content in payload.items():
        (data_dir / name).write_text(json.dumps(content, indent=2, sort_keys=True), encoding="utf-8")
    manifest = build_manifest(data_dir.glob("*.json"), base=data_dir)
    (root / "twin-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    return Twin(root=root, manifest=manifest)
