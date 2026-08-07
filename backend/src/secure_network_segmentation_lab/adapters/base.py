"""Base helpers for DRY-RUN adapter plans."""

from __future__ import annotations

from secure_network_segmentation_lab.models import AdapterPlan, utc_now

COMMON_WARNINGS = [
    "DRY-RUN PLAN ONLY",
    "PROPOSED / SIMULATED — NOT APPLIED",
    "No network connection will be opened.",
    "connects=false; mutates=false",
]


def make_plan(adapter_id: str, steps: list[str]) -> AdapterPlan:
    return AdapterPlan(
        adapter_id=adapter_id,
        mode="live-adapter-plan",
        capability="read-only-plan",
        connects=False,
        mutates=False,
        steps=steps,
        warnings=list(COMMON_WARNINGS),
        generated_at_utc=utc_now(),
    )
