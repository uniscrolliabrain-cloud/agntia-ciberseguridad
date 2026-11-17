# VS-06B — Evidencia

**Base:** `1946f8c` · **Rama:** `docs/cyber-bitacora-viva` · entorno: `.venv` Python 3.12.

## Reproducción del fallo con 1.45.2

```
$ .venv/bin/python -m unittest tests.integration.test_telemetry.TraceTests -v
FAIL: test_persisted_trace_propagates_to_worker_and_report_link
AssertionError: 202682239420548641850572154310773230848 != 55734777246419817665641122736863237168
```

Aislamiento del SDK (1.45.2), sin código del proyecto:

```
carrier {'traceparent': '00-b63f2d9c6b1093a8a8346d6bbd380ee8-2fab197b15b403a1-03'}
api.request b63f2d9c6b1093a8a8346d6bbd380ee8 parent None
job.execute b63f2d9c6b1093a8a8346d6bbd380ee8 parent 2fab197b15b403a1
current_span in ctx valid: True
```

El SDK continúa el padre correctamente. El descarte era del servicio:

```
$ .venv/bin/python -c "…Telemetry(...).span('api.request', root=True) … current_parent()"
parent 00-4b3aef8de1149877d0fde87e09ee84a9-7bdc628a82b0c597-03 regex ok? False
```

## Tras la corrección (mismo entorno, 1.45.2)

```
$ .venv/bin/python -m unittest tests.integration.test_telemetry -v
Ran 10 tests in 1.642s
OK
```

## Auditoría de dependencias

```
$ .venv/bin/pip-audit --local --progress-spinner off   # OTel 1.45.2, pip 24.0
Found 12 known vulnerabilities in 1 package
pip 24.0 PYSEC-2026-1795 25.3 … PYSEC-2026-3721 26.2
EXIT_BEFORE=1

$ .venv/bin/pip install --upgrade pip                    # pip 26.3
$ .venv/bin/pip-audit --local --progress-spinner off
No known vulnerabilities found
EXIT_AFTER=0

$ .venv/bin/pip-audit . --progress-spinner off
No known vulnerabilities found
PROJECT_EXIT=0
```

## Suite completa

```
$ .venv/bin/python -m unittest discover -s tests
Ran 205 tests in 27.002s
OK (skipped=8)
```

## Validador documental

```
{"status": "PASS", "scope": "documentation, repository metadata and planned budget consistency only",
 "markdown_files": 272, "security_scans_executed": 0, "words": 165192}
```

## Límites de esta evidencia

- Ejecutada en el workspace del agente, no en GitHub Actions: el workflow
  `dependency-audit.yml` **no** tiene run verde todavía. Se declara pendiente de CI.
- `pip-audit` consulta el feed de OSV/PyPI en el momento; un CVE publicado después no está cubierto.
- No se ejecutó `scripts/verify_observability.py` (requiere Docker, ausente aquí).
