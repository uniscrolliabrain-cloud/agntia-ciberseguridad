# HANDOFF EJECUTABLE — CY-VS
## Instrucción principal para FreeBuff/Codex/Cline
Eres el ejecutor técnico del repositorio `uniscrolliabrain-cloud/agntia-ciberseguridad`. **No te limites a escribir documentación.** Debes auditar primero el HEAD real y TODAS las ramas; después ejecutar **en secuencia** las campañas CY-VS-00 a CY-VS-08 de `01-CAMPANAS-SECUENCIALES.md`, implementando código y pruebas que falten, reutilizando todo lo existente, sin recrear un middleware ni importar el laboratorio al proceso de servicio.

### Rama, commits y límites
1. `git fetch --all --prune`; `git status --short`; registrar `git rev-parse HEAD`; `git switch main && git pull --ff-only`; `git switch -c feat/cyber-vertical-slices-installable-20261120` **solo si esa rama no existe**. Si ya existe, verificar propietario/estado y continuar sin sobreescribir. No trabajar en `main`.
2. Leer íntegramente `00-REAUDITORIA-Y-ESTADO.md`, `01-CAMPANAS-SECUENCIALES.md`, `02-CUENTAS-Y-CONECTORES.md`, los documentos CP y el programa CY-IP, además de README, tests, manifests, workflows y release. Inspeccionar `agente` en **solo lectura** al SHA actual y comprobar qué patchsets P1–P6 ya existen; no asumir documentación histórica.
3. Para cada campaña: baseline → código mínimo → tests positivos/negativos → typecheck/lint → evidencia → reportes → commit en la rama → mensaje de chat con resumen y enlace → siguiente campaña. **Nunca hacer merge a main, publicar paquete, crear cuentas, desplegar ni tocar repos externos sin aprobación.**
4. Usar los nombres/rutas reales encontrados. Las rutas en el programa son objetivos; si el código ya ofrece una capacidad, verificar y añadir solo integración o tests. Evitar secretos reales, comandos de extracción de secretos y salida de valores.
5. Ante dependencia externa: implementar interfaz, config, stub fail-closed, fake para tests, smoke que pueda ejecutar el founder tras configurar credenciales; registrar `BLOCKED_FOUNDER` con acción concreta. Continuar con la siguiente campaña que no dependa de ese servicio. No convertir `BLOCKED` en `PASS`.
6. Si hay defecto de aislamiento, fuga, aprobación omitida, doble efecto o error crítico: STOP, crear reporte, no continuar con acciones externas; informar en chat. No ejecutar scans fuera de fixtures o activos propios autorizados.
7. CI debe comprobar Python 3.11/3.12, SDK Node >=22, pruebas de contratos y aislamiento, artefacto reproducible, manifests y gates. No atribuir al HEAD resultados de un SHA anterior.
8. Mantener `docs/release/status.json` como NO-GO hasta evidencias reales, revisión independiente y autorización del founder. Entregar PR al final, sin merge.

### Mensaje de chat obligatorio al terminar **cada** campaña
`CY-VS-XX | COMPLETE/PARTIAL/BLOCKED | branch@SHA | cambios (archivos) | tests realmente ejecutados (pass/fail/skip) | gate | stubs | decisiones/cuentas founder | reporte (link) | siguiente CY-VS-YY`.
No esperar a terminar nueve campañas para informar. Si la herramienta no permite mensajes intermedios, detener la ejecución al final de cada campaña para informar antes de continuar.

### Definition of Done
Dos verticales defensivas completas como mínimo (scan→finding→report y finding→proposal→approval→retest), tercera sintética si viable; SDK instalable y reproducible; integración al padre lista como patchset y contract tests, sin falsa afirmación de wiring real; configuración de proveedores preparada hasta secret refs; stubs seguros; test y reporte por campaña; handoff final con comandos exactos, prerequisitos, versiones, SHA, rollback, gaps, costes y tareas del founder. Todo en rama y PR, nada en main.
