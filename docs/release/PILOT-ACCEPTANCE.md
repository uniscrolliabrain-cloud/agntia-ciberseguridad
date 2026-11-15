> **ACTUALIZACIÓN 2026-11-15 — LEE ESTO ANTES DEL TEXTO**
> Base medida: `main@dd18f2a` + AD-01 `c57251c` · 196 tests Python OK (8 skips) · SDK 6/1 · 84 rutas `/v1` · esquema 8 · demo sintética, `production_enabled=false` · 2 PASS / 40 PARTIAL · sin PR ni revisión independiente.
> **Vigente aquí:** La lista de bloqueos para clientes reales sigue completa y sin resolver.
> **Corregido/obsoleto:** AD-01 no acepta nada: PR, revisión independiente, licencia, DPA, operadores y wiring de `/agente` siguen pendientes.
> Mapa de ramas, contradicciones y pendientes: [ESTADO-VIGENTE.md](../ESTADO-VIGENTE.md)

---

> **ACTUALIZACIÓN 2026-11-14 — LECTURA OBLIGATORIA ANTES DEL DOCUMENTO HISTÓRICO**
> Las ramas de implementación y recuperación se integraron en `main` mediante PR #10 y #11. Las menciones a ramas sin fusionar, PR apiladas y capacidades ausentes pueden estar obsoletas. Estado actual: demo sintética, **no producción**; CI reejecutada en el head de implementación con Python 3.11/3.12, SDK, Docker scanner y navegador en verde. Esto no constituye aceptación independiente ni piloto. `docs/release/status.json`: 2 fases PASS, 40 PARTIAL. Para trabajo nuevo, consultar `docs/auditoria-runtime/AUDITORIA-FUNCIONAL-2026-11-14.md` y `docs/auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md`, verificar el HEAD de `main`, evitar duplicar trabajo y preservar gates pendientes. **Texto histórico original conservado íntegramente debajo.**

---

# Aceptación pendiente: demo sintética

Clasificación actual: SYNTHETIC_DEMO_NOT_PRODUCTION. La implementación cubre aspectos de las42 fases; no hay42 gates completos ni paridad universal con líderes. Ningún resultado de CI constituye aceptación humana de clientes/producción. Las PR permanecen draft y apiladas. No se pide aceptación de un resultado que aún no exista; este documento es el checklist concreto para la revisión posterior del owner.

Criterios reproducibles: seleccionar SHA y artifact correctos; verificar atestación y manifiesto/hashes; instalar Python desde wheelhouse en venv limpia y SDK desde tarball; ejecutar smoke fuera del checkout; revisar fuentes, límites y matriz; reproducir permisos/cross-tenant y ausencia de cobertura sin datos; conservar evidencia y demostrar recuperación en directorio nuevo. Los jobs se registran en checkpoint9, incluidos fallos/BLOCKED si aparecen. No elevar un gate de plataforma que no se ejecutó.

Antes de datos reales faltan aceptación independiente de seguridad, licencia propia elegida, revisión de licencias/reglas/feeds y prestación comercial, canal privado de seguridad, DPA/contratos, custodia/retención/derechos completos, operadores y escalado, backups productivos completos y restores con claves/revocaciones actuales, alertado/observabilidad operativa, límites reales de proveedores y gasto total, autenticación/BFF y wiring autorizados en AgntiaPro. Asignar persona/fecha/evidencia a cada uno; no inventar nombres de responsables.

Decisiones del owner pendientes: licencia; canal de divulgación privado; qué entorno se acepta como laboratorio; responsables humanos; alcance de piloto con clientes y condiciones contractuales; autorización separada para modificar `/agente`, fusionar PRs y desplegar. Nada de eso se ejecuta por el mero cierre documental. Se permite revisar/reproducir esta demo aislada dentro de la autorización ya dada.
