# Installation into agente — staging-only integration contract

**Status: NOT READY TO MERGE / NO-GO until tests and compatibility pass.** This is a reproducible operator plan, not a claim of successful deployment.

## Current state
- Parent `uniscrolliabrain-cloud/agente` uses `@agntia/ciberseguridad` from `vendor/agntia-ciberseguridad-0.1.0-alpha.2.tgz` (observed 2026-11-22).
- Child `typescript/package.json` declares `0.1.0-alpha.3`.
- Parent has existing `apps/server/src/engine/security-v2/sdk-adapter.ts` and `event-relay.ts`. Reuse them, do not duplicate clients or bypass tenant policy.
- Child remains `SYNTHETIC_DEMO_NOT_PRODUCTION`; keep customer execution disabled.

## 1. Child verification before packaging
```bash
python -m compileall -q agntia_ciberseguridad tests
python -m unittest tests.security.test_identity_tenancy tests.unit.test_integration_ports tests.unit.test_host_bridge -v
python -m unittest tests.integration.test_cyber_vertical_slices -v
python -m unittest discover -s tests -v
(cd typescript && npm ci && npm test && npm run pack:deterministic && npm run provenance:check)
```
Stop on any failure; investigate existing package script availability if a command is not supported.

## 2. Package and pin, without modifying parent yet
- Record exact child SHA and package SHA-256.
- Generate SDK tarball using the existing deterministic packaging path, then verify `PROVENANCE.json` against the actual artifact.
- Compare exports, `CyberClient` API, Hono adapter and agent-tools against parent imports.
- Do not bump alpha.2 to alpha.3 based on semver alone.

## 3. Parent read-only compatibility checks
Inspect and run existing parent tests `tests/cognition-v2-cyber-bridge.test.ts`; inspect `apps/server/src/engine/security-v2/sdk-adapter.ts` and `event-relay.ts`. Validate tenant, actor, idempotency, event ACK, restart replay, outbox ordering and failure paths. Preserve parent lockfile consistency.

## 4. Parent patch proposal (requires separate authorization)
Only after all checks pass: copy exact verified tarball to `vendor/`, update root `package.json` and `pnpm-lock.yaml`, run `pnpm install --frozen-lockfile`, parent typecheck and bridge tests, and produce a rollback commit. Do not alter `agente` as part of this child branch.

## 5. Host identity boundary
The parent must authenticate its human/service principal, resolve tenant from its trusted server context, enforce permission and map it to an explicitly configured child principal. `HostIdentity` is a server-side value object, NOT a trusted client JSON schema; its `verified_host` marker alone is not proof. The child independently revalidates the principal and tenant via `resolve_host_read`. The bridge supports read-only capabilities only; jobs and approvals use existing governed routes.

## 6. Founder inputs: only at real connector boundary
| Integration | Before credentials | Founder action |
|---|---|---|
| GitHub App / Actions | Disabled, no API calls | App installation ID, least-privilege permissions, secret references |
| Doppler | Disabled, secret references only | Project/config/service token in secret manager |
| Parent identity | HOST_IDENTITY_NOT_CONFIGURED | Trusted tenant and principal binding policy |
| OCI scanner | No external scan; synthetic fixture only | Isolated worker runtime, image digest/policy approval |
| Evidence object storage | Local synthetic custody only | Private bucket, retention, encryption key references |
| Observability | Local metrics only | Collector endpoint and access policy |
| Notifications | No outgoing messages | Approved delivery provider and destination policy |

For every connector, use `ConnectorPort` with injected adapter and a real `verify` callback; `CONFIGURED_UNVERIFIED` is not operational. Never put tokens in repo, docs, tests, logs or chat.

## 7. Gates
- **Synthetic gate:** compile, unit, integration, deterministic packaging, provenance, no network.
- **Staging gate:** isolated scanner, verified connector identities, cross-tenant negative tests, parent bridge.
- **Production gate:** independent security review, owner acceptance, verified legal consent, external resource isolation, rollback and release controls.

Until production gate: do not deploy or enable production scans.
