# Motor científico de experimentación continua
## Objetivo
Diseñar un **experimento reproducible**, no una conversación infinita de un agente. La ejecución diaria debe priorizar cambios y riesgo, administrar presupuesto, acumular conocimiento verificado y detectar regresiones.

## Objetos conceptuales
**Engagement:** tenant, consentimiento, alcance, vencimiento, políticas y responsable.
**Twin:** código/build/topología/data/identity/fidelity manifest.
**Hypothesis:** ID, activo, tipo, precondiciones, falsadores, coste estimado, riesgo, evidencias previas.
**Experiment:** hipótesis, herramienta/adaptador, entorno, seed, input hash, presupuesto, stop, oracle.
**Observation:** salida tipada, exit code, trace, provenance, hashes, timestamp, clasificación.
**Verdict:** CONFIRMED, DISPROVED, INCONCLUSIVE, NOT_RUN; justificación y evaluator independiente.
**Finding:** solo si la hipótesis fue confirmada; severidad y confianza separadas.
**Retest:** comparación vulnerable/fixed con tests funcionales y de seguridad.
**Learning:** patrones verificados y prioridad; no entrenamiento con datos privados sin permiso.

## Scheduler experimental
Trigger por commit, cambio de dependencia, nuevo CVE aplicable, cambio de configuración, reporte de incidente, expiración de prueba o ciclo diario. Prioridad inicial transparente = impacto × exposición × probabilidad de fallo × novedad / (coste+riesgo); pesos configurables y auditables. Evitar modelos opacos de bandits antes de tener suficientes datos. Scheduler debe soportar ventanas, rate limits, fairness por tenant, cancelación, reintento, checkpoint, circuit breaker y caducidad de permisos.

## Planificación agnóstica
Un planner puede usar LLM, heurísticas o humano. Produce **propuestas estructuradas**; el policy engine acepta o rechaza cada paso. Nunca aceptar tool calls sin schema ni conceder capacidades por texto. El experimento y su oráculo son independientes del proveedor.
## Memoria de investigación
Ledger append-only de hipótesis, observaciones, fallos, descartes, evidencias y decisiones. El agente puede recibir un resumen compacto, pero el estado autoritativo vive fuera de su contexto. Evitar loops mediante fingerprints de hipótesis/experimentos, TTL y budgets.
## Experimentos comparativos
A/B mismo repo, mismos límites, seeds y oráculos, diferentes agentes; baseline sin LLM; evaluador blind. Repetir n veces y reportar varianza, no solo mejor ejecución. Distinguir bug confirmado, no confirmado, falso positivo, test no ejecutado y error de infraestructura.
## Resultado diario
Cambios evaluados, experimentos ejecutados/omitidos, hipótesis nuevas/descartadas, hallazgos confirmados, falsos positivos, fallos de herramientas, coste, riesgo residual y acciones recomendadas. Sin reportes de 'todo seguro' por ausencia de findings.
