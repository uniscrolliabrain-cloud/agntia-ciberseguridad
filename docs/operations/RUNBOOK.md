# Instalación y operación del laboratorio

Entrega: demo sintética single-node. No usar datos de clientes ni exponerla públicamente. El código vigente está en la rama de cierre de PR#9, apilada sobre PR#8; main no incorpora automáticamente las PR draft. Clonar y seleccionar esa rama antes de instalar. Python3.12 y Node24 son los objetivos de empaquetado de CI; consultar [compatibilidad](../release/COMPATIBILITY.md) para resultados realmente observados.

## Artefacto limpio

Descargar el artifact synthetic-release correspondiente a SO/arquitectura del workflow Synthetic release artifacts del SHA revisado. Los artifacts caducan a los7 días; no son un release comercial en GitHub Releases. Verificar la procedencia del manifiesto mediante `gh attestation verify manifest.json --repo uniscrolliabrain-cloud/agntia-ciberseguridad`; comprobar también SHA/workflow de origen frente a la ejecución aceptada. Después `python scripts/release_bundle.py --verify /ruta/al/bundle` desde el checkout revisado. SHA256SUMS comprueba integridad, por sí solo no autentica al editor.

Crear una venv nueva: `python -m venv .venv`; seleccionar `.venv/bin/python` en Linux o `.venv\Scripts\python.exe` en Windows. Instalar desde el bundle con `python -m pip install --no-index --require-hashes --find-links /ruta/bundle/wheelhouse -r /ruta/bundle/requirements.lock`. Ese lock es específico del bundle/plataforma; no mezclar wheels Linux/Windows o arquitecturas distintas. Desde un directorio fuera del checkout ejecutar `python -I -m agntia_ciberseguridad.releasecheck`. Sus resultados son sintéticos y no ejecutan scanners.

El SDK se entrega como tarball creado con npm pack, sin publicación a npm. Instalarlo en un consumidor de prueba con `npm install --ignore-scripts /ruta/bundle/agntia-ciberseguridad-0.1.0-alpha.1.tgz`; necesita obtener Hono si no está cacheado. La instalación SDK no es offline integral: la wheelhouse solo cubre Python. Mantener lock del consumidor y revisar licencia propia pendiente antes de distribución comercial. [Patchset de /agente](../integration/PATCHSET-AGENTE.md) es propuesta, no wiring aplicado.

## Servidor privado y Compose

Configurar Settings JSON fuera del repo: data_dir=/state, principals con token_env y tenants explícitos, target/consent refs administrados, claves externas de evidencia y política legal de custodia. No hay owner ni token por defecto. En Windows host, data_dir debe ser una ruta privada nativa; /state es la ruta dentro del contenedor Linux. Para el host, `agntia-ciberseguridad serve --config /ruta/privada/server.json` escucha127.0.0.1:8012 con un worker. El archivo privado de variables debe tener acceso mínimo; nunca commitearlo ni imprimir docker compose config si puede interpolar secretos. La consola manual sigue siendo piloto.

Para construir imagen usar solo wheelhouse/requirements.lock del bundle verificado como contexto, `infra/Dockerfile` como Dockerfile y PYTHON_BASE fijado por digest observado en CI. El Dockerfile instala sin red, usa65532:65532 y no copia el checkout ni secretos. Un tag no es un digest; no sustituirlo por latest. La prueba CI registra base e imageID en el artifact de provenance y en checkpoint9/evidence/runtime-image.json. No se publica imagen en registry.

Configurar AGNTIA_RUNTIME_IMAGE al imageID inmutable local, AGNTIA_SERVER_CONFIG a un archivo JSON externo y AGNTIA_SECRET_ENV_FILE a un archivo privado externo. `docker compose -f infra/compose.yaml config --quiet` valida sin imprimir la configuración; `docker compose -f infra/compose.yaml up -d` solo se usa después de revisar configuración y aceptar el laboratorio propio. Puerto loopback, red internal, sin socket Docker ni mounts del host generales; root filesystem read-only, capabilities eliminadas, no-new-privileges, límites CPU/RAM/PIDs y volumen de estado. Overlay L: añadir `-f infra/profiles/l.yaml`; XL: `-f infra/profiles/xl.yaml`. Son límites de laboratorio, no capacidad prometida o coste mensual medido.

La imagen no contiene scanners, fuentes de clientes, CA privadas ni secretos de registry. El núcleo API no recibe Docker socket; un futuro worker dedicado requiere su propio gate y configuración, no montar el socket en api para hacerlo funcionar. La prueba container de CI ejecuta selfcheck sintético con network=none, no un Compose productivo con cuentas reales.

## Comprobaciones, rotación y recuperación

Linux: `bash scripts/verify_lab.sh`. Windows: `pwsh -NoProfile -File scripts/verify_lab.ps1`; no cambia ExecutionPolicy ni instala paquetes globales. Si una política organizativa prohíbe el script, usar comandos revisados individualmente o el procedimiento de TI; no desactivar controles globales. Docker Desktop Linux containers es una plataforma distinta y su cobertura no se infiere del smoke Windows.

Rotar tokens en el almacén externo y renovar bindings/manifests/delegaciones según sus revisiones; no reutilizar una delegación de un uso tras timeout. Revocación o policy hash cambiado bloquean ejecución. Claves de evidencia: conservar claves anteriores mientras existan envelopes que las referencien; añadir nueva key_ref no recifra automáticamente el histórico. No borrar una clave antigua para simular borrado RGPD. No exponer variables en incidencias públicas.

Backup/restore verificados hasta ahora son parciales y solo para laboratorio detenido: base, configuración cifrada y ciphertext referenciado; no incluyen árboles de snapshots ni candidatos. Ver [recuperación](../implementation/RECOVERY-RESULTS.md). Mantener RESTORE_BLOCKED hasta conciliar restricciones/identidades actuales, claves, grants y efectos externos. No retirar el marcador automáticamente ni usarlo como procedimiento productivo aprobado.

Ante incidente: detener admisión, preservar auditoría/ciphertext, registrar hechos verificados y responsable; no enviar avisos regulatorios ni activar contención de host desde esta demo. Cumplimiento prepara expedientes revisables, no dictámenes. Para upgrade guardar backup consistente, verificar migraciones/esquema y permisos; no arrancar un ejecutable antiguo contra un esquema posterior. Más detalles en [rollback](ROLLBACK.md).
