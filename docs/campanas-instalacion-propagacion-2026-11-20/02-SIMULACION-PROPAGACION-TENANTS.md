# 02 · Simulación de propagación a tenants

**Campañas cubiertas:** IP-04, IP-05, IP-06, IP-07, IP-08. **Estado:** SIMULADO, NO EJECUTADO.
**Punto de partida:** host instalado en anillo B según [01](01-SIMULACION-INSTALACION-HOST.md).

Propagar no es copiar una flag: es inscribir un tenant, habilitar una capacidad concreta,
observar una ventana y poder volver atrás. Esta página simula ese recorrido con tenants ficticios
y datos sintéticos.

## 1. Modelo de inscripción

Cada tenant propagado tiene un registro con, como mínimo:

| Campo | Ejemplo simulado | Regla |
|---|---|---|
| `tenant_id` | `pilot-01` | Asignado por el servidor; nunca por el cliente |
| `ring` | `C` | A, B, C o D; no se salta |
| `capability` | `findings.read` | Una por ola |
| `state` | `enabled` | `pending`, `enabled`, `paused`, `revoked` |
| `revision` | `3` | Toda mutación exige revisión esperada |
| `consent_ref` | `consent-pilot-01` | Referencia verificable, no texto libre |
| `budget_cents` | `0` | Presupuesto acotado; sin reserva no hay ejecución |
| `expires_at` | `2027-02-01` | La habilitación caduca |
| `reason` | `piloto aprobado` | Auditoría legible |

Sin `consent_ref`, sin presupuesto o con revisión desactualizada, la ola no avanza.

## 2. Olas simuladas

| Ola | Tenants | Capacidad | Cobertura | Ventana | Criterio de salida |
|---|---|---|---|---|---|
| W0 | `lab-alpha`, `lab-beta` | `assets.read` | 100 % anillo A | 1 día | Aislamiento entre ambos |
| W1 | `pilot-01` | `findings.read` | 1 tenant | 3 días | Cero cruces; delegación de un uso |
| W2 | `pilot-01`…`pilot-03` | `findings.read` | 5 % del anillo C | 2 días | Sin 5xx; cuotas respetadas |
| W3 | 25 % del anillo C | `findings.read` | 25 % | 3 días | Deriva de política = 0 |
| W4 | 100 % anillo C | `findings.read` | 100 % | 3 días | Sombra estable |
| W5 | 25 % anillo D | `findings.read` | 25 % | 3 días | Soporte y on-call informados |
| W6 | 100 % anillo D | `findings.read` | 100 % | 5 días | Sin incidentes de aislamiento |

La capacidad `jobs.read` se propagaría después, con su propia W1–W6. **No se propaga un paquete
"completo"**: cada capacidad repite el ciclo porque su riesgo es distinto.

## 3. Recorrido simulado de un tenant

### Día 1 · Alta

1. Operación crea `pilot-01` y registra el consentimiento.
2. El servidor fija tenant y activos; el tenant no puede ampliarlos desde la petición.
3. Se emite una delegación de un uso para `findings.read`, ligada al principal y al recurso.
4. La flag nace apagada hasta que la revisión esperada coincide.

**Esperado:** auditoría con actor, motivo, revisión y `consent_ref`; ninguna lectura posible aún.

### Día 2 · Primera lectura

1. El host resuelve la sesión y pide una lectura nominada.
2. El middleware valida principal, manifiesto, política, recurso, TTL y consumo del token.
3. Devuelve solo findings del tenant, con `tenant_id` en la proyección.
4. El token queda consumido; el segundo intento falla.

**Esperado:** una lectura correcta y un rechazo por reutilización. Ambos en auditoría.

### Día 3 · Ventana de observación

Se revisan métricas y auditoría: lecturas por tenant, rechazos, latencia, errores y presupuesto.
No se amplía la ola si hay un rechazo inexplicado o una lectura fuera de tenant.

### Día 4 · Decisión

- **Avanzar:** la ola siguiente se planifica con revisión nueva.
- **Pausar:** la flag del tenant pasa a `paused`; se conserva la inscripción.
- **Revocar:** se revoca la delegación, se apaga la flag y se registra el motivo.

## 4. Propagación a agentes (IP-07)

Secuencia simulada, sin ejecutar:

