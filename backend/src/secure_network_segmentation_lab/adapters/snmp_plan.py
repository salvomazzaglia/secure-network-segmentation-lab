"""SNMP adapter DRY-RUN plan — read-only plan, no SET."""

from __future__ import annotations

from secure_network_segmentation_lab.adapters.base import make_plan
from secure_network_segmentation_lab.models import AdapterPlan


def build_snmp_plan() -> AdapterPlan:
    return make_plan(
        "snmp",
        [
            "Document future read-only SNMP GET plan for interface/FDB hints.",
            "Explicitly forbid SNMP SET and write communities.",
            "No live SNMP sessions in v1.0.",
        ],
    )
