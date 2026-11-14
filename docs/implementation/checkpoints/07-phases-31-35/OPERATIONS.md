# Operación del corte

## Instalación y upgrade

Requiere Python>=3.11; instalar `python -m pip install -e '.[dev]'`. Usar factoría/CLI existente en red privada. Hacer backup SQLite coherente y copiar evidencias/snapshots/claves por canales separados antes de migrar. Schema7 es aditivo: expedientes, historia inmutable, claves idempotentes, restricciones y scopes de informes. El wheel incluye governance/legal_sources.json y la CI lo comprueba.

Los cambios de auth/guards actualizan el hash de política agéntica. Calcular/revisar POLICY_HASH del artefacto instalado, renovar configuración y grants si procede; no usar un hash anterior para saltarse la denegación. No desplegar con clientes reales en este piloto.

## API nominada

Prefijo `/v1/tenants/{tenant}`:

- GET `/governance/sources`: catálogo/versión/hash y límites.
- POST `/governance/inventories`, `/assessments`, `/controls`: DTOs cerrados con roles/finalidad/owner/fuentes/evidencias. Ningún campo compliant aceptado.
- GET `/governance/records/{id}`: acceso scoped y lectura auditada. Datos sensibles requieren rol o asignación. GET `/governance/assessments/{id}` añade estado efectivo de revisión/fuentes.
- POST `/governance/records/{id}/review`: expected_revision, record_hash, evidence_ids revisados y competence_ref; otro humano.
- POST `/privacy/requests`: action restrict/release_restriction/delete/export_metadata, targets con revisiones, finalidad/base referenciadas. POST `/{id}/apply` requiere humano autorizado y revisión vigente. Restricciones más nuevas invalidan propuestas antiguas.
- POST `/privacy/breaches`, GET `/{id}`: detección, constancia, confirmación, rol/riesgo declarados y preparación condicional; no envía notificación.
- POST `/fraud/observations`, POST `/{id}/verify`: señales offline y atestación humana con canal de Settings.verification_channels y evidencia revisada; no usar el teléfono/link del mensaje.
- POST `/incidents`, POST `/{id}/transition`: claves de origen estables, cronología, evidencia, dueño y estados explícitos.
- POST `/containments`, POST `/{id}/execute-lab`, POST `/{id}/reconcile`: efecto interno limitado y revisado; producción denegada.
- POST `/remediations`, POST `/{id}/materialize-lab`: propuesta y candidato, sin fuente sobrescrita. Retest no se expone como runner genérico por HTTP; lo invoca un worker interno con runner verificado.

## Privacidad y restauración

Una purga bloqueada por retención/hold requiere nueva decisión al cambiar hechos, no forzar SQL. Una purga completada del archivo espera reconciliar backups y demás sistemas; nunca mostrarla como borrado integral. Si se pierde ACK/FS falla, conservar reconciliation_required y verificar estado/artefactos antes de actuar.

Restaurar solo en entorno aislado; validar claves/integridad/auditoría y reimportar el registro más reciente de restricciones/tombstones desde un canal custodiado antes de abrir lecturas. No hay restore global productivo certificado. No habilitar un informe antiguo sin fuentes verificables; reconstruirlo desde fuentes actuales y preservar historia según política competente.

## Laboratorio y contención

Settings.lab_mode debe ser True para ejecución de contención; el propio request no puede activarlo. El efecto admitido es lab_revoke_work_grant con hash/revisión del grant. Proponente y revisor diferentes. Si queda executing/reconciliation_required, usar reconcile: comprueba estado y evento grant.revoked con correlación exacta/audit íntegra. No repetir revocación ni atribuir una revocación ajena como propia. Recuperación significa nuevo grant y aprobación nueva, nunca reactivar el revocado.

## Remediaciones

Configurar remediation_fixture_refs exclusivamente con IDs de repositorios sintéticos de servidor. Las reglas soportadas son remove_synthetic_canary sobre canary.txt y remove_fixture_eval sobre fixture_eval.py, ambas con contenido exacto. No ejecutar sobre un checkout real de cliente. La aprobación liga finding/snapshot/política/diff/hashes, licencia declarada y ruta permitida. Cambios de origen producen stale_origin.

El candidato se guarda bajo data_dir/remediations, con contenido sellado. No es una rama Git. Retest interno requiere ReleaseGates verificados y la imagen/política del scanner correspondiente. El runner existente limita red, usuario, permisos, tiempo y recursos; no ejecutar hooks/tests del repositorio en el host. Un error/partial deja retest_failed o conciliación, nunca verified_fixed. Merge/deploy permanecen separados e inhabilitados.

## Verificar y revertir

Ejecutar suite Python y validadores. CI realiza los8 tests Docker, incluido un caso con dos reglas, y navegador/observabilidad. No contar skips locales como pruebas correctas. Para revertir: detener nuevas mutaciones, conservar tablas/audit/ciphertexts y comprobar compatibilidad con schema7. No restaurar una DB antigua que borre restricciones o decisiones nuevas. No hacer downgrade destructivo.
