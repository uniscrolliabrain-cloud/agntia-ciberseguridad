# Ejecutar el núcleo en laboratorio

Python>=3.11. Esto permite inventario, grants y preflight. No ejecuta scanners ni protege una aplicación en producción.

```bash
python -m venv .venv
# Linux/macOS
. .venv/bin/activate
python -m pip install -e '.[dev]'
python -m unittest discover -s tests -v
agntia-ciberseguridad --version
```

En PowerShell, activar con `.\.venv\Scripts\Activate.ps1`. No modificar la política de ejecución del equipo desde el middleware. Como alternativa, ejecutar directamente `.\.venv\Scripts\python.exe`.

Crear un JSON privado con `data_dir`, `principals`, `approved_workspace_roots`, `targets` y `consents`, siguiendo `config.py` y las fixtures sintéticas de `tests/support.py`. Rutas absolutas existentes en el SO local, nada de rutas copiadas de otro equipo. Los tokens se generan de forma aleatoria con al menos32 bytes de entropía; el JSON solo incluye el nombre de la variable de entorno en `token_env`. Nunca subir el fichero privado ni tokens a Git.

El registro tiene que incluir dos personas distintas para proponer/aprobar. Los consentimientos declaran titular, referencia de la evidencia de representación, recursos, perfiles, ventana y límites. La fixture de pruebas solo acredita el flujo sintético; no sirve como consentimiento de un cliente. Los tenants los provisiona el servidor desde sus bindings, no un campo del LLM.

```bash
agntia-ciberseguridad serve --config /ruta/privada/config.json
```

La CLI usa127.0.0.1:8012 por defecto, un worker. `/health/live` informa vida del proceso; `/health/ready` comprueba esquema y al menos una credencial vigente y devuelve `security_scanners_ready=false`. Readiness no garantiza cobertura de cada tenant ni capacidad de auditoría.

Rutas disponibles, siempre con Bearer servidor y scope de tenant salvo health:

- `GET/POST /v1/tenants/{tenant}/assets`; `GET .../assets/{id}`.
- `POST .../grants`; `GET .../grants/{id}`.
- `POST .../grants/{id}/approve`; `POST .../grants/{id}/revoke`.
- `POST .../audits/preview`; `GET .../audit/integrity`.

No se admiten URLs ni comandos libres en esos bodies. Referencias de recursos, consentimientos y credenciales se administran fuera de la API. Las revisiones de aprobación/revocación son optimistas. Cambiar el objetivo aprobado invalida su hash y requiere revisión de configuración, no sobrescritura silenciosa.

Antes de exponer servicio: TLS privado, control de red y rate limiting, secretos gestionados, cifrado/backup/retención, protocolo de identidad de `/agente` y revisión independiente. Estas tareas siguen pendientes. No abrir puertos al público ni montar `/var/run/docker.sock` en la API.

Detener el proceso detiene nuevas admisiones. Conservar `state` y backups, verificar cadena antes de restaurar. Las migraciones son aditivas; no ejecutar un downgrade destructivo. Restaurar solo con el servicio detenido desde una copia consistente y probada. La suite ensaya restauración SQLite sintética, no recuperación del equipo ni de backups cloud.

## Segundo bloque

Hay rutas POST/GET de snapshots y adaptadores de scanner internos. Consultar [checkpoint6–10](checkpoints/02-phases-06-10/REPORT.md) e [infra/scanners](../../infra/scanners/README.md). La API no ejecuta scanners; el opt-in Docker solo habilita fixtures sintéticas de CI, no aprobación de un piloto.

## Tercer corte

El [informe10–15](checkpoints/03-phases-10-15/REPORT.md) documenta POST audits202, GET/cancel jobs y findings/historial. Configurar tool_policy_hashes solo en servidor. Los jobs quedan bloqueados por defecto hasta verificar ReleaseGates; no copiar valores positivos de fixtures a producción. La distribución incluye validación CycloneDX1.5 sin red; los casos Docker reales siguen opt-in de laboratorio.
