# Campaña de siete días · Agntia Ciberseguridad

**42 fases, 294 microtareas, 84 escenarios de aceptación.** Estado: plan documentado, no implementación ejecutada. Objetivo: piloto verificable con rigor inspirado en plataformas líderes, sin prometer equivalencia mundial en una semana.

## Empezar

1. [Campaña maestra](00-campana-maestra.md).
2. [Día1](01-dia-1.md), [Día2](02-dia-2.md), [Día3](03-dia-3.md), [Día4](04-dia-4.md), [Día5](05-dia-5.md), [Día6](06-dia-6.md), [Día7](07-dia-7.md).
3. [Pruebas y evidencia](08-matriz-de-pruebas-y-evidencia.md) y [84 escenarios](gate-scenarios.md).
4. [Calidad y comparación](09-calidad-y-comparacion-con-lideres.md).
5. [Operación y prompts](10-operacion-y-prompts.md).
6. [Continuidad30/60/90](11-continuidad-30-60-90.md) y [contratos](12-contratos-y-artefactos.md).
7. [Plantilla de fase](templates/phase-report.md), [reporte founder](templates/founder-report.md) y [evidencia](evidence/README.md).

[Campaign.json](campaign.json) contiene el DAG de fases/tareas y estados iniciales. [validation.json](validation.json) solo acredita comprobaciones documentales. [observability-upstreams.json](observability-upstreams.json) recoge siete candidatos adicionales de observabilidad, sin instalación/auditoría de código.

## Validar y empaquetar

Desde la raíz:

```bash
python scripts/validate_foundation.py
python scripts/validate_campaign.py
python scripts/create_handoff_zip.py
```

El ZIP incluye únicamente archivos versionados, sin .git/secretos/datos de clientes. El script se ejecuta tras añadir/commitear la documentación. No arranca el middleware ni instala herramientas.

La campaña parte de la [documentación técnica inicial](../../README.md). No modifica ni autoriza escribir en `/agente`, comprar servicios o activar producción. El usuario sí ha pedido publicar esta documentación en `uniscrolliabrain-cloud/agntia-ciberseguridad`; la implementación futura mantiene sus propios gates.
