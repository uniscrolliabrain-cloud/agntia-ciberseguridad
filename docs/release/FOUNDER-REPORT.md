# Informe al founder — cierre de campaña42 fases

Hemos construido una demo sintética de middleware defensivo con controles deterministas, evidencia y revisión humana. No es todavía un servicio de ciberseguridad productivo, un SOC24×7 ni un certificado AI Act/RGPD. El código completo se revisa en PRs draft apiladas; main no se ha fusionado automáticamente. Para otra IA: empezar por checkpoint9, su evidencia y este informe antes de tocar clientes o el repo madre.

## Capacidades comprobadas y diferencias

| Dominio | Qué puede demostrarse | Qué falta |
|---|---|---|
| Identidad/alcance | Principales de servidor, tenants, activos, consentimientos/grants revisados, revocación y política | Identidad/BFF real de AgntiaPro y aceptación independiente |
| AppSec | Snapshots acotados; Gitleaks, Semgrep, OSV y Trivy reales offline con fixtures e imágenes/reglas registradas | Cobertura real de aplicaciones de clientes, DAST/cloud/autorización de cada entorno |
| Custodia/reportes | Cifrado de evidencia, vistas minimizadas, cadena local de auditoría, review, reportes con cobertura/no probado | Anclaje externo, custodia/retención/RGPD completos y revisión contractual |
| Observabilidad | Logs/metrics scoped, collector OTLP/Prometheus sintéticos, investigación y consola | Backend/SLA operativo, sensores runtime/EDR y guardia humana |
| Agentes | Manifest/política, delegación de un uso, stop, flujos/MCP acotados y evaluación de casos permitidos/adversariales | Runtime empresarial real, egress productivo y seguridad universal de modelos |
| Cumplimiento | Inventario y aplicabilidad por régimen/fecha con pendientes y revisión humana | Dictamen profesional, cobertura territorial/sectorial y automatización legal íntegra |
| Antifraude | Señales offline de dominios/cabeceras/cambio de pago y canal previamente registrado | Sensor de correo, reputación/procedencia verificada, detector fiable de deepfakes |
| Incidentes/fixes | Casos y reconciliación; revocación interna de laboratorio; dos plantillas sintéticas con retest | Contención real de proveedor/host, propuestas Git de cliente, operadores/MDR |
| Presupuesto | Ledger EUR mensual por tenant con reserva/conciliación/freeze y tarifas revisadas | Facturas/medición/hard limits externos y coste total de infraestructura |
| Integración/UX | SDK servidor TS/Hono y tres tools de lectura; UI de revisión móvil/escritorio | Wiring autorizado en `/agente`, login/BFF final y WCAG/usabilidad formal |
| Entrega | Wheelhouse/hashes, SDK tarball, manifiesto/SBOM, smoke limpio y scripts Linux/PowerShell | Solo plataformas que CI confirme; licencia propia, aceptación y operación real pendientes |

Wiz/Palo Alto aportan graph y contexto cloud/identidades a escala que aquí no existe. CrowdStrike/SentinelOne/Microsoft/Google aportan sensores, telemetría, inteligencia, ecosistemas y equipos humanos que no se obtienen instalando estos repos OSS. Cloudflare aporta borde/red y DDoS que este proceso local no tiene. Snyk/Semgrep separan motores, reglas/comercialización y servicios: usar CE no concede todas las licencias o datos Pro. Consultar [fuentes y comparación original](../research/08-companias-y-capacidades.md); no se han vuelto a auditar todos esos productos para este cierre. Nuestro resultado útil es un núcleo acotado y revisable, no paridad global.

## Evidencia y reproducción

Antes del cierre: checkpoint8 comprobó187 casos Python distintos (179 núcleo+8 Docker), tsc/Hono/contrato HTTP, Chromium móvil/escritorio y collector. El bloque final añade3 tests de release y ejecuta instalación limpia desde artifacts por plataforma; consultar su SHA/jobs reales en [checkpoint9](../implementation/checkpoints/09-phases-41-42/REPORT.md). No sumar suites repetidas por scripts, matrices Python o demos. Windows completo/Docker Desktop/ARM no heredan el PASS Linux.

[Runbook](../operations/RUNBOOK.md) incluye wheelhouse offline, verificación del editor/manifiesto, configuración externa, imagen sin socket, scripts por SO, rotación y límites de backup/restore. [Rollback](../operations/ROLLBACK.md) conserva datos y no ofrece downgrade/reset destructivo. Release artifacts caducan; no se ha publicado paquete npm, imagen de registry o release comercial. La atestación, si CI la verifica, prueba procedencia del manifiesto; no es una auditoría ni aprobación del producto.

## Coste y estado global

Caps de diseño: Lite30€, L70€, XL300€ por tenant/workspace/mes. Ledger controla solo costes declarados y operaciones que pasan por él. No se han contratado servicios; cero llamadas pagadas de proveedor en los tests no significa coste total cero. Hosting, almacenamiento, backups, CI, impuestos, FX y trabajo humano requieren medición/factura. No hay un precio mensual productivo verificado. Las mediciones API sintéticas de checkpoint8 incluyen CPU/RSS/disco y p50/p95; no son throughput de scanners ni capacidad contractual.

El registro machine-readable incluye42 fases y294 tareas con estado real. Dos fases históricas tienen PASS; los gates restantes siguen parciales, con dependencias/aceptaciones abiertas. Llegar al final del plan no los eleva por calendario. [Estado consolidado](status.json) y [aceptación](PILOT-ACCEPTANCE.md) hacen visible qué falta. El owner tiene las decisiones de licencia/canal privado/personas/contratos y autorización separada de integración, merge y despliegue. El backlog [30/60/90](NEXT-90-DAYS.md) propone orden por gates, sin actividad ficticia ni compras implícitas.
