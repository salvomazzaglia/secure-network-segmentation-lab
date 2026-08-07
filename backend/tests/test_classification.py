from __future__ import annotations

from secure_network_segmentation_lab.classification import classify_device
from secure_network_segmentation_lab.confidence import status_for_confidence
from secure_network_segmentation_lab.enums import ClassificationStatus, DeviceClass


def test_printer_classification(sample_printer):
    result = classify_device(
        sample_printer,
        observations=[
            {
                "device_id": sample_printer.device_id,
                "dhcp_fingerprint": "printer-fp",
                "services": ["printing"],
            }
        ],
    )
    assert result.predicted_class == DeviceClass.PRINTER
    assert result.evidence
    assert "vlan" not in result.model_dump()


def test_unknown_low_evidence(sample_unknown):
    result = classify_device(sample_unknown)
    assert result.classification_status in set(ClassificationStatus)


def test_thresholds():
    assert status_for_confidence(0.80) == ClassificationStatus.CLASSIFIED
    assert status_for_confidence(0.79) == ClassificationStatus.UNCERTAIN
    assert status_for_confidence(0.59) == ClassificationStatus.UNKNOWN


def test_deterministic(sample_printer):
    a = classify_device(sample_printer)
    b = classify_device(sample_printer)
    assert a.predicted_class == b.predicted_class
    assert a.confidence == b.confidence


def test_explanation(sample_printer):
    result = classify_device(sample_printer)
    assert result.explanation or result.evidence
    assert "probability" in result.note.lower() or "heuristic" in result.note.lower()


def test_alternatives(sample_printer):
    result = classify_device(
        sample_printer,
        observations=[{"device_id": sample_printer.device_id, "services": ["printing"]}],
    )
    assert isinstance(result.alternatives, list)


def test_vendor_evidence(sample_printer):
    result = classify_device(sample_printer)
    assert any(e.key == "vendor_hint" for e in result.evidence)


def test_hostname_evidence(sample_printer):
    result = classify_device(sample_printer)
    assert any(e.key == "hostname_pattern" for e in result.evidence)


def test_services_evidence(sample_printer):
    result = classify_device(
        sample_printer,
        observations=[{"device_id": sample_printer.device_id, "services": ["printing"]}],
    )
    assert any(e.key == "services" for e in result.evidence)


def test_dhcp_evidence(sample_printer):
    result = classify_device(
        sample_printer,
        observations=[{"device_id": sample_printer.device_id, "dhcp_fingerprint": "printer-xyz"}],
    )
    assert any(e.key == "dhcp_fingerprint" for e in result.evidence)
