# Gates21–25

Se mantienen PARTIAL aunque los tests de mecanismos concretos pasen. El sistema no consigue paridad mundial ni cumplimiento legal automático con estas fases.

- D4P3: schema cerrado, filas/bytes limitados, cursor secuencial y retención/hold actual probados; logs externos no se ingieren como texto libre. Pendiente backend y política continua de hold/retención por cliente.
- D4P4: UI autenticada por tenant y pruebas Chromium móvil/escritorio; unknown/stale visibles. Falta vista completa finding→evidencia y operativa de trace backend. No se instala Grafana; decisión y licencia documentadas.
- D4P5: fixture webhook real a API con HMAC, replay/out-of-order, fuente revocada y429. No se anuncian sensores, conectores cloud ni cobertura EDR. Firma es simétrica y verifica posesión de clave, no verdad de observación.
- D4P6: ráfaga sintética y fallos opcionales no relajan policy; métricas de drops visibles. Disco físico lleno, WAL/backups, carga distribuida y costes reales NO VERIFICADOS. No gateG4 global.
- D5P1: dos humanos para manifest; token de lectura firmado, sujeto/audiencia/TTL, scope atenuado, revocación y carreras. Solo camino delegado; no se declara todo agente protegido frente a rutas ajenas. Gateway completo pendiente.

La revisión independiente sigue pendiente. ReleaseGates permanece cerrado para clientes. Queda prohibido interpretar PARTIAL como permiso de despliegue.
