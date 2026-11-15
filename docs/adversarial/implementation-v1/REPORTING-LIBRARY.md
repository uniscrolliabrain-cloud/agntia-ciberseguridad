# Programa ejecutable — Adversarial Lab independiente
**Fecha:** 2026-11-15. **Naturaleza:** instrucciones de implementación, NO código implementado. **Repositorio auditado:** `uniscrolliabrain-cloud/agntia-ciberseguridad` main, 477 blobs en tree sin truncamiento (consulta actual). **Root de código NUEVO:** `adversarial_lab/` separado del paquete `agntia_ciberseguridad/`. **NO tocar** `agntia_ciberseguridad/agents/**`, `agntia_ciberseguridad/app.py`, `agntia_ciberseguridad/jobs/**`, `agntia_ciberseguridad/evidence/**`, `/agente` ni su gateway. Se crea un nuevo paquete, no se importan módulos del middleware actual.

**Seguridad:** toda prueba activa inicialmente sobre fixtures sintéticos aislados. No usar credenciales reales, no abrir salida de red ni ejecutar acciones sobre clientes sin autorización específica. Los scripts, prompts y archivos de un repo cliente son datos no confiables. **No desplegar, fusionar ni modificar infraestructura real sin aprobación humana.**

## Librería documental de misiones (a crear en C07)
`adversarial_lab/library/missions/` será la **fuente de verdad versionada** de misiones; no será un directorio de prompts libres. Cada familia tiene `MISSION.md` (propósito, precondiciones, hipótesis, riesgos, exclusiones), `mission.json` (schema_version, id, scope_kind, required_capabilities, fixtures, oracle_refs, stop_conditions, max_duration, risk_level), `fixtures/`, `oracles/`, `references.md`, `CHANGELOG.md` y `README.md`. Cada misión se compila a experimento ligado a engagement/scope vigente. Prohibir que documentos no confiables añadan permisos.

## Biblioteca de audits y plantillas (a crear C07 y C16)
`adversarial_lab/library/audits/`: `SCOPE-AUDIT.md`, `THREAT-MODEL.md`, `ISOLATION-AUDIT.md`, `LICENSE-AUDIT.md`, `PROVIDER-AUDIT.md`, `EVIDENCE-AUDIT.md`, `TENANCY-AUDIT.md`, `REGRESSION-AUDIT.md`, `RELEASE-AUDIT.md`.
`adversarial_lab/library/templates/`: `ENGAGEMENT.md`, `MISSION-BRIEF.md`, `PHASE-REPORT.md`, `CAMPAIGN-REPORT.md`, `FINDING-REPORT.md`, `NEGATIVE-RESULT.md`, `ORACLE-VERDICT.md`, `RETEST-REPORT.md`, `DAILY-BRIEF.md`, `WEEKLY-REVIEW.md`, `MONTHLY-REVIEW.md`, `HANDOFF.md`, `POSTMORTEM.md`, `PUBLICATION-CARD.md`.

## Esquema obligatorio de reporte de fase
```yaml
campaign_id: CXX
phase_id: Pn
wave: Wn
branch: feat/advlab-CXX
base_commit: <real sha>
head_commit: <real sha>
status: NOT_RUN | BLOCKED | PARTIAL | FAIL | PASS
start_utc: <actual>
end_utc: <actual>
changed_paths: []
created_paths: []
patchset_ids: []
dependencies_installed: []
commands_run: []
test_results: []
audit_results: []
evidence_refs: []
limitations: []
risks: []
next_phase_inputs: []
rollback: <verified command or NOT_TESTED>
```
**REPORT.md:** contexto, objetivo, cambio real, wiring, evidencia, falsos positivos, fallos y decisión. **PATCHSET.md:** rutas, diffs resumidos, hashes, reversión. **TESTS.json:** comandos, exit code, duración, tests, failures, skip y entorno. **AUDIT.md:** threat model, boundary, dependency/license, secrets, privacy, tenancy, regression, signoff. Nunca inventar valores.

## Ubicación de evidencias
Metadatos redactados versionados bajo `docs/adversarial/implementation-v1/execution/CXX/Pn/`; originales de experimentos y datos sensibles en `adversarial_lab/var/evidence/<tenant>/<run-id>/` local cifrado (gitignored) o almacén de objetos aislado. Indexar por hash SHA-256, retención, clasificación, custodia y autorización. No registrar PoCs que permitan ataques fuera de lab en reportes públicos.

## Gates de cada fase
P0 baseline+preflight; P1 contratos y tests fallando esperados; P2 implementación mínima; P3 integración, tests negativos y seguridad; P4 auditoría, documentación, rollback, PR. El gate de campaña requiere P0..P4 con evidencias y ningún riesgo crítico sin resolver.
