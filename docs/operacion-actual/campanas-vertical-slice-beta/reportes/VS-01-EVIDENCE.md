# VS-01 — Evidencia

**Base SHA:** `2da922ff8ae33bfb0824ae2a6dcec3f3b00e1c93`

| Comprobación | Comando | Resultado |
|---|---|---|
| Contratos existentes | `grep -n "class \(AssetPublic\|Job\|Evidence\|Finding\|Approval\|GrantCreate\|AuditJobCreate\)" agntia_ciberseguridad/contracts.py agntia_ciberseguridad/jobs/contracts.py` | 7 modelos localizados con línea |
| Idempotencia real | `grep -rn "idempot" agntia_ciberseguridad --include=*.py` | `jobs/store.py` valida clave, `job_idempotency`, `request_hash`, `binding_id`, `replayed` |
| Esquema de jobs | `agntia_ciberseguridad/jobs/schema.py` | tablas `jobs`, `job_idempotency`, `job_reservations`, `job_results`; columnas `fence`, `lease_owner`, `cancel_requested`, `causation_id` |
| Retest/remediación | `grep -rln "retest" agntia_ciberseguridad --include=*.py` | `governance/remediation.py`, `reviews.py` |
| Evento de auditoría | `grep -rln "audit_event\|AuditEvent" agntia_ciberseguridad --include=*.py` | sin coincidencias: no hay contrato versionado |
| Suites | VS-00 | 196 tests middleware OK (8 skipped), 6/7 SDK, 117 laboratorio |

## Reproducir

```bash
python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/python -m unittest discover -s tests
cd typescript && npm ci && npm test
```

No se ejecutaron escaneos ni acciones sobre activos. No se usaron secretos.
