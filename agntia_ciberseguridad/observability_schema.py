"""Additive schema5: operational records are separate from immutable security audit."""
SCHEMA=[
'''CREATE TABLE operational_logs(sequence INTEGER PRIMARY KEY AUTOINCREMENT,tenant_id TEXT NOT NULL REFERENCES tenants(id),id TEXT NOT NULL,created_at TEXT NOT NULL,expires_at TEXT NOT NULL,legal_hold INTEGER NOT NULL DEFAULT 0,bytes INTEGER NOT NULL,body TEXT NOT NULL CHECK(json_valid(body)),UNIQUE(tenant_id,id))''',
'CREATE INDEX logs_time ON operational_logs(tenant_id,created_at,id)',
'''CREATE TABLE passive_events(sequence INTEGER PRIMARY KEY AUTOINCREMENT,tenant_id TEXT NOT NULL REFERENCES tenants(id),source_id TEXT NOT NULL,event_id TEXT NOT NULL,source_hash TEXT NOT NULL,received_at TEXT NOT NULL,body TEXT NOT NULL CHECK(json_valid(body)),state TEXT NOT NULL DEFAULT 'pending',UNIQUE(tenant_id,source_id,event_id))''',
'''CREATE TABLE source_state(tenant_id TEXT NOT NULL REFERENCES tenants(id),source_id TEXT NOT NULL,watermark TEXT,window TEXT NOT NULL,received INTEGER NOT NULL,PRIMARY KEY(tenant_id,source_id))''',
'''CREATE TABLE agent_manifests(tenant_id TEXT NOT NULL REFERENCES tenants(id),id TEXT NOT NULL,agent_binding TEXT NOT NULL,revision INTEGER NOT NULL,body TEXT NOT NULL CHECK(json_valid(body)),PRIMARY KEY(tenant_id,id))''',
'''CREATE TABLE delegations(tenant_id TEXT NOT NULL REFERENCES tenants(id),id TEXT NOT NULL,parent_id TEXT,body TEXT NOT NULL CHECK(json_valid(body)),token_hash TEXT NOT NULL,used_at TEXT,revoked INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(tenant_id,id),FOREIGN KEY(tenant_id,parent_id) REFERENCES delegations(tenant_id,id))''',
'CREATE INDEX delegation_parent ON delegations(tenant_id,parent_id)',
]
