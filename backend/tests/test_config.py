from __future__ import annotations

import pytest

from secure_network_segmentation_lab.config import (
    load_app_config,
    load_device_classes,
    load_evidence_weights,
    load_reachability_policy,
    load_segmentation_policy,
    load_segments,
)
from secure_network_segmentation_lab.policy_validation import (
    validate_reachability_policy,
    validate_segmentation_policy,
)


def test_valid_default_config():
    cfg = load_app_config()
    assert cfg.bind_host == "127.0.0.1"


def test_demo_config():
    cfg = load_app_config("demo.config.json")
    assert cfg.source_mode.value == "synthetic"


def test_segments_six():
    segs = load_segments()["segments"]
    assert len(segs) == 6
    assert {s["vlan_id"] for s in segs} == {210, 220, 230, 240, 250, 260}


def test_vlan_note_synthetic():
    for s in load_segments()["segments"]:
        assert "SYNTHETIC VLAN ID" in s["vlan_note"]


def test_device_classes():
    classes = load_device_classes()
    assert "unknown" in classes and "printer" in classes


def test_evidence_weights_sum():
    assert abs(sum(load_evidence_weights().values()) - 1.0) < 0.05


def test_segmentation_policy_valid():
    validate_segmentation_policy(load_segmentation_policy())


def test_reachability_policy_valid():
    validate_reachability_policy(load_reachability_policy())


def test_implicit_default_permit_rejected():
    policy = dict(load_segmentation_policy())
    policy["implicit_default_permit"] = True
    with pytest.raises(Exception):
        validate_segmentation_policy(policy)


def test_duplicate_rule_id_rejected():
    policy = dict(load_segmentation_policy())
    rules = list(policy["rules"])
    rules.append(dict(rules[0]))
    policy["rules"] = rules
    with pytest.raises(Exception):
        validate_segmentation_policy(policy)


def test_unknown_segment_rejected():
    policy = {
        "version": "1.0.0",
        "implicit_default_permit": False,
        "default_decision": "no_match",
        "rules": [
            {
                "id": "SNSL-SEG-999",
                "precedence": 1,
                "description": "x",
                "match": {"device_class": "printer"},
                "recommend_segment": "not-a-segment",
                "decision": "recommend_move",
                "approval": {"required": False},
            }
        ],
    }
    with pytest.raises(Exception):
        validate_segmentation_policy(policy)


def test_unknown_class_rejected():
    policy = {
        "version": "1.0.0",
        "implicit_default_permit": False,
        "default_decision": "no_match",
        "rules": [
            {
                "id": "SNSL-SEG-998",
                "precedence": 1,
                "description": "x",
                "match": {"device_class": "toaster"},
                "recommend_segment": "iot",
                "decision": "recommend_move",
                "approval": {"required": False},
            }
        ],
    }
    with pytest.raises(Exception):
        validate_segmentation_policy(policy)


def test_invalid_confidence_rejected():
    policy = {
        "version": "1.0.0",
        "implicit_default_permit": False,
        "default_decision": "no_match",
        "rules": [
            {
                "id": "SNSL-SEG-997",
                "precedence": 1,
                "description": "x",
                "match": {"device_class": "printer", "confidence_minimum": 1.5},
                "recommend_segment": "iot",
                "decision": "recommend_move",
                "approval": {"required": False},
            }
        ],
    }
    with pytest.raises(Exception):
        validate_segmentation_policy(policy)


def test_forbidden_eval_rejected():
    policy = {
        "version": "1.0.0",
        "implicit_default_permit": False,
        "default_decision": "no_match",
        "rules": [
            {
                "id": "SNSL-SEG-996",
                "precedence": 1,
                "description": "x",
                "match": {},
                "recommend_segment": "iot",
                "decision": "recommend_move",
                "approval": {"required": False},
                "eval": "1+1",
            }
        ],
    }
    with pytest.raises(Exception):
        validate_segmentation_policy(policy)
