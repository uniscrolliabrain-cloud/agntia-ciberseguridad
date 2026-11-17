# VS-08 — Adaptador hacia /agente

**Base:** `6390b7e`. **Estado:** inventario y patchset propuesto; E2E `BLOCKED` por permiso.
**No se tocó `/agente`.** Solo lectura de nuestro SDK y rutas.

## Inventario del SDK actual

`typescript/src/client.ts` expone: `assets`, `job`, `budget`, `outbox`, `findings`, `policy`,
`report`, `auditPreview`, `governedRead`. Es server-only (rechaza `window`), exige origen aprobado,
timeout acotado, cuerpo máximo de 1 MiB, `X-Correlation-ID` propio y errores tipados.

## Mapeo de las cinco capacidades

| Capacidad pedida | Endpoint real | SDK hoy | Hueco |
|---|---|---|---|
| `cyber.audit.request` | `POST /v1/tenants/{tenant}/audits` (202) | **no existe** | falta método; requiere `Idempotency-Key` en cabecera |
| `cyber.audit.status` | `GET /jobs/{job_id}` | `job()` | cubierto |
| `cyber.audit.findings` | `GET /findings`, `GET /findings/{id}/history` | `findings()` parcial | falta historial y campos de riesgo |
| `cyber.audit.report` | `GET /reports/{id}` | `report()` | cubierto |
| `cyber.audit.retest` | **no existe** | no existe | gap de contrato y de ruta (VS-01) |
| Evidencia | `POST/GET evidence` | **no existe** | falta método y límites de tamaño |
| Cancelación | `POST /jobs/{id}/cancel` | **no existe** | falta método |

## Patchset propuesto (no aplicado en /agente)

1. `submitAudit(input, idempotencyKey)`: valida `asset_id`, `grant_id`, `snapshot_id`, `tool`,
   `max_attempts`; envía la clave idempotente en cabecera y **no** en el body.
2. `cancelJob(id, expectedRevision)`: devuelve el job actualizado; 409 si cambió.
3. `findingHistory(id, after, limit)`: hash de 64, cursor hex.
4. `uploadEvidence(jobId, bytes, mediaType)`: límite 2 MiB, base64 explícito, sin logs del contenido.
5. `retest`: no implementar hasta que exista `RetestRequestV1`; documentar como `unsupported`.
6. Eventos: mapear `job.*`, `review.*`, `evidence.*` a un sobre con `tenant_id`, `correlation_id` y
   `causation_id`; hoy `causation_id` se rellena con la correlación (ver VS-01A).


## Delta aplicado

Se implementaron en el SDK los dos métodos que no dependían de `/agente`:

- `submitAudit(input, idempotencyKey)`: valida activo, grant, snapshot, hash, herramienta, intentos y
  coste cero; exige clave de 8–100 y la envía en la cabecera `Idempotency-Key`, nunca en el body.
- `cancelJob(id, expectedRevision)`: exige revisión no negativa y devuelve el job actualizado.

`#request` acepta cabeceras extra para no exponer un cliente genérico. La prueba nueva cubre
cabecera idempotente, rechazo de coste distinto de cero, clave corta, asset no hexadecimal y
revisión negativa.

**Evidencia:** SDK 8 tests, 7 pass, 1 skip (contrato vivo); suite Python 197 OK (8 skipped).

## Gate

`BLOCKED` para E2E: falta permiso explícito sobre `/agente` y no existe ruta de retest. El patchset
queda documentado para aplicarse en una campaña separada, sin privilegios nuevos para el LLM.
