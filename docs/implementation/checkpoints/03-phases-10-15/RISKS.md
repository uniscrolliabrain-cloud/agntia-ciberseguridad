# Riesgos y límites residuales

- Revisión independiente y aceptación de despliegue pendientes. Los flags de test no deben habilitar clientes.
- El launcher con acceso al daemon requiere separación de la API. El contenedor scanner no recibe socket, red ni credenciales globales.
- SQLite/leases se han probado en un host/CI con fallos sintéticos; no hay prueba de caída de host completo, NFS, restauración distribuida o Windows nativo de snapshots.
- Una confirmación persistente no es exactly-once del proceso físico. Revisar el worker anterior y limpiar su contenedor antes de conciliar una lease incierta.
- Las reservas cuentan intentos con coste0. No hay autorización ni implementación para cobrar/pagar proveedores; falta el ledger de D6P6 y medición mensual por tenant.
- No hay cuotas acumuladas de almacenamiento/rate limit de producción. Resultados e historial necesitan cifrado, conservación, legal hold y gestión de claves operativos.
- Semgrep cubre dos patrones de eval en tres lenguajes; no SAST universal ni interarchivo. Trivy solo configuración Dockerfile, sin paquetes desplegados o DB de imagen.
- CycloneDX válido no prueba veracidad. Importación limitada, sin despliegue inferido, licencias verificadas o soporte SPDX como documento de entrada.
- Relaciones entre herramientas están probadas como mecanismo de normalización; no se ha demostrado correlación completa imagen/SBOM/despliegue.
- Estados humanos/excepciones/retest, evidencia original cifrada y reportes finales quedan para los siguientes bloques.
- La licencia del código propio sigue pendiente. La existencia de notices de dependencias no aprueba por sí sola cualquier forma de redistribución o servicio comercial.
- El workspace local no pudo revisarse tras el corte; la fuente entregada es la rama remota validada. Conservar cambios ajenos si el executor vuelve.
