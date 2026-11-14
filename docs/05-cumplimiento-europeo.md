> Actualización: consultar el [catálogo y límites del checkpoint31–35](implementation/checkpoints/07-phases-31-35/SOURCES.md). Las fechas de investigación inicial siguientes no deben usarse como motor sin cotejar modificaciones posteriores, incluida la edición AI Act observada2026-07-27.

# 05 · Cumplimiento europeo como evaluación con evidencias

Fecha de consulta: 2026-11-10. «GEPR» en la petición se interpreta como GDPR/RGPD. El producto ayuda a inventariar, evaluar y documentar controles; no certifica por sí solo cumplimiento ni sustituye decisiones del responsable, DPO o asesor competente.

## Cómo decidir aplicabilidad

Por cliente y sistema, registrar rol, finalidad, sujetos afectados, sector, jurisdicción, datos, proveedores/subencargados y despliegue. Separar proveedor/deployer de IA, responsable/encargado RGPD, fabricante de producto digital y entidad eventualmente afectada por NIS2/DORA/ENS. No clasificar un sistema como alto riesgo solo porque use LLM o seguridad.

Cada requisito tiene fuente, versión/publicación, fecha de aplicación, condición, control, evidencia, responsable, vencimiento y revisión. Estados: applicable, not_applicable_with_reason, insufficient_information, evidence_missing, evidence_present_unreviewed y reviewed. La respuesta final de un LLM no puede pasar directamente a compliant.

## RGPD y privacidad

Texto oficial: [Reglamento2016/679 en BOE](https://www.boe.es/buscar/doc.php?id=DOUE-L-2016-80807). Mapear base/finalidad y minimización (arts5/6), contratos de encargado/subencargado (28), registro cuando corresponda (30), medidas de seguridad proporcionadas (32), brechas (33/34), EIPD cuando corresponda (35) y transferencias internacionales (44ss). Son categorías de evaluación; su aplicabilidad requiere hechos del caso.

Propuesta técnica: separar logs de seguridad de contenido de clientes, datos seudonimizados y referencias; acceso por necesidad; cifrado con claves por entorno/tenant cuando proceda; borrado/retención con legal hold; registro de consultas y exportaciones; contratos/regiones antes de usar IA externa. No se asume que el consentimiento sea la base universal para monitorizar trabajadores o clientes.

Según [AEPD](https://www.aepd.es/derechos-y-deberes/cumple-tus-deberes/medidas-de-cumplimiento/brechas-de-datos-personales-notificacion), el responsable evalúa el riesgo y notifica a la autoridad cuando corresponde sin dilación indebida y dentro del plazo aplicable de72h desde constancia; informar a afectados depende de otros requisitos. Un encargado alerta al responsable sin dilación indebida. No toda alerta de malware es una brecha personal notificable. El middleware propone expediente/cronología; no envía una notificación automática a la AEPD.

## AI Act

Base: [Reglamento2024/1689 en BOE](https://www.boe.es/buscar/doc.php?id=DOUE-L-2024-81079), más modificaciones y [explicación actual de Comisión](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai). Evaluar finalidad/riesgo y rol; inventario de modelos/proveedores, transparencia cuando corresponda, supervisión, alfabetización, documentación y evaluación de robustez/ciberseguridad. Los requisitos de sistemas de alto riesgo no se atribuyen indistintamente a todos los chatbots.

La página de Comisión consultada comunica aplicación general y excepciones, y sitúa determinadas obligaciones de alto riesgo en diciembre2027/agosto2028 tras cambios de2026. El acceso directo al DOUE de la modificación mediante EUR-Lex quedó bloqueado por anti-bot en esta sesión. Por tanto, las fechas se guardan como información oficial de guía que requiere cotejo del texto consolidado antes de automatizar decisiones legales; no usar una infografía antigua con fecha2026 como autoridad universal.

Evidencia técnica propuesta: versiones/model cards y contratos, inventario de agentes, scopes, registros de decisiones y revisión humana, evaluaciones por idioma/caso, cambios de herramientas, incidentes y limitaciones. Nada de ello prueba por sí solo conformidad jurídica o certificación. Si el sistema afecta contratación, crédito u otro ámbito sensible, escalar clasificación y consecuencias; no autorizar decisiones significativas únicamente automatizadas por llamarlas «ciberseguridad».

## CRA, NIS2, DORA y ENS

El [Cyber Resilience Act](https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act) y su [guía de reporting](https://digital-strategy.ec.europa.eu/en/policies/cra-reporting) se evalúan si hay productos/roles incluidos. La Comisión indica reporting desde11-09-2026 y obligaciones principales desde11-12-2027; distinguir vulnerabilidad explotada/incidente severo y rol del fabricante. El servicio debe poder conservar SBOM, soporte/versiones y expediente; no toda empresa SaaS o proyecto OSS tiene automáticamente la misma obligación.

Para [NIS2 España](https://digital-strategy.ec.europa.eu/es/policies/nis2-directive-spain), la página oficial consultada no basta para demostrar transposición completa y actual. Antes de asignar plazos o contactos nacionales se requiere revisión de BOE/autoridades y sector. DORA puede aplicar al sector financiero y ENS a determinados servicios del sector público español: evaluar por contrato/actividad, no marcar todo cliente como obligado ni reutilizar un plazo de RGPD para otro régimen.

## Matriz inicial de controles

| Control propuesto | Evidencia | Responsable |
|---|---|---|
| Inventario de activos/agentes/datos | Snapshot y relaciones versionadas | Owner técnico y privacidad |
| Privilegio mínimo | Políticas, concesiones y decisiones probadas | Seguridad/identidad |
| Cadena de suministro | SBOM, licencias, versiones y advisories | AppSec |
| Protección de datos | Minimización, DPA, regiones, accesos y retención | Responsable/DPO según rol |
| Supervisión y cambios | Propuesta, aprobación, diff y rollback | Humano autorizado |
| Gestión de vulnerabilidades | Finding, prioridad, excepción y retest | Responsable del activo |
| Incidentes | Cronología, alcance, constancia y evaluación de obligación | Equipo de incidente y responsable jurídico |
| Evaluación IA | Seguridad y utilidad, versiones y casos excluidos | Responsable IA |

## Gestión de cambios normativos

Una tarea periódica consulta fuentes oficiales, captura hash/fecha y abre una propuesta de cambio, nunca actualiza reglas legales a ciegas. Mantener versiones con effective_from/effective_to y revisión; fuentes contradictorias o inaccesibles dan insufficient_information. Feeds/noticias sirven como alerta, no reemplazan ley vigente.

Antes de operar con clientes: contrato, alcance de auditoría, DPA, subencargados, canal de incidentes, responsable, política de acceso y retención, evaluación de transferencias y revisión jurídica del servicio. El presupuesto técnico no incluye honorarios humanos, evaluación de conformidad o asesoramiento externo que puedan ser necesarios.
