"""Firewall adapter DRY-RUN plan — intended policy model only."""

from __future__ import annotations

from secure_network_segmentation_lab.adapters.base import make_plan
from secure_network_segmentation_lab.models import AdapterPlan


def build_firewall_plan() -> AdapterPlan:
    return make_plan(
        "firewall",
        [
            "Compare intended reachability-policy.yml to synthetic observations.",
            "Produce DRY-RUN diff of allow/deny/conditional paths.",
            "Never push firewall rules or open management sessions.",
        ],
    )
