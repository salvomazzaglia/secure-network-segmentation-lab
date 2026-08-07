"""FDB / MAC table adapter DRY-RUN plan."""

from __future__ import annotations

from secure_network_segmentation_lab.adapters.base import make_plan
from secure_network_segmentation_lab.models import AdapterPlan


def build_fdb_plan() -> AdapterPlan:
    return make_plan(
        "fdb",
        [
            "Plan offline FDB/MAC-table import for access-port binding.",
            "Correlate LAA MAC → switch/port without claiming cable length.",
            "Never poll live switches.",
        ],
    )
