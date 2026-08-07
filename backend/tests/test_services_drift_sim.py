from __future__ import annotations

from secure_network_segmentation_lab.drift import detect_drift
from secure_network_segmentation_lab.enums import Provenance, ServiceCategory
from secure_network_segmentation_lab.services import category_for_port, make_service_observation
from secure_network_segmentation_lab.simulator import simulate_run, simulate_step


def test_port_category():
    assert category_for_port(443) == ServiceCategory.SECURE_WEB
    assert category_for_port(9100) == ServiceCategory.PRINTING


def test_service_observed():
    svc = make_service_observation("d1", port=443, protocol="tcp", provenance=Provenance.OBSERVED)
    assert svc.provenance == Provenance.OBSERVED
    assert "product inference" in (svc.note or "").lower() or "category" in (svc.detail or "")


def test_drift_runs(bootstrapped_db):
    devices = bootstrapped_db.list_devices()
    decisions = bootstrapped_db.list_policy_decisions()
    classifications = bootstrapped_db.list_classifications()
    findings = detect_drift(devices, classifications, decisions)
    assert isinstance(findings, list)


def test_simulate_step(bootstrapped_db):
    events = simulate_step(bootstrapped_db, scenario="mixed", seed=42)
    assert events


def test_simulate_run(bootstrapped_db):
    events = simulate_run(bootstrapped_db, scenario="mixed", seed=42, duration_steps=3)
    assert len(events) >= 1
