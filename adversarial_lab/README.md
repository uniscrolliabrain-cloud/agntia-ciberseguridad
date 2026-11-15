# Adversarial Lab (independiente)

Red team supervisado y agnóstico de proveedor sobre **gemelos sintéticos**. No importa
`agntia_ciberseguridad`, no toca `/agente` y no abre red.

## Estado real

| Área | Estado | Nota |
|---|---|---|
| Paquete, config, CLI | Implementado | `doctor`, `missions`, `run` |
| Engagement, scope, revocación | Implementado | Deny-by-default, tenant y fingerprint |
| Contratos y procedencia | Implementado | Pydantic v2, SHA-256 canónico |
| Persistencia y ledger | Implementado | SQLite, transiciones explícitas |
| Sandbox y broker | Implementado (local) | argv-only, allowlist, sin shell; sin OCI todavía |
| Gemelos sintéticos | Implementado | Datos seeded, fidelidad medida |
| Misiones | Implementado | 5 misiones versionadas y validadas |
| Proveedores | Mock real; externos BLOCKED | Sin API/CLI verificada no se invoca nada |
| Herramientas | Contratos + stubs | Semgrep/OSV/Syft/ZAP/PyRIT/garak BLOCKED sin binario verificado |
| Fuzzing y caos | Implementado local | Determinista, solo ficheros sintéticos |
| Oráculos, triage, retest | Implementado | Nunca convierten NOT_RUN en PASS |
| Evidencia | Implementado | AES-GCM, 2 MiB, hash verificable |
| Informes | Implementado | Markdown determinista con limitaciones |
| Operación diaria | Implementado (sintética) | Resultado PARTIAL por herramientas bloqueadas |
| Release gates | Implementado | `scripts/releasecheck.py`, `scripts/verify_boundary.py` |

## Uso

```bash
python -m pip install -e adversarial_lab
PYTHONPATH=adversarial_lab/src python -m agntia_adversarial.cli doctor
PYTHONPATH=adversarial_lab/src python -m agntia_adversarial.cli run --tenant tenant-synthetic
PYTHONPATH=adversarial_lab/src python -m unittest discover -s adversarial_lab/tests
python adversarial_lab/scripts/releasecheck.py
```

## Límites que no se maquillan

- No hay ejecución de modelos reales: el proveedor por defecto es `mock`.
- Las herramientas externas no están instaladas; devuelven `BLOCKED`, no resultados inventados.
- El sandbox es local (subprocess allowlisted), no un runtime OCI con kernel aislado.
- El ciclo diario usa observaciones **simuladas** para demostrar la cadena completa.
- Nada de esto autoriza pruebas sobre clientes reales ni sustituye una revisión independiente.
