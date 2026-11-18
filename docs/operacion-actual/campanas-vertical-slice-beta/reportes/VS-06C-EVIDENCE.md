# VS-06C — Evidencia

**Base:** `7fdb14e` · consulta a la API de GitHub el 2026-11-17 · sin Docker · sin ejecución local del
workflow (no hay `pip-audit` de CI en este entorno, solo el local ya documentado en VS-06B).

## Workflow

Archivo en la rama: `.github/workflows/dependency-audit.yml` (añadido en `5c12bbd`, VS-06B).

```yaml
name: Dependency audit
on: [push, pull_request]
permissions:
  contents: read
jobs:
  audit:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.12'}
      - run: … pip install -e '.[dev]' … pip install 'pip-audit==2.10.1'
      - run: .audit-venv/bin/python -m pip_audit --local --progress-spinner off
      - run: .audit-venv/bin/python -m pip_audit . --progress-spinner off
```

## Runs (respuesta de la API, campos recortados)

```
workflow  .github/workflows/dependency-audit.yml   (workflow_id 421277785)
total_count 6   ·   todos con head_branch = docs/cyber-bitacora-viva

run 44084229258
  event         push
  head_branch   docs/cyber-bitacora-viva
  head_sha      7fdb14e0c4cf06db2daa486ac52eafb27a05378b
  status/concl  completed / success
  created_at    2026-11-17T12:33:18Z

run 44084241625
  event         pull_request
  head_branch   docs/cyber-bitacora-viva
  head_sha      7fdb14e0c4cf06db2daa486ac52eafb27a05378b
  status/concl  completed / success
  created_at    2026-11-17T12:33:23Z
  updated_at    2026-11-17T12:34:00Z
  run_number    6 · run_attempt 1
```

Ambos runs corresponden al **head actual** de la rama (`7fdb14e`), uno por disparador. El `push` que
los generó fue el de VS-07C: el workflow ya estaba en la rama desde VS-06B, así que los runs aparecen
como consecuencia normal del trabajo, no de una ejecución manual.

## Qué se desprende

- El job `audit` habría fallado con cualquier vulnerabilidad conocida en el conjunto declarado, porque
  `pip-audit` sale con código distinto de cero. Conclusión soportada: **0 avisos abiertos el
  2026-11-17 en Python 3.12**, verificado por un ejecutor que no es este portátil.
- No hay caché de dependencias ni `--ignore-vuln`: el workflow no tiene forma de silenciar un hallazgo.
- `permissions: contents: read` y ningún secreto: el job no puede publicar artefactos ni tocar el
  repositorio.

## Lo que la evidencia no permite afirmar

- Nada sobre días posteriores: la foto caduca y no hay escaneo programado.
- Nada sobre las imágenes de escáneres (`gitleaks`, `semgrep`, `trivy`, `osv-scanner`), que van por
  digest en `scanner-contracts.yml`.
- Nada sobre `releasecheck.py --production`, que sigue en exit 1 fail-closed.
- Nada sobre `main`: los runs son de la rama; tras fusionar #14–#17 hay que repetirlos allí.

## Reproducción

La consulta se hizo con las herramientas de integración de GitHub sobre
`uniscrolliabrain-cloud/agntia-ciberseguridad`. No se reejecutó el workflow a mano ni se modificó el
YAML para esta campaña; el delta de código es **cero**.
