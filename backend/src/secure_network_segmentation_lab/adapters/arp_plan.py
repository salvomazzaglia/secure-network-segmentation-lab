"""ARP/neighbor adapter DRY-RUN plan."""

from __future__ import annotations

from secure_network_segmentation_lab.adapters.base import make_plan
from secure_network_segmentation_lab.models import AdapterPlan


def build_arp_plan() -> AdapterPlan:
    return make_plan(
        "arp",
        [
            "Plan offline import of sanitized ARP/neighbor tables.",
            "Bind documentation IPs to LAA MACs in synthetic inventory.",
            "Never run arp/ip neigh against a live host.",
        ],
    )
