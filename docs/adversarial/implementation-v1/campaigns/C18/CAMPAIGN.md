# C18 — Hardening, release & handoff

**Wave:** W4 · **Root independiente:** `adversarial_lab/`. No tocar `agntia_ciberseguridad/**` ni `/agente`.

## Archivos nuevos
- `adversarial_lab/scripts/releasecheck.py`
- `adversarial_lab/scripts/verify_boundary.py`
- `adversarial_lab/infra/README.md`
- `adversarial_lab/tests/security/test_release_gates.py`
- `adversarial_lab/README.md`

## Dependencias
pip-audit u OSV-Scanner en CI, SBOM, no desplegar. Añadir versiones fijadas y hashes en `adversarial_lab/pyproject.toml` y lock tras revisión. No instalar repos enteros sin ADR.

## Fases y patchsets
- **P0 PS0-A:** inspeccionar HEAD, interfaces previas, dependencias y amenazas; registrar base SHA y paths.
- **P1 PS1-A/B:** crear contratos tipados, fixtures y tests positivos/negativos que fallen inicialmente; definir errores y semántica NOT_RUN.
- **P2 PS2-A/B/C:** implementar módulos listados, validación, cancelación, límites y errores fail-closed; conectar solo dentro de paquete nuevo.
- **P3 PS3-A/B:** integración, pruebas de seguridad y regresión; casos: no touched agents, SBOM, reproducible build, signoff. Validar con `python -m pytest adversarial_lab/tests`.
- **P4 PS4-A/B:** revisión de diff, licencias, SBOM, threat model, rollback, PR sin merge y handoff.

## Reportes por fase
Crear `docs/adversarial/implementation-v1/execution/C18/P0..P4/{REPORT.md,PATCHSET.md,TESTS.json,AUDIT.md}` con commits reales, archivos, comandos, exit codes, evidencias, fallos, costes, riesgos y decisiones. Originales privados en vault cifrado, no Git.

## Wiring
Entrada `EngagementRef + ScopeRef + ExperimentSpec + Budget + PolicySnapshot`; salida `RunReceipt + Observations + EvidenceRefs + Status`. Solo contracts versionados; nada de imports de agentes existentes. Si no existe interfaz real, mock disabled y BLOCKED.

## Gates
Scope y consentimiento, aislamiento, tenant, secretos, red, rollback, tests de error y licencias. PASS solo con evidencias verificadas. STOP ante incompatibilidad, cambio fuera de ownership, acceso a cliente o falta de autorización.
