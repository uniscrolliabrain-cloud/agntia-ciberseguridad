"""Hypotheses are falsifiable statements attached to a mission and a target."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class Hypothesis(BaseModel):
    id: str
    mission_id: str
    statement: str
    disproof: str
    target_ref: str
    technique_tags: List[str] = Field(default_factory=list)


def derive_hypotheses(mission: dict, target_ref: str) -> List[Hypothesis]:
    statements = mission.get("hypotheses") or []
    derived: List[Hypothesis] = []
    for index, item in enumerate(statements, start=1):
        derived.append(
            Hypothesis(
                id=f"{mission['id']}-H{index}",
                mission_id=mission["id"],
                statement=item["statement"],
                disproof=item["disproof"],
                target_ref=target_ref,
                technique_tags=list(mission.get("technique_tags", [])),
            )
        )
    return derived
