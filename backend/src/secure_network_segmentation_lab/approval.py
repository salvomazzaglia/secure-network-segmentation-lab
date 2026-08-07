"""Synthetic approval workflow — NO network action."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from secure_network_segmentation_lab.enums import ApprovalDecision, SecurityState, SourceMode
from secure_network_segmentation_lab.models import Approval, Device, utc_now

OPERATOR_LABEL = "SYNTHETIC-OPERATOR"
APPROVAL_NOTE = "SIMULATED APPROVAL — NO NETWORK CHANGE APPLIED"
CHANGE_LABEL = "PROPOSED / SIMULATED — NOT APPLIED"


class ApprovalError(ValueError):
    pass


def record_approval(
    device: Device | dict[str, Any],
    decision: ApprovalDecision | str,
    *,
    source_mode: SourceMode | str = SourceMode.SYNTHETIC,
    synthetic: bool = True,
    recommended_segment: str | None = None,
    chosen_segment: str | None = None,
    policy_id: str | None = None,
    justification: str = "",
    operator_label: str = OPERATOR_LABEL,
) -> tuple[Approval, Device]:
    """Approve/reject/keep_quarantined/choose_alternate_segment — simulated only."""
    if isinstance(device, dict):
        device = Device.model_validate(device)
    if isinstance(decision, str):
        decision = ApprovalDecision(decision)
    if isinstance(source_mode, str):
        source_mode = SourceMode(source_mode)

    if not synthetic:
        raise ApprovalError("synthetic=true is required for approval mutations in v1.0")
    if source_mode != SourceMode.SYNTHETIC:
        raise ApprovalError("Approvals rejected when source_mode != synthetic")
    if operator_label != OPERATOR_LABEL:
        # Force synthetic operator for fixture consistency
        operator_label = OPERATOR_LABEL

    previous = device.current_segment
    recommended = recommended_segment or device.recommended_segment
    data = device.model_dump()
    data["metadata"] = {
        **(data.get("metadata") or {}),
        "change_label": CHANGE_LABEL,
        "network_applied": False,
        "approval_note": APPROVAL_NOTE,
    }

    if decision == ApprovalDecision.APPROVE:
        target = chosen_segment or recommended or previous
        data["current_segment"] = target
        data["recommended_segment"] = recommended
        data["security_state"] = (
            SecurityState.QUARANTINED if target == "quarantine" else SecurityState.APPROVED
        )
        chosen = target
    elif decision == ApprovalDecision.REJECT:
        chosen = previous
        data["security_state"] = SecurityState.RESTRICTED
        data["metadata"]["approval_state"] = "rejected"
    elif decision == ApprovalDecision.KEEP_QUARANTINED:
        data["current_segment"] = "quarantine"
        data["security_state"] = SecurityState.QUARANTINED
        chosen = "quarantine"
    elif decision == ApprovalDecision.CHOOSE_ALTERNATE_SEGMENT:
        if not chosen_segment:
            raise ApprovalError("choose_alternate_segment requires chosen_segment")
        data["current_segment"] = chosen_segment
        data["recommended_segment"] = recommended
        data["security_state"] = (
            SecurityState.QUARANTINED if chosen_segment == "quarantine" else SecurityState.APPROVED
        )
        chosen = chosen_segment
    else:
        raise ApprovalError(f"Unsupported approval decision: {decision}")

    approval = Approval(
        approval_id=f"apr-{uuid4().hex[:12]}",
        device_id=device.device_id,
        previous_segment=previous,
        recommended_segment=recommended,
        chosen_segment=chosen,
        decision=decision,
        operator_label=operator_label,
        justification=justification or "Synthetic lab approval",
        created_at_utc=utc_now(),
        policy_id=policy_id,
        synthetic=True,
        change_label=CHANGE_LABEL,
        note=APPROVAL_NOTE,
    )
    return approval, Device.model_validate(data)
