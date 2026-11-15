"""SQLite persistence with tenant checks on every write and scoped read."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ..contracts.experiment import ExperimentSpec
from ..contracts.result import RunReceipt
from ..domain.engagement import Engagement
from ..domain.scope import Scope

MIGRATIONS = Path(__file__).with_name("migrations")


class TenantBoundaryError(RuntimeError):
    pass


class Store:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        for migration in sorted(MIGRATIONS.glob("*.sql")):
            self.connection.executescript(migration.read_text(encoding="utf-8"))
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def _tenant_of(self, table: str, identifier: str) -> str | None:
        row = self.connection.execute(f"SELECT tenant_id FROM {table} WHERE id = ?", (identifier,)).fetchone()
        return str(row["tenant_id"]) if row else None

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
        engagement_tenant = self._tenant_of("engagements", scope.engagement_id)
        if engagement_tenant is not None and engagement_tenant != scope.tenant_id:
            raise TenantBoundaryError("scope tenant does not match engagement tenant")
        self.connection.execute(
            "INSERT OR REPLACE INTO scopes(id, engagement_id, tenant_id, payload) VALUES (?,?,?,?)",
            (scope.id, scope.engagement_id, scope.tenant_id, scope.model_dump_json()),
        )
        self.connection.commit()

    def add_experiment(self, experiment: ExperimentSpec) -> None:
        scope_tenant = self._tenant_of("scopes", experiment.scope_id)
        if scope_tenant is not None and scope_tenant != experiment.tenant_id:
            raise TenantBoundaryError("experiment tenant does not match scope tenant")
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
        experiment_tenant = self._tenant_of("experiments", receipt.experiment_id)
        if experiment_tenant is not None and experiment_tenant != receipt.tenant_id:
            raise TenantBoundaryError("run tenant does not match experiment tenant")
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

    def record_transition(
        self, tenant_id: str, run_id: str, from_status: str, to_status: str, reason: str
    ) -> None:
        if self._tenant_of("runs", run_id) != tenant_id:
            raise TenantBoundaryError("run does not belong to tenant")
        self.connection.execute(
            "INSERT INTO ledger(run_id, from_status, to_status, reason, created_at) VALUES (?,?,?,?,?)",
            (run_id, from_status, to_status, reason, datetime.now(timezone.utc).isoformat()),
        )
        self.connection.commit()

    def ledger(self, tenant_id: str, run_id: str) -> list[dict[str, str]]:
        rows = self.connection.execute(
            "SELECT l.from_status, l.to_status, l.reason FROM ledger l"
            " JOIN runs r ON r.id = l.run_id"
            " WHERE r.tenant_id = ? AND l.run_id = ? ORDER BY l.seq",
            (tenant_id, run_id),
        ).fetchall()
        return [dict(row) for row in rows]

    def count_runs(self, tenant_id: str) -> int:
        row = self.connection.execute(
            "SELECT COUNT(*) AS total FROM runs WHERE tenant_id = ?", (tenant_id,)
        ).fetchone()
        return int(row["total"])

    def snapshot(self, tenant_id: str) -> dict[str, object]:
        run_ids = self.list_run_ids(tenant_id)
        return {
            "runs": run_ids,
            "run_count": len(run_ids),
            "ledger_entries": sum(len(self.ledger(tenant_id, run_id)) for run_id in run_ids),
        }


def dumps(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, default=str)
