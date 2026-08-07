from __future__ import annotations

from secure_network_segmentation_lab.classification import classify_device
from secure_network_segmentation_lab.enums import ClassificationStatus, DeviceClass, PolicyDecision
from secure_network_segmentation_lab.models import Classification
from secure_network_segmentation_lab.policy import evaluate_device_policy


def test_printer_to_iot(sample_printer, printer_classification):
    decision = evaluate_device_policy(sample_printer, printer_classification)
    assert decision.recommended_segment == "iot"
    assert "SIMULATED" in decision.change_label or "NOT APPLIED" in decision.change_label


def test_unknown_to_quarantine(sample_unknown):
    clf = classify_device(sample_unknown)
    # force unknown status profile
    clf = clf.model_copy(
        update={
            "classification_status": ClassificationStatus.UNKNOWN,
            "confidence": 0.2,
            "predicted_class": DeviceClass.UNKNOWN,
        }
    )
    decision = evaluate_device_policy(sample_unknown, clf)
    assert decision.recommended_segment == "quarantine"
    assert decision.approval_required is True


def test_server_requires_approval(sample_printer):
    sample_printer = sample_printer.model_copy(
        update={
            "device_class_hint": DeviceClass.SERVER,
            "hostname": "server-99.lab.example.invalid",
            "vendor": "Example Systems Inc.",
        }
    )
    clf = classify_device(sample_printer)
    clf = clf.model_copy(
        update={
            "predicted_class": DeviceClass.SERVER,
            "confidence": 0.95,
            "classification_status": ClassificationStatus.CLASSIFIED,
        }
    )
    decision = evaluate_device_policy(sample_printer, clf)
    assert decision.recommended_segment == "infrastructure"
    assert decision.approval_required is True


def test_guest_keep(sample_printer):
    sample_printer = sample_printer.model_copy(
        update={
            "device_class_hint": DeviceClass.SMARTPHONE,
            "tags": ["guest_ssid"],
            "current_segment": "guest",
            "hostname": "phone-99.lab.example.invalid",
        }
    )
    clf = Classification(
        device_id=sample_printer.device_id,
        predicted_class=DeviceClass.SMARTPHONE,
        confidence=0.85,
        classification_status=ClassificationStatus.CLASSIFIED,
        evidence=[],
    )
    decision = evaluate_device_policy(sample_printer, clf)
    assert decision.recommended_segment == "guest"


def test_low_confidence_quarantine(sample_unknown):
    clf = Classification(
        device_id=sample_unknown.device_id,
        predicted_class=DeviceClass.UNKNOWN,
        confidence=0.4,
        classification_status=ClassificationStatus.UNKNOWN,
        evidence=[],
    )
    decision = evaluate_device_policy(sample_unknown, clf)
    assert decision.decision in {PolicyDecision.QUARANTINE, PolicyDecision.REQUIRE_APPROVAL}
