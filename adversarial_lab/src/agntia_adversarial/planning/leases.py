"""Durable mission leases with fencing tokens.

A crashed worker leaves an expired lease behind; the next owner gets a higher fence and any stale
worker that tries to renew, release or record with the old fence is rejected.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from ..store.sqlite import Store


class LeaseError(RuntimeError):
    pass


@dataclass(frozen=True)
class Lease:
    tenant_id: str
    mission_id: str
    owner: str
    fence: int
    expires_at: datetime

    def expired(self, now: datetime | None = None) -> bool:
        return (now or datetime.now(timezone.utc)) >= self.expires_at


class LeaseManager:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.connection = store.connection

    def acquire(
        self,
        tenant_id: str,
        mission_id: str,
        owner: str,
        ttl_seconds: int = 60,
        now: datetime | None = None,
    ) -> Lease | None:
        if ttl_seconds <= 0:
            raise LeaseError("ttl must be positive")
        now = now or datetime.now(timezone.utc)
        expires = now + timedelta(seconds=ttl_seconds)
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute(
                "SELECT owner, fence, expires_at FROM leases WHERE tenant_id = ? AND mission_id = ?",
                (tenant_id, mission_id),
            ).fetchone()
            if row is not None and datetime.fromisoformat(row["expires_at"]) > now:
                self.connection.rollback()
                return None
            fence = (int(row["fence"]) if row else 0) + 1
            self.connection.execute(
                "INSERT OR REPLACE INTO leases(tenant_id, mission_id, owner, fence, acquired_at, expires_at)"
                " VALUES (?,?,?,?,?,?)",
                (tenant_id, mission_id, owner, fence, now.isoformat(), expires.isoformat()),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        return Lease(tenant_id, mission_id, owner, fence, expires)

    def renew(self, lease: Lease, ttl_seconds: int = 60, now: datetime | None = None) -> Lease | None:
        now = now or datetime.now(timezone.utc)
        expires = now + timedelta(seconds=ttl_seconds)
        cursor = self.connection.execute(
            "UPDATE leases SET expires_at = ? WHERE tenant_id = ? AND mission_id = ?"
            " AND owner = ? AND fence = ? AND expires_at > ?",
            (expires.isoformat(), lease.tenant_id, lease.mission_id, lease.owner, lease.fence, now.isoformat()),
        )
        self.connection.commit()
        if cursor.rowcount != 1:
            return None
        return Lease(lease.tenant_id, lease.mission_id, lease.owner, lease.fence, expires)

    def release(self, lease: Lease) -> bool:
        cursor = self.connection.execute(
            "DELETE FROM leases WHERE tenant_id = ? AND mission_id = ? AND owner = ? AND fence = ?",
            (lease.tenant_id, lease.mission_id, lease.owner, lease.fence),
        )
        self.connection.commit()
        return cursor.rowcount == 1

    def owns(self, lease: Lease, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        row = self.connection.execute(
            "SELECT fence, expires_at FROM leases WHERE tenant_id = ? AND mission_id = ?",
            (lease.tenant_id, lease.mission_id),
        ).fetchone()
        if row is None:
            return False
        return int(row["fence"]) == lease.fence and datetime.fromisoformat(row["expires_at"]) > now

    def register_run(self, tenant_id: str, key: str, run_id: str) -> tuple[str, bool]:
        now = datetime.now(timezone.utc).isoformat()
        cursor = self.connection.execute(
            "INSERT OR IGNORE INTO run_keys(tenant_id, key, run_id, created_at) VALUES (?,?,?,?)",
            (tenant_id, key, run_id, now),
        )
        self.connection.commit()
        row = self.connection.execute(
            "SELECT run_id FROM run_keys WHERE tenant_id = ? AND key = ?", (tenant_id, key)
        ).fetchone()
        return str(row["run_id"]), cursor.rowcount == 1

    def durable_state(self, tenant_id: str) -> dict[str, int]:
        leases = self.connection.execute(
            "SELECT COUNT(*) AS total FROM leases WHERE tenant_id = ?", (tenant_id,)
        ).fetchone()["total"]
        keys = self.connection.execute(
            "SELECT COUNT(*) AS total FROM run_keys WHERE tenant_id = ?", (tenant_id,)
        ).fetchone()["total"]
        return {"leases": int(leases), "run_keys": int(keys)}
