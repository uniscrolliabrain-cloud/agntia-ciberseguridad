# PR — Integration: adversarial lab + hardening B/D

**Base:** `main` · **Head:** `integration/advlab-hardening-20261115` · **Fecha:** 2026-11-15

## Qué entra

1. **Laboratorio adversarial C01–C18** (`adversarial_lab/`): paquete independiente con engagement y
   scope, contratos, persistencia, gemelos sintéticos, broker, misiones, oráculos, evidencia cifrada,
   informes, CLI y operación diaria. No importa `agntia_ciberseguridad` ni toca `/agente`.
2. **Hardening B** (`45a927d`): paths confinados, clave HKDF por tenant, AAD ligado, escritura atómica,
   gate de release fail-closed y guardas de broker.
3. **Operaciones D** (`e07bee5`): leases durables con fencing, claves idempotentes, backup/restore con
   hash por archivo y fronteras de tenant en scope, experimento, run y ledger.

## Evidencia

| Comprobación | Exit | Resultado |
|---|---|---|
| `unittest discover -s adversarial_lab/tests -t adversarial_lab/tests` | 0 | **115 tests OK** |
| `releasecheck.py` | 0 | PASS integridad, `release_eligible=false` |
| `releasecheck.py --production` | 1 | FAIL cerrado: audit BLOCKED y firma sin atestación externa |
| `verify_boundary.py` | 0 | PASS, 0 violaciones |
| `cli run --tenant tenant-synthetic` | 0 | PARTIAL, ciclo completo |
| `scripts/validate_foundation.py` | 0 | PASS, 218 Markdown |

## Alcance y límites

- No se toca middleware, API, SDK ni producción. `main` no se modifica con este PR.
- Herramientas externas (Semgrep, OSV, Syft, Schemathesis, ZAP, PyRIT, garak) siguen `BLOCKED` sin binario verificado.
- Proveedores reales `BLOCKED` hasta conectar la cuenta Doppler de ciberseguridad.
- Sin runtime OCI en esta máquina: el adaptador está probado, la ejecución real no.
- Multitenant: aislamiento lógico en SQLite, sin RLS ni KMS; declarado en el informe D.

## Cómo revisar

1. `docs/adversarial/implementation-v1/execution/ADVLAB-EXECUTION-2026-11-15.md` (C01–C18).
2. `.../B-VAULT-BROKER-RELEASE-2026-11-15.md` (P0 de vault/broker/release).
3. `.../D-OPERATIONS-MULTITENANT-2026-11-15.md` (D01/D03 y revisión multitenant).
4. Reproducir los comandos de la tabla anterior; no se pide confiar en cifras del informe.

## Riesgos que asume quien fusione

- El laboratorio ejecuta probes sintéticos en proceso; no es un pentest ni certifica seguridad.
- La clave maestra del host descifra todos los tenants de ese host.
- `audit BLOCKED` sigue impidiendo release de producción; el gate ya lo refleja.

## Rollback

Revertir los commits de `adversarial_lab/` y de los dos informes elimina todo el trabajo. No hay
migraciones sobre datos existentes del middleware ni cambios de esquema fuera de `var/`.

## Gate

**NO-GO producción.** **GO** para revisión de código y para piloto interno con dos tenants sintéticos.
