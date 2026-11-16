# VS-00 — Evidencia reproducible

**Base SHA:** `2da922ff8ae33bfb0824ae2a6dcec3f3b00e1c93`
**Entorno:** Linux, Python 3.12.3, Node v26.13.0, venv local `.venv`.

## Comandos y resultados

| # | Comando | Exit | Resultado |
|---|---|---|---|
| 1 | `git rev-parse HEAD` | 0 | `2da922ff8ae33bfb0824ae2a6dcec3f3b00e1c93` |
| 2 | `git branch -r \| wc -l` | 0 | 23 |
| 3 | `git ls-files '*.py' \| wc -l` | 0 | 278 |
| 4 | `git ls-files 'tests/*.py' \| wc -l` | 0 | 46 |
| 5 | `grep -rhoE '@(app\|router)\.(get\|post\|put\|patch\|delete)\(' … \| wc -l` | 0 | 88 |
| 6 | `python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'` | 0 | fastapi 0.141.1 instalado |
| 7 | `.venv/bin/python -m unittest discover -s tests` | **0** | **196 tests OK (skipped=8)** |
| 8 | `cd typescript && npm ci && npm test` | 0 | 7 tests, 6 pass, 0 fail |
| 9 | `.venv/bin/python -m unittest tests.contracts.test_python_ts` | 0 | OK tras el parche |
| 10 | `PYTHONPATH=adversarial_lab/src:adversarial_lab/tests python3 -m unittest discover …` | 0 | 117 tests OK |
| 11 | `python3 adversarial_lab/scripts/releasecheck.py` | 0 | PASS, `release_eligible=false`, audit `BLOCKED` |
| 12 | `python3 adversarial_lab/scripts/releasecheck.py --production` | 1 | FAIL cerrado (esperado) |
| 13 | `python3 adversarial_lab/scripts/verify_boundary.py` | 0 | PASS |
| 14 | `python3 scripts/validate_foundation.py` | 0 | PASS |

Los logs completos se conservan fuera de Git en `/tmp/vs00-*.log` durante la sesión. No contienen
secretos; las claves del laboratorio son locales y no se imprimen.

## Fallo reproducido antes del parche

```
FAIL: test_actual_node_client_reads_python_dtos_and_safe_errors
AssertionError: 1 != 0
SyntaxError [ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX]:
TypeScript parameter property is not supported in strip-only mode
  at typescript/build-runtime.mjs
```

Con el entorno sin dependencias, la misma suite producía 24 errores de import (`fastapi` ausente).
Eso se corrigió instalando `.[dev]`; no se contabiliza como fallo de código.

## Evidencia que no se pudo producir

- Ejecución OCI en este workspace: no hay `docker`; **sí** se ejecutó el job OCI en GitHub Actions
  en el commit `5bd2d15` (run 43735163376, success).
- Escaneo real con Gitleaks/OSV/Semgrep/Trivy: binarios no instalados aquí → `BLOCKED`, no PASS.
- Revisión independiente: `PENDING`.
