# B01/B02/B04/B05 — Vault, broker y gate de release

**Base SHA:** `ba08d7e` (rama `feat/advlab-campaigns-C01-C18`)
**Rama:** `work/advlab-B-vault-broker-release`
**Fecha:** 2026-11-15
**Origen:** campaña documental `docs/auditoria-y-plan-operativo-cyber-20261115` (hallazgos CY-02, CY-03, CY-04).

## Objetivo

Cerrar los tres P0 que la auditoría documental señaló sobre mi código, sin cuentas ni infraestructura:
path traversal en el vault, clave única compartida entre tenants y gate de release que daba PASS con la
auditoría de dependencias bloqueada.

## Cambios

| Hallazgo | Antes | Ahora |
|---|---|---|
| CY-02 paths | `root / tenant_id / f"{id}.bin"` sin validar | `validate_component` + `confined()` con `resolve()`, `is_relative_to` y rechazo de symlinks |
| CY-03 custodia | una clave AES para todos los tenants, AAD solo con `evidence_id` | clave HKDF-SHA256 por tenant y AAD `tenant|evidence|v1`; blob movido a otro tenant no descifra |
| CY-03 escritura | escritura directa | temporal + `os.replace` atómico y permisos `0600` |
| CY-04 release | `audit: BLOCKED` salía con exit 0 y sin hallazgo | `--production` falla cerrado; `release_eligible=false` y motivos explícitos |
| CY-09 broker | sin revocación, deadline, dedupe ni tope de salida | `authorize`, `deadline`, `idempotency_key` con receipt cacheado y truncado de stdout/stderr |

## Pruebas ejecutadas

| Comando | Exit | Resultado |
|---|---|---|
| `PYTHONPATH=adversarial_lab/src:adversarial_lab/tests .venv/bin/python -m unittest discover -s adversarial_lab/tests -t adversarial_lab/tests` | 0 | **103 tests OK** |
| `releasecheck.py` | 0 | PASS integridad, `release_eligible: false` |
| `releasecheck.py --production` | **1** | FAIL esperado: `dependency audit not verified: BLOCKED` y `signature ... not external attestation` |
| `verify_boundary.py` | 0 | PASS, 0 violaciones |
| `cli run` | 0 | PARTIAL, ciclo completo con el vault nuevo |
| `scripts/validate_foundation.py` | 0 | PASS, 216 Markdown |

Casos negativos añadidos: `../escape` como tenant e id, symlink de tenant, blob copiado entre tenants,
blob renombrado a otro id, herramienta fuera de catálogo, autorización revocada, ventana vencida,
doble invocación idempotente y salida gigante truncada.

## Resultado por campaña

- **B01 vault paths: PASS** con evidencia de tests.
- **B02 custodia: PARTIAL** — aislamiento criptográfico por tenant real, pero sin KMS externo ni envelope con clave de tercero.
- **B04 broker: PARTIAL** — revocación, deadline, idempotencia y topes probados; cancelación en vuelo de un proceso ya lanzado sigue pendiente.
- **B05 release: PARTIAL** — el gate ya falla cerrado; falta `pip-audit` real y atestación externa.
- **B03 OCI: BLOCKED** — no hay runtime en esta máquina.
- **C01–C02 proveedores: BLOCKED** — esperando la cuenta Doppler de ciberseguridad.

## Riesgos residuales

- Sin KMS, la clave maestra vive en disco local; un compromiso del host permite descifrar toda la evidencia de ese host.
- La atestación de release es de integridad, no de identidad externa.
- El broker no puede matar un proceso ya en ejecución dentro del sandbox local; el deadline se comprueba antes de cada llamada.

## Rollback

Revertir el commit de esta rama devuelve el vault anterior; la evidencia nueva en `adversarial_lab/var/`
es descartable (gitignored) y no hay migraciones sobre datos de cliente.

## Gate

**NO-GO para producción.** GO para seguir con OCI real (B03) y con el proveedor real cuando exista la
cuenta y la clave.

## Decisión pendiente del founder

Ninguna para este bloque. Para B02/B05 harán falta proveedor de claves y `pip-audit` en CI.
