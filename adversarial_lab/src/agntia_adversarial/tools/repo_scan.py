"""Static, read-only review of the synthetic repository.

It parses text. It never imports or executes repository code.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..twins.repo import CANARY

SECRET = re.compile(r"(?i)(api[_-]?token|secret|password)\s*=\s*[\"'][^\"']{6,}[\"']")
PINNED = re.compile(r"^[A-Za-z0-9_.-]+\s*==\s*[0-9]")


def scan_repo(root: Path) -> list[dict[str, object]]:
    root = Path(root)
    findings: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in SECRET.finditer(text):
            findings.append(
                {
                    "kind": "secret",
                    "severity": "high",
                    "summary": f"posible secreto en {path.name}",
                    "reproduced": True,
                    "evidence": {"file": path.name, "canary": CANARY in match.group(0)},
                }
            )
        if path.name in {"requirements.txt", "requirements-dev.txt"}:
            for line in text.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and not PINNED.match(line):
                    findings.append(
                        {
                            "kind": "dependency",
                            "severity": "medium",
                            "summary": f"dependencia sin versión fijada: {line}",
                            "reproduced": True,
                            "evidence": {"file": path.name, "dependency": line},
                        }
                    )
    return findings
