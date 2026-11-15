# Baseline verificado — AD-01

**Repositorio:** `uniscrolliabrain-cloud/agntia-ciberseguridad`
**SHA auditado:** `dd18f2ad5b3fdc54dec28e3eede6a504642fcbc7` (`main`, 2026-11-15 13:37 UTC)
**Rama de trabajo:** `feat/cyber-autodoc-AD-01`
**Fecha de ejecución:** 2026-11-15
**Entorno:** Linux x86_64, Python 3.12.3, Node v26.13.0, `pip install -e '.[dev]'`, `npm ci`.

Esta auditoría **sí ejecutó** tests y scripts. No es una lectura estática como la del programa
original: sustituye sus estimaciones por salidas reales y códigos de salida.

## 1. Resultados medidos

| Comprobación | Comando | Exit | Resultado |
|---|---|---|---|
| Suite Python | `.venv/bin/python -m unittest discover -s tests` | 0 | 196 tests (190 previos + 6 nuevos), **OK (skipped=8)** |
| Contrato Python↔TS | `.venv/bin/python -m unittest tests.contracts.test_python_ts` | 0 | OK tras reparar el build script |
| Suite SDK | `cd typescript && npm test` | 0 | 6 pass, 1 skip, 0 fail |
| Validador documental | `.venv/bin/python scripts/validate_foundation.py` | 0 | PASS, 168 Markdown, 31 registros, 97.250 palabras |
| Estado de release | `.venv/bin/python scripts/release_status.py` | 0 | 42 fases, 294 tareas, `SYNTHETIC_DEMO_NOT_PRODUCTION` |

Lectura de `docs/release/status.json`:

- `production_enabled=false`, `owner_acceptance=PENDING`, `independent_review=PENDING`.
- `phase_counts`: 2 PASS / 40 PARTIAL. `task_counts`: 80 PASS / 214 PARTIAL.

## 2. Superficie real

| Elemento | Valor medido | Fuente |
|---|---|---|
| Rutas `/v1` con tenant | **84** | `create_app(Settings)` vía `tests.support.Fixture` |
| Prefijo obligatorio | `/v1/tenants/{tenant}/…` en todas | mismo |
| Rutas de publicación/despliegue | **0** | mismo |
| Migraciones SQLite | **8** (`CURRENT_SCHEMA=8`) | `agntia_ciberseguridad/storage.py:42` |
| Ficheros de test Python | 31 | `find tests -name 'test_*.py'` |
| Módulos del paquete | 40 ficheros `.py` en la raíz + subpaquetes | `ls agntia_ciberseguridad` |

Las 84 rutas cubren assets, auditorías, findings, evidencias, jobs, outbox, grants, delegaciones,
revisiones, reportes, presupuesto, snapshots, gobernanza, privacidad, fraude, incidentes,
contenciones, remediaciones, workspace, operaciones, logs y agentes. Ninguna publica ni despliega.

## 3. Defecto encontrado y reparado

`typescript/build-runtime.mjs` llamaba a `stripTypeScriptTypes(source,{mode:'transform'})`. Node 26
eliminó `transform` y solo admite `strip`, así que el test de contrato Python↔TS fallaba en un
checkout limpio:

```
TypeError [ERR_INVALID_ARG_VALUE]: The property 'options.mode' must be one of: 'strip'.
Received 'transform'
Ran 190 tests — FAILED (failures=1, skipped=8)
```

Reparación aplicada (la misma ya validada en la rama de documentación): usar el compilador
`typescript` fijado en `node_modules` cuando existe y, si no, `strip` sin modo. Es tooling de
verificación, no runtime de producto; no cambia el comportamiento del servicio ni del SDK.

Tras la reparación: 196/196 OK, contrato OK, SDK 6 pass.

## 4. Qué NO cubre este baseline

- No ejecuta los tests Docker opt-in (8 skips): requieren imágenes de escáneres.
- No ejecuta escaneo real de terceros ni datos de clientes.
- No hay revisión independiente (Codex) ni PR: el conector GitHub devuelve 403.
- No valida CI sobre este SHA: el plan AD no se ha ejecutado en Actions todavía.
- Windows/macOS no probados; solo Linux.

Por tanto: **PASS de reproducibilidad local**, **NOT_VERIFIED** de independencia y CI.

## 5. Contradicciones con el plan AD detectadas en F0

| Afirmación del plan | Realidad medida | Acción |
|---|---|---|
| «`storage.py` migraciones 1–8» | Correcto | Ninguna |
| «`docs/release/status.json`: 2 PASS / 40 PARTIAL, 80/214» | Correcto | Ninguna |
| «lectura selectiva, sin ejecución» | Esta campaña ejecuta y corrige | Documentado aquí |
| «no tocar runtime» | Se tocó solo tooling TS | Justificado en §3; runtime intacto |
