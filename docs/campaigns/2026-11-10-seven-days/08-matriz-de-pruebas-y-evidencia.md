# 08 · Pruebas, evidencia y aceptación

Esta edición contiene **escenarios planificados**, no resultados de ciberseguridad. El [catálogo](gate-scenarios.md) y campaign.json enumeran84 gates de comportamiento. Los tests concretos se escribirán conforme se implemente cada componente; no existe una suite aprobada por crear carpetas con su nombre.

## Capas de validación

| Capa | Qué demuestra | Qué no demuestra |
|---|---|---|
| Unidad/propiedades | Reglas, canonicalización, parsers y transiciones bajo entradas controladas | Proveedor/ORM/host reales |
| Contrato simulado | Formatos/errores y composición esperada | Compatibilidad de una versión instalada |
| Contrato real | Scanner/motor/API fijado en entorno aislado | Cobertura de todos los lenguajes/casos |
| Integración | Persistencia, sandbox, red, queues y scopes reales | Seguridad universal o servicio global |
| E2E | Recorrido del cliente con roles y evidencia | Conformidad jurídica automática |
| Adversarial/fallos | Invariantes bajo entradas hostiles y fallos seleccionados | Ausencia de fallos desconocidos |
| Rendimiento/coste | Medida para un hardware/workload/periodo concreto | SLA o coste de cualquier cliente |
| Revisión humana | Aceptación del scope y riesgos explícitos | Sustitución de autoridad reguladora |

## Escenarios transversales obligatorios

Cross-tenant en API, DB, fichero, reporte, trace y evento; grants/actores revocados; rutas/DNS/redirects fuera de scope; sandbox sin credenciales/sockets; supply chain no ejecutada; manifest/schema drift; modelo hostil; exfiltración por composición; aprobaciones replay/caducadas; caída de proveedor/collector; parser inválido; DB/reglas stale; worker antiguo; reservas concurrentes; crash antes/después de efecto; backup/restore; corrupción y claves; tarea legítima completada además del bloqueo de ataques.

Cada caso usa datos sintéticos y objetivos autorizados. Un canario es un valor de laboratorio generado para probar fugas, no una credencial real o muestra de cliente. No usar malware real ni secretos de clientes para mejorar aparente realismo.

## Registro mínimo por ejecución

FechaUTC, autor/principal, fase/tarea, SHA de implementación y configuración, SO/arquitectura, hardware/límites, versiones/digests/hashes de reglas/DB, comando real, entradas minimizadas, código de salida, duración, tests ejecutados/pasados/fallidos/skipped, artefactos y hash, límites de cobertura, revisión y siguiente paso.

No pegar stdout bruto de scanner, bearer, dump o prompt confidencial en Git. Los logs privados se guardan fuera del checkout; el reporte público enlaza referencias redactadas. Guardar el original autorizado bajo custodia no da permiso para enviarlo a un SaaS público.

## Estados

- PLANNED/NOT_EXECUTED: especificado o escrito sin ejecución.
- PASS: comando/caso ejecutado y resultado esperado observado en el scope declarado.
- FAIL: ejecución no cumple el criterio; conservar evidencia útil.
- BLOCKED: falta entorno, permisos o dependencia. No contarlo como PASS.
- PARTIAL: evidencia incompleta con cobertura declarada.
- DEFERRED: trabajo fuera de esta entrega, con owner/motivo/dependencias.
- NOT_APPLICABLE: requisito no aplicable por hecho verificado, no por comodidad.

Skipped no cuenta como gate aprobado. Un fallo esperado correctamente bloqueado puede ser un test PASS; el producto no debe presentar ese trabajo bloqueado como auditoría realizada. Los reportes necesitan ambas semánticas.

## Medición de seguridad agéntica

Reportar tarea benigna completada, bloqueo adecuado, acción indebida efectiva, rechazo/ignorancia, falsos positivos/negativos conocidos, escalados, coste, latencia y tamaño de suite. Guardar modelo/prompt/policy/versiones y datos de evaluación separados del ajuste. Ataque fallido no significa defensa si el agente no ejecutó ninguna tarea útil.

Comparaciones con papers solo bajo protocolo/versiones compatibles, con diferencias explícitas. No importar resultados de AgentDojo/CaMeL/Progent al marketing propio. Un mecanismo inspirado en ellos no hereda sus garantías ni supuestos.

## Observabilidad y SLO

Fijar antes de la prueba hipótesis de carga, objetivo de latencia, frescura, pérdida admitida y presupuesto de recursos. Medir p50/p95/error ratio con denominadores y registrar regresiones. Los valores objetivo son propuestas hasta probarlos; no cambiarlos después para maquillar la aceptación. La audit/evidencia requerida no se samplea como un trace opcional.

Cardinalidad y datos sensibles son parte del gate: meter tenantID/userID/URL arbitraria en labels globales puede causar fuga y coste. Correlación por IDs opacos se consulta mediante autorización, no un datasource global expuesto al cliente.

## Aceptación de jornada y release

Usar las [plantillas](templates/phase-report.md). El revisor puede bloquear dependientes aunque existan commits y tests unitarios verdes. Para cerrar día7 se publica una tabla por capacidad, no un único «todo aprobado». Los M1 diferidos y condiciones legales/operativas pendientes aparecen en el informe ejecutivo y en el paquete descargable.
