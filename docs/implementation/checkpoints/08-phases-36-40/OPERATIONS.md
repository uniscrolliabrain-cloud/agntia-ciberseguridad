# Operación y reversión

Instalar el runtime Python como se indica en checkpoints anteriores. Configurar budget_policies por tenant solo desde servidor, con referencias revisadas de asignación/tarifa y clave de backup independiente fuera del repo. Los registros de presupuesto no llaman proveedores ni sustituyen su aprobación/hard limit.

Ejecutar tests con `python -m unittest discover -s tests -v`; SDK con `cd typescript && npm install --ignore-scripts && npm test`. En Node24 el runtime transpiler offline sirve para pruebas de ejecución; tsc es obligatorio en CI. Los contratos Python↔TS abren solo loopback con credenciales sintéticas; un sandbox que lo prohíbe produce skip explícito local y fallo en CI.

Demo: `PYTHONPATH=. python scripts/demo_synthetic.py`. Recuperación sintética: `PYTHONPATH=. python scripts/backup_restore_lab.py`. Medición: `PYTHONPATH=. python scripts/measure_workspace.py`. Navegador: `PYTHONPATH=. python scripts/browser_pilot.py` con Playwright/Chromium instalados. No usar datos reales para salvar estos gates.

Para rollback desactivar consola/rutas nuevas por routing de despliegue y detener admisión; preservar SQLite8, auditoría, reservas, outbox/receipts y ciphertext. No arrancar un binario que solo conoce schema7 contra schema8: migraciones no destructivas no equivalen a compatibilidad de todo ejecutable anterior. No borrar tablas ni liberar reservas started/inciertas para aparentar saldo. Reconciliarlas con la fuente autorizada. No quitar RESTORE_BLOCKED sin revisión offline de privacidad/revocaciones actuales, claves y efectos externos; no existe bypass web.

Los eventos no se borran por ACK; los consumidores deben registrar dedup+efecto antes de confirmar. Ledger/outbox requieren archivo/retención operativa posterior. Revisión independiente, licencias, distribución y despliegue productivo siguen pendientes. No modificar `/agente` ni fusionar esta PR por efecto de estos comandos.
