# RESEARCH MASTER V2 — Autonomous Adversarial Research Laboratory
**Fecha:** 2026-11-15 · **Estado:** investigación y diseño de referencia, NO implementación · **Repositorio:** uniscrolliabrain-cloud/agntia-ciberseguridad
**Invariante absoluto:** esta capacidad es **independiente** de los agentes actuales. NO modificar `agntia_ciberseguridad/agents/**`, sus manifests, gateway MCP, policies, tools, grants, rutas o su semántica. Tampoco modificar `/agente`. No reinterpretar los agentes existentes como parte del laboratorio. Codex, Antigravity, Cline, Freebuff, Claude Code, OpenHands u otros son **clientes externos** de un protocolo agnóstico, nunca roles internos del sistema actual.

## 0. Corrección del enfoque anterior
El documento `docs/adversarial/CONCEPT-MASTER-ADVERSARIAL-LAB-Y-15-CAMPANAS.md` se conserva como **borrador V1 superado**, no como plan autorizado. Mezclaba el gateway de agentes existente con un sistema nuevo, adelantaba campañas sin investigación profunda y asumía integraciones sin comprobar compatibilidad. Este V2 sustituye su enfoque conceptual; no iniciar ADV-01..15 de V1. Antes de planificar código se exige ADR de arquitectura, revisión de licencias y PoC de aislamiento.

## 1. Pregunta de investigación
¿Cómo construir un sistema persistente de investigación de seguridad que, cada día, elija hipótesis de fallo, ensaye pruebas reproducibles en copias sintéticas de tecnología de clientes, aprenda de evidencia real, y produzca informes, casos de regresión y propuestas de corrección, manteniendo la posibilidad de pruebas muy limitadas sobre sistemas reales **solo con autorización específica**?

No es un escáner, ni un chatbot pentester, ni un wrapper de Codex, ni una modificación del sistema de agentes existente. Es una **infraestructura experimental** con planificación, reproducción, medición, control de riesgos y una cartera de hipótesis.

## 2. Estado del arte: papers, competiciones y laboratorios
### 2.1 DARPA AI Cyber Challenge / AIxCC — referencia de sistema completo
- DARPA, resultados 2025: https://www.darpa.mil/news/2025/aixcc-results
- Team Atlanta, Atlantis CRS (MIT): https://github.com/Team-Atlanta/aixcc-afc-atlantis
- Preguntas a investigar en el código: estructura del CRS, priorización, validación, fuzzing, generación de parches, observabilidad, reparto de compute, reproducción, manejo de estados, fallos y seguridad del harness.
- Transferencia: tratar el hallazgo como un experimento verificable y el parche como una hipótesis sometida a pruebas. **No** asumir que el repo ganador puede desplegarse sin adaptación.

### 2.2 CyberGym — vulnerabilidades reales reproducibles
- Paper: https://arxiv.org/abs/2506.02548
- Sitio y leaderboard: https://www.cybergym.io/cybergym/
- 1.507 vulnerabilidades históricas en 188 proyectos. El artículo original encontró un 11,9% de reproducción con su mejor combinación evaluada entonces; los resultados de 2026 son muy diferentes y dependen del harness y la fecha. No comparar números de diferentes evaluaciones como si fueran equivalentes.
- Transferencia: construir tasks con estado vulnerable, ground truth, entorno reproducible, oráculo de éxito y métricas con denominador. Reutilizar datasets bajo sus términos, sin copiar automáticamente contenido explotable a repos públicos.

### 2.3 CyberGym-E2E — cierre del ciclo
- Paper ICML 2026: https://proceedings.mlr.press/v306/shi26r.html
- Proyecto: https://www.cybergym.io/cybergym-e2e/
- 920 vulnerabilidades de 139 proyectos; ciclo discovery→reproducción→patch sin regresión.
- Transferencia: separar descubrimiento, demostración y reparación, con evaluador independiente y comparaciones frente a baselines.

