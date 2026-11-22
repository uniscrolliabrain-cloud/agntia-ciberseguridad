"""Dependency-free tests for external provider boundaries."""
import unittest

from agntia_ciberseguridad.integration_ports import (
    ConnectorPort, ConnectorSpec, ConnectorState, ConnectorUnavailable,
)


class ConnectorPortTests(unittest.TestCase):
    def test_disabled_is_not_connected(self):
        self.assertEqual(ConnectorSpec("github").state, ConnectorState.DISABLED)
        with self.assertRaises(ConnectorUnavailable):
            ConnectorPort(ConnectorSpec("github"), lambda: "called").execute()

    def test_missing_reference_is_closed(self):
        spec = ConnectorSpec("evidence", enabled=True)
        self.assertEqual(spec.state, ConnectorState.MISSING_CONFIG)
        with self.assertRaises(ConnectorUnavailable) as caught:
            ConnectorPort(spec).execute()
        self.assertEqual(caught.exception.code, "PROVIDER_NOT_CONFIGURED")

    def test_reference_is_not_connection(self):
        spec = ConnectorSpec("doppler", enabled=True, secret_ref="CYBER_DOPPLER_TOKEN")
        self.assertEqual(spec.state, ConnectorState.CONFIGURED_UNVERIFIED)
        with self.assertRaises(ConnectorUnavailable):
            ConnectorPort(spec, lambda: "should-not-run").execute()

    def test_verified_adapter_requires_injected_operation(self):
        spec = ConnectorSpec("github", enabled=True,
                             secret_ref="CYBER_GITHUB_TOKEN",
                             verified_environment="sandbox")
        with self.assertRaises(ConnectorUnavailable):
            ConnectorPort(spec).execute()
        self.assertEqual(ConnectorPort(spec, lambda x: x + 1, verify=lambda: True).execute(2), 3)

    def test_failed_verification_never_executes_adapter(self):
        spec = ConnectorSpec("github", enabled=True, secret_ref="CYBER_GITHUB_TOKEN", verified_environment="sandbox")
        called = []
        with self.assertRaises(ConnectorUnavailable) as caught:
            ConnectorPort(spec, lambda: called.append(True), verify=lambda: False).execute()
        self.assertEqual(caught.exception.code, "PROVIDER_VERIFICATION_FAILED")
        self.assertEqual(called, [])

    def test_bad_refs_and_forged_verification_are_rejected(self):
        for ref in ("token-value", "https://example.com", "CYBER_A=B", "cyber_key"):
            with self.subTest(ref=ref):
                with self.assertRaises(ValueError):
                    ConnectorSpec("github", enabled=True, secret_ref=ref)
        with self.assertRaises(ValueError):
            ConnectorSpec("github", verified_environment="production")
        with self.assertRaises(ValueError):
            ConnectorSpec("github", enabled=True,
                          verified_environment="production")

    def test_no_secret_values_in_repr(self):
        spec = ConnectorSpec("github", enabled=True, secret_ref="CYBER_GITHUB_TOKEN")
        self.assertNotIn("actual-secret-value", repr(spec))


if __name__ == "__main__":
    unittest.main()
