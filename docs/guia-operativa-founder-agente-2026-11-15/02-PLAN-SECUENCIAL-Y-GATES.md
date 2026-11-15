# 02 — Programa diferencial secuencial (founder + agente)
**No repetir C01–C18 sin comparar implementación y evidencia.** Cada campaña se realiza en rama de código independiente, PR y reporte `REPORT.md` con SHA, archivos, comandos, tests, riesgo, rollback, coste y siguiente gate. Los gates P0 son bloqueantes.

## Fase A — Baseline y reproducibilidad (A01–A03)
### A01 · Inventario y reconciliación
**Agente:** fijar SHA de main/advlab, listar 125 paths, agrupar por paquete/contrato/test/doc; comparar con C01–C18 y status 42 fases. **Founder:** confirmar alcance. **Aceptación:** matriz `existente / probado / no probado / bloqueado / faltante` con referencia exacta por archivo; sin duplicados.
### A02 · CI independiente
**Agente:** instalación reproducible en entorno desechable sin secretos, ejecutar unittest, releasecheck, boundary, validador middleware, SDK y tests relevantes; guardar logs. **Aceptación:** resultados por suite y SHA; no confundir reportes históricos con rerun.
### A03 · Threat model y autoridad
**Agente:** DFD de trust boundaries, rutas de datos, ejecución, claves, egress, proveedores, identidad, aprobaciones y recuperación; STRIDE/abuse cases. **Founder:** firma alcance y niveles de riesgo. **Aceptación:** amenazas P0 con test negativo asignado.

## Fase B — Cerrar seguridad bloqueante (B01–B05)
### B01 · Vault y rutas
**Agente:** ID validators, rutas confinadas, no symlink traversal, escrituras atómicas y permisos; tests tenantA/B y rutas hostiles. **Aceptación:** ningún acceso fuera de root; rechazo fail-closed; evidencia de test.
### B02 · Custodia criptográfica
**Agente:** envelope por tenant, KMS/secret ref, AAD tenant+evidence+schema, key version, rotación, restauración, expiración/retención; pruebas de swap y restore. **Founder:** elige proveedor de claves. **Aceptación:** aislamiento criptográfico, sin claves en Git/logs.
### B03 · OCI ejecutado realmente
**Agente:** runner en host efímero, rootless/userns cuando viable, seccomp, no-new-privileges, cgroups, read-only, egress none, montajes mínimos, timeouts, kill y cleanup; probar ataques negativos seguros. **Founder:** autoriza host de laboratorio. **Aceptación:** no lectura de host/secretos, no red, límites de recursos, cancelación real, logs y versión del runtime. Si no hay host, BLOCKED.
### B04 · Broker y revocación
**Agente:** manifest de tools, scope por tenant/asset, TTL, presupuesto, cancelación en vuelo, receipts, idempotencia, límites de output, sin shell libre. **Aceptación:** intento fuera de scope denegado; revocación efectiva antes del efecto.
### B05 · Release gate de verdad
**Agente:** pip-audit real, SBOM verificable, dependencias pinneadas, provenance, firma/attestation, branch protection; `audit BLOCKED` no puede dar `release_eligible=true`. **Aceptación:** CI fail-closed ante auditoría ausente y prueba de vulnerabilidad conocida en fixture.

## Fase C — Proveedores y herramientas (C01–C04)
### C01 · Primer proveedor de agente
**Founder:** escoger solo uno entre Codex vía interfaz verificable, Cline u otro con API/CLI documentada. **Agente:** capability discovery, auth desde secret broker, límites, cancelación, salida estructurada, dry-run, tests de contrato. **Aceptación:** una misión sintética con evidencia real del provider; no anunciar disponibilidad de otros.
### C02 · Segunda implementación comparable
Misma misión, mismo oráculo y presupuesto; comparar calidad, coste, latencia y reproducibilidad. **Aceptación:** reportes comparables y límites.
### C03 · Herramientas OSS por necesidad
Instalar en contenedor pinneado primero Semgrep/OSV/Syft; después Schemathesis/ZAP para APIs propias de prueba; PyRIT/garak solo cuando haya modelo autorizado. **Aceptación:** version, licencia, capability probe, output parseado, 1 caso positivo y 1 negativo; `BLOCKED` si falta binario.
### C04 · Biblioteca de misiones
Versionar más misiones con asset scope, engagement, oráculo, impacto, budget, cleanup y retest. **Aceptación:** cobertura explícita y no inferir seguridad por 0 hallazgos.

## Fase D — Operación diaria sintética y staging (D01–D03)
### D01 · Scheduler durable
Cron/work queue con leases, fencing, idempotency, DLQ, retries, presupuesto por tenant, dedup y ventanas; restart/crash tests.
### D02 · Observabilidad y alertas
OTel/logs redactados, SLIs, fallo de herramienta, coste, evidencia incompleta, cancelación, kill switch; alertas a responsable real.
### D03 · Recuperación
Backup/restore del ledger y vault, rotación, disaster exercise, auditoría de accesos; medir RTO/RPO sin inventar.

## Fase E — Integración padre y primer cliente (E01–E04)
### E01 · SDK/bridge con `/agente`
Contrato versionado, identity binding, tenant isolation, Pedro como agente visible, approvals humanas, event bus y audit; no duplicar runtime.
### E02 · Piloto interno dos tenants
Solo assets propios, alcance firmado por founder, gemelos/staging, pruebas de cruce tenant, reportes, presupuesto y retest.
### E03 · Preparación comercial/regulatoria
Engagement/ROE por activo y horario, DPA cuando aplique, privacidad, licencias OSS, incident response, responsabilidad, retención y custodia; revisión profesional donde corresponda.
### E04 · Go/no-go del primer cliente
Auditoría independiente, matriz de riesgos residuales, autorización escrita y plan de rollback. Inicio pasivo/de bajo impacto. Sin aprobación founder: NO-GO.

## Dependencias y límites
A01→A02→A03→B01/B02/B03/B04/B05→C01→C02/C03/C04→D01/D02/D03→E01/E02/E03→E04. B03 y B05 bloquean ejecución no confiable o release productivo. No ejecutar herramientas activas fuera de laboratorio autorizado.
