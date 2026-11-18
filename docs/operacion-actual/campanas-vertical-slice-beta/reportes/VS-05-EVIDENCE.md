# VS-05 — Evidencia

**Base:** `24bd252`.

| Comprobación | Comando | Exit | Resultado |
|---|---|---|---|
| Entorno | `python3 -m venv .venv && pip install -e '.[dev]'` | 0 | Python 3.12.3, FastAPI 0.141.1 |
| Jobs | `.venv/bin/python -m unittest tests.integration.test_jobs -v` | 0 | 15 OK, incluida cancelación en vuelo |
| Suite | `.venv/bin/python -m unittest discover -s tests` | 0 | 197 OK (8 skipped) |
| Validador | `python3 scripts/validate_foundation.py` | 0 | PASS |

Secuencia: submit → claim → escaneo suspendido → cancel con revisión vigente → heartbeat detecta →
tarea cancelada → `reconciliation_required` → `job_results` vacío.

Límites: sin Docker no se probó kill de contenedor; workers en el mismo proceso.
