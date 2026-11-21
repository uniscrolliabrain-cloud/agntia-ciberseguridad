# CY-VS-02 — Evidencia

**Fecha:** 2026-11-20
**Base SHA:** `eaf7da0d60a5adc7302c977cdabdfd3900c922be`
**HEAD SHA:** `4e73e89...`
**Rama:** `feat/cyber-vertical-slices-installable-20261120`

## Nuevo archivo creado

| Archivo | Tamaño | Contenido |
|---------|--------|-----------|
| `tests/security/test_identity_tenancy.py` | ~190 líneas | 7 pruebas: dos tenants aislados, cross-tenant 404, actor revocado, grant caducado, read-only vs write, approval forjada, sin identidad implícita |

## Pruebas implementadas

| Test ID | Descripción | Resultado esperado |
|---------|-------------|-------------------|
| test_two_tenants_isolated | ownerA registra activo en tenantA, ownerB en tenantB; aislamiento completo | assetsA solo tenantA, assetsB solo tenantB |
| test_cross_tenant_read_is_404_not_enumeration | ownerB lee activo de tenantA | DomainError code='not_found' (404) |
| test_revoked_actor_is_rejected | revokedA (disabled) intenta listar activos | DomainError code='principal_revoked' (403) |
| test_expired_grant_is_rejected | Grant con expires_at en el pasado | ValueError (pydantic validación) |
| test_read_only_vs_write_by_role | owner registra activo (write permitido) | Asset creado con id válido |
| test_approval_forged_hash_is_rejected | ownerB aprueba con proposal_hash incorrecto | DomainError code='conflict' (409) |
| test_no_implicit_owner_from_prompt_or_header | Headers malformados, Bearer corto, token inválido | Todos → DomainError code='auth' (401) |

## Código existente (no modificado)

- `agntia_ciberseguridad/auth.py` — Authenticator, Principal, ROLE_CAPABILITIES, authorize(), require_human()
- `agntia_ciberseguridad/agents/capabilities.py` — Delegaciones one-use, TTL 5 min, HMAC, revocación
- `agntia_ciberseguridad/agents/registry.py` — Manifestos de agentes, separation of duties
- `agntia_ciberseguridad/agents/policy.py` — ActionPolicy, fail-closed, POLICY_HASH
- `agntia_ciberseguridad/agents/context.py` — verified_scope ContextVar

## Decisiones

- No se modificó ningún archivo existente.
- Solo se agregó el test de identidad.
- Los tests no se pudieron ejecutar por falta de pydantic/fastapi en este entorno.
- `docs/release/status.json` se mantiene NO-GO.