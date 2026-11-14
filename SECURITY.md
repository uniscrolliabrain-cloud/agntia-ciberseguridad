> **ACTUALIZACIÓN 2026-11-14 — ESTADO VIGENTE**
> PR #10 y #11 integraron las ramas en `main`. El repositorio dispone de demo sintética funcional, **no productiva**; las referencias a código solo proyectado o ramas no fusionadas son históricas. CI de Python 3.11/3.12, SDK, scanner Docker y navegador reejecutada en el head de implementación: SUCCESS; esto no valida seguridad independiente ni clientes reales. Fuente de verdad: `docs/release/status.json` (2 fases PASS, 40 PARTIAL), `docs/auditoria-runtime/AUDITORIA-FUNCIONAL-2026-11-14.md` y `docs/auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md`. Contrastar toda instrucción con `main` antes de actuar. **Se conserva íntegramente el documento original debajo.**

---

# Seguridad y divulgación

Estado: repositorio de investigación y diseño; no hay servicio de producción ni SLA de respuesta. No se ha configurado todavía un canal privado de divulgación.

No abrir issues públicos con credenciales, datos de clientes, muestras privadas o detalles explotables de un tercero. Usar el canal privado que el propietario configure antes del piloto. La ausencia de canal es un gate pendiente de producción.

Las auditorías futuras requieren un registro de autorización, alcance, ventanas y responsables. La validación inicial utilizará fixtures sintéticos y laboratorios aislados.
