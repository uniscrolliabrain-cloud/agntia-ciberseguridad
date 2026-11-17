# VS-07 — Evidencia

**Base:** `45b5a7a`.

| Comprobación | Comando | Exit | Resultado |
|---|---|---|---|
| Verificación OTel | `.venv/bin/python scripts/verify_observability.py` | **1** | requiere Docker; no disponible aquí |
| Medición piloto | `PYTHONPATH=. .venv/bin/python scripts/measure_pilot.py` | 0 | p50 6,04 ms, p95 7,02 ms, 0 errores |
| Carga con tenancy | `PYTHONPATH=. .venv/bin/python tests/performance/observability_workload.py` | 0 | 100 req, 20 denegaciones esperadas, p95 7,19 ms |
| Reglas de alerta | `infra/observability/alerts.yaml` | — | 5 reglas, sin receptor |

Límites: sin Docker no se validó el colector; sin receptor no hay entrega ni acuse.
