# HANDOFF · FREEBUFF — PMV ultraserio de Agntia Ciberseguridad

> **Instrucciones para el agente autónomo que recibe este handoff.**
> Lee este archivo entero antes de escribir una línea de código. Tu misión es convertir la documentación existente (sólida pero sin runtime) en un **Producto Mínimo Viable ultraserio**: middleware agéntico instalable en el repo padre `/agente`, compatible con **pnpm + Hono + TypeScript**, con adaptadores plug-in a herramientas de ciberseguridad y observabilidad, gateway de policy determinista, y trazabilidad end-to-end. Trabaja en autónomo, pero **no inventes PASS ni resultados no ejecutados**. Si algo no se puede probar en tu entorno, márcalo `BLOCKED` con motivo.

---

## 0. Contexto que YA existe (no lo rehagas)

El repo contiene:
- `README.md`, `docs/` (12 documentos + research con 31 repos y 7 papers), `docs/campaigns/2026-11-10-seven-days/` (42 fases, 294 tareas, 84 gates `NOT_EXECUTED`).
- `config/plans.json` (Lite 30€ / L 70€ / XL 300€, `state: DESIGN_ONLY_NOT_ENFORCED`).
- `scripts/validate_foundation.py`, `scripts/validate_campaign.py` (validan docs, no seguridad).
- `AGENTS.md`, `SECURITY.md`, `.gitignore`.

**Calidad de la documentación:** muy alta. **Código de runtime:** inexistente. **Integración con `/agente`:** solo propuesta.

No borres ni reescribas la documentación existente. Añade encima.

---

## 1. Decisiones de stack (BLOQUEANTES — resuélvelas primero)

La documentación propone Python/FastAPI para el core y TS/Hono para el SDK. **Para este PMV, unifica en TypeScript.** Motivo: se instala dentro de `/agente` (Node/Hono/pnpm), evita dual-runtime, reduce latencia en el path de policy (crítico: se evalúa por tool call).

**Stack obligatorio del PMV:**
- **Runtime:** Node 20 LTS + pnpm 9.
- **Framework HTTP:** Hono (server-side).
- **Lenguaje:** TypeScript strict (`strict: true`, `noUncheckedIndexedAccess: true`, `exactOptionalPropertyTypes: true`).
- **Validación:** Zod (schemas runtime + tipos inferidos).
- **Persistencia:** SQLite vía `better-sqlite3` para el PMV (transaccional, zero-config). Deja un `StorageDriver` interface para migrar a PostgreSQL sin tocar dominio.
- **Colas/jobs:** tabla `jobs` en SQLite con leases + fencing tokens (NO Redis en el PMV; documenta cómo añadirlo).
- **Policy engine:** implementación propia determinista en TS (reglas declarativas + evaluador). NO adoptes OPA/Cedar en el PMV (complejidad de despliegue); deja un `PolicyEngine` interface para sustituir.
- **Observabilidad:** OpenTelemetry (`@opentelemetry/sdk-node` + instrumentación Hono) + métricas Prometheus vía `prom-client`. Logs estructurados JSON con redacción.
- **CLI / adaptadores:** subprocesos aislados con `child_process.spawn` (argv cerrado, env allowlist, timeout, límite de salida). NO `exec` con shell. Documenta el paso futuro a contenedor.
- **Testing:** Vitest + fixtures reales + `testcontainers` opcional (marca `BLOCKED` si no hay Docker).
- **Lint/format:** Biome (más rápido y simple que ESLint+Prettier juntos).

Documenta esta decisión en `docs/adr/0002-stack-typescript-unificado.md` con motivo, alternativas y consecuencias.

---

## 2. Estructura de repo objetivo

Crea esta estructura (monorepo pnpm):

