# Agntia Cyber — Autodocumentación, evidencia y publicaciones técnicas
**Estado:** propuesta de arquitectura y plan de implementación; NO implica capacidades ya construidas. **Fecha:** 2026-11-15.
**Propósito:** convertir cada ejecución verificable del sistema en evidencia reproducible, documentación técnica mantenible y material candidato para publicaciones públicas rigurosas, sin comprometer la privacidad de clientes.

## 0. Contexto y límites
La fuente de verdad de implementación es el código y las pruebas de `main`, junto a `docs/release/status.json`, `docs/auditoria-runtime/AUDITORIA-FUNCIONAL-2026-11-14.md` y `docs/auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md`. La demo sintética NO es producción ni validación independiente. No duplicar capacidades existentes sin auditar. Este documento define **qué construir**, no afirma que ya funcione. No modificar `/agente` sin contrato y aprobación.

## 1. Principio
**El sistema no redacta éxitos: registra hechos, deriva métricas de hechos y redacta afirmaciones respaldadas por esos hechos.**
Cadena: ejecución autorizada → eventos tipados → artefactos verificables → evaluación independiente → expediente de evidencia → documentación técnica versionada → revisión humana → publicación. Una publicación nunca es un subproducto automático sin aprobación.

## 2. Objetivos medibles
- Trazar cada finding a activos, versión, ejecución, herramienta, alcance, evidencia y decisión.
- Comparar baseline y post-remediación; demostrar seguridad **y** regresión funcional.
- Medir tasa de hallazgos reproducibles, falsos positivos, remediaciones correctas, regresiones, cobertura, latencia, coste y tasa de rollback; reportar denominadores y exclusiones.
- Reproducir benchmarks sintéticos con seeds, fixtures, hashes, versiones, contenedores y scripts.
- Emitir reportes internos para cliente, ingeniero y auditor, y un borrador público **sanitizado**.
- Impedir que modelos, agentes o herramientas publiquen datos sensibles o declaren pruebas no ejecutadas.

## 3. Arquitectura propuesta
### 3.1 Capture plane
Instrumentar los SOPs y jobs existentes mediante eventos append-only (id, schemaVersion, timestamp UTC, tenantId, correlationId, causationId, actor, policyDecisionId, environment, runId, artifactRefs, status). Reutilizar bus, observabilidad, auditoría y contratos actuales; evitar un segundo event bus. Eventos propuestos: `cyber.run.started`, `cyber.scope.approved`, `cyber.finding.recorded`, `cyber.attack_simulation.completed`, `cyber.patch.proposed`, `cyber.test.completed`, `cyber.patch.approved`, `cyber.deployment.completed`, `cyber.rollback.completed`, `cyber.run.closed`, `cyber.evidence.sealed`. Registrar eventos de fallo y timeout, no solo éxitos.

### 3.2 Evidence store
Objetos inmutables por tenant con SHA-256, procedencia, firma cuando sea viable, clasificación, caducidad y política de retención. Mantener artefactos grandes fuera del bus; el evento solo almacena referencias. Tipos: resultados de scanners normalizados, logs redactados, SBOM, diffs, reportes de pruebas, capturas de configuración sin secretos, approvals, manifiestos de builds, indicadores de recuperación. Preservar evidencia forense con controles de cadena de custodia cuando aplique. Evitar datos personales y secretos en prompts.

### 3.3 Evaluation plane
Evaluadores independientes del agente que propuso o ejecutó el cambio. Gates: alcance/autorización, reproducibilidad de finding, seguridad, pruebas funcionales, regresión, calidad de evidencia, impacto operativo y rollback. Resultado tipado PASS/FAIL/INCONCLUSIVE/NOT_RUN con razones; **NOT_RUN nunca equivale a PASS**. Prohibir que un LLM otorgue por sí solo un veredicto definitivo.

