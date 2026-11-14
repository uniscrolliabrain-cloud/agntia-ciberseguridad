# Matriz de compatibilidad

| Entorno | Evidencia vigente | Límite |
|---|---|---|
| Linux Python3.11/3.12, Node24 | CI de runtime hasta checkpoint8 correcta; cierre vuelve a ejecutar | Fixtures; no clientes/productivo |
| Ubuntu24.04 x86_64 Python3.12 | Empaquetado/clean venv/offline wheelhouse/SDK configurados en release CI | Resultado del SHA final en checkpoint9; no heredar PASS anterior |
| Windows hosted Python3.12 Node24/PowerShell | Nuevo job de paquete y smoke instalados | No implica suite completa Windows, daemon Docker Desktop ni Linux containers |
| Docker Linux x86_64 | Scanners/collector probados en CI; imagen API nueva requiere su smoke | API no contiene worker/socket/scanners; Compose de cliente no ensayado |
| Windows local + Docker Desktop | NOT_VERIFIED | Otro agente/owner debe registrar su ejecución real |
| ARM64, macOS, cluster multi-node | NOT_VERIFIED | No prometer wheels/digests/capacidad sin pruebas |

El bundle de wheels resuelve y congela versiones/hashes por ejecución/plataforma. Una futura construcción puede resolver dependencias distintas; no se promete reproducción bit a bit entre fechas o SO. SDK incluye JS/declaraciones y manifiesto, pero instala su dependencia Hono desde npm/caché del consumidor. El empaquetado tiene referencias de licencia, no autorización legal completa.

Resultados de cierre observados: la instalación desde artefacto Python y SDK, hash verification y SBOM pasaron en Ubuntu24.04 y Windows hosted. PowerShell pasó tras corregir lectura UTF-8; la primera ejecución fallida se conserva en checkpoint9. La imagen Linux pasó con usuario65532, root read-only y network=none. Compose Lite/L/XL pasó config --quiet local sin arrancar containers. La atestación de ambos manifiestos se comprueba en el job dedicado del SHA final; consultar evidence/ci.json. Nada de ello amplía el smoke Windows a la suite completa o a Docker Desktop.
