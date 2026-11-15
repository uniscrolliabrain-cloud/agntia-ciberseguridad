"""Explicit run state machine. Ambiguous states are rejected, not guessed."""

from __future__ import annotations

from ..contracts.result import Status

ALLOWED: dict[Status, set[Status]] = {
    Status.NOT_RUN: {Status.BLOCKED, Status.PARTIAL, Status.PASS, Status.FAIL},
    Status.BLOCKED: {Status.NOT_RUN, Status.PARTIAL},
    Status.PARTIAL: {Status.PASS, Status.FAIL, Status.BLOCKED},
    Status.PASS: {Status.FAIL},
    Status.FAIL: {Status.PARTIAL, Status.PASS},
}


def can_transition(current: Status, target: Status) -> bool:
    return target in ALLOWED.get(current, set())
