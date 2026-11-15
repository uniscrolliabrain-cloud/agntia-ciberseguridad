# 04 — Handoff para el agente ejecutor (Freebuff/Codex)
## Mandato
Trabaja en `uniscrolliabrain-cloud/agntia-ciberseguridad`. La documentación de coordinación vive en `docs/auditoria-y-plan-operativo-cyber-20261115` bajo `docs/guia-operativa-founder-agente-2026-11-15/`. **No modifiques main, no fusiones PR, no despliegues, no uses datos de clientes ni ejecutes pruebas activas fuera de gemelos sintéticos sin aprobación expresa.** No borres ramas históricas. El trabajo adversarial existente está en `feat/advlab-campaigns-C01-C18`; deriva nuevas ramas de código de ese HEAD si es necesario, conservando su historia.

## Protocolo de sesión
1. Lee todos los archivos de este folder, `AGENTS.md`, `README.md`, `docs/release/status.json`, auditoría diferencial y reporte advlab.
2. Fija y escribe SHAs, versión Python, SO, dependencias, permisos y entorno; comprueba que no hay secretos en logs.
3. Crea `work/advlab-A01-baseline-<fecha>` desde `feat/advlab-campaigns-C01-C18`. Cada siguiente fase usa rama nueva desde base aprobada, no apiles sin registrar dependencias.
4. Inspecciona el código real antes de planificar patches; el informe es hipótesis hasta reproducir.
5. Ejecuta comandos solo con red cerrada y datos sintéticos. No cambies `ADVLAB_ALLOW_NETWORK` a true.
6. Escribe `docs/guia-operativa-founder-agente-2026-11-15/reports/<ID>-REPORT.md` en rama de trabajo, incluyendo el diff y las pruebas; no uses `PASS` sin exit/log.
7. Abre PR pequeño; solicita revisión independiente de P0 y autorización del founder para merge.
8. Si una herramienta o proveedor no está disponible, devuelve `BLOCKED` y dependencia exacta; no simules un éxito.

## Formato obligatorio de reporte
```md
# <ID> — <título>
Base SHA: | Work SHA: | Branch: | Fecha:
Objetivo / Alcance / Exclusiones:
Archivos inspeccionados:
Archivos modificados y por qué:
Contratos y trust boundaries:
Pruebas (comando, versión, exit, resultado, log path):
Resultados: PASS / FAIL / PARTIAL / BLOCKED / NOT_VERIFIED
Hallazgos y severidad:
Riesgos residuales:
Coste medido:
Rollback comprobado:
Gate de seguridad: GO / NO-GO / BLOCKED
Decisiones que debe tomar el founder:
Siguiente campaña:
```

## Prohibiciones y escalado
- No interpretar un permiso de repo como permiso de ataque a activos.
- No introducir claves en código, commits, issue comments ni prompts.
- No cambiar scores para lograr verde ni eliminar tests que fallan.
- No usar `subprocess` local para cargas hostiles.
- No ejecutar `pip install` desde fuentes no fijadas en hosts de producción.
- No habilitar red, SSH al cliente, escáner activo, email real o API de terceros sin alcance autorizado.
- No automatizar compra, merge, despliegue, eliminación de evidencia ni aceptación de riesgos.
- Parar ante fuga de tenant, ejecución fuera de scope, doble efecto, clave expuesta o sospecha de escape. Registrar incidente con mínimo de datos.

## Primer encargo concreto: A01+A02
Inventariar diff 125 archivos, comparar implementación con 18 campañas, ejecutar tests y producir matriz de evidencia. No escribir nuevas 18 campañas ni comenzar integraciones antes de terminarlo.
