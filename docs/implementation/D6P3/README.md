# D6P3 — Antifraude y verificación por contexto

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 6. Prioridad M1; rol Analista antifraude.

## Objetivo
Ayudar a detectar suplantación/estafas sin acusaciones ni bloqueos basados solo en un scoreIA.

## Artefactos previstos
- `agntia_ciberseguridad/fraud/signals.py`
- `agntia_ciberseguridad/fraud/verification.py`
- `tests/e2e/test_fraud_triage.py`

## Contrato
Señales con fuente/incertidumbre y revisión; cambios sensibles se verifican por canal previamente registrado.

## Dependencias
D5P3, D6P2

## Tareas originales
- D6P3T1: Definir permisos de lectura de correo/URLs y minimizar datos antes de análisis. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P3T2: Normalizar dominios, Unicode, cabeceras y relaciones de remitente sin visitar destinos arbitrarios. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P3T3: Recoger SPF/DKIM/DMARC/reputación solo cuando la fuente/licencia y autenticidad estén comprobadas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P3T4: Diseñar flujo de verificación fuera de banda para pagos, destinatarios y solicitudes urgentes. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P3T5: Tratar deepfake/provenance como señales falibles y explicar ausencia de evidencia sin concluir falsedad. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P3T6: Probar casos sintéticos benignos, suplantación, cambioIBAN y confirmación por canal no confiable. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P3T7: Entregar recomendaciones citadas y revisión humana; ningún envío, transferencia o bloqueo real por defecto. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D6P3-TEST-1: Mensaje con supuesto nuevoIBAN no convierte su propio enlace/teléfono en canal confiable.
- D6P3-TEST-2: Dominio/voz sospechosos no producen veredicto definitivo ni bloqueo laboral automático.

Rollback: Retirar señal/automatismo y mantener caso revisable; no borrar el mensaje original ni publicar acusaciones.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
