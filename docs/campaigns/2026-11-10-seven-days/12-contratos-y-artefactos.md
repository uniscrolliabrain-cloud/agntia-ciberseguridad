# 12 · Contratos y artefactos de referencia

Especificación futura: no hay API ni SDK runtime implementados por estos ejemplos. El diseño definitivo debe contrastarse con el repo madre y las decisiones del día1. Los nombres siguientes guían tests y ownership.

## Recursos

Tenant/Principal, Asset/Grant, Snapshot/Component/SBOM, ToolManifest/PolicyBundle, Job/Lease, Finding/Observation, EvidenceRef, Approval/Remediation, Incident, RegulatoryAssessment, BudgetReservation y AuditEvent. Todos los recursos del cliente tienen tenant, versión/revisión y política de acceso/retención. Las relaciones entre recursos se comprueban, no se aceptan por compartir un nombre.

## API propuesta

- GETassets, findings, evidence, jobs, reports, budgets y coverage, siempre scoped y paginados.
- POSTaudits/preview y audits, con grant/snapshot/profile, idempotency y coste máximo.
- POSTpolicies/evaluate para una decisión sin efectos; policy_changes/propose para el cambio revisable.
- POSTtools/admit y grants/approve solo para autoridad humana/servicio autorizado.
- POSTremediations/propose, approve y execute separados; merge/deploy sigue deshabilitado inicialmente.
- GETevents y POSTevents/ack con consumidor autenticado/deduplicación; no fan-out fingido.

No endpoints genéricos de shell, modelo/método, URLfetch o ejecución de templates escritos por un agente. La lectura de un recurso no habilita salida de sus datos a cualquier destino.

## Envelope conceptual

schema_version, contexto de identidad generado/verificado en servidor, authorization_id, asset_id, capability, correlation_id, causation_id, expected_revision, idempotency_key, dry_run, approval_id, policy_version y payload tipado. Un JSON con esos campos no acredita autorización: se valida contra sesión, firma/audiencia, scope, caducidad y recurso.

Resultado: status, resource_refs, warnings, coverage, evidence_refs, source_snapshot, tool/policy_versions, retryable y reconciliation_required. Error público seguro sin traceback/token/contenido del cliente. Un resultado200 puede ser blocked o incierto; la UI distingue transporte y negocio.

## Finding y cobertura

El finding conserva observaciones originales, regla/fuente, CVE/CWE cuando existan, ubicación minimizada, contexto, severidad/confianza y estado. La cobertura describe qué se intentó/analizó/omitió, por qué, fecha de DB y resultados stale/partial/failed. No calcular «porcentaje seguro» a partir de pocos scans.

## Telemetría

TraceIDs correlacionan sin dar acceso; baggage externo no determina tenant. Métricas técnicas usan labels acotados y vistas de cliente pasan por API scoped. Los logs guardan codes y referencias, no prompts/tokens. La auditoría requerida y evidencia de controles no se descartan por un sampling genérico de observabilidad.

## Artefacto por fase

Propuesta/ADR, código, schema/contract, fixtures, tests y resultados, logs minimizados, hashes/versiones y rollback. Cada archivo o endpoint sugerido en el día correspondiente puede consolidarse si se preserva el contrato y se documenta el mapeo. No crear archivos vacíos para aparentar cumplimiento de nombres.

## Compatibilidad y aceptación

Versionar API, schemas de herramientas y eventos. Tests de consumidor Python/TS y de actualización con historial real. Una incompatibilidad de parser obliga a estado parcial/bloqueado, no a descartar la evidencia. Compatibilidad Windows/Linux se anuncia solo para combinaciones probadas y el middleware no necesita exponer implementación de herramientas al usuario final.
