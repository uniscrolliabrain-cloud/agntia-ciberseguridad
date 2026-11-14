#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python --version
node --version
python -m agntia_ciberseguridad.releasecheck
python scripts/validate_foundation.py
python scripts/validate_campaign.py
# Read-only checks; no daemon start, reset, policy change or global package install.
if command -v docker >/dev/null; then
  if docker info >/dev/null 2>&1; then echo 'Docker reachable; scanners/container release require their separate gates.';
  else echo 'Docker NOT VERIFIED: daemon/socket unavailable.'; fi
else echo 'Docker NOT VERIFIED: executable unavailable.'; fi
