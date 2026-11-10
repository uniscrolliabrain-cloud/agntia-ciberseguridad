# Campaña maestra · Agntia Ciberseguridad en siete días

Fecha de diseño: 2026-11-10. Repo: `uniscrolliabrain-cloud/agntia-ciberseguridad`. Estado: **campaña preparada, implementación NO ejecutada**. Esta publicación añade documentación y validadores; no implementa un SOC, API runtime o defensa activa por el hecho de describirlos.

## Mandato y resultado

Construir un middleware defensivo conectado a AgntiaPro mediante contratos servidor, usando herramientas OSS y conectores opcionales. El cliente debe poder saber qué activos están cubiertos, qué evidencia existe, qué riesgos se confirmaron, qué datos faltan y qué corrección puede autorizar. Los agentes trabajan bajo identidad/capacidades reales; no elevan permisos por texto o personalidad.

Objetivo de la semana: un **piloto verificable dentro de un alcance pequeño**, con aislamiento, auditoría real de fixtures, policy gateway, observabilidad, reportes y límites económicos. El nivel de ingeniería se inspira en actores líderes: evidencia reproducible, mínimo privilegio, recuperación, trazabilidad, cobertura explícita y utilidad. No prometemos igualar en siete días la telemetría global, sensores, soporte24/7, personal o certificaciones de empresas con años de inversión.

La [matriz de referencia](09-calidad-y-comparacion-con-lideres.md) define qué significa esa ambición y qué permanece diferido. No ocultar exclusiones para vender paridad. Un scope piloto bien resuelto vale más que31 wrappers sin aislamiento.

## Tamaño y artefactos

- **7 jornadas**, fechas orientativas10–16nov2026 si ese esT0.
- **42 fases**, seis por jornada.
- **294 microtareas**, siete por fase, con IDs estables.
- **84 escenarios de gate**, dos por fase, inicialmente NOT_EXECUTED.
- DAG de dependencias y estado en [campaign.json](campaign.json).
- Evidencias/estado en [evidence](evidence/README.md), sin logs privados.

El calendario no es una estimación de horas validada. Requiere capacidad de trabajo por roles funcionales y herramientas disponibles. No se ha contratado personal ni creado subagentes. Si la capacidad real no permite los gates, se reduce M1, se conserva el avance y se recalendariza; no se añaden horas ficticias ni se rebajan controles.

## Secuencia

| Día | Foco | Resultado observable |
|---|---|---|
| [1](01-dia-1.md) | Base, identidad y autorización | Dos tenants/grants, API y datos con fronteras probadas |
| [2](02-dia-2.md) | Adquisición, sandbox, AppSec | Snapshots sin ejecución y tres adaptadores reales; Trivy opcional |
| [3](03-dia-3.md) | Jobs, findings y evidencia | Vertical reproducible hasta reporte con revisión |
| [4](04-dia-4.md) | Observabilidad | Trazas/métricas/logs seguros, cobertura y fallos visibles |
| [5](05-dia-5.md) | Seguridad agéntica | Tools versionadas, política determinista, egress y revocación |
| [6](06-dia-6.md) | Legal, privacidad, respuesta y coste | Aplicabilidad revisable, caps; fraude/IR/fixes según gates |
| [7](07-dia-7.md) | Contratos, E2E y entrega | SDK/piloto, recuperación, empaquetado y founder report |

## Prioridades y dependencia

**M0**: necesario para el alcance piloto que se prometa. **M1**: ampliación que puede quedar explícitamente diferida. Las M1 no superadas no se cuentan como funciones disponibles. Ningún tier puede quitar aislamiento, autorización, secretos, audit o aprobación para reducir coste. Una dependencia fallida bloquea a sus consumidores; otro track independiente puede continuar.

`campaign.json` enlaza fases y primeras tareas a los últimos pasos de sus dependencias. Las herramientas AppSec independientes pueden integrarse después del runner/snapshot sin esperar entre sí. El revisor comprueba la composición antes de habilitar un recorrido. Las rutas de archivos del plan son entregables futuros, no evidencia de código existente.

## Invariantes operativos

1. Scope de activos/grants válido antes de cada operación y job; nunca dominio/IP libres escritos por un agente.
2. Principal/tenant/capacidad verificados en servidor; no fallback owner ni acceso cruzado por IDs conocidos.
3. Código, logs, documentos, tools/skills y resultados LLM son datos no confiables; no ejecutarlos en host.
4. Scanners fijados, sandbox con recursos/red mínimos y sin socket Docker/credenciales globales.
5. Propuestas con diff/hash/objetivo/coste/TTL; aprobación humana según efecto y sin autoaprobación agéntica.
6. Idempotencia y reserva antes del efecto; timeout implica conciliación, no otro create/cambio.
7. Secretos fuera de reportes/logs/prompts y custodia cifrada con recuperación probada.
8. Métricas de seguridad y utilidad juntas; nadie convierte una tarea no hecha en ataque correctamente rechazado.
9. Fuentes/versiones legales y evidencia revisable; no certificado AI Act/RGPD automático.
10. No compras, phishing real, pruebas destructivas, terceros no autorizados, despliegue o cambios en `/agente` por esta campaña documental.

La implementación del middleware puede prepararse en ramas/laboratorio autorizado. El wiring del repo madre y efectos sensibles de producción conservan sus aprobaciones específicas. No pedir autorizaciones repetidas para tareas reversibles ya permitidas; sí presentar un resultado concreto antes de una aprobación necesaria.

## Presupuestos

Mantener [plans.json](../../../config/plans.json): Lite30€, L70€, XL300€ mensuales como coste técnico por workspace piloto bajo la hipótesis actual. Cómputo, datos, API y reservas fiscales/FX se suman; no son precios de venta ni una plantilla humana financiada. Los perfiles/SLIs se validan bajo esos límites, no se promete volumen ilimitado.

La fase económica implementará ledger, concurrencia y degradación. Hasta entonces el JSON es diseño y no debe anunciarse hard cap efectivo. No activar trials, auto-upgrades o SaaS con uso comercial/MSSP/retención sin revisar.

## Gates y parada

Cada fase exige artefacto, SHA, comandos/entorno, pruebas ejecutadas con resultados, evidencia sanitizada, límites y rollback. Mocks son válidos para contratos simulados; no acreditan instalación real del scanner o un sandbox que no estuvo disponible.

Stop inmediato de la capacidad afectada: fuga entre tenants, ejecución no autorizada, secreto expuesto, bypass del gateway, pérdida de audit/evidencia, duplicación de efecto o gasto sin reserva. Preservar el estado, abrir incidencia y resolver antes de avanzar. Una revisión independiente debe poder demostrar el comportamiento, no limitarse a leer un test.

Día7 puede terminar en BLOCKED o demo parcial. La fecha no cambia la clasificación: documental, demo, piloto o producción requieren sus propios gates. No se habilita producción automáticamente por aprobar un laboratorio.

## Definition of Done del piloto

Dos tenants, fixtures benignos/vulnerables, tools reales del alcance, jobs durables, findings con fuente/cobertura, reportes seguros, policy/egress fuera del modelo, revocación, observabilidad correlacionada, presupuesto probado, backup restaurado y paquete reproducible. El consumidor simulado del SDK debe demostrar contrato hacia AgntiaPro sin modificar `/agente`.

UI ampliada, cloud/DAST, sensores endpoint, fraude, contención y remediaciones solo se cuentan si su M1/gate se ejecutó. Cualquier diferencia se registra en [futuro30/60/90](11-continuidad-30-60-90.md). La aceptación humana se realiza sobre evidencia concreta, no sobre promesas de «ultrapro».
