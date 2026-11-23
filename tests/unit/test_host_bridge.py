"""Host identity cannot come from the model or bypass child permissions."""
import unittest
from unittest.mock import Mock

from agntia_ciberseguridad.host_bridge import HostIdentity, resolve_host_read
from agntia_ciberseguridad.errors import DomainError


class HostBridgeTests(unittest.TestCase):
    def setUp(self):
        self.service = Mock()
        self.service.auth.current.return_value = Mock(
            actor_id="actorA", tenants=("tenantA",)
        )
        self.identity = HostIdentity(
            tenant_id="tenantA", principal_binding_id="bindingA",
            host_actor_id="actorA", assurance="verified_host",
            correlation_id="synthetic-001",
        )

    def test_missing_identity_fails_closed(self):
        with self.assertRaises(DomainError) as caught:
            resolve_host_read(self.service, None, "assets.read")
        self.assertEqual(caught.exception.code, "HOST_IDENTITY_NOT_CONFIGURED")

    def test_write_capability_is_never_exposed(self):
        with self.assertRaises(DomainError):
            resolve_host_read(self.service, self.identity, "jobs.submit")
        self.service.authorize.assert_not_called()

    def test_mismatched_actor_is_rejected(self):
        self.service.auth.current.return_value.actor_id = "other"
        with self.assertRaises(DomainError) as caught:
            resolve_host_read(self.service, self.identity, "assets.read")
        self.assertEqual(caught.exception.code, "HOST_IDENTITY_MISMATCH")

    def test_current_child_authorization_is_required(self):
        principal = resolve_host_read(self.service, self.identity, "findings.read")
        self.service.authorize.assert_called_once_with(
            principal, "tenantA", "findings.read"
        )

    def test_assurance_marker_is_explicit(self):
        with self.assertRaises(ValueError):
            HostIdentity("tenantA", "bindingA", "actorA", "unverified", "trace")


if __name__ == "__main__":
    unittest.main()
