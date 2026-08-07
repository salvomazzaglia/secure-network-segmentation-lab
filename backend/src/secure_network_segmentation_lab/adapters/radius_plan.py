"""RADIUS adapter DRY-RUN plan — no CoA, no Disconnect-Request, no secrets."""

from __future__ import annotations

from secure_network_segmentation_lab.adapters.base import make_plan
from secure_network_segmentation_lab.models import AdapterPlan


def build_radius_plan() -> AdapterPlan:
    return make_plan(
        "radius",
        [
            "Identify future read-only RADIUS accounting/auth event source (not connected).",
            "Map synthetic Calling-Station-Id (LAA MAC) → device inventory.",
            "Map NAS-Identifier → synthetic switch/AP label.",
            "Represent Tunnel-Type / Tunnel-Medium-Type / Tunnel-Private-Group-ID conceptually.",
            "Emit VLAN recommendation as DRY-RUN only — never send Access-Accept mutations.",
            "Do NOT implement RADIUS CoA or Disconnect-Request.",
            "Do NOT store or transmit shared secrets.",
        ],
    )
