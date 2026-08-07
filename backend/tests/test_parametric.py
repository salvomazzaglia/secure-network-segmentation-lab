from __future__ import annotations

import pytest

from secure_network_segmentation_lab.adapters import PLANS, get_adapter_plan
from secure_network_segmentation_lab.confidence import status_for_confidence
from secure_network_segmentation_lab.enums import (
    ClassificationStatus,
    ReachabilityDecision,
    SignalBucket,
)
from secure_network_segmentation_lab.reachability import evaluate_reachability
from secure_network_segmentation_lab.segmentation import get_segments
from secure_network_segmentation_lab.services import category_for_port
from secure_network_segmentation_lab.wireless import bucket_from_rssi, illustrative_placement

SEGMENTS = ["management", "infrastructure", "trusted", "iot", "guest", "quarantine"]


@pytest.mark.parametrize(
    "conf,expected",
    [
        (1.0, ClassificationStatus.CLASSIFIED),
        (0.8, ClassificationStatus.CLASSIFIED),
        (0.799, ClassificationStatus.UNCERTAIN),
        (0.6, ClassificationStatus.UNCERTAIN),
        (0.599, ClassificationStatus.UNKNOWN),
        (0.0, ClassificationStatus.UNKNOWN),
    ],
)
def test_confidence_thresholds(conf, expected):
    assert status_for_confidence(conf) == expected


@pytest.mark.parametrize(
    "rssi,bucket",
    [
        (-40, SignalBucket.STRONG),
        (-55, SignalBucket.STRONG),
        (-56, SignalBucket.GOOD),
        (-65, SignalBucket.GOOD),
        (-66, SignalBucket.MODERATE),
        (-75, SignalBucket.MODERATE),
        (-76, SignalBucket.WEAK),
        (-90, SignalBucket.WEAK),
    ],
)
def test_rssi_boundaries(rssi, bucket):
    assert bucket_from_rssi(rssi) == bucket


@pytest.mark.parametrize(
    "port,cat",
    [
        (80, "web"),
        (443, "secure_web"),
        (22, "ssh"),
        (53, "dns"),
        (123, "ntp"),
        (67, "dhcp"),
        (9100, "printing"),
        (445, "file_service"),
        (554, "media"),
        (3306, "database"),
        (9999, "unknown"),
    ],
)
def test_ports(port, cat):
    assert category_for_port(port).value == cat


@pytest.mark.parametrize("adapter", sorted(PLANS))
def test_adapters(adapter):
    plan = get_adapter_plan(adapter)
    assert plan.connects is False and plan.mutates is False and plan.steps


@pytest.mark.parametrize("destination", ["management", "trusted", "infrastructure", "iot"])
def test_quarantine_denied(destination):
    r = evaluate_reachability("quarantine", destination, "ssh")
    assert r.decision == ReachabilityDecision.DENIED


@pytest.mark.parametrize(
    "source,destination,service,ok",
    [
        ("guest", "management", "any", False),
        ("guest", "infrastructure", "any", False),
        ("guest", "trusted", "any", False),
        ("iot", "management", "any", False),
        ("trusted", "internet", "secure_web", True),
        ("management", "infrastructure", "any", True),
        ("trusted", "iot", "printing", True),
        ("quarantine", "quarantine", "any", False),
        ("infrastructure", "infrastructure", "ssh", True),
        ("guest", "internet", "secure_web", True),
        ("iot", "infrastructure", "ntp", True),
        ("quarantine", "infrastructure", "dns", True),
        ("quarantine", "infrastructure", "ntp", True),
        ("quarantine", "infrastructure", "dhcp", True),
    ],
)
def test_reach_cases(source, destination, service, ok):
    r = evaluate_reachability(source, destination, service)
    if ok:
        assert r.decision == ReachabilityDecision.ALLOWED
    else:
        assert r.decision in {ReachabilityDecision.DENIED, ReachabilityDecision.CONDITIONAL}


@pytest.mark.parametrize("device_id", [f"SYNTHETIC-DEV-{i}" for i in range(25)])
def test_illustrative_positions(device_id):
    pos = illustrative_placement(device_id, SignalBucket.GOOD)
    assert pos["meters"] is None
    assert "Illustrative" in pos["note"]


@pytest.mark.parametrize("segment_id", SEGMENTS)
def test_segments(segment_id):
    assert segment_id in {s.segment_id for s in get_segments()}


@pytest.mark.parametrize("vlan", [210, 220, 230, 240, 250, 260])
def test_vlans(vlan):
    assert vlan in {s.vlan_id for s in get_segments()}
