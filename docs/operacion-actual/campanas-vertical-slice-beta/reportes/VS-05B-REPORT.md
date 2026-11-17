# VS-05B — Dos procesos worker sobre una base: un solo dueño por trabajo

**Base:** `7fdb14e`. **Rama:** `docs/cyber-bitacora-viva`. **PR:** #17.
**Estado:** `PARTIAL` alto. El multiproceso real queda probado; la DLQ sigue abierta y se declara.

## El hueco que cierra

VS-05A probó la parada ordenada con `SIGTERM`, pero un solo proceso en un solo hilo. La pregunta que
faltaba es la del fencing: **si dos workers reales leen la misma fila pendiente, ¿puede ejecutarse dos
veces?** Con `claim` leyendo candidatos fuera de la transacción y confirmando dentro, la ventana de
carrera existe por diseño; lo que había que demostrar es que la revalidación la cierra.

## Cómo se prueba

`tests/integration/test_worker_multiprocess.py` levanta **dos procesos del sistema operativo**, cada uno
con su conexión SQLite, su propia app y su propio bucle `serve()` de VS-05A, compitiendo por los mismos
tres trabajos pendientes. El escáner de cada hijo es un doble que **anota la clave de ejecución**
(`job_id-fence`) en un fichero compartido antes de dormir 50 ms y devolver un resultado válido.

Ese registro es la prueba: si el fencing fallara, la misma clave aparecería dos veces, `attempts`
sería mayor que 1 o `job_results` tendría más de tres filas.

## Resultado medido

- Tres trabajos, dos procesos, diez iteraciones cada uno.
- Claves ejecutadas: **3, todas distintas**, una por trabajo.
- Estado final: `completed` en los tres, `attempts = 1` en los tres, `job_results = 3`.
- Auditoría: **3 eventos `job.claimed`**, uno por trabajo; ningún trabajo reclamado dos veces.
- Los dos procesos terminaron con **exit 0**.

## Lo que este test no demuestra

- **No demuestra paralelismo.** La política de `claim` limita a un trabajo en ejecución por tenant y
  herramienta (`tenant_limit=1`, `tool_limit=1`), así que los trabajos se ejecutan en serie. Lo probado
  es la propiedad del fencing, no el rendimiento.
- **No cubre `SIGKILL` ni caída del host** con escritura a medias: la prueba de lease vencida de VS-05
  sigue siendo el mecanismo para ese caso, y el `SIGTERM` real está en VS-05A.
- **No hay cola ni host de worker:** los dos procesos se lanzan a mano contra el mismo fichero SQLite
  local. Un despliegue multiproceso real necesita host, supervisión y una base con escritura
  concurrente de verdad, no SQLite en WAL.
- **No hay DLQ.** Deliberadamente: la tabla `jobs` ya conserva los fallos terminales con `error_code` y
  `attempts`, y añadir una segunda cola sin consumidor sería decoración. Queda declarado como pendiente
  con consumidor real y política de descarte.

## Delta de producto

Ninguno. Es una campaña de verificación: el código de `claim`, `complete` y `AuditEvent` ya existía.
Si el test hubiera encontrado doble ejecución, el arreglo habría sido de producto; no fue el caso.

## Gate

`PARTIAL`: el fencing se sostiene entre procesos reales en el laboratorio. El gate de operación 24×7
sigue cerrado por host, cola, DLQ y supervisión.

**Seguimiento:** [VS-05A-REPORT.md](VS-05A-REPORT.md) para la parada ordenada y
[VS-05-REPORT.md](VS-05-REPORT.md) para cancelación en vuelo.
