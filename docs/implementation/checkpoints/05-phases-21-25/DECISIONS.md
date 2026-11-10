# Decisiones

1. Logs sin campo mensaje: el contenido no permitido se descarta y no se intenta resolver redacción universal. Audit y evidencia tienen políticas distintas.
2. SQLite aditivo schema5, índices y secuencia monótona de logs/eventos. No se despliega un segundo datastore ni scheduler.
3. Consola propia mínima para Lite/L/XL, sin Grafana instalado. La adopción futura de Grafana requiere revisar AGPL-3.0 y separar credenciales/datasources. No se degrada aislamiento por precio.
4. Señales de fuente con HMAC canónico, audiencia fija y clave distinta por fuente. Solo campos cerrados de observación; no endpoint para shell/rawlogs. OTel sigue siendo observabilidad y no identidad de una fuente de eventos.
5. Acuse no confirma incidentes. Cola llena rechaza con429; límites totales obligan a operación de mantenimiento antes de crecer.
6. Manifest declara versión/hash/esquema conocidos; no descarga ni ejecuta skills. La aprobación requiere otro principal humano, sujeto a limitaciones del binding kind heredado.
7. Sobre firmado y registro persistente de un uso; HMAC del token es diferente del bearer de actor. Permisos del padre solo pueden atenuarse y la cadena se revalida en cada consumo.
8. No resolver secretos de proveedores donde no hay un ejecutor gobernado. Este bloque entrega lecturas seguras y deja la ejecución general al gateway posterior.
9. Las pruebas browser se intentaron localmente. Al quedar bloqueadas por sockets se trasladan a CI con Chromium real y capturas sintéticas.
10. No repetir merge/main ni conexiones a otros repos: PR#5 apilada sobre PR#4. El reinicio conservó commit local y se comprobó remoto antes de retomar publicación.
