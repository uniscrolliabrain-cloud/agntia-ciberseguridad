"""Install manifest and offline artifact verification (F0/F1).

The verifier never extracts the package to disk and never runs package scripts:
tar members are hashed in memory under fixed size limits. Results carry digests
and stable failure codes, never package contents or environment values.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
from typing import Annotated, Any, Literal

from pydantic import AwareDatetime, Field, ValidationError, field_validator

from .contracts import Hash, Model, OpaqueId

Capability = Literal['assets.read', 'findings.read', 'jobs.read', 'notes.propose']
CAPABILITY_NAMES: tuple[str, ...] = ('assets.read', 'findings.read', 'jobs.read', 'notes.propose')

MAX_ARTIFACT_BYTES = 64 * 1024 * 1024
MAX_UNPACKED_BYTES = 256 * 1024 * 1024
MAX_ENTRIES = 2000
METADATA_FILES = frozenset({'package.json', 'README.md', 'PROVENANCE.json', 'LICENSE', 'LICENSE.txt', 'NOTICE'})
TAR_PREFIX = 'package/'

_CHUNK = 1024 * 1024
_SECRET_VALUE = re.compile(r'(?i)(?:token|secret|password|passwd|api[_-]?key|private[_-]?key|authorization|credential)\s*[=:]')
_PEM = '-----BEGIN'

GitSha = Annotated[str, Field(pattern=r'^[a-f0-9]{40}$')]
Version = Annotated[str, Field(pattern=r'^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$')]
PackageName = Annotated[str, Field(pattern=r'^(?:@[a-z0-9][a-z0-9._-]*/)?[a-z0-9][a-z0-9._-]*$')]


class InstallManifest(Model):
    """What is installed, where and with which capability; never with secrets."""

    schema_version: Literal[1]
    package: PackageName
    version: Version
    digest: Hash
    host_ref: Annotated[str, Field(min_length=1, max_length=128, pattern=r'^[A-Za-z0-9][A-Za-z0-9._@:/+-]*$')]
    tenant: OpaqueId
    capabilities: Annotated[list[Capability], Field(min_length=1, max_length=4)]
    created_at: AwareDatetime
    source_sha: GitSha

    @field_validator('host_ref', 'tenant')
    @classmethod
    def reference_is_relative_and_secret_free(cls, value: str) -> str:
        if value.startswith('/') or '\\' in value or '..' in value.split('/'):
            raise ValueError('references must be relative and traversal-free')
        if _PEM in value or _SECRET_VALUE.search(value):
            raise ValueError('references must not embed credentials')
        return value

    @field_validator('capabilities')
    @classmethod
    def capabilities_are_unique(cls, value: list[str]) -> list[str]:
        if len(set(value)) != len(value):
            raise ValueError('capabilities must be unique')
        return value


@dataclass(frozen=True)
class Verification:
    ok: bool
    checks: dict[str, bool]
    digest: str | None
    failures: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {'ok': self.ok, 'checks': self.checks, 'digest': self.digest, 'failures': list(self.failures)}


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(_CHUNK), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def provenance_digest(name: str, version: str, files: dict[str, str]) -> str:
    """Reproduce typescript/scripts/provenance.mjs: JSON.stringify in recorded order."""
    payload = json.dumps({'name': name, 'version': version, 'files': files}, separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def _scan_tar(artifact: Path) -> tuple[dict[str, str], dict[str, Any] | None, list[str]]:
    """Hash package members without extracting them; return failures, not contents."""
    digests: dict[str, str] = {}
    package_json: dict[str, Any] | None = None
    failures: list[str] = []
    try:
        archive = tarfile.open(artifact, 'r:gz')
    except (tarfile.TarError, OSError):
        return digests, package_json, ['artifact_unreadable']
    with archive:
        try:
            members = archive.getmembers()
        except (tarfile.TarError, OSError):
            return digests, package_json, ['artifact_unreadable']
        if len(members) > MAX_ENTRIES:
            failures.append('too_many_entries')
        total = 0
        for member in members:
            name = member.name
            if member.isdir():
                continue
            if not member.isfile():
                failures.append('unsupported_entry:' + name)
                continue
            if not name.startswith(TAR_PREFIX):
                failures.append('entry_outside_package:' + name)
                continue
            relative = name[len(TAR_PREFIX):]
            path = PurePosixPath(relative)
            if not relative or '\\' in relative or path.is_absolute() or '..' in path.parts:
                failures.append('unsafe_entry:' + name)
                continue
            if relative in digests:
                failures.append('duplicate_entry:' + relative)
                continue
            handle = archive.extractfile(member)
            if handle is None:
                failures.append('unreadable_entry:' + relative)
                continue
            hasher = hashlib.sha256()
            captured: list[bytes] | None = [] if relative == 'package.json' and member.size <= 65536 else None
            size = 0
            for chunk in iter(lambda: handle.read(_CHUNK), b''):
                size += len(chunk)
                total += len(chunk)
                if total > MAX_UNPACKED_BYTES:
                    return digests, package_json, failures + ['too_large_unpacked']
                hasher.update(chunk)
                if captured is not None:
                    captured.append(chunk)
            digests[relative] = hasher.hexdigest()
            if captured is not None:
                try:
                    document = json.loads(b''.join(captured))
                except ValueError:
                    failures.append('package_json_invalid')
                else:
                    if isinstance(document, dict):
                        package_json = document
                    else:
                        failures.append('package_json_invalid')
    return digests, package_json, failures


def _load_provenance(source: Path | dict[str, Any] | None) -> tuple[dict[str, Any] | None, list[str]]:
    if source is None:
        return None, ['provenance_missing']
    if isinstance(source, dict):
        document: Any = source
    else:
        path = Path(source)
        if not path.is_file() or path.is_symlink():
            return None, ['provenance_missing']
        try:
            document = json.loads(path.read_text())
        except (OSError, ValueError):
            return None, ['provenance_unreadable']
    if not isinstance(document, dict):
        return None, ['provenance_invalid']
    files = document.get('files')
    name, version = document.get('name'), document.get('version')
    if not isinstance(name, str) or not isinstance(version, str) or not isinstance(files, dict) or not files:
        return None, ['provenance_invalid']
    for entry, digest in files.items():
        if not isinstance(entry, str) or not isinstance(digest, str) or not re.fullmatch(r'[a-f0-9]{64}', digest):
            return None, ['provenance_invalid']
    if document.get('content_digest') != provenance_digest(name, version, files):
        return None, ['provenance_digest_mismatch']
    return document, []


def verify(artifact: Path | str, manifest: InstallManifest | dict[str, Any], provenance: Path | dict[str, Any] | None = None) -> Verification:
    """Check size, digest, tar entries and provenance coherence; never repair."""
    checks: dict[str, bool] = {}
    failures: list[str] = []
    if isinstance(manifest, InstallManifest):
        model = manifest
    else:
        try:
            model = InstallManifest.model_validate(manifest)
        except ValidationError:
            return Verification(False, {'manifest': False}, None, ('manifest_invalid',))
    checks['manifest'] = True
    path = Path(artifact)
    if not path.is_file() or path.is_symlink():
        return Verification(False, {**checks, 'artifact_present': False}, None, ('artifact_missing',))
    checks['artifact_present'] = True
    size = path.stat().st_size
    checks['artifact_size'] = 0 < size <= MAX_ARTIFACT_BYTES
    if not checks['artifact_size']:
        failures.append('artifact_size_invalid')
    digest = sha256_file(path)
    checks['digest'] = digest == model.digest
    if not checks['digest']:
        failures.append('digest_mismatch')
    files, package_json, tar_failures = _scan_tar(path)
    checks['entries'] = not tar_failures
    failures.extend(tar_failures)
    document, provenance_failures = _load_provenance(provenance)
    checks['provenance'] = not provenance_failures
    failures.extend(provenance_failures)
    if document is not None and not provenance_failures:
        expected = document['files']
        missing = [name for name in expected if name not in files]
        mismatched = [name for name, value in expected.items() if name in files and files[name] != value]
        extra = sorted(set(files) - set(expected) - METADATA_FILES)
        failures.extend('provenance_file_missing:' + name for name in missing)
        failures.extend('provenance_file_mismatch:' + name for name in mismatched)
        failures.extend('unexpected_entry:' + name for name in extra)
        checks['coverage'] = not (missing or mismatched or extra)
        checks['identity'] = package_json is not None and package_json.get('name') == document['name'] == model.package and package_json.get('version') == document['version'] == model.version
        if not checks['identity']:
            failures.append('identity_mismatch')
    return Verification(not failures and all(checks.values()), checks, digest, tuple(failures))
