# Riesgos residuales

- Revisión independiente pendiente; no se habilita ejecución para clientes.
- kind=human es declaración de configuración, no identidad verificada mediante IdP/MFA. Quien controla configuración y tokens controla el principal.
- Redacción falible; no anonimización garantizada, malware scanning ni limpieza de documentos. PDF permanece en cuarentena.
- Variables de entorno sirven para el piloto; KMS, rotación operativa, recuperación y separación de operadores pendientes. Backups deben incluir claves por canal separado y controles de acceso.
- SQLite guarda metadatos y resultados normalizados; AES-GCM de evidencias no cifra todo el servicio. Se necesita cifrado de disco/backup y política legal concreta por cliente.
- Hash chain local no resiste reescritura por administrador que controle DB/proceso. No hay anclaje externo firmado desplegado.
- Una caída durante purga deja purge_pending y requiere reconciliación operativa antes de repetir; no restaurar lectura saltando la comprobación de retención.
- Carrera entre procesos al generar el mismo informe puede dejar una evidencia cifrada huérfana, aunque el índice UNIQUE impide dos informes con misma fuente. Falta recolector/reconciliador de huérfanos aprobado.
- verified_fixed se limita a misma regla/ruta/herramienta/política y snapshot; no prueba que desapareciera todo el riesgo. Scans no completos no sirven como retest válido.
- Fuentes de riesgo externas no implementadas. No se infiere explotación, CVSS, KEV o EPSS.
- Métricas en memoria se reinician al reiniciar proceso; Prometheus debe conservar sus muestras. Multiworker y agregación distribuida no validados. Queue lag se consulta por tenant, no implica alerta global desplegada.
- SDK ausente local: cuatro tests omiten explícitamente; CI instala la dependencia real. Dependencias runtime son obligatorias en instalación soportada.
- ALWAYS_ON no representa política de costes/privacidad para producción. Cola finita descarta y contabiliza; debug exporter no sustituye almacenamiento de trazas ni retención.
- Laboratorio Docker no equivale a aislamiento revisado independientemente; sin datos de clientes.
