"""Artifact verification: digest, tar members and provenance; never repair or execute."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from agntia_ciberseguridad.install import provenance_digest, verify

ROOT = Path(__file__).resolve().parents[2]

PACKAGE_JSON = json.dumps({'name': '@agntia/ciberseguridad', 'version': '0.1.0-alpha.3'}).encode()
FILES = {
    'package.json': PACKAGE_JSON,
    'README.md': b'synthetic readme\n',
    'dist/client.js': b'export const synthetic = true;\n',
}


def build_pack(files):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w') as archive:
        for name, data in sorted(files.items()):
            info = tarfile.TarInfo('package/' + name)
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o644
            info.uid = info.gid = 0
            info.uname = info.gname = ''
            archive.addfile(info, io.BytesIO(data))
    return gzip.compress(buffer.getvalue(), compresslevel=9, mtime=0)


def build_provenance(files, name='@agntia/ciberseguridad', version='0.1.0-alpha.3'):
    digests = {entry: hashlib.sha256(data).hexdigest() for entry, data in files.items()}
    return {'generator': 'typescript/scripts/provenance.mjs', 'name': name, 'version': version,
            'files': digests, 'content_digest': provenance_digest(name, version, digests)}


def build_manifest(pack, capabilities=('findings.read',)):
    return {'schema_version': 1, 'package': '@agntia/ciberseguridad', 'version': '0.1.0-alpha.3',
            'digest': hashlib.sha256(pack).hexdigest(), 'host_ref': 'agente@lab', 'tenant': 'lab-cyber',
            'capabilities': list(capabilities), 'created_at': '2026-11-20T00:00:00+00:00',
            'source_sha': 'b' * 40}


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.pack = build_pack(FILES)
        self.artifact = self.root / 'package.tgz'
        self.artifact.write_bytes(self.pack)
        self.provenance = build_provenance(FILES)

    def tearDown(self):
        self.directory.cleanup()

    def test_valid_pack_passes_every_check(self):
        result = verify(self.artifact, build_manifest(self.pack), self.provenance)
        self.assertTrue(result.ok, result.failures)
        self.assertEqual(result.failures, ())
        self.assertEqual(result.digest, hashlib.sha256(self.pack).hexdigest())
        self.assertTrue(all(result.checks.values()))

    def test_altered_byte_on_disk_fails_and_is_not_repaired(self):
        altered = bytearray(self.pack)
        altered[-1] ^= 0xFF
        self.artifact.write_bytes(bytes(altered))
        before = hashlib.sha256(self.artifact.read_bytes()).hexdigest()
        result = verify(self.artifact, build_manifest(self.pack), self.provenance)
        self.assertFalse(result.ok)
        self.assertIn('digest_mismatch', result.failures)
        self.assertEqual(hashlib.sha256(self.artifact.read_bytes()).hexdigest(), before)

    def test_extra_entry_is_rejected(self):
        pack = build_pack({**FILES, 'dist/extra.js': b'export const extra = true;\n'})
        self.artifact.write_bytes(pack)
        result = verify(self.artifact, build_manifest(pack), build_provenance(FILES))
        self.assertFalse(result.ok)
        self.assertIn('unexpected_entry:dist/extra.js', result.failures)

    def test_missing_provenance_fails_closed(self):
        result = verify(self.artifact, build_manifest(self.pack), None)
        self.assertFalse(result.ok)
        self.assertIn('provenance_missing', result.failures)

    def test_tampered_provenance_digest_fails(self):
        provenance = build_provenance(FILES)
        provenance['content_digest'] = 'c' * 64
        result = verify(self.artifact, build_manifest(self.pack), provenance)
        self.assertFalse(result.ok)
        self.assertIn('provenance_digest_mismatch', result.failures)

    def test_links_and_traversal_are_rejected(self):
        for name, link in (('package/../evil', None), ('package/dist/link.js', 'client.js')):
            buffer = io.BytesIO()
            with tarfile.open(fileobj=buffer, mode='w') as archive:
                for entry, data in sorted(FILES.items()):
                    info = tarfile.TarInfo('package/' + entry)
                    info.size = len(data)
                    info.mtime = 0
                    archive.addfile(info, io.BytesIO(data))
                info = tarfile.TarInfo(name)
                if link is None:
                    info.size = 0
                    archive.addfile(info, io.BytesIO(b''))
                else:
                    info.type = tarfile.SYMTYPE
                    info.linkname = link
                    archive.addfile(info)
            pack = gzip.compress(buffer.getvalue(), compresslevel=9, mtime=0)
            path = self.root / 'bad.tgz'
            path.write_bytes(pack)
            result = verify(path, build_manifest(pack), build_provenance(FILES))
            self.assertFalse(result.ok, name)
            self.assertTrue(any(failure.startswith(('unsafe_entry:', 'unsupported_entry:')) for failure in result.failures),
                            (name, result.failures))

    def test_manifest_must_match_the_artifact_digest(self):
        result = verify(self.artifact, {**build_manifest(self.pack), 'digest': 'd' * 64}, self.provenance)
        self.assertFalse(result.ok)
        self.assertIn('digest_mismatch', result.failures)

    def test_result_never_carries_package_contents(self):
        result = verify(self.artifact, build_manifest(self.pack), self.provenance)
        rendered = json.dumps(result.to_dict())
        self.assertNotIn('synthetic readme', rendered)
        self.assertNotIn('export const synthetic', rendered)

    def test_repository_provenance_recomputes_identically(self):
        document = json.loads((ROOT / 'typescript/PROVENANCE.json').read_text())
        self.assertEqual(document['content_digest'],
                         provenance_digest(document['name'], document['version'], document['files']))

    def test_manifest_rejects_unknown_capability_at_verification(self):
        result = verify(self.artifact, {**build_manifest(self.pack), 'capabilities': ['rollout.apply']}, self.provenance)
        self.assertFalse(result.ok)
        self.assertEqual(result.failures, ('manifest_invalid',))


if __name__ == '__main__':
    unittest.main()
