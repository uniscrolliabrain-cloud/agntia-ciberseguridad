"""Build or validate an install manifest; the digest is the artifact's, not the manifest's."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

from pydantic import ValidationError

from agntia_ciberseguridad.install import InstallManifest, MAX_ARTIFACT_BYTES, sha256_file

ROOT = Path(__file__).resolve().parents[1]


def _fail(reason, code=1):
    print(json.dumps({'install_manifest': 'FAIL', 'failures': [reason]}))
    return code


def build(args):
    artifact = args.artifact.resolve()
    if not artifact.is_file() or artifact.is_symlink():
        return _fail('artifact_missing')
    size = artifact.stat().st_size
    if not 0 < size <= MAX_ARTIFACT_BYTES:
        return _fail('artifact_size_invalid')
    try:
        provenance = json.loads(args.provenance.read_text())
    except (OSError, ValueError):
        return _fail('provenance_unreadable')
    source_sha = args.source_sha or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    try:
        manifest = InstallManifest(schema_version=1, package=args.package or provenance['name'],
            version=args.version or provenance['version'], digest=sha256_file(artifact), host_ref=args.host_ref,
            tenant=args.tenant, capabilities=args.capability,
            created_at=args.created_at or datetime.now(timezone.utc), source_sha=source_sha)
    except (KeyError, ValueError):
        return _fail('manifest_invalid')
    payload = manifest.model_dump(mode='json')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps({'install_manifest': 'PASS', 'artifact_bytes': size, 'digest': payload['digest'],
                      'capabilities': payload['capabilities'], 'output': str(args.out)}))
    return 0


def check(args):
    try:
        document = json.loads(args.manifest.read_text())
    except (OSError, ValueError):
        return _fail('manifest_unreadable')
    try:
        manifest = InstallManifest.model_validate(document)
    except ValidationError as error:  # report locations and types only, never input values
        errors = [{'loc': '.'.join(str(part) for part in item.get('loc', ())), 'type': item.get('type', 'invalid')}
                  for item in error.errors()]
        print(json.dumps({'install_manifest': 'FAIL', 'failures': ['manifest_invalid'], 'errors': errors}))
        return 1
    payload = manifest.model_dump(mode='json')
    print(json.dumps({'install_manifest': 'PASS', 'digest': payload['digest'], 'host_ref': payload['host_ref'],
                      'tenant': payload['tenant'], 'capabilities': payload['capabilities']}))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description='Build or validate the install manifest for a packaged artifact.')
    sub = parser.add_subparsers(dest='command', required=True)
    make = sub.add_parser('build')
    make.add_argument('--artifact', type=Path, required=True)
    make.add_argument('--host-ref', required=True)
    make.add_argument('--tenant', required=True)
    make.add_argument('--capability', action='append', required=True)
    make.add_argument('--provenance', type=Path, default=ROOT / 'typescript/PROVENANCE.json')
    make.add_argument('--package')
    make.add_argument('--version')
    make.add_argument('--source-sha')
    make.add_argument('--created-at')
    make.add_argument('--out', type=Path, required=True)
    verify = sub.add_parser('check')
    verify.add_argument('--manifest', type=Path, required=True)
    args = parser.parse_args(argv)
    return build(args) if args.command == 'build' else check(args)


if __name__ == '__main__':
    raise SystemExit(main())
