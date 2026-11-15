CREATE TABLE IF NOT EXISTS leases (
    tenant_id TEXT NOT NULL,
    mission_id TEXT NOT NULL,
    owner TEXT NOT NULL,
    fence INTEGER NOT NULL,
    acquired_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    PRIMARY KEY (tenant_id, mission_id)
);

CREATE TABLE IF NOT EXISTS run_keys (
    tenant_id TEXT NOT NULL,
    key TEXT NOT NULL,
    run_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (tenant_id, key)
);

CREATE INDEX IF NOT EXISTS idx_ledger_run_tenant ON ledger(run_id);
CREATE INDEX IF NOT EXISTS idx_runs_tenant_created ON runs(tenant_id, created_at);
