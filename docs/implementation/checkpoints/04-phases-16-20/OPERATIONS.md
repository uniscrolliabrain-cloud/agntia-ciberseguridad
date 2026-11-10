# Operación del piloto

Instalar Python>=3.11 con `python -m pip install -e '.[dev]'`. Ejecutar `python -m unittest discover -s tests -v`, validadores de documentos/campaña, export de schemas y comprobación de distribución como en CI. Docker debe ejecutarse solo en el laboratorio definido y con fixtures sintéticos, no como fallback de scanners en el host.

## Configuración exclusivamente del servidor

Añadir a Settings:

```json
{
  "evidence_policies": {
    "tenantA": {
      "key_refs": ["CYBER_EVIDENCE_KEY_A"],
      "custodian_ref": "operator-A",
      "legal_basis_ref": "approved-policy-A",
      "retention_days": 30
    }
  },
  "metrics_token_env": "CYBER_METRICS_TOKEN",
  "telemetry_export": "disabled"
}
```

El operador genera una clave aleatoria de32 bytes codificada base64 mediante su gestor de secretos. No pegar la clave en JSON, Git o chat. Cada tenant usa referencias distintas; conservar versiones anteriores mientras existan evidencias cifradas con ellas. Los secretos no aparecen en exportaciones. La identidad humana/agente se fija en PrincipalBinding.kind en servidor; no en petición del modelo.

`telemetry_export=local_collector` solo habilita `http://127.0.0.1:4318/v1/traces`; requiere Collector local/conectividad de namespace adecuada. Revisar `infra/observability/collector.yaml` antes de operarlo. No expone automáticamente puertos. CI usa puertos loopback y destruye su contenedor exacto. Prometheus requiere credencial montada en `/run/secrets/agntia_metrics_token`; debe ser distinta de todos los tokens de usuarios/tenants. `/metrics` no habilitado sin configuración; endpoint de operaciones por tenant mantiene autorización habitual.

## API nominada

Prefijo `/v1/tenants/{tenant}`:

- POST `/evidence`: base64, MIME permitido, source_job_id opcional; limita2MiB.
- GET `/evidence/{id}` y `/content`: metadatos o vista redactada autorizada.
- POST `/evidence/{id}/original`: motivo obligatorio y humano autorizado; descarga octet-stream.
- POST `/evidence/{id}/review`, `/hold`, `/purge`: revisión esperada, política y rol humano.
- POST `/reviews/proposals` y `/{id}/approve`: evidencia revisada, revisión/hash y separación de actores.
- POST `/reports`, GET `/reports/{id}?format=json|html|csv`: informe no revisado; PDF devuelve422.
- GET `/operations`: estados/lag/cobertura del propio tenant.

Las descargas incluyen attachment, no-store, nosniff y CSP restrictiva. No incorporar documentos no confiables al contexto del modelo automáticamente.

## Backup, restauración y reversión

Detener mutaciones; obtener backup coherente de SQLite/WAL con método SQLite y copiar el directorio de evidencias/snapshots; conservar manifiesto y hashes. Custodiar claves fuera del backup de datos. Restaurar en un laboratorio aislado y probar lectura autenticada, checksum, auditoría y scope. Las pruebas automatizadas actuales restauran acceso a una evidencia con su clave, no acreditan un restore total de producción.

Desactivar export antes de cambiar Collector. Retirar refs de clave solo después de inventario/rotación comprobada. Ante corrupción, denegar lectura/informe y preservar artefacto para investigación. Ante purge_pending, revisar DB/archivos y audit trail antes de reconciliar; no editar estados a mano en producción. Reversión de código conserva tablas aditivas y datos; restaurar una DB anterior perdería decisiones nuevas y exige plan explícito. No rebajar schema destructivamente.
