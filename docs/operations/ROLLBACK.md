> **ACTUALIZACIÓN 2026-11-14 — LECTURA OBLIGATORIA**
> Este documento es histórico. Las ramas de implementación y recuperación ya se integraron en `main` (PR #10 y #11); las afirmaciones de ramas apiladas, código no integrado o baseline anterior deben contrastarse con HEAD. Estado: demo sintética **no producción**; reruns CI de Python/SDK, Docker scanner y navegador exitosos en el head de implementación, no equivalen a aceptación de clientes. Estado de gates en `docs/release/status.json`: 2 PASS / 40 PARTIAL. Fuente de verdad complementaria: `docs/auditoria-runtime/AUDITORIA-FUNCIONAL-2026-11-14.md` y `docs/auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md`. Freebuff debe auditar el delta real y no repetir capacidades existentes. **Se preserva el contenido original completo a continuación.**

---

# Reversión sin pérdida de evidencia

No hay un comando automático de downgrade de SQLite ni reset destructivo. Detener nueva admisión y workers, conservar volúmenes, ciphertext, snapshots originales, auditoría, jobs, reservas, outbox/receipts y claves externas. En Compose `docker compose -f infra/compose.yaml stop` detiene ese proyecto; comprobar antes nombre/directorio para no operar sobre otro laboratorio. No ejecutar down -v, prune, git reset --hard ni eliminar directorios de usuario.

La rama actual usa schema8. Antes de arrancar otra versión verificar que conoce ese esquema; conservar migraciones aditivas no hace compatible una versión que las rechaza. Las PR anteriores tienen diferentes esquemas y gates: no sustituir la imagen a ciegas. Si hace falta restaurar, hacerlo en ubicación nueva y aislada, verificar hashes/cadena y conciliar privacidad y revocaciones posteriores. La herramienta de laboratorio deja la API bloqueada. Restore productivo integral sigue pendiente.

Una operación remota incierta conserva sus evidencias y fondos; no liberar reservas ni repetir efecto a ciegas. El rollback de una revocación requiere nueva autorización, no resucitar la antigua. No borrar history para hacer pasar tests o volver al saldo anterior. Los fixes del laboratorio no modifican origen y no crean PR de cliente; no hay despliegue del cliente que revertir por este cierre.

La aceptación de reversión productiva requiere simulación con operadores humanos, almacén real de claves, backups integrales y RTO/RPO. La prueba actual demuestra destino nuevo, integridad y bloqueo, no esa aceptación. Otros checkouts y `/agente` quedan fuera del alcance.
