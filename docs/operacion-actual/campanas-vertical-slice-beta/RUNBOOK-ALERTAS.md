# Runbook de alertas — grupo `agntia-pilot-hypotheses`

**Estado:** procedimiento escrito y ejecutable en local; **propietario, guardia y escalado siguen
`BLOCKED`** hasta que el founder elija proveedor y persona. Este documento no crea un turno de
guardia ni promete cobertura 24×7.

Las siete reglas viven en `infra/observability/alerts.yaml`. Las alertas se entregan firmadas
(`X-Agntia-Signature`) al receptor local `scripts/alert_sink.py`, que acusa con
`acknowledged: true` y **`contained: false`**. Un acuse significa "recibí y registré", nunca
"alguien lo leyó" ni "el incidente está contenido".

## Reglas comunes a toda alerta

1. **No hay PASS por documentación.** Cerrar una alerta exige evidencia adjunta, no una frase.
2. **No pegar secretos ni datos de cliente** en el canal de incidente. El sujeto son métricas y
   `job_id`; el contenido del activo no viaja.
3. **No relajar controles para "que deje de sonar":** ni límites de cupo, ni firma, ni gates de
   release, ni `--production`.
4. **La ausencia de señal no es salud.** Si el colector no puede leer, el estado es `unknown`.
5. Guardar el JSONL de acuses del receptor como evidencia del simulacro o del incidente.

## Qué mirar primero, por regla

| Regla | Significado operativo | Comprobaciones concretas | Lo que NO se puede concluir |
|---|---|---|---|
| `AgntiaApiSignalAbsent` (`up == 0` o `absent`) | La API o el scrape se han perdido | proceso vivo y puerto; `/health/live` y `/health/ready`; último scrape del colector; reinicios del contenedor | Que no haya incidentes: el estado es desconocido |
| `AgntiaTraceDeliveryIncomplete` | Se descartaron o fallaron exportaciones de traza | `agntia_telemetry_dropped_total` y `agntia_telemetry_export_failures_total`; endpoint del exportador; cola acotada; errores del proceso | Que la auditoría se haya perdido: la auditoría va a la base de datos, no a las trazas |
| `AgntiaDeclaredScanCoverageIncomplete` | Un escaneo no cubrió el alcance declarado | estado del job y `error_code`; intentos y backoff; digest de la imagen del runner; cobertura del snapshot | Que el activo esté limpio o comprometido: **no se infiere seguridad** de un scan incompleto |
| `AgntiaScanSignalAbsentOrOld` | Sin señal de escaneo en 24 h o nunca | autorización vigente y ventana; activos del tenant; programación autorizada; reloj del host | Que haya que escanear sin autorización: sin grant no se ejecuta |
| `AgntiaAttemptBudgetExhausted` | Se rechazan admisiones por cupo local | suma de `job_reservations` frente a `max_requests` de la autorización; jobs `cancelled`/`failed` que consumieron cupo; cliente reintentando en bucle | Que haya que ampliar el cupo: lo decide el propietario de la autorización, no el operador de guardia |
| `AgntiaBackupStale` | Sin backup verificado en 26 h, o sin serie de backup | contenido del libro de intentos (`scripts/backup_ledger.py status`); `consecutive_failures`; clave externa disponible; destino y espacio; que el exportador escriba el *textfile* | Que exista una copia en otro sitio: el libro comparte host con la base; y que restaurar sea posible, porque aquí no se restaura |
| `AgntiaApiPilotErrorBudgetFastBurn` | Fracción de 5xx por encima del 5 % en 5 min | desglose `agntia_http_requests_total` por operación y estado; dependencias; reinicios | Que sea un SLA: es una hipótesis de piloto |

Los contadores se leen en `/metrics`, protegido por el token de métricas
(`Settings.metrics_token_env`). Los estados de job se consultan con permiso `jobs.read`; en el
laboratorio, directamente sobre SQLite (`SELECT state,error_code FROM jobs …`).

## Procedimiento por severidad

**`warning`** (seis de siete reglas): confirmar señal, acotar el alcance, escribir qué se sabe y qué
no, y decidir si procede incidente. El rechazo por cupo se resuelve hablando con el propietario de la
autorización; no se amplía por iniciativa propia.

**`info`** (`AgntiaScanSignalAbsentOrOld`): revisar si la ausencia es esperada (sin autorización
vigente, activo retirado) antes de tratarla como avería.

## Qué falta para que este runbook sea operativo

- **Propietario por alerta** y horario de guardia: `BLOCKED` (persona y proveedor).
- **Canal real** con escalado y acuse humano: `BLOCKED` (proveedor y coste).
- **Colector real del *textfile* de backup:** el exportador y su regla existen desde `VS-07D`, pero
  ningún Prometheus lee el fichero; falta un `node_exporter` con `--collector.textfile.directory`.
  Sin él la serie está ausente y `AgntiaBackupStale` dispara por `absent()`, que es lo correcto pero
  no llega a ninguna persona.
- **Ensayos con Prometheus/Alertmanager reales**: requieren Docker, no disponible en este entorno.

## Enlaces

- Reglas: `infra/observability/alerts.yaml`
- Receptor: `scripts/alert_sink.py`
- Simulacros y resultado por avería: [VS-07B-REPORT.md](reportes/VS-07B-REPORT.md)
- Señal de backup y simulacro D2 repetido: [VS-07D-REPORT.md](reportes/VS-07D-REPORT.md)
- Entrega y acuse: [VS-07A-REPORT.md](reportes/VS-07A-REPORT.md)
