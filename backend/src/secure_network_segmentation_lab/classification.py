"""Deterministic explainable classification — NO machine learning."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from secure_network_segmentation_lab.confidence import (
    clamp_confidence,
    normalize_scores,
    status_for_confidence,
)
from secure_network_segmentation_lab.config import ConfidenceThresholds, load_evidence_weights
from secure_network_segmentation_lab.enums import DeviceClass, Provenance
from secure_network_segmentation_lab.evidence import make_evidence, summarize_evidence
from secure_network_segmentation_lab.models import Classification, Device, EvidenceItem, utc_now

# Hostname / fingerprint → class hints (synthetic patterns only)
_HOSTNAME_HINTS: dict[str, DeviceClass] = {
    "fw": DeviceClass.FIREWALL,
    "firewall": DeviceClass.FIREWALL,
    "sw": DeviceClass.SWITCH,
    "switch": DeviceClass.SWITCH,
    "ap": DeviceClass.ACCESS_POINT,
    "srv": DeviceClass.SERVER,
    "server": DeviceClass.SERVER,
    "ws": DeviceClass.WORKSTATION,
    "pc": DeviceClass.WORKSTATION,
    "laptop": DeviceClass.LAPTOP,
    "phone": DeviceClass.SMARTPHONE,
    "tablet": DeviceClass.TABLET,
    "printer": DeviceClass.PRINTER,
    "prt": DeviceClass.PRINTER,
    "cam": DeviceClass.CAMERA,
    "camera": DeviceClass.CAMERA,
    "nas": DeviceClass.NAS,
    "media": DeviceClass.MEDIA_DEVICE,
    "iot": DeviceClass.IOT,
    "appliance": DeviceClass.NETWORK_APPLIANCE,
}

_SERVICE_HINTS: dict[str, DeviceClass] = {
    "printing": DeviceClass.PRINTER,
    "media": DeviceClass.CAMERA,
    "database": DeviceClass.SERVER,
    "ssh": DeviceClass.SERVER,
    "management": DeviceClass.NETWORK_APPLIANCE,
    "file_service": DeviceClass.NAS,
}

_VENDOR_HINTS: dict[str, list[DeviceClass]] = {
    "synthetic devices ltd.": [
        DeviceClass.WORKSTATION,
        DeviceClass.LAPTOP,
        DeviceClass.SMARTPHONE,
    ],
    "example systems inc.": [DeviceClass.SERVER, DeviceClass.NAS, DeviceClass.NETWORK_APPLIANCE],
    "demo iot corporation": [DeviceClass.IOT, DeviceClass.CAMERA, DeviceClass.MEDIA_DEVICE],
    "sample network hardware": [
        DeviceClass.SWITCH,
        DeviceClass.ACCESS_POINT,
        DeviceClass.FIREWALL,
    ],
    "fictional print works": [DeviceClass.PRINTER],
}


def _hint_from_hostname(hostname: str | None) -> DeviceClass | None:
    if not hostname:
        return None
    lower = hostname.lower()
    for token, klass in _HOSTNAME_HINTS.items():
        if token in lower:
            return klass
    return None


def classify_device(
    device: Device | dict[str, Any],
    *,
    observations: list[dict[str, Any]] | None = None,
    weights: dict[str, float] | None = None,
    thresholds: ConfidenceThresholds | None = None,
) -> Classification:
    """Score device classes from weighted evidence. Classification ≠ VLAN assignment."""
    if isinstance(device, dict):
        device = Device.model_validate(device)
    weights = weights or load_evidence_weights()
    thresholds = thresholds or ConfidenceThresholds()
    observations = observations or []

    class_scores: dict[str, float] = {c.value: 0.0 for c in DeviceClass}
    evidence: list[EvidenceItem] = []

    # Vendor hint
    w_vendor = weights.get("vendor_hint", 0.15)
    vendor = (device.vendor or "").lower()
    if vendor in _VENDOR_HINTS:
        for klass in _VENDOR_HINTS[vendor]:
            class_scores[klass.value] += w_vendor
        evidence.append(
            make_evidence(
                "vendor_hint",
                "Vendor hint",
                w_vendor,
                w_vendor,
                f"Vendor '{device.vendor}' suggests {_VENDOR_HINTS[vendor][0].value}",
                Provenance.SYNTHETIC,
            )
        )

    # Hostname pattern
    w_host = weights.get("hostname_pattern", 0.10)
    host_class = _hint_from_hostname(device.hostname or device.alias)
    if host_class:
        class_scores[host_class.value] += w_host
        evidence.append(
            make_evidence(
                "hostname_pattern",
                "Hostname pattern",
                w_host,
                w_host,
                f"Hostname/alias pattern maps to {host_class.value}",
            )
        )

    # DHCP fingerprint (from latest observation)
    w_dhcp = weights.get("dhcp_fingerprint", 0.20)
    dhcp_fp = None
    for obs in reversed(observations):
        if obs.get("device_id") == device.device_id and obs.get("dhcp_fingerprint"):
            dhcp_fp = obs["dhcp_fingerprint"]
            break
    if dhcp_fp:
        dhcp_class = _hint_from_hostname(str(dhcp_fp))
        if dhcp_class:
            class_scores[dhcp_class.value] += w_dhcp
            evidence.append(
                make_evidence(
                    "dhcp_fingerprint",
                    "DHCP fingerprint",
                    w_dhcp,
                    w_dhcp,
                    f"Synthetic DHCP fingerprint suggests {dhcp_class.value}",
                )
            )

    # Reported OS
    w_os = weights.get("reported_os", 0.15)
    reported_os = None
    for obs in reversed(observations):
        if obs.get("device_id") == device.device_id and obs.get("reported_os"):
            reported_os = str(obs["reported_os"]).lower()
            break
    if reported_os:
        os_class = DeviceClass.UNKNOWN
        if "server" in reported_os or "linux-srv" in reported_os:
            os_class = DeviceClass.SERVER
        elif "windows" in reported_os or "desktop" in reported_os:
            os_class = DeviceClass.WORKSTATION
        elif "android" in reported_os or "ios" in reported_os:
            os_class = DeviceClass.SMARTPHONE
        elif "camera" in reported_os or "rtsp" in reported_os:
            os_class = DeviceClass.CAMERA
        elif "printer" in reported_os:
            os_class = DeviceClass.PRINTER
        elif "embedded" in reported_os or "iot" in reported_os:
            os_class = DeviceClass.IOT
        if os_class != DeviceClass.UNKNOWN:
            class_scores[os_class.value] += w_os
            evidence.append(
                make_evidence(
                    "reported_os",
                    "Reported OS family",
                    w_os,
                    w_os,
                    f"Reported OS '{reported_os}' suggests {os_class.value}",
                )
            )

    # Services
    w_svc = weights.get("services", 0.25)
    service_cats: set[str] = set(device.tags)  # may include guest_ssid etc.
    for obs in observations:
        if obs.get("device_id") == device.device_id:
            for s in obs.get("services") or []:
                service_cats.add(str(s))
    matched_svc = False
    for cat, klass in _SERVICE_HINTS.items():
        if cat in service_cats:
            class_scores[klass.value] += w_svc * 0.5
            matched_svc = True
    if matched_svc:
        evidence.append(
            make_evidence(
                "services",
                "Observed services",
                w_svc,
                w_svc * 0.5,
                f"Service categories {sorted(service_cats & set(_SERVICE_HINTS))} inform class",
            )
        )

    # Historical consistency / device_class_hint
    w_hist = weights.get("historical_consistency", 0.15)
    if device.device_class_hint:
        class_scores[device.device_class_hint.value] += w_hist
        evidence.append(
            make_evidence(
                "historical_consistency",
                "Historical / hint consistency",
                w_hist,
                w_hist,
                f"Prior hint class {device.device_class_hint.value}",
            )
        )

    # Network role from connection infrastructure
    if device.connection_type and device.connection_type.value == "wireless":
        # slight boost toward mobile/iot if no strong signal
        pass

    normalized = normalize_scores(class_scores)
    ranked = sorted(normalized.items(), key=lambda kv: kv[1], reverse=True)
    best_class_name, best_score = ranked[0]
    if best_score <= 0:
        best_class_name = DeviceClass.UNKNOWN.value
        best_score = 0.0

    confidence = clamp_confidence(best_score)
    # If we have almost no evidence, force low confidence
    if not evidence:
        confidence = 0.0
        best_class_name = DeviceClass.UNKNOWN.value

    status = status_for_confidence(confidence, thresholds)
    alternatives = [
        {"class": name, "confidence": round(score, 4)} for name, score in ranked[1:4] if score > 0
    ]

    return Classification(
        device_id=device.device_id,
        predicted_class=DeviceClass(best_class_name),
        confidence=round(confidence, 4),
        alternatives=alternatives,
        evidence=evidence,
        classification_status=status,
        generated_at_utc=utc_now(),
        explanation=summarize_evidence(evidence),
    )


def classify_inventory(
    devices: Sequence[Device | dict[str, Any]],
    observations: list[dict[str, Any]] | None = None,
) -> list[Classification]:
    return [classify_device(d, observations=observations) for d in devices]
