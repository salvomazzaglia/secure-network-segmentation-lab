"""Wireless signal buckets and illustrative radial placement — NEVER meters."""

from __future__ import annotations

import hashlib
from typing import Any

from secure_network_segmentation_lab.enums import SignalBucket

# Illustrative radial units for visualization only — NOT physical meters.
_BUCKET_RADIUS: dict[SignalBucket, float] = {
    SignalBucket.STRONG: 0.25,
    SignalBucket.GOOD: 0.45,
    SignalBucket.MODERATE: 0.65,
    SignalBucket.WEAK: 0.85,
}

ILLUSTRATIVE_NOTE = "Illustrative wireless position — not physical localization"


def bucket_from_rssi(rssi: int) -> SignalBucket:
    """Map synthetic RSSI (dBm-like integer) to quality bucket. No distance claim."""
    if rssi >= -55:
        return SignalBucket.STRONG
    if rssi >= -65:
        return SignalBucket.GOOD
    if rssi >= -75:
        return SignalBucket.MODERATE
    return SignalBucket.WEAK


def illustrative_placement(
    device_id: str,
    signal_bucket: SignalBucket | str,
    *,
    ap_x: float = 0.0,
    ap_y: float = 0.0,
    ap_z: float = 1.0,
) -> dict[str, Any]:
    """Deterministic angular placement from device hash; radial from signal bucket.

    NEVER converts RSSI to meters. Positions are visualization-only units.
    """
    if isinstance(signal_bucket, str):
        signal_bucket = SignalBucket(signal_bucket)
    digest = hashlib.sha256(device_id.encode("utf-8")).hexdigest()
    angle = (int(digest[:8], 16) % 36000) / 100.0  # degrees
    import math

    rad = math.radians(angle)
    radius = _BUCKET_RADIUS[signal_bucket]
    x = ap_x + radius * math.cos(rad)
    y = ap_y + radius * math.sin(rad)
    z = ap_z
    return {
        "x": round(x, 4),
        "y": round(y, 4),
        "z": round(z, 4),
        "angle_degrees": angle,
        "illustrative_radius": radius,
        "signal_bucket": signal_bucket.value,
        "note": ILLUSTRATIVE_NOTE,
        "distance_claim": None,
        "meters": None,
    }


def wireless_client_record(
    device_id: str,
    ap_id: str,
    ssid: str,
    rssi: int,
    *,
    band: str = "5GHz",
    channel: int = 36,
) -> dict[str, Any]:
    bucket = bucket_from_rssi(rssi)
    placement = illustrative_placement(device_id, bucket)
    return {
        "device_id": device_id,
        "ap_id": ap_id,
        "ssid": ssid,
        "band": band,
        "channel": channel,
        "rssi": rssi,
        "signal_bucket": bucket.value,
        "placement": placement,
        "note": ILLUSTRATIVE_NOTE,
    }
