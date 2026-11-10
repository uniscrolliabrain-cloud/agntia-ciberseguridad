"""Schema6: governing version, tainted facts, reviewed tools and local approved effects."""
SCHEMA=[
'''CREATE TABLE agent_epochs(tenant_id TEXT PRIMARY KEY REFERENCES tenants(id),epoch INTEGER NOT NULL)''',
'''CREATE TABLE agent_controls(tenant_id TEXT NOT NULL REFERENCES tenants(id),kind TEXT NOT NULL,scope_id TEXT NOT NULL,body TEXT NOT NULL CHECK(json_valid(body)),PRIMARY KEY(tenant_id,kind,scope_id))''',
'''CREATE TABLE data_flows(tenant_id TEXT NOT NULL REFERENCES tenants(id),id TEXT NOT NULL,resource_id TEXT NOT NULL,evidence_id TEXT NOT NULL,body TEXT NOT NULL CHECK(json_valid(body)),PRIMARY KEY(tenant_id,id),FOREIGN KEY(tenant_id,resource_id) REFERENCES assets(tenant_id,id),FOREIGN KEY(tenant_id,evidence_id) REFERENCES evidence(tenant_id,id))''',
'''CREATE TABLE flow_releases(tenant_id TEXT NOT NULL,id TEXT NOT NULL,flow_id TEXT NOT NULL,body TEXT NOT NULL CHECK(json_valid(body)),PRIMARY KEY(tenant_id,id),FOREIGN KEY(tenant_id,flow_id) REFERENCES data_flows(tenant_id,id))''',
'''CREATE TABLE governed_tools(tenant_id TEXT NOT NULL REFERENCES tenants(id),id TEXT NOT NULL,body TEXT NOT NULL CHECK(json_valid(body)),PRIMARY KEY(tenant_id,id))''',
'''CREATE TABLE tool_versions(tenant_id TEXT NOT NULL,tool_id TEXT NOT NULL,revision INTEGER NOT NULL,body TEXT NOT NULL CHECK(json_valid(body)),PRIMARY KEY(tenant_id,tool_id,revision),FOREIGN KEY(tenant_id,tool_id) REFERENCES governed_tools(tenant_id,id))''',
'''CREATE TABLE mcp_sessions(tenant_id TEXT NOT NULL,id TEXT NOT NULL,body TEXT NOT NULL CHECK(json_valid(body)),last_request_id INTEGER NOT NULL,PRIMARY KEY(tenant_id,id),FOREIGN KEY(tenant_id) REFERENCES tenants(id))''',
'''CREATE TABLE effect_proposals(tenant_id TEXT NOT NULL,id TEXT NOT NULL,resource_id TEXT NOT NULL,body TEXT NOT NULL CHECK(json_valid(body)),PRIMARY KEY(tenant_id,id),FOREIGN KEY(tenant_id,resource_id) REFERENCES assets(tenant_id,id))''',
'''CREATE TABLE local_notes(tenant_id TEXT NOT NULL,id TEXT NOT NULL,proposal_id TEXT NOT NULL,body TEXT NOT NULL CHECK(json_valid(body)),PRIMARY KEY(tenant_id,id),UNIQUE(tenant_id,proposal_id),FOREIGN KEY(tenant_id,proposal_id) REFERENCES effect_proposals(tenant_id,id))''',
'''CREATE TABLE effect_operations(tenant_id TEXT NOT NULL,key TEXT NOT NULL,proposal_id TEXT NOT NULL,request_hash TEXT NOT NULL,state TEXT NOT NULL,result TEXT NOT NULL CHECK(json_valid(result)),reserved_cents INTEGER NOT NULL CHECK(reserved_cents=0),PRIMARY KEY(tenant_id,key),UNIQUE(tenant_id,proposal_id),FOREIGN KEY(tenant_id,proposal_id) REFERENCES effect_proposals(tenant_id,id))''',
"CREATE TRIGGER tool_versions_no_update BEFORE UPDATE ON tool_versions BEGIN SELECT RAISE(ABORT,'append-only tool version'); END",
"CREATE TRIGGER tool_versions_no_delete BEFORE DELETE ON tool_versions BEGIN SELECT RAISE(ABORT,'append-only tool version'); END",
"CREATE TRIGGER notes_no_update BEFORE UPDATE ON local_notes BEGIN SELECT RAISE(ABORT,'immutable local note'); END",
"CREATE TRIGGER notes_no_delete BEFORE DELETE ON local_notes BEGIN SELECT RAISE(ABORT,'immutable local note'); END",
]
