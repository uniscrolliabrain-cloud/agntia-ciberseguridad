# D3P3 — Normalización, deduplicación y contexto

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 3. Prioridad M0; rol Modelo de findings.

## Objetivo
Unificar herramientas preservando evidencia, diferencias de cobertura e historial.

## Artefactos previstos
- `agntia_ciberseguridad/findings/normalize.py`
- `agntia_ciberseguridad/findings/identity.py`
- `tests/unit/test_finding_history.py`

## Contrato
ID estable por regla/recurso/ubicación normalizada; historial de cambios y relaciones de componente/activo.

## Dependencias
D2P3, D2P4, D2P5

## Tareas originales
- D3P3T1: Definir schema de finding con fuente, snapshot, regla/CVE/CWE, ubicación, severidad y confianza separadas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P3T2: Crear adaptadores de normalización con campos desconocidos explícitos y validación estricta. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P3T3: Diseñar identidad estable sin secretos y reglas de deduplicación por dominio/versión. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P3T4: Conservar first_seen/last_seen, reaparición, excepción y estados suspected/confirmed/remediated/verified_fixed. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P3T5: Relacionar repo, SBOM, imagen, despliegue e identidad sin inferir exposición faltante. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P3T6: Probar merges, splits, cambios de regla, scanner parcial y rutas homónimas entre tenants. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P3T7: Entregar consulta de historial que explique por qué cambió un riesgo sin inventar un ataque real. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D3P3-TEST-1: Dos herramientas que señalan lo mismo se relacionan sin borrar sus observaciones originales.
- D3P3-TEST-2: Un finding desaparece por parser fallido y no se marca automáticamente arreglado.

Rollback: Reconstruir proyección desde observaciones originales; no reescribir evidencia fuente.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
