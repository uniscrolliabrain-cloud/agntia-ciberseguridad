# Checkpoint9 — fases41–42

Baseline remoto6146077ae0d2df585d5db633d28959e4ec6033ab, árbol b85aa439b49cc0a74501e002e4be7f09f075f6f8, idéntico al checkout al comenzar. Rama feat/cyber-phases-41-42 apilada sobre36–40. Último bloque de implementación de la campaña; gates pendientes conservados. No se modifica `/agente`, main, datos de clientes, secretos ni producción.

D7P5 implementa bundle específico de plataforma con wheelhouse y requirements.lock de hashes, SDK tarball, manifiesto, SHA256SUMS, CycloneDX1.5 y notices de metadata. El builder exige checkout limpio y destino nuevo. Instala Python offline en una venv temporal fuera del checkout; ejecuta módulo con -I y comprueba que no importó código editable. Instala SDK en consumidor temporal y carga cliente/Hono. Los recursos estáticos/esquemas/catálogo legal se verifican dentro del paquete. No se publica a npm ni registry.

La imagen API consume solo wheelhouse/lock, instala sin red, usa usuario65532:65532 y no incluye socket Docker, checkout o secretos. CI resuelve tag Python exacto a digest inmutable y registra imageID/smoke; Compose ofrece loopback/red interna, no-new-privileges, read-only y límites por perfil. Scripts Linux/PowerShell son comprobadores, no cambian políticas globales ni destruyen estado. Windows paquete y Linux container son gates distintos; no se atribuye soporte a Docker Desktop/ARM/macOS sin ensayo.

La atestación GitHub del manifiesto se solicita solo en push y con permisos limitados al job dedicado. Su ejecución y verificación se registran, no se presuponen por escribir el YAML. Hashes verifican integridad; autenticación del publisher exige verificar provenance y SHA/workflow correctos. SBOM enumera archivos/wheels y dependencias npm, no aporta por sí solo auditoría de vulnerabilidades/licencias. Builds futuros pueden resolver otras versiones; el bundle concreto queda fijado por hashes. Instalación SDK usa npm/caché, no es offline integral.

D7P6 entrega founder report, estado42/294, comparación con líderes sin paridad inventada, aceptación pendiente, compatibilidad y backlog30/60/90. Clasificación SYNTHETIC_DEMO_NOT_PRODUCTION. Licencia propia, canal privado, contratos/DPA, revisión independiente, custodia/restore productivo, responsables y wiring real permanecen abiertos. No se solicita aprobación para trabajo hipotético ni se despliega por cerrar la campaña.

Pruebas nuevas: integridad de bundle ante extra/tamper/traversal; wheel inventory único/con proyecto; smoke API/recursos/scopes. Suite local y CI se registran en evidence/; la instalación editable local no acredita una instalación limpia. Docker local falla por permiso al socket; CI usa su daemon aislado. Firma, Windows y container quedan NOT_VERIFIED hasta recibir sus jobs. Las pruebas de3.11/3.12, scanners, browser y collector se vuelven a comprobar para el SHA publicado.

Ver [runbook](../../../operations/RUNBOOK.md), [rollback](../../../operations/ROLLBACK.md), [informe founder](../../../release/FOUNDER-REPORT.md), [aceptación](../../../release/PILOT-ACCEPTANCE.md) y [compatibilidad](../../../release/COMPATIBILITY.md). El próximo trabajo es cerrar backlog/gates y revisar PRs, no inventar una fase43 ni habilitar clientes.

## Corrección Windows y resultados observados

Primer SHA5dc6e7e: Linux completó bundle/venv limpia/SDK/SBOM/container. Windows completó bundle/instalación/SBOM, pero el comprobador documental falló al decodificar UTF-8 con cp1252. Se conservan run/job y causa en evidence/first-windows-failure.json. La revisión6ad9b971 corrigió lecturas explícitas UTF-8, modo del proceso Python en PowerShell y LF mediante .gitattributes: los seis workflows pasaron, incluido paquete Windows y atestación Linux. Se amplía después el job para atestar/verificar también el manifiesto Windows; el SHA final6ff332cb y sus resultados se registrarán en evidence/ci.json.

Las tres validaciones locales Compose config --quiet (Lite/L/XL) pasan sin daemon o contenedores. El bundle Linux inicial fue descargado y verificado por hashes localmente; no se ejecutó código de artefacto durante esa comprobación. Publisher verification queda separado de checksum y de aceptación del producto.

Suite local:190 casos descubiertos,177 correctos,13 skips (8 Docker,4 SDK local,1 loopback). Runtime remoto6ad9b971:190 descubiertos,182 núcleo correctos y8 Docker correctos aparte, cero fallos. Tsc/Hono/contrato HTTP, Chromium/collector y matrices conservan sus propios jobs y no se suman duplicados. La compatibilidad final es la acotada en la matriz, no soporte universal de Windows.

## Cierre remoto definitivo

SHA probado `6ff332cba6622dfaef9faafac2ada7e702f5c263`: seis workflows de push SUCCESS.190 casos Python distintos correctos:182 núcleo y8 Docker aparte; matriz3.11/3.12 sin sumar duplicados. Instalación limpia Python/SDK en Ubuntu y Windows,39 wheels por bundle, lock por hashes y SBOM1.5 validados. Imagen Linux no root/read-only/network=none correcta. Los manifiestos Linux y Windows se atestaron y verificaron ambos con gh; no extrapolar la firma de uno al otro. IDs, hashes y expiración de artifacts, image/base digest y jobs están en [evidence/ci.json](evidence/ci.json) y [runtime-image.json](evidence/runtime-image.json).

La entrega completa está publicada en PR#9, draft y apilada. Los commits posteriores de cierre son documentales; no cambian el código probado. Se han recorrido las42 fases y consolidado294 tareas:2 gates históricos PASS,40 PARTIAL. No queda una fase sin abordar, pero sí gates/alcances abiertos. Clasificación demo sintética, no piloto de clientes ni producción aceptados. No se ha modificado `/agente`, fusionado main, comprado servicios o desplegado.
