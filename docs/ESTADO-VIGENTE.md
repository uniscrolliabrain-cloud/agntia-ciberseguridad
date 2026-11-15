# Estado vigente — verdad medida del repositorio

**Fecha:** 2026-11-15. **Sustituye a cualquier cabecera anterior** como resumen operativo.
**Base medida:** `main@dd18f2ad5b3fdc54dec28e3eede6a504642fcbc7` y rama `feat/cyber-autodoc-AD-01` (`c57251c`).
**Naturaleza:** demo sintética. `production_enabled=false` en `docs/release/status.json`.

Este documento no sustituye al código ni a `docs/release/status.json`: los resume y explica qué
documentos están desactualizados y por qué.

## 1. Hechos medidos (no estimados)

| Hecho | Valor | Cómo se comprobó |
|---|---|---|
| Tests Python | **196 OK**, 8 skipped (Docker opt-in) | `unittest discover -s tests` |
| Contrato Python↔TS | OK en Node 26 tras reparar el build | `tests.contracts.test_python_ts` |
| SDK TypeScript | 6 pass, 1 skip, 0 fail | `cd typescript && npm test` |
| Rutas API | **84** bajo `/v1/tenants/{tenant}/…` | `create_app` vía `tests.support.Fixture` |
| Rutas de publicación/despliegue | **0** | mismo inventario + test AD-01 |
| Esquema SQLite | **8** migraciones (`CURRENT_SCHEMA=8`) | `storage.py` |
| Validador documental | PASS, 168 Markdown, 31 registros | `scripts/validate_foundation.py` |
| Gates de producto | **2 fases PASS / 40 PARTIAL**, 80/214 tareas | `scripts/release_status.py` |
| Revisión independiente | **PENDIENTE** | `status.json` |
| PR de las ramas nuevas | **NO CREADO** (conector GitHub 403) | intento real |
| Escáneres reales contra clientes | **NO EJECUTADOS** | 8 tests Docker skipped |

## 2. Mapa de ramas

| Rama | HEAD | Contenido | Estado |
|---|---|---|---|
| `main` | `dd18f2a` | Programa AD-01→AD-15, auditoría estática previa | Referencia; sin los trabajos de abajo |
| `feat/cyber-autodoc-AD-01` | `c57251c` | AD-01 ejecutada + reparación Node 26 | Pusheada, sin PR |
| `docs/cy-v2-connection-requirements` | `8db390e` | Concept Master, plan maestro, arquitectura E/S, stack | Pusheada, sin PR |
| `feat/cy-v2-01-baseline` | `84c8499` | Baseline CY-V2-01 anterior | Superada por AD-01 |

Ninguna rama nueva está fusionada. Nada de esto autoriza escribir en `/agente`.

## 3. Programa AD

| Campaña | Estado | Evidencia |
|---|---|---|
| AD-01 baseline verificable | **PASS local** | `docs/autodoc/BASELINE-AUDIT.md`, `reports/AD-01-REPORT.md` |
| AD-02 modelo de run y claims | Pendiente | — |
| AD-03…AD-15 | Pendientes | Plan en `docs/autodoc/PROGRAMA-15-CAMPANAS-ULTRAGRANULARES.md` |

AD-01 encontró y reparó un defecto real: `typescript/build-runtime.mjs` usaba `mode:'transform'`,
eliminado en Node 26. Sin esa reparación, un checkout limpio fallaba 1 test.

## 4. Contradicciones corregidas

| Documento | Decía | Realidad 2026-11-15 |
|---|---|---|
| `README.md` | «Estado al 2026-11-10: middleware en desarrollo» | API, SDK y 196 tests medidos; sigue sin ser producción |
| `docs/README.md` | «Las tareas están NOT_STARTED» | 80 PASS / 214 PARTIAL |
| `docs/02` | «no servicios implementados» | 84 rutas, worker, outbox y vault implementados |
| `docs/03` | Propuestas «todavía no implementadas» | Gateway, manifiestos, delegación y preflight existen offline |
| `docs/04` | «Ninguno se ha instalado, ejecutado o auditado» | Cuatro adaptadores implementados con fixtures |
| `docs/09` | «No describen endpoints implementados» | El prefijo `/v1/tenants/{tenant}` existe con 84 rutas |
| `docs/10` | «No hay escáneres instalados» | Adaptadores offline y CI de contratos; sin clientes reales |
| `docs/12` | «No hay … API runtime, scanners instalados» | Falso a esta fecha: hay API y adaptadores |
| `handoff_freebuff.md` | «Código de runtime: inexistente»; unificar en TypeScript | Hay paquete Python + SDK TS server-only; el stack TS único fue descartado |
| `docs/release/FOUNDER-REPORT.md` | «main no se ha fusionado» | Fusionado por PR #10/#11 y hoy en `dd18f2a` |
| `docs/autodoc/PROGRAMA-15…` | «PLANIFICADO, NO IMPLEMENTADO» | AD-01 ejecutada y documentada |

Ninguna corrección elimina el texto original: cada documento conserva su historia y añade el aviso
arriba.

## 5. Lo que sigue sin verificarse

- Revisión independiente (Codex u otra IA) de auth, cross-tenant, cifrado, restore e idempotencia.
- PR formal y CI sobre las ramas nuevas.
- Escáneres reales, DAST, cloud posture, EDR o SOC: no existen por tener adaptadores offline.
- Integración en `/agente`: no hay contrato firmado ni patchset aprobado.
- Licencia, DPA, canal privado de divulgación, operadores y aceptación del owner.

## 6. Regla de actualización documental

1. Cada documento empieza con un bloque `ACTUALIZACIÓN` fechado; el más reciente arriba.
2. El bloque dice qué sigue vigente, qué quedó obsoleto y dónde está la fuente.
3. No se reescribe el cuerpo histórico: se corrige encima y se enlaza la evidencia.
4. Ninguna afirmación de capacidad sin comando, SHA y código de salida.

## 7. Próximo paso

AD-02 (contratos de run, estado y claims) sobre `contracts.py` y `jobs/schema.py`. Antes de
fusionar nada: abrir PR y obtener revisión independiente.
