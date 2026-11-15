> **ACTUALIZACIÓN 2026-11-15 — LEE ESTO ANTES DEL TEXTO**
> Base medida: `main@dd18f2a` + AD-01 `c57251c` · 196 tests Python OK (8 skips) · SDK 6/1 · 84 rutas `/v1` · esquema 8 · demo sintética, `production_enabled=false` · 2 PASS / 40 PARTIAL · sin PR ni revisión independiente.
> **Vigente aquí:** No hay canal privado de divulgación todavía; no abrir issues públicos con datos sensibles. Ese gate sigue pendiente.
> **Corregido/obsoleto:** Los 196 tests y el baseline AD-01 no constituyen auditoría de seguridad ni cambian el estado de divulgación.
> Mapa de ramas, contradicciones y pendientes: [ESTADO-VIGENTE.md](docs/ESTADO-VIGENTE.md)

---

> **ACTUALIZACIÓN 2026-11-14 — ESTADO VIGENTE**
> PR #10 y #11 integraron las ramas en `main`. El repositorio dispone de demo sintética funcional, **no productiva**; las referencias a código solo proyectado o ramas no fusionadas son históricas. CI de Python 3.11/3.12, SDK, scanner Docker y navegador reejecutada en el head de implementación: SUCCESS; esto no valida seguridad independiente ni clientes reales. Fuente de verdad: `docs/release/status.json` (2 fases PASS, 40 PARTIAL), `docs/auditoria-runtime/AUDITORIA-FUNCIONAL-2026-11-14.md` y `docs/auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md`. Contrastar toda instrucción con `main` antes de actuar. **Se conserva íntegramente el documento original debajo.**

---

# Seguridad y divulgación

Estado: repositorio de investigación y diseño; no hay servicio de producción ni SLA de respuesta. No se ha configurado todavía un canal privado de divulgación.

No abrir issues públicos con credenciales, datos de clientes, muestras privadas o detalles explotables de un tercero. Usar el canal privado que el propietario configure antes del piloto. La ausencia de canal es un gate pendiente de producción.

Las auditorías futuras requieren un registro de autorización, alcance, ventanas y responsables. La validación inicial utilizará fixtures sintéticos y laboratorios aislados.
