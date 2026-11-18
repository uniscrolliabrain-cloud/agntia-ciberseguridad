# VS-07C — Evidencia

**Base:** `eca27cb` · `.venv` Python 3.12 · sin Docker · 2026-11-17.

## Validación documental

```
$ .venv/bin/python scripts/validate_foundation.py
{"status": "PASS", "scope": "documentation, repository metadata and planned budget consistency only",
 "markdown_files": 293, "repository_metadata_records": 31, "security_scans_executed": 0}
```

El validador comprueba que existen todos los Markdown declarados y que cada enlace local resuelve;
los tres enlaces del runbook (`VS-07A-REPORT.md`, `VS-07B-REPORT.md`) pasan.

## Suite sin cambios de código

```
Ran 215 tests in 33.303s
OK (skipped=8)
```

Sin delta de código: no hay prueba nueva que ejecutar. **No** se declara PASS de operación.

## Comprobaciones de exactitud hechas al escribir el runbook

| Afirmación | Comprobación |
|---|---|
| `/metrics` existe y exige token | `agntia_ciberseguridad/features.py` registra `/metrics`; `telemetry/api.py` compara el token de `Settings.metrics_token_env` |
| `/health/live` y `/health/ready` existen | `app.py` líneas 157 y 161 |
| El receptor acusa sin contener | `scripts/alert_sink.py` devuelve `acknowledged: true`, `contained: false`; probado en `test_alert_delivery` |
| Hay seis reglas | `infra/observability/alerts.yaml`; `test_alert_delivery` fija el número en 6 |
| El cupo lo consume la reserva | `job_reservations.units`; `JobStore._submit` compara la suma con `max_requests` |

## Límites

- No se ejecutó ningún colector real ni se recorre el runbook con una persona: es un borrador
  revisable, no un procedimiento ensayado.
- No hay propietario ni horario: el gate de operación sigue cerrado por decisión, no por código.
