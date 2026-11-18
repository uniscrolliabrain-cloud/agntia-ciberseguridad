# Revisión del cierre de ramas de ciberseguridad — 2026-11-18

**Base medida:** `main@525769a` (`2da922f..525769a`, 98 ficheros, +4710/−67).
**Alcance:** revisión de código del rango mergeado el 2026-11-18, con foco en auth, tenancy,
idempotencia, secretos, custodia de evidencia y observabilidad.
**Naturaleza:** demo sintética. `production_enabled=false` en `docs/release/status.json`.
**Estado:** los ocho hallazgos están resueltos o decididos el 2026-11-18; ver §6.

> **Aviso de independencia.** Esta revisión la ejecuta el mismo agente que realizó los cinco
> merges del rango. **No sustituye al gate `independent_review: PENDING`** de
> `docs/release/status.json`: es una auto-revisión con evidencia reproducible, no una revisión
> de terceros. Todo hallazgo de aquí es una hipótesis comprobada contra el árbol, no una
> auditoría de seguridad externa.

## 1. Qué entró y qué no

| Superficie | Cambio en el rango | Revisado |
|---|---|---|
| `jobs/runner.py` (nuevo, 64 líneas) | Bucle de worker con SIGTERM/SIGINT y gracia acotada | Sí |
| `jobs/store.py` | Contador de admisiones rechazadas por cuota | Sí |
| `telemetry/tracing.py` | Nueva regla `trusted_parent` (muestreo obligatorio) | Sí |
| `telemetry/metrics.py` | Serie `agntia_job_admission_rejections_total{reason}` | Sí |
| `contracts.py` + `schemas/Finding.json` | Reescritura de la proyección `Finding` | Sí |
| `scripts/alert_sink.py` (nuevo) | Receptor de alertas con HMAC, dedupe y recibo | Sí |
| `scripts/backup_ledger.py`, `backup_exporter.py` (nuevos) | Libro de copias y exportador textfile atómico | Sí |
| `typescript/src/client.ts` | `submitAudit`, `cancelJob`, `ackOutbox` | Sí |
| **Auth, tenancy, rutas de `/v1`, esquema SQLite** | **Sin cambios en el rango** | No aplica |

## 2. Lo que aguanta (verificado, no asumido)

| Comprobación | Resultado | Cómo |
|---|---|---|
| Suite Python | **224 OK, 8 skipped** | `.venv/bin/python -m unittest discover -s tests` (exit 0) |
| SDK TypeScript | build OK; 8 pass, 1 skip | `cd typescript && npm test` (exit 0) |
| CI remoto de `main` | `success`, 0 fallidos, 0 en curso | workflows `docs.yml`, `release.yml` sobre `525769a` |
| `traceparent` externo | **No se extrae**: el middleware abre span `root=True` | `telemetry/api.py:19-20` + test con `baggage` malicioso |
| Sello de admisión | Hashea `credential_fingerprint`, **no** el token | `auth.py:22-28`, `store.py:15` |
| Contrato vivo del ACK | Cubierto contra FastAPI real: 403 sin permiso, `duplicate` false→true, `tenantB`→`not_found` | `typescript/test/client.test.mjs`, test de contrato en vivo |
| Libro de copias | `O_APPEND` + `fsync`, dir `0o700`, fichero `0o600` | `scripts/backup_ledger.py:44-52` |
| Exportador textfile | `mkstemp` + `fsync` + `os.replace` atómico | `scripts/backup_exporter.py:31-41` |
| Bump OpenTelemetry 1.38→1.45.2 | **Justificado**, no accidental | commit `5c12bbd` («propagar trazas con OpenTelemetry 1.45») |

Corrección respecto a lo que dije al cerrar los merges: atribuí el bump de OpenTelemetry a un
arrastre sin justificar. Es falso: `5c12bbd` lo motiva y lo acompaña del gate de auditoría de
dependencias (`.github/workflows/dependency-audit.yml`).

