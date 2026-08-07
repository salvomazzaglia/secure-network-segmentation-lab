from __future__ import annotations

import json

import pytest

from secure_network_segmentation_lab.classification import classify_device
from secure_network_segmentation_lab.enums import (
    ClassificationStatus,
    DeviceClass,
    PolicyDecision,
    ReachabilityDecision,
    SignalBucket,
)
from secure_network_segmentation_lab.inventory import device_from_dict
from secure_network_segmentation_lab.paths import synthetic_dir
from secure_network_segmentation_lab.policy import evaluate_device_policy
from secure_network_segmentation_lab.reachability import evaluate_reachability
from secure_network_segmentation_lab.simulator import simulate_step
from secure_network_segmentation_lab.wireless import illustrative_placement


def _load_devices():
    data = json.loads((synthetic_dir() / "devices.json").read_text(encoding="utf-8"))
    return [device_from_dict(d) for d in data["devices"]]


DEVICES = _load_devices()
DEVICE_IDS = [d.device_id for d in DEVICES]


@pytest.mark.parametrize("device_id", DEVICE_IDS)
def test_each_device_classifies(device_id):
    device = next(d for d in DEVICES if d.device_id == device_id)
    result = classify_device(device)
    assert result.device_id == device_id
    assert 0.0 <= result.confidence <= 1.0
    assert result.classification_status in set(ClassificationStatus)
    assert "vlan" not in result.model_dump()


@pytest.mark.parametrize("device_id", DEVICE_IDS[:20])
def test_each_device_policy(device_id):
    device = next(d for d in DEVICES if d.device_id == device_id)
    clf = classify_device(device)
    decision = evaluate_device_policy(device, clf)
    assert decision.device_id == device_id
    assert decision.decision in set(PolicyDecision)
    assert "NOT APPLIED" in decision.change_label or "SIMULATED" in decision.change_label


@pytest.mark.parametrize(
    "scenario", ["normal", "new-device", "quarantine", "roaming", "policy-drift", "mixed"]
)
def test_scenarios(bootstrapped_db, scenario):
    events = simulate_step(bootstrapped_db, scenario=scenario, seed=99)
    assert isinstance(events, list)


@pytest.mark.parametrize(
    "source,destination,service",
    [
        ("trusted", "management", "ssh"),
        ("trusted", "infrastructure", "management"),
        ("iot", "guest", "ssh"),
        ("guest", "iot", "printing"),
        ("management", "guest", "ssh"),
        ("infrastructure", "quarantine", "ssh"),
        ("quarantine", "guest", "ssh"),
        ("iot", "internet", "secure_web"),
        ("guest", "internet", "dns"),
        ("trusted", "iot", "media"),
    ],
)
def test_more_reachability(source, destination, service):
    r = evaluate_reachability(source, destination, service)
    assert r.decision in set(ReachabilityDecision)
    assert r.explanation


@pytest.mark.parametrize("bucket", list(SignalBucket))
def test_all_signal_buckets_place(bucket):
    pos = illustrative_placement("SYNTHETIC-PLACE-01", bucket)
    assert pos["meters"] is None
    assert pos["distance_claim"] is None


@pytest.mark.parametrize("klass", list(DeviceClass))
def test_device_class_enum_roundtrip(klass):
    assert DeviceClass(klass.value) is klass
