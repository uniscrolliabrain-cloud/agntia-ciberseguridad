> **ACTUALIZACIÓN 2026-11-15 — FUSIONADO EN MAIN**
> Base: `main@1e0ff5e` (2026-11-15) · 196 tests Python OK (8 skips) · SDK 6/1 · 84 rutas `/v1` · demo sintética, `production_enabled=false` · 2 PASS / 40 PARTIAL · sin PR ni revisión independiente.
> **Vigente aquí:** La decisión B (gemelo digital 43 y antivisiones 44 en paralelo a G1), la instalación y la ruta de despliegue siguen vigentes.
> **Corregido/obsoleto:** El mapa de ramas del documento quedó atrás: todo está fusionado en `main`. Los seis secretos del MVP y la autorización de `/agente` siguen pendientes.
> Estado y pendientes: [ESTADO-VIGENTE.md](../ESTADO-VIGENTE.md)

---

# Plan maestro — visión, decisión, instalación y despliegue

**Fecha:** 2026-11-15. **Estado:** documento de dirección; no implementación.
**Marco superior:** [CONCEPT-MASTER.md](CONCEPT-MASTER.md).
**Documentos operativos:** [ALINEACION-CONCEPT-MASTER.md](ALINEACION-CONCEPT-MASTER.md),
[REQUISITOS-CONEXION.md](REQUISITOS-CONEXION.md), [STACK-FINAL.md](STACK-FINAL.md),
[ARQUITECTURA-IO-FINAL.md](ARQUITECTURA-IO-FINAL.md).

Este es el documento que hay que leer primero. Resume qué estamos construyendo, qué se decidió en
los últimos turnos, qué hay que instalar para el MVP y para el producto terminado, qué claves y
permisos solo puede aportar el founder, y cómo se sale de «demo local» hasta «instalado en
`/agente`» sin saltarse controles.

---

## 1. Qué estamos construyendo

Un **sistema inmunitario digital, agéntico y evolutivo**: observa, audita, comprende, anticipa,
planifica, protege, actualiza, reconstruye, endurece, valida, despliega y aprende. No es un escáner
con informes; es una función empresarial permanente cuyo resultado es **protección ejecutable y
verificable**.

Los diez dominios: infraestructura/cloud, software/DevSecOps, IA y agentes, detección/intel/respuesta,
identidad y confianza cero, resiliencia, antifraude, gobernanza/cumplimiento, gemelo digital y
actualización/regeneración.

Tres conceptos finales: **Enterprise Digital Immune & Evolution Engine**, **Agentic Digital
Ecosystem Updater** e **Infrastructure for Collective Resilience** (micro empresa, meso ecosistema,
macro sociedad).

Regla que no cambia nunca: **el LLM propone, el runtime determinista dispone**.

## 2. Qué se dijo y se pidió en los últimos turnos

| Turno | Petición | Resultado |
|---|---|---|
| 1 | Ejecutar el programa CY-V2 desde `main` | Baseline auditado: 190 tests, 88 rutas, CI 6/6 verde; dos defectos de tooling corregidos |
| 2 | Qué se necesita de entrada/salida para el PMV | [REQUISITOS-CONEXION.md](REQUISITOS-CONEXION.md) con IDs y secretos |
| 3 | Qué E/S tendrá el producto acabado | [ARQUITECTURA-IO-FINAL.md](ARQUITECTURA-IO-FINAL.md) con siete planos |
| 4 | Qué stack y librerías | [STACK-FINAL.md](STACK-FINAL.md) con alternativas descartadas |
| 5 | «El repo que ves como final no se acerca a mi visión» | Se localiza el Concept Master y se mide la distancia |
| 6 | Consolidar visión, decisión, instalación y despliegue | Este documento |

## 3. La distancia real

El repo cubre **5 de 10 dominios** y solo dos con profundidad. Lo que falta no es «más escáneres»:

1. **Gemelo digital de negocio** — procesos, servicios críticos, proveedores y dependencias; sin
   él no se puede responder «si falla esto, ¿qué deja de funcionar?».
2. **Antivisiones** — escenarios negativos, propagación de fallos, servicios mínimos y simulacros.
3. **Flota multi-cliente** — el caso «vulnerabilidad crítica en 40 empresas»: detección agregada,
   priorización y parcheo masivo verificado.
4. **Continuidad, certificación y resiliencia meso/macro** — expediente de resiliencia reutilizable
   por clientes, auditores y aseguradores.

## 4. Decisión adoptada: opción B

**Se insertan el gemelo digital (43) y el motor de antivisiones (44) en paralelo a G1**, antes de
congelar el esquema de activos de CY-V2-12. El resto de campañas nuevas (45–48) forman **G6**.

Motivo: el gemelo digital cambia las entidades (`Asset` → `Asset + Service + Process + Provider +
Dependency`). Construirlo después obliga a migrar el grafo, los informes y los eventos. Hacerlo
ahora cuesta lo mismo que el grafo v1 y evita dos migraciones.

Qué **no** implica la decisión:

