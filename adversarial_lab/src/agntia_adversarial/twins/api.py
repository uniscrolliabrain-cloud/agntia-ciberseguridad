"""Synthetic API in-process. No sockets, no network: a dict and a token map."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SyntheticAPI:
    flaw_horizontal: bool = True
    flaw_role: bool = True
    orders: dict[str, dict] = field(default_factory=dict)
    tokens: dict[str, str] = field(
        default_factory=lambda: {
            "tok-user-1": "user-001",
            "tok-user-2": "user-002",
            "tok-support": "support-1",
            "tok-admin": "admin-1",
        }
    )

    def __post_init__(self) -> None:
        self.orders.setdefault("order-100", {"id": "order-100", "user_id": "user-002", "status": "created"})

    def _user(self, token: str) -> str | None:
        return self.tokens.get(token)

    def get_order(self, token: str, order_id: str) -> dict:
        user = self._user(token)
        if user is None:
            return {"status": 401, "body": {"error": "unauthenticated"}}
        order = self.orders.get(order_id)
        if order is None:
            return {"status": 404, "body": {"error": "not_found"}}
        if order["user_id"] != user and user != "admin-1" and not self.flaw_horizontal:
            return {"status": 404, "body": {"error": "not_found"}}
        return {"status": 200, "body": order}

    def ship_order(self, token: str, order_id: str) -> dict:
        user = self._user(token)
        if user is None:
            return {"status": 401, "body": {"error": "unauthenticated"}}
        if not user.startswith("admin") and not (self.flaw_role and user.startswith("support")):
            return {"status": 403, "body": {"error": "forbidden"}}
        return {"status": 200, "body": {"id": order_id, "status": "shipped"}}
