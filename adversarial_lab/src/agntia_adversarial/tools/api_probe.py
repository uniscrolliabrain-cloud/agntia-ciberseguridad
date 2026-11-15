"""Deterministic API probes against the in-process synthetic twin."""

from __future__ import annotations

from ..twins.api import SyntheticAPI


def probe_authorization(api: SyntheticAPI) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    cross = api.get_order("tok-user-1", "order-100")
    if cross["status"] == 200:
        findings.append(
            {
                "kind": "authorization",
                "severity": "high",
                "summary": "user-001 lee el pedido de user-002 (IDOR horizontal)",
                "reproduced": True,
                "evidence": {"token": "tok-user-1", "order": "order-100", "status": 200},
            }
        )
    escalation = api.ship_order("tok-support", "order-100")
    if escalation["status"] == 200:
        findings.append(
            {
                "kind": "authorization",
                "severity": "medium",
                "summary": "support puede enviar pedidos sin rol admin (escalada vertical)",
                "reproduced": True,
                "evidence": {"token": "tok-support", "status": 200},
            }
        )
    return findings


def probe_benign_control(api: SyntheticAPI) -> bool:
    return api.get_order("tok-user-2", "order-100")["status"] == 200
