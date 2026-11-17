# VS-05 — Jobs, leases, cancelación e idempotencia

**Base:** `24bd252`. **Estado:** PARTIAL por multiproceso y SIGTERM reales.
**Verificación:** 197 tests OK (8 skipped), incluida la prueba nueva.

## Lo que ya estaba

- Idempotencia tenant-scoped: clave 8–100, `request_hash`, `binding_id`, `replayed: true`, sin duplicar job ni reserva.
- Fencing por claim; `heartbeat`/`fail`/`complete` rechazan lease vieja con `stale_lease`.
- Lease vencida → `reconciliation_required` con `lease_expired`; nunca reejecuta a ciegas.
- Cancelación en `pending` inmediata; en `running` marca `cancel_requested` y el worker cancela.
- Backoff exponencial con jitter, cupos global/tenant/herramienta y reconciliación con limpieza verificada.

## Delta

Prueba nueva `tests/integration/test_jobs.py::test_cancel_during_execution_stops_scan_and_requires_reconciliation`:
el escaneo arranca, se solicita cancelación, el worker cancela la tarea, el job queda
`reconciliation_required` y no se persiste resultado.

Integración: esta rama no tenía el fix de `CyberError` de VS-00 y el contract test fallaba; se trajo
`typescript/src/client.ts` para que la rama pase la suite por sí sola.

## Huecos

Multiproceso real, SIGTERM de contenedor, cancelación tras efecto externo y ausencia de DLQ.

## Gate

PARTIAL: doble ejecución y estados recuperables cubiertos; cancelación en proceso probada.

**Seguimiento:** SIGTERM, SIGINT y cancelación acotada cerrados en [VS-05A-REPORT.md](VS-05A-REPORT.md); multiproceso con proveedor y DLQ siguen abiertos.
