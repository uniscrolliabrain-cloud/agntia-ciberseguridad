# VS-07D — Señal de backup: el fallo deja de ser silencioso

**Base:** `7fdb14e`. **Rama:** `docs/cyber-bitacora-viva`. **PR:** #17.
**Estado:** `PARTIAL` alto. El simulacro D2 de VS-07B pasa de `BLOCKED` a **PASS** porque ahora existe
una señal real; siguen sin existir Prometheus, proveedor de alertas ni guardia.

## El hueco que cierra

VS-07B declaró, en vez de maquillar, que un backup fallido **no avisaba a nadie**: el fallo era cerrado
y correcto (`lab_only`, `backup_key_unavailable`), pero no tocaba ninguna métrica ni ninguna regla. La
campaña pedía un exportador con su propia alerta. Aquí está, con una condición: la señal solo puede
describir lo que de verdad pasó.

## Diseño

La API **no hace backups**, así que no debe inventar una serie de backup. Un backup del laboratorio
quieto se ejecuta como proceso aparte, y su resultado tiene que sobrevivir a ese proceso. De ahí tres
piezas pequeñas:

| Pieza | Archivo | Qué garantiza |
|---|---|---|
| Libro de intentos | `scripts/backup_ledger.py` | JSONL append-only, modo `0600`, solo resultado, código de motivo acotado y digest del bundle cifrado. Un `success` **sin digest se rechaza**: no es evidencia. Un `failure` **con digest también**: no hay bundle que digerir |
| Exportador | `scripts/backup_exporter.py` | Convierte el libro en cuatro series Prometheus y escribe el *textfile* de forma atómica (`mkstemp` + `fsync` + `os.replace`), para que un corte no deje un fichero a medias que parezca un éxito reciente |
| Regla | `infra/observability/alerts.yaml` | `AgntiaBackupStale`: sin éxito verificado, con más de 26 h, o con la serie ausente |

Series expuestas, todas sin tenant, ruta ni clave:

- `agntia_backup_last_success_timestamp_seconds` — `0` cuando no hay éxito conocido.
- `agntia_backup_last_attempt_timestamp_seconds`
- `agntia_backup_consecutive_failures`
- `agntia_backup_ledger_corrupt_total`

## El criterio que importa: silencio no es salud

Un libro ausente, ilegible o con líneas corruptas se resume como **desconocido**, nunca como un éxito
reciente. El exportador escribe `0`, y `0` es exactamente lo que la regla lee como obsoleto. La prueba
lo fija: un libro vacío y un libro con basura producen `last_success = 0` y `corrupt > 0`.

## Simulacro D2, repetido

| Paso | Señal |
|---|---|
| `backup_lab(quiesced=False)` → `lab_only`; `quiesced=True` sin clave → `backup_key_unavailable`; sin destino creado | el libro anota `failure` con el motivo acotado |
| Exportador sobre el libro | `last_success 0.0`, `consecutive_failures 1`, `corrupt 0` |
| Predicado de la regla | `value == 0` ⇒ **stale**; la alerta se entrega firmada y se acusa (`contained: false`) |
| Backup real cifrado con clave efímera → `backup_sha256` | `record(success, digest=…)` |
| Exportador de nuevo | `last_success = ahora`, `consecutive_failures 0`, edad ≤ 26 h ⇒ **no stale** |

El segundo tramo no es decorativo: demuestra que la señal **se apaga** cuando el backup se recupera, y
que solo un bundle con digest verificado puede apagarla.

## Verificación

- `tests/unit/test_backup_ledger.py`: **7 tests** (validaciones, append-only, ausencia/corrupción,
  fallos consecutivos, exportación atómica, directorio inexistente).
- `tests/integration/test_p3_drills.py`: **3 tests**, con el D2 reescrito.
- `tests/integration/test_alert_delivery.py`: **7 reglas** entregables (antes 6); el test falla si el
  YAML y el número esperado divergen.
- Suite completa: **223 tests OK (8 skipped)**; validador documental PASS con 305 Markdown (293 antes de añadir estos informes).
- CLI real: `backup_ledger.py record|status` y `backup_exporter.py --ledger … --destination …`
  producen libro `0600` y *textfile* `0644`.

## Lo que esto NO es

- **No hay Prometheus ni Alertmanager.** El *textfile* necesita un colector real (`node_exporter` con
  `--collector.textfile.directory` o equivalente). Sin colector, la serie está ausente y la regla
  dispara por `absent()`: es correcto, pero nadie la recibe fuera del receptor sintético.
- **La ventana de 26 h es una hipótesis, no un RPO acordado.** El RPO/RTO real sigue `BLOCKED` con el
  proveedor de storage/KMS (VS-04).
- **El libro comparte el destino del host.** Si el host se pierde, se pierden la base y el libro que
  dice cuándo se copió: es un problema de arranque que no se resuelve dentro de este repositorio.
  Queda declarado para que nadie lea `AgntiaBackupStale` como «hay copia en otro sitio».
- **El registro lo escribe el envoltorio del operador**, no la API. Un backup que nunca se lanza no
  produce ninguna línea; la serie queda en `0` y la alerta dispara, que es lo que se busca, pero no
  distingue «nadie lo intentó» de «falló»: para eso está `last_attempt` junto a
  `consecutive_failures`.
- **No se prueba restauración** aquí: `restore_lab` ya tenía su semántica de bloqueo (`RESTORE_BLOCKED`)
  y su prueba pertenece a VS-04.

## Gate

`PARTIAL` alto: la avería ya tiene ruta de señal y el simulacro pasa de verdad. El gate de operación
sigue cerrado por colector real, proveedor, guardia y RPO acordado.

**Seguimiento:** [RUNBOOK-ALERTAS.md](../RUNBOOK-ALERTAS.md) incluye la regla nueva;
[VS-07B-REPORT.md](VS-07B-REPORT.md) conserva el estado `BLOCKED` original como histórico.