```
agntia-ciberseguridad/
├── package.json                    # pnpm workspaces
├── pnpm-workspace.yaml
├── tsconfig.base.json
├── biome.json
├── .nvmrc                          # 20
├── packages/
│   ├── core/                       # dominio puro, sin I/O
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── domain/             # entidades, value objects, errores
│   │   │   ├── policy/             # PolicyEngine interface + impl determinista
│   │   │   ├── adapters/           # AdapterManifest, AdapterContext, AdapterResult
│   │   │   ├── findings/           # normalización, dedupe, historial
│   │   │   ├── budget/             # reservas, ledger
│   │   │   └── index.ts
│   │   └── tests/
│   ├── server/                     # Hono app + endpoints + jobs
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── app.ts              # factory Hono
│   │   │   ├── config.ts           # env validado con Zod
│   │   │   ├── auth/               # principal, tenant, capabilities
│   │   │   ├── middleware/         # auth, tenant-scope, request-id, otel
│   │   │   ├── routes/             # /v1/audits, /v1/findings, /v1/reports, /v1/tools
│   │   │   ├── jobs/               # worker, leases, fencing
│   │   │   ├── storage/            # SQLite driver + migraciones
│   │   │   ├── evidence/           # custodia cifrada + redacción
│   │   │   ├── telemetry/          # otel + prom-client + logger
│   │   │   └── main.ts
│   │   └── tests/
│   ├── adapters/                   # un paquete por adaptador
│   │   ├── gitleaks/
│   │   ├── osv-scanner/
│   │   └── semgrep/
│   ├── sdk/                        # cliente TS para /agente
│   │   ├── package.json
│   │   └── src/client.ts, hono.ts, tools.ts
│   └── agent-tools/                # definiciones de tools para el LLM
│       └── src/definitions.ts      # JSON Schema de cada tool
├── fixtures/                       # repos sintéticos (benigno + vulnerable + secreto canario)
├── scripts/
│   ├── validate_foundation.py      # existente
│   ├── validate_campaign.py        # existente
│   └── demo.ts                     # demo end-to-end del PMV
└── docs/
    └── adr/0002-stack-typescript-unificado.md
```

---

## 3. Contrato de adaptador (LO MÁS IMPORTANTE que falta hoy)

Implementa esto en `packages/core/src/adapters/`:

```ts
// manifest.ts
export const AdapterManifestSchema = z.object({
  id: z.string().regex(/^[a-z0-9-]+$/),
  version: z.string(),                    // pin exacto, ej "8.21.0"
  license: z.string(),                    // SPDX
  capabilities: z.array(z.enum([
    "secret-scan", "sast", "sca", "iac", "sbom", "container"
  ])),
  network: z.enum(["none", "allowlist"]),
  resourceLimits: z.object({
    cpuMs: z.number().int().positive(),
    memMb: z.number().int().positive(),
    timeoutMs: z.number().int().positive(),
    maxOutputBytes: z.number().int().positive(),
  }),
  entrypoint: z.string(),                 // binario o "npx <pkg>@<version>"
  profiles: z.array(z.enum(["static_read", "passive_web", "active_lab"])),
  inputSchema: z.string(),                // JSON Schema del input
  outputSchema: z.string(),               // JSON Schema del output normalizado
});

export type AdapterManifest = z.infer<typeof AdapterManifestSchema>;

export interface AdapterContext {
  tenantId: string;
  jobId: string;
  correlationId: string;
  grantId: string;
  snapshotPath: string;                   // read-only
  workdir: string;                        // temporal, aislado
  env: Record<string, string>;            // allowlist, sin secretos globales
  signal: AbortSignal;
  logger: Logger;
  budget: { reserve(cents: number): Promise<void>; };
}

export type AdapterResult =
  | { status: "ok"; findings: NormalizedFinding[]; coverage: Coverage; artifacts: ArtifactRef[] }
  | { status: "partial"; findings: NormalizedFinding[]; coverage: Coverage; reason: string }
  | { status: "blocked"; reason: string }
  | { status: "failed"; reason: string; retryable: boolean };

export interface SecurityAdapter {
  readonly manifest: AdapterManifest;
  run(ctx: AdapterContext): Promise<AdapterResult>;
}
```

