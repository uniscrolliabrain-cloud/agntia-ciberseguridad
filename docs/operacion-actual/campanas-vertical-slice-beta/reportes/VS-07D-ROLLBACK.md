# VS-07D — Rollback

Cinco pasos, todos reversibles, sin datos ni esquema:

1. Restaurar el D2 anterior en `tests/integration/test_p3_drills.py` (el que comprobaba que **no**
   existía ninguna señal de backup) y quitar los imports de `base64`, `os`, `patch` y de los dos
   módulos nuevos.
2. `git rm tests/unit/test_backup_ledger.py`
3. `git rm scripts/backup_exporter.py scripts/backup_ledger.py`
4. Quitar `AgntiaBackupStale` de `infra/observability/alerts.yaml`.
5. Revertir en `tests/integration/test_alert_delivery.py` el número esperado de reglas de 7 a 6.
6. `python -m unittest discover -s tests` → **216 tests** (223 − 7 unitarios) y el D2 vuelve a `BLOCKED`.

## Efecto

- **El fallo de backup vuelve a ser silencioso.** Es el efecto principal y hay que decirlo: sin libro ni
  exportador, un `backup_key_unavailable` correcto no avisa a nadie.
- Ningún backup real, destino o clave se ve afectado: la campaña no escribe fuera de su directorio
  temporal y la clave del simulacro es efímera.
- Los libros `*.jsonl` que existieran como evidencia **no se borran** con el rollback del código; si se
  quiere descartar la evidencia, es una decisión aparte y explícita.
- Sin migraciones ni datos que deshacer: el único estado persistente es el fichero del libro.

## Orden seguro

Retirar la regla **y** el exportador en el mismo commit. Una regla con `absent()` sin exportador deja un
`warning` permanente que nadie puede cerrar, y un exportador sin regla produce una señal que nadie
consume.
