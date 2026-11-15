"""Ranking is deterministic: risk first, then cost, then id."""

from __future__ import annotations

RISK_ORDER = {"low": 0, "medium": 1, "high": 2}


def rank_missions(missions: list[dict]) -> list[dict]:
    return sorted(
        missions,
        key=lambda mission: (
            -RISK_ORDER.get(mission.get("risk_level", "low"), 1),
            mission["limits"].get("max_cost_cents", 100),
            mission["id"],
        ),
    )
