# Centro de ejecución — Agntia Ciberseguridad (founder + agente)
**Fecha:** 2026-11-15 · **Rama documental:** `docs/auditoria-y-plan-operativo-cyber-20261115` · **No fusionar automáticamente.**
**Objetivo:** convertir una demo sintética y una rama adversarial no integrada en un laboratorio defensivo verificable, después en piloto autorizado, y finalmente en servicio gestionado, sin inventar pruebas ni contratar infraestructura prematuramente.

## Leer en este orden
1. [01-AUDITORIA-Y-MAPA-DE-BLOQUEOS.md](01-AUDITORIA-Y-MAPA-DE-BLOQUEOS.md): hechos contrastados, riesgos, evidencia y diferencias entre middleware y laboratorio.
2. [02-PLAN-SECUENCIAL-Y-GATES.md](02-PLAN-SECUENCIAL-Y-GATES.md): campañas de cierre y dependencias con criterios verificables.
3. [03-DECISIONES-DEL-FOUNDER-Y-CUENTAS.md](03-DECISIONES-DEL-FOUNDER-Y-CUENTAS.md): elecciones humanas, proveedores, infraestructura y cuentas sin claves en Git.
4. [04-HANDOFF-AGENTE-EJECUTOR.md](04-HANDOFF-AGENTE-EJECUTOR.md): mandato copiable para Freebuff/Codex y política de ramas, evidencias y paradas.
5. [05-SEGURIDAD-PRUEBAS-Y-ACEPTACION.md](05-SEGURIDAD-PRUEBAS-Y-ACEPTACION.md): threat model, pruebas negativas, release y piloto.
6. [06-TABLERO-Y-REGISTRO.md](06-TABLERO-Y-REGISTRO.md): checklist vivo, decisiones, reportes y gates.

## Separación de los dos productos
- **Middleware principal:** `agntia_ciberseguridad/**`, SDK y documentación de 42 fases. `docs/release/status.json` en main: `SYNTHETIC_DEMO_NOT_PRODUCTION`, 2 PASS/40 PARTIAL, owner acceptance pendiente, production_enabled false.
- **Adversarial Lab:** `adversarial_lab/**` en `feat/advlab-campaigns-C01-C18`, +4 commits y 125 archivos de diferencia frente a main al revisar. 18 campañas descritas, 86 tests **declarados** por su informe, no reejecutados aquí; herramientas externas y agentes reales bloqueados.
- No elevar los PASS locales del laboratorio a aceptación del middleware. No mezclar claves, estado, autoridades o evidencia de ambos.

## Semáforo
- **ROJO:** ejecutar código adversarial de clientes en subprocess local; conectar clientes reales; habilitar red arbitraria; aprobar releases con dependencias no auditadas; fusionar sin review.
- **ÁMBAR:** reproducir tests offline; OCI con fixture y sin red; conectar un proveedor de agente a gemelo sintético bajo presupuesto; observar ciclos sintéticos.
- **VERDE:** lectura, auditoría, pruebas unitarias sin red, documentación, fixtures y comparación de ramas.

## Primeras 24 horas de trabajo
1. Founder revisa y aprueba solo este plan documental, no el despliegue.
2. Agente crea PR desde esta rama documental; no merge automático.
3. Agente toma SHA de main y rama adversarial, exporta comparación completa y manifiesto de 125 archivos.
4. Reejecuta suites en entorno efímero sin secretos y adjunta logs; separa reproducible/no reproducible.
5. Abre PR de código **desde rama nueva derivada de la adversarial**, nunca desde main ni sobre el branch original sin autorización.
6. Corrige primero seguridad de paths/keys y sandbox; realiza test de aislamiento OCI real.
7. Founder elige infraestructura, secretos y proveedor solo cuando gates previos sean verdes.

## Fuente de verdad
Esta guía es un **plan de trabajo**, no un certificado de seguridad. Priorizar `README.md`, `docs/release/status.json`, `docs/auditoria-runtime/`, `docs/adversarial/implementation-v1/execution/ADVLAB-EXECUTION-2026-11-15.md` y el código fijado por SHA. Cualquier discrepancia se documenta; nunca se resuelve cambiando un estado a PASS sin evidencia.