### 2.4 AgentCyberRange — realismo multi-host
- Paper: https://arxiv.org/abs/2606.14295
- 8 cyber ranges empresariales y 156 hosts internos, según el abstract; la complejidad de multi-host cambia el problema respecto a un repo o un CTF individual.
- Transferencia: modelar topología, identidades, servicios, dependencias, estados, telemetría y verificación de objetivos en un **entorno cerrado**. Reproducir escenarios de red sin permitir rutas a infraestructuras externas.

### 2.5 PentestGPT — planificación y memoria operativa
- USENIX Security 2024: https://pentestgpt.com/paper.html
- Hallazgo: los LLM resuelven subtareas, pero pierden contexto global en procesos prolongados.
- Transferencia: árbol de hipótesis, ledger de observaciones, objetivos pendientes, contradicciones, deduplicación y handoff entre sesiones. No usar la memoria del modelo como fuente de verdad.

### 2.6 CAI — framework ofensivo/defensivo y cautela de licencias
- https://github.com/aliasrobotics/CAI
- **Archivado**; documentación declara componentes MIT y adiciones propietarias restringidas a investigación. No copiar ni integrar código hasta revisión jurídica de archivos específicos. Investigar arquitectura, herramientas, experimentos, limitaciones y sucesor, no convertirlo en dependencia de producción.

### 2.7 Investigación adicional obligatoria antes del roadmap
- Fuzzing guiado por cobertura: OSS-Fuzz/ClusterFuzzLite, libFuzzer, AFL++, Jazzer; oráculos, crash triage, corpus minimization, differential fuzzing.
- Análisis estático y semántico: CodeQL, Semgrep, análisis interprocedimental, taint tracking, análisis de autorización y flujos de datos.
- Seguridad de IA: Microsoft PyRIT, NVIDIA garak, AgentDojo, OWASP LLM Top 10, MITRE ATLAS; ataques de instrucciones indirectas, abuso de herramientas y fronteras de confianza.
- Evaluación de seguridad realista: benchmarks con contaminación de datos, sesgos de selección, false positives, tasa de confirmación, regresiones y coste por hallazgo.
- Seguridad de entornos: microVMs (Firecracker), gVisor, Kata Containers, namespaces/seccomp, egress control, snapshots, claves efímeras, política de imágenes y teardown. **Docker sin red no equivale automáticamente a aislamiento fuerte**.

## 3. Empresas y laboratorios de referencia — hipótesis a contrastar
| Organización | Área relevante | Qué estudiar | Qué NO asumir |
|---|---|---|---|
| DARPA AIxCC / Team Atlanta | CRS autónomo | orquestación de discovery, PoC, patch | producto multi-tenant listo |
| Trail of Bits | investigación y análisis de programas | metodología, CodeQL, análisis estático, revisión | que sus herramientas cubren todas las clases |
| Theori | investigación ofensiva y AIxCC | verificación de vulnerabilidades y benchmarks | código disponible en todos los módulos |
| XBOW | pentesting autónomo | selección de objetivos, reproducción, validación, humanos | arquitectura privada demostrada |
| Google Project Zero / Big Sleep | investigación de vulnerabilidades asistida por IA | triage, análisis profundo y divulgación responsable | acceso a técnicas propietarias |
| Microsoft AI Red Team | red teaming de modelos | PyRIT, scoring, trazas, multi-turn | equivalencia con seguridad de infraestructura |
| NVIDIA | evaluaciones LLM | garak, probes, detección y cobertura | protección completa de agentes |
| Google OSS-Fuzz | fuzzing continuo | instrumentación, corpus, minimización, regresión | aplicabilidad directa a todos los stacks |
| UC Berkeley CyberGym | evaluación científica | oráculos, benchmarks, validez experimental | leaderboard comparable sin misma configuración |

**Evidencia pública y no marketing:** los detalles internos de XBOW/Big Sleep no están confirmados aquí; cualquier afirmación arquitectónica requiere publicación o repositorio primario. Fuentes de referencia para ampliar: https://www.darpa.mil/news/2025/aixcc-results ; https://github.com/Team-Atlanta/aixcc-afc-atlantis ; https://github.com/google/oss-fuzz ; https://github.com/microsoft/PyRIT .