### 3.4 Documentation plane
Generadores deterministas producen: `run-manifest.json`, `evidence-index.json`, `metrics.json`, `evaluation.json`, `technical-report.md`, `executive-report.md`, `limitations.md`. Un LLM puede resumir solo a partir de esos registros, con enlaces de evidencia y clasificación de cada afirmación: MEASURED / OBSERVED / PROVIDER_CLAIM / HYPOTHESIS / NOT_VERIFIED. Validar citas, unidades, fechas, muestras y cobertura antes de aceptar un borrador.

### 3.5 Publication plane
Dataset sintético/consentido → selección de resultados → anonimización y revisión de privacidad → revisión de seguridad ofensiva (no exponer secretos, accesos, exploits de clientes) → revisión técnica independiente → aprobación explícita del owner → release versionado. **Nunca autopublicar** ni publicar incidentes de clientes sin consentimiento y revisión contractual.

## 4. Contratos mínimos propuestos
```ts
type EvidenceClaim = {
  id: string;
  statement: string;
  class: 'MEASURED' | 'OBSERVED' | 'PROVIDER_CLAIM' | 'HYPOTHESIS' | 'NOT_VERIFIED';
  evidenceIds: string[];
  limitations: string[];
};
type Evaluation = {
  runId: string;
  evaluatorVersion: string;
  scopeId: string;
  status: 'PASS' | 'FAIL' | 'INCONCLUSIVE' | 'NOT_RUN';
  checks: Array<{ id: string; status: 'PASS' | 'FAIL' | 'INCONCLUSIVE' | 'NOT_RUN'; evidenceIds: string[] }>;
};
type PublicationCandidate = {
  benchmarkId: string;
  datasetVersion: string;
  commitSha: string;
  environmentDigest: string;
  claims: EvidenceClaim[];
  evaluationIds: string[];
  privacyReview: 'PENDING' | 'APPROVED' | 'REJECTED';
  securityReview: 'PENDING' | 'APPROVED' | 'REJECTED';
  ownerApproval: 'PENDING' | 'APPROVED' | 'REJECTED';
};
```
Extender contratos existentes solo tras revisión; nunca usar estos tipos como sustitución automática de los contratos reales.

## 5. Benchmark de referencia
Crear una suite de escenarios **autorizados y aislados**, inicialmente sintéticos: vulnerabilidad en dependencia; secreto ficticio; configuración cloud insegura simulada; prompt injection en documento de prueba; escalada de privilegios simulada; interrupción y recuperación de servicio; remediación que provoca regresión; falsa alarma; prueba no ejecutada; herramienta que devuelve resultado contradictorio. Conservar baseline vulnerable, estado deseado, exploit/PoC seguro solo en entorno cerrado, remediación esperada, tests funcionales y negativos. Separar conjuntos de desarrollo y evaluación para evitar sobreajuste. Incluir una baseline sin agentes y otra con asistencia humana.

## 6. Métricas y denominadores
- Detección confirmada: hallazgos verdaderos detectados / vulnerabilidades confirmadas del conjunto evaluado.
- Precisión de hallazgos: hallazgos confirmados / hallazgos reportados y revisados.
- Remediación correcta: correcciones que pasan gates de seguridad **y** funcionalidad / correcciones intentadas.
- Regresión: cambios con regresión confirmada / cambios probados.
- Tiempo de respuesta y de reparación: distribución p50/p95, no solo media.
- Cobertura: escenarios ejecutados / escenarios planificados; informar NOT_RUN.
- Recuperación: RTO/RPO medidos en simulacros frente a objetivos definidos.
- Coste: tokens, compute, APIs y horas humanas por escenario y por remediación.
- Seguridad de agentes: intentos bloqueados/permitidos, escapes confirmados y tasa de falsos bloqueos.
Siempre registrar tamaños muestrales, intervalos de confianza cuando proceda, hardware, modelos y versiones, exclusiones y fallos.

