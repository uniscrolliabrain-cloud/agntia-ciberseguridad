# Roadmap de integración AgntiaPro — agntia-ciberseguridad

> **Orden propuesto: 1/14.** Rama documental `docs/roadmap-integracion-agente-20261115`. Fecha 2026-11-15. **No sustituye las 42 campañas ni la documentación original.** Estado declarado en README, pendiente de reauditar código, ramas, CI y dependencias antes de ejecutar.

## Objetivo y estado de partida

**Dominio:** Auditoría, hardening, remediación y evidencia.

**Estado observado en README:** Código y demo sintética existentes; ramas de implementación integradas según README; CI indicada, sin equivalencia a producción. Este resumen no es una certificación; contrastar archivos, commits, tests y ramas antes de modificar nada.

**Objetivo de este hijo:** Definir y certificar primer bundle y dominio padre de ciberseguridad, controles de autorización para acciones de riesgo y evidencias de remediación.

**Resultado empresarial esperado:** Auditoría autorizada de una empresa interna, findings reproducibles, propuestas de reparación, aprobaciones y verificación.

## Roadmap común y landmarks (gates)

**L0 — Reconocimiento y preservación.** Inspeccionar `main`, ramas abiertas, PRs, código, tests, documentación y reportes de campañas existentes. No borrar ni reescribir código sin demostrar necesidad. Reconciliar ramas por PR/merge seguro, sin forzar merges ni perder cambios; obtener baseline verificable.

**L1 — Cierre del especialista.** Ejecutar las campañas del hijo que falten; completar contratos tipados, schemas de entradas/salidas, SDK/adaptador, seguridad, políticas, persistencia, fixtures, test unitario/integración, CI, telemetría y reportes. Si es DOCUMENTATION_ONLY, construir; si tiene código, preservar y completar.

**L2 — Bundle de capacidades versionado.** Publicar manifiesto de capabilities, SOPs, skills, pipelines, efectos, scopes, permisos, aprobaciones, idempotencia, compensaciones, eventos y compatibilidad semver. No dar autoridad a prompts o agentes.

**L3 — Desarrollo paralelo de `uniscrolliabrain-cloud/agente`.** Crear/adaptar dominio padre y proyecciones; instalar el bundle, mapear actor/tenant/owner, montar APIs/UI, conectar kernel, policy, approvals, worker, event bus, logs y receipts. La integración se desarrolla **en paralelo** al cierre del hijo, mediante ramas y contratos estables; no bloquear todo el trabajo del padre hasta el final de los 14.

**L4 — Producto humano operativo.** Realizar el proceso completo desde el software con el fundador actuando como usuario, **sin depender de LLM**. Confirmar que el dominio es útil, auditable y recuperable; no fingir tareas completadas.

**L5 — Certificación end-to-end.** Smoke, unit, integración, contratos, adversarial, aislamiento multi-tenant, replay de proyecciones, duplicados, retries, DLQ, cancelación, fallos externos, rollback, CI y observabilidad por correlationId. Registrar p50/p95 y evidencias, no solo resultados declarados.

**L6 — Acoplamiento cognitivo.** Exponer acciones autorizables al **slow LLM** mediante propuestas tipadas; kernel aprueba y runtime ejecuta. El slow no se conecta directamente a efectos ni al canal de voz.

**L7 — Experiencia conversacional.** Laia y agentes especializados usan **el mismo FastConversationV2/harness propio** para voz Anam y chat. Agentes son interfaz humana, no orquestadores. Tarjetas empresariales compactas precalculadas; `IntentBridge` asíncrono envía solicitudes; `ProgressProjector` traduce eventos reales a lenguaje humano. El fast no espera al slow ni al SOP para hablar. Animación SVG y cinco fases ilustrativas opcionales pueden educar sin simular confirmaciones de efectos. Barge-in corta audio, no tarea aceptada.

**L8 — Release y aprendizaje.** Canary interno, dos empresas dogfood, SLO, coste, RGPD, runbook, alertas, rollback, aprobación founder y reporte de campaña. Registrar desviaciones para los siguientes repos.

## Integración particular: agntia-ciberseguridad

**Vertical slice inicial:** Auditoría autorizada de una empresa interna, findings reproducibles, propuestas de reparación, aprobaciones y verificación.

**Contratos a diseñar:** entrada de solicitud del owner → `IntentEnvelope` (dato no confiable) → kernel/policy → capability tipada del hijo → effect receipt/evento → proyección UI → resumen verificable del presenter → respuesta conversacional fast.

**UX y agentes:** El perfil conversacional no debe memorizar internals de este repositorio; su tarjeta solo describe qué servicio ofrece la empresa, datos y límites de comunicación. Cualquier detalle operativo se resuelve en el bridge, kernel y runtime.

**Definition of Done:** acción humana completa, aprobación donde proceda, trazabilidad causal, no duplicación de efectos, tenant isolation, recuperación, UI útil, tests automatizados, evidencia de resultado y conversación coherente en chat/Anam.

## Secuencia global de los 14 hijos

01. agntia-ciberseguridad — Auditoría, hardening, remediación y evidencia
02. agntia-clientes — Atención al cliente, tickets, CRM de soporte y customer success
03. agntia-gestoria — Gestión documental, fiscal y obligaciones empresariales
04. agntia-comunicacion — Comunicación corporativa, prensa, crisis y mensajería
05. agntia-ventas — CRM comercial, oportunidades, propuestas y seguimiento
06. agntia-finanzas — Tesorería, FP&A, conciliación y reporting
07. agntia-redes — Publicación, inbox y analítica social
08. agntia-marketing — Campañas, investigación y atribución
09. agntia-video — Edición, podcast, clips y exportación audiovisual
10. agntia-branding — Identidad visual y activos de marca
11. agntia-dise-o — Diseño UI/UX, web y activos digitales
12. agntia-legal — Contratos, expedientes y cumplimiento
13. agntia-seguros — Pólizas, riesgos, renovaciones y siniestros
14. agntia-formacion — Formación, itinerarios y evaluación

El orden es **propuesta operativa por dependencias y retorno de aprendizaje**, no afirmación de que los repos de menor número estén terminados. Se puede avanzar en hijos diferentes en paralelo; **la certificación e integración en el padre se cierran una a una**. Si el reconocimiento L0 revela dependencias bloqueantes, actualizar este orden de forma explícita en todos los roadmaps.

## Handoff de ejecución para el agente desarrollador

1. Leer este roadmap y la documentación histórica, código y reportes del repo. No asumir ausencia de implementación.
2. Auditar ramas y `main`, proponer reconciliación segura y no destruir trabajo existente.
3. Entregar informe `BASELINE.md` con paths, líneas, SHA, pruebas corridas, pendientes y riesgos.
4. Ejecutar L1–L2 por campañas pequeñas, dejando reporte por campaña.
5. Preparar contrato de integración L3 para el equipo de `agente`; sincronizar cambios de contrato y compatibilidad.
6. Certificar L4–L5 con el founder y solo después habilitar L6–L8.

**Estado de este documento:** planificación inicial. No se han ejecutado tests, merges, instalaciones ni despliegues en este cambio.
