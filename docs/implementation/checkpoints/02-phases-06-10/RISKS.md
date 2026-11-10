# Límites del segundo corte

- D1P6 no tiene revisión independiente. Las pruebas hechas por el implementador y la CI no la sustituyen; ejecución de clientes denegada por defecto.
- Docker local no es accesible. La evidencia Docker válida procede del runner GitHub de pruebas, asociada a su SHA, y no demuestra el sandbox de otra instalación.
- Adquisición solo local POSIX: no remote Git, Windows nativo, imágenes, extracciones, historial, LFS o submódulos. Un origen mutable no tiene consistencia multiarchivo atómica.
- Copias read-only y hashes no protegen de un administrador que reescribe base, ficheros y configuración. Sin cifrado/retención/anclaje externo de despliegue.
- Un crash entre rename y commit puede dejar un directorio huérfano no registrado. Se rechaza al consultar; falta un job operativo de conciliación/retención.
- Perfiles de contenedor reducen riesgo, no son una frontera frente a un kernel/daemon comprometido. El launcher es de confianza, debe separarse de la API y no exponer el socket a un worker.
- Tests reales usan canario y advisory sintéticos, no un benchmark de cobertura de secretos/vulnerabilidades ni un feed completo/actual de producción.
- SBOM es observado: relaciones/licencias/reachability desconocidas no se completan con LLM. Validación oficial de esquema e importación amplia de SBOM quedan pendientes.
- Faltan jobs durables, lease/fencing/retries, resultados persistentes e informes finales; siguen en fases11+. No hay monitorización continua, cambios en /agente, despliegue o gasto contratado.
- Límites de adquisición son por operación, no cuotas acumuladas por tenant. Faltan cuotas de almacenamiento/rate limiting; mantener la API privada de laboratorio y no exponerla como servicio de clientes.
