# Evidencias

performance-local.json: medición ASGI sintética por plan; no benchmark de scanners ni coste real. dependencies-local.json: inventario de distribuciones directas, no auditoría de CVE/licencia. tests-local.json: conteos/entorno del wrapper unittest, con skips explícitos. ci.json se añadirá después de consultar jobs del SHA implementado; no hereda resultados de la rama anterior. Los scripts demo/recovery invocan casos ya contados; no duplicar el total. No publicar logs íntegros con datos de clientes, tokens ni claves.
