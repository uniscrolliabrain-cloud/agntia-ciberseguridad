# Checkpoint05 — fases21–25

Fecha: 2026-11-10. Rama `feat/cyber-phases-21-25`. [PR#5](https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad/pull/5), apilada sobre PR#4. Baseline remoto `4f1e5d84b2eb8f7b4caca7f743efecdb64e429b8`, árbol local contrastado antes de cambios. El entorno se reinició durante publicación; el commit local `26af8aa` conservó la implementación. La publicación por GitHub API se retomó sin reset, merge o cambios en otros repositorios.

## Capacidades que añade

|Fase|Implementación|Gate completo|
|---|---|---|
|21 / D4P3|Logs operativos de schema cerrado, consulta por tenant/cursor, retención, hold sobre registros existentes, cuotas por número/bytes y métricas de pérdida|PARTIAL: backend productivo, continuidad de hold y control total de disco pendientes|
|22 / D4P4|Consola propia responsive, lectura autenticada, cobertura/frescura explícitas y navegación a referencias de job/evidencias|PARTIAL: navegación completa de findings y evidencia en UI, evaluación de accesibilidad amplia y backend de trazas pendientes|
|23 / D4P5|Webhook pasivo con HMAC, audiencia/tenant/fuente, reloj, deduplicación, watermark, cuotas/backpressure y acuse sin confirmar incidente|PARTIAL: sensores/adaptadores Wazuh/Falco/cloud y retención integral de eventos pendientes|
|24 / D4P6|Límites de señal, carga sintética concurrente, saturación, fallo de logs opcionales sin bypass de autorización y mediciones|PARTIAL: volumen realmente lleno, despliegue multitenant y dimensionado/coste de producción pendientes|
|25 / D5P1|Registro de manifests ligado a principal agente, revisión por dos humanos, grants firmados de lectura, delegación atenuada, revocación en cadena y consumo único transaccional|PARTIAL: gateway universal, aislamiento de credenciales de proveedores e identidad organizacional real pendientes|

Los gates previos permanecen pendientes de revisión independiente. Estos componentes no se habilitan para escanear clientes, no instalan sensores privilegiados y no conectan `/agente`.

## Logs y privacidad

Los logs operativos persisten únicamente nivel, componente, evento, code y correlation UUID dentro de listas cerradas, más timestamp/ID generados en servidor. Headers, excepciones, stdout de herramientas y mensajes arbitrarios se descartan: no se pretende detectar por regex todos los secretos posibles. Los originales permanecen en el mecanismo de evidencia del bloque anterior; auditoría inmutable sigue separada. El logger de peticiones solo recibe tenant resuelto tras autenticación/autorización. Las peticiones sin identidad confiable no generan un log tenant inventado; continúan los errores seguros de frontera.

Cada tenant tiene cuotas de500 registros y256000 bytes por defecto, retención7días y consulta con secuencia monótona, limitada a100 filas. La purga respeta hold y no borra audit/evidencias. El hold del endpoint afecta los registros presentes, no crea una política legal continua para futuros registros. Una cuota agotada descarta el log opcional y cuenta la pérdida; el fallo no cambia permisos ni sustituye auditoría obligatoria. No se promete que estas cuotas acoten SQLite/WAL, backups o el volumen entero.

## Consola y evidencia de interfaz

`/console` sirve un shell público sin datos; la consulta de tenant requiere bearer. El token solo permanece en memoria de la pestaña, nunca URL/localStorage; el campo password se vacía al consultar. Logout y cambios de sesión invalidan resultados en vuelo. Se renderizan datos mediante textContent y CSP restringe scripts, estilos, conexiones y framing. En ausencia de ejecuciones: not_tested, freshness unknown y Collector not_monitored. No hay salud verde inferida de datos ausentes.

La vista muestra las últimas20 ejecuciones y hallazgos, referencias de evidencia y relaciones de investigación. Cada petición se reautoriza; no expone queries ni URLs de un backend global. La consola no es un SOC/XDR, no ofrece administración de claves ni un chat con autoridad implícita.

## Eventos pasivos

Cada fuente se configura en servidor con tenant, targets aprobados, referencia de clave propia y límite por minuto. El productor firma HMAC-SHA256 del JSON canónico validado; audiencia `agntia-ciberseguridad.events`. Clave mínimo32 caracteres de alta entropía, fuera de Git/DB/prompts. TLS/red privada deben añadirse en despliegue real. Una fuente no cambia tenant/target mediante payload. Los campos admitidos son cerrados; no se acepta un documento arbitrario ni instrucciones para un LLM.

La ventana de envío es cinco minutos; occurred_at puede reflejar hasta30días anteriores y cinco minutos de adelanto, siempre marcado producer_reported. Evento idéntico da recibo duplicate; mismoID con contenido distinto da409. El watermark solo avanza al commit; se conservan observaciones fuera de orden sin rebobinarlo. El estado pendiente y cuotas totales provocan429, no una falsa recepción exitosa. La respuesta202 significa señal recibida, no incidente ni trabajo de respuesta completado. El acuse autenticado solo libera cola de pendientes; no confirma ataque. No hay sensor EDR ni adaptación real de Wazuh/Falco/cloud en este bloque.

## Registro y delegación agéntica

Manifest cerrado: binding de agente provisionado en servidor, versión/hash declarados, proveedor, capabilities de lectura conocidas, activos existentes y clasificación redacted_metadata. No admite shell, URLs, schema remoto o red de salida. El hash de artefacto es declaración de inventario, no descarga ni auditoría de un binario. La propuesta requiere humano reviewer/owner y aprobación por otro humano.

Los grants tienen audiencia `agntia-ciberseguridad.read`, policy delegated-read-v1, nonce, caducidad máxima5minutos, principal/fingerprint vinculados y hash/revisión de manifest. El HMAC se calcula en servidor con clave externa; solo se almacena el hash del token y su sobre, no bearer original. Un agente titular puede delegar a otro manifest aprobado, reduciendo o manteniendo capabilities/recursos y sin ampliar caducidad; profundidad máxima cuatro niveles y ocho hijos por padre. Revocación de ancestro, expiración, rotación de credencial o modificación de manifest bloquean uso posterior.

La operación `/delegations/use` acepta únicamente tres lecturas nominadas de metadatos: assets.read, jobs.read y findings.read. Consumo y audit quedan en una misma transacción; dos consumidores concurrentes solo obtienen un éxito. No resuelve secretos de proveedores ni ejecuta código/herramientas. No se anuncian controles sobre otras rutas heredadas: un bearer con su rol anterior todavía puede acceder según sus permisos. Gobernar toda llamada y caminos externos corresponde al gateway de fases posteriores. Ver [RISKS.md](RISKS.md).

## Verificación

Baseline:103 descubiertos,92 correctos y11 skips locales (7Docker,4SDK). Primera batería ampliada:116 descubiertos,105 correctos,11 skips,0 fallos.13 pruebas nuevas cubren cuotas/retención, secretos centinela descartados, firmas/replay/reordenación, aislamiento, revocación, expiración y carreras de consumo. La prueba browser local se intentó y falló porque el sandbox prohíbe crear sockets; se ejecuta Chromium real en CI separada. Los resultados remotos y cualquier fallo se registran en `evidence/` antes de entrega; no se cuentan skips como tests correctos.

La carga sintética de100 solicitudes concurrentes(concurrencia10) incluye20 denegaciones cross-tenant esperadas, saturación de logs a10 registros y fallo inyectado del log opcional. Se registran p50/p95, RSS/CPU de proceso, bytes por registro, series y pérdida. ASGI no usa TCP/TLS ni scans; no determina capacidad productiva o SLA. La fórmula de coste está en resource_limits.json; no hay tarifa cloud medida ni suscripción comprada.

## Resultados ampliados y navegador

Batería local final:119 descubiertos,108 correctos,11 omitidos y0 fallos,5.729s. Incluye15 tests nuevos de controles, un test nuevo de migración4→5 y los103 anteriores. La migración conserva evidencia/audit existentes. Se verifica además que el wheel distribuya los tres assets de consola.

Chromium real en CI:PASS en1440×1000 y390×844, sin overflow ni errores JS, cross-tenant rechazado y respuesta en vuelo tras logout descartada. Run42902060399, SHA a02e59300174e0f9d7bc4f697e889c64a111c1e5. Capturas sintéticas con hash y artefacto en evidence/browser-ci.json; no se atribuye revisión visual manual independiente. El primer runner ubuntu-latest no fue compatible con Playwright; se fijó ubuntu-24.04 y se conserva la causa del fallo.

## Cierre de validación remota

Código validado SHA `ca6ae9a471d90ce7c987666b7104b88637afbe07`: **119 tests distintos correctos**,112 del núcleo con SDK real en cada matriz Python3.11/3.12 y7 Docker en job separado. No se suman versiones ni push/PR duplicados como tests distintos. Los7 skips de runtime son los mismos tests ejecutados en el job Docker. Distribución wheel comprueba también HTML/JS/CSS de consola. Configuración/recepción OTLP y promtool:PASS. Chromium móvil/escritorio y carrera de logout:PASS. CI íntegra, artefactos y hashes en evidence/ci.json y browser-ci-final.json.

Carga concurrente en CI con SDK activo:100 solicitudes,20 denegaciones esperadas,0 resultados inesperados, p50=3.627ms, p95=4.831ms,10 logs retenidos,2360bytes y71 drops declarados,20 series. RSS pico65652KiB de proceso. Estos resultados incluyen saturación/fallo opcional de logs y no prueban capacidad o coste de producción. Ver JSON sin redondear.

## Continuidad

Siguiente bloque26–30: seguir los cinco IDs de la campaña relativos al gateway y evaluación de seguridad agéntica. Releer los IDs exactos antes de actuar. Mantener los gates PARTIAL, no modificar `/agente`, no desplegar ni fusionar automáticamente. Ver operaciones, riesgos y decisiones del checkpoint.
