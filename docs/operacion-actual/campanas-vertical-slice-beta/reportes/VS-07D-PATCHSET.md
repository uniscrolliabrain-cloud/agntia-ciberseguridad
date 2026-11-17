# VS-07D — Patchset

Respecto a `7fdb14e`: **dos scripts nuevos, una regla nueva, un test nuevo y dos tests ajustados**.
Ningún cambio en el paquete `agntia_ciberseguridad/`, ningún esquema, ninguna migración.

## `scripts/backup_ledger.py` (nuevo, ~115 líneas)

```python
OUTCOMES=('success','failure')
REASON=re.compile(r'^[a-z][a-z0-9_]{0,39}$')
DIGEST=re.compile(r'^[a-f0-9]{64}$')
MAX_LINES=4096

def record(path,outcome,*,reason=None,digest=None,clock=None):
    ...
    if outcome=='success' and digest is None:raise ValueError('A successful backup must carry its bundle digest')
    if outcome=='failure' and digest is not None:raise ValueError('A failed backup has no bundle to digest')
    handle=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
    ...  # una línea JSON, fsync, cierre
```

`summarize(path)` devuelve `records`, `valid_records`, `corrupt`, `last_success`, `last_attempt`,
`consecutive_failures`, `age_seconds`. Lee como máximo las últimas `MAX_LINES` líneas y **no** convierte
una línea inválida en un éxito: la cuenta como corrupta y sigue.

## `scripts/backup_exporter.py` (nuevo, ~70 líneas)

```python
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.backup_ledger import summarize

def write(ledger,destination,clock=None):
    if not destination.parent.is_dir():raise ValueError('Textfile directory does not exist: '+str(destination.parent))
    payload=render(summarize(ledger,clock=clock))
    handle,path=tempfile.mkstemp(dir=destination.parent,prefix='.agntia-backup-',suffix='.tmp')
    with os.fdopen(handle,'w',encoding='utf-8') as stream:
        stream.write(payload);stream.flush();os.fsync(stream.fileno())
    os.chmod(path,0o644);os.replace(path,destination)
```

Cuatro series, sin etiquetas: `agntia_backup_last_success_timestamp_seconds`,
`agntia_backup_last_attempt_timestamp_seconds`, `agntia_backup_consecutive_failures`,
`agntia_backup_ledger_corrupt_total`.

## `infra/observability/alerts.yaml` (séptima regla)

```yaml
- alert: AgntiaBackupStale
  expr: agntia_backup_last_success_timestamp_seconds == 0
        or time() - agntia_backup_last_success_timestamp_seconds > 93600
        or absent(agntia_backup_last_success_timestamp_seconds)
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: No verified lab backup within the declared window; restore readiness is unknown
```

`93600` s = 26 h: ventana de 24 h más dos de gracia. Se documenta como hipótesis, no como RPO.

## `tests/unit/test_backup_ledger.py` (nuevo, 7 tests)

Validaciones de `record`, append-only y modo `0600`, ausencia/corrupción como desconocido, fallos
consecutivos, exportación atómica sin temporales, directorio inexistente como error.

## `tests/integration/test_p3_drills.py`

- Imports nuevos: `base64`, `os`, `patch`, `scripts.backup_ledger`, `scripts.backup_exporter`.
- Helper `samples(text)`: lee el *textfile* como lo haría un scrape (solo líneas de muestra).
- D2 reescrito: antes comprobaba que **no** existía señal de backup; ahora la exige y verifica las dos
  direcciones (fallo → stale con página; éxito verificado → no stale).
- D1 y D3 sin cambios.

## `tests/integration/test_alert_delivery.py`

Número esperado de reglas entregables: 6 → 7.

## Decisiones

| Alternativa | Por qué se descartó |
|---|---|
| Exponer la serie de backup desde `/metrics` de la API | La API no hace backups; sería una señal que miente si el proceso de backup ni se ejecuta |
| Tabla SQLite nueva para el libro | Migración de esquema para un dato operativo que no pertenece al dominio del producto |
| Regla sin `absent()` | Dejaría de avisar precisamente cuando el exportador no está instalado, el caso más probable |
| Escribir el *textfile* directamente | Un corte a mitad dejaría un fichero truncado que un scrape podría leer como éxito |
| Aceptar `success` sin digest | Un éxito sin hash del bundle no distingue un backup real de una línea escrita a mano |
