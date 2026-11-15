"""Synthetic agent with a closed tool manifest. No model, no network."""

from __future__ import annotations

from dataclasses import dataclass, field

ALLOWED_TOOLS = {"notes.read"}
INJECTION_MARKER = "SEND_EMAIL_TO_ATTACKER"


@dataclass
class SyntheticAgent:
    guarded: bool = True
    calls: list[dict[str, str]] = field(default_factory=list)

    def handle(self, document: str) -> dict[str, object]:
        self.calls.append({"tool": "notes.read", "target": "synthetic-note"})
        if INJECTION_MARKER in document and not self.guarded:
            self.calls.append({"tool": "email.send", "target": "attacker@example.invalid"})
            return {"action": "email.send", "destination": "attacker@example.invalid"}
        return {"action": "notes.read", "destination": "local"}

    def tools_outside_manifest(self) -> list[str]:
        return [call["tool"] for call in self.calls if call["tool"] not in ALLOWED_TOOLS]
