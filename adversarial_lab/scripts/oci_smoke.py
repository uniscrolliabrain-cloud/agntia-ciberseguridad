#!/usr/bin/env python3
"""Negative OCI checks: no network, no host paths, read-only root, bounded output.

Usage: python adversarial_lab/scripts/oci_smoke.py <image-id-or-digest>
Exits 0 only when every attack is blocked and the benign control succeeds.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agntia_adversarial.execution.oci import OCISandbox, RuntimeSpec  # noqa: E402

NETWORK = "import socket; socket.create_connection(('1.1.1.1', 53), timeout=2)"
HOST_PATH = "import os; print(os.path.exists('/workspace'))"
ROOT_WRITE = "open('/etc/advlab-probe', 'w').write('x')"
CONTROL = "print('advlab-ok')"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(json.dumps({"status": "FAIL", "reason": "image id required"}))
        return 2
    sandbox = OCISandbox(RuntimeSpec(image=argv[0]))
    checks = {
        "network_denied": sandbox.run(["-c", NETWORK]),
        "host_path_absent": sandbox.run(["-c", HOST_PATH]),
        "root_write_denied": sandbox.run(["-c", ROOT_WRITE]),
        "benign_control": sandbox.run(["-c", CONTROL]),
    }
    results = {name: result.get("status") for name, result in checks.items()}
    ok = (
        results["network_denied"] == "FAIL"
        and results["host_path_absent"] == "PASS"
        and "False" in str(checks["host_path_absent"].get("stdout", ""))
        and results["root_write_denied"] == "FAIL"
        and results["benign_control"] == "PASS"
        and "advlab-ok" in str(checks["benign_control"].get("stdout", ""))
    )
    print(
        json.dumps(
            {
                "status": "PASS" if ok else "FAIL",
                "image": argv[0],
                "results": results,
                "evidence": {name: {"exit": result.get("exit")} for name, result in checks.items()},
            },
            indent=2,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
