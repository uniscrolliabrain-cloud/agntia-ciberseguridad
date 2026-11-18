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

## Simulación del job de CI en venv limpio

Mismos comandos que `dependency-audit.yml`, ejecutados en `/tmp/audit-venv` (sin Docker, sin caché
previa):

```
$ python3 -m venv /tmp/audit-venv
$ /tmp/audit-venv/bin/python -m pip install --upgrade pip
$ /tmp/audit-venv/bin/python -m pip install -e '.[dev]'
$ /tmp/audit-venv/bin/python -m pip install 'pip-audit==2.10.1'
$ /tmp/audit-venv/bin/python -m pip_audit --local --progress-spinner off
CI_LOCAL=0
$ /tmp/audit-venv/bin/python -m pip_audit . --progress-spinner off
No known vulnerabilities found
CI_PROJECT=0
```

## El gate tiene dientes

Con el pin anterior, el mismo auditor falla:

```
$ printf 'opentelemetry-api==1.38.0\n' > /tmp/old-req.txt
$ /tmp/audit-venv/bin/python -m pip_audit -r /tmp/old-req.txt --progress-spinner off
Found 2 known vulnerabilities in 1 package
opentelemetry-api 1.38.0 CVE-2026-114603 1.45.1
opentelemetry-api 1.38.0 CVE-2026-126360 1.45.2
OLD_PIN_EXIT=1
```

## Artefacto de release con las dependencias nuevas

Sobre el commit `5c12bbd` (árbol limpio):

```
$ python scripts/release_bundle.py --output dist/release
{"release_bundle": "PASS", "source_commit": "5c12bbd1337c669e98afb1cb449065012ab6fdea",
 "wheels": 39, "installed_artifact_smoke": "PASS", "production_accepted": false}
BUNDLE=0
$ python scripts/release_bundle.py --verify dist/release
{"bundle_integrity": "PASS", "publisher_identity": "requires independent signature/attestation verification"}
BUNDLE_VERIFY=0
$ python adversarial_lab/scripts/releasecheck.py --production
"signature is lab integrity only, not external attestation"
PRODUCTION_GATE=1
```

El artefacto se construye y verifica con OTel 1.45.2, y el gate de producción **sigue fallando
cerrado**: no se relajó ningún control para quitar el bloqueo de dependencias.

## Límites de esta evidencia

- Ejecutada en el workspace del agente. Los comandos del workflow se simularon en un venv limpio,
  pero `dependency-audit.yml` **no** tiene todavía un run verde en GitHub Actions; se declara
  pendiente de CI.
- `pip-audit` consulta el feed de OSV/PyPI en el momento; un CVE publicado después no está cubierto.
- No se ejecutó `scripts/verify_observability.py` (requiere Docker, ausente aquí).
