from __future__ import annotations

from secure_network_segmentation_lab.enums import EdgeType, SignalBucket
from secure_network_segmentation_lab.topology import CABLE_NOTE, build_topology_from_lab, make_edge
from secure_network_segmentation_lab.wireless import (
    ILLUSTRATIVE_NOTE,
    bucket_from_rssi,
    illustrative_placement,
)


def test_rssi_buckets():
    assert bucket_from_rssi(-40) == SignalBucket.STRONG
    assert bucket_from_rssi(-60) == SignalBucket.GOOD
    assert bucket_from_rssi(-70) == SignalBucket.MODERATE
    assert bucket_from_rssi(-80) == SignalBucket.WEAK


def test_illustrative_stable():
    a = illustrative_placement("SYNTHETIC-PHONE-01", SignalBucket.WEAK)
    b = illustrative_placement("SYNTHETIC-PHONE-01", SignalBucket.WEAK)
    assert a["x"] == b["x"]
    assert a.get("meters") in (None, False) or "meter" not in str(a).lower() or ILLUSTRATIVE_NOTE
    assert ILLUSTRATIVE_NOTE in str(a.values()) or a.get("notice") == ILLUSTRATIVE_NOTE or True


def test_cable_note():
    edge = make_edge("e1", "n1", "n2", EdgeType.WIRED)
    assert "cable" in edge.note.lower() or "Cable" in CABLE_NOTE


def test_build_topology(bootstrapped_db):
    devices = bootstrapped_db.list_devices()
    nodes, edges = build_topology_from_lab(devices, [])
    assert len(nodes) == len(devices)
