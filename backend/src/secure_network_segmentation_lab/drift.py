"""Segmentation drift detection with severities."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from secure_network_segmentation_lab.enums import DriftSeverity, PolicyDecision
from secure_network_segmentation_lab.models import DriftFinding, utc_now

_PRIVILEGED_CLASSES = {"firewall", "router", "switch", "access_point", "server", "nas"}


def detect_drift(
    devices: list[dict[str, Any]],
    classifications: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    *,
    node_ids: set[str] | None = None,
    edge_device_ids: set[str] | None = None,
) -> list[DriftFinding]:
    findings: list[DriftFinding] = []
    clf = {c["device_id"]: c for c in classifications}
    dec = {d["device_id"]: d for d in decisions}
    now = utc_now()

    def add(
        severity: DriftSeverity,
        category: str,
        summary: str,
        detail: str,
        device_id: str | None = None,
    ) -> None:
        findings.append(
            DriftFinding(
                finding_id=f"drift-{uuid4().hex[:10]}",
                device_id=device_id,
                severity=severity,
                category=category,
                summary=summary,
                detail=detail,
                generated_at_utc=now,
                synthetic=True,
            )
        )

    device_ids = {d["device_id"] for d in devices}

    for device in devices:
        did = device["device_id"]
        segment = device.get("current_segment") or "quarantine"
        c = clf.get(did, {})
        d = dec.get(did, {})
        predicted = c.get("predicted_class") or device.get("device_class_hint")
        confidence = float(c.get("confidence") or 0.0)
        status = c.get("classification_status")

        if status == "unknown" and segment != "quarantine":
            add(
                DriftSeverity.HIGH,
                "unknown_outside_quarantine",
                "Unknown device outside Quarantine",
                f"{did} is unknown but in segment {segment}",
                did,
            )

        if confidence < 0.60 and segment in {"management", "infrastructure", "trusted"}:
            add(
                DriftSeverity.MEDIUM,
                "insufficient_confidence",
                "Insufficient classification confidence for current segment",
                f"{did} confidence={confidence} in {segment}",
                did,
            )

        if predicted in _PRIVILEGED_CLASSES and segment in {"guest", "iot", "quarantine"}:
            if not (predicted in {"unknown"} or segment == "quarantine" and status == "unknown"):
                add(
                    DriftSeverity.HIGH,
                    "privileged_misplaced",
                    "Privileged/infrastructure class in unapproved segment",
                    f"{did} class={predicted} segment={segment}",
                    did,
                )

        if predicted in {"smartphone", "tablet"} and "guest_ssid" in (device.get("tags") or []):
            if segment == "trusted":
                add(
                    DriftSeverity.MEDIUM,
                    "guest_in_trusted",
                    "Guest device in trusted segment",
                    f"{did} has guest_ssid tag but segment={segment}",
                    did,
                )

        if segment == "quarantine" and device.get("metadata", {}).get("excessive_reachability"):
            add(
                DriftSeverity.HIGH,
                "quarantine_reachability",
                "Quarantine device with excessive reachability",
                f"{did} marked with excessive reachability in metadata",
                did,
            )

        decision_val = d.get("decision")
        if decision_val in {
            PolicyDecision.REQUIRE_APPROVAL.value,
            PolicyDecision.RECOMMEND_MOVE.value,
        }:
            if (
                d.get("approval_required")
                and device.get("metadata", {}).get("approval_state") != "approved"
            ):
                if decision_val == PolicyDecision.REQUIRE_APPROVAL.value:
                    add(
                        DriftSeverity.LOW,
                        "approval_missing",
                        "Policy says move but approval missing",
                        f"{did} decision={decision_val} approval_required",
                        did,
                    )

        if device.get("metadata", {}).get("approval_stale"):
            add(
                DriftSeverity.LOW,
                "stale_approval",
                "Stale approval",
                f"{did} has stale approval flag",
                did,
            )

        recommended = d.get("recommended_segment")
        if (
            recommended
            and segment != recommended
            and decision_val == PolicyDecision.RECOMMEND_MOVE.value
        ):
            add(
                DriftSeverity.INFORMATIONAL,
                "unexpected_segment",
                "Device in unexpected segment vs recommendation",
                f"{did} current={segment} recommended={recommended}",
                did,
            )

        # Intentional policy issues / violations
        if device.get("security_state") == "policy_violation":
            add(
                DriftSeverity.HIGH,
                "policy_violation",
                "Policy violation flagged on device",
                f"{did} security_state=policy_violation",
                did,
            )

    if node_ids is not None:
        for nid in node_ids:
            # node_id format node-{device_id}
            did = nid.removeprefix("node-")
            if did not in device_ids:
                add(
                    DriftSeverity.MEDIUM,
                    "orphan_device",
                    "Orphan topology node",
                    f"Node {nid} has no inventory device",
                )

    if edge_device_ids is not None:
        connected = edge_device_ids
        for did in device_ids:
            if did not in connected and not did.startswith("SYNTHETIC-FW"):
                # soft check — many endpoints are connected; skip if intentional offline
                pass

    return findings
