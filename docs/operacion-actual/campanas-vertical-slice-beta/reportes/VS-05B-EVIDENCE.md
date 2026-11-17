# VS-05B — Evidencia

**Base:** `7fdb14e` · `.venv` Python 3.12 · sin Docker · Linux local · 2026-11-17.

## Pruebas nuevas

```
$ .venv/bin/python -m unittest tests.integration.test_worker_multiprocess -v
test_two_worker_processes_execute_each_claimed_job_exactly_once (…MultiProcessTests) ... ok

Ran 1 test in 2.4s
OK
```

## Qué hace el test, paso a paso

```
fixture: 1 tenant, 1 activo autorizado, 3 jobs pendientes (max_attempts=2 → 6 unidades de 100)
proceso A: python -c <hijo> settings.json executions.log workerAlpha 10
proceso B: python -c <hijo> settings.json executions.log workerBeta  10
```

Cada hijo, en su propio intérprete y con su propia conexión SQLite:

1. reconstruye `Settings` desde el JSON volcado por el padre y `create_app(...)`;
2. crea `JobStore(service, gates=ReleaseGates(True,True,True))`;
3. ejecuta `serve(Worker(store, ScannerDoble(), owner), max_iterations=10, interval=0)`;
4. el doble anota `execution_key` (`<job_id>-<fence>`) en el log compartido y duerme 50 ms;
5. imprime `{"results": n, "states": [...]}` en la última línea.

## Invariantes comprobadas

```
sum(report['results'] for reports)            == 3
len(executed)                                 == 3        # ni una ejecución de más
len(set(executed))                            == 3        # ninguna clave de fencing repetida
len({key.split('-')[0] for key in executed}) == 3        # un job por clave, no tres del mismo
estados de jobs                               == ['completed','completed','completed']
attempts por job                              == [1,1,1]
SELECT count(*) FROM job_results              == 3
audit WHERE action='job.claimed'              == 3
ids devueltos por submit                      == ids en la tabla jobs
returncode de ambos procesos                  == 0
```

El doble es deliberadamente tonto: si `claim` revalidara mal y dos procesos completaran el mismo
trabajo, el log tendría la misma clave dos veces y `job_results` cuatro o más filas.

## Ejecución agregada

```
$ .venv/bin/python -m unittest tests.unit.test_backup_ledger \
    tests.integration.test_worker_multiprocess tests.integration.test_p3_drills -v
Ran 11 tests in 3.303s
OK
```

```
$ .venv/bin/python -m unittest discover -s tests
Ran 223 tests in 35.626s
OK (skipped=8)
```

## Límites medidos, no supuestos

- `claim` aplica `global_limit=2, tenant_limit=1, tool_limit=1` por defecto, y el fixture tiene un solo
  tenant: la política hace que **los trabajos corran en serie**. El test no mide paralelismo; mide
  propiedad única bajo contención de la misma fila candidata.
- La contención concreta (leer `pending`, entrar en `BEGIN IMMEDIATE`, revalidar) ocurre, pero el test
  **no exige** que ambos procesos lleguen a reclamar: si el proceso A se lleva los tres, la prueba pasa
  igual, porque la propiedad que se afirma es «nunca dos veces», no «siempre ambos».
- SQLite en WAL sobre un fichero local. Un despliegue multiproceso real necesita otro motor y otro host;
  por eso el gate no se marca PASS de operación.
- No se envía `SIGKILL` a mitad de escritura: eso es la prueba de lease vencida de VS-05 más la parada
  ordenada de VS-05A.
