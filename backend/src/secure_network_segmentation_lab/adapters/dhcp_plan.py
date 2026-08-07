"""DHCP adapter DRY-RUN plan."""

from __future__ import annotations

from secure_network_segmentation_lab.adapters.base import make_plan
from secure_network_segmentation_lab.models import AdapterPlan


def build_dhcp_plan() -> AdapterPlan:
    return make_plan(
        "dhcp",
        [
            "Plan offline ingest of sanitized DHCP lease/fingerprint exports.",
            "Normalize hostname, vendor-class, and fingerprint into observations.",
            "Never query live DHCP servers in v1.0.",
            "Never modify scopes or reservations.",
        ],
    )
