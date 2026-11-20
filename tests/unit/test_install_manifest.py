"""Install manifest: closed fields, no secrets, no absolute references."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from pydantic import ValidationError

import scripts.install_manifest as install_manifest
from agntia_ciberseguridad.install import InstallManifest

BASE = {
    'schema_version': 1,
    'package': '@agntia/ciberseguridad',
    'version': '0.1.0-alpha.3',
    'digest': 'a' * 64,
    'host_ref': 'agente@lab',
    'tenant': 'lab-cyber',
    'capabilities': ['findings.read'],
    'created_at': '2026-11-20T00:00:00+00:00',
    'source_sha': 'b' * 40,
}


class ManifestTests(unittest.TestCase):
    def test_valid_manifest_round_trips_without_extra_fields(self):
        manifest = InstallManifest.model_validate(BASE)
        payload = manifest.model_dump(mode='json')
        self.assertEqual(InstallManifest.model_validate(payload), manifest)
        self.assertEqual(set(payload), set(BASE))

    def test_missing_field_is_rejected(self):
        for field in ('digest', 'tenant', 'capabilities', 'source_sha'):
            document = {key: value for key, value in BASE.items() if key != field}
            with self.assertRaises(ValidationError):
                InstallManifest.model_validate(document)

    def test_unknown_capability_is_rejected(self):
        with self.assertRaises(ValidationError):
            InstallManifest.model_validate({**BASE, 'capabilities': ['rollout.apply']})
        with self.assertRaises(ValidationError):
            InstallManifest.model_validate({**BASE, 'capabilities': []})
        with self.assertRaises(ValidationError):
            InstallManifest.model_validate({**BASE, 'capabilities': ['findings.read', 'findings.read']})

    def test_secret_key_and_embedded_credentials_are_rejected(self):
        with self.assertRaises(ValidationError):
            InstallManifest.model_validate({**BASE, 'client_secret': 'value'})
        with self.assertRaises(ValidationError):
            InstallManifest.model_validate({**BASE, 'host_ref': 'https://user:token=abc@host'})
        with self.assertRaises(ValidationError):
            InstallManifest.model_validate({**BASE, 'host_ref': '-----BEGIN PRIVATE KEY-----'})

    def test_absolute_and_traversing_references_are_rejected(self):
        for host_ref in ('/srv/agente', 'C:\\agente', '../../etc/passwd'):
            with self.assertRaises(ValidationError):
                InstallManifest.model_validate({**BASE, 'host_ref': host_ref})

    def test_naive_timestamp_and_short_digest_are_rejected(self):
        with self.assertRaises(ValidationError):
            InstallManifest.model_validate({**BASE, 'created_at': '2026-11-20T00:00:00'})
        with self.assertRaises(ValidationError):
            InstallManifest.model_validate({**BASE, 'digest': 'A' * 64})
        with self.assertRaises(ValidationError):
            InstallManifest.model_validate({**BASE, 'source_sha': 'b' * 64})


class ManifestCliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.artifact = self.root / 'package.tgz'
        self.artifact.write_bytes(b'synthetic artifact')
        self.provenance = self.root / 'PROVENANCE.json'
        self.provenance.write_text(json.dumps({'name': '@agntia/ciberseguridad', 'version': '0.1.0-alpha.3'}))
        self.out = self.root / 'manifest.json'

    def tearDown(self):
        self.directory.cleanup()

    def test_build_then_check_keeps_the_artifact_digest(self):
        code = install_manifest.main(['build', '--artifact', str(self.artifact), '--host-ref', 'agente@lab',
            '--tenant', 'lab-cyber', '--capability', 'findings.read', '--provenance', str(self.provenance),
            '--source-sha', 'b' * 40, '--created-at', '2026-11-20T00:00:00+00:00', '--out', str(self.out)])
        self.assertEqual(code, 0)
        document = json.loads(self.out.read_text())
        self.assertEqual(document['digest'], hashlib.sha256(b'synthetic artifact').hexdigest())
        self.assertEqual(document['capabilities'], ['findings.read'])
        self.assertEqual(install_manifest.main(['check', '--manifest', str(self.out)]), 0)

    def test_build_refuses_missing_artifact(self):
        code = install_manifest.main(['build', '--artifact', str(self.root / 'absent.tgz'), '--host-ref', 'agente@lab',
            '--tenant', 'lab-cyber', '--capability', 'findings.read', '--provenance', str(self.provenance),
            '--out', str(self.out)])
        self.assertEqual(code, 1)
        self.assertFalse(self.out.exists())

    def test_check_reports_failure_without_echoing_values(self):
        document = {**BASE, 'host_ref': 'token=abc'}
        self.out.write_text(json.dumps(document))
        self.assertEqual(install_manifest.main(['check', '--manifest', str(self.out)]), 1)
