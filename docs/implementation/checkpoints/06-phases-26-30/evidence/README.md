# Evidencias del bloque

baseline-local.json:119 descubiertos,108 correctos,11 skips. tests-local.json: suite ampliada, con Docker/SDK local omitidos por entorno. evaluation-local.json: corpus propio, fingerprint y resultados sin modelo. ci.json y evaluation-ci.json registran runs/jobs/SHA y resultados remotos realmente observados. browser-ci.json contiene artefactos sintéticos cuando se recolectan. first-regression.json conserva la primera regresión de semántica de error y su resolución.

No sumar matrices Python o push/PR como tests distintos. Los7 tests Docker se ejecutan aparte de los omitidos en runtime; SDK se instala de verdad en CI. No poner tokens, originales, secretos de clientes ni dumps completos en evidencia pública.

Cierre: código SHA06a5ddf933311da25dd8a75b65dd7af501df0e58,143 casos distintos correctos entre136 core y7 Docker. stop-ci.json documenta10/10 denegaciones tras acuse; evaluation-ci.json conserva utilidad y configuración del planner scriptado. Commit posterior solo incorpora evidencia/documentación.
