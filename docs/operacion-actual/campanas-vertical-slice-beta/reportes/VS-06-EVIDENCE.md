# VS-06 — Evidencia

**Base:** `008aaeb`.

```bash
python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/python -m agntia_ciberseguridad.releasecheck            # exit 0, PASS
PYTHONPATH=adversarial_lab/src .venv/bin/python adversarial_lab/scripts/releasecheck.py   # exit 0
PYTHONPATH=adversarial_lab/src .venv/bin/python adversarial_lab/scripts/releasecheck.py --production  # exit 1
.venv/bin/python scripts/release_bundle.py --output /tmp/vs06-release && .venv/bin/python scripts/release_bundle.py --verify /tmp/vs06-release
.venv/bin/python -m pip install pip-audit
.venv/bin/python -m pip_audit --local -f json                     # exit 1, 14 vulns
```

## Auditoría

| Paquete | Versión | IDs | Fix |
|---|---|---|---|
| opentelemetry-api | 1.38.0 | CVE-2026-114603, CVE-2026-126360 | 1.45.2 |
| pip | 24.0 | PYSEC-2026-1795/1796/196/2875/2876/3721 | 26.2 |

## Intento de upgrade

`pip install opentelemetry-sdk==1.45.2 opentelemetry-exporter-otlp-proto-http==1.45.2` resuelve,
pero `tests.integration.test_telemetry` falla por trace-id distinto. Revertido a 1.38.0: 24 tests de
telemetría OK y suite completa 197 OK (8 skipped).
