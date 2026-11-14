# Scanners offline para laboratorio

`releases.json` fija release, asset y SHA256 de Gitleaks y OSV-Scanner Linux amd64. `prepare_scanner_images.py` descarga y verifica esos bytes, copia únicamente el binario esperado (sin extraer rutas del tar), conserva notices y construye imágenes scratch. Verifica la versión **dentro del contenedor** y guarda image ID + policy_hash. No ejecuta esos binarios en el host.

La instalación es administrativa, separada de la API. Requiere Docker local autorizado, acceso de descarga de releases, Python y dependencias del paquete. No hay descarga automática durante un scan. `build_probe_image.py` resuelve un digest de Python únicamente para un probe sintético de CI; no fija una imagen de producto basada en un tag mutable.

```bash
python scripts/prepare_scanner_images.py
python scripts/build_probe_image.py
AGNTIA_RUN_DOCKER_TESTS=1 python -m unittest tests.docker.test_real_scanners -v
```

En PowerShell usar `$env:AGNTIA_RUN_DOCKER_TESTS='1'` y el Python del entorno virtual. **Windows nativo no tiene adquisición POSIX validada**: usar un ejecutor Linux/WSL2 con paths locales coherentes y validar sus bind mounts. No afirmar soporte Windows completo por poder instalar Python.

Los tests reales solo generan canarios no funcionales y un paquete/advisory ficticio. Comprueban scope del contenedor, UID, permisos, red deshabilitada, ausencia de secretos/proxies/socket, CPU/RAM/pids configurados, timeout, salida excesiva y limpieza. `unittest discover` sin opt-in omite esos cuatro casos expresamente; sus skips no son un PASS Docker.

Se escanea en modo directorio, sin historia Git; OSV funciona offline, sin resolver paquetes ni instalar nada. El feed de test no sirve para clientes. El estado de validación y los fallos previos están en el checkpoint02. Deshabilitar una herramienta conserva snapshots y auditoría; no borrar el origen ni matar procesos globalmente.

Licencias/avisos: `licenses/`. El uso de binarios y defaults por API/proceso no incorpora la action comercial ni una suscripción Enterprise. El coste de CI/hosting/almacenamiento sigue existiendo y no se ha medido como precio por tenant en esta entrega.
