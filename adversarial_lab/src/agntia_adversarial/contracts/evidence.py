"""Evidence references: Git stores metadata and hashes, never private payloads."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EvidenceRef(BaseModel):
    id: str
    sha256: str = Field(pattern="^[a-f0-9]{64}$")
    bytes: int = Field(ge=0)
    media_type: str = "application/octet-stream"
    classification: str = "internal"
    redacted: bool = True
