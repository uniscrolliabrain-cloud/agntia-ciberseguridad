# AD-01 — Reporte de campaña

**Campaña:** AD-01 · Baseline verificable y mapa de integración
**Rama:** `feat/cyber-autodoc-AD-01`
**SHA inicial:** `dd18f2ad5b3fdc54dec28e3eede6a504642fcbc7`
**SHA final:** el de esta rama tras el commit de AD-01
**Fecha:** 2026-11-15
**Entorno:** Linux x86_64, Python 3.12.3, Node v26.13.0
**Estado:** **PASS (local)** — pendiente revisión independiente y CI.

## 1. Alcance ejecutado

AD-01 pedía fijar SHA, registrar migraciones, rutas, dependencias y gates, comprobar que los
reportes no contradicen `status.json`, y dejar baseline, ownership y trazabilidad. Se ha hecho con
ejecución real, no con lectura estática.

## 2. Comandos y resultados

| Comando | Exit | Resultado |
|---|---|---|
| `python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'` | 0 | Entorno reproducible |
| `.venv/bin/python -m unittest discover -s tests` | 1 → **0** | 1 fallo inicial de tooling; reparado; después 196 tests OK, 8 skips |
| `.venv/bin/python -m unittest tests.contracts.test_python_ts` | 0 | Contrato Python↔TS OK |
| `cd typescript && npm ci` | 0 | Dependencias fijadas por lockfile |
| `cd typescript && npm test` | 0 | 6 pass, 1 skip, 0 fail |
| `.venv/bin/python scripts/validate_foundation.py` | 0 | PASS, 168 Markdown, 31 registros |
| `.venv/bin/python scripts/release_status.py` | 0 | 42 fases, 294 tareas, demo sintética |
| `.venv/bin/python -m unittest tests.autodoc.test_baseline_inventory` | 0 | 6 tests nuevos OK |

## 3. Ficheros

Creados:

- `docs/autodoc/BASELINE-AUDIT.md`
- `docs/autodoc/FILE-OWNERSHIP.md`
- `docs/autodoc/TRACEABILITY.md`
- `tests/autodoc/test_baseline_inventory.py`
- `docs/autodoc/reports/AD-01-REPORT.md` (este fichero)

Modificado:

- `typescript/build-runtime.mjs` — Node 26 eliminó `mode:'transform'`; se usa el `tsc` fijado y, si
  no está, `strip` sin modo. Solo tooling de verificación; runtime de producto intacto.

No modificado: `app.py`, `features.py`, `storage.py`, `evidence/vault.py`, `events/outbox.py`,
`jobs/worker.py`, `docs/release/status.json`.

## 4. Hallazgos

1. **P0 resuelto:** checkout limpio fallaba 1 test por incompatibilidad Node 26. Ahora 190/190.
2. **Confirmado:** 84 rutas `/v1`, todas con tenant en la ruta; 0 rutas de publicación.
3. **Confirmado:** esquema 8, 2 PASS / 40 PARTIAL, 80/214 tareas, `production_enabled=false`.
4. **Límite:** 8 tests Docker skipped; sin escáneres reales en esta sesión.

## 5. Gate

| Gate | Estado | Motivo |
|---|---|---|
| G1 seguridad | PASS local | Sin nuevas superficies; solo tooling y docs; test de aislamiento de rutas |
| G2 funcionalidad | PASS local | Suite completa verde (196) |
| G3 reproducibilidad | PASS local | Mismos comandos y versiones; fallo inicial reproducido y corregido |
| G4 privacidad | PASS local | Sin datos reales; sin secretos nuevos |
| G5 evidencia | PASS local | Comandos, exits, SHA y artefactos registrados |

**Decisión:** PASS de campaña en local. `NOT_VERIFIED` para revisión independiente (Codex), PR y
CI, que no están disponibles en este entorno.

## 6. Riesgos y falsos positivos

- Riesgo: el test de inventario fija el número de fases y conteos; un cambio legítimo de estado
  exigirá actualizarlo junto con el reporte. Es intencional: evita deriva silenciosa.
- Falso positivo descartado: el fallo inicial no era del producto ni de Python, era del script de
  build en Node 26.
- No se afirma que el producto sea seguro ni completo: sigue siendo demo sintética.

## 7. Rollback

1. `git revert` del commit de AD-01 en la rama.
2. Si solo se revierte el tooling: restaurar `typescript/build-runtime.mjs` a `dd18f2a` y aceptar
   que el contrato vuelve a fallar en Node ≥26.
3. No hay migración ni cambio de datos: no se requiere backup.

## 8. Siguiente campaña

AD-02 (modelo canónico de run, estado y claims) puede empezar: `contracts.py` y `jobs/schema.py`
auditados; sin conflicto de ownership con AD-01.
