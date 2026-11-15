# CY-V2-01 — Reporte de ejecución

## Identificación

- **Campaña:** CY-V2-01 · Baseline verificable y reconciliación documental.
- **Rama:** `feat/cy-v2-01-baseline` desde `main` `b2cea46bd03e1eafec2f31eff96db1a07890a23c`.
- **SHA base:** `b2cea46`. **SHA final:** `0b8dd9d` (rama publicada, sin fusionar).
- **PR:** pendiente de abrir tras la revisión del diff.
- **Fecha:** 2026-11-15.
- **Estado:** **NOT_VERIFIED** — gates locales superados; CI y revisión independiente pendientes.

## Objetivo

Congelar SHA, árbol, tests, skips y deuda; reconciliar documentación con el código real; reparar
solo los defectos de tooling que impedían reproducir el baseline; no promocionar ninguna fase.

## Baseline y capacidades previas

`main` contiene una demo sintética funcional: FastAPI, 88 rutas, cuatro adaptadores offline, jobs
con leases, evidencia cifrada, agentes con policy, gobernanza, ledger, SDK TS/Hono y UI piloto.
`docs/release/status.json` declara 2 fases PASS y 40 PARTIAL. El inventario completo está en
[BASELINE.md](../BASELINE.md).

## Decisiones arquitectónicas

- No se reconstruye ninguna capacidad existente; solo se corrige tooling roto.
- El build de runtime del SDK prefiere el `tsc` pineado y mantiene `strip` como fallback offline,
  porque el modo `transform` desapareció en Node 26 y `strip` no soporta parameter properties.
- `validate_foundation.py` excluye directorios de dependencias: validar documentación no debe
  depender de que `node_modules` esté limpio ni de su contenido.

## Archivos creados

- `docs/campanas-cy-v2/BASELINE.md`
- `docs/campanas-cy-v2/reportes/CY-V2-01-REPORT.md`
- `docs/campanas-cy-v2/ESTADO-GLOBAL.md`

## Archivos modificados

- `typescript/build-runtime.mjs` — compilador pineado con fallback; corrige el contrato Node 26.
- `scripts/validate_foundation.py` — ignora `node_modules`, `.venv`, `dist`, `__pycache__`.

## Contratos y migraciones

Sin cambios de contrato ni migraciones. El DTO TS y los esquemas Pydantic siguen sincronizados
(`export_schemas.py` sin diff).

## Tests ejecutados

| Comando | Exit | Resultado |
|---|---:|---|
| `python -m unittest discover -s tests` | 0 | 190 tests, 8 skipped, 0 fail |
| `python -m unittest tests.contracts.test_python_ts -v` | 0 | contrato real Node↔FastAPI |
| `cd typescript && npm test` | 0 | 7 tests, 6 pass, 1 skip |
| `python scripts/export_schemas.py && git diff --exit-code docs/implementation/schemas` | 0 | sin drift |
| `python scripts/check_distribution.py` | 0 | distribución válida |
| `PYTHONPATH=. python scripts/evaluate_agent_gateway.py` | 0 | 16/16 adversariales rechazados, 8/8 benignos, p95 4,2 ms |
| `PYTHONPATH=. python scripts/measure_agent_stop.py` | 0 | 10/10 llamadas denegadas tras stop, p95 6,8 ms |
| `python scripts/validate_foundation.py` | 0 | 162 Markdown, PASS |

Antes de los arreglos: 190 tests con **1 FAIL** (`ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`) y
`validate_foundation.py` con `JSONDecodeError`. Después: 0 FAIL.

## Tests omitidos y motivo

- 8 tests de `tests/docker/` (`Docker integration not requested`, `Real Docker extended tools not
  requested`): son opt-in y en esta sesión no se ejecutaron escáneres reales. Estado
  **NOT_VERIFIED**, no PASS.
- 1 test de SDK omitido porque el contrato live ya lo cubre el runner de Python.

## Resultados CI

Push de `0b8dd9d`: **6/6 workflows completados, 0 fallos, 0 en curso**
(`scanner-contracts` 43664454716, `runtime` 43664454717, más browser, observability, docs y
release). Evidencia consultada vía API de Actions, no reutilizada de auditorías anteriores.
La revisión independiente sigue pendiente, por eso la campaña no se marca PASS.

## Hallazgos de seguridad

- El defecto de tooling no era explotable, pero rompía la verificación del contrato Python↔TS en
  runtimes nuevos y podía pasar desapercibido como «fallo de entorno».
- Ningún hallazgo nuevo de autorización o aislamiento; la matriz adversarial es CY-V2-02.

## Riesgos residuales

- CI y revisión independiente pendientes; sin ellas la campaña no puede declararse aceptada.
- Sandbox/escáneres reales sin ejecutar en esta sesión.
- Sin integración con `/agente` (campañas 08 y 38).

## Revisión Codex

**REVIEW_PENDING.** Codex no está disponible en esta sesión; no se simula su veredicto.

## Rollback y recuperación

Revertir los dos archivos de tooling restaura el baseline anterior. No hay migraciones ni datos
afectados; el árbol de `main` permanece intacto hasta que se autorice el merge.

## Dependencias para la siguiente campaña

CY-V2-02 (auth adversarial y aislamiento tenant) puede empezar sobre este baseline. Requiere que
el PR de CY-V2-01 esté abierto y que su CI se ejecute; si CI falla, se corrige antes de continuar.

## Desviaciones respecto al plan

- No se ejecutaron las 12 campañas diferenciales completas: se reconciliaron en la matriz de
  solapamiento y se asignaron a las campañas CY-V2 correspondientes.
- No se modificó `docs/release/status.json`: no hay pruebas nuevas de fases que justifiquen
  promocionar 40 PARTIAL.

## Recomendaciones

1. Abrir PR y dejar que CI ejecute Python 3.11/3.12, SDK, docs y scanner contracts.
2. Programar los tests Docker con opt-in en el runner antes de cerrar G0.
3. No promover ninguna fase de `status.json` por este trabajo.

## Decisión de cierre

**NOT_VERIFIED.** El baseline es reproducible localmente (190 tests OK) y los dos defectos de
tooling están corregidos, pero el gate exige CI y revisión; ninguno de los dos existe aún.
