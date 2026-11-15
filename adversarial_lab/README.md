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
| Sandbox y broker | Implementado (local) | argv-only, allowlist, sin shell; adaptador OCI endurecido, runtime no disponible |
| Gemelos sintéticos | Implementado | Datos seeded, fidelidad medida |
| Misiones | Implementado | 5 misiones versionadas y validadas |
| Proveedores | Mock real; externos BLOCKED | Sin API/CLI verificada no se invoca nada |
| Herramientas | Contratos + stubs | Semgrep/OSV/Syft/ZAP/PyRIT/garak BLOCKED sin binario verificado |
| API sintética | Implementado | IDOR y escalada de rol en proceso, con control benigno y retest |
| Repo y agente sintéticos | Implementado | canario y dependencia sin fijar; inyección con `email.send` fuera de manifiesto |
| Fuzzing y caos | Implementado local | Determinista, solo ficheros sintéticos |
| Oráculos, triage, retest | Implementado | Nunca convierten NOT_RUN en PASS |
| Evidencia | Implementado | AES-GCM, 2 MiB, hash verificable |
| Informes | Implementado | Markdown determinista con limitaciones |
| Operación diaria | Implementado (sintética) | Resultado PARTIAL por herramientas bloqueadas |
| Release gates | Implementado (parcial) | `releasecheck` genera SBOM, firma Ed25519 y reporta `pip-audit` como BLOCKED |

## Uso

```bash
python -m pip install -e adversarial_lab
PYTHONPATH=adversarial_lab/src python -m agntia_adversarial.cli doctor
PYTHONPATH=adversarial_lab/src python -m agntia_adversarial.cli run --tenant tenant-synthetic
PYTHONPATH=adversarial_lab/src python -m unittest discover -s adversarial_lab/tests
python adversarial_lab/scripts/releasecheck.py
```

## Claves

`evidence` y `release` se generan localmente con 32 bytes, permisos `0600` y huella SHA-256 visible en
`advlab doctor`. Viven en `var/`, que Git ignora. Las credenciales de proveedores externos no se
guardan en el repo.

## Límites que no se maquillan

- No hay ejecución de modelos reales: el proveedor por defecto es `mock`.
- Las herramientas externas no están instaladas; devuelven `BLOCKED`, no resultados inventados.
- El sandbox es local (subprocess allowlisted); el adaptador OCI exige digest y `network=none`, pero no hay runtime verificado en esta máquina.
- El ciclo diario ejecuta las cinco misiones contra gemelos sintéticos en proceso; no hay sistemas de cliente ni modelos externos implicados.
- Nada de esto autoriza pruebas sobre clientes reales ni sustituye una revisión independiente.
