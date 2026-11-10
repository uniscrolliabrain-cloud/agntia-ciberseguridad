# 08 · Compañías de referencia y capacidades a construir

Fecha: 2026-11-10. Muestra representativa, no ranking independiente de «las mejores del mundo». Las páginas comerciales y anuncios describen capacidades del proveedor; no son una evaluación propia de eficacia, disponibilidad contractual o cobertura de cada plan. Se estudian patrones sin copiar tecnología propietaria ni prometer paridad dentro de30€.

| Referencia primaria | Qué declara/ofrece | Patrón que proponemos | Diferencia material |
|---|---|---|---|
| [Wiz Agents & Workflows](https://www.wiz.io/blog/introducing-wiz-agents),marzo2026 | Contexto cloud/código y workflows con agentes | Relaciones activo-identidad-dato-finding y remediación revisable | No contamos con su sensor graph/telemetría/equipo; empezar con relaciones básicas |
| [PaloAlto Prisma AIRS Agent Security](https://www.paloaltonetworks.com/prisma/agent-security) | Evaluación y control de identidad/acciones de agentes | Inventario, policy gateway y chequeo de tools/destinos | No implica adquirir suite o disponer de su cobertura endpoint/red |
| [CrowdStrike Charlotte AI](https://www.crowdstrike.com/en-us/platform/charlotte-ai/) | Investigación/triage dentro de Falcon | Casos, evidencias, explicación y decisiones gobernadas | No sustituimos sensores/MDR ni inteligencia global del fabricante |
| [SentinelOne Purple AI](https://www.sentinelone.com/platform/purple/) y [ASOC,octubre2026](https://www.sentinelone.com/press/sentinelone-brings-security-superintelligence-to-the-soc-with-singularity-asoc/) | Contexto/normalización y procesos de investigación | Modelo común de eventos y agente investigador limitado | Anuncio no demuestra disponibilidad de todas las funciones o precio pequeño |
| [Microsoft Security Copilot agents](https://learn.microsoft.com/en-us/copilot/security/agents-overview) | Agentes y flujos dentro de herramientas de seguridad | Roles, autorización y conectores sobre datos existentes | Licencias/consumo/tenant Microsoft no se incluyen por defecto |
| [Google/Mandiant GTIG](https://cloud.google.com/blog/topics/threat-intelligence/from-prompting-to-autonomy-the-evolution-of-adversarial-ai) | Inteligencia e investigación de campañas | Correlación de evidencia y revisión continua de amenazas | No tenemos su visibilidad global ni atribución independiente |
| [Cloudflare WAF](https://developers.cloudflare.com/waf/) | Controles de tráfico web/API según plan | Borde gestionado opcional o proxy WAF propio con reglas | DDoS de red y AI Security premium no nacen del middleware local |
| [Snyk](https://snyk.io/plans/) | SCA/SAST/IaC/container; productos Evo en nivel empresarial | DevSecOps integrado y priorización | Team económico no incluye automáticamente seguridad agéntica empresarial |
| [Semgrep](https://semgrep.dev/pricing/) | Detección basada en reglas y funciones de plataforma/IA | Regla determinista más revisión contextual | CE, reglas Pro, SaaS y créditos son productos/términos diferentes |

## Recorrido que pretendemos igualar en utilidad

El cliente quiere saber qué tiene expuesto, qué importa, qué puede hacer y qué quedó arreglado. Nuestra primera meta no es replicar los portafolios anteriores: es dar una respuesta útil para una aplicación pequeña con fuente, cobertura y coste conocido.

Ejemplo objetivo: entra un commit, se identifica dependencia vulnerable, se comprueba si aparece en la imagen desplegada y si el servicio está expuesto, se abre un finding con evidencia, un agente propone un parche y se genera una rama revisable. Tras aprobación, CI y retest verifican la corrección. Si la información de exposición falta, el reporte lo declara; no inventa un exploit path.

Segundo recorrido: una tool intenta sacar un documento a un destino nuevo. El gateway compara permiso, sensibilidad, procedencia y destino. Deniega o solicita revisión conforme a política, preserva evidencia minimizada y permite al humano ver qué cambió. Esto debe funcionar aunque falle el clasificador de prompts o no haya presupuesto LLM.

## Matriz de cobertura honesta

- AppSec/ASPM: primeros adaptadores OSS y correlación básica, pendientes de implementar.
- AI-SPM: inventario de modelos/agentes/tools/skills y policies, pendiente de implementar.
- Runtime IA: control de acciones/data egress, no detector universal de intención maliciosa.
- SIEM/XDR: conectores/ingestión opcional, no un EDR propio ni cobertura completa de endpoints.
- SOAR: propuestas y playbooks aprobados, no respuesta irreversible autónoma.
- GRC: evidencia y aplicabilidad revisable, no certificación legal automática.
- Antifraude: indicadores y verificación humana de contexto, no prevención absoluta de estafas.

## Cómo escoger servicios comerciales

Preferir compras puntuales que cubran un hueco concreto: borde/WAF, repos privados o conector que el cliente ya paga. Comparar costo total, cobertura, límites, exportación, region/DPA, SLA, derecho MSSP y salida del proveedor. Los productos por presupuesto personalizado no se colocan dentro de un tier sin oferta válida.

Un cliente con Falcon, Wiz o Microsoft puede aportar sus propios permisos/licencia para un conector BYOL revisado. No se puede compartir arbitrariamente la cuenta de otro cliente ni vender acceso a servicios que el contrato no permite. Si un catálogo ofrece «agentic SOC», se verifica qué componente es GA, preview o una promesa comercial antes de anunciarlo como capacidad nuestra.
