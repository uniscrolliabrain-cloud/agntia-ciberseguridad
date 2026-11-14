# Operación y reversión

Instalar Python>=3.11: `python -m pip install -e '.[dev]'`. Usar la CLI existente `agntia-ciberseguridad serve --config <archivo-servidor>` en red privada. No iniciar sobre datos reales de clientes en este piloto. Schema5 es aditivo; antes de upgrade usar backup SQLite coherente y copia cifrada de evidencias/snapshots/claves por canal separado. No downgrade destructivo.

## Configuración nueva

Settings incorpora log_retention_days(7), log_max_records(500), log_max_bytes(256000), event_max_records(10000), event_max_bytes(10000000), event_pending_limit(1000), event_sources y delegation_key_env. Son límites de payload por tenant, no volumen total.

Una entrada event_sources es un ID aprobado que contiene tenant_id, key_env, target_refs aprobados, max_per_minute y enabled. La referencia de clave debe ser diferente de fuentes, principals, evidencia, métricas y delegaciones. La configuración valida tenant/targets. La clave no va en JSON ni Git; cargar desde gestor de secretos. La clave de delegación también es una referencia a secreto del servidor. Longitud mínima no sustituye generar entropía criptográfica.

## Webhook

POST `/v1/tenants/{tenant}/sources/{source_id}/events` con `X-Source-Signature` = hex minúsculo de HMAC-SHA256 del JSON canónico del modelo PassiveEvent validado(incluidos defaults, timestamps serializados y campos null). Usar el modelo/version compartidos para no depender del orden textual JSON. Evento tiene schema_version1, tenant/source/event IDs, audiencia fija, sent_at/occurred_at aware, tipo cerrado, target_ref, severity(default unknown), rule_ref(default null), count(default1). No añadir payload libre. TTL de firma300s, reloj observado30d atrás/5min adelante. Para repetir recepción incierta, reenviar exactamente el mismo sobre dentro de ventana; no cambiar sent_at manteniendo event_id. Tras ventana, reconciliar por GET events antes de crear otro ID.

La respuesta202 solo es receipt de observación. GET `/events?after=<sequence>&limit=50` revalida principal/tenant. POST `/events/{sequence}/acknowledge` requiere reviewer/owner, libera pendiente sin confirmar incidente. Fuente revocada: enabled=false en configuración y recarga del proceso. Los registros y watermark permanecen. No hay conector hacia un SIEM de terceros activado.

## Logs y consola

GET `/logs?after=<sequence>&limit=50` exige scope. POST `/logs/hold` body enabled aplica a filas presentes; no política continua. POST `/logs/purge-expired` solo humano reviewer/owner y nunca elimina audit. Si el log opcional falla, revisar counter agntia_signals_total kind=logs/outcome=dropped; no silenciar ese síntoma ni alterar policy.

Abrir `/console` en HTTPS privado. El shell no contiene datos. Introducir ID de tenant y bearer de lectura; nunca usar token global de métricas o clave de fuente/delegación. El password se borra del formulario y logout vacía memoria/vistas. GET `/dashboard` y `/investigation/jobs/{id}` son scopes tenant y no exponen backend global de trace. Mantener proxy sin cachear respuestas autenticadas.

## Agentes y grants

Provisionar PrincipalBinding kind=agent en servidor. POST `/agents/manifests` exige humano reviewer/owner y activos existentes; aprobar con otro humano en `/agents/manifests/{id}/approve` con expected_revision. El schema solo acepta metadatos redactados y tres lecturas, sin network ni shell. GET `/agents` muestra cobertura limitada.

POST `/delegations`: manifest_id, capabilities, resource_ids, expires_at<=5min, parent_token opcional. Raíz requiere humano autorizado; hijo requiere titular agente y scope no ampliado. El token devuelto se trata como credencial temporal y no se guarda en logs, navegador, Git o prompts. POST `/delegations/use` requiere bearer del sujeto, token, capability y resource_id; consumo único. El endpoint ejecuta una lectura nominada y no expone credenciales/proveedores. POST `/delegations/{id}/revoke` requiere humano y bloquea descendientes al revalidar. Nunca usar este permiso para herramientas arbitrarias.

## Verificación

Suite `python -m unittest discover -s tests -v`; validators; `node --check agntia_ciberseguridad/web/console.js`; `PYTHONPATH=. python tests/performance/observability_workload.py`. Browser: instalar Playwright según workflow y ejecutar scripts/browser_observability.py sobre fixtures; capturas se crean bajo ruta de evidencia sintética. El socket local de la sesión está bloqueado, CI dispone de Chromium. No reutilizar capturas con credenciales/clientes reales.

Reversión: cerrar nuevas admisiones/event_sources y quitar acceso a consola/delegaciones en proxy, preservar DB/audit/evidencia. Revertir código solo después de comprobar compatibilidad con tablas5 y sin restaurar una DB que borre operaciones nuevas. No modificar datos históricos para simular éxito.
