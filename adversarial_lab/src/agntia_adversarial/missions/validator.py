"""Mission definitions are data, not instructions to trust."""

from __future__ import annotations

from typing import Iterable

ALLOWED_CAPABILITIES = {
    "repo.read",
    "repo.static",
    "sbom",
    "sandbox.test",
    "api.passive",
    "api.active",
    "ai.evaluate",
    "chaos.simulate",
    "evidence.write",
}
REQUIRED = ("schema_version", "id", "title", "scope_kind", "required_capabilities", "limits", "stop_conditions", "hypotheses")


class MissionInvalid(ValueError):
    pass


def validate_mission(mission: dict, catalog_capabilities: Iterable[str] = ALLOWED_CAPABILITIES) -> None:
    for field in REQUIRED:
        if field not in mission:
            raise MissionInvalid(f"missing field: {field}")
    if mission["schema_version"] != 1:
        raise MissionInvalid("unsupported schema_version")
    if not mission["id"].startswith(("api-", "repo-", "ai-", "resilience")):
        raise MissionInvalid("mission id must declare its family")
    for capability in mission["required_capabilities"]:
        if capability not in set(catalog_capabilities):
            raise MissionInvalid(f"unknown capability: {capability}")
    if not mission["hypotheses"]:
        raise MissionInvalid("mission needs at least one falsifiable hypothesis")
    if not mission["stop_conditions"]:
        raise MissionInvalid("mission needs stop conditions")
    limits = mission["limits"]
    if not 0 < limits.get("max_duration_seconds", 0) <= 3600:
        raise MissionInvalid("max_duration_seconds out of bounds")
    if "never_network" not in mission["stop_conditions"]:
        raise MissionInvalid("lab mission must stop on network attempt")