## 3. Hallazgos

| ID | Severidad | Título | Evidencia |
|---|---|---|---|
| H-01 | **Media** | Una cola truncada del libro de copias parece una copia correcta | experimento §3.1 |
| H-02 | **Media** | El bucle del worker muere ante una excepción transitoria | experimento §3.2 |
| H-03 | **Media** | `Finding` cambia de forma rompiendo consumidores y mantiene `schema_version: 1` | diff de esquema §3.3 |
| H-04 | Baja | Los recibos de alerta se escriben `0o644` y sin `fsync` | experimento §3.4 |
| H-05 | Baja | `submitAudit` y `cancelJob` no tienen contrato vivo en CI | lectura del test de contrato |
| H-06 | Info | `exposure` triplicado y `risk.source` como texto libre | `contracts.py:143-181` |
| H-07 | Info | Un `traceparent` no muestreado corta la continuidad de la traza | `tracing.py:20-25`, test `test_telemetry.py:81-84` |
| H-08 | Info | El dedupe del receptor de alertas vive en memoria y sin cota | `alert_sink.py:66-73` |

### 3.1. H-01 · Copia de seguridad fallida invisible (Media)

`summarize()` cuenta las líneas ilegibles en `corrupt`, pero `last_success` y
`consecutive_failures` se calculan solo sobre las líneas válidas. Si el proceso muere a mitad
del `append`, la última escritura queda truncada y el resumen sigue presentando una copia
reciente:

```
{"age_seconds": 1.0, "consecutive_failures": 0, "corrupt": 1,
 "last_attempt": 1000.0, "last_success": 1000.0, "records": 2, "valid_records": 1}
```

El exportador publica `agntia_backup_ledger_corrupt_total`, pero **ninguna regla de
`infra/observability/alerts.yaml` consume esa serie** (verificado: solo hay reglas sobre
`agntia_backup_last_success_timestamp_seconds`). Resultado: el fallo que el módulo dice hacer
visible («un backup que falla en silencio es exactamente el fallo que este fichero existe para
hacer visible») sigue siendo invisible cuando el fallo es de escritura.

**Arreglo mínimo:** regla `AgntiaBackupLedgerCorrupt` sobre `agntia_backup_ledger_corrupt_total > 0`
y, opcionalmente, marcar `last_success` como desconocido cuando la última línea es ilegible.

### 3.2. H-02 · El bucle del worker no tiene frontera de error (Media)

`serve()` propaga cualquier excepción de `worker.run_once()` y termina:

```
escapa del bucle: RuntimeError database is locked
```

`Worker.run_once` ya captura `Exception`, así que lo que escapa son fallos del propio bucle o
`DomainError('stale_lease')`, que se re-lanza a propósito. El efecto práctico: un `database is
locked` transitorio de SQLite o un fallo de heartbeat mata el proceso; sin supervisor, el worker
queda caído y los jobs esperan a que expire el lease para pasar a `reconciliation_required`.
No hay pérdida de datos —el lease y el fence lo impiden— pero sí una parada no planificada que
el código de arranque no trata.

**Arreglo mínimo:** contar fallos consecutivos y salir solo tras un umbral, o registrar y seguir
para excepciones que no sean `stale_lease`.

### 3.3. H-03 · Cambio rompiente en el contrato `Finding` (Media)

`VS-01A` alineó el modelo con la proyección real. El cambio es correcto en sustancia —el
esquema anterior no describía lo que el servidor devuelve— pero es **incompatible** para
cualquier consumidor y no se versionó:

| Campo | Antes (`2da922f`) | Ahora (`525769a`) |
|---|---|---|
| `required` | `fingerprint, id, job_id, rule_id, severity, tenant_id, title, tool_id, tool_version` | `asset_id, confidence, exception_expired, first_seen, id, last_job_id, last_seen, last_snapshot_id, observation_count, path, reappeared, revision, risk, rule_id, severity, state, tool` |
| `state` | `unverified, confirmed, false_positive, resolved` | `suspected, confirmed, false_positive, remediated, verified_fixed, accepted_risk, suppressed` |
| `id` | `^[a-f0-9]{32}$` | hash de 64 |
| `schema_version` | `1` | **`1`** |

