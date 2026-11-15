import unittest

from agntia_adversarial.planning.budget import Budget, BudgetExceeded
from agntia_adversarial.planning.hypothesis import rank_missions
from agntia_adversarial.planning.scheduler import Scheduler

MISSIONS = [
    {"id": "api-authz", "limits": {"max_cost_cents": 20}, "risk_level": "high"},
    {"id": "repo-review", "limits": {"max_cost_cents": 10}, "risk_level": "low"},
    {"id": "ai-trust", "limits": {"max_cost_cents": 90}, "risk_level": "medium"},
]


class SchedulerTests(unittest.TestCase):
    def test_ranking_is_deterministic(self):
        self.assertEqual([m["id"] for m in rank_missions(MISSIONS)], ["api-authz", "ai-trust", "repo-review"])

    def test_scheduler_skips_missions_over_budget(self):
        scheduler = Scheduler(Budget(max_cost_cents=30, max_actions=5))
        selected = scheduler.select(MISSIONS)
        self.assertEqual([m["id"] for m in selected], ["api-authz", "repo-review"])

    def test_budget_exhaustion_is_an_error(self):
        budget = Budget(max_cost_cents=5, max_actions=1)
        with self.assertRaises(BudgetExceeded):
            budget.charge(cost_cents=10)


if __name__ == "__main__":
    unittest.main()
