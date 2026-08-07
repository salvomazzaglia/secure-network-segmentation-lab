#!/usr/bin/env python3
"""Generate deterministic synthetic lab artifacts (seed=42 by default).

CRITICAL: Documentation IPs only (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24,
2001:db8::/32). LAA MACs starting with 02:. Never RFC1918. Never real network data.
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "synthetic"

DOC_NETS = {
    "management": "192.0.2",
    "infrastructure": "198.51.100",
    "trusted": "203.0.113",
}
SSIDS = ("SYNTHETIC-LAB", "SYNTHETIC-GUEST", "SYNTHETIC-IOT")
VENDOR = {
    "infra": "Sample Network Hardware",
    "endpoint": "Synthetic Devices Ltd.",
    "server": "Example Systems Inc.",
    "iot": "Demo IoT Corporation",
    "printer": "Fictional Print Works",
}

BASE_TIME = datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC)


def mac(rng: random.Random, n: int) -> str:
    # Locally administered: 02:xx:xx:xx:xx:xx
    b = [
        0x02,
        rng.randint(0, 255),
        rng.randint(0, 255),
        rng.randint(0, 255),
        rng.randint(0, 255),
        n & 0xFF,
    ]
    return ":".join(f"{x:02x}" for x in b)


def ip4(net: str, host: int) -> str:
    return f"{net}.{host}"


def ip6(host: int) -> str:
    return f"2001:db8::{host:x}"


def ts(offset_hours: float = 0) -> str:
    return (BASE_TIME + timedelta(hours=offset_hours)).isoformat()


def device(
    device_id: str,
    alias: str,
    mac_addr: str,
    segment: str,
    klass: str,
    *,
    vendor: str,
    connection: str,
    online: bool = True,
    tags: list[str] | None = None,
    ipv4: str | None = None,
    hostname: str | None = None,
    security_state: str = "approved",
    stale: bool = False,
    first_seen: str | None = None,
    last_seen: str | None = None,
    ssid: str | None = None,
    ap_id: str | None = None,
    switch_id: str | None = None,
    port_id: str | None = None,
    rssi: int | None = None,
    signal_bucket: str | None = None,
    metadata: dict | None = None,
) -> dict:
    return {
        "device_id": device_id,
        "alias": alias,
        "mac": mac_addr,
        "ipv4": ipv4,
        "ipv6": ip6(abs(hash(device_id)) % 0xFFFF) if ipv4 else None,
        "hostname": hostname or alias.lower().replace(" ", "-"),
        "vendor": vendor,
        "device_class_hint": klass,
        "connection_type": connection,
        "current_segment": segment,
        "recommended_segment": None,
        "security_state": security_state,
        "online": online,
        "first_seen_utc": first_seen or ts(-720),
        "last_seen_utc": last_seen or (ts(-48) if stale else ts(-0.5)),
        "stale": stale,
        "tags": tags or [],
        "ssid": ssid,
        "ap_id": ap_id,
        "switch_id": switch_id,
        "port_id": port_id,
        "signal_bucket": signal_bucket,
        "rssi": rssi,
        "ownership_label": "SYNTHETIC-ORG",
        "provenance": "synthetic",
        "source_mode": "synthetic",
        "metadata": metadata or {"synthetic": True},
    }


def build_lab(
    seed: int = 42,
) -> tuple[
    list[dict],
    list[dict],
    list[dict],
    list[dict],
    list[dict],
    list[dict],
    list[dict],
    list[dict],
]:
    rng = random.Random(seed)
    devices: list[dict] = []
    observations: list[dict] = []
    services: list[dict] = []
    nodes: list[dict] = []
    edges: list[dict] = []
    radius_events: list[dict] = []
    wireless_metrics: list[dict] = []
    policy_events: list[dict] = []

    idx = 1

    def add(d: dict, x: float, y: float, z: float = 0.0, node_type: str | None = None) -> None:
        nonlocal idx
        devices.append(d)
        nodes.append(
            {
                "node_id": f"node-{d['device_id']}",
                "device_id": d["device_id"],
                "node_type": node_type or d["device_class_hint"],
                "label": d["alias"],
                "segment": d["current_segment"],
                "x": x,
                "y": y,
                "z": z,
            }
        )
        idx += 1

    # --- Infrastructure: 1 FW, 1 core SW, 2 edge SW, 3 APs ---
    fw = device(
        "SYNTHETIC-FW-01",
        "SYNTHETIC-FW-01",
        mac(rng, 1),
        "management",
        "firewall",
        vendor=VENDOR["infra"],
        connection="wired",
        ipv4=ip4(DOC_NETS["management"], 1),
        switch_id=None,
    )
    add(fw, 0, 0, 2, "firewall")

    core = device(
        "SYNTHETIC-SW-CORE-01",
        "SYNTHETIC-SW-CORE-01",
        mac(rng, 2),
        "infrastructure",
        "switch",
        vendor=VENDOR["infra"],
        connection="wired",
        ipv4=ip4(DOC_NETS["infrastructure"], 1),
    )
    add(core, 0, -2, 1, "switch")

    edge1 = device(
        "SYNTHETIC-SW-EDGE-01",
        "SYNTHETIC-SW-EDGE-01",
        mac(rng, 3),
        "infrastructure",
        "switch",
        vendor=VENDOR["infra"],
        connection="wired",
        ipv4=ip4(DOC_NETS["infrastructure"], 2),
    )
    add(edge1, -4, -3, 0.5, "switch")

    edge2 = device(
        "SYNTHETIC-SW-EDGE-02",
        "SYNTHETIC-SW-EDGE-02",
        mac(rng, 4),
        "infrastructure",
        "switch",
        vendor=VENDOR["infra"],
        connection="wired",
        ipv4=ip4(DOC_NETS["infrastructure"], 3),
    )
    add(edge2, 4, -3, 0.5, "switch")

    for i, (ax, ay) in enumerate([(-3, -5), (0, -5), (3, -5)], start=1):
        ap = device(
            f"SYNTHETIC-AP-{i:02d}",
            f"SYNTHETIC-AP-{i:02d}",
            mac(rng, 10 + i),
            "infrastructure",
            "access_point",
            vendor=VENDOR["infra"],
            connection="wired",
            ipv4=ip4(DOC_NETS["infrastructure"], 10 + i),
            switch_id="SYNTHETIC-SW-EDGE-01" if i < 3 else "SYNTHETIC-SW-EDGE-02",
            port_id=f"Gi0/{i}",
        )
        add(ap, ax, ay, 1.2, "access_point")

    # Uplinks (wired path across two switches)
    edges.extend(
        [
            {
                "edge_id": "uplink-edge1-core",
                "source_node_id": "node-SYNTHETIC-SW-EDGE-01",
                "target_node_id": "node-SYNTHETIC-SW-CORE-01",
                "edge_type": "logical_upstream",
                "provenance": "synthetic",
                "label": "uplink",
            },
            {
                "edge_id": "uplink-edge2-core",
                "source_node_id": "node-SYNTHETIC-SW-EDGE-02",
                "target_node_id": "node-SYNTHETIC-SW-CORE-01",
                "edge_type": "logical_upstream",
                "provenance": "synthetic",
                "label": "uplink",
            },
            {
                "edge_id": "uplink-core-fw",
                "source_node_id": "node-SYNTHETIC-SW-CORE-01",
                "target_node_id": "node-SYNTHETIC-FW-01",
                "edge_type": "logical_upstream",
                "provenance": "synthetic",
                "label": "core-to-fw",
            },
        ]
    )

    # --- 3 servers ---
    for i in range(1, 4):
        d = device(
            f"SYNTHETIC-SRV-{i:02d}",
            f"SYNTHETIC-SRV-{i:02d}",
            mac(rng, 20 + i),
            "infrastructure",
            "server",
            vendor=VENDOR["server"],
            connection="wired",
            ipv4=ip4(DOC_NETS["infrastructure"], 20 + i),
            hostname=f"synthetic-srv-{i:02d}",
            switch_id="SYNTHETIC-SW-EDGE-01",
            port_id=f"Gi1/{i}",
            security_state="pending_approval" if i == 3 else "approved",
            tags=["requires_approval"] if i == 3 else [],
        )
        add(d, -5 + i, -1, 0)
        services.append(
            {
                "service_id": f"svc-srv-{i}-443",
                "device_id": d["device_id"],
                "port": 443,
                "protocol": "tcp",
                "category": "secure_web",
                "provenance": "observed",
            }
        )
        services.append(
            {
                "service_id": f"svc-srv-{i}-22",
                "device_id": d["device_id"],
                "port": 22,
                "protocol": "tcp",
                "category": "ssh",
                "provenance": "observed",
            }
        )
        edges.append(
            {
                "edge_id": f"wired-{d['device_id']}-edge1",
                "source_node_id": f"node-{d['device_id']}",
                "target_node_id": "node-SYNTHETIC-SW-EDGE-01",
                "edge_type": "wired",
                "provenance": "synthetic",
                "label": "access",
                "metadata": {"port_id": d["port_id"]},
            }
        )

    # --- 5 workstations/laptops (one intentionally wrong segment) ---
    for i in range(1, 6):
        is_laptop = i > 3
        klass = "laptop" if is_laptop else "workstation"
        # Device incorrectly located in Trusted: IoT-like printer role later;
        # workstation #5 wrongly? We'll put laptop 5 as policy violation guest-ish
        segment = "trusted"
        security = "approved"
        tags: list[str] = []
        if i == 5:
            # intentional: device incorrectly in trusted with violation flag
            security = "policy_violation"
            tags = ["intentional_misplacement"]
        d = device(
            f"SYNTHETIC-{'LAP' if is_laptop else 'WS'}-{i:02d}",
            f"SYNTHETIC-{'LAP' if is_laptop else 'WS'}-{i:02d}",
            mac(rng, 30 + i),
            segment,
            klass,
            vendor=VENDOR["endpoint"],
            connection="wired" if i <= 3 else "wireless",
            ipv4=ip4(DOC_NETS["trusted"], 30 + i),
            hostname=f"synthetic-{'lap' if is_laptop else 'ws'}-{i:02d}",
            switch_id="SYNTHETIC-SW-EDGE-02" if i <= 3 else None,
            port_id=f"Gi2/{i}" if i <= 3 else None,
            ssid=SSIDS[0] if i > 3 else None,
            ap_id="SYNTHETIC-AP-02" if i > 3 else None,
            rssi=-48 if i == 4 else (-72 if i == 5 else None),
            signal_bucket="strong" if i == 4 else ("moderate" if i == 5 else None),
            security_state=security,
            tags=tags,
            online=i != 3,  # offline device
            last_seen=ts(-30) if i == 3 else None,
        )
        add(d, 2 + i * 0.8, -2, 0)
        if i <= 3:
            edges.append(
                {
                    "edge_id": f"wired-{d['device_id']}-edge2",
                    "source_node_id": f"node-{d['device_id']}",
                    "target_node_id": "node-SYNTHETIC-SW-EDGE-02",
                    "edge_type": "wired",
                    "provenance": "synthetic",
                    "label": "access",
                }
            )
        else:
            edges.append(
                {
                    "edge_id": f"wlan-{d['device_id']}-ap02",
                    "source_node_id": f"node-{d['device_id']}",
                    "target_node_id": "node-SYNTHETIC-AP-02",
                    "edge_type": "wireless_association",
                    "provenance": "synthetic",
                    "label": "association",
                }
            )

    # --- 5 phones/tablets (guest + corporate) ---
    for i in range(1, 6):
        guest = i <= 2
        klass = "smartphone" if i % 2 else "tablet"
        d = device(
            f"SYNTHETIC-{'PHONE' if klass == 'smartphone' else 'TAB'}-{i:02d}",
            f"SYNTHETIC-{'PHONE' if klass == 'smartphone' else 'TAB'}-{i:02d}",
            mac(rng, 40 + i),
            "guest" if guest else "trusted",
            klass,
            vendor=VENDOR["endpoint"],
            connection="wireless",
            ipv4=None,
            hostname=f"synthetic-mobile-{i:02d}",
            ssid=SSIDS[1] if guest else SSIDS[0],
            ap_id="SYNTHETIC-AP-01" if guest else "SYNTHETIC-AP-03",
            rssi=-50 if i == 1 else (-78 if i == 2 else -60),
            signal_bucket="strong" if i == 1 else ("weak" if i == 2 else "good"),
            tags=["guest_ssid"] if guest else [],
        )
        add(d, -2 + i, -6, 0.2)
        edges.append(
            {
                "edge_id": f"wlan-{d['device_id']}-{d['ap_id']}",
                "source_node_id": f"node-{d['device_id']}",
                "target_node_id": f"node-{d['ap_id']}",
                "edge_type": "wireless_association",
                "provenance": "synthetic",
                "label": "association",
            }
        )

    # --- 3 printers in IoT ---
    for i in range(1, 4):
        d = device(
            f"SYNTHETIC-PRT-{i:02d}",
            f"SYNTHETIC-PRT-{i:02d}",
            mac(rng, 50 + i),
            "iot",
            "printer",
            vendor=VENDOR["printer"],
            connection="wired",
            ipv4=None,
            hostname=f"synthetic-printer-{i:02d}",
            switch_id="SYNTHETIC-SW-EDGE-01",
            port_id=f"Gi3/{i}",
        )
        add(d, -6, -4 + i * 0.5, 0)
        services.append(
            {
                "service_id": f"svc-prt-{i}",
                "device_id": d["device_id"],
                "port": 9100,
                "protocol": "tcp",
                "category": "printing",
                "provenance": "observed",
            }
        )
        edges.append(
            {
                "edge_id": f"wired-{d['device_id']}-edge1",
                "source_node_id": f"node-{d['device_id']}",
                "target_node_id": "node-SYNTHETIC-SW-EDGE-01",
                "edge_type": "wired",
                "provenance": "synthetic",
                "label": "access",
            }
        )

    # --- 4 cameras in IoT ---
    for i in range(1, 5):
        d = device(
            f"SYNTHETIC-CAM-{i:02d}",
            f"SYNTHETIC-CAM-{i:02d}",
            mac(rng, 60 + i),
            "iot",
            "camera",
            vendor=VENDOR["iot"],
            connection="wired",
            hostname=f"synthetic-cam-{i:02d}",
            switch_id="SYNTHETIC-SW-EDGE-02",
            port_id=f"Gi4/{i}",
        )
        add(d, 6, -4 + i * 0.4, 0)
        services.append(
            {
                "service_id": f"svc-cam-{i}",
                "device_id": d["device_id"],
                "port": 554,
                "protocol": "tcp",
                "category": "media",
                "provenance": "observed",
            }
        )
        edges.append(
            {
                "edge_id": f"wired-{d['device_id']}-edge2",
                "source_node_id": f"node-{d['device_id']}",
                "target_node_id": "node-SYNTHETIC-SW-EDGE-02",
                "edge_type": "wired",
                "provenance": "synthetic",
                "label": "access",
            }
        )

    # --- 5 generic IoT ---
    for i in range(1, 6):
        d = device(
            f"SYNTHETIC-IOT-{i:02d}",
            f"SYNTHETIC-IOT-{i:02d}",
            mac(rng, 70 + i),
            "iot",
            "iot",
            vendor=VENDOR["iot"],
            connection="wireless",
            hostname=f"synthetic-iot-{i:02d}",
            ssid=SSIDS[2],
            ap_id="SYNTHETIC-AP-01",
            rssi=-58 - i,
            signal_bucket="good" if i < 4 else "moderate",
        )
        add(d, -4 + i * 0.5, -7, 0.1)
        edges.append(
            {
                "edge_id": f"wlan-{d['device_id']}-ap01",
                "source_node_id": f"node-{d['device_id']}",
                "target_node_id": "node-SYNTHETIC-AP-01",
                "edge_type": "wireless_association",
                "provenance": "synthetic",
                "label": "association",
            }
        )

    # --- 2 media devices ---
    for i in range(1, 3):
        d = device(
            f"SYNTHETIC-MEDIA-{i:02d}",
            f"SYNTHETIC-MEDIA-{i:02d}",
            mac(rng, 80 + i),
            "iot",
            "media_device",
            vendor=VENDOR["iot"],
            connection="wireless",
            hostname=f"synthetic-media-{i:02d}",
            ssid=SSIDS[2],
            ap_id="SYNTHETIC-AP-03",
            rssi=-62,
            signal_bucket="good",
        )
        add(d, 1 + i, -7.5, 0.1)
        edges.append(
            {
                "edge_id": f"wlan-{d['device_id']}-ap03",
                "source_node_id": f"node-{d['device_id']}",
                "target_node_id": "node-SYNTHETIC-AP-03",
                "edge_type": "wireless_association",
                "provenance": "synthetic",
                "label": "association",
            }
        )

    # --- 2 network appliances ---
    for i in range(1, 3):
        d = device(
            f"SYNTHETIC-APPL-{i:02d}",
            f"SYNTHETIC-APPL-{i:02d}",
            mac(rng, 90 + i),
            "infrastructure",
            "network_appliance",
            vendor=VENDOR["server"],
            connection="wired",
            ipv4=ip4(DOC_NETS["infrastructure"], 40 + i),
            hostname=f"synthetic-appliance-{i:02d}",
            switch_id="SYNTHETIC-SW-CORE-01",
            port_id=f"Gi0/{10 + i}",
            security_state="pending_approval",
            tags=["requires_approval"],
        )
        add(d, i * 0.5, -1.5, 0.3)
        edges.append(
            {
                "edge_id": f"wired-{d['device_id']}-core",
                "source_node_id": f"node-{d['device_id']}",
                "target_node_id": "node-SYNTHETIC-SW-CORE-01",
                "edge_type": "wired",
                "provenance": "synthetic",
                "label": "access",
            }
        )

    # --- 4 unknown/quarantined (+ uncertain classification candidate) ---
    for i in range(1, 5):
        uncertain = i == 2
        stale = i == 4
        d = device(
            f"SYNTHETIC-UNK-{i:02d}",
            f"SYNTHETIC-UNK-{i:02d}",
            mac(rng, 100 + i),
            "quarantine",
            "unknown",
            vendor="Synthetic Devices Ltd.",
            connection="wireless" if i % 2 else "wired",
            hostname=f"synthetic-unknown-{i:02d}" if not uncertain else "host-xyz-temp",
            security_state="quarantined" if not uncertain else "uncertain",
            ssid=SSIDS[0] if i % 2 else None,
            ap_id="SYNTHETIC-AP-02" if i % 2 else None,
            switch_id="SYNTHETIC-SW-EDGE-01" if not i % 2 else None,
            port_id=f"Gi5/{i}" if not i % 2 else None,
            rssi=-70 if i % 2 else None,
            signal_bucket="moderate" if i % 2 else None,
            stale=stale,
            last_seen=ts(-100) if stale else ts(-1),
            tags=["awaiting_approval"] if i == 1 else (["uncertain_seed"] if uncertain else []),
            metadata={"approval_state": "required"} if i == 1 else {"synthetic": True},
        )
        add(d, -1 + i * 0.6, 2, 0)
        if i % 2:
            edges.append(
                {
                    "edge_id": f"wlan-{d['device_id']}-ap02",
                    "source_node_id": f"node-{d['device_id']}",
                    "target_node_id": "node-SYNTHETIC-AP-02",
                    "edge_type": "wireless_association",
                    "provenance": "synthetic",
                    "label": "association",
                }
            )
        else:
            edges.append(
                {
                    "edge_id": f"wired-{d['device_id']}-edge1",
                    "source_node_id": f"node-{d['device_id']}",
                    "target_node_id": "node-SYNTHETIC-SW-EDGE-01",
                    "edge_type": "wired",
                    "provenance": "synthetic",
                    "label": "access",
                }
            )

    # Intentional: camera-like device wrongly in trusted (policy issue)
    wrong = device(
        "SYNTHETIC-CAM-MISPLACED-01",
        "SYNTHETIC-CAM-MISPLACED-01",
        mac(rng, 110),
        "trusted",
        "camera",
        vendor=VENDOR["iot"],
        connection="wired",
        hostname="synthetic-cam-misplaced-01",
        switch_id="SYNTHETIC-SW-EDGE-02",
        port_id="Gi4/9",
        security_state="policy_violation",
        tags=["intentional_policy_issue"],
        ipv4=ip4(DOC_NETS["trusted"], 99),
    )
    add(wrong, 5, 0, 0)
    edges.append(
        {
            "edge_id": "wired-SYNTHETIC-CAM-MISPLACED-01-edge2",
            "source_node_id": "node-SYNTHETIC-CAM-MISPLACED-01",
            "target_node_id": "node-SYNTHETIC-SW-EDGE-02",
            "edge_type": "wired",
            "provenance": "synthetic",
            "label": "access",
        }
    )
    policy_events.append(
        {
            "event_type": "policy_violation_detected",
            "device_id": wrong["device_id"],
            "message": "Camera class in Trusted segment — intentional synthetic issue",
            "change_label": "PROPOSED / SIMULATED — NOT APPLIED",
        }
    )

    # Observations for all devices
    for i, d in enumerate(devices):
        obs = {
            "observation_id": f"obs-{i:04d}",
            "device_id": d["device_id"],
            "observed_at_utc": d["last_seen_utc"],
            "provenance": "synthetic",
            "source": "synthetic-generator",
            "ipv4": d.get("ipv4"),
            "ipv6": d.get("ipv6"),
            "mac": d["mac"],
            "hostname": d.get("hostname"),
            "vendor_hint": d.get("vendor"),
            "dhcp_fingerprint": d.get("device_class_hint"),
            "reported_os": {
                "server": "linux-srv",
                "workstation": "desktop-os",
                "laptop": "desktop-os",
                "smartphone": "android-like",
                "tablet": "android-like",
                "printer": "printer-fw",
                "camera": "camera-rtsp",
                "iot": "embedded-iot",
                "media_device": "media-os",
                "firewall": "fw-os",
                "switch": "switch-os",
                "access_point": "ap-os",
                "network_appliance": "appliance-os",
                "unknown": None,
                "nas": "nas-os",
            }.get(d.get("device_class_hint")),
            "ssid": d.get("ssid"),
            "ap_id": d.get("ap_id"),
            "switch_id": d.get("switch_id"),
            "port_id": d.get("port_id"),
            "rssi": d.get("rssi"),
            "signal_bucket": d.get("signal_bucket"),
            "connection_type": d.get("connection_type"),
            "tags": d.get("tags") or [],
            "services": [],
        }
        observations.append(obs)

        if d.get("connection_type") == "wireless" and d.get("rssi") is not None:
            wireless_metrics.append(
                {
                    "device_id": d["device_id"],
                    "ap_id": d.get("ap_id"),
                    "ssid": d.get("ssid"),
                    "rssi": d.get("rssi"),
                    "signal_bucket": d.get("signal_bucket"),
                    "band": "5GHz",
                    "channel": 36 + (i % 4) * 4,
                    "note": "Illustrative wireless position — not physical localization",
                    "event_type": "signal_changed",
                    "message": f"Wireless metric for {d['device_id']}",
                }
            )

        if d.get("device_class_hint") in {"smartphone", "tablet", "laptop"} and d.get("ssid"):
            radius_events.append(
                {
                    "event_type": "device_seen",
                    "device_id": d["device_id"],
                    "message": f"Synthetic RADIUS accounting for {d['device_id']}",
                    "identity_alias": f"user-{d['device_id']}",
                    "calling_station": d["mac"],
                    "nas_identifier": d.get("ap_id") or d.get("switch_id"),
                    "ssid": d.get("ssid"),
                    "assigned_segment": d.get("current_segment"),
                    "vlan_recommendation": {
                        "management": 210,
                        "infrastructure": 220,
                        "trusted": 230,
                        "iot": 240,
                        "guest": 250,
                        "quarantine": 260,
                    }.get(d.get("current_segment")),
                    "tunnel_type": "VLAN",
                    "note": "DRY-RUN conceptual attributes only — no secrets",
                    "change_label": "PROPOSED / SIMULATED — NOT APPLIED",
                }
            )

    return (
        devices,
        observations,
        services,
        nodes,
        edges,
        radius_events,
        wireless_metrics,
        policy_events,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic SNSL lab data")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    (
        devices,
        observations,
        services,
        nodes,
        edges,
        radius_events,
        wireless_metrics,
        policy_events,
    ) = build_lab(args.seed)

    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)

    (out / "devices.json").write_text(
        json.dumps(
            {
                "version": "1.0.0",
                "seed": args.seed,
                "note": "SYNTHETIC DEMONSTRATION DATA — documentation IPs only",
                "device_count": len(devices),
                "devices": devices,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "lab-topology.json").write_text(
        json.dumps(
            {
                "version": "1.0.0",
                "seed": args.seed,
                "note": (
                    "The position and edge length are normalized for visualization. "
                    "No physical cable-length estimation is performed."
                ),
                "nodes": nodes,
                "edges": edges,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "services.json").write_text(
        json.dumps(
            {
                "version": "1.0.0",
                "note": "Port maps to category hint only; no product inference.",
                "services": services,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    def write_jsonl(path: Path, rows: list[dict]) -> None:
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, default=str) + "\n")

    write_jsonl(out / "observations.jsonl", observations)
    write_jsonl(out / "radius-events.jsonl", radius_events)
    write_jsonl(out / "wireless-metrics.jsonl", wireless_metrics)
    write_jsonl(out / "policy-events.jsonl", policy_events)

    print(f"Wrote {len(devices)} devices to {out}")
    print("SYNTHETIC DEMONSTRATION DATA — PROPOSED / SIMULATED — NOT APPLIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
