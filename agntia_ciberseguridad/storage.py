"""Single-node SQLite foundation with transactional additive migrations and backups."""
import json
import time
from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterable

from .errors import reject
from .util import canonical, digest, now, uid

SCHEMA = [
    "CREATE TABLE tenants(id TEXT PRIMARY KEY,created_at TEXT NOT NULL)",
    """CREATE TABLE assets(tenant_id TEXT NOT NULL REFERENCES tenants(id),id TEXT NOT NULL,
        target_ref TEXT NOT NULL,revision INTEGER NOT NULL,state TEXT NOT NULL,body TEXT NOT NULL CHECK(json_valid(body)),
        PRIMARY KEY(tenant_id,id),UNIQUE(tenant_id,target_ref))""",
    """CREATE TABLE grants(tenant_id TEXT NOT NULL,id TEXT NOT NULL,asset_id TEXT NOT NULL,
        revision INTEGER NOT NULL,state TEXT NOT NULL,body TEXT NOT NULL CHECK(json_valid(body)),
        PRIMARY KEY(tenant_id,id),FOREIGN KEY(tenant_id,asset_id) REFERENCES assets(tenant_id,id))""",
    """CREATE TABLE audit(tenant_id TEXT NOT NULL REFERENCES tenants(id),sequence INTEGER NOT NULL,
        body TEXT NOT NULL CHECK(json_valid(body)),hash TEXT NOT NULL,
        PRIMARY KEY(tenant_id,sequence))""",
    "CREATE INDEX grants_asset ON grants(tenant_id,asset_id,state)",
    "CREATE TRIGGER audit_no_update BEFORE UPDATE ON audit BEGIN SELECT RAISE(ABORT,'append-only audit'); END",
    "CREATE TRIGGER audit_no_delete BEFORE DELETE ON audit BEGIN SELECT RAISE(ABORT,'append-only audit'); END",
]
MIGRATIONS = ((1, SCHEMA),)


class Database:
    def __init__(self, root: Path, timeout: float = 1.0):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = self.root / "cyber.sqlite3"
        self.timeout = timeout

    @contextmanager
    def connection(self, *, readonly: bool = False):
        db = sqlite3.connect(self.path, timeout=self.timeout)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        if readonly:
            db.execute("PRAGMA query_only=ON")
        try:
            yield db
            if not readonly:
                db.commit()
        except sqlite3.OperationalError as exc:
            db.rollback()
            if "locked" in str(exc).lower() or "busy" in str(exc).lower():
                reject("storage_busy", "Almacenamiento temporalmente ocupado", 503, retryable=True)
            raise
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @contextmanager
    def transaction(self):
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            yield db

    def migrate(self, migrations=None):
        migrations = migrations if migrations is not None else MIGRATIONS
        check_versions = [v for v, _ in migrations]
        if check_versions != sorted(set(check_versions)) or not check_versions:
            raise ValueError("Invalid migration sequence")
        with self.connection() as db:
            deadline = time.monotonic() + self.timeout
            while True:
                try:
                    db.execute("PRAGMA journal_mode=WAL")
                    break
                except sqlite3.OperationalError as exc:
                    if "locked" not in str(exc).lower() or time.monotonic() >= deadline:
                        raise
                    time.sleep(0.01)
            exists = db.execute("SELECT 1 FROM sqlite_master WHERE name='schema_migrations'").fetchone()
            applied = {r[0] for r in db.execute("SELECT version FROM schema_migrations")} if exists else set()
        if applied - set(check_versions):
            raise ValueError("Database version is newer than this application")
        if set(check_versions) <= applied:
            return None
        backups = self.root / "migration-backups"
        backups.mkdir(exist_ok=True, mode=0o700)
        backup = backups / ("before-migration-" + uid() + ".sqlite3")
        with sqlite3.connect(self.path) as source, sqlite3.connect(backup) as destination:
            source.backup(destination)
        backup.chmod(0o600)
        with self.transaction() as db:
            db.execute("CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY,applied_at TEXT NOT NULL)")
            for version, statements in migrations:
                if db.execute("SELECT 1 FROM schema_migrations WHERE version=?", (version,)).fetchone():
                    continue
                for statement in statements:
                    db.execute(statement)
                db.execute("INSERT INTO schema_migrations VALUES(?,?)", (version, now()))
        self.path.chmod(0o600)
        return backup

    def provision_tenants(self, tenants: Iterable[str]):
        with self.transaction() as db:
            for tenant in sorted(set(tenants)):
                db.execute("INSERT INTO tenants VALUES(?,?) ON CONFLICT(id) DO NOTHING", (tenant, now()))

    @staticmethod
    def audit(db, tenant: str, actor: str, action: str, object_id: str, correlation: str, detail: dict):
        previous = db.execute("SELECT sequence,hash FROM audit WHERE tenant_id=? ORDER BY sequence DESC LIMIT 1", (tenant,)).fetchone()
        sequence = previous["sequence"] + 1 if previous else 1
        # detail contains safe IDs/codes/hashes only; never a raw request or authorization header.
        event = {"tenant_id": tenant, "sequence": sequence, "at": now(), "actor_id": actor,
                 "action": action, "object_id": object_id, "correlation_id": correlation,
                 "detail": detail, "content_hash": digest(detail),
                 "previous_hash": previous["hash"] if previous else "0" * 64}
        db.execute("INSERT INTO audit VALUES(?,?,?,?)", (tenant, sequence, canonical(event), digest(event)))

    @staticmethod
    def verify_audit(db, tenant: str):
        previous = "0" * 64
        count = 0
        for row in db.execute("SELECT * FROM audit WHERE tenant_id=? ORDER BY sequence", (tenant,)):
            count += 1
            try:
                event = json.loads(row["body"])
                valid = (event["tenant_id"] == tenant and row["sequence"] == count == event["sequence"]
                         and event["previous_hash"] == previous and digest(event) == row["hash"]
                         and event["content_hash"] == digest(event["detail"]))
            except (KeyError, TypeError, ValueError):
                valid = False
            if not valid:
                return {"valid": False, "checked_events": count, "failure_sequence": row["sequence"]}
            previous = row["hash"]
        return {"valid": True, "checked_events": count, "last_hash": previous,
                "limitation": "Local integrity check; no external anchoring against a privileged database administrator."}
