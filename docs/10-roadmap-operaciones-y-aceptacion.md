# 10 · Roadmap, operaciones y criterios de aceptación

Estado: planificación inicial. No hay escáneres instalados, tests de seguridad ejecutados, agentes conectados, tráfico de clientes inspeccionado ni servicio de producción. Las comprobaciones documentales no acreditan protección.

## Entregas incrementales

| Fase | Resultado | Gate de salida |
|---|---|---|
| C0 Investigación/documentación | README, fuentes, arquitectura, presupuesto y backlog | Fuentes trazables, enlaces/JSON válidos, límites explícitos |
| C1 Identidad/scopes/evidencia | Core API y modelos, autorización de activos, auditoría | Cross-tenant, revocación, entrada inválida y datos minimizados |
| C2 Snapshot y AppSec | Gitleaks/OSV/Semgrep y parser robusto | Fixture benigno/vulnerable, error de scanner, sin ejecutar código analizado |
| C3 Jobs/reportes | Estados, idempotencia, reservas y reportes | Crash/replay/cancelación, evidencia/cobertura reproducible |
| C4 Gateway agéntico | Políticas de acción, egress, tools/skills versionadas | Ataques sintéticos bloqueados fuera del modelo y tareas legítimas útiles |
| C5 Evaluación IA | AgentDojo/casos propios, utilidad/seguridad | Protocolos, versiones, coste y casos excluidos; sin porcentajes inventados |
| C6 API/web/cloud | Perfiles pasivos y activos autorizados | Laboratorio, scope DNS/redirect, rate limits y no fuga |
| C7 Privacidad/GRC/antifraude | Aplicabilidad y expedientes con revisión | Fuentes/fecha/rol, datos faltantes y plazos diferenciados |
| C8 Runtime/operación | Conectores de eventos, recuperación y piloto | Backups/restauración, observabilidad, secretos y runbooks probados |
| C9 Integración AgntiaPro | SDK/UI/tools/event bus | Patchset concreto y aprobación para `/agente`, E2E de dos tenants |

No activar todas las herramientas de catálogo para considerar terminada C2. Priorizar un recorrido completo y barato; ampliar con fixtures y evidencia. El presupuesto se mide en cada fase y reduce alcance si no cabe.

## Demo mínima objetivo

Dos tenants sintéticos, dos repos fixture y dos agentes con scopes diferentes. Una dependencia vulnerable y un secreto canario generan findings sin exfiltrar el valor. Un documento contiene instrucciones adversariales sintéticas y el agente intenta una salida fuera de scope: el gateway la deniega. Otro caso benigno termina correctamente. Un humano revisa el reporte y una propuesta de parche en una rama de laboratorio; retest comprueba el cambio. Nada toca infraestructura real de terceros.

## Pruebas críticas futuras

- Acceso cruzado a activos/findings/documentos/eventos denegado sin revelar existencia.
- Scope caducado, worker antiguo, rol revocado y manifest cambiado bloqueados.
- Misma idempotency_key/payload conserva resultado; payload diferente produce conflicto.
- Costes concurrentes no superan reservas; proveedor sin hard cap excluido o margen documentado.
- Repo malicioso con hooks/postinstall no se ejecuta en host; sandbox sin credenciales ni socket Docker.
- Secretos centinela ausentes de reportes/logs/prompts; redacción y cifrado con recuperación probada.
- SSRF/link-local/metadata/redirect y objetivos fuera de autorización bloqueados.
- Timeout tras efecto real produce reconciliación; no parche ni cambio de IAM duplicados.
- DB/advisories obsoletos y scan parcial se muestran como tales; parser failure no es clean.
- Kill switch comprobado en todos los caminos de herramientas; operaciones ya en vuelo se identifican.

## Operación y límites humanos

Antes del piloto: canal privado de incidentes, responsable on-call según contrato, nivel de cobertura, backups y restauración, registro de proveedores/DPA, TLS/redes, versiones y política de actualizaciones. Un PC apagado o un worker on-demand no ofrece observación continua. No vender24/7 por disponer de un cron.

Métricas: cobertura por activo/perfil, lag y drops, versión de DB/reglas, findings confirmados, FP/FN conocidos, tiempo de triage/retest, latencia p50/p95, presupuesto reservado/consumido y tareas diferidas. Las tasas solo se calculan con denominador/periodo/suite explícitos. Un benchmark de paper no se pega en la ficha comercial como cifra propia.

Incident response: detectar → corroborar → delimitar tenant/activo/datos → preservar evidencia → proponer contención → aprobar/ejecutar si autorizado → recuperar → retest → revisión legal/postmortem. No borrar ficheros o logs automáticamente para «limpiar» una infección. Los reportes regulatorios son expedientes para decisión humana, no se envían por la existencia de un finding.

Actualizaciones: releases/digests verificados, changelog, canary y rollback. Una vulnerabilidad de scanner/feed puede comprometer al auditor; monitorizar componentes propios y separar trust roots. Mantener el inventario real de herramientas, no el catálogo aspiracional.

## Definición de terminado

Se entrega una capacidad cuando hay contrato, autorización, ejecución real dentro de scope, resultado reproducible, tratamiento de errores/recovery, evidencia minimizada, coste medido, interfaz revisable y pruebas ejecutadas. Debe declarar exclusiones y responsable. Una fuente estudiada, un addon instalado o un dashboard bonito no satisfacen esa definición.

Esta edición solo cierra la fundación documental C0 en el alcance verificable. C1–C9 están pendientes. No contratar servicios, fusionar código de otros proyectos o desplegar por interpretar una hoja de ruta como autorización operativa.
