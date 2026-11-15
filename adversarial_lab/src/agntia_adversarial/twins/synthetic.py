"""Synthetic data only: deterministic, seeded, never derived from real customers."""

from __future__ import annotations

import random
from typing import List

FIRST_NAMES = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Farid", "Gala", "Hugo"]
LAST_NAMES = ["Lopez", "Garcia", "Martin", "Nunez", "Ortiz", "Perez", "Ruiz", "Sanz"]


def generate_users(count: int, seed: int = 7) -> List[dict[str, object]]:
    rng = random.Random(seed)
    users = []
    for index in range(count):
        users.append(
            {
                "id": f"user-{index:03d}",
                "name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
                "email": f"user{index:03d}@example.invalid",
                "role": rng.choice(["customer", "support", "admin"]),
            }
        )
    return users


def generate_orders(count: int, user_count: int, seed: int = 11) -> List[dict[str, object]]:
    rng = random.Random(seed)
    return [
        {
            "id": f"order-{index:04d}",
            "user_id": f"user-{rng.randrange(user_count):03d}",
            "total_cents": rng.randrange(500, 40000),
            "status": rng.choice(["created", "paid", "shipped", "refunded"]),
        }
        for index in range(count)
    ]
