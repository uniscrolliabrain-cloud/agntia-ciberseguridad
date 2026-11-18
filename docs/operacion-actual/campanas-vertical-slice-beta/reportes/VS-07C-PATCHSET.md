# VS-07C — Patchset

Solo documentación. Ningún archivo de código, configuración ni regla cambia.

## Nuevo: `docs/operacion-actual/campanas-vertical-slice-beta/RUNBOOK-ALERTAS.md` (~70 líneas)

| Sección | Contenido |
|---|---|
| Reglas comunes | Acuse ≠ contención; ausencia de señal ≠ salud; no pegar secretos; no relajar controles; guardar el JSONL de acuses |
| Tabla por regla | Significado, comprobaciones concretas y **lo que no se puede concluir**, para las seis reglas declaradas |
| Severidad | Cinco `warning`, un `info`; el cupo lo amplía el propietario de la autorización |
| Dónde se lee | `/metrics` con token, `jobs.read`, SQLite de laboratorio |
| Huecos | Propietario, guardia, canal, exportador de backup, ensayo con colector real |

## Nuevo: `VS-07C-REPORT.md`, `VS-07C-EVIDENCE.md`, `VS-07C-ROLLBACK.md`

Cierre de campaña con gate `PARTIAL` documental y las comprobaciones de exactitud sobre rutas y
campos citados.

## Decisión

| Alternativa | Por qué se descartó |
|---|---|
| Inventar propietarios y turnos | Sería documentación falsa: nadie estaría de guardia. |
| Escribir el runbook dentro de `alerts.yaml` como anotaciones | El YAML es para reglas evaluables; el procedimiento necesita contexto largo y revisión humana. |
| Añadir alertas de backup para "completar" | Sin métrica real, serían alarmas que nunca disparan. El hueco queda declarado en VS-07B. |
| Marcar PASS de P4 | Sin ensayo ni persona no hay operación probada; el gate se queda en `PARTIAL`. |
