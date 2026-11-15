"""Egress is denied by policy, not by hoping the tool behaves."""

from __future__ import annotations


class EgressDenied(RuntimeError):
    pass


class EgressPolicy:
    def __init__(self, allow: bool = False) -> None:
        self.allow = allow

    def check(self, destination: str) -> None:
        if not self.allow:
            raise EgressDenied(f"egress denied: {destination}")
        raise EgressDenied("lab v1 never opens egress, even when configured")
