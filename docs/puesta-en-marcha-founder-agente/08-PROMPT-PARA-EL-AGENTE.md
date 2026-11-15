# 08 — Prompt ejecutable para Freebuff/Codex
Trabaja en `uniscrolliabrain-cloud/agntia-ciberseguridad` siguiendo `docs/puesta-en-marcha-founder-agente/`. **Objetivo:** ayudar al founder a poner en marcha el middleware de ciberseguridad existente: cuentas, permisos, instalaciones, variables, servicios, integración, operaciones, legal y piloto. NO rehagas el Adversarial Lab ni sus 18 campañas: otro agente trabaja en `feat/advlab-campaigns-C01-C18`.

## Restricciones
- Esta rama es documental; crea rama de trabajo propia para cambios de código y PR para revisión.
- No escribas en main, no fusiones, no despliegues, no contrates, no crees cuentas, no uses clientes reales ni modifiques `/agente` sin aprobación expresa.
- No solicites secretos en chat ni los copies a GitHub; prepara referencias y validadores.
- No ejecutes pruebas activas sobre sistemas de terceros. Solo activos sintéticos o propios autorizados.
- Revisa `README.md`, `docs/ESTADO-VIGENTE.md`, `docs/operations/RUNBOOK.md`, `docs/release/PILOT-ACCEPTANCE.md`, `docs/auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md` y código real antes de actuar.
- Contrasta cualquier afirmación histórica con HEAD; evita repetir funciones ya implementadas.

## Primer encargo, sin preguntas innecesarias
1. Congela SHA de main y crea inventario de todos los servicios/paquetes, config, env vars, adaptadores, tests y operaciones. Indica ruta y si la dependencia es real, simulada o ausente.
2. Ejecuta pruebas offline existentes en entorno efímero y guarda comandos, versiones, exit codes y logs redactados.
3. Produce `reports/00-INVENTARIO-REAL.md` con tabla `servicio / estado / cuenta / coste / secret-ref / instalación / responsable / próximo paso`.
4. Produce `reports/01-CHECKLIST-FOUNDER.md` con solo decisiones y cuentas que el founder deba activar ahora, instrucciones de UI precisas y enlaces oficiales verificados.
5. Produce `reports/02-PLAN-OPERATIVO-PRIMER-LAB.md` con pasos técnicos, rollback, presupuesto y pruebas.
6. No avances a infraestructura de pago, red, tokens reales, /agente ni producción sin autorización.
7. Crea PR de documentación para review. Al finalizar, resume `HECHO / PENDIENTE / BLOQUEADO / REQUIERE_FOUNDER`.

## Formato de cada reporte
Fecha, repo, rama, SHA, objetivo, archivos inspeccionados, decisiones, pasos ejecutados, pruebas con comando+exit, servicios/credenciales necesarios sin valores, costes verificados y fecha, bloqueos, seguridad, rollback y siguiente aprobación.

## Criterio de éxito
El founder puede entrar en cada consola necesaria, saber qué configurar y cuándo; el agente puede continuar sin adivinar nombres de variables, permisos o entornos; no hay promesas de producción ni acciones no autorizadas.