- No se reescriben las 42 campañas ni se marcan como hechas.
- No se toca `main` ni `/agente` sin autorización.
- No se promete cobertura de los diez dominios en el piloto: el piloto sigue siendo micro (empresa).

Secuencia resultante: **G0 (01–08) → G1 (09–14) + 43/44 → G2 (15–21) → G3 (22–28) → G4 (29–35) →
G5 (36–42) → G6 (45–48)**.

## 5. Qué hay que instalar

### 5.1 Para el MVP (una empresa, un host, datos sintéticos o un repo autorizado)

| Pieza | Obligatoria | Nota |
|---|---|---|
| Python 3.12 | Sí | `pip install -e '.[dev]'` |
| Node 22+ | Solo para SDK | `npm ci && npm test` en `typescript/` |
| Docker | Recomendado | Necesario para escáneres reales y tests de sandbox |
| Gitleaks, OSV-Scanner, Semgrep CE, Trivy | Sí para escaneo real | Mejor como imágenes con digest |
| `server.json` + variables de token | Sí | Sin valores por defecto; no hay owner implícito |
| Disco persistente | Sí | SQLite, evidencias y backups |
| PostgreSQL, S3, KMS, OTel | No | Se añaden en el producto terminado |

Arranque mínimo:

```bash
python -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/python scripts/validate_foundation.py
agntia-ciberseguridad serve --config /ruta/privada/server.json --host 127.0.0.1 --port 8012
```

### 5.2 Para el producto terminado

| Capa | Instalación | Campaña |
|---|---|---|
| Base de datos | PostgreSQL 16 + psycopg 3 + migraciones | 05 |
| Objetos y claves | S3/MinIO + KMS o Vault Transit | 06 |
| Identidad | OIDC del padre (sin IdP propio) | 02/38 |
| Eventos | Outbox; bus del padre cuando exista | 08/38 |
| Observabilidad | Colector OTel + Prometheus/Grafana | 17/36 |
| Escáneres | Cuatro imágenes fijadas por digest + feeds con allowlist | 04 |
| Simulación | Motor de escenarios (nuevo) | 44 |
| Flota | Gestión multi-tenant agregada (nuevo) | 45 |

## 6. Claves, secretos y permisos: qué necesito de ti

**Regla:** nada de esto se pega en el chat. Se genera y se guarda en el gestor de secretos o en el
archivo privado del host. Aquí solo están nombres y formatos.

### 6.1 Mínimo para arrancar el MVP (1 tenant, 1 humano, 1 agente)

| # | Qué abrir/generar | Nombre de referencia | Formato |
|---|---|---|---|
| 1 | Ruta del `server.json` | `AGNTIA_CYBER_CONFIG_FILE` | archivo, permisos 600 |
| 2 | Token del owner | `AGNTIA_CYBER_TOKEN_OWNER_<TENANT>` | 24–512 ASCII |
| 3 | Token del agente | `AGNTIA_CYBER_TOKEN_AGENT_<TENANT>` | 24–512 ASCII |
| 4 | Clave de evidencia | `AGNTIA_CYBER_EVIDENCE_KEY_<TENANT>` | base64 de 32 bytes |
| 5 | Clave de delegación | `AGNTIA_CYBER_DELEGATION_KEY` | ≥32 bytes aleatorios |
| 6 | Token de emergencia | `AGNTIA_CYBER_EMERGENCY_TOKEN` | ≥32 bytes, distinto de todos |
| 7 | Token de métricas (opcional) | `AGNTIA_CYBER_METRICS_TOKEN` | ≥24 caracteres |
| 8 | Acceso a Docker | grupo/socket o rootless | permiso del host |
| 9 | Cuatro imágenes con digest | `sha256:<64>` por herramienta | registry o build local |

Con **6 secretos, 4 digests y un archivo de configuración** se puede ejecutar la primera auditoría
real sobre un repositorio autorizado.

### 6.2 Para instalar en `/agente` (staging)

| # | Qué abrir | Detalle |
|---|---|---|
| 10 | Token de reviewer | `AGNTIA_CYBER_TOKEN_REVIEWER_<TENANT>` |
| 11 | Credencial de servicio del padre | principal `kind: "service"`, tenant mínimo |
| 12 | Contraseña de PostgreSQL | si se migra en esta fase |
| 13 | Credenciales S3/MinIO | bucket de evidencias |
| 14 | Clave KMS o token de Vault | cifrado de evidencias |
| 15 | Certificado TLS y hostname privado | el middleware no va a Internet |
| 16 | Cliente OIDC del padre | id/secret y callbacks |
| 17 | Permiso de PR en GitHub | **hoy el conector devuelve 403** |
| 18 | Lectura del repo padre | inventariar sesión, bus, aprobaciones, BFF |

### 6.3 Para el piloto

Licencia del código, DPA/base legal, canal privado de seguridad, fecha de revisión independiente,
alcance del piloto, operadores humanos y consentimientos por activo.

### 6.4 Lo que no puedo conseguir por ti

