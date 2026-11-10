# Decisiones del corte10–15

1. Fase10 se revisita para cerrar la validación estructural SBOM;11–15 corresponden a Semgrep, Trivy opcional, jobs, worker y normalización. Se preservan los42 IDs del plan.
2. SQLite sigue siendo el backend de un nodo. Migración3 aditiva, FKs compuestas y transacciones inmediatas; no se anuncia clúster distribuido.
3. Un POST202 es un recibo de admisión. Actor/tenant/capacidad no vienen de texto del agente. El payload no acepta shell, mounts, URL de DB, credenciales o coste positivo.
4. Sello de autorización es un hash del principal capturado, que incluye el fingerprint interno de credencial. No es el bearer ni su fingerprint directo de autenticación y no se devuelve. Permite revocar trabajos pendientes al rotar rol/scope/token sin guardar el token en DB.
5. Reservas del corte son intentos locales con importe0; no una simulación de pago ni el ledger del plan económico. Los límites de reintentos se reservan una sola vez y de forma conservadora.
6. Caducidad de lease es incertidumbre, no permiso para duplicar el proceso. Se conserva execution_name, se bloquea capacidad y se requiere cleanup verificado antes de reintentar. Fencing protege la confirmación de resultados; no implica una garantía física exactly-once frente a todos los fallos del host/daemon.
7. Cancelación pending es efectiva. Cancelación running o pérdida de worker puede requerir conciliación. No se deduce cleanup del simple hecho de cancelar una coroutine.
8. Resultado minimizado y observaciones se confirman en una transacción. Originales cifrados/exportables y retention/legal hold son fases posteriores; no se guarda stdout crudo aquí.
9. Identidad del finding excluye snapshot y secretos, incluye tenant/activo/tool/política/regla/ubicación/componente. Cambiar bundle puede separar identidades; correlación no equivale a fusionar verdad de dos scanners.
10. No observado no equivale a corregido. Los estados humanos/excepciones requieren su flujo posterior. Las salidas de herramientas no adquieren autoridad para aprobarse.
11. Semgrep conserva la distribución LGPL2.1 del upstream por digest y usa solo CE/reglas propias. No registry ni Pro. Trivy se limita a Dockerfile/checks embebidos; imágenes/advisories se declaran not_tested.
12. CycloneDX1.5 se valida con bundle oficial Apache2.0 y resolución de referencias cerrada. Importar un documento válido no verifica su contenido, despliegue o licencias.
13. Tras la caída del ejecutor se conservó la implementación por GitHub y se volvió a validar en CI. No se atribuye al source rescatado la identidad de un commit local que no pudo leerse.
14. Se preservan fallos: ubicación incorrecta del CLI Semgrep, edición de sintaxis en la API, flag de Trivy no válido para config y alias antiguo DS002 frente a DS-0002. Se corrigieron y se ejecutaron otra vez los contratos completos.
15. La PR#3 es apilada y de revisión; no se fusiona a main ni modifica /agente o producción. ReleaseGates permanece cerrado por defecto; las fixtures no rellenan la revisión independiente pendiente.
