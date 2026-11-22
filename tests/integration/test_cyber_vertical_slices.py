"""CY-VS-03/04: executable synthetic vertical slices using existing domain stores.

Scanner output is explicitly simulated; these tests DO NOT claim a real OSS scanner,
production connector, customer remediation or independently verified fix.
"""
import unittest
from datetime import timedelta

from agntia_ciberseguridad.jobs.worker import Worker
from agntia_ciberseguridad.findings.store import FindingStore
from agntia_ciberseguridad.reports import Reports, ReportRequest
from agntia_ciberseguridad.reviews import Reviews, ReviewProposal, ReviewApproval
from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.util import utcnow
from tests.security.support_custody import CustodySetup
from tests.integration.test_jobs import Setup


class SyntheticScanToReport(CustodySetup, unittest.IsolatedAsyncioTestCase):
    async def test_authorized_snapshot_job_finding_report(self):
        # Existing fixture creates approved grant and captured local snapshot.
        store = Setup.submit(self, "cyber-vs03-synthetic")
        self.assertEqual(store["state"], "pending")
        from agntia_ciberseguridad.jobs.store import JobStore
        from agntia_ciberseguridad.safety import ReleaseGates
        jobs = JobStore(self.f.service, gates=ReleaseGates(True, True, True),
                        clock=lambda: self.instant[0])
        scanner = Setup.scanner(self, Setup.result(
            self, [{"rule_id": "synthetic-rule", "path": "file.py",
                    "start_line": 1}]))
        completed = await Worker(jobs, scanner, "synthetic-worker").run_once()
        self.assertEqual(completed["state"], "completed")
        findings = FindingStore(self.f.service).list(self.actor, "tenantA")["items"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["state"], "suspected")
        report = Reports(self.f.service).create(
            self.actor, "tenantA",
            ReportRequest(job_ids=[completed["id"]]), "synthetic-vs03")
        self.assertEqual(report["summary"]["jobs"], 1)
        self.assertEqual(report["summary"]["findings"], 1)
        self.assertFalse(report["security_guarantee"])
        self.assertEqual(report["review_status"], "not_reviewed")
        self.assertEqual(
            Reports(self.f.service).get(
                self.actor, "tenantA", report["id"], "synthetic-vs03")["id"],
            report["id"],
        )


class SyntheticFindingReview(CustodySetup, unittest.IsolatedAsyncioTestCase):
    async def test_review_requires_independent_human_and_evidence(self):
        from agntia_ciberseguridad.jobs.store import JobStore
        from agntia_ciberseguridad.safety import ReleaseGates
        jobs = JobStore(self.f.service, gates=ReleaseGates(True, True, True),
                        clock=lambda: self.instant[0])
        jobs.submit(self.actor, "tenantA", self.body,
                    "cyber-vs04-synthetic", "synthetic-vs04")
        scanner = Setup.scanner(self, Setup.result(
            self, [{"rule_id": "synthetic-rule", "path": "file.py",
                    "start_line": 1}]))
        await Worker(jobs, scanner, "synthetic-worker").run_once()
        finding = FindingStore(self.f.service).list(
            self.actor, "tenantA")["items"][0]
        evidence = self.reviewed_document()
        reviews = Reviews(self.f.service)
        proposal = reviews.propose(
            self.actor, "tenantA",
            ReviewProposal(
                finding_id=finding["id"],
                expected_finding_revision=finding["revision"],
                action="confirm",
                reason="Human review of synthetic observation",
                evidence_ids=[evidence["id"]],
            ),
            "synthetic-vs04",
        )
        with self.assertRaises(DomainError):
            reviews.approve(
                self.actor, "tenantA", proposal["id"],
                ReviewApproval(expected_revision=0,
                               proposal_hash=proposal["proposal_hash"]),
                "synthetic-vs04",
            )
        decision = reviews.approve(
            self.reviewer, "tenantA", proposal["id"],
            ReviewApproval(expected_revision=0,
                           proposal_hash=proposal["proposal_hash"]),
            "synthetic-vs04",
        )
        self.assertEqual(decision["action"], "confirm")
        updated = FindingStore(self.f.service).history(
            self.actor, "tenantA", finding["id"])["finding"]
        self.assertEqual(updated["state"], "confirmed")
        self.assertEqual(updated["revision"], finding["revision"] + 1)
