# 02 — Matriz diferencial de cierre a producción

**Regla:** esto es una matriz de **verificación y cierre**, no una declaración de que todas las filas exigen código nuevo. Antes de programar, comprobar el HEAD, los informes y las pruebas existentes. Prioridad P0 bloquea piloto real; P1 bloquea cliente; P2 amplía cobertura.

| ID | Prioridad | Superficie | Hecho comprobado o reportado | Cierre mínimo y evidencia de aceptación | Responsable |
|---|---|---|---|---|---|
| CP-01 | P0 | Baseline | Docs anteriores mezclan SHAs y programas | Inventario de HEAD, árbol, ramas, SHA, pruebas y reporte de contradicciones | Agente |
| CP-02 | P0 | Runtime OCI | Adaptador existe; ejecución real BLOCKED | Digest fijado, red desactivada, límites, test OCI real y escape/denegación registrados | Agente + host founder |
| CP-03 | P0 | Herramientas | Siete herramientas del laboratorio BLOCKED en informe C | Instalar solo las necesarias para el piloto, fijar versiones/feeds, fixtures positivos y negativos, receipts | Agente |
| CP-04 | P0 | Secrets | Claves internas locales; externos sin proveedor verificado | Referencias a Doppler u otro gestor, scopes mínimos, no-logs, rotación y revocación probadas | Founder + agente |
| CP-05 | P0 | Release | `--production` falla cerrado por audit/atestación | pip-audit real, SBOM reproducible, procedencia/atestación acordada; gate mantiene FAIL si falta | Agente |
| CP-06 | P0 | Vault y backup | HKDF/AES-GCM, backup SQLite+vault local; master key en host | Custodia de clave, almacenamiento externo, cifrado, restore completo con pérdida de host simulada | Founder + agente |
| CP-07 | P0 | Auth/tenancy | Revisión lógica y tests negativos previos | Revisión independiente de todas las rutas, principal/tenant/grants, cross-tenant, revocación, tokens expirados | Revisor |
| CP-08 | P0 | Broker/worker | Leases, fencing y dedupe reportados; cancelación en vuelo no cerrada | Test multiproceso, kill switch efectivo, timeouts y retry sin duplicar efectos | Agente + revisor |
| CP-09 | P0 | Observabilidad | Planes y workflows existen | Alertas reales con destinatario, trazas redactadas, simulacro de incidente y evidencia | Founder + agente |
| CP-10 | P1 | Contrato /agente | SDK TS y API existen; integración no acreditada | API/SDK versionados, identidad delegada, tenant, idempotency, aprobación, correlación y E2E | Agente, con autorización founder |
| CP-11 | P1 | Piloto propio | Misiones sintéticas no equivalen a escaneo de activos | ROE interno, inventario allowlist, escaneo de propiedad, informe, remediación/retest y costes | Founder + agente |
| CP-12 | P1 | Operación legal | Plantillas y propuestas documentadas | ROE, DPA, retención, privacidad, licencia OSS/feeds, canal de divulgación y soporte aprobados | Founder + asesor |
| CP-13 | P1 | Cliente | `owner_acceptance=PENDING` | GO firmado, evidencia de CP-01…12, límites de servicio y plan de rollback | Founder |
| CP-14 | P2 | Extensiones | SOC/EDR/DAST/cloud posture y proveedores IA no equivalen a capacidad productiva | Activar solo según oferta, ROI, alcance y licencias; no bloquear piloto mínimo | Producto |

## Dependencias y orden

- **Wave 0 — Inventario:** CP-01. No crear nuevos tickets de implementación hasta clasificar `YA IMPLEMENTADO / NECESITA INTEGRACIÓN / FALTA / BLOQUEADO / FUERA DE ALCANCE`.
- **Wave 1 — Entorno sintético:** CP-02, CP-03, CP-04, CP-05. Reutilizar Codespaces/Actions para CI, pero no afirmar aislamiento OCI sin ejecución verificada.
- **Wave 2 — Custodia y control:** CP-06, CP-07, CP-08, CP-09. Revisión independiente obligatoria para hallazgos críticos.
- **Wave 3 — Vertical interna:** CP-10 y CP-11. No tocar `/agente` sin autorización separada y patchset revisable.
- **Wave 4 — Cliente:** CP-12 y CP-13. CP-14 es posterior y no forma parte del mínimo.

## Formato obligatorio por gate

`ID | SHA | entorno | comando | exit | evidencia/ruta | hallazgo | estado | owner | dependencia | rollback`.

Estados válidos: `PASS` (verificado en entorno objetivo), `PARTIAL` (parte demostrada), `BLOCKED` (dependencia explícita), `NOT_VERIFIED`, `N/A` (justificado). Nunca transformar un `BLOCKED` en `PASS` por disponibilidad de código.

## Criterio GO/NO-GO

- **GO laboratorio sintético:** CP-01 a CP-09 resueltos para el alcance seleccionado, o excepción documentada que no comprometa aislamiento, secretos, custodia ni seguridad.
- **GO piloto propio:** laboratorio GO, CP-10 y CP-11 completos, autorización del owner.
- **GO primer cliente:** piloto propio GO, CP-12, revisión independiente y CP-13 firmados; `docs/release/status.json` y gates actualizados mediante ejecución real, no edición cosmética.

Ningún GO se concede automáticamente por esta documentación.
