# D1P5 — Inventario de activos y autorización de trabajo

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 1. Prioridad M0; rol Seguridad del alcance.

## Objetivo
Garantizar que cada auditoría se limita a activos y efectos autorizados, también tras DNS o cambios de objetivo.

## Artefactos previstos
- `agntia_ciberseguridad/assets.py`
- `agntia_ciberseguridad/grants.py`
- `agntia_ciberseguridad/network_policy.py`
- `tests/security/test_scope.py`

## Contrato
Grant liga titular, tenant, snapshot/host, perfil, ventana, exclusiones y presupuesto; no autorización por nombre de dominio libre.

## Dependencias
D1P3, D1P4

## Tareas originales
- D1P5T1: Modelar titular/representación, recursos, entornos, paths, IP/hosts, perfiles, ventana y contactos de emergencia. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P5T2: Crear alta/revisión de assets con ownership verificado y snapshots inmutables; no descubrimiento de terceros abierto. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P5T3: Aplicar DNS/IP allowlist y bloqueo de metadata, loopback no autorizado, IPv6 mapeada y credenciales en URLs. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P5T4: Definir redirects, cambios de resolución y subdominios: denegar expansión de alcance por defecto. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P5T5: Clasificar perfiles static_read, passive_web y active_lab con efectos y límites documentados. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P5T6: Probar grant cruzado, host homónimo, destino cambiado, expiración durante trabajo y salida de red no permitida. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P5T7: Publicar inventario/grants revisables sin exponer credenciales ni infraestructura de otro tenant. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D1P5-TEST-1: Una URL a metadata/link-local y un redirect fuera del grant se bloquean antes de conectar.
- D1P5-TEST-2: Un grant caducado o revocado impide iniciar/reintentar una auditoría.

Rollback: Revocar el grant, parar nuevas admisiones y preservar el estado de trabajos en curso para conciliación.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
