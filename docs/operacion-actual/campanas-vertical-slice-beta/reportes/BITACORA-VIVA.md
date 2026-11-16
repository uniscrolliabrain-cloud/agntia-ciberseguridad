# Bitácora viva — programa VS-CY

Registro acumulativo. Cada entrada se escribe al cerrar una campaña y no se reescribe: las
correcciones se añaden como entrada nueva.

## VS-00 — Baseline y trazabilidad · 2026-11-16

- **Base:** `2da922f`. **Rama:** `feat/cyber-vs-00-baseline`. **PR:** #14.
- **Medido:** 196 tests middleware OK (8 skipped), 117 laboratorio, 6/7 SDK; 88 decoradores de ruta,
  278 archivos Python, 23 ramas, 7 workflows.
- **Defecto corregido:** `CyberError` usaba parameter properties y rompía el contract test en Node 26.
- **Gates:** G0 PASS; G2–G5 PARTIAL; G6/G7 BLOCKED; G8 NO-GO.
- **Pendiente:** revisión independiente.

## VS-01 — Contratos del slice · 2026-11-16

- **Base:** `2da922f`. **Rama:** `feat/cyber-vs-01-contracts`. **PR:** #15.
- **Resultado:** seis de ocho contratos existen con otro nombre; idempotencia ya implementada por
  cabecera; dos contratos sin esquema versionado (`AuditEventV1`, `RetestRequestV1`).
- **Corregido después:** el hallazgo sobre `finding_id` estaba invertido (ver VS-01A).

## VS-01A — Corrección de impacto · 2026-11-16

- **Rama:** `feat/cyber-vs-01a-finding-contract`. **PR:** #16.
- **Hecho:** `Finding` alineado con la proyección real (`Hash` de 64, `risk`, `context`,
  `exception`) y prueba sobre un finding escaneado. `RemediationPlan.finding_id: Hash` era correcto.
- **Acotado:** `causation_id = correlation_id` es inconsistencia semántica sin consumidor; no
  vulnerabilidad. Delta propuesto: cabecera opcional `X-Causation-Id`.
- **Verificación:** 197 tests OK (8 skipped); validador PASS.

## VS-02 — Herramientas reales en CI · 2026-11-16 · PASS sintético

- **Evidencia:** run **43982858508**, job `docker-contracts` `133703454341`, **success**.
- **Ejecutado:** Gitleaks (canario pese a supresión del repo), OSV (vulnerable/limpio/caducado/ausente),
  Semgrep (eval con `nosemgrep`), Trivy (DS-0002) y sandbox (UID, red, timeout, PIDs, limpieza).
- **Límites:** solo fixtures; digests resueltos en build y publicados como artefacto, no fijados en
  el repo; sin feeds en vivo ni licencias.
- **Gates:** G2 y G3 pasan en sintético; auditoría externa sigue pendiente.
- **Informe:** `VS-02-REPORT.md`.

## VS-03 — Secretos · no iniciada

- **Puede ejecutarse en autónomo:** adaptadores e interfaz con backend falso; no la revocación real.
- **Bloqueo:** cuenta de gestor de secretos y valores; los aporta el founder.
- **Criterio de cierre:** interfaz `SecretStore`, adaptador de fichero para tests, pruebas de
  revocación/idempotencia, y `BLOCKED` explícito para el backend real.

## Cola y dependencias

| Campaña | Carril | Bloqueo |
|---|---|---|
| VS-02 | autónomo (CI) | ninguno técnico; requiere push del workflow |
| VS-03 | autónomo parcial | gestor real y credenciales |
| VS-04 custodia/KMS | autónomo parcial | proveedor y clave |
| VS-05+ endurecimiento | autónomo | revisión de contrato |
| `/agente` | founder | autorización expresa |
| Activos propios / ROE | founder | inventario y permiso |
| Beta / cliente | founder | despliegue y aceptación |
| Revisión independiente | externo | revisor |

## Reanudación

1. Leer esta bitácora y `docs/ESTADO-VIGENTE.md`.
2. Revisar PR #14, #15 y #16; no fusionar sin revisión.
3. Empezar por VS-02 en CI, que no depende de decisiones del founder.
4. No marcar PASS sin receipt de CI o comando local con exit 0.
