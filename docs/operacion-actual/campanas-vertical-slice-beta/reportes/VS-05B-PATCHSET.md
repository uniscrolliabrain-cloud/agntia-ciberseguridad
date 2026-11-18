# VS-05B — Patchset

Respecto a `7fdb14e`: **un archivo nuevo de pruebas y ningún cambio de producto**.

## `tests/integration/test_worker_multiprocess.py` (~100 líneas)

| Elemento | Para qué |
|---|---|
| Constante `CHILD` | Programa hijo completo: reconstruye `Settings` desde JSON, `create_app`, `JobStore`, `serve(Worker(…))` |
| `Scanner` del hijo | Doble con `runner.images[Tool.gitleaks].policy_hash` correcto; escribe `execution_key` en el log compartido y devuelve un resultado `no_findings` válido |
| `MultiProcessTests` | Crea 3 jobs con `Setup.submit`, vuelca settings a JSON, lanza dos `Popen` con `sys.executable -c` y verifica los invariantes |

Decisiones:

| Alternativa | Por qué se descartó |
|---|---|
| Hilos en el mismo proceso | Compartirían el objeto `Database` y el `threading.local` de transacciones: no reproduce dos procesos |
| `tests.support.Fixture` dentro del hijo | Crearía una base nueva y vacía; el sentido es compartir la misma |
| Escáner real (gitleaks/semgrep) | El sujeto es el fencing de `claim`/`complete`, no un motor; un binario ausente habría convertido la prueba en un skip |
| Bajar `tenant_limit` sobreescribiendo `claim` | Requeriría cambiar `Worker` o falsear la política; la política real es parte de lo que se está probando |
| Mesa de DLQ nueva | Sin consumidor sería una tabla decorativa; se declara como pendiente |

## Riesgos considerados

- **Bloqueo de SQLite entre procesos:** `Database` abre con `timeout=1.0`, `BEGIN IMMEDIATE` y WAL. En
  seis ejecuciones completas no apareció `database is locked`; si apareciera, el hijo fallaría y el
  test lo mostraría como `worker_failure`, no como PASS silencioso.
- **Orden de arranque:** los hijos se lanzan en el mismo bucle, pero el test no exige simultaneidad
  exacta; la propiedad verificada no depende de ella.
- **Puerto o red:** no se abre ninguno; los hijos hablan con SQLite y nada más.
