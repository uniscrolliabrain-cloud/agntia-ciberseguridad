# D5P2 — Policy engine y control determinista de acciones

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 5. Prioridad M0; rol Policy/seguridad.

## Objetivo
Hacer que un modelo comprometido no pueda autorizar llamadas fuera de la política.

## Artefactos previstos
- `agntia_ciberseguridad/agents/policy.py`
- `policies/`
- `tests/security/test_policy_gateway.py`

## Contrato
Decisión sobre principal, acción, recurso, argumentos, destino, sensibilidad y contexto verificado; deny por defecto.

## Dependencias
D5P1

## Tareas originales
- D5P2T1: Comparar OPA/Cedar y elegir un motor pequeño con versión/licencia y casos de frontera documentados. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P2T2: Definir reglas mínimas de lectura, propuestas, escritura aprobada, scopes y excepciones temporales. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P2T3: Aplicar evaluación en cada llamada, no solo al inicio del plan ni en un prompt de supervisor. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P2T4: Permitir reducciones verificadas; expansiones exigen aprobación vinculada a diff/hash/fecha. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P2T5: Crear modo explain/dry-run sin revelar secretos ni permitir que el agente cambie la regla. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P2T6: Probar argumentos anidados, Unicode/canonicalización, policy stale, bypass y cambios de contexto concurrentes. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P2T7: Medir latencia y ejecutar la prueba con respuesta LLM deliberadamente hostil, sin confiar en su rechazo textual. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D5P2-TEST-1: Una salida maliciosa del modelo pide una tool/argumento no permitido y el executor la bloquea.
- D5P2-TEST-2: Política caducada o motor caído no se resuelve ejecutando como owner.

Rollback: Activar bundle anterior firmado o denegar efectos; nunca bypass directo al proveedor.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
