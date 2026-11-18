# Compatibilidad del contrato `Finding` — corte del 2026-11-18

**Decisión registrada:** [`Finding.json`](Finding.json) cambia de forma en `main@525769a`
(campaña VS-01A). `schema_version` **se mantiene en 1** a propósito. Este documento declara el
corte para que ningún consumidor lo descubra por sorpresa.

## 1. Por qué hay un corte

El esquema anterior describía un hallazgo que el servidor nunca devolvió: hablaba de
`tool_id`, `tool_version`, `fingerprint` y `title`, y de estados (`unverified`, `resolved`) que
no existen en la proyección real de `findings.list`, `findings.history` ni en los informes. Se
sustituye por la proyección que el código sí produce.

No es una evolución del contrato: es la corrección de un contrato que estaba mal. Por eso no
tiene sentido anunciarlo como versión 2 —no hay una versión 1 real con la que convivir.

## 2. Qué rompe

| Campo | Antes | Ahora |
|---|---|---|
| `id` | 32 hex | hash de 64 hex |
| `tenant_id` | presente y requerido | **eliminado de la proyección** (la ruta ya fija el tenant) |
| `job_id` | requerido | sustituido por `last_job_id` y `last_snapshot_id` |
| `fingerprint` | requerido | eliminado (la identidad es `id`) |
| `tool_id`, `tool_version` | requeridos | sustituidos por `tool` (enum cerrado de cuatro herramientas) |
| `title` | requerido | eliminado (el hallazgo se identifica por `rule_id` y `path`) |
| `evidence_ids` | requerido | movido a `context.evidence_ids` y `exception.evidence_ids` |
| `state` | `unverified·confirmed·false_positive·resolved` | `suspected·confirmed·false_positive·remediated·verified_fixed·accepted_risk·suppressed` |
| nuevos | — | `asset_id`, `path`, `revision`, `confidence`, `first_seen`, `last_seen`, `observation_count`, `reappeared`, `exception_expired`, `risk`, `exposure`, `context`, `exception`, `reviewed_at/by`, `last_decision_id`, `owner_ref`, `due_at` |

Un consumidor que filtre por `state === "unverified"` o que espere `id` de 32 caracteres
**falla en silencio**: no hay error de esquema, simplemente no encuentra nada.

## 3. Qué debe hacer un consumidor

1. Leer `risk.priority` (`P0·P1·P2·P3·needs_context`) en vez de deducir prioridad de `severity`.
2. Aceptar `id` como cadena hexadecimal de 64 caracteres y usarlo como cursor de paginación.
3. No esperar `tenant_id` en el objeto: la tenencia la fija la ruta autenticada.
4. Tratar `state` como el conjunto de siete valores de arriba; `suspected` es el estado inicial.

## 4. Límites de esta nota

- No se añadió migración de datos: `finding_current` guarda el cuerpo ya proyectado, y las filas
  anteriores a este corte no existen en ningún entorno desplegado (demo sintética,
  `production_enabled=false`).
- Si en el futuro se publica un consumidor externo estable, cualquier corte posterior sí debe
  subir `schema_version` y negociarse por cabecera.
