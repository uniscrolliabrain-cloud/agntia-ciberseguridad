"""AES-GCM evidence vault. Git never stores the payload, only the reference."""

from __future__ import annotations

import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ..contracts.evidence import EvidenceRef
from ..keys import KeyRing
from ..provenance.manifest import sha256_bytes


class EvidenceTooLarge(ValueError):
    pass


class Vault:
    def __init__(self, root: Path, max_bytes: int = 2 * 1024 * 1024) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.key = KeyRing(self.root).ensure("evidence")
        self.max_bytes = max_bytes

    def put(self, tenant_id: str, evidence_id: str, payload: bytes, media_type: str = "application/json") -> EvidenceRef:
        if len(payload) > self.max_bytes:
            raise EvidenceTooLarge(f"evidence exceeds {self.max_bytes} bytes")
        tenant_dir = self.root / tenant_id
        tenant_dir.mkdir(parents=True, exist_ok=True)
        nonce = os.urandom(12)
        ciphertext = AESGCM(self.key).encrypt(nonce, payload, evidence_id.encode("utf-8"))
        (tenant_dir / f"{evidence_id}.bin").write_bytes(nonce + ciphertext)
        return EvidenceRef(
            id=evidence_id,
            sha256=sha256_bytes(payload),
            bytes=len(payload),
            media_type=media_type,
        )

    def get(self, tenant_id: str, evidence_id: str) -> bytes:
        blob = (self.root / tenant_id / f"{evidence_id}.bin").read_bytes()
        return AESGCM(self.key).decrypt(blob[:12], blob[12:], evidence_id.encode("utf-8"))

    def verify(self, tenant_id: str, ref: EvidenceRef) -> bool:
        return sha256_bytes(self.get(tenant_id, ref.id)) == ref.sha256
