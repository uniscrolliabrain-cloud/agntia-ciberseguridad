# VS-06 — Revisión, CI y release fail-closed

**Base:** `008aaeb`. **Estado:** gate `BLOCKED` por auditoría de dependencias; el resto pasa.
**Actualización 2026-11-17:** el bloqueo de dependencias está resuelto y el diagnóstico del upgrade
era incorrecto; ver [VS-06B-REPORT.md](VS-06B-REPORT.md). La atestación externa sigue `BLOCKED`.
**Verificación:** 197 tests OK (8 skipped) tras revertir el intento de upgrade.

## Lo que pasa de verdad

| Comprobación | Exit | Resultado |
|---|---|---|
| Smoke de artefacto instalado | 0 | PASS; recursos con SHA-256; `production_accepted=false`, `scanner_executed=false` |
| Bundle de release + verificación | 0 / 0 | `scripts/release_bundle.py` genera y verifica |
| Esquema CycloneDX del SBOM | 0 | `SBOM_SCHEMA_PASS` con el validador oficial incluido |
| Gate del laboratorio | 0 | integridad PASS, `findings: []` |
| Gate `--production` | **1** | falla cerrado: firma local no es atestación externa |
| `pip-audit --local` | **1** | **14 vulnerabilidades en 62 dependencias** |

## Hallazgo P0: dependencia de runtime vulnerable

`opentelemetry-api==1.38.0` acumula dos CVE con fix en **1.45.1 / 1.45.2**. Viene fijado por
`opentelemetry-sdk==1.38.0` y `opentelemetry-exporter-otlp-proto-http==1.38.0` en `pyproject.toml`.

Intenté el upgrade real a 1.45.2 y **rompe la propagación de trazas**: el test
`test_persisted_trace_propagates_to_worker_and_report_link` compara trace-ids y falla
(`2286… != 2510…`). No es un bump seguro; requiere migración de la instrumentación. Revertí a 1.38.0
y la suite vuelve a 197 OK.

El resto de avisos (12) son de `pip==24.0`, herramienta del entorno, no dependencia de runtime.

## Hallazgo P1: no hay auditoría en CI

Ningún workflow ejecuta `pip-audit`; el gate de producción lo declara `BLOCKED` correctamente, pero
nada impide fusionar una dependencia vulnerable. Añadir el job sin resolver los CVE dejaría CI en
rojo permanente, así que no se añade a medias.

## Delta recomendado

1. Migrar la instrumentación a OpenTelemetry 1.45.x y actualizar los pins; repetir telemetría y suite.
2. Job `audit` en CI: actualizar `pip`, instalar `pip-audit` y ejecutar `--local` con exit != 0.
3. Atestación externa (GitHub Artifact Attestations ya se usa para publicar; el gate debe distinguir
   procedencia de aceptación de producto, como ya hace el mensaje).

## Gate

`BLOCKED`: no se puede declarar release beta con una dependencia de runtime vulnerable y sin
atestación externa. El fail-closed funciona: prefiere fallar antes que publicar.
