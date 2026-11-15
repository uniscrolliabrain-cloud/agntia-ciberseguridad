"""Hugging Face Space (Docker, free CPU): one synthetic adversarial cycle.

No provider keys, no client data, no network calls from the lab itself.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import gradio as gr

REPO = Path("/app/repo")
TENANT = re.compile(r"^[a-z0-9][a-z0-9-]{2,31}$")
LAST_RUN = {"at": 0.0}
COOLDOWN_SECONDS = 30

INTRO = """# Adversarial Lab (MVP sintético)

Ciclo completo sobre gemelos sintéticos: IDOR y escalada de rol en una API en proceso, canario en un
repo, inyección de prompt en un agente y fallo/restore con RTO medido.

- Sin datos de clientes. Sin claves. Sin red desde el laboratorio.
- Resultado esperado: **PARTIAL**, porque las herramientas externas están `BLOCKED`.
- Esto no es un sandbox de seguridad: no ejecutes código hostil aquí.
"""


def run_cycle(tenant: str) -> tuple[str, str, str]:
    tenant = (tenant or "").strip()
    if not TENANT.match(tenant):
        return "tenant inválido: usa minúsculas, números y guiones", "", ""
    now = time.monotonic()
    if now - LAST_RUN["at"] < COOLDOWN_SECONDS:
        wait = int(COOLDOWN_SECONDS - (now - LAST_RUN["at"]))
        return f"espera {wait}s entre ejecuciones", "", ""
    LAST_RUN["at"] = now

    data_dir = tempfile.mkdtemp(prefix="advlab-")
    env = dict(os.environ, PYTHONPATH=str(REPO / "adversarial_lab" / "src"), ADVLAB_DATA_DIR=data_dir)
    try:
        completed = subprocess.run(
            [sys.executable, "-m", "agntia_adversarial.cli", "run", "--tenant", tenant],
            cwd=REPO,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "timeout del ciclo sintético", "", ""
    if completed.returncode != 0:
        return "fallo de ejecución", completed.stderr[-4000:], ""
    payload = json.loads(completed.stdout)
    report_path = Path(payload.get("report", ""))
    report = report_path.read_text(encoding="utf-8") if report_path.is_file() else "sin informe"
    evidence = "\n".join(line for line in report.splitlines() if "sha256=" in line)
    return json.dumps(payload, indent=2), report, evidence


with gr.Blocks(title="Agntia Adversarial Lab") as demo:
    gr.Markdown(INTRO)
    tenant = gr.Textbox(label="Tenant sintético", value="tenant-hf")
    button = gr.Button("Ejecutar ciclo sintético", variant="primary")
    summary = gr.Code(label="Resumen", language="json")
    report = gr.Textbox(label="Informe", lines=18)
    evidence = gr.Textbox(label="Evidencia (hashes)", lines=6)
    button.click(run_cycle, inputs=tenant, outputs=[summary, report, evidence])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
