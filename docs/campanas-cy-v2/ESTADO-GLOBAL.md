# CY-V2 — Estado global de ejecución

**Actualizado:** 2026-11-15. **SHA de `main`:** `b2cea46bd03e1eafec2f31eff96db1a07890a23c`.
**Rama activa:** `feat/cy-v2-01-baseline`. **Producto:** demo sintética, `production_enabled=false`.

## Situación

| Campaña | Estado | Evidencia |
|---|---|---|
| CY-V2-01 Baseline y reconciliación | NOT_VERIFIED (local PASS) | [BASELINE.md](BASELINE.md) · [reporte](reportes/CY-V2-01-REPORT.md) |
| CY-V2-02 Auth adversarial y tenancy | NOT_STARTED | — |
| CY-V2-03 RequestBoundary y sandbox | NOT_STARTED | — |
| CY-V2-04 Scanners y coverage truth | NOT_STARTED | — |
| CY-V2-05 Jobs durables y replay | NOT_STARTED | — |
| CY-V2-06 Evidencia, cifrado y restore | NOT_STARTED | — |
| CY-V2-07 Gateway de agentes y MCP | NOT_STARTED | — |
| CY-V2-08 SDK, outbox y contrato padre | NOT_STARTED | — |
| CY-V2-09..14 Asset & Exposure | NOT_STARTED | — |
| CY-V2-15..21 Threat Intel & Detection | NOT_STARTED | — |
| CY-V2-22..28 AI Security & Fraud | NOT_STARTED | — |
| CY-V2-29..35 Response & Remediation | NOT_STARTED | — |
| CY-V2-36..42 Enterprise Delivery | NOT_STARTED | — |

## Baseline reproducible

```bash
python -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/python -m unittest discover -s tests       # 190 tests, 8 skipped
(cd typescript && npm ci && npm test)                 # 6 pass, 1 skip
.venv/bin/python scripts/validate_foundation.py       # PASS
```

## CI de la rama

SHA `0b8dd9d`: 6/6 workflows completados sin fallos. Sin PR: el conector GitHub responde 403 al
crear pull requests; el compare manual es
`https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad/compare/main...feat/cy-v2-01-baseline`.

## Riesgos críticos abiertos

- Sin CI ejecutada para la rama y sin revisión independiente.
- Tests Docker/escáneres reales opt-in, no ejecutados.
- Autenticación y aislamiento tenant pendientes de matriz adversarial (CY-V2-02).

## Próxima acción

Abrir el PR de CY-V2-01 y dejar que CI valide el SHA; después iniciar CY-V2-02 con la matriz
principal/actor/tenant/grant/revocación por endpoint.
