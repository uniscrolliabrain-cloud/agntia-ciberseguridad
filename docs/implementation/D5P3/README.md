# D5P3 — Flujos de datos, egress y cuarentena

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 5. Prioridad M0; rol Data security.

## Objetivo
Evitar fuga por combinaciones de herramientas permitidas y separar material hostil del control.

## Artefactos previstos
- `agntia_ciberseguridad/agents/data_labels.py`
- `agntia_ciberseguridad/agents/egress.py`
- `tests/security/test_data_flows.py`

## Contrato
Datos etiquetados por origen/sensibilidad/destino permitido; executor verifica uso y salida.

## Dependencias
D5P1, D5P2

## Tareas originales
- D5P3T1: Definir etiquetas y propagación mínima de origen, tenant, sensibilidad y restricciones de salida. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P3T2: Aislar extracción de documentos/repos/tools de la planificación privilegiada y aceptar hechos tipados. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P3T3: Crear allowlist de destinos y proxy de salida con validación DNS/IP y audiencia. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P3T4: Comprobar composición de acciones y adjuntos, no únicamente si la tool send/email existe en ACL. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P3T5: Implementar desclasificación humana explícita ligada al contenido/destino sin quitar el historial de origen. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P3T6: Probar exfiltración canario, instrucciones indirectas, memoria contaminada y resultado engañoso de herramientas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P3T7: Documentar límites textuales/phishing y evitar anunciar una prueba formal general derivada de CaMeL. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D5P3-TEST-1: Lectura permitida de un documento privado seguida de envío a destino nuevo queda denegada.
- D5P3-TEST-2: Una instrucción inyectada en log/repo/PDF no amplía tools ni permisos del plan.

Rollback: Cerrar salida no verificada, conservar el trabajo en cuarentena y pedir revisión cuando corresponda.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
