# D2P6 — Trivy para imágenes e IaC del piloto

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 2. Prioridad M1; rol AppSec contenedores.

## Objetivo
Ampliar al artefacto desplegable cuando exista capacidad, sin multiplicar scanners redundantes.

## Artefactos previstos
- `agntia_ciberseguridad/adapters/trivy.py`
- `infra/fixtures/container/`
- `tests/contracts/test_trivy.py`

## Contrato
Imagen por digest o IaC snapshot; sin ejecutar la imagen ni aplicar infraestructura.

## Dependencias
D2P1, D2P2

## Tareas originales
- D2P6T1: Elegir perfiles image/config del piloto y decidir qué resultados ya cubre OSV para evitar duplicación. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P6T2: Fijar imagen/herramienta/DB, permisos de registro y caché separada de credenciales del cliente. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P6T3: Analizar artefactos sin arrancar workloads ni aplicar planes Terraform/Kubernetes. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P6T4: Normalizar paquetes, configuración, severidad y corrección con referencias al digest y regla. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P6T5: Comparar SBOM/lockfile con imagen para describir presencia o desconocimiento de despliegue. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P6T6: Ejecutar casos reales sintéticos, cache caducada y cancelación con medición de recursos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P6T7: Aceptar como diferido si no cabe en presupuesto; reportar hueco y dependencia para ampliación posterior. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D2P6-TEST-1: Imagen de laboratorio afectada por advisory produce evidencia del componente realmente presente.
- D2P6-TEST-2: No hay imagen/IaC o DB reciente y el reporte distingue not_tested/partial.

Rollback: Desactivar perfil Trivy y mantener explícita la cobertura ausente; no instalar Grype/Checkov para ocultar el fallo.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
