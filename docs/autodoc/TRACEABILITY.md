# Trazabilidad de afirmaciones — AD-01

Cada afirmación pública del producto debe poder rastrearse hasta código, test o ejecución. Este
mapa fija el estado **real** a `dd18f2a`, sin elevar gates.

| # | Afirmación | Evidencia | Estado |
|---|---|---|---|
| 1 | El servicio expone API multi-tenant | 84 rutas `/v1/tenants/{tenant}/…`; `tests/security` y `tests/contracts` | PASS local |
| 2 | Las rutas no publican ni despliegan | Cero coincidencias `publish`/`deploy` en rutas; test AD-01 | PASS local |
| 3 | El esquema SQLite está en versión 8 | `MIGRATIONS` con 8 entradas; `CURRENT_SCHEMA=8`; test AD-01 | PASS local |
| 4 | La auditoría es append-only con hash encadenado | `storage.py`, `tests/security/test_audit_chain.py` | PASS local |
| 5 | Las evidencias se cifran con AES-GCM y límite 2 MiB | `evidence/vault.py`; tests de evidencia | PASS local |
| 6 | El outbox es local y no hay bus remoto | `events/outbox.py`; `SyntheticConsumer`; tests | PASS local |
| 7 | El worker tiene lease/fence y reconciliación | `jobs/worker.py`; tests de jobs | PASS local |
| 8 | El gateway de agentes no tiene egress habilitado | `agents/flows.py`; evaluación sintética | PASS local |
| 9 | La evaluación de agentes es sintética, no benchmark real | `scripts/evaluate_agent_gateway.py`; sin proveedor | PASS local (limitado) |
| 10 | El SDK TS es privado y no está integrado en el padre | `typescript/package.json`; 6 tests; sin dependencia en `/agente` | PASS local |
| 11 | El producto no está en producción | `status.json`: `production_enabled=false`; test AD-01 | PASS local |
| 12 | 2 fases PASS y 40 PARTIAL de 42 | `status.json`; `release_status.py` exit 0 | PASS local |
| 13 | La suite Python pasa completa | 190 tests, 0 fallos, 8 skips Docker | PASS local |
| 14 | El contrato Python↔TS es reproducible en Node 26 | Reparación de `build-runtime.mjs`; test de contrato OK | PASS local |
| 15 | El validador documental pasa | 164 Markdown, 31 registros, 95.245 palabras | PASS local |
| 16 | No hay revisión independiente | `independent_review=PENDING` | NOT_VERIFIED |
| 17 | No hay PR de esta campaña | Conector GitHub 403; rama pusheada sin PR | NOT_VERIFIED |
| 18 | No hay CI ejecutada sobre este SHA | Sin workflow run de AD-01 | NOT_VERIFIED |
| 19 | Los escáneres reales funcionan | 8 tests Docker skipped | NOT_RUN |
| 20 | Cobertura de los 10 dominios del Concept Master | 5 de 10, ver `docs/campanas-cy-v2/ALINEACION-CONCEPT-MASTER.md` | PARTIAL |

## Regla de uso

- Un `PASS local` significa: ejecutado en esta máquina, con este SHA, con salida y código de salida
  registrados. No significa auditado por terceros.
- `NOT_VERIFIED` no se convierte en PASS por paso del tiempo ni por documentación.
- `NOT_RUN` (Docker, red, clientes reales) se declara siempre; nunca se omite del reporte.
