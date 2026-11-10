# 03 · Seguridad agéntica y conceptos propios

Propuestas de ingeniería, no invenciones patentadas ni resultados experimentales. Se inspiran en mecanismos publicados de capacidades, control de flujos, políticas y evaluación; todavía no están implementadas.

## Amenazas a cubrir

Inyección directa/indirecta y multimodal, envenenamiento de RAG/memoria, tool poisoning, cambios de descripción de tools/skills, confused deputy, delegación excesiva, robo/reutilización de tokens, exfiltración, fuga entre tenants, SSRF, supply chain de paquetes/modelos, output handling inseguro, llamadas recursivas y coste descontrolado. Los agentes propios también pueden equivocarse o ser comprometidos: no clasificar un agente como bueno por su marca, país o personalidad.

Marcos de referencia: [OWASP Agentic Top10 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/), [OWASP MCP Top10](https://owasp.org/projects/mcp-top-10), [seguridad MCP](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices) y [NIST GenAI Profile](https://doi.org/10.6028/NIST.AI.600-1). Son vocabularios y guías, no certificados de seguridad.

## Propuesta A · Autorización verificable por acción

Cada llamada sensible requiere un sobre canónico: principal verificado, tenant, finalidad, recurso, operación, argumentos permitidos, sensibilidad, origen, concesión padre, política, expiración, nonce y presupuesto. La firma la emite un servidor de confianza, no un prompt. La delegación solo reduce privilegios; el receptor verifica audiencia, TTL, revocación y límites.

Comprobar la herramienta y también argumentos/destino/efectos. Permitir send_email no equivale a permitir cualquier destinatario o adjunto. Una lectura de un fichero secreto y una salida permitida por separado pueden formar una fuga: necesitamos seguimiento de datos y no solo ACL de funciones.

## Propuesta B · Separación entre evidencia y control

Etiquetar documentos, webs, issues, memoria recuperada y tool outputs como no confiables, con procedencia y restricciones de salida. Un extractor aislado produce hechos tipados y citas; un planificador ve una representación minimizada, nunca instrucciones elevadas por el origen. Un ejecutor determinista verifica cada efecto, aunque el modelo insista.

CaMeL muestra una dirección útil, pero su modelo de amenaza no cubre toda falsedad textual o phishing: además de controlar herramientas necesitamos procedencia visible y verificaciones de negocio. No copiar su arquitectura como una prueba general de inmunidad. Los redactores de informes deben evitar convertir el texto hostil de un log en órdenes para el coordinador.

## Propuesta C · Registro versionado de tools y skills

Manifiesto firmado/hash por herramienta: proveedor, versión, descripción, schema, permisos, clasificación de datos, URLs autorizadas y dependencias. Cualquier cambio invalida su admisión anterior y exige revisión según riesgo. Registrar también instrucciones de skills, no únicamente el binario. No ejecutar un MCP/skill descargado para «ver si es seguro» en el host.

Inventariar endpoints realmente usados, evitar token passthrough y aplicar controles OAuth/audiencia acordes a la versión fijada del protocolo. No anunciar cumplimiento de la especificación más reciente sin un test contractual. Un servidor externo comprometido sigue siendo no confiable aunque su metadata estuviera firmada antes.

## Propuesta D · Evidencia y contexto de riesgo conectados

Relacionar activo→commit→dependencia→imagen→deployment→identidad→agente→herramienta→dato→finding. Empezar con relaciones en una base convencional; no es necesario desplegar una base de grafos o recrear Wiz para priorizar. La información faltante se marca unknown.

Prioridad combina severidad, exposición, sensibilidad, uso real, explotación conocida y fiabilidad de evidencia. CVSS/EPSS/KEV ayudan; no equivalen a explotación comprobada en el cliente. Excepciones caducan y preservan responsable/motivo. El LLM puede explicar, no reducir silenciosamente severidad para mejorar un dashboard.

## Propuesta E · Presupuesto de acciones y degradación segura

Limitar llamadas, pasos, bytes de salida, destinos, coste monetario, paralelismo y tiempo, además de tokens. Reservar antes de ejecutar, reconciliar gasto real y bloquear nuevos efectos sin margen. Al agotar IA se mantiene enforcement determinista y se anuncian las tareas diferidas; no desactivar auditoría básica o aislamiento.

Los límites de SaaS/retención deben impedir gasto técnico no aprobado; el middleware no puede garantizar la factura de un proveedor sin cuotas/precios contractuales y medición. La acción denegada por coste debe distinguirse de una denegación por amenaza.

## Propuesta F · Antifraude con verificación de contexto

Combinar reputación permitida, dominio/URL normalizada, SPF/DKIM/DMARC observados, cambios de destinatario/IBAN, procedencia y patrón de solicitud. Ninguna señal individual prueba fraude. Confirmar modificaciones de pago por un canal previamente registrado, no por teléfono o enlace incluido en el mensaje sospechoso. No hacer transferencias ni bloquear empleados basándose solo en clasificación IA.

Los análisis de voz/deepfake se presentan como señales con incertidumbre. C2PA/provenance puede aportar información positiva verificable cuando existe; ausencia de firma no prueba falsedad y una firma válida no demuestra veracidad de toda afirmación. No prometer detección universal de estafas generadas por IA.

## Evaluación requerida

Fixtures benignos y adversariales de texto, HTML, repositorios y salidas de tools, con canarios sintéticos. Medir acciones indebidas bloqueadas, tareas legítimas completadas, falsos positivos/negativos, escalados, latencia p50/p95, coste y cobertura. Evitar vender una tasa de ataques fallidos como seguridad si el agente simplemente no hace ninguna tarea.

Ensayar memoria contaminada, cambio de schema, instrucciones legítimas de terceros, datos en idioma distinto, modelo cambiado y ataque adaptativo en laboratorio. No publicar ni ejecutar campañas ofensivas reales como condición de esta investigación. Los casos de alto impacto deben demostrar rechazo por controles externos al modelo aun cuando el texto generado sea malicioso.
