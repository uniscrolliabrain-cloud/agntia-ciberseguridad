SCHEMA=[
'''CREATE TABLE governance_records(tenant_id TEXT NOT NULL REFERENCES tenants(id),id TEXT NOT NULL,kind TEXT NOT NULL,revision INTEGER NOT NULL,body TEXT NOT NULL CHECK(json_valid(body)),PRIMARY KEY(tenant_id,id))''',
'''CREATE TABLE governance_history(tenant_id TEXT NOT NULL,id TEXT NOT NULL,revision INTEGER NOT NULL,body TEXT NOT NULL CHECK(json_valid(body)),PRIMARY KEY(tenant_id,id,revision),FOREIGN KEY(tenant_id,id) REFERENCES governance_records(tenant_id,id))''',
'''CREATE TABLE governance_keys(tenant_id TEXT NOT NULL,kind TEXT NOT NULL,key TEXT NOT NULL,record_id TEXT NOT NULL,request_hash TEXT NOT NULL,PRIMARY KEY(tenant_id,kind,key),FOREIGN KEY(tenant_id,record_id) REFERENCES governance_records(tenant_id,id))''',
'''CREATE TABLE evidence_privacy(tenant_id TEXT NOT NULL,evidence_id TEXT NOT NULL,restricted INTEGER NOT NULL,body TEXT NOT NULL CHECK(json_valid(body)),PRIMARY KEY(tenant_id,evidence_id),FOREIGN KEY(tenant_id,evidence_id) REFERENCES evidence(tenant_id,id))''',
"CREATE TRIGGER governance_history_no_update BEFORE UPDATE ON governance_history BEGIN SELECT RAISE(ABORT,'append-only governance history'); END",
"CREATE TRIGGER governance_history_no_delete BEFORE DELETE ON governance_history BEGIN SELECT RAISE(ABORT,'append-only governance history'); END",
'''CREATE TABLE report_source_scopes(tenant_id TEXT NOT NULL,evidence_id TEXT NOT NULL,sources TEXT NOT NULL CHECK(json_valid(sources)),PRIMARY KEY(tenant_id,evidence_id),FOREIGN KEY(tenant_id,evidence_id) REFERENCES evidence(tenant_id,id))''',
'CREATE INDEX governance_kind ON governance_records(tenant_id,kind,id)',
]
