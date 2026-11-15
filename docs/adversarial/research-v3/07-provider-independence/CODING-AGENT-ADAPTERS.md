# Adaptadores de agentes de programación — independencia real
## Principio
Codex, Antigravity, Cline, Freebuff, Claude Code, OpenHands y otros son **proveedores externos reemplazables**. No reutilizar ni tocar el sistema de agentes de Agntia Cyber. La independencia exige pruebas, no una interfaz vacía.

## Contrato abstracto (diseño, no código existente)
`ProviderCapabilities`: supports_noninteractive, tool_permissions, workspace_mount, max_runtime, session_resume, structured_output, model_selection, telemetry, cost_reporting, cancellation, license.
`AgentTask`: experiment_id, workspace_ref, objective, permitted_tool_ids, input_artifact_refs, output_schema, time_budget, token_budget, network_policy_ref.
`AgentResult`: status, artifact_refs, observations, trace_ref, usage, cost, exit_code, errors, provider_version.
`cancel(run_id)`, `health()`, `capabilities()`, `execute(task)`, `resume(checkpoint)` (si disponible).

## Riesgos por proveedor
- **Codex:** investigar CLI/API y ejecución no interactiva, políticas de approvals, aislamiento, telemetría y licencias según versión; no asumir capacidad de sandbox remoto local.
- **Antigravity:** verificar existencia de API/CLI automatizable, exportación de resultados, permisos y condiciones; si no existe interfaz estable, adapter = BLOCKED, no simular soporte.
- **Cline:** evaluar modo headless, control de permisos y tool approvals; IDE no equivale a runner autónomo.
- **Freebuff:** verificar protocolo real, integración cloud, permisos, API y límites. No prometer automatización si no hay API verificable.
- **OpenHands/otros:** estudiar runtime y Docker/socket boundaries; no adoptar su sandbox como frontera de confianza sin auditoría.

## PoC obligatoria de independencia
Mismo experimento sintético con 2 proveedores diferentes; mismo input, scope, broker, oracle y output JSON; registrar diferencias en tool calls, coste, tiempos, findings y errores. Sustituir un proveedor sin tocar policy, campaign, evidence ni evaluator. Simular proveedor hostil, prompt injection en README, herramienta inexistente, timeout, cancel, respuesta no JSON, crash y reanudación.
## Prohibiciones
Ningún adapter puede elevar scope, abrir red, tocar repos no autorizados, escribir en producción, montar credenciales persistentes ni marcar hallazgos confirmados. Un proveedor solo entrega **propuestas y observaciones**, no veredictos finales.
