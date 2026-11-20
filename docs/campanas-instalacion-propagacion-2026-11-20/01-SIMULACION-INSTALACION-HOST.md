# 01 · Simulación de instalación en el host

**Campañas cubiertas:** IP-01, IP-02, IP-03. **Estado:** SIMULADO, NO EJECUTADO.
**Destino simulado:** copia no productiva de `agente` en el commit de referencia
`3f15ca824af29ce15680c561fed3d7134c49b812`, en anillo B. Ningún comando de esta página se ha
lanzado contra ese repositorio.

## 1. Escenario

| Elemento | Valor simulado |
|---|---|
| Host | `agente-staging`, sin tráfico de clientes |
| Tenant | `lab-cyber`, sintético |
| Paquete | `@agntia/ciberseguridad@0.1.0-alpha.3` |
| Artefacto | pack generado por `npm run pack:deterministic` |
| Enforcement | apagado; solo lectura gobernada |
| Ventana | 2 días de observación antes de cerrar IP-03 |
| Responsable | equipo del hijo para el paquete; equipo del padre para el host |

## 2. Línea temporal

| Momento | Acción | Criterio de continuidad |
|---|---|---|
| D-5 | Preflight de inventario y permisos | Inventario completo, sin secretos en claro |
| D-3 | Verificación del artefacto | Digest y procedencia coinciden |
| D-2 | Instalación en laboratorio (anillo A) | Dos tenants sintéticos aislados |
| D-1 | Configuración del host por referencia | Arranque fail-closed con una referencia ausente |
| D0 | Instalación en staging y sombra | Contrato vivo verde, sin enforcement |
| D+1 | Observación | Sin cruces de tenant ni errores 5xx inexplicados |
| D+2 | Cierre o aborto | Gate G1–G4 revisado y evidencia archivada |

## 3. Fase A · Preflight

**Objetivo:** saber qué se va a instalar, dónde y con qué permisos, antes de escribir nada.

Comprobaciones simuladas:

1. SHA del host y del paquete; versión de Node y del runtime del host.
2. Rutas del host que consumirán el SDK: resolver de sesión, cliente servidor, BFF.
3. Variables de entorno referenciadas y su origen en el secret manager (solo nombres).
4. Migraciones del hijo que la instalación espera encontrar; ninguna se aplica al host.
5. Flags existentes y su valor por defecto; se exige que la nueva capacidad nazca apagada.
6. Ausencia de credenciales en el plan, en logs y en el repositorio.

**Salida esperada:** `IP-00/inventario.json` con SHA, rutas, versiones y nombres de variables.
**Aborto:** cualquier secreto en claro, ruta inexistente o versión no soportada.

## 4. Fase B · Verificación del artefacto

Secuencia simulada, escrita para que un revisor la ejecute después:

```bash
cd typescript
npm ci --ignore-scripts          # esperado: exit 0, lockfile sin cambios
npm test                         # esperado: 12 casos, 10 pass, 2 skip, 0 fail
npm run provenance:check         # esperado: exit 0, digest coincide
npm run pack:deterministic       # esperado: dos ejecuciones, mismo SHA256
sha256sum .pack/*.tgz            # esperado: igual al digest registrado en IP-01
```

Notas de la simulación:

- El último digest medido del pack fue `09c94d52a5fa813cb93fc92e3864317abcab5332edc3c5c2f2b8ec98763dbcf7`
  (2026-11-18, 9 272 bytes, 11 entradas). **No se reutiliza como evidencia de hoy**: al ejecutar
  de verdad debe recalcularse y compararse con `PROVENANCE.json`.
- `npm ci --ignore-scripts` es obligatorio: un `postinstall` de dependencia no revisada no debe
  ejecutarse en la instalación.
- Si `PROVENANCE.json` no coincide con `dist`, el artefacto se descarta; no se "regenera para que
  pase". Regenerar procedencia para ocultar una diferencia es un fallo de gate, no una corrección.

Desde el 2026-11-20 la verificación tiene implementación: `scripts/install_manifest.py build`
genera el manifiesto y `scripts/verify_artifact.py` comprueba tamaño, digest, entradas del tar y
coherencia con `PROVENANCE.json`. La secuencia de esta sección sigue **sin ejecutarse en un host**:
el único artefacto verificado es el pack del árbol.

**Aborto:** digest distinto, tests en rojo o skip nuevo no explicado.

## 5. Fase C · Instalación en laboratorio

En anillo A se instala el artefacto como dependencia local del host sintético, nunca desde un
registro público:

```bash
# simulado: host sintético, sin red externa
npm install --ignore-scripts /ruta/al/pack/agntia-ciberseguridad-0.1.0-alpha.3.tgz
node -e "require('@agntia/ciberseguridad')"   # esperado: carga sin efectos de red
```

Verificaciones:

1. El paquete no abre conexiones al importarse.
2. El cliente rechaza `http://` fuera de loopback y rechaza credenciales en URL.
3. Una llamada sin delegación devuelve rechazo, no datos.
4. Dos tenants sintéticos no comparten activos, findings ni jobs.
5. La parada del proceso no deja leases ni jobs en estado inconsistente.

**Salida esperada:** `IP-02/instalacion.log` y `IP-02/aislamiento.txt` con los cinco casos.
**Aborto:** cualquier lectura cruzada, cualquier conexión saliente no declarada.

## 6. Fase D · Configuración por referencia en el host

La configuración del host se describe como contrato, no como parche:

| Referencia | Contenido | Quién la provee |
|---|---|---|
| `AGNTIA_CYBER_BASE_URL` | Origen HTTPS del middleware | Operación del host |
| `AGNTIA_CYBER_TENANT` | Tenant fijado por el servidor | Resolver de sesión |
| `AGNTIA_CYBER_CREDENTIAL_REF` | Referencia al secret manager | Operación |
| `AGNTIA_CYBER_ORIGINS` | Allowlist de orígenes del host | Operación |

Reglas simuladas:

- El navegador no elige tenant, origen ni credencial; los fija el servidor.
- Un valor ausente o mal formado impide el arranque; no se cae a un valor por defecto inseguro.
- La credencial se lee en el momento de la llamada y no se escribe en logs, trazas ni respuestas.
- El host no reenvía `Authorization`, cookies ni `tenant_id` del cliente como prueba de identidad.

**Prueba negativa obligatoria:** arrancar sin `AGNTIA_CYBER_CREDENTIAL_REF` y comprobar que el
host falla cerrado con un error explícito. Si arranca, la instalación no cumple G2.

## 7. Fase E · Sombra

Con el host ya instalado, la capacidad se enciende en **sombra**:

1. El host calcula qué decisión tomaría para cada lectura.
2. Registra decisión, política y versión, sin aplicarla.
3. No se envía nada al middleware que no sea una lectura nominada.
4. Se compara durante 24 horas la decisión calculada con la acción permitida.

**Salida esperada:** `IP-03/sombra.json` con conteos de coincidencia y divergencia.
**Aborto:** divergencia sin explicación, decisión que depende de texto de un modelo o error de
tenant en la decisión.

## 8. Fallos inyectados

| # | Fallo | Cómo se inyecta | Respuesta esperada | Gate |
|---|---|---|---|---|
| 1 | Digest distinto | Alterar un byte del pack | Instalación abortada; artefacto descartado | G2 |
| 2 | Referencia ausente | Quitar `AGNTIA_CYBER_CREDENTIAL_REF` | Arranque falla cerrado; sin reintento inseguro | G2 |
| 3 | Tenant equivocado | Enviar tenant de otro cliente en la petición | Rechazo; el servidor usa su propio tenant | G1 |
| 4 | Delegación expirada | Esperar más del TTL y reintentar | Rechazo; se exige delegación nueva | G1 |
| 5 | Caída a mitad de job | Matar el worker con un job en curso | Lease recuperable; job no queda `completed` falso | G3 |
| 6 | Disco lleno en evidencia | Limitar el volumen de evidencia | Error explícito; no se pierde auditoría previa | G3 |

Ninguno de estos fallos se ha provocado todavía. La tabla es el guion de la prueba, no su resultado.

## 9. Evidencia que se archivaría

| Artefacto | Contenido | Formato |
|---|---|---|
| `IP-01/verificacion.txt` | Comandos, exit codes, digest calculado | Texto con fecha y SHA |
| `IP-01/mismatch.txt` | Fallo inyectado 1 | Texto |
| `IP-02/instalacion.log` | Instalación y carga sin red | Log |
| `IP-02/aislamiento.txt` | Cinco comprobaciones y resultados | Tabla |
| `IP-03/contrato-vivo.txt` | Lectura gobernada de extremo a extremo | Log |
| `IP-03/rollback.txt` | Tiempo de reversión y estado posterior | Texto |

Los artefactos se nombran ahora y se rellenan al ejecutar. **No existen todavía.**

## 10. Rollback

1. Apagar la flag del tenant y de la capacidad.
2. Revocar delegaciones emitidas durante la ventana.
3. Retirar el paquete del host y restaurar la versión anterior del despliegue.
4. Conservar auditoría y evidencia; no borrar para "dejar limpio".
5. Verificar que el host sigue funcionando sin el middleware, con su comportamiento previo.

Criterio de reversión: **menos de 15 minutos** desde la decisión hasta el host estable, medido en
ensayo. Hoy es un objetivo, no una medición.

## 11. Límites de esta simulación

- No se ha ejecutado ningún comando contra `agente`.
- No hay credenciales, hosts ni tenants reales.
- Los tiempos y conteos son objetivos de diseño.
- El contrato del host depende de PS-P1…PS-P6, que siguen **propuestos y no aplicados**.
- La instalación en staging no demuestra compatibilidad de producción ni aceptación de clientes.