Claves y tokens, cuentas de proveedor, dominios y DNS, certificados, credenciales cloud del cliente,
permisos sobre `/agente`, licencia, DPA, auditor independiente, socios aseguradores y datos reales
de clientes. Sin esos elementos puedo construir y probar; no puedo desplegar ni operar.

## 7. Cómo se sale de aquí: ruta de despliegue

### M0 · Demo local (estado actual)

- 190 tests verdes, CI 6/6, datos sintéticos.
- No requiere nada tuyo.
- Salida: baseline reproducible y arquitectura documentada.

### M1 · Laboratorio propio

Requisitos: 1–9 de la tabla anterior, un repositorio autorizado y Docker.
Pasos:

1. Escribir `server.json` (plantilla en `docs/integration/server-config.example.json`).
2. Exportar las variables en el archivo privado del host.
3. Arrancar `serve` en loopback.
4. Registrar activo, consentimiento y grant.
5. Ejecutar auditoría `static_read` y comprobar findings, evidencia y reporte.
6. Probar cross-tenant: un segundo tenant debe recibir 404.

Gate: auditoría real completada con evidencia y cero acceso cruzado.

### M2 · Staging dentro de `/agente`

Requisitos: 10–18, más autorización de escritura para un PR pequeño.
Pasos:

1. Empaquetar el SDK (`npm pack`) y fijar versión.
2. Montar `cyberRoutes` detrás de la sesión/BFF del padre; el navegador nunca ve el token interno.
3. Resolver tenant y actor en servidor; mapear organización → tenant.
4. Consumir el outbox con `consumer_id`, procesar antes del ACK y deduplicar por id+hash.
5. Conectar aprobaciones del padre al `approval_id` del middleware.
6. Smoke: solicitud → capability → job → evento → proyección → respuesta de Laia.

Gate: dos tenants, aprobación humana real, replay sin duplicar efectos y rollback probado.

### M3 · Piloto con cliente

Requisitos: licencia, DPA, revisión independiente, backup/restore ensayado, operadores y alcance
firmado.
Pasos: canario interno → un cliente → dos clientes → métricas de continuidad y coste.
Gate: el founder completa el recorrido sin LLM y acepta por escrito.

### Rollback en cada etapa

- M1: parar el servicio y restaurar `data_dir` desde copia verificada.
- M2: revertir la versión del SDK en el padre y desactivar la ruta; el middleware no borra datos.
- M3: volver a la versión anterior del bundle, mantener evidencia y no borrar auditoría.

## 8. Qué cambia en el producto con la decisión B

1. **Modelo de datos:** añadir `Service`, `Process`, `Provider` y aristas de dependencia con
   procedencia; `Asset` deja de ser la entidad central única.
2. **Eventos:** nuevos tipos de dominio para proceso/servicio afectado, no solo activo.
3. **Informes:** impacto en negocio, no solo severidad técnica.
4. **Métricas:** tiempo hasta protección, tiempo hasta recuperación verificada, cobertura por
   proceso crítico y lead time de parche.
5. **Antivisiones:** entidad `Scenario` con supuestos, propagación y servicios mínimos.

## 9. Riesgos y límites que no se van a maquillar

- Sin gemelo digital completo, «impacto de negocio» será estimación, no verdad.
- Sin conectores cloud, el dominio 1 queda en `not_tested`.
- Sin flota, el caso de 40 clientes sigue siendo manual.
- La certificación de resiliencia es evidencia técnica, no certificación acreditada ni póliza.
- La resiliencia meso/macro requiere socios e instituciones; no se construye solo con software.

## 10. Próximos pasos concretos

1. Aprobar esta decisión y el orden G1 + 43/44.
2. Generar los 6 secretos del MVP y elegir el primer repositorio autorizado (M1).
3. Diseñar el esquema `Service/Process/Provider` antes de CY-V2-12.
4. Abrir el permiso de PR en GitHub (bloqueo actual del conector).
5. Autorizar lectura de `/agente` para preparar el patchset de M2.

## 11. Artefactos y para qué sirve cada uno

| Documento | Uso |
|---|---|
| [CONCEPT-MASTER.md](CONCEPT-MASTER.md) | La visión; fuente de verdad |
| Este plan | Dirección, instalación, secretos y despliegue |
| [ALINEACION-CONCEPT-MASTER.md](ALINEACION-CONCEPT-MASTER.md) | Cobertura y huecos por dominio |
| [PROGRAMA-42-CAMPANAS-FREEBUFF.md](PROGRAMA-42-CAMPANAS-FREEBUFF.md) | Ejecución del sustrato |
| [REQUISITOS-CONEXION.md](REQUISITOS-CONEXION.md) | Checklist detallada de conexión |
| [ARQUITECTURA-IO-FINAL.md](ARQUITECTURA-IO-FINAL.md) | Planos de E/S del sustrato |
| [STACK-FINAL.md](STACK-FINAL.md) | Stack y librerías |
| [BASELINE.md](BASELINE.md) | Estado técnico verificado |
