"""CY-VS-02: security regression tests using the repository's established fixtures.

No external accounts, real assets or network access are needed.
"""
import unittest
from datetime import timedelta

from pydantic import ValidationError

from agntia_ciberseguridad.contracts import AssetCreate, GrantCreate, GrantApproval
from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.util import utcnow
from tests.integration.test_jobs import Setup


class IdentityTenancyTests(Setup, unittest.TestCase):
    """Exercise real service authorization rather than mock HTTP responses."""

    def test_cross_tenant_asset_access_is_not_found(self):
        foreign = self.f.service.auth.authenticate(
            self.f.headers("operatorB")["Authorization"]
        )
        with self.assertRaises(DomainError) as caught:
            self.f.service.get_asset(foreign, "tenantA", self.fixture.asset["id"])
        self.assertEqual(caught.exception.status, 404)

    def test_cross_tenant_job_access_is_not_found(self):
        receipt = self.submit()
        foreign = self.f.service.auth.authenticate(
            self.f.headers("operatorB")["Authorization"]
        )
        with self.assertRaises(DomainError) as caught:
            self.store.get(foreign, "tenantA", receipt["id"])
        self.assertEqual(caught.exception.status, 404)

    def test_viewer_cannot_write_assets_or_submit_jobs(self):
        viewer = self.f.service.auth.authenticate(
            self.f.headers("viewerA")["Authorization"]
        )
        with self.assertRaises(DomainError) as caught:
            self.f.service.create_asset(
                viewer, "tenantA",
                AssetCreate(target_ref="repoA", kind="repository",
                            display_name="Synthetic repo"),
                "synthetic-test",
            )
        self.assertEqual(caught.exception.status, 403)
        with self.assertRaises(DomainError):
            self.store.submit(viewer, "tenantA", self.body,
                              "viewer-denied-001", "synthetic-test")

    def test_revocation_invalidates_existing_principal(self):
        principal = self.actor
        binding = next(p for p in self.f.settings.principals
                       if p.id == principal.binding_id)
        previous = binding.enabled
        try:
            binding.enabled = False
            with self.assertRaises(DomainError) as caught:
                self.f.service.list_assets(principal, "tenantA")
            self.assertEqual(caught.exception.code, "principal_revoked")
        finally:
            binding.enabled = previous

    def test_expired_grant_interval_is_invalid(self):
        now = utcnow()
        with self.assertRaises(ValidationError):
            GrantCreate(
                asset_id=self.fixture.asset["id"],
                consent_ref="consentA", profile="static_read",
                starts_at=now - timedelta(days=40),
                expires_at=now - timedelta(days=1),
                purpose="Synthetic regression test",
            )

    def test_missing_or_malformed_bearer_is_rejected(self):
        auth = self.f.service.auth
        for header in (None, "", "Basic abc", "Bearer short",
                       "Bearer " + "z" * 64):
            with self.subTest(header=bool(header)):
                with self.assertRaises(DomainError) as caught:
                    auth.authenticate(header)
                self.assertEqual(caught.exception.status, 401)

    def test_forged_approval_contract_rejects_bad_hash(self):
        with self.assertRaises(ValidationError):
            GrantApproval(
                expected_revision=0, proposal_hash="not-a-sha256",
                notes="Synthetic forged approval",
            )
