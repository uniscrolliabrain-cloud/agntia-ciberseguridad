"""CLI: judge the lab before trusting it."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .config import LabConfig
from .keys import KeyRing
from .domain.engagement import Engagement, EngagementStatus
from .domain.scope import Scope, Target
from .missions.registry import MissionRegistry
from .operations.daily import run_daily
from .providers.registry import default_registry
from .tools.registry import default_catalog


def _demo_engagement(tenant: str) -> tuple[Engagement, Scope, list[dict]]:
    now = datetime.now(timezone.utc)
    engagement = Engagement(
        id="eng-demo",
        tenant_id=tenant,
        authorized_by="founder",
        signature_ref="sig-demo",
        starts_at=now - timedelta(minutes=5),
        ends_at=now + timedelta(hours=1),
        status=EngagementStatus.ACTIVE,
    )
    scope = Scope(
        id="scope-demo",
        engagement_id=engagement.id,
        tenant_id=tenant,
        targets=[
            Target(kind="repo", ref="synthetic-shop", fingerprint="a" * 64),
            Target(kind="api", ref="synthetic-api", fingerprint="b" * 64),
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
    return engagement, scope, []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="advlab")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    sub.add_parser("missions")
    run = sub.add_parser("run")
    run.add_argument("--tenant", default="tenant-synthetic")
    args = parser.parse_args(argv)

    config = LabConfig.from_env()
    if args.command == "doctor":
        config.validate()
        registry = MissionRegistry(Path("adversarial_lab/library/missions"))
        print(
            json.dumps(
                {
                    "config": {
                        "allow_network": config.allow_network,
                        "allow_subprocess_providers": config.allow_subprocess_providers,
                        "max_evidence_bytes": config.max_evidence_bytes,
                    },
                    "tools": default_catalog().status(),
                    "providers": default_registry().status(),
                    "keys": {
                        **KeyRing(config.data_dir / "evidence").describe(),
                        **KeyRing(Path("adversarial_lab/var/keys")).describe(),
                    },
                    "missions": sorted(registry.load()),
                },
                indent=2,
            )
        )
        return 0
    if args.command == "missions":
        registry = MissionRegistry(Path("adversarial_lab/library/missions"))
        print(json.dumps({key: value["title"] for key, value in registry.load().items()}, indent=2))
        return 0

    engagement, scope, _ = _demo_engagement(args.tenant)
    missions = list(MissionRegistry(Path("adversarial_lab/library/missions")).load().values())
    for mission in missions:
        mission["target_ref"] = {
            "repo": "synthetic-shop",
            "api": "synthetic-api",
            "model": "synthetic-model",
            "container": "synthetic-db",
        }[mission["scope_kind"]]
    outcome = run_daily(config, engagement, scope, missions)
    print(
        json.dumps(
            {
                "run_id": outcome.receipt.run_id,
                "status": outcome.receipt.status.value,
                "selected": outcome.selected,
                "blocked_tools": outcome.blocked_tools,
                "report": str(outcome.report_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
