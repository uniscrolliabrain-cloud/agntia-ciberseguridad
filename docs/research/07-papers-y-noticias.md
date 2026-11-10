# 07 · Papers y noticias: resultados útiles para el diseño

Corte: 2026-11-10. Investigación inicial selectiva de fuentes primarias, no revisión sistemática exhaustiva. Se leyeron abstracts/páginas y secciones concretas de modelo de amenaza de CaMeL/Progent. No se reprodujeron experimentos, no se auditó todo su código ni se incorporaron pesos. Los resultados publicados no son métricas propias de Agntia.

## Papers seleccionados

| Fuente/version observada | Aporte observado | Decisión de diseño y límite |
|---|---|---|
| [AgentDojo,2406.13352v3](https://arxiv.org/abs/2406.13352v3),2024 | Benchmark de tareas con tools y datos no confiables | Usarlo como base de regresiones; éxito en suite no equivale a seguridad del cliente |
| [ASB,2410.02644](https://arxiv.org/abs/2410.02644) | Taxonomía y evaluación de ataques/defensas agénticas | Diversificar escenarios; lectura inicial de resumen/ficha, no replicación |
| [CaMeL,2503.18813v2](https://arxiv.org/html/2503.18813v2),2025 | Separar control/datos y aplicar capacidades a los flujos | Inspirar executor/policy; no usar un porcentaje antiguo o de una versión distinta como garantía |
| [Progent,2504.11703v3](https://arxiv.org/html/2504.11703v3),revisado14-05-2026 | Políticas simbólicas sobre tools/argumentos y control de ampliación/reducción | Permisos monotónicos sin aprobación; verificar cada llamada fuera del LLM |
| [AgentDyn,2602.03117v3](https://arxiv.org/abs/2602.03117v3),07-05-2026 | Tareas abiertas/dinámicas y tensión seguridad/utilidad | Incluir instrucciones legítimas de terceros y cambios de entorno, no solo prompts evidentemente maliciosos |
| [Assessing Automated Prompt Injection Attacks in Agentic Environments,2606.10525](https://arxiv.org/abs/2606.10525),09-06-2026 | Estudia evaluación automatizada en entornos agénticos y dependencia del modelo | Retest tras cambios de modelo/prompt; no asumir transferencia universal |
| [Ignored, Not Refused,2610.23254](https://arxiv.org/abs/2610.23254),16-10-2026 | Diferencia ataque ignorado, rechazo y cumplimiento de tarea | Medir matriz de seguridad y utilidad; no vender un agente paralizado como defensa excelente |

### Qué sí tomamos de CaMeL

En el modelo revisado el prompt del usuario es confiable y hay supuestos sobre memoria. Su protección de flujos no resuelve toda manipulación puramente textual o phishing. Adoptamos la separación como patrón y añadimos procedencia visible/verificación de negocio. La prueba de un framework no cubre un host comprometido, un token robado o nuestra integración defectuosa.

### Qué sí tomamos de Progent

El artículo revisado distingue reducción de privilegios y expansión con aprobación. Adoptamos una política que el modelo puede proponer pero no autorizar. Los supuestos del threat model sobre usuario e internos del agente obligan a añadir protección de identidad, supply chain y runtime; no se asume que el paper cubra adversarios con control del servidor.

### Evaluación que falta antes de implementar una defensa propia

Definir tareas benignas y adversariales, actores, sensibilidad y resultados permitidos; separar train/dev/test y evitar ajustar a las mismas frases. Usar canarios sintéticos, idiomas, datos multimodales cuando sean relevantes y ataques adaptativos únicamente en laboratorio. Medir utilidad, bloqueo correcto, FP/FN, latencia/coste y decisiones revisadas. Publicar configuración/modelo/versión y casos excluidos.

No copiamos implementaciones o datasets sin revisar licencia. No convertimos contenido de investigación ofensiva en herramientas de ataque a terceros. El objetivo es demostrar que las fronteras aguantan incluso si el modelo falla.

## Noticias e informes de amenazas

- [GTIG: From Prompting to Autonomy](https://cloud.google.com/blog/topics/threat-intelligence/from-prompting-to-autonomy-the-evolution-of-adversarial-ai), consultado como informe2026: describe evolución hacia flujos de ataque asistidos por agentes y manipulación de artefactos. Implicación: tratar repos/configuración/resultados de scans como material hostil. Atribuciones y casos son afirmaciones del emisor, no observaciones de Agntia.
- [Anthropic: Countering misuse, septiembre2026](https://www.anthropic.com/threat-intelligence-report-september-2026): casos de abuso de herramientas IA. Implicación: monitorizar comportamiento y credenciales, no confiar en la marca del modelo. No generalizar su visibilidad a todos los proveedores.
- [Google: prompt injections on the web, abril2026](https://blog.google/security/prompt-injections-web/): observaciones sobre contenido web que interactúa con agentes. Implicación: origen de datos y separación de control, incluso al navegar documentación o leer issues.
- [CrowdStrike: agent insider threat,04-11-2026](https://crowdstrike.gcs-web.com/news-releases/news-release-details/crowdstrike-extends-agentic-soc-detect-and-stop-agent-insider): anuncio empresarial reciente de controles para agentes. Implicación: evaluar inventario/revocación/kill switch; no asumir disponibilidad, eficacia independiente ni precio de contratación.

## Investigación continua

Revisión mensual de papers/versiones y semanal de advisories/fuentes bajo presupuesto. El equipo abre propuestas de nuevos controles con fuente, hipótesis, coste y test reproducible; no instala repos de una noticia automáticamente. Feeds pueden contener información errónea o inyección: sanitizar y requerir aprobación para cualquier cambio de herramientas/políticas.

Criterios de admisión: fuente primaria, fecha y versión, artefactos reproducibles, amenazas cubiertas/no cubiertas, licencia, mantenimiento, coste y relevancia para nuestros clientes. Se prefieren pocos mecanismos verificables a una lista de papers sin efecto sobre diseño.
