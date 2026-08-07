"""WLAN adapter DRY-RUN plan."""

from __future__ import annotations

from secure_network_segmentation_lab.adapters.base import make_plan
from secure_network_segmentation_lab.models import AdapterPlan


def build_wlan_plan() -> AdapterPlan:
    return make_plan(
        "wlan",
        [
            "Plan offline WLAN association/RSSI metric JSONL import.",
            "Map RSSI → signal buckets (strong/good/moderate/weak).",
            "Never convert RSSI to meters or claim physical location.",
            "Never disconnect wireless clients.",
        ],
    )
