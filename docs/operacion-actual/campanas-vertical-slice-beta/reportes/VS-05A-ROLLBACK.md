# VS-05A — Rollback

Los dos archivos son nuevos y solo se importan entre sí y desde las pruebas.

1. `git rm agntia_ciberseguridad/jobs/runner.py tests/integration/test_worker_runner.py`
2. Reejecutar `python -m unittest discover -s tests` → **208 tests** (215 − 7).
3. No hay esquema, migración, configuración ni datos que revertir.

## Efecto

- Desaparece la única parada ordenada por `SIGTERM`/`SIGINT`; el proceso de worker, cuando exista,
  volvería a morir abruptamente y a depender solo de la expiración de lease.
- `Worker`, `JobStore` y la API no cambian: nada de producción importa `runner.py` todavía.
- Los jobs que quedaron `reconciliation_required` por una parada anterior conservan su estado y
  siguen necesitando `reconcile`; el rollback no los toca.
