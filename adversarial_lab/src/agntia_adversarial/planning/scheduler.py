"""Scheduler: picks missions that fit the budget and the authorized window."""

from __future__ import annotations

from dataclasses import dataclass, field

from .budget import Budget
from .hypothesis import rank_missions


@dataclass
class Scheduler:
    budget: Budget
    max_runs: int = 5
    selected: list[str] = field(default_factory=list)

    def select(self, missions: list[dict]) -> list[dict]:
        chosen: list[dict] = []
        for mission in rank_missions(missions):
            cost = mission["limits"].get("max_cost_cents", 0)
            if not self.budget.remaining()["actions"]:
                break
            if cost > self.budget.remaining()["cost_cents"]:
                continue
            self.budget.charge(cost_cents=cost, actions=1)
            self.selected.append(mission["id"])
            chosen.append(mission)
            if len(chosen) >= self.max_runs:
                break
        return chosen
