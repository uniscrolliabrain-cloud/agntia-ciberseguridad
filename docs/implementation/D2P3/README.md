# D2P3 — Adaptador Gitleaks y protección de secretos

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 2. Prioridad M0; rol AppSec secretos.

## Objetivo
Detectar canarios/secretos en snapshots sin exponer ni validar credenciales reales.

## Artefactos previstos
- `agntia_ciberseguridad/adapters/gitleaks.py`
- `fixtures/secrets/`
- `tests/contracts/test_gitleaks.py`

## Contrato
El finding guarda ubicación/regla y referencia redactada; jamás secreto crudo como ID, log o prompt.

## Dependencias
D2P1, D2P2

## Tareas originales
- D2P3T1: Revisar licencia y formato de la release elegida; fijar configuración y modo de salida redactado. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P3T2: Implementar parser versionado con límites y estados distinctos findings/no-findings/error. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P3T3: Normalizar repositorio, commit, fichero, rango, rule_id, confianza y evidencia minimizada. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P3T4: Deduplicar por ubicación/regla/snapshot sin usar valores secretos o hashes débiles públicamente correlacionables. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P3T5: Crear fixtures de canario, falso positivo, binario omitido y parser roto. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P3T6: Ejecutar contrato real con binario fijado y buscar centinelas en reportes/logs/eventos producidos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P3T7: Presentar guía de rotación como propuesta; nunca llamar al servicio externo para comprobar si una credencial funciona. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D2P3-TEST-1: Canario fixture genera finding, pero su valor no aparece en export/log/evento.
- D2P3-TEST-2: Error de scanner, versión desconocida o JSON inválido no se convierte en scan limpio.

Rollback: Deshabilitar adaptador y mantener snapshot/fallo; rotar únicamente secretos propios de laboratorio si fue necesario.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
