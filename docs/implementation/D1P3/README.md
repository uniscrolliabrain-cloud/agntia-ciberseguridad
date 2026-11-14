# D1P3 — Identidad, tenancy y capacidades

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 1. Prioridad M0; rol Identidad/policy.

## Objetivo
Impedir que una herramienta o un LLM fabrique autoridad y demostrar aislamiento desde la primera ruta.

## Artefactos previstos
- `agntia_ciberseguridad/auth.py`
- `agntia_ciberseguridad/tenancy.py`
- `agntia_ciberseguridad/capabilities.py`
- `tests/security/test_tenancy.py`

## Contrato
Principal deriva de credencial validada; el tenant del path y payload se compara con el scope del servidor.

## Dependencias
D1P2

## Tareas originales
- D1P3T1: Especificar emisor, audiencia, expiración, revocación y autenticación local de laboratorio sin dueño implícito remoto. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P3T2: Definir roles viewer, analyst, reviewer y operator con capacidades separadas de proponer, aprobar y ejecutar. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P3T3: Resolver tenant/empresa desde claims verificados y rechazar identidades contradictorias enviadas en texto o JSON. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P3T4: Aplicar scope a cada consulta, export, evento, fichero y operación asíncrona antes de acceder a recursos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P3T5: Diseñar claves de servicio por tenant y referencias secret-manager; redactar logs y representaciones de error. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P3T6: Probar acceso cruzado con IDs conocidos, token intercambiado, rol insuficiente y credencial caducada/revocada. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P3T7: Revisar que los nombres Pedro/Laia o un header capability nunca concedan autoridad sin política. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D1P3-TEST-1: PrincipalA consulta IDB y recibe404 sin metadatos, tamaño o export deB.
- D1P3-TEST-2: Un token revocado entre petición y job no permite usar permisos antiguos.

Rollback: Revocar credenciales piloto y bloquear rutas; no añadir fallback owner.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
