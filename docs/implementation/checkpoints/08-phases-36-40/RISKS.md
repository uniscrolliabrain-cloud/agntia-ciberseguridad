# Riesgos y pendientes

- Ledger solo conoce costes declarados y reservas admitidas. No mide facturas/infra automáticamente ni impide un cobro de un proveedor externo no integrado. Las tarifas/márgenes de producción requieren revisión y límites reales.
- SDK/Hono depende de autenticación y resolver de confianza del host, red privada y egress administrado; no dar esos callbacks a modelos. Tools usan principal kind=agent, nunca owner prestado. Tokens manuales de consola son solo piloto.
- Consumidor sintético no acredita ACK/cursor correctos en el Event Bus real. Catálogo parcial; no hay push/delivery supervisor.
- Restore parcial omite snapshots/candidatos y necesita escritores detenidos. La copia antigua puede contener restricciones/revocaciones obsoletas; RESTORE_BLOCKED no debe retirarse automáticamente. No hay RTO/RPO productivo.
- Los E2E nuevos usan resultado de scan sintético y no prueban de una vez todos los conectores reales. Docker separado no se convierte en una demo única grabada.
- Inventario directo de dependencias no es SBOM transitivo ni scan de CVE completo. Licencia propia, revisión de terceros, WCAG y revisión independiente pendientes.
- SQLite es single-node. No se ofrece coordinación distribuida, despliegue ni SOC24/7. Se conservan límites de fases anteriores.