Implementa un **AdapterRegistry** (`packages/core/src/adapters/registry.ts`) que:
- Descubre adaptadores en `packages/adapters/*/manifest.json`.
- Valida manifest con Zod.
- Comprueba que `version` está pineada (no `latest`, no `^`).
- Registra capability → adapter.
- Expone `getForCapability(cap)` y `listAll()`.

---

## 4. Gateway de policy (determinista, fuera del LLM)

Implementa `packages/core/src/policy/`:

```ts
export interface PolicyInput {
  principal: { id: string; tenantId: string; capabilities: string[] };
  action: string;                         // "audit.create", "finding.read", "remediation.propose"
  resource: { type: string; id: string; tenantId: string };
  args: Record<string, unknown>;          // argumentos tipados
  destination?: string;                   // para egress
  dataLabels?: string[];                  // "secret", "pii", "internal", "public"
  policyVersion: string;
}

export type PolicyDecision =
  | { effect: "allow"; reason: string }
  | { effect: "deny"; reason: string }
  | { effect: "require_approval"; reason: string; approvalSpec: ApprovalSpec };
```

Reglas mínimas a implementar (en TS, declarativas, versionadas en `policies/v1.ts`):
1. `deny` si `principal.tenantId !== resource.tenantId`.
2. `deny` si acción no está en `principal.capabilities`.
3. `deny` si `dataLabels` incluye `"secret"` y destino es externo.
4. `deny` si args contienen shell, URLs arbitrarias, o campos desconocidos (Zod strict).
5. `require_approval` si acción es `remediation.execute` o cambia permisos.
6. `allow` solo si todas las reglas anteriores pasan.

**Tests obligatorios:** cross-tenant, capability faltante, exfiltración por composición, args anidados con Unicode, policy stale. Todos ejecutados realmente.

---

## 5. Endpoints Hono mínimos

En `packages/server/src/routes/`:

| Método | Path | Efecto | Auth |
|---|---|---|---|
| GET | `/health/live` | liveness | ninguna |
| GET | `/health/ready` | readiness (DB up) | ninguna |
| POST | `/v1/audits` | crea job (202) idempotente | tenant + capability `audit.create` |
| GET | `/v1/audits/:id` | estado job | tenant scope |
| POST | `/v1/audits/:id/cancel` | cancelación | tenant scope |
| GET | `/v1/findings` | lista scoped + paginada | tenant scope |
| GET | `/v1/findings/:id` | detalle + historial | tenant scope |
| GET | `/v1/reports/:jobId` | reporte JSON | tenant scope |
| POST | `/v1/policy/evaluate` | dry-run de decisión | capability `policy.evaluate` |
| GET | `/v1/tools` | catálogo de tools expuestas al LLM | capability `tool.list` |

**Reglas duras:**
- Auth server-side: principal y tenant derivados de header `Authorization` verificado (HMAC de laboratorio en PMV; documenta OIDC/JWT para producción).
- Middleware de tenant-scope: **toda** query a DB filtra por `tenantId` del principal verificado, nunca del body.
- Idempotencia: header `Idempotency-Key` obligatorio en POST; misma key+payload devuelve mismo job; payload distinto → 409.
- Errores normalizados: `{ code, message, correlationId, retryable, reconciliationRequired }`. Nunca exponer stack traces.

---

## 6. Tools expuestas al LLM (`packages/agent-tools/`)

Cada tool con JSON Schema estricto:

```ts
export const TOOLS = [
  {
    name: "security_audit_create",
    description: "Crea una auditoría sobre un activo autorizado.",
    inputSchema: { /* Zod → JSON Schema */ },
    // NUNCA incluir: approve, elevate, shell, buy, send_email, arbitrary_url
  },
  { name: "security_audit_status", ... },
  { name: "security_findings_list", ... },
  { name: "security_report_get", ... },
  { name: "security_policy_explain", ... },
] as const;
```

Reglas:
- Toda tool pasa por el gateway de policy **antes** de ejecutar.
- Toda tool recibe `correlation_id` y lo propaga a trazas.
- Ninguna tool puede aprobar, elevar permisos, cambiar presupuesto ni ejecutar comandos arbitrarios.
- Test que verifica que el catálogo **no** contiene esas capacidades prohibidas.

