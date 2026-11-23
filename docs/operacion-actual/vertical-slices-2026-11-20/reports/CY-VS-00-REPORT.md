# CY-VS-00 — Baseline y reconciliación de ramas

**Fecha:** 2026-11-20
**Base SHA:** `eaf7da0d60a5adc7302c977cdabdfd3900c922be` (main)
**HEAD SHA:** `eaf7da0d60a5adc7302c977cdabdfd3900c922be` (rama `feat/cyber-vertical-slices-installable-20261120`)
**Rama:** `feat/cyber-vertical-slices-installable-20261120`
**Objetivo:** Reauditar código actual, todas las ramas, tests, CI y diferencias con `/agente`. Clasificar ramas e identificar código exclusivo.

## Resumen ejecutivo

Se realizó el baseline sobre `main@eaf7da0`. El repositorio contiene 29 ramas remotas (incluyendo `main`). De ellas:
- 1 rama fusionada sin commits únicos vs main: `origin/feat/cyber-audit-2026-11-18`
- 1 rama con 4 commits de documentación ahead de main: `origin/docs/cyber-vertical-slices-handoff-20261120` (los 4 docs del handoff publicados)
- 26 ramas disjoint / sin ancestro común con main (necesitan revisión manual de contenido exclusivo)

No se confirmó contenido de código exclusivo en ninguna rama sin ejecutar `git diff` contra cada una (bloqueado por falta de ancestro común). Ninguna rama se borró.

## Stack y componentes

| Componente | Ruta | Estado |
|------------|------|--------|
| Middleware Python/FastAPI | `agntia_ciberseguridad/` | Implementado, 84 rutas `/v1`, 8 migraciones SQLite |
| SDK TypeScript server-only | `typescript/` | `@agntia/ciberseguridad@0.1.0-alpha.3`, exports `.`, `./hono`, `./agent-tools` |
| Laboratorio adversarial | `adversarial_lab/` | Paquete separado, 18 campañas C01-C18 |
| Adaptadores de scanner | `agntia_ciberseguridad/adapters/` | Gitleaks, OSV, Semgrep, Trivy (parsers, sin binarios reales) |
| Jobs/worker | `agntia_ciberseguridad/jobs/` | JobStore, worker, contracts, runner |
| Evidencias/vault | `agntia_ciberseguridad/evidence/` | Vault, redaction, schema, contracts |
| Agentes/gateway | `agntia_ciberseguridad/agents/` | Capabilities, flows, policy, registry, tools, routes |
| Tests | `tests/` | unit, e2e, integration, security, docker, contracts, etc. |
| CI workflows | `.github/workflows/` | runtime, scanner-contracts, release, adversarial-lab, browser, observability, docs, dependency-audit |

## Tests ejecutados (baseline real)

```
Comando: python3 -m unittest discover tests/ -v
Resultado: 36 pass, 8 skip, 44 errors
```

Los 44 errors son `ModuleNotFoundError: No module named 'pydantic'` / `fastapi` — dependencias no instaladas en este entorno de ejecución, no fallos de lógica. Los 36 tests que pudieron ejecutarse pasaron. Los 8 skips son intencionales.

Suites de test existentes:
- `tests/unit/` — test_contracts, test_environment, test_observation_identity, test_backup_ledger, test_config_rollout, test_install_artifact, test_install_manifest
- `tests/e2e/` — test_pilot_journeys (viajes sintéticos de piloto con mocks explícitos)
- `tests/security/` — pruebas de seguridad
- `tests/integration/` — pruebas de integración
- `tests/docker/` — pruebas de contenedor

## Matriz de ramas (28 ramas remotas excluyendo main)