## 7. Privacidad, aislamiento y controles
Tenant isolation fail-closed; RBAC/ABAC; cifrado; credenciales efímeras; secretos en vault; retención limitada; redacción previa a modelos externos; DLP y revisión humana de muestras. Pentesting solo con autorización y alcance firmado. Sandboxes sin rutas a producción, con red de salida controlada y datos sintéticos. No usar un repositorio público como almacén de evidencias privadas. Separar métricas agregadas de datos de cliente; no afirmar anonimato cuando exista riesgo de reidentificación.

## 8. Estructura sugerida (no crear hasta auditar el árbol)
```
docs/engineering/AUTODOCUMENTACION-EVIDENCIAS-Y-PUBLICACIONES-TECNICAS.md
docs/publications/README.md
docs/publications/templates/technical-paper.md
docs/publications/templates/evaluation-card.md
docs/publications/templates/model-and-tool-card.md
docs/publications/templates/reproducibility-checklist.md
benchmarks/cyber-evidence/README.md
schemas/evidence/ (si no existe equivalente)
```
Evidencia de clientes: almacenamiento privado segregado, **nunca** `docs/publications`.

## 9. Implementación incremental y aceptación
**Fase A — auditoría y contratos:** mapear jobs, events, stores, tests, CI, SDK y reportes existentes; ADR de reutilización y amenazas. Aceptación: mapa de integración y cero duplicaciones no justificadas.
**Fase B — trazabilidad:** instrumentar 2 SOPs sintéticos end-to-end, eventos correlacionados, artefactos hasheados y replay. Aceptación: todos los resultados PASS/FAIL/NOT_RUN trazables al run.
**Fase C — evaluación:** evaluador independiente, benchmarks positivos/negativos y pruebas de regresión. Aceptación: una corrección que rompe negocio se marca FAIL; una prueba omitida NOT_RUN.
**Fase D — autoinformes:** generar reportes deterministas, claims con referencias, límites y métricas; comprobar que una afirmación sin evidencia es rechazada.
**Fase E — publicación controlada:** generar un paper técnico desde benchmark sintético, checklist reproducible y gate de tres aprobaciones. Aceptación: ningún dato privado sale, ninguna publicación se realiza automáticamente.
**Fase F — operación continua:** comparar versiones, detectar drift de métricas y producir changelog técnico por release; incorporar evaluaciones independientes periódicas.

Cada fase requiere tests unitarios, integración, aislamiento multi-tenant, casos de fallo, CI, reporte de campaña, evidencia de resultados y rollback. No avanzar a pilotos reales sin aprobación explícita y revisión de seguridad.

## 10. Primera publicación recomendada
**Título provisional:** «De hallazgo a corrección verificable: evaluación reproducible de un pipeline agéntico de ciberseguridad». Incluir hipótesis, arquitectura, threat model, baselines, dataset sintético, metodología, resultados con denominadores, casos fallidos, costes, limitaciones, scripts y hashes. No prometer autonomía total, seguridad absoluta ni equivalencia a auditoría independiente.

## 11. Criterio final de éxito
Cualquier afirmación pública sobre eficacia debe poder responder: **¿qué ejecución la respalda, sobre qué versión y escenario, qué pruebas se ejecutaron, qué quedó sin probar y cómo puede reproducirse?** Si falta alguna respuesta, la afirmación debe etiquetarse como no verificada y no convertirse en una promesa comercial.


## Programa de implementación auditado (2026-11-15)

[15 campañas AD-01..AD-15, rutas reales, patchsets, pruebas, auditorías, dependencias y handoff](../autodoc/PROGRAMA-15-CAMPANAS-ULTRAGRANULARES.md). **Plan no ejecutado**; se basa en revisión estática selectiva del código de main y exige reauditar cada SHA, ejecutar CI y no confundir demo sintética con producción. El programa CY-R01..R12 conserva prioridad en gates de seguridad.
