# D7P5 — Empaquetado, Windows/Linux y supply chain de release

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 7. Prioridad M0; rol Release engineering.

## Objetivo
Hacer instalable/reproducible el piloto y documentar operación segura sin suponer Docker local perfecto.

## Artefactos previstos
- `infra/compose.yaml`
- `scripts/verify_lab.ps1`
- `scripts/verify_lab.sh`
- `docs/operations/RUNBOOK.md`
- `docs/operations/ROLLBACK.md`

## Contrato
Paquetes/versiones y contenedores fijados; secretos externos, puertos mínimos y ninguna credencial de ejemplo real.

## Dependencias
D7P4

## Tareas originales
- D7P5T1: Construir paquetePython/SDK y Dockerfiles sin latest variable ni copiar secretos al contexto. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P5T2: Preparar Compose de laboratorio con redes/puertos mínimos, volúmenes y límites por perfil. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P5T3: Escribir PowerShell/servidorLinux con comprobación de entorno, sin cambiar políticas globales o reset destructivo. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P5T4: Emitir SBOM, checksums, notas de licencia y avisos; firmar/verificar artefactos cuando la infraestructura lo permita. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P5T5: Documentar instalación, rotación, backup, restore, upgrade, incidentes y rollback con comandos reales. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P5T6: Probar instalación desde artefacto limpio, no solo import editable dentro del checkout. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P5T7: Registrar matrices SO/arquitectura/runtime verificadas y no prometer soporte de combinaciones no ensayadas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D7P5-TEST-1: Instalación limpia en el entorno declarado ejecuta demo/tests del alcance o registra plataforma no verificada.
- D7P5-TEST-2: Rollback conserva evidencia y no borra cambios del usuario ni contactos/proyectos ajenos.

Rollback: Publicar versión anterior compatible, desactivar features nuevas y conservar migraciones aditivas.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
