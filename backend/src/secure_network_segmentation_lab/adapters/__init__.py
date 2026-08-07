"""DRY-RUN adapter plans — connects=false, mutates=false."""

from __future__ import annotations

from secure_network_segmentation_lab.adapters.arp_plan import build_arp_plan
from secure_network_segmentation_lab.adapters.dhcp_plan import build_dhcp_plan
from secure_network_segmentation_lab.adapters.fdb_plan import build_fdb_plan
from secure_network_segmentation_lab.adapters.firewall_plan import build_firewall_plan
from secure_network_segmentation_lab.adapters.lldp_plan import build_lldp_plan
from secure_network_segmentation_lab.adapters.radius_plan import build_radius_plan
from secure_network_segmentation_lab.adapters.snmp_plan import build_snmp_plan
from secure_network_segmentation_lab.adapters.wlan_plan import build_wlan_plan
from secure_network_segmentation_lab.models import AdapterPlan

PLAN_BUILDERS = {
    "radius": build_radius_plan,
    "dhcp": build_dhcp_plan,
    "arp": build_arp_plan,
    "lldp": build_lldp_plan,
    "fdb": build_fdb_plan,
    "snmp": build_snmp_plan,
    "wlan": build_wlan_plan,
    "firewall": build_firewall_plan,
}

PLANS = PLAN_BUILDERS


def build_all_plans() -> list[AdapterPlan]:
    return [builder() for builder in PLAN_BUILDERS.values()]


def build_plan(adapter_id: str) -> AdapterPlan:
    if adapter_id not in PLAN_BUILDERS:
        raise KeyError(f"Unknown adapter: {adapter_id}")
    return PLAN_BUILDERS[adapter_id]()


def get_adapter_plan(adapter_id: str) -> AdapterPlan:
    return build_plan(adapter_id)
