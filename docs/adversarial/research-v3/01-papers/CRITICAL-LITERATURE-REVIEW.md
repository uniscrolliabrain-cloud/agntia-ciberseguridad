# Papers y sistemas científicos — lectura crítica
## 1. AIxCC / Atlantis
Fuente: https://github.com/Team-Atlanta/aixcc-afc-atlantis ; https://www.darpa.mil/news/2025/aixcc-results .
**Observación del código público:** repo MIT, implementación bajo `example-crs-webservice`, despliegue bajo `example-crs-architecture`, utilidades bajo `example-crs-appendix`. Árbol recursivo de API truncado (>34.000 blobs listados), por lo que no puede considerarse inventario completo. El repo público tiene 7 commits en la vista consultada, una advertencia sobre reproducibilidad y trazabilidad histórica.
**Qué estudiar:** DAG de tareas, asignación de presupuesto, fuzzers, crash triage, patch validation, build cache, concurrencia, scheduling, evaluación por resultado real. **No probado:** rendimiento reproducido, instalación local, seguridad multi-tenant o compatibilidad comercial directa.
**Transferencia:** separar discovery, proof, repair y oracle; orquestación determinista alrededor de componentes experimentales.

## 2. CyberGym
Fuente: https://arxiv.org/abs/2506.02548 ; https://www.cybergym.io/cybergym/ .
Benchmark de reproducción de vulnerabilidades, no garantía de pentesting general. Estudiar datasets, splits, oráculos y coste. Riesgo: contaminación de modelos y discrepancia entre reproducción y severidad real.

## 3. CyberGym-E2E — ICML 2026
Fuentes: https://proceedings.mlr.press/v306/shi26r.html ; https://www.cybergym.io/cybergym-e2e/ .
920 vulnerabilidades reales de 139 proyectos. S1 PoC provoca fallo en build vulnerable; S2 parche evita ese fallo; S3 tests funcionales pasan; S4 verifica vulnerabilidad ground-truth. S1–S3 es el éxito operativo de la evaluación, S4 diagnóstico adicional; **no sumar ni confundir métricas**. Leaderboard de octubre de 2026 contiene diferentes presupuestos y generaciones de tareas: comparar solo configuraciones equivalentes.
**Transferencia:** stages cumulativos, baseline patch-only, tests de regresión, diagnóstico de bug alternativo, ground truth protegido, reportar falsos éxitos y tests omitidos.
**Limitación:** un crash reproducible no demuestra automáticamente impacto en sistemas empresariales; datasets OSS no representan todas las aplicaciones de clientes.

## 4. AgentCyberRange
Fuente: https://arxiv.org/abs/2606.14295 ; https://agentcyberrange.io/ .
Paper de junio 2026 describe 110 vulnerabilidades en 15 aplicaciones y 8 ranges con 156 hosts; el sitio actual informa 203 vulnerabilidades. **Versiones diferentes, no contradicción a ocultar**. El sistema CAGE orquesta ejecución, recolección y verificación. Transferencia: topologías y secuencias de acciones realistas en red cerrada, no solo CTF de una máquina. No copiar técnicas de post-explotación fuera de lab.

## 5. PentestGPT — USENIX Security 2024
Fuente: https://www.usenix.org/conference/usenixsecurity24/presentation/deng .
Tres módulos que reducen pérdida de contexto. La mejora de 228,6% es relativa a GPT-3.5 y al benchmark del paper, no una tasa absoluta. Transferencia: estado persistente, plan de subtareas, observaciones, reevaluación y checkpoints. Falta demostrar que su arquitectura por sí sola escala a operaciones continuas multi-tenant.

## 6. Fuzzilli — investigación de motores JavaScript
Fuente primaria: https://github.com/googleprojectzero/fuzzilli/blob/main/Docs/HowFuzzilliWorks.md .
FuzzIL como IR para generación/mutación con corrección sintáctica por construcción; motor mutacional e híbrido; historial de mutaciones y REPRL para ejecución persistente. Transferencia **conceptual**: representación intermedia de experimentos, provenance de mutaciones, minimizar desperdicio por casos inválidos. No integrar Fuzzilli como herramienta general de web pentest.

## 7. OSS-Fuzz / ClusterFuzz
Fuente primaria: https://github.com/google/oss-fuzz/blob/master/docs/oss-fuzz/architecture.md .
Pipeline explícito maintainer→build→fuzz targets→ClusterFuzz→issue→fix→retest. Importante: disclosure y triage tienen política específica; nunca replicar publicación automática de hallazgos de clientes. Transferencia: builds reproducibles, corpus, crash dedupe, regression tests, verificación de fixes.

## 8. CAI y agentes ofensivos
Fuente primaria: https://github.com/aliasrobotics/CAI/blob/archive/docs/cai/architecture/overview.md .
Siete pilares: Agents, Tools, Handoffs, Patterns, Turns, Tracing, HITL. Repo archivado (rama archive); `LICENSE` y `LICENSE-MIT` coexistentes. Transferencia: taxonomía y comparación de patrones, no copiar código sin licencia por archivo y dependencias.

## Hipótesis para contrastar experimentalmente
H1: oráculos deterministas reducen false-confirmed findings frente a LLM-as-judge.
H2: diversificación de agentes mejora cobertura a presupuesto fijo, pero puede aumentar duplicados.
H3: un ledger de hipótesis reduce loops repetidos en sesiones de >24h.
H4: entornos de mayor fidelidad aumentan detección de fallos de integración, a coste mayor.
H5: selección por cambios de código produce mayor hallazgo verificado/€ que barridos uniformes.
**No declarar ninguna hipótesis como demostrada sin benchmark propio.**
