# VS-05A — Parada ordenada del worker (SIGTERM/SIGINT) y cancelación acotada

**Base:** `acccf0d`. **Rama:** `docs/cyber-bitacora-viva`. **PR:** #17.
**Estado:** `PARTIAL` alto. SIGTERM real demostrado; multiproceso con proveedor y DLQ siguen abiertos.

## Qué faltaba

VS-05 dejó cuatro huecos declarados: multiproceso real, **SIGTERM del proceso**, **cancelación tras
efecto externo** y ausencia de **DLQ**. El código de `Worker.run_once` ya cerraba bien el caso
`CancelledError` (persistía `worker_cancelled` con `cleanup_verified=False`), pero nada conectaba una
señal del sistema operativo con esa ruta: el proceso solo podía morir abruptamente, dejando el job
`running` hasta que venciera la lease y pasara a `reconciliation_required` por `lease_expired`.

## Qué se construyó

`agntia_ciberseguridad/jobs/runner.py` — primitiva de proceso, sin framework nuevo y sin scheduler:

| Propiedad | Implementación |
|---|---|
| Una ejecución a la vez | `serve()` reclama como máximo un job por iteración (`worker.run_once`) y espera a que termine antes de la siguiente |
| Parada sin reclamar | Si la parada ya está pedida o llega entre iteraciones, no se reclama nada nuevo |
| Gracia acotada | Si la parada llega con un intento en vuelo, espera `shutdown_grace` (5 s por defecto) para que el resultado se persista con normalidad |
| Cancelación explícita | Agotada la gracia, cancela la tarea; `Worker` la convierte en `reconciliation_required` con `error_code=worker_cancelled`, `cleanup_verified=False`, sin resultado persistido |
| Nunca reintenta solo | No hay reejecución tras cancelación: la decisión queda en `reconcile`, que exige limpieza verificada y revisa la lease |
| Señales reales | `ShutdownWatch` instala `SIGTERM` y `SIGINT`, los traduce a un único `asyncio.Event` con `call_soon_threadsafe` y **restaura los handlers previos** al salir |
| Sin estado oculto | El bucle devuelve la lista de estados persistidos; el callback opcional `on_result` es del llamador |

El handler no hace E/S ni escribe en base de datos: solo registra la señal y despierta al bucle. Toda
la persistencia sigue ocurriendo en el hilo del evento, dentro de `Worker`.

## Resultado medido

- `tests/integration/test_worker_runner.py`: **7 tests OK**.
- **SIGTERM real entre procesos**: el hijo imprime `attempt`, el padre envía `SIGTERM`, el hijo
  imprime `cancelled`, termina con **exit 0** y reporta `{"results": [], "cancelled": 1, "signals": [15]}`.
- **SIGINT y SIGTERM en proceso**: ambos ponen el evento de parada y los handlers originales quedan
  restaurados (`assertIs` sobre el handler previo).
- **Parada con job reclamado**: el job queda `reconciliation_required` / `worker_cancelled` y
  `job_results` sigue en **0 filas**.
- Suite completa: **215 tests OK (8 skipped)**.

## Lo que esto NO es

- **No hay binario de worker desplegado.** El bucle es la pieza que faltaba; sigue sin existir una
  cola real ni un entrypoint de operación, así que la prueba de proceso usa un worker falso y la de
  servicio usa el fixture. Montar el proceso real exige decidir cola y host (no lo decide una IA).
- **No hay multiproceso real** con dos workers compitiendo por la misma cola: el fencing está probado
  en store; la competición entre procesos queda pendiente de ese despliegue.
- **No hay DLQ.** Los jobs `failed` y `reconciliation_required` son consultables con su `error_code`
  y su `result_hash` nulo, pero no existe una superficie dedicada de carta muerta ni política de
  retención.
- **`SIGKILL` no se puede gestionar** y no se simula: para eso está la lease y la reconciliación.

## Gate

`PARTIAL` alto: el hueco "SIGTERM de contenedor" de VS-05 queda cerrado con una prueba de proceso
real; multiproceso con proveedor y DLQ siguen abiertos y no se marcan como hechos.

## Delta recomendado a continuación

1. Elegir cola y host del worker; conectar `serve()` y medir dos procesos compitiendo por un job.
2. Superficie de DLQ (listado de `failed`/`reconciliation_required` con código y antigüedad).
3. Envolver `serve()` en un entrypoint con `systemd`/contenedor y probar `SIGTERM` en el contenedor.

**Seguimiento:** el punto 1 (dos procesos compitiendo por un job) está cubierto por [VS-05B-REPORT.md](VS-05B-REPORT.md); la DLQ y el entrypoint siguen abiertos.