## 4. Repositorios públicos candidatos — matriz de transferencia
| Repo | Función | Licencia/estado observado | Estrategia |
|---|---|---|---|
| https://github.com/Team-Atlanta/aixcc-afc-atlantis | CRS ganador AIxCC | MIT declarado | leer arquitectura y prototipos, no importar indiscriminadamente |
| https://github.com/aliasrobotics/CAI | investigación agentic cyber | archivado; mixto MIT + research-only | solo estudio hasta revisión por archivo |
| https://github.com/google/oss-fuzz | fuzzing continuo | verificar licencia de cada componente | adaptador de jobs aislados |
| https://github.com/microsoft/PyRIT | red team de IA | MIT declarado | adaptador de evaluación IA |
| https://github.com/NVIDIA/garak | probes para LLM | Apache-2.0 declarado | adaptador y normalizador de hallazgos |
| https://github.com/ossf/scorecard | postura de supply chain | revisar release y dependencias | observación de repos y baselines |
| https://github.com/semgrep/semgrep | SAST y reglas | verificar edición/licencia | reutilizar integración existente |
| https://github.com/github/codeql | análisis de código | verificar restricciones de uso | estudiar queries y empaquetado |
| https://github.com/returntocorp/semgrep-rules | reglas de seguridad | revisar licencia de reglas | corpus de cobertura |
| https://github.com/OWASP/Amass | inventario de superficie | verificar licencia | SOLO descubrimiento autorizado |
| https://github.com/zaproxy/zaproxy | DAST | Apache-2.0 declarado, verificar | tests web/API en lab |
| https://github.com/schemathesis/schemathesis | property-based API testing | verificar licencia | fuzzing de contrato en lab |
| https://github.com/aquasecurity/trivy | SCA/container/IaC | verificar release/licencia | reutilizar adaptador actual |
| https://github.com/anchore/syft | SBOM | verificar licencia | provenance |
| https://github.com/anchore/grype | vulnerability matching | verificar licencia | contraste de findings |
| https://github.com/prowler-cloud/prowler | cloud security posture | verificar licencia | solo lectura autorizada |
| https://github.com/Netflix/security_monkey | historial de cambios cloud | **archivado** | referencia histórica, NO dependencia |
| https://github.com/google/oss-fuzz/tree/master/infra/cifuzz | CI fuzzing | verificar | patrón de ejecución recurrente |

**No se ha hecho todavía auditoría profunda de dependencias, licencias y commits de todos los repos**. Las etiquetas 'verificar' son tareas de investigación, no aprobaciones de instalación.

## 5. Taxonomía de investigación adversarial avanzada
En lugar de una lista de comandos ofensivos, construir un **árbol de experimentos** con hipótesis, precondiciones, límites, oráculos y evidencias:
1. **Source-to-sink y flujos de confianza:** taint, serialización, parsing, autenticación y autorización.
2. **Lógica de negocio:** inconsistencias de roles, estados, pagos, inventario, concurrencia e idempotencia.
3. **Supply chain:** dependencias, CI/CD, firmas, artefactos, actualizaciones y procedencia.
4. **APIs y protocolos:** contratos, máquinas de estados, propiedades, autenticación, límites y errores.
5. **Cloud/IAM:** privilegios, exposición, límites de cuentas, secretos y configuración.
6. **Agentes IA y LLM:** prompt injection, tool misuse, memory/RAG poisoning, abuso de delegaciones y confianza MCP.
7. **Resiliencia:** fallos de red, disco, colas, DB, clock skew, recuperación, RTO/RPO y degradación.
8. **Composición multi-servicio:** ataques en fronteras entre servicios, autorización transversal, eventos y datos.
9. **Races y temporalidad:** TOCTOU, leases, retries, replay, sesiones caducadas, deduplicación.
10. **Regresiones de seguridad:** un parche que resuelve un finding pero crea otro o rompe funcionalidad.
Cada clase debe tener **benchmarks sintéticos, controles negativos y criterios de parada**. La ausencia de hallazgos no implica seguridad.

