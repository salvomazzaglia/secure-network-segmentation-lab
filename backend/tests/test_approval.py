from __future__ import annotations

import pytest

from secure_network_segmentation_lab.approval import ApprovalError, record_approval
from secure_network_segmentation_lab.enums import ApprovalDecision, SourceMode


def test_approve(sample_unknown):
    record, updated = record_approval(
        sample_unknown,
        ApprovalDecision.APPROVE,
        recommended_segment="iot",
        justification="synthetic review",
        synthetic=True,
        source_mode=SourceMode.SYNTHETIC,
    )
    assert record.synthetic is True
    assert updated.current_segment == "iot"
    assert record.operator_label == "SYNTHETIC-OPERATOR"


def test_reject(sample_unknown):
    _, updated = record_approval(
        sample_unknown, ApprovalDecision.REJECT, recommended_segment="iot", justification="no"
    )
    assert updated.current_segment == sample_unknown.current_segment


def test_keep_quarantined(sample_unknown):
    _, updated = record_approval(
        sample_unknown,
        ApprovalDecision.KEEP_QUARANTINED,
        recommended_segment="iot",
        justification="still unknown",
    )
    assert updated.current_segment == "quarantine"


def test_alternate(sample_unknown):
    _, updated = record_approval(
        sample_unknown,
        ApprovalDecision.CHOOSE_ALTERNATE_SEGMENT,
        recommended_segment="iot",
        chosen_segment="guest",
        justification="guest",
    )
    assert updated.current_segment == "guest"


def test_imported_refused(sample_unknown):
    with pytest.raises(ApprovalError):
        record_approval(
            sample_unknown,
            ApprovalDecision.APPROVE,
            recommended_segment="iot",
            justification="x",
            source_mode=SourceMode.IMPORTED,
        )


def test_synthetic_required(sample_unknown):
    with pytest.raises(ApprovalError):
        record_approval(
            sample_unknown,
            ApprovalDecision.APPROVE,
            recommended_segment="iot",
            justification="x",
            synthetic=False,
        )