---

## 7. Adaptadores del PMV (mínimo 3, reales)

Implementa **en este orden**, cada uno con tests reales contra `fixtures/`:

### 7.1 Gitleaks (`packages/adapters/gitleaks/`)
- `manifest.json`: `version: "8.x.x"` pineada, `license: "MIT"`, `network: "none"`.
- Runner: `spawn("gitleaks", ["detect", "--source", snapshotPath, "--report-format", "json", "--report-path", "/dev/stdout", "--no-git"], { env: allowlist, timeout })`.
- Parser: JSON → `NormalizedFinding[]`, **redactando el secreto** (solo `location`, `rule_id`, `confidence`).
- Test: fixture con canario → finding creado, **canario ausente** de logs, reporte y eventos. Test adversarial: gitleaks falla → `status: "failed"`, NO `ok` con 0 findings.

### 7.2 OSV-Scanner (`packages/adapters/osv-scanner/`)
- `manifest.json`: `version` pineada, `license: "Apache-2.0"`, `network: "allowlist"` (solo `api.osv.dev`).
- Runner: `spawn("osv-scanner", ["--lockfile", "<path>", "--format", "json"])`.
- Parser: JSON → findings con `purl`, `advisory_id`, `severity`, `fixed_version`.
- Test: lockfile con dep vulnerable + lockfile benigno → resultados distintos. Test: sin red → `status: "partial"`, NO `ok`.

### 7.3 Semgrep CE (`packages/adapters/semgrep/`)
- `manifest.json`: `version` pineada, `license: "LGPL-2.1"`, `network: "none"`.
- Runner: `spawn("semgrep", ["--config", "<bundle-local>", "--json", "--no-git-ignore", "--metrics=off", snapshotPath])`.
- Bundle de reglas propias en `rules/semgrep/v1/` (mínimo 3 reglas: hardcoded secret, SQL injection, insecure deserialization).
- Parser: JSON → findings con `rule_id`, `path`, `line`, `severity`, `confidence`.
- Test: fixture vulnerable detectado + variante corregida NO detectada. Test: comentario hostil `// ignore previous instructions` NO modifica el resumen.

**Si una herramienta no se puede instalar/probar en tu entorno:** crea el adaptador con tests `test.skip` marcados `BLOCKED` con motivo concreto en el reporte final. **NO inventes PASS.**

---

## 8. Jobs con leases + fencing (SQLite)

`packages/server/src/jobs/`:
- Tabla `jobs(id, tenant_id, type, payload_json, status, lease_owner, lease_expires_at, fencing_token, attempts, idempotency_key, created_at, updated_at)`.
- Reclamo atómico: `UPDATE jobs SET lease_owner=?, lease_expires_at=?, fencing_token=fencing_token+1 WHERE id=? AND (lease_owner IS NULL OR lease_expires_at < now())`.
- Worker loop: reclama → ejecuta → escribe resultado **solo si** `fencing_token` coincide → ACK.
- Crash simulado: test que mata el worker entre reclamo y ACK → nuevo worker recupera, **no duplica**.
- Revocación: antes de ejecutar efecto externo, revalida `grant` vigente; si revocado → `blocked`.

---

## 9. Evidencia + redacción

`packages/server/src/evidence/`:
- Almacenamiento cifrado (AES-256-GCM con clave de env; documenta KMS para prod).
- Separar: `original` (cifrado), `redacted` (texto plano para reportes), `summary` (LLM, marcado como falible).
- Redacción: regex + allowlist de patrones (secrets, tokens, PII básica). **Documenta que la redacción automática es falible.**
- Test: canario en fixture → ausente de `redacted`, `summary`, logs, métricas OTel. Presente solo en `original` cifrado.

---

## 10. Observabilidad