## 6. Arquitectura independiente propuesta — límites duros
```text
adversarial-lab/ (nuevo bounded context o repo independiente a decidir en ADR)
  research/            papers, artefactos y matriz de evidencia
  control-plane/       engagement, scope, presupuesto, scheduler, approvals
  provider-adapters/   contrato de agente externo: Codex, Antigravity, Cline, Freebuff, etc.
  campaign-library/   escenarios versionados y metodología
  experiment-engine/  hypothesis graph, planner, observation ledger, evaluator
  execution-plane/    microVM/containers endurecidos, broker, network guard, kill switch
  digital-twins/      build reproducible, synthetic fixtures, fidelity score
  integrations/       herramientas de análisis con licencias y versiones fijadas
  evidence/           hashes, trazas, cadena de custodia, redacción
  evaluation/         oráculos independientes, coverage, false positives, cost
  reporting/          informes diarios, diffs, hallazgos, límites y recomendaciones
  tests/              isolation, fuzzing, failure injection, tenancy, reproducibility
```
**Prohibiciones arquitectónicas:** no importar ni editar `agntia_ciberseguridad/agents/**`; no modificar su gateway MCP, registry, policy o capabilities; no hacer que un agente externo sea una autoridad de autorización; no reutilizar credenciales de cliente en el laboratorio; no acceso a socket Docker host desde workers; no pruebas destructivas sobre sistemas reales sin autorización y procedimientos especiales. Si el repositorio actual no puede albergar este bounded context sin acoplarlo, proponer **nuevo repositorio hermano** con API de intercambio de evidencias, sin tocar el código existente.

## 7. Motor experimental: lo que lo hace distinto
**Hypothesis ledger:** cada hipótesis tiene ID, activo, confianza, precondiciones, falsadores, costo esperado, riesgo, técnica y estado. Un modelo puede proponer pero no marcar CONFIRMED sin oráculo.
**Evidence-driven planning:** la siguiente campaña depende de resultados, cambios en repos, CVEs y regresiones, no solo de una lista cron.
**Adaptive experiment selection:** presupuesto multi-armed bandit / Bayesian optimization solo cuando exista dataset y baselines; inicialmente heurísticas transparentes.
**Multi-model diversity:** asignar investigadores independientes con diferentes modelos/estrategias; agregar por evidencia, no votación.
**Tool observation contract:** salidas tipadas, hashes, provenance, exit code, stderr sanitizado, timeouts y NOT_RUN.
**Reproducibility harness:** imagen fijada por digest, commits, seed, fixture, topology, políticas, modelos, costes y tiempo.
**Oracle:** resultado de test objetivo y verificable; crash por sí solo no demuestra impacto; output LLM no es prueba.
**Retest:** segundo evaluador en entorno nuevo; comparar vulnerable/fixed y test de regresión.
**Learning:** actualizar priorización y corpus de casos a partir de hallazgos verificados; evitar entrenar con datos de cliente sin permiso.
**Risk budget:** ventanas, peticiones, duración, consumo, potencia, límites de red, paradas y revisión humana.

## 8. Digital twin y datos sintéticos: modelo de fidelidad
No decir 'duplicar el sistema del cliente' como garantía automática. Separar:
- F0 **source twin:** código/config sin secretos.
- F1 **service twin:** servicios, rutas, contratos, identidades sintéticas.
- F2 **data twin:** esquemas, distribuciones y restricciones preservadas con generación sintética validada; evitar memorizar registros.
- F3 **dependency twin:** versiones de servicios, colas, permisos y topología, con mocks explícitos para servicios inaccesibles.
- F4 **behavioral twin:** tests de paridad y diferencias documentadas respecto al entorno real.
- F5 **resilience twin:** estados de fallo, backup, restauración y degradación.
Un fidelity report debe enumerar componentes no reproducidos. Nunca copiar tokens, credenciales, PII ni secretos. Los datos sintéticos **no garantizan anonimato por sí solos**: medir riesgos de memorization y reidentificación.