Un consumidor que distinga por `state: "unverified"` o por `id` de 32 caracteres rompe en
silencio; `schema_version` sigue en 1, así que no puede detectarlo. `tenant_id` desaparece de la
proyección, de modo que el SDK ya no puede comprobar la tenencia de cada hallazgo (solo la ruta).

**Arreglo mínimo:** nota de compatibilidad fechada en `docs/implementation/schemas/` declarando
el corte, o subir `schema_version` a 2 si se quiere que un cliente pueda negociar.

### 3.4. H-04 · Recibos de alerta legibles por otros usuarios y sin `fsync` (Baja)

`AlertSink.accept()` abre el fichero de estado con `Path.open('a')`, sin modo explícito:

```
modo: 0o644   (backup_ledger usa 0o600)
```

El contenido son recibos con `tenant`, `job_id` y `traceparent`: metadatos de cliente en un
fichero legible por cualquier usuario local, mientras el módulo hermano se toma la molestia de
usar `0o600` y directorio `0o700`. Además no hay `fsync`: un reinicio del sistema puede perder
recibos que el emisor ya vio confirmados con `202`. El recibo dice «entregado y reconocido», no
«persistido»; conviene que el código y el docstring digan lo mismo.

### 3.5. H-05 · Dos métodos nuevos del SDK sin contrato vivo (Baja)

El test de contrato en vivo (`test_python_ts`) ejercita `assets`, `budget`, `job`, `outbox` y
`ackOutbox` contra FastAPI real. `submitAudit` y `cancelJob` solo se prueban contra un `fetch`
falso. El servidor sí está cubierto por `tests/security/test_jobs_api.py`; lo no verificado es el
cliente real, donde una cabecera `Idempotency-Key` mal puesta o un `expected_revision` de tipo
equivocado no se detectaría.

### 3.6. Observaciones informativas

- **H-06**: `exposure` aparece en `Finding`, `FindingContext` y `FindingRisk` con la misma
  enumeración. Tres copias del mismo vocabulario divergen con el tiempo. `risk.source` es texto
  libre de hasta 200 caracteres en un contrato por lo demás cerrado.
- **H-07**: `trusted_parent` exige ahora el bit de muestreo; un padre guardado sin muestrear
  arranca una traza nueva en vez de continuarla. Es deliberado y está probado
  (`test_telemetry.py:81-84` rechaza `03`, `02`, ids en cero y versión distinta de `00`), pero
  rompe la continuidad de trazas no muestreadas. El ACK del sink aplica la misma regla, así que
  ambos lados coinciden.
- **H-08**: `_receipts` no tiene cota. Con el receptor en `127.0.0.1` y cuerpo máximo de 64 KiB
  el riesgo es local, pero un emisor comprometido puede hacer crecer el proceso sin límite.

## 4. Lo que esta revisión no cubre

- **No es una revisión independiente.** El gate `independent_review: PENDING` sigue abierto.
- **No se ejecutaron los gates de Docker ni de navegador** en local (`browser.yml`,
  `scanner-contracts.yml`); el CI remoto de `525769a` está verde, lo que no equivale a haberlos
  reproducido aquí.
- **No hay escáneres reales, DAST ni pentest.** Los adaptadores siguen siendo offline.
- **No se revisó auth ni tenancy en profundidad**: no cambiaron en este rango. Los invariantes
  citados se comprobaron por lectura y por los tests existentes, no con un análisis nuevo.
- **No se probó con dos cuentas reales ni con clientes reales.**

## 5. Prioridad sugerida

