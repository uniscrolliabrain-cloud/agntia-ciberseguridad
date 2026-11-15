#!/usr/bin/env bash
# Codespaces / devcontainer bootstrap. Offline: no client data, no provider key required.
set -euo pipefail

cd "$(dirname "$0")/../.."

python -m pip install --upgrade pip
python -m pip install -e adversarial_lab

python -m unittest discover -s adversarial_lab/tests -t adversarial_lab/tests
PYTHONPATH=adversarial_lab/src python -m agntia_adversarial.cli doctor >/dev/null
python adversarial_lab/scripts/releasecheck.py >/dev/null
python adversarial_lab/scripts/verify_boundary.py >/dev/null

echo "advlab listo: tests y gates en verde. Docker disponible: $(command -v docker || echo 'no')"
echo "Siguiente: PYTHONPATH=adversarial_lab/src python -m agntia_adversarial.cli run --tenant tenant-synthetic"