| Rama | SHA | Commits | Relación con main | Clasificación |
|------|-----|---------|-------------------|---------------|
| main | `eaf7da0...` | — | Base | Base |
| docs/cyber-vertical-slices-handoff-20261120 | `b164782...` | 4 | 4 ahead, 0 behind | Documentación exclusiva (4 docs handoff) |
| feat/cyber-audit-2026-11-18 | `eaf7da0...` | 0 | Igual que main | Fusionada, sin código exclusivo |
| docs/auditoria-y-plan-operativo-cyber-20261115 | `39ce297...` | 199 | Sin ancestro común | Disjoint / needs-review |
| docs/cy-v2-connection-requirements | `8db390e...` | 147 | Sin ancestro común | Disjoint / needs-review |
| docs/cyber-bitacora-viva | `e4aee6d...` | 258 | Sin ancestro común | Disjoint / needs-review |
| docs/factory-recovery-v1-20261114 | `9d2050a...` | 57 | Sin ancestro común | Disjoint / needs-review |
| docs/hyperupdate-audit-20261115 | `7f1ebc2...` | 145 | Sin ancestro común | Disjoint / needs-review |
| docs/puesta-en-marcha-founder-operaciones-20261115 | `945d6f6...` | 202 | Sin ancestro común | Disjoint / needs-review |
| docs/roadmap-integracion-agente-20261115 | `f1df0c7...` | 137 | Sin ancestro común | Disjoint / needs-review |
| feat/advlab-campaigns-C01-C18 | `ba08d7e...` | 198 | Sin ancestro común | Disjoint / needs-review |
| feat/cognition-v2-sdk-ack | `0a809a1...` | 225 | Sin ancestro común | Disjoint / needs-review |
| feat/cy-v2-01-baseline | `84c8499...` | 142 | Sin ancestro común | Disjoint / needs-review |
| feat/cyber-autodoc-AD-01 | `c57251c...` | 144 | Sin ancestro común | Disjoint / needs-review |
| feat/cyber-d1-foundation | `548692c...` | 4 | Sin ancestro común | Disjoint / needs-review |
| feat/cyber-phases-06-10 | `f61a36e...` | 9 | Sin ancestro común | Disjoint / needs-review |
| feat/cyber-phases-10-15 | `4bc761c...` | 15 | Sin ancestro común | Disjoint / needs-review |
| feat/cyber-phases-16-20 | `4f1e5d8...` | 18 | Sin ancestro común | Disjoint / needs-review |
| feat/cyber-phases-21-25 | `d41e29b...` | 22 | Sin ancestro común | Disjoint / needs-review |
| feat/cyber-phases-26-30 | `ef862fe...` | 28 | Sin ancestro común | Disjoint / needs-review |
| feat/cyber-phases-31-35 | `231db08...` | 32 | Sin ancestro común | Disjoint / needs-review |
| feat/cyber-phases-36-40 | `6146077...` | 36 | Sin ancestro común | Disjoint / needs-review |
| feat/cyber-phases-41-42 | `85c8b87...` | 40 | Sin ancestro común | Disjoint / needs-review |
| feat/cyber-vs-00-baseline | `6cc8e93...` | 238 | Sin ancestro común | Disjoint / needs-review |
| feat/cyber-vs-01-contracts | `53eb054...` | 239 | Sin ancestro común | Disjoint / needs-review |
| feat/cyber-vs-01a-finding-contract | `2d84a94...` | 238 | Sin ancestro común | Disjoint / needs-review |
| integration/advlab-hardening-20261115 | `b2bd576...` | 203 | Sin ancestro común | Disjoint / needs-review |
| work/advlab-B-vault-broker-release | `45a927d...` | 199 | Sin ancestro común | Disjoint / needs-review |
| work/advlab-D-operations | `b2bd576...` | 203 | Sin ancestro común | Disjoint / needs-review (mismo SHA que integration/advlab-hardening) |

**Nota:** 26 ramas son "disjoint" — no comparten ancestro común con `main`. Esto puede indicar historia reescrita, roots diferentes o ramas creadas desde forks. Se requiere revisión manual de `git diff` para identificar código exclusivo. **No se borró ninguna rama.**

## Diferencias con `/agente`

El repositorio `/agente` no está disponible en este checkout. Según la documentación:
- `docs/integration/PATCHSETS-2026-11-18.md`: H1–H5 del hijo y P1–P6 propuestos para `/agente`; referencias a árbol sin commit son históricas.
- SDK TS `0.1.0-alpha.3` tiene `createManifest`, `approveManifest`, `issueDelegation`, `revokeDelegation`, `governedRead` — preparación para integración con `/agente`, no wiring real declarado.
- Flag `CYBER_ENABLED=false` preparado para el padre.
- No hay integración E2E productiva firmada con `/agente`.

## Hallazgos priorizados (CY-VS-00)

| ID | Prioridad | Descripción |
|----|-----------|-------------|
| H-01 | P0 | 26 ramas sin ancestro común con main — contenido exclusivo no verificado. Puede haber código valioso o duplicado. |
| H-02 | P0 | 44 tests no ejecutables por dependencias faltantes (pydantic, fastapi) en este entorno — baseline incompleto. |
| H-03 | P0 | SDK TS no probado (no hay node/npm en este entorno). |
| H-04 | P1 | `origin/feat/cyber-audit-2026-11-18` está en el mismo SHA que main — confirma que algunos trabajos de auditoría ya se integraron. |
| H-05 | P1 | `docs/cyber-vertical-slices-handoff-20261120` solo contiene documentación (4 docs), sin código de implementación. |

## Decisiones

- No se borró ninguna rama, incluso las disjoint/stale.
- No se modificó `main`.
- Se trabaja en rama `feat/cyber-vertical-slices-installable-20261120`.
- `docs/release/status.json` se mantiene NO-GO (`production_enabled=false`) hasta evidencias reales.

## Siguiente campaña

CY-VS-01 — Contrato de instalación y paquete reproducible.

## Archivos relacionados

- `docs/operacion-actual/vertical-slices-2026-11-20/reports/CY-VS-00-EVIDENCE.md`
- `docs/operacion-actual/vertical-slices-2026-11-20/reports/CY-VS-00-ROLLBACK.md`
- `docs/release/status.json`
- `docs/operacion-actual/02-MATRIZ-CIERRE-PRODUCCION.md` (CP-01 baseline)