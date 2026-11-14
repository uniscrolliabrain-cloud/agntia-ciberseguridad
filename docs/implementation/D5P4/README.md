# D5P4 — MCP, skills y cambios de supply chain

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 5. Prioridad M0; rol Identidad/tools.

## Objetivo
Evitar que una herramienta cambie sus permisos o comportamiento descrito sin nueva admisión.

## Artefactos previstos
- `agntia_ciberseguridad/agents/mcp_adapter.py`
- `agntia_ciberseguridad/agents/manifest_review.py`
- `tests/contracts/test_mcp_security.py`

## Contrato
Protocolo/versiones fijados, audiencia y consentimiento; sin token passthrough ni ejecución de skill no admitida.

## Dependencias
D5P1, D5P2

## Tareas originales
- D5P4T1: Fijar versión MCP e identificar transporte, OAuth, audiencia y reglas de sesión aplicables. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P4T2: Registrar hash de descripciones, schemas, instrucciones de skills y dependencias, no solo binarios. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P4T3: Validar consentimiento de cliente, callback/redirect y resource audience sin reenviar tokens ciegamente. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P4T4: Aplicar red, timeout, tamaño y rate limits a cada servidor de herramientas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P4T5: Crear detección de drift y revisión de diferencias de manifest con aprobación de expansión. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P4T6: Probar tool poisoning sintético, schema cambiado, replay de sesión y recurso equivocado. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P4T7: Entregar matriz de conformidad contractual y limitaciones de integración, sin etiquetar todo MCP como seguro. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D5P4-TEST-1: Una descripción/schema de tool cambia y su autorización anterior deja de valer.
- D5P4-TEST-2: Un MCP externo intenta reutilizar un token de otro recurso y no obtiene acceso.

Rollback: Desconectar servidor/version nueva y restaurar admisión previa verificada si sigue vigente.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
