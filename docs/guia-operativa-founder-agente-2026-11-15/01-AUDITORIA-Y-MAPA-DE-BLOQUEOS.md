# 01 — Auditoría selectiva y mapa de bloqueos
**Alcance efectivamente revisado:** comparación GitHub `main...feat/advlab-campaigns-C01-C18`; README del laboratorio; informe de C01–C18; `sandbox.py`, `oci.py`, `vault.py`, `providers/registry.py`, `releasecheck.py` y `docs/release/status.json`. **No** se ejecutaron tests, se clonó todo el árbol ni se certificó seguridad. El inventario de archivos se basa en respuesta de comparación GitHub, no en análisis línea por línea de 125 archivos.

## Hechos
- Comparación: 4 commits por delante, 0 por detrás, 125 archivos en diff.
- El laboratorio dispone de CLI, SQLite/ledger, misiones sintéticas, oráculos, informes, vault y tests. Informe declara 86 tests OK, 5 misiones y ciclo diario PARTIAL por 7 tools BLOCKED; confirmar con ejecución independiente.
- Proveedores externos `codex`, `antigravity`, `cline`, `freebuff` quedan BLOCKED en registry, mock es el único provider registrado por defecto.
- `Sandbox.run`: permite subprocess local, env reducido, timeout y output truncado; carece de aislamiento de kernel, filesystem y red por sí mismo.
- `OCISandbox.command`: digest obligatorio, `--network=none`, read-only, cap-drop, no-new-privileges, límites de memoria/pids, tmpfs y mount ro. Esto prueba construcción de comando, no defensa real ni disponibilidad del runtime.
- `Vault`: crea `evidence.key` en root, una clave para todas las carpetas de tenant; usa `root / tenant_id / evidence_id.bin` sin validación local visible de identificadores. AAD incluye evidence_id, no tenant_id. **Riesgo a investigar** de traversal, colisión/cross-tenant y debilidad de separación; no se afirma explotación.
- `releasecheck`: audit_status se imprime como estado, pero su retorno no añade hallazgo fatal cuando es BLOCKED. El exit 0 significa chequeos internos pasados, **no** autorización de release completo.
- Middleware main: `SYNTHETIC_DEMO_NOT_PRODUCTION`; `owner_acceptance=PENDING`, `independent_review=PENDING`, `production_enabled=false`, 2 PASS/40 PARTIAL.

## Registro de hallazgos y mitigación
| ID | Severidad de prioridad | Hallazgo | Archivo | Acción y evidencia exigida |
|---|---|---|---|---|
| CY-01 | P0 | subprocess no es sandbox para código hostil | `execution/sandbox.py` | negar uso no confiable; OCI/microVM real; prueba de red, FS, usuario, mounts, recursos y escape |
| CY-02 | P0 | paths derivados de identificadores sin confinamiento explícito en vault | `evidence/vault.py` | validar IDs, resolve/is_relative_to, symlink race, atomic writes, tests traversal |
| CY-03 | P0 | clave de evidencia compartida y AAD incompleto por tenant | `evidence/vault.py` | claves por tenant o envelope KMS, tenant+id+versión en AAD, rotación y restore |
| CY-04 | P0 | PASS de release con auditoría de dependencias BLOCKED | `scripts/releasecheck.py` | gate de producción FAIL/BLOCKED si pip-audit o política de vulnerabilidades no verificadas |
| CY-05 | P0 | falta autorización real de activos/cliente y aceptación independiente | status + informes | engagement firmado, alcance, revocación y aceptación |
| CY-06 | P1 | herramientas y agentes reales bloqueados | provider registry + informe | conectar uno en gemelo sintético, probe de capabilities, presupuesto y receipts |
| CY-07 | P1 | OCI no probado en runtime real | `execution/oci.py` | ejecutar pruebas negativas en host efímero y registrar runtime/versiones |
| CY-08 | P1 | 42 fases middleware siguen mayoritariamente PARTIAL | status.json | delta contra auditoría diferencial; cerrar gates por evidencia, no por texto |
| CY-09 | P1 | daily cycle sintético no es scheduler productivo | README/informe | persistencia, lock, idempotencia, alertas, kill switch y restore |
| CY-10 | P1 | reporte de ejecución no sustituye logs reejecutados | ADVLAB-EXECUTION | CI reproducible, SHA, OS, python, dependencia lock y resultados |

## Hipótesis a comprobar, no vulnerabilidades confirmadas
1. Un `tenant_id` con `../` podría intentar salir del directorio esperado. Probar con fixtures seguros en copia temporal; no ejecutar contra datos reales.
2. Una misma evidencia_id con tenant diferente no debería poder intercambiar ciphertext o contexto AAD.
3. Un runtime OCI rootful podría seguir exponiendo superficie host pese a flags; medir configuración real, usuario, seccomp, AppArmor/SELinux y límites.
4. La política de release debe diferenciar `lint-pass`, `integrity-pass`, `dependency-audit-blocked`, `production-release-denied`.

## Evidencias que debe reunir el agente
- `git rev-parse HEAD` para main, rama advlab y rama de trabajo.
- `git diff --stat main...feat/advlab-campaigns-C01-C18`, `git diff --name-status`, `git log --oneline`.
- Tests con `PYTHONPATH=adversarial_lab/src:adversarial_lab/tests python -m unittest discover -s adversarial_lab/tests -t adversarial_lab/tests`.
- `python adversarial_lab/scripts/releasecheck.py` y `python adversarial_lab/scripts/verify_boundary.py`.
- `python scripts/validate_foundation.py` desde raíz, más CI principal y SDK según runbooks.
- Capturar exit, logs redactados, versiones y desviaciones; no contar como PASS una dependencia ausente.
