"""Daily cycle: authorize -> plan -> simulate -> evidence -> triage -> report.

Tools that are not installed return BLOCKED. The run is therefore PARTIAL by construction, and the
report says so. This is a synthetic lab, not a client pentest.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from ..config import LabConfig
from ..contracts.result import Observation, RunReceipt, Status
from ..domain.engagement import Engagement
from ..domain.scope import Scope
from ..evaluation.oracles import evaluate_observations
from ..evaluation.triage import triage
from ..evidence.redaction import redact
from ..evidence.vault import Vault
from ..missions.compiler import compile_experiment
from ..planning.budget import Budget
from ..planning.scheduler import Scheduler
from ..providers.mock import MockProvider
from ..reports.render import render_report
from ..store.sqlite import Store
from ..tools.registry import default_catalog

SIMULATED = {
    "api-authz": {
        "id": "obs-authz-1",
        "kind": "authorization",
        "severity": "high",
        "summary": "user-001 puede leer el pedido de user-002 (simulado)",
        "reproduced": True,
        "expect_finding": True,
    },
    "repo-review": {
        "id": "obs-repo-1",
        "kind": "secret",
        "severity": "medium",
        "summary": "canario sintético detectado en fixture (simulado)",
        "reproduced": True,
        "expect_finding": True,
    },
    "api-state": {
        "id": "obs-state-1",
        "kind": "business-logic",
        "severity": "medium",
        "summary": "transición created→shipped sin pago (simulado)",
        "reproduced": True,
        "expect_finding": True,
    },
    "ai-trust": {
        "id": "obs-ai-1",
        "kind": "prompt-injection",
        "severity": "high",
        "summary": "instrucción embebida intenta elevar privilegios (simulado)",
        "reproduced": True,
        "expect_finding": True,
    },
    "resilience-faults": {
        "id": "obs-resilience-1",
        "kind": "backup",
        "severity": "info",
        "summary": "pérdida de datos detectada y restaurada (simulado)",
        "reproduced": True,
        "expect_finding": False,
    },
}


@dataclass
class DailyOutcome:
    tenant_id: str
    receipt: RunReceipt
    report_path: Path
    selected: list[str]
    blocked_tools: list[str]
    metrics: dict[str, object]


def run_daily(
    config: LabConfig,
    engagement: Engagement,
    scope: Scope,
    missions: list[dict],
    *,
    output_dir: Path | None = None,
    provider=None,
) -> DailyOutcome:
    config.validate()
    if not engagement.is_active():
        raise PermissionError("engagement revoked, expired or not active")
    store = Store(config.data_dir / "lab.sqlite")
    store.add_engagement(engagement)
    store.add_scope(scope)
    vault = Vault(config.data_dir / "evidence", config.max_evidence_bytes)
    catalog = default_catalog()
    blocked_tools = [name for name, status in catalog.status().items() if status == "BLOCKED"]
    provider = provider or MockProvider()

    budget = Budget(config.default_budget_cents, max_actions=config.max_runs_per_day * 4)
    selected = Scheduler(budget, max_runs=config.max_runs_per_day).select(missions)
    if not selected:
        raise RuntimeError("scheduler selected no mission within budget")

    started = datetime.now(timezone.utc)
    observations: list[Observation] = []
    evidence = []
    oracle_failures: list[str] = []

    for mission in selected:
        if not engagement.is_active():
            raise PermissionError("engagement revoked during run")
        target_ref = mission.get("target_ref") or scope.targets[0].ref
        experiment = compile_experiment(mission, engagement, scope, target_ref)
        store.add_experiment(experiment)
        provider.plan(experiment.id, [item["statement"] for item in mission["hypotheses"]])
        provider.execute(experiment.id, mission["id"])
        simulated = SIMULATED.get(mission["id"])
        if not simulated:
            continue
        payload = json.dumps(
            {"mission": mission["id"], "summary": redact(simulated["summary"]), "synthetic": True},
            sort_keys=True,
        ).encode("utf-8")
        reference = vault.put(engagement.tenant_id, f"ev-{uuid.uuid4().hex[:10]}", payload)
        evidence.append(reference)
        observation = Observation(
            id=simulated["id"],
            kind=simulated["kind"],
            target_ref=target_ref,
            summary=redact(simulated["summary"]),
            severity=simulated["severity"],
            confidence=0.6,
            evidence=[reference],
            reproduced=simulated["reproduced"],
        )
        observations.append(observation)
        verdict = evaluate_observations(
            [observation],
            expect_finding=simulated["expect_finding"],
            forbidden_substrings=["AKIA", "user@example"],
        )
        if verdict.status != "PASS":
            oracle_failures.append(f"{mission['id']}: {verdict.reason}")

    triaged = triage(observations)
    confirmed = [item for item in triaged if item.confirmed]
    if oracle_failures:
        status = Status.FAIL
    elif blocked_tools:
        status = Status.PARTIAL
    else:
        status = Status.PASS

    receipt = RunReceipt(
        run_id=f"run-{uuid.uuid4().hex[:12]}",
        experiment_id=experiment.id if selected else "none",
        tenant_id=engagement.tenant_id,
        status=status,
        started_at=started,
        ended_at=datetime.now(timezone.utc),
        observations=[item.observation for item in triaged],
        evidence=evidence,
        limitations=[
            "synthetic simulation: no client system was touched",
            "mock provider: no model was invoked",
            f"tools BLOCKED without verified binary: {', '.join(blocked_tools) or 'none'}",
            f"confirmed findings: {len(confirmed)} (simulated)",
        ],
    )
    store.add_run(receipt)
    store.record_transition(receipt.run_id, Status.NOT_RUN.value, status.value, "daily cycle")
    report = render_report(receipt)
    destination = Path(output_dir or config.data_dir / "reports")
    destination.mkdir(parents=True, exist_ok=True)
    report_path = destination / f"{receipt.run_id}.md"
    report_path.write_text(report, encoding="utf-8")

    return DailyOutcome(
        tenant_id=engagement.tenant_id,
        receipt=receipt,
        report_path=report_path,
        selected=[mission["id"] for mission in selected],
        blocked_tools=blocked_tools,
        metrics={
            "selected": len(selected),
            "observations": len(receipt.observations),
            "confirmed": len(confirmed),
            "oracle_failures": oracle_failures,
        },
    )
