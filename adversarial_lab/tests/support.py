from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agntia_adversarial.config import LabConfig  # noqa: E402
from agntia_adversarial.domain.engagement import Engagement, EngagementStatus  # noqa: E402
from agntia_adversarial.domain.scope import Scope, Target  # noqa: E402

LIBRARY = ROOT / "library" / "missions"


def engagement(**overrides) -> Engagement:
    now = datetime.now(timezone.utc)
    payload = dict(
        id="eng-1",
        tenant_id="tenant-a",
        authorized_by="founder",
        signature_ref="sig-1",
        starts_at=now - timedelta(minutes=5),
        ends_at=now + timedelta(hours=1),
        status=EngagementStatus.ACTIVE,
    )
    payload.update(overrides)
    return Engagement(**payload)


def scope(**overrides) -> Scope:
    payload = dict(
        id="scope-1",
        engagement_id="eng-1",
        tenant_id="tenant-a",
        targets=[
            Target(kind="api", ref="synthetic-api", fingerprint="b" * 64),
            Target(kind="repo", ref="synthetic-shop", fingerprint="a" * 64),
            Target(kind="model", ref="synthetic-model", fingerprint="c" * 64),
            Target(kind="container", ref="synthetic-db", fingerprint="d" * 64),
        ],
        capabilities=[
            "repo.read",
            "repo.static",
            "sbom",
            "sandbox.test",
            "api.passive",
            "api.active",
            "ai.evaluate",
            "chaos.simulate",
            "evidence.write",
        ],
    )
    payload.update(overrides)
    return Scope(**payload)


def config(tmp_path: Path) -> LabConfig:
    return LabConfig(data_dir=tmp_path / "var", max_evidence_bytes=1024 * 1024)


from agntia_adversarial.contracts.experiment import ExperimentSpec, Limits, TargetRef  # noqa: E402
from agntia_adversarial.contracts.result import RunReceipt, Status  # noqa: E402


def experiment(**overrides) -> ExperimentSpec:
    now = datetime.now(timezone.utc)
    payload = dict(
        id="exp-1",
        campaign_id="C10",
        mission_id="repo-review",
        tenant_id="tenant-a",
        engagement_id="eng-1",
        scope_id="scope-1",
        targets=[TargetRef(kind="repo", ref="synthetic-shop", fingerprint="a" * 64)],
        capabilities=["repo.static"],
        limits=Limits(max_requests=4),
        stop_conditions=["never_network"],
        created_at=now,
    )
    payload.update(overrides)
    return ExperimentSpec(**payload)


def receipt(**overrides) -> RunReceipt:
    now = datetime.now(timezone.utc)
    payload = dict(
        run_id="run-1",
        experiment_id="exp-1",
        tenant_id="tenant-a",
        status=Status.PARTIAL,
        started_at=now,
        ended_at=now,
        limitations=["synthetic"],
    )
    payload.update(overrides)
    return RunReceipt(**payload)
