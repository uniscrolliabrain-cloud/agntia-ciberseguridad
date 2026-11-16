# Centro de operaciones — Agntia Ciberseguridad

**Actualización:** 2026-11-16. **Ámbito:** estado, decisiones y cierre hacia producción. **Rama de publicación:** `main`.

> Este es el **punto de entrada operativo vigente**. La documentación anterior se conserva como investigación, historial, diseño y evidencia; no debe ejecutarse como si todas sus campañas siguieran pendientes. Ninguna frase de esta carpeta sustituye los gates ejecutables ni `docs/release/status.json`.

## Programa de ejecución para FreeBuff

**[Campañas VS-00→VS-13: vertical slice productivo y beta dogfooding](campanas-vertical-slice-beta/README.md)** — diseño de ejecución, contratos, gates, reportes y handoff. **Solo documentación; FreeBuff implementa el código y el founder aprueba merges, integraciones y despliegues.**

## Orden de lectura

1. [01 — Estado y alcance](01-ESTADO-Y-ALCANCE.md): qué está construido, qué está probado y qué sigue bloqueado.
2. [02 — Matriz de cierre](02-MATRIZ-CIERRE-PRODUCCION.md): trabajo verificable, dependencias, gates y orden.
3. [03 — Cuentas y secretos](03-CUENTAS-SECRETOS-FOUNDER.md): lo que prepara el founder y lo que implementa el agente.
4. [04 — Handoff de ejecución](04-HANDOFF-EJECUCION.md): procedimiento seguro para FreeBuff y revisores.

## Fuentes de verdad y precedencia

1. **Código y configuración de `main`** para saber qué existe; confirmar SHA al iniciar una campaña.
2. **Ejecución reproducible y artefactos de CI** para afirmar que algo funciona; si no se ejecutó en el entorno objetivo, escribir `NO VERIFICADO`.
3. **`docs/release/status.json`** para los gates del programa original de 42 fases; **no** equivale a porcentaje global de terminación del producto ni al estado de las 18 campañas adversariales.
4. **Informes fechados** para conocer el resultado y las limitaciones de una ejecución concreta; nunca extrapolar resultados a otro SHA.
5. **Concept masters, campañas, roadmaps y handoffs históricos** como diseño y trazabilidad, no como inventario de faltantes actuales.

## Familias documentales, sin sumar campañas

| Familia | Función | Referencia | Interpretación |
|---|---|---|---|
| 42 fases / 294 tareas | Programa original de middleware | [status.json](../release/status.json) y [campaña](../campaigns/2026-11-10-seven-days/README.md) | 2 fases PASS, 40 PARTIAL; estados del programa, no del laboratorio |
| CY-R01–R12 | Auditoría y correcciones diferenciales del runtime | [auditoría](../auditoria-runtime/AUDITORIA-FUNCIONAL-2026-11-14.md) y [programa](../auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md) | Revisar contra código antes de ejecutar |
| AD-01–AD-15 | Trazabilidad y documentación verificable | [baseline](../autodoc/BASELINE-AUDIT.md) | AD-01 reportada; posteriores, comprobar ejecución antes de declarar pendientes |
| C01–C18 + B/D | Laboratorio adversarial y hardening | [ejecución](../adversarial/implementation-v1/execution/ADVLAB-EXECUTION-2026-11-15.md), [B](../adversarial/implementation-v1/execution/B-VAULT-BROKER-RELEASE-2026-11-15.md), [D](../adversarial/implementation-v1/execution/D-OPERATIONS-MULTITENANT-2026-11-15.md) | Código integrado posteriormente en main; tests reportados, dependencias reales pendientes |
| Founder onboarding | Infra, credenciales, aceptación y piloto | [guía](../puesta-en-marcha-founder-agente/02-CUENTAS-Y-SERVICIOS.md) y [plan](../puesta-en-marcha-founder-agente/07-PLAN-DE-TRABAJO-Y-CHECKLIST.md) | Reutilizar y actualizar por gates |

## Reglas de edición

- Nunca sobrescribir informes de ejecución históricos ni alterar métricas antiguas.
- No llamar PASS a una capacidad sin SHA, entorno, comando, resultado y limitaciones.
- Distinguir `IMPLEMENTADO`, `PROBADO EN SINTÉTICO`, `BLOQUEADO POR ENTORNO`, `NO VERIFICADO`, `ACEPTADO PARA PRODUCCIÓN`.
- No copiar secretos, tokens, datos de clientes ni muestras sensibles a Markdown.
- Los documentos históricos con avisos contradictorios deben enlazar aquí; conservar su contexto original.
- Sin escritura en `/agente`, sin despliegues y sin habilitar escaneo de clientes por actualizar documentos.
