# Operación del gateway de prueba

## Upgrade y configuración

Usar Python>=3.11 y la instalación existente. Hacer backup coherente de SQLite y de evidencias/snapshots/claves por separado antes de migrar. Schema6 añade tablas de control, flows, releases, tools/versiones, sesiones MCP y efectos/notas/idempotencia. Conserva grants, evidencias y audit previos; los tokens sin policy_hash/epoch dejan de ser válidos y se deben reemitir.

Configurar en servidor agent_policy_hash y agent_policy_expires_at(ISO aware). Obtener el hash del artefacto instalado:

```bash
python -c "from agntia_ciberseguridad.agents.policy import POLICY_HASH; print(POLICY_HASH)"
```

Revisar el artefacto antes de aprobar el valor: el comando lo calcula, no acredita revisión humana. Una política ausente/caducada/distinta deniega acciones. Reiniciar instancias con el mismo artefacto y configuración; no hot-patchear código. La clave delegation_key_env ya existente sigue siendo referencia externa; emergency_token_env debe apuntar a otro secreto de alta entropía, mínimo32caracteres, distinto de bearers/evidencia/métricas/fuentes.

Provisionar agentes con kind=agent; no usar human/service para sortear el gateway. Las rutas heredadas de lectura/escritura ya no son accesibles directamente a agentes. Conservar identidades humanas separadas para proponer manifests y aprobarlos. La clasificación kind sigue sin ser MFA/IdP.

## Lectura, datos y policy

Las delegaciones mantienen endpoints del corte anterior. El manifest permite assets.read, jobs.read, findings.read y notes.propose; no shell ni salida de red. POST `/v1/tenants/{tenant}/agent/explain` recibe UseRequest cerrado y verifica todo sin consumir el token ni devolver contenido. POST `/delegations/use` ejecuta la lectura y consume un uso. flow_ids opcional incluye solo fuentes del mismo activo/tenant; destination_ref no habilita egress y queda denegado.

Un humano registra flow con POST `/agent/flows`, evidence_id y resource_id. Fuente debe existir y seguir en retención. JSON de paquetes es un esquema cerrado: `{"packages":[{"name":"demo","version":"1.2.3"}]}`. Todo lo demás queda en cuarentena. El original sigue cifrado en custodia; la proyección es dato no confiable y confidencial.

Para preparar una salida futura: approved_egress_refs contiene solo IDs web de settings.targets, nunca URLs de un modelo. POST `/agent/flows/{id}/releases` con destino aprobado, hash exacto y expires_at<=15min; otro humano aprueba proposal_hash en `/agent/releases/{id}/approve`. `/egress-preflight` valida DNS/IP y devuelve allowed_to_send=false, bytes_sent=0, transport=unsupported. No incorporar requests HTTP ni credenciales de proveedor para saltar esa condición.

## Tools y MCP

POST `/agent/tools` propone ToolDescriptor: protocol_version2025-11-25, nombre fixed agntia.metadata.read, version, description, input_schema igual a UseRequest.model_json_schema(), skill_hash y dependency_hashes. Otro humano aprueba hash/revisión. Manifest.tool_ids vincula el ID admitido al agente. POST `/agent/tools/{id}/observe` con expected_revision y descriptor detecta cambio: descriptor idéntico es no-op; distinto crea versión pendiente y eleva epoch. No ejecutar skills descritas.

POST `/agent/mcp/{manifest_id}/{tool_id}` exige bearer propio, sin Origin. Secuencia:

1. JSON-RPC2.0 initialize con ID entero, protocolVersion2025-11-25, capabilities={} y clientInfo cerrado(name/version).
2. Guardar header Mcp-Session-Id; usarlo junto a Mcp-Protocol-Version en las siguientes peticiones.
3. Enviar notifications/initialized sin ID y params vacíos; respuesta202 vacía.
4. tools/list o tools/call con IDs enteros crecientes. tools/call solo admite name agntia.metadata.read y arguments UseRequest con grant de un uso.

SesiónTTL<=2min, sin passthrough de bearers, OAuth externo, SSE ni código remoto. No reutilizar tokens propios en otro proveedor. Ante drift/epoch nuevo/rotación reaprobar y crear sesión/grants nuevos.

## Propuestas y efectos locales

POST `/agent/effects/proposals`: grant con notes.propose, resource_id, categoría cerrada, texto acotado, flow_ids y expected_policy_hash. Devuelve el diff local, hash y caducidad; ninguna nota final se crea todavía. Otro humano distinto de proponente/emisor del grant aprueba expected_revision/proposal_hash. Commit con token original, proposal_hash e Idempotency-Key estable8–80ASCII. No cambiar clave si se perdió la respuesta: replay idéntico devuelve receipt; otra petición con la misma key409.

Solo se crea una nota local de revisión, con reserva0céntimos. No modifica finding reviewed, no parchea ni despliega. Ante fallo obligatorio de audit se revierte la transacción. No extrapolar esta atomicidad a un proveedor externo. Receipts históricos tras stop no son una nueva ejecución.

## Parada y recuperación

GET/POST `/agent/controls` requiere humano reviewer/owner; POST además X-Operator-Stepup, kind/scope_id, stopped, expected_epoch y reason. Las credenciales no van a prompts, query strings, logs ni Git. La CLI equivalente usa variables de entorno, no valores de secretos como argumentos:

```bash
PYTHONPATH=. python scripts/agent_emergency.py --config /ruta/servidor.json --tenant tenantA --actor-token-env OPERADOR_BEARER --stepup-env OPERADOR_STEPUP --kind agent --scope agentA --state stopped --expected-epoch 0 --reason "Parada aprobada del piloto"
```

Usar primero --dry-run para inspeccionar epoch y alcance; ese modo no cambia estado ni promete que la segunda credencial vaya a autorizar commit. La CLI solo abre una DB existente, no crea un servicio ni migra en emergencia. El actor y segundo secreto se verifican en la operación real. No ejecutar el ejemplo sobre producción sin autorización.

Stop eleva epoch e invalida todos los grants/sesiones previos del tenant; comprobar respuesta y auditoría. Un commit que ya tenía la transacción puede confirmar antes de la respuesta. Recuperación: investigar, corregir causa, verificar audit, emitir resume con epoch actual, reaprobar artefactos cambiados y reemitir grants/sesiones. No borrar notas/historia ni reactivar tokens viejos.

## Verificar

`python -m unittest discover -s tests -v`, validadores de docs/campaña y `PYTHONPATH=. python scripts/evaluate_agent_gateway.py`. El runner usa fixtures de tests del checkout y no está ofrecido como servicio de modelo de pago. La CI conserva pruebas SDK/Docker/browser reales del núcleo anterior. Mantener puertas de release cerradas hasta revisión independiente.
