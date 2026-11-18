# VS-01A — Corrección de impacto: finding y causalidad

**Base SHA:** `2da922ff8ae33bfb0824ae2a6dcec3f3b00e1c93`
**Branch:** `feat/cyber-vs-01a-finding-contract`
**Origen:** revisión de GPT sobre VS-01. Dos hallazgos míos resultaron uno mal orientado y otro
sobrevalorado; este informe los corrige con código y prueba.

## 1. `finding_id`: mi informe estaba invertido

VS-01 decía que `RemediationPlan.finding_id: Hash` era sospechoso frente a `Finding.id: ResourceId`.
La realidad es lo contrario:

| Evidencia | Valor real |
|---|---|
| `findings/normalize.py:51` | `finding_id=digest(identity)` → 64 hex |
| `finding_current.id` | el mismo hash de 64 |
| `app.py:242` | la ruta valida `[a-f0-9]{64}` |
| `reviews.py`, `governance/incidents.py`, `remediation.py` | todos consultan por ese hash de 64 |

Por tanto **`RemediationPlan.finding_id: Hash` es correcto** y no hay traducción inestable: el hash
es el identificador canónico. El defecto real estaba en `contracts.py::Finding`, que:

- declaraba `id: ResourceId` (32 hex) cuando el valor es de 64;
- exigía `tenant_id`, `job_id`, `fingerprint`, `title` y `evidence_ids`, campos que la proyección no
  devuelve (el tenant va en la ruta y la evidencia se consulta aparte);
- no modelaba `risk`, `context`, `exception` ni los campos de revisión;
- **no se usaba en ninguna parte** (una sola coincidencia: su definición).

Un contrato que nadie valida y que no describe la respuesta real es peor que no tenerlo: da falsa
cobertura. Lo he alineado con la proyección efectiva (`Finding`, `FindingRisk`, `FindingContext`,
`FindingException`) y he añadido una prueba que valida un finding real recién escaneado, no un dict
inventado.

**Impacto demostrado:** antes, `Finding.model_validate(finding_real)` fallaba por `id` de 64 y por
campos ausentes; ahora pasa y cubre también el estado `suspected` sin revisión.

## 2. `causation_id`: inconsistencia real, impacto bajo

Confirmado el uso:

- `jobs/store.py:74` escribe `causation_id = correlation` al admitir el job.
- `jobs/worker.py:27` lee `causation_id` y cae a `correlation_id` si falta.
- `telemetry/tracing.py` solo lo exporta como atributo.

No hay ningún consumidor que reconstruya el grafo causal con esa columna, y la correlación no se
pierde: sigue en `correlation_id` y en la auditoría. Por eso **no es una vulnerabilidad ni impide
la trazabilidad actual**; es una columna semánticamente incorrecta que impedirá el día que se
quiera encadenar reintentos o efectos derivados.

No la he “arreglado” rellenándola con otra cosa: el valor correcto solo existe si el cliente envía
la causa. La propuesta queda como delta explícito: cabecera opcional `X-Causation-Id` validada como
UUID, con `correlation_id` como fallback y prueba de que ambos valores se conservan distintos.
Hacerlo sin ese contrato habría sido cambiar un nombre por otro.

## 3. Correcciones al programa de GPT

- **Acepto** convertir cada campaña en patchset diferencial: implementación existente, defecto
  demostrado, cambio mínimo, prueba de regresión, criterio de aceptación.
- **Acepto** separar carriles técnicos de decisiones del founder, con un matiz: VS-03 puede preparar
  adaptadores, pero no puede probar revocación real sin un gestor; su gate debe decirlo.
- **Corrijo** “solo faltan dos contratos”: el alcance no es un contrato único, es una composición, y
  el retest existe como flujo sin contrato. La formulación correcta es “dos contratos sin esquema
  versionado, uno de ellos con flujo ya implementado”.
- **Corrijo** “quizá impide reconstruir relaciones”: hoy no las impide porque nadie las reconstruye
  con esa columna; el riesgo es futuro y está acotado.
- **Mantengo** los PR sin fusionar hasta revisión, pero el fix de Node 26 ya está cubierto por el
  contract test que antes fallaba; no es un cambio a ciegas.

## Verificación

| Comprobación | Exit | Resultado |
|---|---|---|
| Tests dirigidos (reviews, identidad, scanners) | 0 | 16 OK, incluida la nueva validación |
| Suite completa | 0 | 196 OK, 8 skipped |
| SDK | 0 | 6 pass, 0 fail |

## Siguiente delta

1. `Finding` en el SDK TS si el cliente llega a consumir findings (hoy no lo hace).
2. `X-Causation-Id` opcional cuando exista cadena de reintentos.
3. `AuditEventV1` y `RetestRequestV1`, en ese orden, con migración revisada.
