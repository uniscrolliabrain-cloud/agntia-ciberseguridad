# VS-02 — Herramientas reales sobre fixtures

**Base:** `afa13bc` (bitácora W0, sobre `2da922f`).
**Evidencia CI:** workflow *Offline scanner contracts*, run **43982858508**, job **docker-contracts**
(`133703454341`), conclusión **success**, 2026-11-16 23:51–23:53 UTC.
**Rama del reporte:** `feat/cyber-vs-02-ci-evidence`.
**Actor:** FreeBuff.

## Resultado

La campaña no estaba bloqueada: ya existía `scanner-contracts.yml` y este turno la ejecutó de punta a
punta en GitHub Actions, con Docker real y fixtures sintéticos. Los pasos del job:

| Paso | Conclusión | Duración aprox. |
|---|---|---|
| Instalar `.[dev]` | success | 13 s |
| `scripts/prepare_scanner_images.py` | success | 44 s |
| `scripts/build_probe_image.py` | success | 4 s |
| Tests reales de sandbox y scanners | success | 19 s |
| Diagnóstico Trivy (solo si fallo) | skipped | — |
| Artefacto de procedencia | success | 1 s |

El paso de tests ejecuta `tests.docker.test_real_scanners` y `tests.docker.test_extended_scanners`
con `AGNTIA_RUN_DOCKER_TESTS=1`, es decir, sin saltos: un skip no cuenta como evidencia.

## Qué cubre de verdad

- **Gitleaks:** canario sintético detectado aunque el repo intente silenciarlo con `.gitleaks.toml`
  y `.gitleaksignore`; control limpio sin hallazgos; el secreto no aparece en el resultado.
- **OSV:** paquete sintético vulnerable detectado, control parcheado limpio, base caducada marcada
  `stale` y base ausente que no se declara limpia.
- **Semgrep:** reglas locales detectan `eval` en Python/JS/TS pese a comentarios `nosemgrep`, sin
  filtrar el código fuente al resultado; control con `ast.literal_eval`/`JSON.parse` limpio.
- **Trivy:** `USER root` en Dockerfile detectado (DS-0002) y control con UID no root limpio;
  vulnerabilidades de imagen declaradas `not_tested`.
- **Sandbox:** UID 65532, sin red, sin secretos del host, límites de timeout, salida y PIDs, y
  limpieza verificada.

## Qué no cubre

- No escanea activos de terceros ni repositorios reales: solo fixtures sintéticos.
- Los digests se resuelven al construir las imágenes y se publican como artefacto; no están fijados
  por digest en el repositorio. Queda como mejora, no como PASS de reproducibilidad bit a bit.
- No valida feeds en vivo ni licencias comerciales; OSV usa base offline creada por el propio test.
- Trivy no evalúa vulnerabilidades de imagen (`not_tested`), solo configuración.

## Gates

| Gate | Antes | Ahora |
|---|---|---|
| G2 aislamiento | PARTIAL | **PASS (sintético)** con evidencia de job |
| G3 integridad de escaneo | PARTIAL | **PASS (sintético)**; sigue sin auditoría externa |

No se toca `docs/release/status.json`: la evidencia es de CI, no una certificación de producción.

## Rollback

El reporte no cambia código. Si se revierte, el workflow sigue disponible en `main`; no hay estado
que deshacer. El artefacto de procedencia caduca según la retención de Actions.

## Siguiente

VS-03: interfaz de secretos y adaptador de fichero para tests, con `BLOCKED` explícito para el
gestor real hasta que exista cuenta y credenciales.
