# 01 · Visión y requisitos trazables

Fecha de investigación: 2026-11-10. Esta especificación convierte la petición del propietario en un producto construible; no acredita capacidades ya implementadas.

## Mandato del propietario

Crear `agntia-ciberseguridad` como middleware del repositorio madre `/agente`, donde un equipo de agentes y humanos observa, audita, protege y explica la seguridad del software de clientes. Combinar ciberseguridad tradicional y agéntica, detectar ataques/estafas/abuso de IA, reunir evidencias y preparar reportes. Ayudar a respetar AI Act, RGPD/GDPR y obligaciones relacionadas. Priorizar repositorios abiertos y conceptos propios, admitiendo los mejores servicios comerciales que encajen en Lite ≤30€, L ≤70€ y XL ≤300€ mensuales.

La ambición de aprender de las compañías de referencia se traduce en un catálogo de capacidades y patrones, no en prometer toda su telemetría, personal, cobertura global, contratos o certificaciones dentro de esos importes. La protección reduce riesgos, verifica controles y detecta cambios; no garantiza ausencia de vulnerabilidades, ataques o errores jurídicos.

## Producto visible al cliente

El cliente usa AgntiaPro. Puede preguntar «¿qué riesgos reales hay en este despliegue?», «¿puede este agente enviar documentos fuera de la empresa?» o «prepara un informe para mi responsable de seguridad». Recibe inventario, findings priorizados, cobertura conocida, pruebas, excepciones, propuestas de corrección y responsables. Los avatares pertenecen a la experiencia del repo madre; no son un mecanismo de autorización.

Recorrido principal: registrar activos autorizados → capturar snapshot → ejecutar un perfil de auditoría permitido → normalizar resultados → revisar falsos positivos → explicar riesgo/contexto → proponer corrección → aprobar si corresponde → aplicar en rama/staging → repetir pruebas → conservar resultado. Un informe debe decir qué no se probó y qué fuentes estaban desactualizadas.

## Ámbitos de capacidad

| ID | Área | Resultado objetivo | Primera entrega |
|---|---|---|---|
| R01 | AppSec | Secretos, dependencias, SAST, imágenes, IaC y SBOM con trazabilidad | Solo snapshots autorizados; no ejecutar código del cliente |
| R02 | Seguridad de agentes | Inventario de agentes/tools/skills, scopes y control de llamadas | Policy gateway con simulación y decisiones reproducibles |
| R03 | IA/LLM | Evaluación de inyección, fuga, RAG/memoria, cambios de herramientas | Benchmarks sintéticos, no ataque a modelos ajenos |
| R04 | APIs/web | Configuración, autenticación, exposición y pruebas permitidas | Pasivo por defecto; activos solo con perfil firmado |
| R05 | Cloud/runtime | Configuraciones, identidades y eventos | Integrar fuentes ya autorizadas; agentes host opcionales posteriores |
| R06 | Antifraude | Indicadores de phishing, suplantación y acciones sensibles | Triage y verificación por canal confiable, no veredicto infalible |
| R07 | Cumplimiento | Aplicabilidad, controles, evidencia y pendientes AI Act/RGPD | Matriz revisable, no sello de conformidad |
| R08 | Respuesta | Casos, contención propuesta, rollback y recuperación | Sin cambios en producción por defecto |
| R09 | Reportes | Ejecutivo, técnico y regulatorio con fuentes y cobertura | JSON/HTML primero; PDF/SARIF después de validar |
| R10 | Coste | Presupuesto por tenant con reserva y degradación explícita | Modelo documentado; enforcement todavía pendiente |

## Equipo y separación de funciones

Pedro puede ser el coordinador de seguridad en AgntiaPro. Se proponen especialistas AppSec, agentes/IA, cloud/runtime, privacidad/cumplimiento e incidentes. Es una distribución funcional, no crear cuentas con poderes por sus nombres. Un principal puede preparar un finding; un responsable distinto acepta riesgo o autoriza cambios sensibles. El LLM no se aprueba sus propias ampliaciones de privilegios.

El runtime de `/agente` coordina objetivos, memoria y rotas. Este middleware publica operaciones, jobs y eventos; no crea un segundo organigrama ni un scheduler empresarial independiente. La cadencia propuesta es revisión continua de eventos dentro de cobertura, auditorías por cambio, resumen diario de hechos y revisión periódica humana de riesgos/excepciones.

## Calidad y semántica

Distinguir not_tested, collecting, failed, partial, observed, suspected, confirmed, accepted_risk, remediated y verified_fixed. Un scanner que devuelve cero hallazgos pudo no entender el lenguaje o no tener la base actualizada. Un detector que marca contenido como sospechoso no prueba fraude; un scoring bajo no significa cumplimiento.

Los roles y fuentes de verdad serán explícitos: `/agente` para identidad organizacional, cliente para autorización de activos y aceptación de riesgo, herramientas para observaciones acotadas, middleware para normalización/evidencia y autoridad competente para resultado administrativo. Los datos de un repositorio, log, issue o documento nunca amplían permisos.

## Fuera del primer alcance

No hay explotación autónoma de terceros, campañas de phishing reales, recuperación ofensiva, compras, cambios de DNS/firewall/IAM en producción ni presentación de notificaciones regulatorias automáticas. Tampoco servicio MDR humano24/7, desarrollo de un EDR propio, defensa contra DDoS volumétrico por un pequeño VPS ni certificación jurídica automática. Estas exclusiones delimitan productos realistas y evitan vender una cobertura que no podemos prestar.

La presente fase entrega README/docs, inventario de fuentes, metadatos de repos y configuración presupuestaria propuesta. No se instala ni ejecuta ningún scanner. El siguiente trabajo es implementar un núcleo mínimo con fixtures, luego integrar pocas herramientas y demostrar un recorrido verificable antes de ampliar el catálogo.
