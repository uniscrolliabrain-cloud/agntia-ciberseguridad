# VS-07B — Evidencia

**Base:** `acccf0d` · `.venv` Python 3.12 · sin Docker · receptor local en `127.0.0.1` · 2026-11-17.

## Simulacros

```
$ .venv/bin/python -m unittest tests.integration.test_p3_drills -v
test_drill_backup_failure_fails_closed_and_reports_no_signal_path ... ok
test_drill_budget_exhausted_pages_before_the_next_admission ... ok
test_drill_scanner_down_retries_then_pages_incomplete_coverage ... ok

Ran 3 tests in 2.185s
OK
```

### D1 — escáner caído

```
intento 1 → state=pending  error_code=runner_unavailable
intento 2 → state=failed   error_code=runner_unavailable
agntia_scan_coverage_total{coverage="incomplete"} 2
agntia_job_transitions_total{tool="gitleaks",state="failed"} 1
SELECT count(*) FROM job_results → 0
alerta AgntiaDeclaredScanCoverageIncomplete (warning) → 202
receipt: acknowledged=true, contained=false, job_id=<job>, deduplicated=false
segundo envío idéntico → deduplicated=true, una sola línea de estado
```

### D2 — backup fallido

```
backup_lab(quiesced=False)                 → DomainError lab_only (403)
backup_lab(quiesced=True, sin clave)       → DomainError backup_key_unavailable (424)
destino creado                              → False
reglas con "Backup" en alerts.yaml          → []
series agntia_*backup* en la exposición     → []
acuses en el receptor                       → 0
```

Resultado del simulacro: **BLOCKED**. La prueba falla si alguien añade una señal de backup, para
forzar la repetición del simulacro en lugar de dejar el hueco silencioso.

### D3 — presupuesto agotado

```
20 admisiones × 5 intentos → reservas suman 100
21.ª admisión              → DomainError quota (429), sin fila nueva
SELECT count(*) FROM jobs  → 20
agntia_job_admission_rejections_total{reason="quota"} 1
alerta AgntiaAttemptBudgetExhausted (warning) → 202, acknowledged=true, contained=false
```

## Entrega con la sexta regla

```
$ .venv/bin/python -m unittest tests.integration.test_p3_drills tests.integration.test_alert_delivery
Ran 9 tests in 5.417s
OK
```

`test_every_declared_rule_can_be_delivered_and_correlated_to_its_job` lee `- alert:` del YAML y
compara el número: con la regla nueva el valor esperado pasó de 5 a 6, así que un cambio de YAML sin
prueba rompe la suite.

## Suite y documentación

```
Ran 215 tests in 33.303s
OK (skipped=8)
```

```
{"status": "PASS", "scope": "documentation, repository metadata and planned budget consistency only",
 "markdown_files": 288, "repository_metadata_records": 31, "security_scans_executed": 0}
```

`tests/integration/test_telemetry.py` sigue imponiendo `series_count() < 25`: el contador nuevo solo
aparece cuando hay un rechazo, no infla la exposición en reposo.

## Límites

- El predicado PromQL se traduce a "el contador creció", no se evalúa con Prometheus.
- El receptor es local; no hay proveedor, turno ni escalado a persona.
- El simulacro de backup no genera ni restaura una copia: solo prueba el fallo cerrado y la ausencia
  de monitor.
- Todo ocurre contra el fixture de pruebas, no contra una API desplegada.
