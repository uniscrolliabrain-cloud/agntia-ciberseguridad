#!/usr/bin/env python3
"""Verify the lab stayed outside the middleware and the parent repository."""

from __future__ import annotations

import json
import subprocess
import sys

FORBIDDEN_PREFIXES = ("agntia_ciberseguridad/", "typescript/", "docs/release/")
ALLOWED = ("adversarial_lab/", "docs/adversarial/implementation-v1/execution/")


def changed_paths() -> list[str]:
    try:
        output = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout
    except OSError:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def main() -> int:
    paths = changed_paths()
    violations = [path for path in paths if path.startswith(FORBIDDEN_PREFIXES)]
    inside = [path for path in paths if path.startswith(ALLOWED)]
    payload = {
        "status": "FAIL" if violations else "PASS",
        "changed": len(paths),
        "inside_ownership": len(inside),
        "violations": violations,
    }
    print(json.dumps(payload, indent=2))
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
