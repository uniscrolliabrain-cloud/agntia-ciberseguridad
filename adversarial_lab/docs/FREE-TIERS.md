# Ejecución gratis del laboratorio (MVP)

Objetivo: correr el mismo código en sitios gratuitos, sin VM dedicada y sin datos de clientes.
**Ninguna de estas vías es una frontera de seguridad**: son entornos de desarrollo. El MVP trabaja
solo con gemelos sintéticos hasta que exista un cliente con autorización escrita.

## Vías disponibles

| Vía | Qué corre | Docker | Límite real | Evidencia |
|---|---|---|---|---|
| Este workspace Freebuff | tests, gates, CLI, backup/restore | No | efímero; se reinstala al restaurar | `adversarial_lab/var/` (gitignored) |
| GitHub Codespaces | todo + pruebas OCI negativas | **Sí** (devcontainer) | cuota gratuita mensual; se para por inactividad | exportar informes; `var/` desaparece |
| GitHub Actions | tests, gates y job OCI con Docker | **Sí** | minutos gratuitos en repo público | logs y artefactos del run |
| Google Colab | ciclo sintético completo | No | CPU gratis, sesión efímera | zip descargable |
| Hugging Face Space | ciclo sintético vía UI | Docker del Space | CPU básica, `/tmp` efímero | informe en pantalla |

## Cómo se lanza cada una

**Codespaces**

```bash
# Abrir el repo en Codespaces: el devcontainer instala y ejecuta los gates.
PYTHONPATH=adversarial_lab/src python -m agntia_adversarial.cli run --tenant tenant-codespaces
python adversarial_lab/scripts/oci_smoke.py "$(docker inspect --format '{{.Id}}' <imagen-local>)"
```

**GitHub Actions**

Workflow `adversarial-lab.yml`: matriz 3.11/3.12, ciclo sintético, gates y job `oci` que construye
una imagen local, la ejecuta con red cerrada y comprueba que no hay red, no hay rutas del host y el
root es de solo lectura.

**Colab**

`adversarial_lab/notebooks/advlab_colab.ipynb`: clona el repo, instala el paquete, ejecuta el ciclo y
descarga un zip con informes y evidencia.

**Hugging Face**

`adversarial_lab/integrations/huggingface/`: Space Docker con `app.py` (Gradio). El build clona el
repo público; no hay secretos. Un botón ejecuta un ciclo con límite de una ejecución cada 30 s.

## Reglas que no cambian por ser gratis

- Solo activos sintéticos; nunca datos, dominios ni credenciales de un cliente.
- Sin proveedor real, el resultado es `PARTIAL` y así se reporta.
- Herramientas ausentes: `BLOCKED`, nunca PASS simulado.
- Secretos fuera del repo: Doppler, secrets de Codespaces/Actions o variables del Space.
- La evidencia se cifra en local; si el entorno es efímero, se exporta o se pierde, y eso se declara.
- Codespaces, Colab y un Space gratuito no aíslan código hostil: para eso hace falta OCI endurecido
  en host propio o microVM, que es un gate posterior.

## Definición del MVP

1. Cinco misiones sintéticas con oráculo y retest.
2. Evidencia cifrada con hash y ledger de transiciones.
3. Informe determinista con limitaciones explícitas.
4. Gates: integridad, boundary y producción fail-closed.
5. Ejecutable en las cinco vías de arriba sin comprar nada.

Cuando haya cliente: autorización firmada, host con OCI real, `pip-audit` en CI y revisión
independiente. Nada de eso se sustituye con un Space público.
