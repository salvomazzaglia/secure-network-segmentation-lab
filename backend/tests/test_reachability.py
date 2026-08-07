from __future__ import annotations

from secure_network_segmentation_lab.enums import ReachabilityDecision
from secure_network_segmentation_lab.reachability import evaluate_reachability


def test_guest_management_denied():
    r = evaluate_reachability("guest", "management", "ssh")
    assert r.decision == ReachabilityDecision.DENIED


def test_iot_dns_allowed():
    r = evaluate_reachability("iot", "infrastructure", "dns")
    assert r.decision == ReachabilityDecision.ALLOWED


def test_quarantine_trusted_denied():
    r = evaluate_reachability("quarantine", "trusted", "ssh")
    assert r.decision == ReachabilityDecision.DENIED


def test_quarantine_dns_allowed():
    r = evaluate_reachability("quarantine", "infrastructure", "dns")
    assert r.decision == ReachabilityDecision.ALLOWED


def test_trusted_internet_allowed():
    r = evaluate_reachability("trusted", "internet", "secure_web")
    assert r.decision == ReachabilityDecision.ALLOWED


def test_management_infra_allowed():
    r = evaluate_reachability("management", "infrastructure", "management")
    assert r.decision == ReachabilityDecision.ALLOWED


def test_no_implicit_permit():
    r = evaluate_reachability("guest", "iot", "database")
    assert r.decision == ReachabilityDecision.DENIED


def test_explanation():
    r = evaluate_reachability("iot", "management", "any")
    assert r.explanation


def test_conditional_quarantine_web():
    r = evaluate_reachability("quarantine", "internet", "secure_web")
    assert r.decision == ReachabilityDecision.CONDITIONAL


def test_guest_ssh_denied():
    r = evaluate_reachability("guest", "internet", "ssh")
    assert r.decision == ReachabilityDecision.DENIED
