# VS-05A — Patchset

Dos archivos nuevos respecto a `acccf0d`. Ningún módulo existente de producción cambia.

## `agntia_ciberseguridad/jobs/runner.py` (~75 líneas)

```python
TERMINATION_SIGNALS=(signal.SIGTERM,signal.SIGINT)

class ShutdownWatch:
    def __enter__(self): ...        # guarda el handler previo e instala el propio
    def _handle(self,signum,frame): # registra la señal y loop.call_soon_threadsafe(stop.set)
    def __exit__(self,*exc_info):   # restaura los handlers previos

async def serve(worker,*,stop=None,interval=1.0,max_iterations=None,shutdown_grace=5.0,on_result=None):
    # un intento por iteración; parada entre iteraciones no reclama nada
    # parada con intento en vuelo: wait_for(shield(attempt),grace) → si expira, cancel → CancelledError
    # devuelve la lista de estados persistidos; nunca reintenta por su cuenta
```

Decisiones:

| Alternativa | Por qué se descartó |
|---|---|
| `asyncio.run` dentro de un handler de señal | Los handlers no pueden esperar; se usa un `Event` y `call_soon_threadsafe`. |
| `signal.signal` sin restaurar | En pruebas y en procesos embebidos dejaría handlers colgados; `__exit__` restaura. |
| Cancelar de inmediato al recibir `SIGTERM` | Un intento a punto de persistir resultado se perdería; la gracia acotada evita reconciliaciones evitables. |
| Reintentar tras cancelación | Repetiría un efecto externo incierto; la decisión queda en `reconcile`, con limpieza verificada. |
| Scheduler/exponential loop nuevo | No hay cola decidida; se mantiene el bucle mínimo y explícito. |

## `tests/integration/test_worker_runner.py` (~95 líneas)

Siete pruebas: parada antes de reclamar, gracia que deja terminar, cancelación tras la gracia,
propagación de fallo de iteración, `SIGTERM`/`SIGINT` en proceso con restauración de handlers,
`SIGTERM` real entre procesos y persistencia de `reconciliation_required`/`worker_cancelled` con
`job_results` vacío.

La prueba de proceso reutiliza `sys.executable` (el mismo intérprete del entorno de pruebas) y un
hijo de una sola línea de comando: no necesita red, contenedor ni servicios.
