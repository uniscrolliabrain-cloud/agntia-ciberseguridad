#!/usr/bin/env python3
"""Release gate for the adversarial lab.

Two modes:
- default (integrity): lints, SBOM, local signature. Exit 0 means "internally consistent", never
  "safe to ship".
- --production: dependency audit and external attestation are required. BLOCKED never passes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "agntia_adversarial"
FORBIDDEN_IMPORTS = re.compile(r"^\s*(from|import)\s+agntia_ciberseguridad", re.MULTILINE)
NETWORK_CALLS = re.compile(r"\b(requests\.|urllib\.|httpx\.|socket\.)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--production", action="store_true")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    findings: list[str] = []
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if FORBIDDEN_IMPORTS.search(text):
            findings.append(f"imports middleware package: {path}")
        if NETWORK_CALLS.search(text):
            findings.append(f"network primitive in source: {path}")
    config = (SRC / "config.py").read_text(encoding="utf-8")
    if "allow_network: bool = False" not in config:
        findings.append("default network flag is not closed")
    sys.path.insert(0, str(ROOT / "src"))
    from agntia_adversarial.missions.registry import MissionRegistry

    missions = MissionRegistry(ROOT / "library" / "missions").load()
    if len(missions) < 5:
        findings.append(f"mission library too small: {len(missions)}")

    from agntia_adversarial.release.sbom import audit_status, build_sbom, sign_manifest, verify_signature

    sbom = build_sbom()
    if not sbom["components"]:
        findings.append("empty SBOM")
    payload = {"sbom_digest": sbom["digest"]}
    signature = sign_manifest(payload, ROOT / "var" / "keys" / "release.key")
    if not verify_signature(payload, signature):
        findings.append("signature verification failed")
    audit = audit_status()

    eligible = False
    if args.production:
        if audit["status"] != "PASS":
            findings.append(f"dependency audit not verified: {audit['status']}")
        if signature["scope"] != "external_attestation":
            findings.append("signature is lab integrity only, not external attestation")
        eligible = not findings

    print(
        json.dumps(
            {
                "mode": "production" if args.production else "integrity",
                "status": "FAIL" if findings else "PASS",
                "release_eligible": eligible and not findings,
                "missions": len(missions),
                "sbom_components": len(sbom["components"]),
                "signature": signature["scope"],
                "audit": audit["status"],
                "findings": findings,
            },
            indent=2,
        )
    )
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
