# D4P1 — OpenTelemetry y correlación extremo a extremo

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 4. Prioridad M0; rol Observabilidad.

## Objetivo
Hacer visible cada decisión de seguridad y ejecución sin introducir secretos en trazas.

## Artefactos previstos
- `agntia_ciberseguridad/telemetry/tracing.py`
- `infra/observability/collector.yaml`
- `tests/integration/test_trace_context.py`

## Contrato
Correlacionar petición→job→runner→finding→reporte con IDs opacos y atributos minimizados.

## Dependencias
D3P1

## Tareas originales
- D4P1T1: Fijar SDK/collector y esquema de atributos; registrar licencias y endpoint de export aprobado. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P1T2: Instrumentar API, policy, DB y workers con propagación W3C y correlation/causation IDs. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P1T3: Validar traceparent/baggage y no confiar en tenant/rol recibidos a través de telemetría. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P1T4: Excluir bodies, tokens, prompts, rutas sensibles y consultas SQL completas de spans. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P1T5: Implementar export acotado, timeout, sampling y fallo del collector sin bloquear rutas críticas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P1T6: Ejecutar una vertical real y reconstruir su secuencia mediante trace y referencias de evidencia. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P1T7: Probar entrada malformada, trace cruzado, collector caído y búsqueda automática de centinelas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D4P1-TEST-1: Una ejecución asíncrona conserva trazabilidad sin aceptar identidad del baggage externo.
- D4P1-TEST-2: Un canario secreto no aparece en span, evento, excepción o export OTLP.

Rollback: Desactivar export externo y conservar logs mínimos seguros; no apagar enforcement si falla el collector.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
