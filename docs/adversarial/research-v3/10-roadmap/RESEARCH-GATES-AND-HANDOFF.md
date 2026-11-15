# Gates de investigación antes de autorizar campañas de implementación
**La solicitud actual es terminar investigación primero. No crear campañas de código todavía.**

## R0 — lectura y bibliografía
Completar fichas con metodología, experimentos, ablations, límites y riesgos de AIxCC/Atlantis, CyberGym/E2E, AgentCyberRange, PentestGPT, Fuzzilli, OSS-Fuzz, PyRIT, garak, CAI. Registrar papers completos y versiones. **Esta entrega cubre fichas críticas iniciales; lectura íntegra y replicación pendientes.**

## R1 — due diligence de repos externos
Por herramienta: checkout a commit, inventario SPDX, dependencias, CVEs, tests, permisos, network/egress, uso comercial, estabilidad de APIs, imágenes y costes. **En esta entrega solo se han inspeccionado árboles y documentos de arquitectura, no tests ni dependencias.**

## R2 — threat model del laboratorio
STRIDE/attack trees sobre adapter, broker, sandbox, synthetic data, evidence, scheduler, publication, approvals. Simular hostiles y cross-tenant. Pendiente de PoC.

## R3 — prototipos comparativos
PoC aislada con dos proveedores verificablemente automatizables; experimento sintético, oráculo independiente, límites, egress y kill switch. No ejecutar sin infraestructura y aprobación.

## R4 — benchmarking
Baselines no-LLM y LLM, mismo presupuesto, oráculos, seeds, holdout, reporte de costes y fallos. No afirmar superioridad sin datos.

## R5 — ADR de ubicación y licencias
Decidir repo hermano vs bounded context, stack, aislamiento, almacenamiento, contratos y ownership. Revisión de licencias y legalidad del uso comercial.

## R6 — SOLO ENTONCES, campañas de código
Diseñar 15–30 campañas según resultados reales, con archivos confirmados, patches, dependencias, rollback, tests, auditorías, recursos, definición de DONE y reports. Nunca partir del V1 ADV-01..15 como si fuera diseño aprobado.

## Handoff literal para IA investigadora
> Estás trabajando en una capacidad **independiente** de hacking ético experimental. NO toques el código de agentes existente ni `/agente`. Lee el dossier research-v3 entero, después abre fuentes primarias y comprueba su implementación a SHAs fijos. Investiga papers completos, arquitectura de herramientas, licencias, dependencias, tests y benchmarks; deja notas reproducibles con fuentes y diferencias entre observación e hipótesis. Compara repo hermano vs módulo aislado. No escribas campañas de código hasta cerrar R0–R5 y obtener aprobación. No ejecutes pruebas contra sistemas ajenos; toda experimentación activa va a sandboxes propios autorizados. Entrega matrices BUILD/WRAP/STUDY/REJECT, threat model, resultados PoC, costes y límites. Si algo no se puede verificar, marca UNKNOWN; no inventes evidencia.
