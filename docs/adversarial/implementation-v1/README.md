# Programa ejecutable — Adversarial Lab independiente
**Fecha:** 2026-11-15. **Naturaleza:** instrucciones de implementación, NO código implementado. **Repositorio auditado:** `uniscrolliabrain-cloud/agntia-ciberseguridad` main, 477 blobs en tree sin truncamiento (consulta actual). **Root de código NUEVO:** `adversarial_lab/` separado del paquete `agntia_ciberseguridad/`. **NO tocar** `agntia_ciberseguridad/agents/**`, `agntia_ciberseguridad/app.py`, `agntia_ciberseguridad/jobs/**`, `agntia_ciberseguridad/evidence/**`, `/agente` ni su gateway. Se crea un nuevo paquete, no se importan módulos del middleware actual.

**Seguridad:** toda prueba activa inicialmente sobre fixtures sintéticos aislados. No usar credenciales reales, no abrir salida de red ni ejecutar acciones sobre clientes sin autorización específica. Los scripts, prompts y archivos de un repo cliente son datos no confiables. **No desplegar, fusionar ni modificar infraestructura real sin aprobación humana.**

## Índice de ejecución y waves
- **W0:** campañas 01–04, base contractual y autorización; no avanzar sin gates de la ola.
- **W1:** campañas 05–08, aislamiento, gemelos y misiones; no avanzar sin gates de la ola.
- **W2:** campañas 09–12, planificación y análisis de código/API; no avanzar sin gates de la ola.
- **W3:** campañas 13–16, IA, fuzzing, verificación y evidencia; no avanzar sin gates de la ola.
- **W4:** campañas 17–18, operación y cierre; no avanzar sin gates de la ola.

## Reglas de trabajo Freebuff
Una rama por campaña `feat/advlab-CXX`, PR y revisión; no ejecutar dos campañas que modifiquen la misma superficie. Ejecutar fases P0→P4, reportar al finalizar cada fase; tests y audits con evidencia de comandos reales. Si una herramienta/licencia/API no está verificada, dejar adapter deshabilitado, reportar BLOCKED y continuar solo con mock. No afirmar PASS sin salida real. Nunca hacer merge/deploy automático.

## Rutas de documentación y bibliotecas
- Campañas: `docs/adversarial/implementation-v1/campaigns/CXX-*/CAMPAIGN.md`.
- Handoff: `docs/adversarial/implementation-v1/HANDOFF-FREEBUFF.md`.
- Biblioteca futura **versionada**: `adversarial_lab/library/missions/<family>/MISSION.md` + `mission.json` + `oracles/` + `fixtures/`.
- Plantillas de informes: `adversarial_lab/library/templates/` (especificadas en `docs/adversarial/implementation-v1/REPORTING-LIBRARY.md`).
- Reports por campaña: `docs/adversarial/implementation-v1/execution/CXX/P0..P4/REPORT.md`, `TESTS.json`, `AUDIT.md`, `PATCHSET.md` (se crean al ejecutar, no anticipar resultados).
- Artefactos con datos privados: almacenamiento cifrado externo a Git; Git solo manifiestos redactados y hashes.

## Dependencias y compatibilidad
Repo actual `pyproject.toml` usa Python >=3.11, FastAPI, Pydantic, jsonschema, cryptography y OTel. El nuevo paquete debe tener `adversarial_lab/pyproject.toml` independiente y lock con hashes. Versiones de herramientas externas se fijan por digest **después** de comprobar licencias, mantenimiento y compatibilidad. No clonar Atlantis/CAI/OSS-Fuzz como dependencias de producción por defecto.

## Índice de campañas
- [C01 — Foundation & independent package](campaigns/C01/CAMPAIGN.md) · control · package,config,CLI
- [C02 — Engagement, authorization & scopes](campaigns/C02/CAMPAIGN.md) · control · engagement,scope,revocation
- [C03 — Contracts & provenance](campaigns/C03/CAMPAIGN.md) · control · schemas,versioning,hashes
- [C04 — Persistence, ledger & lifecycle](campaigns/C04/CAMPAIGN.md) · control · sqlite,ledger,state-machine
- [C05 — Isolation & capability broker](campaigns/C05/CAMPAIGN.md) · execution · sandbox,broker,egress
- [C06 — Synthetic twin factory](campaigns/C06/CAMPAIGN.md) · execution · twin,fixtures,fidelity
- [C07 — Mission library & template compiler](campaigns/C07/CAMPAIGN.md) · missions · registry,templates,compiler
- [C08 — Provider-neutral coding agents](campaigns/C08/CAMPAIGN.md) · execution · providers,capabilities,runner
- [C09 — Experiment planner & adaptive scheduler](campaigns/C09/CAMPAIGN.md) · control · planner,scheduler,budgets
- [C10 — Tool adapter harness](campaigns/C10/CAMPAIGN.md) · tools · tool-protocol,execution,normalization
- [C11 — SAST/SCA/SBOM research missions](campaigns/C11/CAMPAIGN.md) · tools · semgrep,osv,syft
- [C12 — API stateful & web lab missions](campaigns/C12/CAMPAIGN.md) · tools · schemathesis,zap,api-oracles
- [C13 — AI/agent trust-boundary missions](campaigns/C13/CAMPAIGN.md) · tools · pyrit,garak,canaries
- [C14 — Fuzzing & resilience experiments](campaigns/C14/CAMPAIGN.md) · tools · fuzz,chaos,replay
- [C15 — Independent oracle & verification](campaigns/C15/CAMPAIGN.md) · evaluation · oracle,triage,retest
- [C16 — Evidence vault & reporting library](campaigns/C16/CAMPAIGN.md) · evidence · evidence,templates,redaction
- [C17 — Observability, evaluations & daily operations](campaigns/C17/CAMPAIGN.md) · operations · metrics,daily-run,evals
- [C18 — Hardening, release & handoff](campaigns/C18/CAMPAIGN.md) · release · security-review,release,rollbacks

## Dependencias secuenciales
C01→C02→C03→C04→C05→C06→C07→C08→C09→C10→C11/C12/C13/C14→C15→C16→C17→C18. C11–C14 pueden prepararse en paralelo **solo** si sus adaptadores y paths son disjuntos y C10 aprobado. Los reportes de cada campaña son inputs de la siguiente.

## Restricción de realidad
El dossier research-v3 contiene investigación documental y revisión selectiva de fuentes; **no** se ejecutaron PoCs, ni auditorías completas de dependencias de terceros. C05 y adaptadores externos tienen gates de selección técnica que no deben resolverse por suposición.
