"""AES-GCM evidence vault with per-tenant keys, bound AAD and atomic writes.

The master key never encrypts evidence directly: each tenant gets a HKDF-derived key and the
associated data binds tenant, evidence id and format version. A blob moved to another tenant
fails authentication instead of decrypting.
"""

from __future__ import annotations

import os
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from ..contracts.evidence import EvidenceRef
from ..keys import KeyRing
from ..provenance.manifest import sha256_bytes
from .paths import confined, validate_component

VERSION = "v1"


class EvidenceTooLarge(ValueError):
    pass


class EvidenceIntegrityError(ValueError):
    pass


class Vault:
    def __init__(self, root: Path, max_bytes: int = 2 * 1024 * 1024) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.master = KeyRing(self.root).ensure("evidence")
        self.max_bytes = max_bytes

    def _key(self, tenant_id: str) -> bytes:
        return HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"advlab-evidence",
            info=f"tenant:{tenant_id}:{VERSION}".encode("utf-8"),
        ).derive(self.master)

    def _aad(self, tenant_id: str, evidence_id: str) -> bytes:
        return f"{tenant_id}|{evidence_id}|{VERSION}".encode("utf-8")

    def _path(self, tenant_id: str, evidence_id: str) -> Path:
        validate_component(tenant_id, "tenant_id")
        validate_component(evidence_id, "evidence_id")
        return confined(self.root, tenant_id, f"{evidence_id}.bin")

    def put(
        self,
        tenant_id: str,
        evidence_id: str,
        payload: bytes,
        media_type: str = "application/json",
    ) -> EvidenceRef:
        if len(payload) > self.max_bytes:
            raise EvidenceTooLarge(f"evidence exceeds {self.max_bytes} bytes")
        path = self._path(tenant_id, evidence_id)
        nonce = os.urandom(12)
        ciphertext = AESGCM(self._key(tenant_id)).encrypt(nonce, payload, self._aad(tenant_id, evidence_id))
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.{os.urandom(4).hex()}.tmp")
        temporary.write_bytes(nonce + ciphertext)
        temporary.chmod(0o600)
        os.replace(temporary, path)
        return EvidenceRef(
            id=evidence_id,
            sha256=sha256_bytes(payload),
            bytes=len(payload),
            media_type=media_type,
        )

    def get(self, tenant_id: str, evidence_id: str) -> bytes:
        path = self._path(tenant_id, evidence_id)
        blob = path.read_bytes()
        try:
            return AESGCM(self._key(tenant_id)).decrypt(
                blob[:12], blob[12:], self._aad(tenant_id, evidence_id)
            )
        except InvalidTag as error:
            raise EvidenceIntegrityError("evidence authentication failed") from error

    def verify(self, tenant_id: str, ref: EvidenceRef) -> bool:
        return sha256_bytes(self.get(tenant_id, ref.id)) == ref.sha256