`packages/server/src/telemetry/`:
- OTel SDK con exporter OTLP configurable por env. **Nunca** exportar `tenant_id`/`user_id` como label de métrica (solo trace attribute).
- `prom-client` con labels acotados: `route`, `method`, `status`, `adapter_id`. **Sin** URLs crudas.
- Logger `pino` con redacción de headers `authorization`, `cookie`, bodies.
- Test: canario secreto NO aparece en spans, métricas, logs. Test: 100k valores distintos de un atributo externo NO crean 100k series (cardinalidad acotada).

---

## 11. SDK para `/agente` (`packages/sdk/`)

```ts
// client.ts
export class SecurityClient {
  constructor(opts: { baseUrl: string; token: string; tenantId: string });
  async createAudit(input: CreateAuditInput, idempotencyKey: string): Promise<AuditJob>;
  async getAudit(id: string): Promise<AuditJob>;
  async listFindings(filter: FindingsFilter): Promise<Paginated<Finding>>;
  async getReport(jobId: string): Promise<Report>;
  async evaluatePolicy(input: PolicyInput): Promise<PolicyDecision>;
  async listTools(): Promise<ToolDefinition[]>;
}
```

```ts
// hono.ts — plugin para montar en /agente
export function securityRoutes(client: SecurityClient): Hono;
```

Reglas:
- Token **nunca** en cliente navegador; solo server-side.
- Tipos generados desde Zod schemas (single source of truth).
- Test de contrato: `packages/sdk/tests/contract.test.ts` que verifica que SDK y server comparten schemas.

---

## 12. Demo end-to-end (`scripts/demo.ts`)

Debe ejecutarse con `pnpm demo` y producir output legible:

1. Arranca server con DB temporal.
2. Crea 2 tenants sintéticos (`tenant-a`, `tenant-b`).
3. Tenant A crea auditoría sobre `fixtures/vulnerable-repo/`.
4. Worker ejecuta Gitleaks + OSV + Semgrep reales.
5. Findings normalizados, sin canario en logs.
6. Tenant B intenta leer finding de A → **404 sin metadatos**.
7. LLM hostil (mock) pide tool prohibida → gateway **deniega** con razón.
8. Genera reporte JSON → incluye `coverage` y `not_tested`.
9. Apaga server, restaura backup, verifica integridad.

Output esperado: exit code 0 + resumen JSON con `status: "PASS"` y conteos reales (findings, latencia, cobertura).

**Si algo no se puede ejecutar:** marca `BLOCKED` con motivo, NO `PASS`.

---

## 13. Tests obligatorios (todos ejecutados de verdad)

- Unit: policy engine (20+ casos), budget ledger, normalización de findings.
- Contract: cada adaptador contra fixture real.
- Integration: jobs con crash/recuperación, idempotencia concurrente, migración fallida revierte.
- Security: cross-tenant (API, DB, reporte, evidencia), revocación entre petición y job, SSRF bloqueado, canario ausente de logs/spans/reportes.
- E2E: `scripts/demo.ts`.
- Performance (básico): 100 audits concurrentes → p95 < umbral definido, sin fugas de memoria.

Cada test debe poder ejecutarse con `pnpm test` y `pnpm test:integration`.

---

## 14. CI (GitHub Actions)

`.github/workflows/ci.yml`:
- `pnpm install --frozen-lockfile`
- `pnpm lint` (Biome)
- `pnpm typecheck` (tsc --noEmit)
- `pnpm test` (Vitest unit)
- `pnpm test:integration` (necesita Docker → `continue-on-error: false` si hay, `skip` si no)
- `python scripts/validate_foundation.py` (existente)
- `python scripts/validate_campaign.py` (existente)

---

## 15. Entregables finales (Definition of Done del PMV)

El agente debe entregar **todo esto** al terminar:

