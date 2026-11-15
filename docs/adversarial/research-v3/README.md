# Investigación técnica V3 — índice y estado
**2026-11-15. Investigación previa al diseño de campañas de código.** Este dossier sustituye la V1 y amplía V2. NO es implementación. La lectura de repos externos se ha realizado mediante metadatos, árboles recursivos y documentos de arquitectura seleccionados, no auditoría exhaustiva ni ejecución de sus tests.

## Orden de lectura
1. `00-governance/SCOPE-AND-NON-INTERFERENCE.md` — fronteras inviolables.
2. `01-papers/CRITICAL-LITERATURE-REVIEW.md` — papers, métodos y límites.
3. `02-repositories/FORENSIC-OSS-MATRIX.md` — SHAs, arquitectura y decisiones de transferencia.
4. `03-industry/FRONTIER-LABS-COMPETITIVE-RESEARCH.md` — empresas y metodologías públicas.
5. `04-techniques/RESEARCH-TAXONOMY.md` — taxonomía de técnicas y oráculos.
6. `05-laboratory/DIGITAL-TWINS-ISOLATION.md` — replicación y aislamiento.
7. `06-experiment-engine/EXPERIMENTAL-SCIENCE.md` — motor científico y scheduler.
8. `07-provider-independence/CODING-AGENT-ADAPTERS.md` — Codex, Antigravity, Cline, Freebuff.
9. `08-evaluation/BENCHMARKS-AND-METRICS.md` — evaluación, denominadores y comparabilidad.
10. `09-architecture/BUILD-WRAP-STUDY-REJECT.md` — decisiones de integración y alternativas.
11. `10-roadmap/RESEARCH-GATES-AND-HANDOFF.md` — trabajo pendiente y criterios para autorizar campañas de código.
12. `11-sources/PRIMARY-SOURCES.md` — fuentes exactas.

## Decisión central
No se modifica `agntia_ciberseguridad/agents/**` ni el repo `/agente`. El laboratorio es un producto autónomo. Tampoco se usa el gateway de agentes existente como backend de ejecución. Se evalúa repositorio hermano como opción preferida, pero la decisión final requiere ADR.

## Grados de evidencia
**A:** paper oficial revisado / código o arquitectura primaria inspeccionada. **B:** README oficial / documentación pública del autor. **C:** afirmación de marketing no reproducida. **D:** hipótesis propia de diseño. En cada documento distinguir observación y propuesta.

## Hallazgos de mayor impacto
- AIxCC y CyberGym-E2E evidencian que un sistema competitivo requiere **oráculos, builds, experimentos y retests**, no solo razonamiento LLM.
- PentestGPT enseña la necesidad de memoria operativa persistente; CAI muestra patrones de coordinación, pero está archivado y con licencias mixtas.
- OSS-Fuzz separa build/fuzzer/triage/verificación; Schemathesis separa schema/phase/transport/event/report.
- PyRIT y garak resuelven seguridad de IA, no pentesting universal.
- El alcance real de la réplica se debe medir; datos sintéticos no garantizan equivalencia funcional ni anonimato.
- Las capacidades de Codex/Antigravity/Freebuff deben probarse con adaptadores reales, no presumirse.

## Alcance de esta entrega
Documentación de investigación, no 15 campañas de implementación. No se han instalado herramientas, desplegado sandboxes ni ejecutado tests de repos externos. Las matrices de licencias no sustituyen revisión legal. Toda cifra de benchmark depende de versión, configuración y fecha.