1. Humano con `agents.manage` crea el manifiesto del agente y lo aprueba.
2. Humano con `agents.delegate` emite una delegación de un uso para el recurso concreto.
3. El host entrega el token al cliente del agente; nunca al navegador ni al modelo.
4. El agente llama a la tool de lectura; el backend comprueba y consume el token.
5. Un segundo uso, un TTL vencido o un recurso distinto se rechazan.
6. La revocación del manifiesto invalida las delegaciones pendientes.

**Pruebas negativas que la simulación exige:**

| Caso | Resultado esperado |
|---|---|
| Token de owner usado por un agente | Rechazo; el principal no coincide |
| Delegación reutilizada | Rechazo por consumo |
| Delegación para otro activo | Rechazo por recurso |
| Lectura sin manifiesto aprobado | Rechazo; `agent_gateway_required` se mantiene |
| Timeout tras consumo | Estado incierto; se exige delegación nueva, no reintento ciego |

## 5. Sombra de políticas (IP-08)

| Paso | Simulación | Evidencia |
|---|---|---|
| Captura | Se registran pares (acción, contexto, decisión calculada) | `sombra.json` |
| Comparación | Se contrasta con la acción realmente permitida | `divergencias.md` |
| Umbral | Divergencias por encima del umbral pactado detienen la ola | Decisión del owner |
| Cierre | Se explica cada divergencia; las no explicadas bloquean N3 | Informe |

La sombra **no bloquea nada**. Un lector no debe inferir enforcement de esta sección: N3 queda
fuera del programa y requiere revisión independiente y aceptación escrita.

## 6. Incidentes simulados

| # | Incidente | Detección | Respuesta simulada | Efecto en la ola |
|---|---|---|---|---|
| 1 | Intento de lectura cruzada | Rechazo y alerta por tenant distinto | Se detiene la ola; se revisa identidad y resolver | Aborto |
| 2 | Delegación reutilizada | Segundo consumo rechazado | Se revoca el manifiesto; se audita el origen | Pausa |
| 3 | Deriva de política | Versión aplicada ≠ versión aprobada | Se apaga la capacidad del tenant afectado | Aborto |
| 4 | Presupuesto agotado | Reserva rechazada | Se detiene la ejecución; no se amplía el límite | Pausa |
| 5 | Lease obsoleto en job | `stale_lease` re-lanzado | El job se recupera; no se marca `completed` | Continúa con nota |
| 6 | Caída del host | Health check y alerta | Se reintenta la ola cuando el host está estable | Pausa |

Cada incidente exige un registro con hora, tenant, decisión, actor y enlace a la evidencia. Un
incidente sin registro no cuenta como resuelto.

## 7. Telemetría esperada

| Señal | Tipo | Uso |
|---|---|---|
| `cyber_rollout_tenants_total{ring,capability,state}` | Métrica | Cobertura real por ola |
| `cyber_read_denied_total{reason}` | Métrica | Rechazos por identidad, TTL, consumo o recurso |
| `cyber_rollout_drift_total` | Métrica | Versión de política distinta de la aprobada |
| `AgntiaRolloutDrift` | Alerta | Detiene la ola |
| `AgntiaCrossTenantAttempt` | Alerta | Revisión inmediata de aislamiento |
| `AgntiaKillSwitchActive` | Alerta | Confirma que la parada se aplicó |

Las alertas se prueban en simulacro: se dispara la condición y se comprueba que llega la
notificación y que la ola se detiene. Una alerta definida pero nunca disparada es `NOT_VERIFIED`.

## 8. Rollback y kill switch

| Nivel | Acción | Alcance | Tiempo objetivo |
|---|---|---|---|
| Tenant | `paused` y revocación de delegaciones | Un tenant | < 5 min |
| Ola | Volver a la ola anterior | Conjunto de la ola | < 15 min |
| Capacidad | Apagar la flag de la capacidad | Todos los tenants | < 15 min |
| Programa | Kill switch global y retirada del paquete | Anillo completo | < 30 min |

El kill switch no borra datos ni auditoría. Deja el host en su comportamiento previo y exige una
decisión explícita para reanudar.

## 9. Límites

- Los tenants, porcentajes y fechas son ficticios.
- No hay tráfico real ni datos de clientes.
- Las olas no se han ejecutado; los tiempos son objetivos.
- La propagación a `agente` depende de PS-P1…PS-P6, propuestos y no aplicados.
- N3 (enforcement) y N4 (respuesta automática) quedan fuera; nada de esta página los autoriza.