1. ✅ `pnpm install && pnpm build && pnpm test && pnpm demo` funcionan desde cero.
2. ✅ 3 adaptadores reales (Gitleaks, OSV, Semgrep) con tests ejecutados.
3. ✅ Gateway de policy determinista con 20+ tests.
4. ✅ Jobs con leases/fencing, recuperación de crash probada.
5. ✅ Evidencia cifrada + redacción con canario ausente verificada.
6. ✅ OTel + Prometheus + logs estructurados, sin canario, cardinalidad acotada.
7. ✅ SDK TS/Hono con contrato verificado.
8. ✅ `scripts/demo.ts` ejecuta end-to-end y produce PASS real.
9. ✅ `docs/adr/0002-stack-typescript-unificado.md` escrito.
10. ✅ `HANDOFF-COMPLETION.md` en raíz con: qué se hizo, qué se probó (comandos + exit codes), qué quedó `BLOCKED` y por qué, y siguiente paso recomendado.
11. ✅ `docs/integration/PATCHSET-AGENTE.md` con el diff **concreto** (no genérico) para integrar en `/agente`: qué archivos tocar, qué imports, qué rutas montar, qué eventos suscribir.
12. ✅ README actualizado con estado real (no aspiracional) y quickstart.

---

## 16. Reglas de honestidad (no negociables)

- **No inventes PASS.** Si un test no se ejecutó, es `NOT_EXECUTED`. Si falló, es `FAIL`. Si faltó entorno, es `BLOCKED`.
- **No inventes comandos ejecutados.** Cada `PASS` en `HANDOFF-COMPLETION.md` debe tener comando real + exit code + timestamp.
- **No borres la documentación existente.** Añade ADRs para cambios.
- **No modifiques `/agente`.** Solo produce el patchset en `docs/integration/PATCHSET-AGENTE.md`.
- **No compres servicios.** No actives trials. No envíes datos a APIs externas en tests.
- **No expongas secretos.** Canarios en fixtures son sintéticos.
- **Si una decisión de stack no funciona** (ej. `better-sqlite3` no compila en tu entorno), documenta la alternativa usada en el ADR y en `HANDOFF-COMPLETION.md`.

---

## 17. Orden de ejecución sugerido

1. ADR 0002 + estructura monorepo + `package.json` + `pnpm-workspace.yaml` + `tsconfig.base.json` + Biome.
2. `packages/core`: dominio, Zod schemas, adapter manifest, policy engine + tests.
3. `packages/server`: Hono app, auth, tenant-scope, storage SQLite + migraciones, jobs + leases.
4. `packages/adapters/gitleaks` + fixture + test real.
5. `packages/adapters/osv-scanner` + fixture + test real.
6. `packages/adapters/semgrep` + bundle reglas + fixture + test real.
7. Evidencia + redacción + tests canario.
8. Observabilidad + tests cardinalidad/redacción.
9. `packages/sdk` + `packages/agent-tools` + test contrato.
10. `scripts/demo.ts` end-to-end.
11. CI + `HANDOFF-COMPLETION.md` + `PATCHSET-AGENTE.md` + README actualizado.

---

## 18. Qué NO hacer (trampas comunes)

- ❌ No instales 31 herramientas. Solo 3 adaptadores reales bien probados.
- ❌ No uses OPA/Cedar/Redis/Postgres en el PMV. SQLite + policy en TS.
- ❌ No expongas endpoint `/execute` genérico ni `/shell` ni `/fetch`.
- ❌ No confíes en el LLM para autorizar nada. El gateway decide.
- ❌ No pongas `tenant_id` en labels de Prometheus.
- ❌ No marques `PASS` un test que no se ejecutó.
- ❌ No escribas "100% seguro" ni "cero vulnerabilidades" en ningún reporte.
- ❌ No modifiques el repo `/agente`; solo patchset.

---

## 19. Criterio de éxito final

El agente ha terminado cuando, en una máquina limpia con Node 20 + pnpm 9 + Docker opcional:

```bash
pnpm install
pnpm build
pnpm test
pnpm demo
```

…terminan con exit code 0, y `HANDOFF-COMPLETION.md` reporta **honestamente** qué se probó, qué quedó `BLOCKED`, y qué falta para producción. Un PMV con 3 adaptadores reales, policy determinista, jobs recuperables, evidencia cifrada, observabilidad sin fugas, SDK TS/Hono y demo end-to-end **es ultraserio**. Un PMV con 31 adaptadores sin tests es basura.

**Prioriza profundidad sobre amplitud. Honestidad sobre marketing.**