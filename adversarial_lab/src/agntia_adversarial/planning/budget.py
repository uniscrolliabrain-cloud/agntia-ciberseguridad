"""Budgets cap actions and cost; exhaustion is an error, not a warning."""

from __future__ import annotations

from dataclasses import dataclass


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class Budget:
    max_cost_cents: int
    max_actions: int
    spent_cents: int = 0
    actions: int = 0

    def charge(self, cost_cents: int = 0, actions: int = 1) -> None:
        if self.spent_cents + cost_cents > self.max_cost_cents:
            raise BudgetExceeded("cost budget exceeded")
        if self.actions + actions > self.max_actions:
            raise BudgetExceeded("action budget exceeded")
        self.spent_cents += cost_cents
        self.actions += actions

    def remaining(self) -> dict[str, int]:
        return {
            "cost_cents": self.max_cost_cents - self.spent_cents,
            "actions": self.max_actions - self.actions,
        }
