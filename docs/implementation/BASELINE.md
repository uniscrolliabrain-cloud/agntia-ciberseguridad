# D1P1 · Baseline de implementación

Fecha:2026-11-10. Main remoto00ee50d2adf672d9815c97aa6fb8cd4bfe00de87; árbol ddbfbe8f33ba8e2cc814d5441325014bd1aeb6d9. El checkout local procede de publicación vía API y tiene SHA local distinto6fd6b5e, con el mismo árbol. Los cambios previos estaban limpios; se conservan historial y documentación. No se modifican otros repos.

Inventario reproducible: [environment.json](baseline/environment.json), generado por scripts/verify_environment.py sin leer credenciales ni contactar clientes. Python3.12 y Node24 están disponibles. Docker/Compose existen; la comprobación del socket local falla por permisos. Los scanners no están instalados. Este hecho bloqueará pruebas de sandbox real hasta disponer de un ejecutor válido; no impide implementar/probar el núcleo documental/API local.

El baseline contiene51 archivos versionados, incluida la documentación y el ZIP anterior. No hay código runtime preexistente de ciberseguridad. Las pruebas de documentación anteriores no se heredan como tests de seguridad del servicio.
