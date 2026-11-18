# VS-04 — Evidencias, claves, backup y restore

**Base:** `9b889ab`.
**Estado:** P0/P1 completos; P2 **BLOCKED** por elección de storage/KMS del founder.

## P0 — Dos custodias, un mismo patrón

| Aspecto | Middleware (`evidence/vault.py`) | Laboratorio (`adversarial_lab/.../evidence/vault.py`) |
|---|---|---|
| Cifrado | AES-GCM, clave de 32 bytes desde `EnvRef` | AES-GCM por tenant, clave del `KeyRing` |
| AAD | Incluye tenant, id y variante (original/redactado) | Incluye tenant e id |
| Clave maestra | En variable de entorno; sin versión por blob | Fichero local con `rotate` y `fingerprint` |
| Metadatos | `public()` acota campos; retención, hold, custodio y base legal | `EvidenceRef` con hash y tamaño |
| Integridad | SHA-256 de original y vista redactada | `verify()` recalcula y compara |
| Backup | No implementado en middleware | `store/backup.py` con manifiesto de hashes y `restore` |
| Restore a host limpio | No probado | Probado localmente en tests del laboratorio |

Conclusión: el middleware cifra y minimiza correctamente, pero **no tiene backup ni restore**. El
laboratorio sí, aunque solo contra disco local. No se copia el `KeyRing` al middleware: son
fronteras distintas y mezclarlas rompería el aislamiento que ya está probado.

## P1 — Diseño mínimo para cerrar VS-04

1. **Envelope de clave por tenant:** clave de datos por blob, envuelta por una clave maestra.
   Guardar `key_ref` y `key_version` en los metadatos para poder descifrar tras rotar.
2. **Almacén externo versionado:** interfaz `put/get/delete/list` con prefijo por tenant, escritura
   atómica (temp + rename o multipart), hash obligatorio y sin listados cruzados.
3. **Backup:** manifiesto con hash por objeto, copia de la base y de las claves envueltas, sin
   incluir la clave maestra. Restore a host limpio con verificación objeto por objeto.
4. **RPO/RTO medibles:** el restore debe registrar tiempo y bytes; sin métricas no hay gate.
5. **Borrado y legal hold:** retención vencida no borra si hay hold; el hold se audita.

## P3 — Pruebas que faltan

- Blob manipulado (bit flip) → integridad falla, no se sirve.
- Path traversal y symlink en el almacén → rechazo.
- Ciphertext de tenant B presentado como tenant A → fallo de AAD, no fuga.
- Clave rotada: blobs antiguos siguen legibles con su versión.
- Backup corrupto → restore aborta sin sobrescribir el original.

## Gate

`BLOCKED`: sin proveedor de storage/KMS no se puede demostrar restore externo ni RPO/RTO. El
middleware no debe declararse recuperable todavía. La custodia local del laboratorio ya está probada
y no se presenta como custodia de producción.

## Dependencias del founder

- Elegir storage externo (S3 compatible, R2, etc.) y KMS o clave maestra gestionada.
- Definir RPO/RTO aceptables y retención por tipo de evidencia.
- Aprobar el coste antes de provisionar.