## 9. Operación continua y publicación
Cadencia propuesta: cada cambio crítico→regresión rápida; diario→reconocimiento pasivo y selección de experimentos; semanal→campañas de laboratorio profundas; mensual→ensayos de resiliencia y revisión humana; tras incidente→reproducción y prevención. No realizar ataques activos diarios a producción por defecto.
Output: attack-run.json, scope-manifest.json, hypothesis-ledger.json, evidence-index.json, coverage.json, findings.json, remediation-proposals.json, retest.json, limitations.md, daily-brief.md.
Interfaz con programa AD de autodocumentación: **exportación versionada de evidencia**, no importación de los agentes existentes. Toda publicación requiere aprobación explícita y revisión de privacidad.

## 10. Plan de investigación y gates ANTES de escribir 15 campañas nuevas
**R0 — bibliografía:** descargar/leer completos AIxCC, CyberGym, CyberGym-E2E, AgentCyberRange, PentestGPT y papers relevantes; fichas por metodología, limitaciones y transferibilidad.
**R1 — código externo:** auditar estructura, tests, licencias, CVEs y mantenibilidad de Atlantis, CAI, OSS-Fuzz, PyRIT, garak, ZAP y Schemathesis. Generar matriz BUILD/WRAP/STUDY/REJECT con SHA exacto.
**R2 — arquitectura propia:** ADR comparando bounded context interno frente a repo hermano. Prohibir tocar agentes existentes.
**R3 — amenazas al laboratorio:** threat model del control plane, agent adapters, executor, data twin, evidence y human approval.
**R4 — PoC:** 2 agentes intercambiables en sandbox sintético sin egress, mismo benchmark, oráculo independiente, límites de recursos y kill switch probado.
**R5 — evaluación:** comparativa contra baseline no-LLM, benchmark histórico y humano, coste y falsos positivos; validación en checkout limpio.
**R6 — solo entonces:** diseñar campañas de implementación ultragranares con archivos confirmados, interfaces, migraciones, tests y orden. No convertir el plan V1 en backlog sin estos gates.

## 11. Criterios de excelencia
- **Seguridad:** cero accesos fuera de scope en pruebas de aislamiento; denegación por defecto; kill switch probado.
- **Reproducibilidad:** reconstruir entorno desde hashes y manifests; resultados con intervalos y varianza entre seeds.
- **Validez:** evidencia verificada por oráculos y controles negativos; no contar hallucinations como findings.
- **Intercambiabilidad:** sustituir proveedor de agente sin cambiar campaña ni políticas; medir diferencias.
- **Autonomía:** operar una semana en lab sintético con supervisión y reportes diarios, sin drift de permisos ni datos.
- **Ciencia:** comparar baseline, registrar negativos, fallos, costes, exclusiones y limitaciones.
- **Separación:** ninguna modificación de `agents/**` ni de `/agente`.

## 12. Handoff para la siguiente IA investigadora
> Tu misión NO es implementar el viejo ADV-01..15. Lee este Research Master V2 y las fuentes primarias. Audita papers y repos externos en profundidad, fijando versiones y licencias, y documenta qué partes se pueden usar comercialmente. El laboratorio es un subsistema independiente; no edites, importes ni cambies `agntia_ciberseguridad/agents/**` ni el repositorio `/agente`. Diseña primero una PoC con dos proveedores de coding agents intercambiables, un entorno sintético y oráculos independientes. No confundas scanning con pentesting autónomo ni output LLM con explotación confirmada. No ejecutes pruebas contra terceros ni contra producción. Deja informes con citas, SHA, evidencias, fallos y decisiones BUILD/WRAP/STUDY/REJECT. Solo después escribe campañas detalladas para el código real.
