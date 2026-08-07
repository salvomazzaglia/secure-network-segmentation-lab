"""Segment helpers — recommended segment applied to simulated state only."""

from __future__ import annotations

from typing import Any

from secure_network_segmentation_lab.config import load_segments
from secure_network_segmentation_lab.enums import SecurityState
from secure_network_segmentation_lab.models import Device, PolicyDecisionResult, Segment


def get_segments() -> list[Segment]:
    raw = load_segments()
    return [Segment.model_validate(s) for s in raw.get("segments", [])]


def segment_by_id(segment_id: str) -> Segment | None:
    for seg in get_segments():
        if seg.segment_id == segment_id:
            return seg
    return None


def apply_recommended_segment_simulated(
    device: Device | dict[str, Any],
    decision: PolicyDecisionResult | dict[str, Any],
) -> Device:
    """Update simulated device state with recommended segment.

    Label: PROPOSED / SIMULATED — NOT APPLIED. No network action.
    """
    if isinstance(device, dict):
        device = Device.model_validate(device)
    if isinstance(decision, dict):
        decision = PolicyDecisionResult.model_validate(decision)

    data = device.model_dump()
    recommended = decision.recommended_segment
    data["recommended_segment"] = recommended
    data["metadata"] = {
        **(data.get("metadata") or {}),
        "last_policy_id": decision.policy_id,
        "change_label": "PROPOSED / SIMULATED — NOT APPLIED",
        "network_applied": False,
    }

    # Simulated state updates — proposed/simulated only (no network action).
    # Quarantine with approval required stays on current segment until synthetic approval.
    if decision.decision.value == "quarantine" and recommended:
        if decision.approval_required:
            data["security_state"] = SecurityState.PENDING_APPROVAL
            data["metadata"]["approval_state"] = "required"
            data["metadata"]["proposed_segment"] = recommended
        else:
            data["current_segment"] = recommended
            data["security_state"] = SecurityState.QUARANTINED
    elif decision.decision.value == "keep" and recommended:
        data["current_segment"] = recommended
        if recommended == "quarantine":
            data["security_state"] = SecurityState.QUARANTINED
        else:
            data["security_state"] = SecurityState.APPROVED
    elif decision.approval_required:
        data["security_state"] = SecurityState.PENDING_APPROVAL
        data["metadata"]["approval_state"] = "required"
    elif (
        decision.decision.value == "recommend_move"
        and recommended
        and not decision.approval_required
    ):
        # Simulated auto-apply for non-approval recommend_move in lab only
        data["current_segment"] = recommended
        data["security_state"] = SecurityState.APPROVED
        data["metadata"]["simulated_move"] = True

    data["metadata"]["note"] = "PROPOSED / SIMULATED — NOT APPLIED"
    return Device.model_validate(data)


def vlan_note(segment_id: str) -> str:
    seg = segment_by_id(segment_id)
    if seg:
        return f"{seg.vlan_note} (VLAN {seg.vlan_id})"
    return "SYNTHETIC VLAN ID — EXAMPLE ONLY"
