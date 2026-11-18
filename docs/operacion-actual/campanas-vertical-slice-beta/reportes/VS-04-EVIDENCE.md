# VS-04 — Evidencia

**Base:** `9b889ab`.

| Comprobación | Comando | Resultado |
|---|---|---|
| API del vault middleware | `grep -n "^class \|^    def " agntia_ciberseguridad/evidence/vault.py` | `put`, `read`, `metadata`, `manage`; AES-GCM con clave por `EnvRef` |
| AAD y política | `vault.py:22–55` | Clave solo si la referencia pertenece a la política del tenant; sin fallback en claro |
| Vault del laboratorio | `grep -n ... adversarial_lab/src/agntia_adversarial/evidence/vault.py` | `put`, `get`, `verify`, ruta por tenant |
| Rotación de claves | `adversarial_lab/src/agntia_adversarial/keys.py` | `rotate`, `fingerprint`, `describe` |
| Backup/restore | `adversarial_lab/src/agntia_adversarial/store/backup.py` | manifiesto con hashes, `backup` y `restore` |
| Tests de backup | `adversarial_lab/tests/integration/test_backup_restore.py` | restore local verificado (117 tests del laboratorio en la última ejecución) |

## No ejecutado

- No hay proveedor externo ni credenciales: no se probó restore fuera del host.
- Sin `.venv` en el workspace restaurado, no se reejecutaron suites en este turno.
- No se leyó ningún valor de clave ni fichero `.env`.
