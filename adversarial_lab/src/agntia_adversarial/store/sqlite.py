"""SQLite persistence for the lab, with tenant isolation enforced in queries."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ..contracts.experiment import ExperimentSpec
from ..contracts.result import RunReceipt
from ..domain.engagement import Engagement
from ..domain.scope import Scope

MIGRATION = Path(__file__).with_name("migrations") / "0001.sql"


class Store:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(MIGRATION.read_text(encoding="utf-8"))
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def add_engagement(self, engagement: Engagement) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO engagements(id, tenant_id, payload, status, created_at) VALUES (?,?,?,?,?)",
            (
                engagement.id,
                engagement.tenant_id,
                engagement.model_dump_json(),
                engagement.status.value,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        self.connection.commit()

    def add_scope(self, scope: Scope) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO scopes(id, engagement_id, tenant_id, payload) VALUES (?,?,?,?)",
            (scope.id, scope.engagement_id, scope.tenant_id, scope.model_dump_json()),
        )
        self.connection.commit()

    def add_experiment(self, experiment: ExperimentSpec) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO experiments(id, tenant_id, scope_id, mission_id, payload, created_at) VALUES (?,?,?,?,?,?)",
            (
                experiment.id,
                experiment.tenant_id,
                experiment.scope_id,
                experiment.mission_id,
                experiment.model_dump_json(),
                experiment.created_at.isoformat(),
            ),
        )
        self.connection.commit()

    def add_run(self, receipt: RunReceipt) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO runs(id, tenant_id, experiment_id, status, payload, created_at) VALUES (?,?,?,?,?,?)",
            (
                receipt.run_id,
                receipt.tenant_id,
                receipt.experiment_id,
                receipt.status.value,
                receipt.model_dump_json(),
                receipt.ended_at.isoformat(),
            ),
        )
        self.connection.commit()

    def get_run(self, tenant_id: str, run_id: str) -> RunReceipt | None:
        row = self.connection.execute(
            "SELECT payload FROM runs WHERE tenant_id = ? AND id = ?", (tenant_id, run_id)
        ).fetchone()
        return RunReceipt.model_validate_json(row["payload"]) if row else None

    def list_run_ids(self, tenant_id: str) -> list[str]:
        rows = self.connection.execute(
            "SELECT id FROM runs WHERE tenant_id = ? ORDER BY created_at", (tenant_id,)
        ).fetchall()
        return [row["id"] for row in rows]

    def record_transition(self, run_id: str, from_status: str, to_status: str, reason: str) -> None:
        self.connection.execute(
            "INSERT INTO ledger(run_id, from_status, to_status, reason, created_at) VALUES (?,?,?,?,?)",
            (run_id, from_status, to_status, reason, datetime.now(timezone.utc).isoformat()),
        )
        self.connection.commit()

    def ledger(self, run_id: str) -> list[dict[str, str]]:
        rows = self.connection.execute(
            "SELECT from_status, to_status, reason FROM ledger WHERE run_id = ? ORDER BY seq",
            (run_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def count_runs(self, tenant_id: str) -> int:
        row = self.connection.execute(
            "SELECT COUNT(*) AS total FROM runs WHERE tenant_id = ?", (tenant_id,)
        ).fetchone()
        return int(row["total"])

    def snapshot(self, tenant_id: str) -> dict[str, object]:
        return {
            "runs": self.list_run_ids(tenant_id),
            "run_count": self.count_runs(tenant_id),
            "ledger_entries": sum(len(self.ledger(run_id)) for run_id in self.list_run_ids(tenant_id)),
        }


def dumps(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, default=str)
