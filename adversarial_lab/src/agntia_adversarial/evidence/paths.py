"""Confined paths for evidence identifiers.

Identifiers come from the lab, not from clients, but they are validated anyway: one `..` in a
tenant or evidence id would otherwise escape the vault root.
"""

from __future__ import annotations

import re
from pathlib import Path

COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class PathEscape(ValueError):
    pass


def validate_component(value: str, field: str) -> str:
    if not isinstance(value, str) or not COMPONENT.match(value):
        raise PathEscape(f"invalid {field}")
    if value in {".", ".."} or "/" in value or "\\" in value or "\x00" in value:
        raise PathEscape(f"invalid {field}")
    return value


def confined(root: Path, *parts: str) -> Path:
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    for value in parts:
        validate_component(value, "path component")
    candidate = root.joinpath(*parts)
    for parent in candidate.parents:
        if parent == root:
            break
        if parent.is_symlink():
            raise PathEscape("symlink in path")
    resolved = candidate.resolve()
    if resolved != root and root not in resolved.parents:
        raise PathEscape("path escapes root")
    return candidate
