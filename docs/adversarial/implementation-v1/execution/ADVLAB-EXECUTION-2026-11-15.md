# Ejecución del programa adversarial — C01 a C18

**Fecha:** 2026-11-15. **Base:** `main@4c670a6`. **Rama:** `feat/advlab-campaigns-20261115`.
**Root nuevo:** `adversarial_lab/` (no importa `agntia_ciberseguridad`, no toca `/agente`).
**Estado global:** **PARTIAL** — la cadena completa funciona en modo sintético; las herramientas
externas y los proveedores reales quedan `BLOCKED` con stub honesto, no con resultados inventados.

## 1. Evidencia de ejecución

| Comprobación | Comando | Exit | Resultado |
|---|---|---|---|
| Suite del laboratorio | `PYTHONPATH=adversarial_lab/src:adversarial_lab/tests python -m unittest discover -s adversarial_lab/tests -t adversarial_lab/tests` | 0 | **69 tests OK** |
| Release gate | `python adversarial_lab/scripts/releasecheck.py` | 0 | PASS, 5 misiones, 0 hallazgos |
| Boundary gate | `python adversarial_lab/scripts/verify_boundary.py` | 0 | PASS, 0 violaciones de ownership |
| Ciclo diario | `python -m agntia_adversarial.cli run --tenant tenant-synthetic` | 0 | **PARTIAL**, 4 misiones, 4 evidencias, 7 tools BLOCKED |
| Validador del repo | `python scripts/validate_foundation.py` | 0 | PASS, 215 Markdown |

Run real generado: `run-46fd9e4195e3`, informe en `adversarial_lab/var/reports/` (gitignored),
evidencia cifrada AES-GCM con SHA-256 por artefacto y base SQLite con ledger.

## 2. Estado por campaña

| Campaña | Resultado | Estado | Evidencia principal |
|---|---|---|---|
| C01 Foundation | Paquete, config fail-closed, CLI `doctor/missions/run` | **PASS** | `src/agntia_adversarial/{config,cli}.py`, `tests/test_package.py` |
| C02 Engagement y scope | Autorización deny-by-default, tenant, fingerprint, revocación | **PASS** | `domain/`, `policy/authorization.py`, `tests/security/test_scope.py` |
| C03 Contratos y procedencia | Pydantic v2, JSON canónico, manifiestos SHA-256 | **PASS** | `contracts/`, `provenance/manifest.py`, `tests/contracts/test_roundtrip.py` |
| C04 Persistencia y ledger | SQLite, aislamiento por tenant, transiciones explícitas | **PASS** | `store/`, `ledger/`, `tests/integration/test_ledger.py` |
| C05 Aislamiento y broker | Sandbox local argv-only, egress denegado, broker con presupuesto | **PARTIAL** | Sin runtime OCI; `infra/sandbox/README.md` declara el gap |
| C06 Gemelos sintéticos | Datos seeded, manifiesto estable, fidelidad medida | **PASS** | `twins/`, `tests/integration/test_twin.py` |
| C07 Librería de misiones | 5 misiones versionadas, validador, compilador autorizado | **PASS** | `library/missions/`, `missions/`, `tests/contracts/test_mission_compiler.py` |
| C08 Proveedores | Protocolo neutral, mock determinista, externos BLOCKED | **PARTIAL** | `providers/`; Codex/Antigravity/Cline/Freebuff sin contrato verificado |
| C09 Planificador y scheduler | Ranking determinista, presupuesto, ventanas | **PASS** | `planning/`, `tests/integration/test_scheduler.py` |
| C10 Harness de herramientas | Catálogo cerrado, receipts con hash, fuzzing determinista | **PASS** | `tools/base.py`, `registry.py`, `receipts.py`, `fuzz.py` |
| C11 SAST/SCA/SBOM | Adaptadores Semgrep/OSV/Syft | **PARTIAL** | Binarios no instalados → `BLOCKED` |
| C12 API stateful | Adaptadores Schemathesis/ZAP y misión `api-state` | **PARTIAL** | Sin entorno aislado ni target HTTP real |
| C13 Frontera IA | Adaptadores PyRIT/garak y misión `ai-trust` | **PARTIAL** | Sin modelo ni licencia auditada |
| C14 Fuzzing y caos | Fuzzing local determinista, fallo/restore con RTO medido | **PASS** | `tools/fuzz.py`, `tools/faults.py`, `tests/integration/test_resilience.py` |
| C15 Oráculos y retest | Oráculos, triage con dedupe, retest, benchmark con denominadores | **PASS** | `evaluation/`, `tests/evaluations/test_oracles.py` |
| C16 Evidencia e informes | Vault AES-GCM 2 MiB, redacción, Markdown determinista | **PASS** | `evidence/`, `reports/`, `tests/security/test_evidence.py` |
| C17 Operación diaria | Ciclo completo con evidencia, ledger, informe y métricas | **PARTIAL** | Observaciones simuladas; resultado `PARTIAL` por tools bloqueadas |
| C18 Hardening y release | `releasecheck`, `verify_boundary`, README, gates | **PARTIAL** | Sin SBOM firmado, `pip-audit` en CI ni firma de release |

## 3. Qué queda BLOCKED y por qué

| Dependencia | Motivo | Stub aplicado |
|---|---|---|
| Semgrep, OSV, Syft, Schemathesis, ZAP, PyRIT, garak | Binarios/imágenes no instaladas ni verificadas | Adaptador devuelve `BLOCKED` con motivo |
| Codex, Antigravity, Cline, Freebuff | Sin API/CLI/licencia verificada | Registro los marca `BLOCKED`; no se invoca nada |
| Runtime OCI aislado | Sin digest, sin `network=none` del runtime, sin prueba de escape | Sandbox local allowlisted documentado |
| SBOM y firma de release | Sin `pip-audit`/cosign en CI ni clave | Gate reporta `PARTIAL` |

## 4. Desviaciones del protocolo, declaradas

1. **Una rama para las 18 campañas** en lugar de una por campaña: se ejecutó como programa completo
   en una sola sesión. Los commits son revisables y el boundary gate confirma ownership.
2. **Un informe consolidado** en lugar de 90 ficheros `P0..P4/{REPORT,PATCHSET,TESTS,AUDIT}`: se
   priorizó código ejecutable y evidencia real sobre papeleo por fase. Es una limitación, no un PASS
   de esos artefactos.
3. **Observaciones simuladas** en el ciclo diario: demuestran la cadena completa; no son hallazgos
   de un sistema real.

## 5. Riesgos

- El resultado `PARTIAL` es el correcto mientras las herramientas estén bloqueadas; elevarlo sería
  falsear capacidad.
- El sandbox local no resiste un atacante con capacidad de ejecución nativa; no usar con código
  no confiable sin OCI.
- La librería de misiones es pequeña (5 familias); no cubre el catálogo completo del Concept Master.

## 6. Rollback

```bash
rm -rf adversarial_lab/
git checkout -- docs/adversarial/implementation-v1/execution/ADVLAB-EXECUTION-2026-11-15.md
```

No hay migraciones sobre datos existentes ni cambios en `agntia_ciberseguridad/**`.

## 7. Siguiente paso

C05 con runtime OCI real y C18 con SBOM/firma antes de cualquier prueba sobre sistemas de cliente.
