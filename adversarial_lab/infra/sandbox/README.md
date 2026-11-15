# Sandbox: estado y requisitos

El sandbox actual es **local y conservador**: ejecuta únicamente binarios allowlisted con `argv`,
sin `shell=True`, con `HOME` y `PATH` mínimos, timeout y salida acotada. No es un aislamiento OCI.

## Qué falta para llamarlo aislamiento fuerte

1. Runtime OCI fijado por digest y usuario sin privilegios.
2. Filesystem de solo lectura salvo el directorio del gemelo.
3. `network=none` aplicado por el runtime, no por la aplicación.
4. Límites de CPU, memoria, pids y tiempo.
5. Destrucción verificable del contenedor y del volumen efímero.
6. Prueba negativa de escape y de egress antes de habilitar herramientas activas.

Hasta entonces: `BLOCKED` para pruebas activas y `PARTIAL` para el ciclo diario.
