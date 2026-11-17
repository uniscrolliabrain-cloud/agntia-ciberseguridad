# VS-07D — Evidencia

**Base:** `7fdb14e` · `.venv` Python 3.12 · sin Docker, sin Prometheus · Linux local · 2026-11-17.

## Simulacro D2 repetido

```
$ .venv/bin/python -m unittest tests.integration.test_p3_drills -v
test_drill_backup_failure_pages_through_the_ledger_and_recovers_after_a_verified_backup ... ok
test_drill_budget_exhausted_pages_before_the_next_admission ... ok
test_drill_scanner_down_retries_then_pages_incomplete_coverage ... ok

Ran 3 tests in 2.1s
OK
```

Secuencia observada dentro del simulacro:

```
API expone agntia_backup_last_success_timestamp_seconds    → False (no inventa backups)
backup_lab(quiesced=False)                                 → DomainError lab_only (403)
backup_lab(quiesced=True, sin clave)                       → DomainError backup_key_unavailable (424)
destino del intento fallido creado                         → False
ledger.record('failure', reason='backup_key_unavailable')  → línea JSON, fichero 0600
exporter.write(ledger, textfile)                           → agntia_backup_last_success_timestamp_seconds 0.0
                                                             agntia_backup_last_attempt_timestamp_seconds 1000.0
                                                             agntia_backup_consecutive_failures 1
                                                             agntia_backup_ledger_corrupt_total 0
predicado de AgntiaBackupStale                             → 0.0 == 0.0  ⇒ stale
alerta AgntiaBackupStale (warning)                         → 202, acknowledged=true, contained=false
backup_lab(quiesced=True, clave efímera de 32 bytes)       → backup_sha256=<64 hex>, files=2
ledger.record('success', digest=backup_sha256)             → línea JSON con digest
exporter.write(ledger, textfile)                           → last_success 1000.0, consecutive_failures 0
predicado de AgntiaBackupStale                             → edad 0 ≤ 93600  ⇒ no stale
```

## Pruebas unitarias del libro y del exportador

```
$ .venv/bin/python -m unittest tests.unit.test_backup_ledger -v
test_absence_and_corruption_are_unknown_not_success ... ok
test_append_only_private_file_keeps_every_attempt ... ok
test_consecutive_failures_since_the_last_success ... ok
test_success_requires_a_digest_and_reasons_are_bounded ... ok
test_atomic_write_leaves_no_temporary_file_behind ... ok
test_missing_textfile_directory_is_an_error_not_a_silent_stale_file ... ok
test_unknown_backup_exports_zero_which_the_rule_reads_as_stale ... ok

Ran 7 tests in 0.9s
OK
```

Casos que fijan el criterio:

```
record('success')                         → ValueError   (un éxito sin digest no es evidencia)
record('failure', digest=…)               → ValueError   (un fallo no tiene bundle)
record('failure', reason='Backup Key …')  → ValueError   (motivo no acotado)
record('success', digest='A'*64)          → ValueError   (digest no hexadecimal en minúsculas)
libro inexistente                         → last_success=None, records=0, corrupt=0
libro con una línea basura                → last_success=None, corrupt=2 (nunca éxito)
directorio del textfile inexistente       → ValueError, sin crear fichero (no deja éxito rancio)
```

## CLI real

```
$ .venv/bin/python scripts/backup_ledger.py record --path "$T/ledger.jsonl" \
      --outcome failure --reason backup_key_unavailable
{"schema_version": 1, "outcome": "failure", "timestamp": 1794929901.26, "reason": "backup_key_unavailable"}

$ .venv/bin/python scripts/backup_ledger.py status --path "$T/ledger.jsonl"
{"schema_version": 1, "records": 1, "valid_records": 1, "corrupt": 0, "last_success": null,
 "last_attempt": 1794929901.26, "consecutive_failures": 1, "age_seconds": null}

$ .venv/bin/python scripts/backup_exporter.py --ledger "$T/ledger.jsonl" \
      --destination "$T/textfile/agntia-backup.prom"
$ cat "$T/textfile/agntia-backup.prom"
agntia_backup_last_success_timestamp_seconds 0.0
agntia_backup_last_attempt_timestamp_seconds 1794929901.261176
agntia_backup_consecutive_failures 1
agntia_backup_ledger_corrupt_total 0

-rw------- ledger.jsonl          # 0600, append-only
-rw-r--r-- agntia-backup.prom    # 0644, escrito con rename atómico
```

## Reglas y entrega

```
$ .venv/bin/python -m unittest tests.integration.test_alert_delivery
Ran 7 tests in 1.6s
OK
```

`test_every_declared_rule_can_be_delivered_and_correlated_to_its_job` pasó de **6 a 7** reglas
esperadas: si el YAML cambia sin actualizar la prueba, la suite falla.

## Suite y documentación

```
$ .venv/bin/python -m unittest discover -s tests
Ran 223 tests in 35.626s
OK (skipped=8)

$ .venv/bin/python scripts/validate_foundation.py
{"status": "PASS", …, "markdown_files": 305, "repository_metadata_records": 31, "security_scans_executed": 0}
```

## Límites

- El *textfile* no lo lee ningún Prometheus: no hay colector en este entorno. La condición `absent()`
  de la regla está declarada y dispararía en un Prometheus sin el colector.
- El libro lo escribe el envoltorio del operador, no la API; la prueba simula ese paso de forma
  explícita y con el mismo esquema que usa la CLI.
- La ventana de 26 h (`93600`) es una hipótesis de campaña; no hay RPO acordado.
