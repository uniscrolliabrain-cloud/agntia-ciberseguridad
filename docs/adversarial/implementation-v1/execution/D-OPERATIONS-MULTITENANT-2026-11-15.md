# D01/D03 + revisión multitenant

**Base:** `45a927d` (rama `work/advlab-B-vault-broker-release`)
**Rama:** `work/advlab-D-operations`
**Fecha:** 2026-11-15

## D01 — Scheduler durable

`planning/leases.py` sobre SQLite (migración `0002.sql`):

- `acquire(tenant, misión, owner, ttl)` con transacción `BEGIN IMMEDIATE`: dos workers no pueden tomar la misma misión.
- Fencing token monótono: al expirar, el siguiente owner recibe `fence+1`; el worker viejo ya no puede renovar, liberar ni operar (`owns`).
- `register_run(tenant, key, run_id)` idempotente por tenant: dos entregas de la misma clave devuelven el primer `run_id`.
- Estado persistente: un `Store` nuevo ve el lease vivo y rechaza al segundo owner.

**Cobertura:** 5 tests (`test_leases.py`). **Estado: PASS** para lease/fencing/idempotencia. Sin cola externa ni DLQ: si el proceso muere antes de registrar el run, el lease expira y se reintenta; el efecto doble lo evita la clave idempotente, no una transacción distribuida.

## D03 — Backup y restore

`store/backup.py`:

- Copia consistente con la API `backup` de SQLite más el vault completo.
- Manifiesto con SHA-256 y tamaño por archivo.
- `restore` verifica **todos** los hashes antes de tocar nada; un backup corrupto lanza `BackupCorrupt` y deja intacto el dato vivo.
- Devuelve `files_verified` y `rto_ms_measured` real, sin estimaciones.

**Cobertura:** 3 tests, incluido restaurar tras borrar base y evidencia, y backup manipulado. **Estado: PASS** a nivel de fichero único. Falta almacenamiento externo versionado y prueba de restore con cifrado del proveedor.

## Revisión multitenant

### Corregido en esta campaña

| Superficie | Antes | Ahora |
|---|---|---|
| `add_scope` | aceptaba un engagement de otro tenant | `TenantBoundaryError` |
| `add_experiment` | aceptaba un scope de otro tenant | `TenantBoundaryError` |
| `add_run` | aceptaba un experimento de otro tenant | `TenantBoundaryError` |
| `record_transition` | escribía en el ledger de cualquier run conocido | exige tenant propietario |
| `ledger` | leía por `run_id` sin tenant | join con `runs` y filtro por tenant |
| `snapshot` | contaba ledger de runs ajenos si se filtraba un id | deriva solo de los runs del tenant |
| Vault | clave única y AAD sin tenant | clave HKDF por tenant, AAD `tenant|id|v1` (B01/B02) |

### Verificado

- `get_run`, `list_run_ids`, `count_runs`, `snapshot`: aislamiento por tenant con tests.
- Evidencia: mismo `evidence_id` en dos tenants coexiste; blob movido entre tenants no descifra.
- Informes: el render incluye el tenant del recibo; no hay rutas que mezclen recibos.
- Backup: restaura y `tenant-b` sigue viendo cero runs.

### Residual, declarado

- Aislamiento **lógico** dentro de una sola base SQLite; no hay RLS ni bases separadas por tenant.
- Quien tenga la clave maestra del host descifra todos los tenants de ese host (sin KMS).
- Un backup contiene todos los tenants; su custodia debe ser equivalente a la del dato vivo.
- Sin prueba de concurrencia real multi-proceso: el fencing está probado por secuencia, no bajo carga.

## Pruebas

| Comando | Exit | Resultado |
|---|---|---|
| suite del laboratorio | 0 | **115 tests OK** |
| `releasecheck.py` | 0 | PASS integridad |
| `releasecheck.py --production` | 1 | FAIL cerrado (sin `pip-audit` ni atestación) |
| `verify_boundary.py` | 0 | PASS |
| `cli run` | 0 | PARTIAL, ciclo completo |
| validador raíz | 0 | PASS |

## Rollback

Revertir el commit elimina leases, backup y comprobaciones de tenant. Las migraciones son `CREATE TABLE IF NOT EXISTS`: no destruyen datos existentes. La base de `var/` es descartable.

## Gate

**NO-GO producción** (sin KMS, sin audit real, sin OCI). **GO** para piloto interno con dos tenants sintéticos, que es exactamente lo que los tests cubren.
