# 09 · Contrato propuesto hacia /agente

No se ha leído ni modificado el repo madre en esta tarea. Los nombres siguientes son una propuesta técnica que se contrastará con su identidad/event bus/approval service reales. No describen endpoints implementados.

## Consumo servidor

`/agente` conserva sesión, tenant, organización, rotas, memoria y política de producto. Un cliente servidor TypeScript/Hono llama al middleware privado con credencial scoped y contexto verificable. La misma capacidad sirve a UI humana y herramientas agénticas, diferenciando permisos. Tokens internos no viajan al navegador.

Proponer API versionada `/v1/tenants/{tid}` para recursos de negocio, sin aceptar model/method/shell libres. Principal/tenant/capability se generan o verifican en servidor y no se confían porque aparezcan en JSON. La autenticación debe fijar audiencia, emisor, expiración y revocación; mTLS/JWT/OIDC por decidir con el gateway existente. No crear una identidad paralela que salte el control del repo madre.

## Operaciones nominadas

| Capacidad | Efecto previsto | Restricción |
|---|---|---|
| assets.read/register | Inventario de activos | Solo propietario/ámbito autorizado |
| authorizations.propose/approve | Alcance de auditoría | Aprobación humana fuera del LLM |
| audits.preview/create | Validar perfil/encolar202 | Concesión vigente, coste reservado y snapshot |
| jobs.read/cancel | Estado/control de tareas | Cancelar no revierte efectos ya ejecutados |
| findings.read/triage.propose | Consulta y clasificación propuesta | No borrar/ocultar findings para mejorar métricas |
| reports.create/read | Informe reproducible | Snapshot y redacción scoped |
| policies.evaluate | Decisión determinista | Lectura de política vigente, no ampliación |
| policy_changes.propose/approve | Cambio de permisos | Expansiones requieren autoridad humana |
| remediations.propose/preview | Rama/diff/playbook | Sin escribir en producción |
| remediations.approve/execute | Efecto autorizado futuro | Identidad/objeto/hash/entorno vinculados |
| incidents.read/containment.propose | Caso/respuesta | Contención real es capacidad separada |
| budgets.read | Consumo/cobertura | No permite al agente elevar su cap |

## Envelope y entidades

Envelope propuesto: schema_version, server_verified_actor_ref, tenant_id, authorization_id, asset_id, capability, correlation_id, causation_id, idempotency_key, expected_revision, dry_run, approval_id y payload tipado. No es un token de seguridad por sí mismo. El servidor compara todos los IDs con sesión, concesión y política.

Finding: id, asset/commit/digest, herramienta/reglas/DB, rule_id/CVE/CWE, ubicación o endpoint minimizado, severidad/confianza, evidencia, first_seen/last_seen, cobertura, estado, dueño y revisión. No incluir secretos crudos en la clave de deduplicación o en el título. Deduplicar por regla/recurso/ubicación normalizada con historial, no por texto de resumen LLM.

Job: pending/running/partial/completed/failed/cancelled/blocked/reconciliation_required. Lease/fencing, presupuesto e idempotencia persistentes; el worker revalida principal y scope al comenzar y antes de efectos. La API202 no significa auditoría finalizada.

Respuesta/error común: code, message seguro, correlation_id, retryable, reconciliation_required, evidence_refs y warnings. Un reporte parcial conserva sus huecos. Providers caídos o schemas inválidos no son findings cero.

## Tools para agentes

Exponer security_asset_inventory, security_audit_preview, security_audit_status, security_findings, security_report, security_policy_explain, security_propose_fix y security_incident_summary como nombres orientativos. No herramientas de shell arbitraria, approve, elevar rol, cambiar presupuesto, subir secretos, comprar SaaS o atacar un dominio escrito en un prompt.

El rol Pedro coordina; especialistas proponen con capacidades limitadas. Laia resume hechos del event bus. El agent runtime programa tareas por eventos/cambios y por cadencia; este repo únicamente procesa jobs autorizados, no inventa horas de actividad. Los LLM generan explicaciones/propuestas y nunca el resultado de un test no ejecutado.

## Eventos propuestos

security.audit.completed, security.finding.created/changed, security.policy.denied, security.tool_manifest.changed, security.remediation.proposed/verified, security.incident.opened y security.budget.threshold. Todos con schemaVersion, event_id, tenant, correlation/causation, fecha, fuente, revisión y referencias minimizadas. Outbox/ACK/deduplicación; entrega at-least-once, no promesa de exactly-once distribuido.

El consumidor mantiene su estado durable antes de ACK. Los eventos sensibles pueden requerir vistas distintas para privacidad, técnico y owner. Ningún evento contiene prompt completo, bearer token o muestra privada. No publicar a Slack/email ni modificar el repo madre por crear esta propuesta.

## Gate de wiring

Antes de aplicar: inventariar interfaces reales del repo madre con autorización de lectura, acordar ownership/credenciales/eventos, implementar SDK/validación y un consumidor de prueba, verificar cross-tenant y revocación, documentar cambios concretos y obtener aprobación para escribir en `/agente`. Este documento permite trabajar en el middleware independientemente sin fingir que ya está conectado.
