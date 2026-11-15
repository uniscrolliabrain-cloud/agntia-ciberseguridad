# CY-V2 — Baseline verificable (CY-V2-01)

**Fecha:** 2026-11-15. **Rama:** `feat/cy-v2-01-baseline`. **SHA base:** `b2cea46bd03e1eafec2f31eff96db1a07890a23c`
(`main` tras PR #12 y cierre de ramas legacy). **Estado del producto:** `SYNTHETIC_DEMO_NOT_PRODUCTION`,
`production_enabled=false`, `owner_acceptance=PENDING`, `independent_review=PENDING`.

Este documento fija el estado real del árbol antes de tocar módulos funcionales. Sustituye a
cualquier afirmación de los documentos históricos que no coincida con el código de este SHA.

## 1. Inventario real

| Superficie | Medida verificada |
|---|---|
| Paquete Python | 85 módulos, 5.666 líneas en `agntia_ciberseguridad/` |
| Rutas HTTP | 88 decoradores en 9 módulos de rutas (`app.py`, `agents/routes.py`, `governance/routes.py`, `billing/routes.py`, `observability_routes.py`, `workspace.py`, `features.py`, `reports.py`, `auth.py`) |
| Tests | 44 archivos, 2.918 líneas (`security/` 15, `integration/` 9, `contracts/` y `docker/` 4, `unit/` 4, `evaluations/` 3, `e2e/` 2, `performance/` 1) |
| Adaptadores | Gitleaks, OSV, Semgrep, Trivy (`adapters/`, con `common.py`) |
| SDK TypeScript | `typescript/` con `client.ts`, `hono.ts`, `agent-tools.ts`, `contracts.ts`; 7 tests Node |
| UI piloto | `agntia_ciberseguridad/web/console.{html,css,js}` |
| Scripts | 29 en `scripts/` (demo, benchmarks, backup, release, validadores, observabilidad) |
| CI | 6 workflows: runtime, scanner-contracts, browser, observability, docs, release |
| Documentación | 159 archivos Markdown en `docs/`; 162 validados por `validate_foundation.py` |
| Configuración | `config/plans.json` (Lite 30 €, L 70 €, XL 300 €, `DESIGN_ONLY_NOT_ENFORCED`), reglas Semgrep propias |

## 2. Capacidades comprobadas por inspección

- **Identidad y tenancy:** principales explícitos, token hash con `compare_digest`, revocación,
  roles/capacidades y guard de agente; tenant resuelto en servidor.
- **Autorización de trabajo:** assets, grants con aprobación/revocación, snapshots y jobs.
- **Scanners:** cuatro adaptadores offline con contrato de sandbox; el runner real exige Docker y
  opt-in explícito.
- **Persistencia:** SQLite con migraciones, leases/fencing en worker, idempotencia por clave.
- **Evidencia:** vault cifrado, redacción, retención/hold, originales con motivo y auditoría.
- **Findings:** normalización, deduplicación, historial y estados (`not_tested`…`verified_fixed`).
- **Agentes:** registry de tools/flows, MCP nominado, aprobaciones y evaluación adversarial
  scripted (16 adversariales rechazados, 8 benignos completados, 0 llamadas a modelos externos).
- **Gobernanza y negocio:** incidentes, remediación revisable, privacidad/legal, ledger de
  reservas, observabilidad OTel y workspace.
- **SDK:** cliente TS/Hono con DTOs espejo de Pydantic; contrato real Node↔FastAPI por loopback.

## 3. Baseline de pruebas (ejecutado, no inferido)

Entorno: Python 3.12.3, Node v26.13.0, macOS/Linux sandbox, Docker 29.1.3 presente.

| Comando | Exit | Resultado |
|---|---:|---|
| `python -m unittest discover -s tests` | 0 | **190 tests OK, 8 skipped** |
| `python -m unittest tests.contracts.test_python_ts -v` | 0 | 1 test OK tras el arreglo del punto 4 |
| `python scripts/export_schemas.py` + `git diff` | 0 | esquemas sincronizados |
| `python scripts/check_distribution.py` | 0 | distribución válida |
| `PYTHONPATH=. python scripts/evaluate_agent_gateway.py` | 0 | 16/16 adversariales rechazados, 8/8 benignos, p95 4,2 ms |
| `PYTHONPATH=. python scripts/measure_agent_stop.py` | 0 | kill-switch: 10/10 siguientes llamadas denegadas, p95 6,8 ms |
| `cd typescript && npm test` | 0 | 7 tests, 6 pass, 1 skip |
| `python scripts/validate_foundation.py` | 0 | PASS documental, 162 Markdown |

**Skips y su motivo real:** 8 tests de `tests/docker/` omitidos con
`Docker integration not requested`, `Real Docker extended tools not requested` y
`Docker integration not requested; no sandbox claim`. Son opt-in: la capacidad Docker existe, pero
en esta sesión **no se ejecutaron escáneres reales**. El skip de SDK corresponde al contrato live
cuando el propio runner de Python ya lo cubre.

**CI:** no se ha ejecutado ningún workflow de GitHub para este SHA. Toda afirmación de CI en este
documento es histórica y queda `NOT_VERIFIED` hasta que exista PR y run asociado.

## 4. Defectos de baseline encontrados y corregidos

1. **Contrato Python↔TS roto en Node ≥26.** `typescript/build-runtime.mjs` llamaba a
   `stripTypeScriptTypes(..., {mode:'transform'})`; Node 26 rechaza `transform` y el modo `strip`
   no soporta parameter properties (`constructor(public readonly kind: ...)`). El test
   `test_actual_node_client_reads_python_dtos_and_safe_errors` fallaba con
   `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`. Arreglo: el script usa el `tsc` pineado cuando está
   instalado y conserva `strip` como fallback offline. Antes: 1 FAIL; después: 190 OK.
2. **`validate_foundation.py` fallaba con dependencias instaladas.** Recorría `*.json` de
   `node_modules`/`.venv`, incluyendo archivos con comentarios. Arreglo: excluye `node_modules`,
   `.venv`, `dist`, `__pycache__` y `.git`. Antes: `JSONDecodeError`; después: PASS.

Ambos son reparaciones de tooling, no cambios de comportamiento de seguridad.

## 5. Ramas y PR

- `main` = `b2cea46` («docs: registrar cierre PR legacy y limpieza segura pendiente de refs»).
- Ramas legacy `docs/factory-recovery-v1-20261114`, `docs/roadmap-integracion-agente-20261115` y
  `feat/cyber-phases-*`: verificadas sin commits exclusivos; **no eliminadas** (el conector no
  expone delete-ref). Ver [CIERRE-RAMAS-LEGACY.md](CIERRE-RAMAS-LEGACY.md).
- Esta campaña trabaja en `feat/cy-v2-01-baseline`, un PR, sin force-push.

## 6. Matriz de solapamiento CY-R ↔ CY-V2

| CY-R | Tema | Campañas CY-V2 que lo absorben | Estado previo |
|---|---|---|---|
| R01 | Baseline, CI y verdad documental | CY-V2-01 | Este documento |
| R02 | Auth y autorización adversarial | CY-V2-02 | P0 abierto |
| R03 | Límites de entrada, snapshots, sandbox | CY-V2-03 | P0 abierto |
| R04 | Cobertura de escáneres y falsos negativos | CY-V2-04 | P1 |
| R05 | Persistencia, jobs, replay | CY-V2-05 | P0 abierto |
| R06 | Custodia, cifrado, restore | CY-V2-06 | P0 abierto |
| R07 | Gateway de agentes, MCP, exfiltración | CY-V2-07, CY-V2-23..25 | P0 abierto |
| R08 | Contratos SDK y padre | CY-V2-08, CY-V2-38 | P1 |
| R09 | Observabilidad y alertas | CY-V2-17, CY-V2-36 | P2 |
| R10 | Costes y reservas | CY-V2-42 | P2 |
| R11 | Legal, privacidad y DPA | CY-V2-41 | P2 |
| R12 | Piloto y aceptación | CY-V2-40, CY-V2-41 | Bloqueado por gates |

## 7. Riesgos residuales del baseline

- **P0:** no hay CI ejecutada para este SHA; no hay revisión independiente ni pentest.
- **P0:** los tests de sandbox/escáneres reales siguen sin ejecutarse en esta sesión.
- **P1:** sin integración verificada con `/agente`; el bundle de capacidades está sin cablear.
- **P1:** autenticación y aislamiento tenant solo cubiertos por la suite existente, no por la
  matriz adversarial que exige CY-V2-02.
- **P2:** licencias de binarios/reglas/feeds pendientes de revisión legal; sin DPA.

## 8. Referencias

- [Reporte CY-V2-01](reportes/CY-V2-01-REPORT.md)
- [Estado global](ESTADO-GLOBAL.md)
- [Programa de 42 campañas](PROGRAMA-42-CAMPANAS-FREEBUFF.md)
- [Auditoría funcional](../auditoria-runtime/AUDITORIA-FUNCIONAL-2026-11-14.md)
