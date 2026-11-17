# VS-07B — Simulacros P3: caída de escáner, backup fallido y presupuesto agotado

**Base:** `acccf0d`. **Rama:** `docs/cyber-bitacora-viva`. **PR:** #17.
**Estado:** `PARTIAL`: dos simulacros pagan a humano; el de backup queda `BLOCKED` por falta de ruta
de señal, y se declara así en lugar de fingir un PASS.

## Por qué simulacros

VS-07A demostró que una alerta se firma, se entrega, se deduplica y se acusa. Eso no responde la
pregunta operativa: **¿ante esta avería concreta, alguien se entera?** Un simulacro recorre la avería
real en el código, deriva la condición de la regla desde los contadores que la API expone, entrega la
alerta al receptor firmado y anota lo que **no** queda cubierto.

## Los tres simulacros

| Simulacro | Reproducción real | Señal observada | Regla | Resultado |
|---|---|---|---|---|
| Escáner caído | `scan` devuelve `status=error`, `error_code=runner_unavailable`; el worker reintenta y agota el intento | `agntia_scan_coverage_total{coverage="incomplete"}=2` (un fallo por intento), `agntia_job_transitions_total{tool="gitleaks",state="failed"}=1`, `job_results` vacío | `AgntiaDeclaredScanCoverageIncomplete` | **PASS**: entrega 202, acuse `acknowledged: true`, `contained: false`, duplicado deduplicado |
| Backup fallido | `backup_lab` sin laboratorio detenido → `lab_only`; con `quiesced=True` y sin clave → `backup_key_unavailable`; no se crea destino | **ninguna**: no hay métrica `agntia_*backup*` ni regla que la evalúe | — | **BLOCKED**: el fallo es cerrado y correcto, pero **no avisa a nadie** |
| Presupuesto agotado | 20 admisiones de 5 intentos contra una autorización de 100; la 21.ª es rechazada con `quota`/429 sin crear job | `agntia_job_admission_rejections_total{reason="quota"} 1` | `AgntiaAttemptBudgetExhausted` (nueva) | **PASS** tras instrumentar el rechazo: entrega 202 y acuse |

## Delta de producto

El tercer simulacro encontró un punto ciego real: un rechazo por presupuesto ocurría **antes** de
crear el job, así que no tocaba ninguna métrica existente y no podía disparar nada. Se añadió:

- `Metrics.admission(reason)` con etiquetas acotadas (`quota`, `scope`, `identity`, `validation`,
  `other`) y la serie `agntia_job_admission_rejections_total` en la exposición Prometheus.
- Instrumentación en el rechazo por cuota de `JobStore._submit`, antes de lanzar el 429. El contador
  no lleva tenant, actor, activo ni clave: solo el motivo acotado.
- Regla `AgntiaAttemptBudgetExhausted` en `infra/observability/alerts.yaml`:
  `increase(agntia_job_admission_rejections_total{reason="quota"}[15m]) > 0`, severidad `warning`.

No se añadió ninguna regla para backup: no existiría una señal real que la sustentara y una regla
sobre una métrica inventada es peor que un hueco declarado.

## Cómo se evalúa la regla en el simulacro

El receptor local no es Prometheus. El simulacro **traduce** el predicado de la regla a su forma
equivalente sobre los contadores en memoria (`increase(counter[15m]) > 0` ↔ el contador creció desde
el inicio del simulacro) y verifica que la regla declarada menciona esa métrica y esa etiqueta. Es una
comprobación de correspondencia, no una evaluación de PromQL: así se declara en la evidencia.

## Resultado medido

- `tests/integration/test_p3_drills.py`: **3 tests OK** (2 PASS, 1 BLOCKED declarado).
- `tests/integration/test_alert_delivery.py`: **6 tests OK** con la sexta regla (el test falla si el
  YAML y el receptor divergen en número).
- Suite completa: **215 tests OK (8 skipped)**; validador documental PASS.

## Lo que esto NO es

- **No hay guardia ni turno.** El acuse sigue siendo del receptor, no de una persona. `contained:
  false` es literal: nada se contiene.
- **No hay Prometheus ni Alertmanager en ejecución.** Las reglas son hipótesis declaradas; el
  colector real sigue necesitando Docker (`verify_observability.py`).
- **El simulacro de backup no prueba una copia real:** prueba que el fallo es cerrado y que **no hay
  monitor**. Cerrarlo requiere un exportador o un chequeo programado con su propia alerta.
- **No se simula corrupción de backup restaurado**: eso pertenece a VS-04 y sigue `BLOCKED` por
  proveedor de storage/KMS.

## Gate

`PARTIAL`: entrega correlacionada y página para dos de tres averías; `BLOCKED` explícito para backup.
El gate de operación 24×7 sigue cerrado por proveedor, guardia y runbook.

## Delta recomendado a continuación

1. Exportador de backup (o *pushgateway* con `backup_last_success_timestamp_seconds`) y regla
   `AgntiaBackupVerifyFailed`; repetir el simulacro.
2. Repetir los tres simulacros tras un `docker compose` real con Prometheus + Alertmanager.
3. Añadir propietario y runbook por alerta; hoy solo hay `summary`.
