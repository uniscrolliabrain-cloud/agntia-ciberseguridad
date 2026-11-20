# Configuración de rollout (F2)

**Estado:** implementado el 2026-11-20. **Ámbito:** validación de arranque; no aplica capacidades,
no escribe estado y no sustituye a la autorización del host.

## 1. Dónde vive

`RolloutConfig` y el campo `rollouts` de `Settings` están en
[`agntia_ciberseguridad/config.py`](../../agntia_ciberseguridad/config.py). La configuración se
carga con `Settings.from_env()`, que exige `AGNTIA_CYBER_CONFIG_FILE` y falla con el mensaje
genérico `Invalid server configuration` si el documento no valida.

## 2. Ejemplo ilustrativo

Los valores son ficticios; las fechas deben ser futuras en el momento del arranque.

```json
{
  "rollouts": [
    {
      "tenant_id": "lab-cyber",
      "capability": "findings.read",
      "ring": "A",
      "previous_ring": null,
      "state": "pending",
      "revision": 1,
      "consent_ref": "consentA",
      "budget_cents": 100,
      "expires_at": "2026-12-01T00:00:00+00:00",
      "secret_ref": "CYBER_AGENT_CREDENTIAL"
    }
  ]
}
```

## 3. Invariantes

| Regla | Efecto al arrancar |
|---|---|
| `consent_ref` obligatorio y debe existir en `consents` con el mismo tenant | Falla cerrado |
| `budget_cents` entero positivo (1…1 000 000) | Falla cerrado |
| `expires_at` futuro y con zona horaria | Falla cerrado |
| `capability` limitada a `assets.read`, `findings.read`, `jobs.read`, `notes.propose` | Falla cerrado |
| `ring` en `A`–`D`; `previous_ring` solo permite el mismo anillo o el siguiente | Falla cerrado |
| Anillo `D` exige `previous_ring` registrado (`C` o `D`) | Falla cerrado |
| `state` nace `pending`; `enabled` nunca es un valor por defecto | La capacidad queda apagada |
| `secret_ref` es un nombre de variable de entorno, no un valor | Falla cerrado si parece un secreto |
| Duplicado `(tenant_id, capability)` | Falla cerrado |

`secret_ref` no se resuelve en esta fase: solo se valida su forma. El host sigue siendo
responsable de leer el valor desde su secret manager en cada llamada.

## 4. Lo que esta fase no hace

- No habilita ninguna capacidad, ni siquiera con `state: "enabled"`: la aplicación efectiva
  corresponde a F5 y hoy no existe.
- No crea tenants, consentimientos ni presupuestos; solo comprueba que ya estén provisionados.
- No aplica migraciones ni escribe en la base de datos.
- No toca `agente`.

## 5. Rollback

Quitar las entradas de `rollouts` y reiniciar. Las entradas nacen `pending`, así que retirarlas
no deja estado mixto: no hay tabla, no hay efecto y no hay migración que revertir.

## 6. Evidencia

`tests/unit/test_config_rollout.py` cubre: configuración válida, consentimiento ausente o ajeno,
presupuesto cero o negativo, caducidad vencida, anillo desconocido o salto `A → D`, estado
desconocido, referencia de secreto con valor embebido, tenant no provisionado y binding duplicado.
Se ejecutan con `python -m unittest discover -s tests`.
