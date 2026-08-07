"""LLDP adapter DRY-RUN plan."""

from __future__ import annotations

from secure_network_segmentation_lab.adapters.base import make_plan
from secure_network_segmentation_lab.models import AdapterPlan


def build_lldp_plan() -> AdapterPlan:
    return make_plan(
        "lldp",
        [
            "Plan offline LLDP neighbor JSON import for wired topology edges.",
            "Record switch/port adjacency with provenance=reported.",
            "Never query live LLDP daemons or SNMP for LLDP MIBs in v1.0.",
        ],
    )
