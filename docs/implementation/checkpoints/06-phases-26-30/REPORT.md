# Checkpoint06 — fases26–30

Fecha:2026-11-10. [PR#6](https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad/pull/6), rama `feat/cyber-phases-26-30`, apilada sobre PR#5. Baseline remoto `d41e29b075e994803b409018ef07ca8ea75d3268`, árbol `e7d58cb1ce7174de2066d164975631d1b6954c11` idéntico al checkout local al iniciar.119 pruebas descubiertas,108 correctas y11 omitidas en baseline local. No se modifica `/agente`, no se despliega, no se compra y no se fusiona main.

## Resultado para producto

Este bloque convierte la delegación del corte anterior en una frontera efectiva dentro del servicio. Un principal provisionado como agente ya no usa directamente las rutas heredadas aunque su rol contenga permisos amplios. Las operaciones gobernadas comprueban política, principal, recurso, manifest, caducidad, token de un uso y epoch vigente. Un texto del modelo no puede elegir owner, tenant, destinos o una implementación de tool.

|Fase|Capacidad entregada|Gate completo|
|---|---|---|
|26 / D5P2|Motor determinista cerrado, hash de reglas/código, dry-run y autorización en cada llamada; rutas heredadas y worker antiguo sin bypass agéntico|PARTIAL: revisión independiente, federación de identidad y más capacidades gobernadas pendientes|
|27 / D5P3|Hechos JSON tipados ligados a evidencia, etiquetas de origen/sensibilidad, cuarentena, release humano ligado a hash/destino y validación de DNS/IP|PARTIAL: transporte egress no habilitado, no desclasificación automática ni protección multimodal universal|
|28 / D5P4|Subconjunto MCP2025-11-25 propio: handshake, sesión autenticada, tools/list y tools/call; drift de descriptor/schema/skill/dependencias invalida autorizaciones|PARTIAL: sin cliente MCP externo, OAuth/OIDC o conformidad completa del protocolo|
|29 / D5P5|Corpus propio reproducible y runner sin modelo con utilidad benigna y peticiones adversariales; fingerprint de configuración y coste externo cero|PARTIAL: no modelo real, dataset independiente/adaptativo ni reproducción de AgentDojo|
|30 / D5P6|Parada persistente por tenant/agente/tool/grant, CLI con segunda credencial, revisión humana e idempotencia de notas locales, pruebas de carrera/rollback|PARTIAL: no remediación/efecto externo, MFA real o cancelación universal de trabajos ya ejecutados|

Los gates anteriores no se convierten en PASS. Se conserva ReleaseGates cerrado por defecto. Se entrega una base verificable, no paridad global con una plataforma SOC ni una certificación de seguridad.

## Frontera de autorización

Authenticator separa una comprobación interna de rol de la autorización ejecutable. Para agentes, salvo la capacidad de protocolo agents.read, requiere un contexto privado creado únicamente por código del gateway tras verificar el grant. Ese contexto no se extrae de headers, instrucciones ni memoria. Se descarta al salir de la operación. Las rutas de assets, findings, logs, reports, dashboard y jobs no se habilitan simplemente por usar un bearer de rol analyst. Se prueba también que un job heredado cuyo principal pasa a agent no alcanza el scanner.

El rol humano y las credenciales de servicio del servidor conservan sus reglas anteriores. `kind=agent` es una clasificación explícita del administrador: no se infiere por llamarse Laia/Marco ni se puede cambiar desde un prompt. Una integración que declare un agente como human/service elude la clasificación; esto requiere gobernanza/IdP real antes de habilitar clientes. No se controla actividad fuera de este servicio ni acceso directo al host, proveedores o repositorios que el operador entregue por otros caminos.

Se compara OPA/Cedar y se elige un motor Python pequeño de acciones cerradas. No se interpreta un DSL suministrado por un usuario. El hash une reglas y fuentes relevantes de implementación; un cambio exige configurar el hash nuevo, aprobación operativa y nueva evaluación. Ausencia, hash distinto, expiración o error de motor deniegan la operación. No hay fallback owner. Los tokens anteriores al gateway quedan registrados para trazabilidad pero pierden validez al carecer de hash/epoch.

## Datos como hechos, no como instrucciones

Un humano autorizado registra evidencia ya custodiada y la vincula a un activo de su empresa. Se acepta un JSON de paquetes con nombres/versiones acotados; campos de control adicionales o contenido no compatible se conservan como referencia en cuarentena. No se ejecuta un repositorio, no se abre un PDF para interpretar instrucciones y no se usa un LLM para extraer autoridad.

La proyección conserva origin=custodied_evidence, trust=untrusted_data, classification=confidential, hash de contenido, activo y audiencia local. La etiqueta no desaparece porque la evidencia haya sido redactada. Una consulta incluye únicamente flows autorizados para ese recurso; fuentes fuera de retención o purgadas quedan bloqueadas. Los hechos derivados almacenados en SQLite siguen necesitando cifrado del volumen y retención operacional.

La salida externa de agentes se deniega. Una propuesta de release exige destino de servidor aprobado, contenido exacto, audiencia, TTL y revisión por otro humano. El preflight valida DNS/IP y bloquea metadata/redes no permitidas; aun aprobado devuelve transporte unsupported, allowed_to_send=false y bytes_sent=0. No hay envío, proxy HTTP genérico ni resolución de secretos de proveedor. Instalar un transporte más adelante exigirá revisión de TLS, DNS fijado en conexión, timeout, idempotencia y consentimiento; una lista de hosts por sí sola no basta.

## MCP y supply chain

El recurso MCP es el servicio propio; no se conecta un servidor remoto ni se reenvía su bearer. El cliente autentica su binding y usa su grant de audiencia propia. Initialize fija versión, capabilities limitadas e identidad de cliente tipada; notifications/initialized es obligatorio antes de listar/llamar tools. La notificación devuelve202 sin cuerpo. Sesión ligada a tenant, actor/fingerprint, manifest, tool/descriptor, epoch y TTL máximo2minutos. Request IDs enteros monótonos permiten rechazar replay. Origin de navegador, métodos, schemas y callbacks fuera del subconjunto se rechazan.

Solo se admite la tool de lectura conocida agntia.metadata.read, con esquema igual al del executor. El descriptor almacena hashes de descripción, skill y dependencias; no inserta instrucciones de tercero en un prompt privilegiado. Proponer cambios pone la versión en pending_review y eleva epoch; otro humano debe aprobar el hash exacto. Sesiones y grants previos quedan invalidados. El historial de versiones es append-only. No se instala ni ejecuta una skill por inventariarla.

## Efectos y parada

El único efecto nuevo es una nota local de revisión, no una remediación productiva. El agente propone texto redactado, activo, fuentes y coste cero usando una capability notes.propose explícita. Otro humano distinto del proponente y del emisor del grant aprueba el hash/revisión y la caducidad. En commit se revalida también que ese revisor siga vigente. No se convierte la nota en finding reviewed ni se modifica una política por texto libre.

Reserva de0céntimos, nota, consumo del token, estado e historia se confirman en una transacción SQLite. La clave idempotente es persistente; replay idéntico devuelve el mismo receipt, contenido distinto da409 y un fallo obligatorio de audit revierte todo. No se supone que esta transacción cubra un proveedor remoto. Perder un HTTP ACK local se recupera consultando/reintentando la misma clave, sin crear otra nota.

Los controles persistidos permiten stop/resume por tenant, agente, tool o grant. Cada cambio eleva el epoch del tenant, invalidando conservadoramente todos sus grants/sesiones previos. Resume no reactiva tokens viejos. La CLI y endpoint exigen humano autorizado y una segunda credencial operativa, separada de bearers; no se denomina MFA a dos secretos del mismo entorno. El stop se serializa con efectos locales: si un efecto ya tenía la transacción, puede confirmar antes de que responda el stop. No se borra ni deshace. Tras la respuesta no se admite otro efecto con la autorización anterior; receipts históricos no son nuevas ejecuciones.

## Verificación y límites de evaluación

El registro de comandos/resultados está en evidence/. La suite ampliada cubre política ausente/caída/caducada, nested arguments, Unicode confusable, rutas heredadas, worker, DNS metadata, cuarentena, MCP/handshake/replay/drift, aprobación revocada, carrera de commit/stop, rollback y CLI sin credenciales impresas.

El corpus propio contiene8 tareas benignas y16 candidatos adversariales estáticos. El runner completó8/8 y rechazó16/16 localmente. Los denominadores, FP/FN, latencias, hash de suite/esquema/código, seed y ausencia de modelo se conservan. No se llama a un modelo ni API de pago. No son ataques adaptativos ni un benchmark real de prompt injection; idiomas de las anotaciones/documentos no acreditan robustez multilingüe de un LLM. PDF/imagen/RAG real no evaluados. Ninguna métrica se hereda de CaMeL/AgentDojo u otro paper.

## Cierre de validación ejecutada

Código verificado SHA `06a5ddf933311da25dd8a75b65dd7af501df0e58`: **143 tests distintos correctos**,136 del núcleo en cada matriz Python3.11/3.12 con SDK real y7 Docker en job separado. No se suman matrices o eventos push/PR como tests nuevos. Suite local final:143 descubiertos,132 correctos,11 skips de entorno y0 fallos(9.658s).24 tests nuevos frente al baseline. Runtime/distribución, schemas, validadores, Collector/Prometheus/OTLP y navegador Chromium1440px/390px:PASS. Capturas sintéticas con hash/artefacto, sin atribuir revisión visual independiente.

Evaluación original en CI:8/8 tareas benignas completas;16/16 candidatos adversariales rechazados; FP/FN0 dentro de ese corpus. Sin modelo real, sin API de pago, sin reproducción de papers. Gateway p50=1.566ms y p95=2.599ms en el runner scriptado, no SLA. Configuración/hash y denominadores completos en evaluation-ci.json.

Parada local en CI con SDK:10 acuses y10 siguientes llamadas denegadas; p50 de acuse=3.663ms, p95=3.813ms. Son llamadas directas en un nodo SQLite, sin HTTP/TLS, red o proceso remoto. Las carreras commit/stop se prueban aparte: un efecto ya confirmado no se deshace.

El esquema MCP visible al modelo no contiene token: el backend inyecta X-Agntia-Grant. Se comprobó también el recorrido HTTP completo con ese header, initialize/initialized y tool call autorizado. Egress/transporte externo, OAuth externo, modelos reales, remediación y MFA productivos continúan pendientes. Gates completos siguen PARTIAL.

## Continuidad

Siguiente bloque31–35: aplicabilidad legal, privacidad/brechas, antifraude, incidentes/contención propuesta y remediación revisable/retest según sus IDs exactos. Antes de continuar leer campaign.json y los riesgos del checkpoint. No habilitar efectos externos o clientes por tener tests verdes. Mantener el aislamiento, las limitaciones de identidad y los gates de revisión independiente.
