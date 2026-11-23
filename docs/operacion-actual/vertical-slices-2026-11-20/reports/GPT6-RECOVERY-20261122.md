# Recovery patch — 2026-11-22

**Branch:** `fix/cyber-vs-hardening-20261122`, based on Cline's `feat/cyber-vertical-slices-installable-20261120`. **Do not merge to main without checks.**

## Actual code changes
1. Replaced syntactically broken `tests/security/test_identity_tenancy.py`. The previous version inserted a class inside the `Settings(...consents={...})` dictionary, used the same bearer token for every principal, attempted to authenticate a disabled principal, and asserted a variable outside its test. The replacement reuses the repository's real `tests.integration.test_jobs.Setup` and checks cross-tenant asset/job 404, viewer write denial, revocation, expired grant schema, malformed bearer and forged approval schema.
2. Added `agntia_ciberseguridad/integration_ports.py`: a dependency-free, fail-closed interface for optional providers. No network or credentials are accessed; an explicit adapter must be injected. Configuration alone is `CONFIGURED_UNVERIFIED`, not connected.
3. Added `tests/unit/test_integration_ports.py` to exercise disabled, missing config, configured-but-unverified, adapter missing, and invalid secret reference cases.

## Verification status
GitHub API edits committed; **full Python unit/integration tests not executed in the connector environment**. New tests must be run in Codespaces/CI; no PASS is claimed for them. `docs/release/status.json` remains unchanged NO-GO. Cline's CY-VS-02 PASS claim must be downgraded to NOT_VERIFIED until tests pass.

## Commands for executor
```bash
python -m compileall -q agntia_ciberseguridad tests/security/test_identity_tenancy.py tests/unit/test_integration_ports.py
python -m unittest tests.unit.test_integration_ports -v
python -m unittest tests.security.test_identity_tenancy -v
python -m unittest discover -s tests -v
cd typescript && npm ci && npm test && npm run pack:deterministic && npm run provenance:check
```

## Remaining engineering — do not confuse scaffold with completion
- CY-VS-03: real local defensive scanner over explicitly allowed fixture; job → normalized finding → report with negative tests, no third-party scanning.
- CY-VS-04: proposal → independent approval → retest → evidence/rollback; no automated client mutation.
- CY-VS-05: adversarial lab separate process, synthetic only, OCI isolation evidence.
- CY-VS-06: test SDK alpha.3 compatibility against `agente`'s currently pinned alpha.2. Do not change parent without explicit approval.
- CY-VS-07: wire each actual provider to `ConnectorPort` with evidence-based verification, real env schemas, stubs for absent accounts. **The `verified_environment` field is an operator declaration, not cryptographic attestation or a network check; production adapters must perform independent credential, endpoint and authorization verification.**
- CY-VS-08: E2E, CI, provenance, rollback, security review and founder acceptance.

## Founder dependencies
For synthetic local tests: none beyond development tools. For staging: authorized host identity and tenant mapping, approved GitHub scopes, secret manager references, isolated OCI runtime, private evidence storage, key custody, telemetry destination. Never put token values in repo, logs, Markdown or chat.

## Merge gate
Run compile, tests, packaging, dependency audit and parent consumer tests. Preserve release flag disabled. Merge only after fixing failures and checking compatibility.


## Additional code implemented in this recovery branch

- `tests/integration/test_cyber_vertical_slices.py`: synthetic domain E2E (existing authorized snapshot → job → simulated scanner result → normalized finding → encrypted report; and finding → reviewed evidence → proposal → distinct human approval → confirmed finding). **Scanner output is mocked**: this is a useful wiring test, NOT evidence that a real OSS scanner has been executed. No remediation, retest or external effect is implemented by this test.
- `agntia_ciberseguridad/host_bridge.py` and `tests/unit/test_host_bridge.py`: explicit read-only host identity adapter that checks current child principal, actor match and child authorization; rejects missing identity and write capabilities. **The parent must independently authenticate and authorize host context**; an `assurance='verified_host'` string is not cryptographic proof. Do not expose this class to untrusted client/LLM input.

## Additional commands
```bash
python -m unittest tests.unit.test_host_bridge tests.unit.test_integration_ports -v
python -m unittest tests.security.test_identity_tenancy -v
python -m unittest tests.integration.test_cyber_vertical_slices -v
```

## Known gaps and restrictions
- No live scanner run, OCI sandbox verification, real retest, production provider or parent SDK compatibility test was executed in this GitHub-only session.
- Do not treat mocked E2E as a finished CY-VS-03/04 production slice.
- The host bridge is not a public HTTP endpoint, and does not alter parent `agente`.
- Tests must pass in CI before a merge decision. Report failing tests verbatim.
