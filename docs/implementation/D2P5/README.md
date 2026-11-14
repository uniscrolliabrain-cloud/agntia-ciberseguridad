# D2P5 — Semgrep CE y reglas propias revisadas

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 2. Prioridad M0; rol AppSec código.

## Objetivo
Obtener hallazgos estáticos útiles sin usar reglas con licencia incompatible o fiarse de comentarios maliciosos.

## Artefactos previstos
- `agntia_ciberseguridad/adapters/semgrep.py`
- `rules/semgrep/`
- `tests/contracts/test_semgrep.py`

## Contrato
Reglas fijadas y con licencia/procedencia; análisis no ejecuta imports o scripts del repositorio.

## Dependencias
D2P1, D2P2

## Tareas originales
- D2P5T1: Seleccionar lenguajes del piloto y distinguir CE, reglas propias, registry y características SaaS/Pro. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P5T2: Crear pequeño bundle de reglas con objetivo, ejemplos positivos/negativos y licencia registrada. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P5T3: Implementar parser JSON/SARIF con ubicaciones canónicas y manejo de timeout/parse/error. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P5T4: Desactivar descargas de reglas variables y ejecución de código analizado; limitar archivos generados/vendor. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P5T5: Probar defectos representativos, falsos positivos y límites de análisis interarchivo declarados. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P5T6: Ejecutar contratos reales y comprobar que findings incluyen versión de motor y bundle. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P5T7: Documentar incertidumbre y cobertura por lenguaje; el LLM puede explicar, no declarar seguro un caso no cubierto. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D2P5-TEST-1: Código fixture vulnerable se detecta y su variante corregida no mantiene el mismo finding confirmado.
- D2P5-TEST-2: Comentario hostil contra el auditor no modifica reglas, scope ni resumen autoritativo.

Rollback: Volver al bundle de reglas anterior; conservar diferencia de cobertura para explicar variaciones.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
