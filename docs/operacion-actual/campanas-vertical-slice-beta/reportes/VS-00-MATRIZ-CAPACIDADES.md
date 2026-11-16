# VS-00 — Matriz capacidad → símbolo → test → estado

**SHA medido:** `2da922ff8ae33bfb0824ae2a6dcec3f3b00e1c93`
Estados: `PASS` (existe y tiene test ejecutado), `PARTIAL` (existe, cobertura incompleta),
`BLOCKED` (depende de cuenta/host/autorización), `FALTA` (no existe).

| Capacidad | Símbolo / ruta real | Test existente | Estado | Nota |
|---|---|---|---|---|
| Contratos base | `agntia_ciberseguridad/contracts.py` (`AssetPublic`, `GrantCreate`, `Job`, `Evidence`, `Finding`, `Approval`) | `tests/contracts/**` | PASS | Pydantic `extra=forbid` |
| Contrato de jobs | `agntia_ciberseguridad/jobs/contracts.py` (`AuditJobCreate`, `CancelJob`) | `tests/jobs/**` | PASS | Sin `idempotencyKey` explícito; se usa revisión |
| Contrato de evidencia | `agntia_ciberseguridad/evidence/contracts.py` | `tests/evidence/**` | PASS | Subida, revisión y hold |
| SDK TypeScript | `typescript/src/{client,contracts,hono,agent-tools}.ts` | `typescript/test/*.test.mjs` | PASS | Fallo de carga corregido en VS-00 |
| Auth y principales | `agntia_ciberseguridad/auth.py`, `agents/` | `tests/security/**` | PARTIAL | 2/42 fases PASS; revisión ruta a ruta pendiente |
| Tenancy | consultas y contratos con `tenant_id` | tests de aislamiento | PARTIAL | Falta prueba E2E con identidad real |
| Assets y grants | `contracts.py`, `service.py` | `tests/**` | PARTIAL | Grants con ventana y coste; aprobación existe como modelo |
| Jobs y estados | `jobs/`, máquina de estados | `tests/jobs/**` | PARTIAL | Idempotencia por revisión; cancelación en vuelo no cerrada |
| Evidencia middleware | `evidence/`, `storage.py` | `tests/evidence/**` | PARTIAL | Custodia/KMS externos pendientes |
| Findings y reportes | `findings/`, `reports.py` | `tests/**` | PARTIAL | Normalización y priorización parciales |
| Escáneres | `adapters/{gitleaks,osv,semgrep,trivy}.py`, `runners/` | `tests/**` | BLOCKED | Binarios y feeds reales no verificados aquí |
| OCI | `adversarial_lab/.../execution/oci.py` | `tests/security/test_oci.py`, job CI | PARTIAL | Job CI real pasó; host dedicado pendiente |
| Vault y claves | `adversarial_lab/.../evidence/{vault,paths}.py`, `keys.py` | `tests/security/test_vault_hardening.py` | PASS | HKDF por tenant, AAD, escritura atómica |
| Backup/restore | `adversarial_lab/.../store/backup.py` | `tests/integration/test_backup_restore.py` | PASS | Local verificado; storage externo pendiente |
| Leases y fencing | `adversarial_lab/.../planning/leases.py` | `tests/integration/test_leases.py` | PASS | Multiproceso real pendiente |
| Release gate | `adversarial_lab/scripts/releasecheck.py` | `tests/integration/test_release_gate.py` | PARTIAL | `--production` falla cerrado; falta `pip-audit`/atestación |
| Observabilidad | `telemetry/`, `observability_routes.py` | `tests/**` | PARTIAL | Sin alertas reales ni receptor |
| Integración `/agente` | — | — | BLOCKED | Requiere autorización y patchset separado |
| Dogfooding propio | — | — | BLOCKED | Falta ROE e inventario de activos |
| Beta interna | — | — | BLOCKED | Review independiente + aceptación founder |

## Deltas priorizados para VS-01+

1. Añadir `idempotencyKey`, `causationId`, `expiresAt` al contrato de job **solo tras** mapear los
   campos existentes y su persistencia.
2. Definir `AuditEventV1` (hoy no hay contrato de evento de auditoría versionado).
3. Definir `RetestRequestV1` enlazado a `FindingV1`.
4. Cerrar el conteo real de rutas y su matriz principal→tenant→capacidad.
