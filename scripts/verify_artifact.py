"""Verify a packaged artifact against its install manifest and PROVENANCE.json (F1)."""
import argparse
import json
from pathlib import Path

from agntia_ciberseguridad.install import verify

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description='Verify an artifact without extracting it or running its scripts.')
    parser.add_argument('--artifact', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--provenance', type=Path, default=ROOT / 'typescript/PROVENANCE.json')
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text())
    except (OSError, ValueError):
        print(json.dumps({'artifact_verification': 'FAIL', 'failures': ['manifest_unreadable']}))
        return 1
    result = verify(args.artifact, manifest, args.provenance)
    print(json.dumps({'artifact_verification': 'PASS' if result.ok else 'FAIL', **result.to_dict()}, indent=2))
    return 0 if result.ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
