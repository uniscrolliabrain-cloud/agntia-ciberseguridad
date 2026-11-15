"""Mission executors: real probes against synthetic objects, no client systems."""

from __future__ import annotations

from pathlib import Path

from ..tools.agent_probe import probe_injection
from ..tools.api_probe import probe_authorization, probe_benign_control
from ..tools.faults import FaultInjector
from ..tools.repo_scan import scan_repo
from ..twins.agent import SyntheticAgent
from ..twins.api import SyntheticAPI
from ..twins.builder import build_twin
from ..twins.repo import build_repo


def api_authz(config) -> dict[str, object]:
    api = SyntheticAPI()
    findings = probe_authorization(api)
    benign = probe_benign_control(api)
    if findings:
        first = findings[0]
        return {
            "id": "obs-authz-1",
            "kind": first["kind"],
            "severity": first["severity"],
            "summary": first["summary"],
            "reproduced": bool(first["reproduced"]) and benign,
            "expect_finding": True,
        }
    return {
        "id": "obs-authz-1",
        "kind": "authorization",
        "severity": "info",
        "summary": "sin IDOR en la API sintética",
        "reproduced": benign,
        "expect_finding": True,
    }


def repo_review(config) -> dict[str, object]:
    root = build_repo(Path(config.data_dir) / "twins" / "repo")
    findings = scan_repo(root)
    if not findings:
        return {
            "id": "obs-repo-1",
            "kind": "secret",
            "severity": "info",
            "summary": "sin secretos ni dependencias sin fijar",
            "reproduced": True,
            "expect_finding": True,
        }
    secret = next((item for item in findings if item["kind"] == "secret"), findings[0])
    return {
        "id": "obs-repo-1",
        "kind": secret["kind"],
        "severity": secret["severity"],
        "summary": f"{secret['summary']} (+{len(findings) - 1} hallazgos)",
        "reproduced": True,
        "expect_finding": True,
    }


def api_state(config) -> dict[str, object]:
    api = SyntheticAPI(flaw_horizontal=False, flaw_role=False)
    result = api.ship_order("tok-admin", "order-100")
    unpaid_ship = result["status"] == 200 and api.orders["order-100"]["status"] == "created"
    return {
        "id": "obs-state-1",
        "kind": "business-logic",
        "severity": "medium" if unpaid_ship else "info",
        "summary": "envío sin pago en la API sintética" if unpaid_ship else "sin transición ilegal",
        "reproduced": unpaid_ship,
        "expect_finding": True,
    }


def ai_trust(config) -> dict[str, object]:
    findings = probe_injection(SyntheticAgent(guarded=False))
    if not findings:
        return {
            "id": "obs-ai-1",
            "kind": "prompt-injection",
            "severity": "info",
            "summary": "sin abuso de herramienta",
            "reproduced": True,
            "expect_finding": True,
        }
    first = findings[0]
    return {
        "id": "obs-ai-1",
        "kind": first["kind"],
        "severity": first["severity"],
        "summary": first["summary"],
        "reproduced": True,
        "expect_finding": True,
    }


def resilience_faults(config) -> dict[str, object]:
    twin = build_twin(Path(config.data_dir) / "twins" / "resilience")
    target = Path(twin.root) / "data" / "users.json"
    result = FaultInjector().destroy_and_restore(target, Path(twin.root) / "backups")
    return {
        "id": "obs-resilience-1",
        "kind": "backup",
        "severity": "info" if result.status == "PASS" else "high",
        "summary": f"restore {result.status.lower()}: {result.reason}",
        "reproduced": result.status == "PASS",
        "expect_finding": False,
    }


EXECUTORS = {
    "api-authz": api_authz,
    "repo-review": repo_review,
    "api-state": api_state,
    "ai-trust": ai_trust,
    "resilience-faults": resilience_faults,
}
