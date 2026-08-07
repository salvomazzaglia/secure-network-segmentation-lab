"""Declarative segmentation policy engine. Classification ≠ VLAN assignment."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from secure_network_segmentation_lab.config import (
    load_segmentation_policy_raw,
    validate_policy_structure,
)
from secure_network_segmentation_lab.enums import PolicyDecision
from secure_network_segmentation_lab.models import (
    Classification,
    Device,
    PolicyDecisionResult,
    utc_now,
)
from secure_network_segmentation_lab.policy_validation import validate_segmentation_policy


def load_segmentation_policy() -> dict[str, Any]:
    raw = load_segmentation_policy_raw()
    validate_policy_structure(raw, "segmentation")
    validate_segmentation_policy(raw)
    return raw


def _match_rule(rule: dict[str, Any], profile: dict[str, Any]) -> bool:
    match = rule.get("match") or {}
    if "device_class" in match and profile.get("device_class") != match["device_class"]:
        return False
    if (
        "classification_status" in match
        and profile.get("classification_status") != match["classification_status"]
    ):
        return False
    if "confidence_minimum" in match:
        conf = profile.get("confidence")
        if conf is None or float(conf) < float(match["confidence_minimum"]):
            return False
    if "confidence_maximum" in match:
        conf = profile.get("confidence")
        if conf is None or float(conf) > float(match["confidence_maximum"]):
            return False
    if "connection_type" in match and profile.get("connection_type") != match["connection_type"]:
        return False
    if "ownership_label" in match and profile.get("ownership_label") != match["ownership_label"]:
        return False
    if "approval_state" in match and profile.get("approval_state") != match["approval_state"]:
        return False
    if "security_state" in match and profile.get("security_state") != match["security_state"]:
        return False
    if "source_segment" in match and profile.get("current_segment") != match["source_segment"]:
        return False
    if "destination_segment" in match:
        # destination checked against recommended context if provided
        if profile.get("destination_segment") != match["destination_segment"]:
            return False
    if "tags" in match:
        required = set(match["tags"] or [])
        have = set(profile.get("tags") or [])
        if not required.issubset(have):
            return False
    return True


def build_device_profile(
    device: Device | dict[str, Any],
    classification: Classification | dict[str, Any] | None = None,
    *,
    destination_segment: str | None = None,
) -> dict[str, Any]:
    if isinstance(device, dict):
        device = Device.model_validate(device)
    clf: dict[str, Any] = {}
    if classification is not None:
        clf = (
            classification.model_dump(mode="json")
            if isinstance(classification, Classification)
            else classification
        )
    return {
        "device_id": device.device_id,
        "device_class": clf.get("predicted_class")
        or (device.device_class_hint.value if device.device_class_hint else None),
        "classification_status": clf.get("classification_status"),
        "confidence": clf.get("confidence"),
        "connection_type": device.connection_type.value if device.connection_type else None,
        "ownership_label": device.ownership_label,
        "security_state": device.security_state.value if device.security_state else None,
        "current_segment": device.current_segment,
        "destination_segment": destination_segment,
        "tags": list(device.tags),
        "approval_state": device.metadata.get("approval_state") if device.metadata else None,
    }


def evaluate_device_policy(
    device: Device | dict[str, Any],
    classification: Classification | dict[str, Any] | None = None,
    *,
    policy: dict[str, Any] | None = None,
    destination_segment: str | None = None,
) -> PolicyDecisionResult:
    policy = policy or load_segmentation_policy()
    profile = build_device_profile(device, classification, destination_segment=destination_segment)
    if isinstance(device, dict):
        device = Device.model_validate(device)

    rules = sorted(policy.get("rules", []), key=lambda r: int(r.get("precedence", 9999)))
    for rule in rules:
        if _match_rule(rule, profile):
            approval = rule.get("approval") or {}
            decision = PolicyDecision(rule["decision"])
            return PolicyDecisionResult(
                policy_id=rule["id"],
                matched_rule=rule["id"],
                device_id=device.device_id,
                current_segment=device.current_segment,
                recommended_segment=rule.get("recommend_segment"),
                decision=decision,
                approval_required=bool(approval.get("required", False)),
                reason=rule.get("description", ""),
                confidence=profile.get("confidence"),
                policy_version=str(policy.get("version", "1.0.0")),
                generated_at_utc=utc_now(),
            )

    default = PolicyDecision(policy.get("default_decision", "no_match"))
    return PolicyDecisionResult(
        policy_id="SNSL-SEG-NONE",
        matched_rule=None,
        device_id=device.device_id,
        current_segment=device.current_segment,
        recommended_segment=None,
        decision=default,
        approval_required=False,
        reason="No segmentation policy rule matched",
        confidence=profile.get("confidence"),
        policy_version=str(policy.get("version", "1.0.0")),
        generated_at_utc=utc_now(),
    )


def evaluate_all(
    devices: Sequence[Device | dict[str, Any]],
    classifications: Sequence[Classification | dict[str, Any]],
    *,
    policy: dict[str, Any] | None = None,
) -> list[PolicyDecisionResult]:
    policy = policy or load_segmentation_policy()
    by_id: dict[str, Classification | dict[str, Any]] = {}
    for c in classifications:
        if isinstance(c, Classification):
            by_id[c.device_id] = c
        else:
            by_id[str(c["device_id"])] = c
    results: list[PolicyDecisionResult] = []
    for device in devices:
        did = device.device_id if isinstance(device, Device) else device["device_id"]
        results.append(evaluate_device_policy(device, by_id.get(did), policy=policy))
    return results