1. **H-01** y **H-04**: dos cambios pequeños que cierran la diferencia entre «señal exportada» y
   «señal que despierta a alguien».
2. **H-03**: nota de compatibilidad del corte de `Finding`; sin ella, el siguiente consumidor
   pierde una tarde.
3. **H-02**: frontera de error en el bucle del worker antes de operar con supervisión.
4. **H-05**: extender el contrato vivo a `submitAudit` y `cancelJob` usando el servidor que el
   test ya levanta.

Ninguno de los hallazgos cambia el estado de release: `production_enabled=false` sigue siendo
correcto.

## 6. Estado de resolución (2026-11-18)

| ID | Estado | Cambio | Evidencia |
|---|---|---|---|
| H-01 | **Resuelto** | `summarize()` marca `tail_corrupt` y retiene `last_success` cuando la última línea es ilegible; nueva regla `AgntiaBackupLedgerCorrupt` | sonda: `last_success=null`, `age_seconds=null`, `tail_corrupt=true`; `test_p3_drills` verifica el predicado |
| H-02 | **Resuelto** | `serve()` tolera fallos consecutivos (`max_consecutive_failures=3`), los reporta por `on_error` y re-lanza `stale_lease` de inmediato | sonda: error reportado y segunda iteración completada; 3 tests en `test_worker_runner` |
| H-03 | **Resuelto (decisión)** | Nota de compatibilidad fechada con la tabla de campos, y por qué `schema_version` sigue en 1 | [`FINDING-COMPATIBILITY.md`](../implementation/schemas/FINDING-COMPATIBILITY.md) |
| H-04 | **Resuelto** | Recibos con `O_APPEND`+`fsync` y modo `0o600` | sonda: modo `0o600`; aserción nueva en `test_alert_delivery` |
| H-05 | **Resuelto** | El contrato vivo ejecuta `submitAudit` (replay idempotente) y `cancelJob` contra FastAPI real | `tests/contracts/test_python_ts.py` + bloque vivo de `client.test.mjs` |
| H-06 | **Resuelto** | Alias único `Exposure` en los tres sitios y `risk.source` con patrón acotado | `contracts.py`; `Finding.json` regenerado |
| H-07 | **Decidido, sin cambio** | Se mantiene exigir muestreo; el motivo queda escrito en `trusted_parent` | comentario en `tracing.py` |
| H-08 | **Resuelto** | Ventana de dedupe acotada a `MAX_RECEIPTS=4096` con expulsión del más antiguo | `scripts/alert_sink.py` |

**H-09 (nuevo, encontrado al arreglar H-05).** Al ejercitar `submitAudit` contra el servidor
real, el SDK devolvía `validation:422` con el cuerpo canónico de `AuditJobCreate`: el validador
`closed()` prohibía `schema_version`, que el modelo del servidor incluye con valor por defecto.
Cualquier consumidor que construyera el cuerpo desde el esquema publicado habría fallado. Se
añadió la clave a la lista cerrada (validando `1` si viene) en `typescript/src/client.ts`.
El test unitario anterior no lo detectó porque construía el cuerpo a mano, sin `schema_version`.

### Verificación tras los cambios

| Comprobación | Resultado |
|---|---|
| Suite Python | **226 tests OK, 8 skipped** (exit 0) — incluye el contrato vivo |
| SDK TypeScript | build OK; 8 pass, 1 skip, 0 fail (exit 0) |
| Esquemas | 13 exportados; `git diff` solo `Finding.json` (patrón y longitud de `risk.source`) |
| `validate_foundation.py` | PASS, 318 Markdown |
| `check_distribution.py` | PASS, recursos y hashes verificados sobre `525769a` |
| `evaluate_agent_gateway.py` / `measure_agent_stop.py` | PASS con `PYTHONPATH=.` (como el CI) |

Estos cambios están en el árbol de trabajo, sin commit: `AGENTS.md` prohíbe fusionar o desplegar
automáticamente.
