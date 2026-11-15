"""SBOM, dependency audit status and local Ed25519 signatures.

The signature proves integrity of the manifest, not the identity of an external publisher.
"""

from __future__ import annotations

import hashlib
import shutil
from importlib import metadata
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from ..provenance.manifest import canonical_json, sha256_file

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "src" / "agntia_adversarial"


def build_sbom() -> dict[str, object]:
    components = []
    for path in sorted(PACKAGE.rglob("*.py")):
        components.append(
            {
                "type": "file",
                "name": str(path.relative_to(ROOT)),
                "hashes": [{"alg": "SHA-256", "content": sha256_file(path)}],
            }
        )
    dependencies = []
    for name in ("pydantic", "jsonschema", "cryptography"):
        try:
            version = metadata.version(name)
        except metadata.PackageNotFoundError:
            version = "unknown"
        dependencies.append({"name": name, "version": version})
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "version": 1,
        "metadata": {"component": {"type": "application", "name": "agntia-adversarial"}},
        "components": components + [{"type": "library", **item} for item in dependencies],
        "digest": hashlib.sha256(canonical_json(components).encode("utf-8")).hexdigest(),
    }


def audit_status() -> dict[str, object]:
    binary = shutil.which("pip-audit")
    if binary is None:
        return {"status": "BLOCKED", "reason": "pip-audit not installed; no vulnerability claim made"}
    return {
        "status": "PARTIAL",
        "reason": "pip-audit present but not executed automatically; CI must run it offline with a pinned DB",
        "binary": binary,
    }


def sign_manifest(payload: dict[str, object], key_path: Path) -> dict[str, str]:
    key_path = Path(key_path)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    if key_path.exists():
        private = Ed25519PrivateKey.from_private_bytes(key_path.read_bytes())
    else:
        private = Ed25519PrivateKey.generate()
        key_path.write_bytes(
            private.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
        key_path.chmod(0o600)
    message = canonical_json(payload).encode("utf-8")
    public = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )
    return {
        "algorithm": "ed25519",
        "signature": private.sign(message).hex(),
        "public_key": public.hex(),
        "scope": "manifest_integrity_only",
    }


def verify_signature(payload: dict[str, object], signature: dict[str, str]) -> bool:
    try:
        public = Ed25519PublicKey.from_public_bytes(bytes.fromhex(signature["public_key"]))
        public.verify(bytes.fromhex(signature["signature"]), canonical_json(payload).encode("utf-8"))
        return True
    except Exception:
        return False
