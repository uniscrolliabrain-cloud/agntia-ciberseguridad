# VS-03 — Secretos, identidad y autorización

**Base:** `6677899` (rama de bitácora).
**Rama:** `docs/cyber-bitacora-viva` (misma PR #17).
**Estado:** P0/P1 completos; P2 **BLOCKED** por gestor y credenciales; P3 parcialmente cubierto.

## P0 — Inventario real de secretos

No hay valores en el repositorio: `config.py` solo admite **referencias** con patrón
`^[A-Z][A-Z0-9_]{2,100}$` (`EnvRef`). Los valores se leen de `os.getenv(<ref>)` en el punto de uso.

| Referencia | Dónde se declara | Consumidor | Ámbito | TTL / rotación |
|---|---|---|---|---|
| `PrincipalBinding.token_env` | `config.py:20` | `auth.py:42` | Un principal (humano/agente/servicio) y sus tenants | `expires_at` opcional; rotar = cambiar valor y reiniciar |
| `EvidencePolicy.key_refs` | `config.py:63` | `evidence/vault.py:31` | Clave de evidencia por política | Sin TTL; rotación manual |
| `EventSource.key_env` | `config.py:71` | `events/ingest.py:36` | Fuente de eventos por tenant | Sin TTL |
| `metrics_token_env` | `config.py:98` | `telemetry/api.py:27` | Métricas internas | Sin TTL; referencia separada obligatoria |
| `delegation_key_env` | `config.py:106` | `agents/capabilities.py:36` | Delegación de lectura de agentes | Sin TTL; referencia separada |
| `emergency_token_env` | `config.py:107` | `agents/controls.py:24` | Parada de emergencia | Sin TTL; no puede coincidir con ningún principal ni clave |

Validadores ya existentes (`config.py:127–135`) impiden reutilizar la referencia de emergencia,
delegación, métricas o eventos para un principal. Eso evita que una credencial operativa sirva como
credencial humana, pero **no sustituye a un gestor**: no hay revocación remota, versionado ni TTL
central.

## P1 — Identidad y autorización

- `Authenticator.authenticate` compara SHA-256 con `hmac.compare_digest`; exige entre 24 y 512
  caracteres y exactamente **un** principal coincidente.
- `current()` rechaza principal deshabilitado, expirado, ausente o con token vacío con
  `principal_revoked` (403).
- `authorize()` revalida el principal en cada llamada, exige pertenencia al tenant (404 si no) y
  capability dentro del rol.
- Los agentes quedan limitados a `agents.read` salvo rutas de efecto revisadas.
- Los 57 mutadores son `POST` y pasan por `service.authorize`; no hay ruta mutadora sin tenant
  autenticado.

## P3 — Cobertura negativa existente

| Caso | Test |
|---|---|
| Aislamiento entre tenants | `tests/security/test_api_foundation.py:52` |
| Grant expirado / configuración cambiada | `tests/security/test_api_foundation.py:108` |
| Identidad revocada antes del claim | `tests/integration/test_jobs.py:87` |
| Tenant equivocado en gateway de agentes | `tests/security/test_agent_gateway.py:126` |
| Replay y conflicto de contenido | `tests/security/test_observability_controls.py:75` |
| Token de un solo uso, firma y sujeto | `tests/security/test_observability_controls.py:117` |

## Huecos reales

1. **No hay gestor**: sin revocación remota, versionado ni auditoría de acceso a secretos. P2
   bloqueado hasta que exista cuenta y credenciales; no se inventa adaptador.
2. **Sin TTL por token**: solo `expires_at` por principal. Rotación manual.
3. **Prueba de fuga en logs añadida:** `tests/security/test_secret_leakage.py` pasa un canario de
   entorno como `authorization`, payload y excepción; el esquema cerrado lo descarta y el valor no
   aparece en la búsqueda. Cubre logs operativos, no volcados de proceso.
4. **Referencias de clave de evidencia sin versión**: `key_refs` es lista, pero no se registra qué
   versión cifró cada blob; corresponde a VS-04.

## Gate

`PARTIAL`: denegación cruzada y referencias separadas demostradas; cero secreto en repo por diseño y
revisión de código; falta gestor real y prueba de no fuga en logs. No se marca PASS de VS-03.
