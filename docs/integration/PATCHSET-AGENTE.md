# Patchset propuesto para /agente — no aplicado

Este repositorio entrega un cliente servidor y una consola piloto. No se ha abierto ni modificado el checkout de `/agente`; sus tipos de sesión, su bus, su almacén de aprobaciones y su Organizational Runtime siguen siendo supuestos pendientes de cotejar. No copiar tokens de este middleware a un bundle de navegador.

## Instalación revisable

Desde el checkout de este repo: `cd typescript`, `npm install --ignore-scripts`, `npm test`. Para pnpm usar `pnpm install --ignore-scripts` y `pnpm test`; el lock de pnpm debe generarse y revisarse en el consumidor, no se afirma que ya exista. El paquete es privado y no está publicado en npm. Puede consumirse mediante workspace local o artefacto empaquetado de una revisión aprobada. `private=true` y la licencia pendiente impiden presentar el paquete como distribución comercial terminada.

Importar `CyberClient` del paquete `@agntia/ciberseguridad` y `cyberRoutes` de `@agntia/ciberseguridad/hono`. El resolver de rutas recibe un Context Hono: debe validar la sesión interna, seleccionar en servidor el tenant permitido y obtener una credencial acotada desde un secret manager. El cliente fija tenant y origen aprobado; el navegador no elige ninguno. No reenviar Authorization, cookies, tenant_id o URL enviados por el cliente como prueba de autorización. El resolver es un límite obligatorio a implementar en el host, no autenticación suministrada por el SDK.

Configurar baseUrl/origins únicamente en servidor. El cliente admite HTTPS o loopback HTTP de laboratorio, rechaza credenciales en URL, query y rutas base. Redirects deshabilitados, respuesta máxima1MiB, timeout hasta30segundos. El allowlist de origen no sustituye controles de DNS/egress/TLS de la red privada: fijar el hostname del backend y no dar esa configuración a modelos ni usuarios finales. No hay método público request(path), shell o fetch(url).

## Herramientas de agentes

`agentTools(resolve)` entrega exactamente cyber_assets_read, cyber_findings_read y cyber_jobs_read. Su input es un objeto vacío cerrado. El resolver de confianza selecciona activo y tenant, obtiene credencial de principal kind=agent y delegación de un uso aprobada por humano para esa capacidad; devuelve resourceId y oneUseToken. Nunca usar credenciales de owner/reviewer para disfrazar a un agente. El backend valida identidad, manifest, política vigente, revisión, recurso, TTL, controles stop y consumo del token. Un timeout exige aclarar estado y emitir una delegación nueva según política; no reutilizar a ciegas una consumida. La tool no compra, cambia presupuesto, aprueba, delega permisos, notifica ni ejecuta contención.

El cliente servidor también permite lecturas nominadas y preflight estático; esas APIs no implican que el agente pueda llamarlas directamente. Un principal kind=agent conserva el bloqueo agent_gateway_required fuera de la vía gobernada. El router Hono es de lectura con paths/métodos cerrados; no expone el cliente entero ni las aprobaciones.

## Eventos

GET `/v1/tenants/{tenant}/outbox?consumer_id=...&after=0` devuelve envelopes sin contenido del cliente: schema_version, id, tenant_id, secuencia de auditoría, tipo, fecha, correlation_id, fuente y object_id. Cada item lleva content_hash. Los eventos se insertan en la misma transacción que la auditoría de operaciones seleccionadas: job terminado/error/conciliación y reserva/conciliación presupuestaria. No son un stream universal de todos los cambios ni eventos de incidentes confirmados.

Procesar el efecto y deduplicación en una transacción durable del consumidor antes de POST `/outbox/{id}/ack` con consumer_id y content_hash. Releer tras una caída; el emisor es at-least-once. No persistir un cursor avanzado antes de procesar los anteriores. ACK perdido se puede repetir; mismo id/hash no duplica el efecto en `SyntheticConsumer`. El ejemplo usa SQLite local y no demuestra integración con el bus real de AgntiaPro. ACK requiere events.ack; no se incluye en tools de modelo. Consumer_id identifica suscripción del backend autorizado, no acredita identidad por sí mismo.

## Revisión y despliegue

El patchset concreto en el repo madre requiere autorización expresa. La consola directa usa token en memoria solo como piloto: sustituir el login por sesión/BFF del host. La rotación de credenciales, autenticación del usuario, step-up y experiencia final pertenecen a AgntiaPro. No existe un segundo scheduler empresarial. Laia puede comunicar hechos del outbox y reportes con fuentes; no inventar actividad cuando no hay datos. Gates productivos, revisión independiente, licencia y ofertas siguen pendientes.
