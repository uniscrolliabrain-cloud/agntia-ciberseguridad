# VS-05A — Evidencia

**Base:** `acccf0d` · `.venv` Python 3.12 · sin Docker · 2026-11-17.

## Bucle de worker y señales

```
$ .venv/bin/python -m unittest tests.integration.test_worker_runner -v
test_real_sigterm_stops_a_worker_process_without_killing_it_abruptly ... ok
test_iteration_failure_propagates_and_stops_claiming ... ok
test_sigterm_and_sigint_set_the_stop_event_and_restore_handlers ... ok
test_stop_after_grace_cancels_the_attempt_instead_of_waiting ... ok
test_stop_before_first_iteration_claims_nothing ... ok
test_stop_during_attempt_finishes_it_within_grace ... ok
test_shutdown_cancellation_is_persisted_as_reconciliation_required ... ok

Ran 7 tests in 0.584s
OK
```

## SIGTERM real, entre procesos

El hijo ejecuta `serve()` con un worker cuyo intento duerme 30 s; el padre espera la línea `attempt`
y envía `SIGTERM`:

```
attempt
cancelled
{"results": [], "cancelled": 1, "signals": [15]}
exit code 0
```

Lectura: el proceso **no muere abruptamente**. La señal despierta al bucle, se agota la gracia
(0,05 s en la prueba) y la tarea en vuelo se cancela; el worker falso registra la cancelación, el
bucle termina con exit 0 y las señales recibidas quedan registradas.

## Parada con job real reclamado

Con el `Worker` real y un `scan` que nunca termina:

```
state=reconciliation_required  error_code=worker_cancelled
SELECT count(*) FROM job_results → 0
```

No se persiste resultado, no se reintenta y el job no vuelve a `pending` por esta vía.

## Handlers restaurados

```
received=[SIGTERM, SIGINT]
signal.getsignal(SIGTERM) is original → True
signal.getsignal(SIGINT)  is original → True
```

## Suite y documentación

```
Ran 215 tests in 33.303s
OK (skipped=8)
```

```
{"status": "PASS", "scope": "documentation, repository metadata and planned budget consistency only",
 "markdown_files": 288, "repository_metadata_records": 31, "security_scans_executed": 0}
```

## Límites de esta evidencia

- El worker de la prueba de proceso es un doble (`run_once` que duerme), no el servicio completo: lo
  que se prueba ahí es la fontanería de señales, no la persistencia.
- La persistencia sí se prueba con el `Worker` real sobre el fixture SQLite, en el mismo proceso.
- No se ejecutó ningún contenedor: el `SIGTERM` de orquestador queda para el despliegue real.
- No hay métrica de paradas: la señal solo se registra en memoria del proceso que la recibe.
