# Puesta en marcha real — Agntia Ciberseguridad
**Guía de operaciones para founder + agente · 2026-11-15**
**Alcance:** middleware principal en main; el Adversarial Lab se desarrolla y audita en su rama independiente. No repetir sus campañas aquí.
**Estado comprobado en documentación:** demo sintética no productiva; API FastAPI, SDK TS, workers, scanners offline y UI piloto existentes. docs/release/status.json indica 2 PASS y 40 PARTIAL; faltan aceptación independiente, licencias, contratos, operadores, despliegue y wiring con /agente. Las cifras de tests/84 rutas son declaradas en README y no reejecutadas durante esta guía.

## Ruta de lectura y ejecución
1. [01-INVENTARIO-Y-ESTADO.md](01-INVENTARIO-Y-ESTADO.md): qué existe y qué no.
2. [02-CUENTAS-Y-SERVICIOS.md](02-CUENTAS-Y-SERVICIOS.md): dónde entrar, qué contratar o reutilizar y cuándo.
3. [03-SECRETOS-Y-CONFIGURACION.md](03-SECRETOS-Y-CONFIGURACION.md): variables existentes, archivos privados, claves, permisos.
4. [04-INSTALACION-Y-ENTORNOS.md](04-INSTALACION-Y-ENTORNOS.md): workstation, laboratorio, staging y producción.
5. [05-INTEGRACIONES-Y-AGENTES.md](05-INTEGRACIONES-Y-AGENTES.md): GitHub, AgntiaPro, scanners y proveedores.
6. [06-OPERACION-LEGAL-Y-CLIENTES.md](06-OPERACION-LEGAL-Y-CLIENTES.md): roles, autorizaciones, privacidad, soporte, costes.
7. [07-PLAN-DE-TRABAJO-Y-CHECKLIST.md](07-PLAN-DE-TRABAJO-Y-CHECKLIST.md): secuencia ejecutable con tareas founder/agente y gates.
8. [08-PROMPT-PARA-EL-AGENTE.md](08-PROMPT-PARA-EL-AGENTE.md): instrucciones para empezar sin rehacer desarrollo.
9. [09-PLANTILLAS-Y-DECISIONES.md](09-PLANTILLAS-Y-DECISIONES.md): registros reutilizables.

## Regla principal
**No crear cuentas ni contratar servicios hasta que la necesidad esté identificada.** El agente audita y prepara, el founder decide y autoriza. No se piden ni registran secretos en documentación. Ningún cambio en main, /agente, infraestructura real, cliente o despliegue se realiza sin aprobación explícita. La rama es documental.

## Primera acción
Dar al agente el archivo 08; pedir inventario vivo con comandos, archivos, pruebas y blockers. El founder solo necesita resolver las decisiones F01–F04 del tablero inicial, no 15 servicios simultáneamente.
