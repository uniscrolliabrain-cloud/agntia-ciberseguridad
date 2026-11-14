# Fronteras de confianza y owners

| Frontera | Control presente | Responsable de continuación | Comprobación pendiente |
|---|---|---|---|
| Cliente → API | Body acotado, DTO cerrado, Bearer explícito | Backend/operaciones | TLS, rate limiting y cabeceras globales |
| Principal → tenant | Binding servidor, rol, revocación antes del efecto | Identidad | Identidad delegada real de `/agente` |
| Titular → grant | Configuración administrativa, hash, revisor distinto | Seguridad/owner | Custodia jurídica de consentimiento real |
| Activo → repo | Referencia aprobada, ruta resuelta dentro de raíz | Adquisición D2P1 | Snapshot inmutable y carrera de filesystem |
| URL → red | Prefijos, CIDRs, DNS completo, metadata/redirect bloqueados | Runner D2P2 | Conexión real fijada a IP/TLS, egress de sandbox |
| API → estado | SQLite/FKs/BEGIN IMMEDIATE/audit/backup | Datos | Cifrado y backups de despliegue |
| Estado → informe | Verificador de cadena local | Evidencia D3P4 | Originales y anclaje externo |
| Código/herramienta → ejecución | Ninguna ruta habilitada | Sandbox D2P2 | Docker real aislado y revisión independiente |
| LLM → acción | Sin integración LLM; cuerpos no dan identidad | Gateway D5 | Evaluaciones adversariales y autorización por efecto |
| Solicitud → gasto | Máximo por grant, preflight sin gasto | Presupuesto D6P6 | Reserva/settlement y reconciliación reales |

El Docker del entorno existe pero su socket no es accesible. No se ha montado, expuesto ni evitado esa restricción. El contenedor de la API nunca debe recibir un socket privilegiado: el diseño de runner requiere otro servicio aislado y revisión.

Una gráfica de arquitectura o un catálogo de escenarios no prueban estas fronteras futuras. Ver `THREAT-MODEL.md` y el estado machine-readable de la campaña. Ningún test de foundation cuenta como test de escáner, SOC o cumplimiento legal.

## Actualización del segundo checkpoint

Snapshots locales con hashes/custodia y perfiles Docker offline ya tienen pruebas sintéticas, incluidas cuatro reales en CI. La tabla anterior conserva las fronteras de diseño; consultar [checkpoint6–10](checkpoints/02-phases-06-10/REPORT.md) para evidencia y pendientes vigentes. El launcher no está desplegado como worker de clientes y la revisión independiente sigue pendiente.
