"""Deterministic markdown: same receipt in, same bytes out."""

from __future__ import annotations

from ..contracts.result import RunReceipt


def render_report(receipt: RunReceipt, extra_limitations: list[str] | None = None) -> str:
    lines = [
        f"# Run {receipt.run_id}",
        "",
        f"- Tenant: `{receipt.tenant_id}`",
        f"- Experiment: `{receipt.experiment_id}`",
        f"- Status: **{receipt.status.value}**",
        f"- Window: {receipt.started_at.isoformat()} → {receipt.ended_at.isoformat()}",
        "",
        "## Observations",
    ]
    if not receipt.observations:
        lines.append("_No observations. Absence of findings is not proof of security._")
    for observation in receipt.observations:
        lines.append(
            f"- `{observation.id}` [{observation.severity}] {observation.summary} "
            f"(reproduced={observation.reproduced}, confidence={observation.confidence})"
        )
    lines += ["", "## Evidence"]
    if not receipt.evidence:
        lines.append("_No evidence recorded._")
    for ref in receipt.evidence:
        lines.append(f"- `{ref.id}` sha256=`{ref.sha256}` bytes={ref.bytes}")
    lines += ["", "## Limitations"]
    limitations = list(receipt.limitations) + list(extra_limitations or [])
    lines += [f"- {item}" for item in limitations] or ["- None declared. This is suspicious, not reassuring."]
    return "\n".join(lines) + "\n"
