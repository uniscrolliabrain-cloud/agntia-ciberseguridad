# Evidencias

baseline-local.json:103 descubiertos,92 correctos,11 skips. tests-local.json:116 descubiertos,105 correctos,11 skips. load-local.json: carga sintética concurrente y fallo opcional; no SLA. browser-local-blocked.json: intento real bloqueado por socket del sandbox. ci.json y browser-ci.json contienen resultados remotos realmente observados, SHA/runs/jobs y capturas sintéticas cuando disponibles. Fallos conservados por separado.

No guardar tokens, logs de clientes ni originales. Versiones Python/push/PR duplicadas no suman tests distintos. Las7 pruebas Docker se omiten en runtime y se ejecutan aparte. La prueba browser no es una auditoría completa de accesibilidad o frontend.

Cierre: ci.json prueba119 casos distintos sobre SHA ca6ae9a471d90ce7c987666b7104b88637afbe07; load-ci.json registra SDK activo y presión/fallo opcional; browser-ci-final.json contiene el artefacto final y hashes. El commit posterior solo incorpora estas evidencias/documentación.
