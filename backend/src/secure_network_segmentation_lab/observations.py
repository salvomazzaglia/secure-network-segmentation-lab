"""Observation normalization with explicit provenance."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from secure_network_segmentation_lab.enums import ConnectionType, Provenance, SignalBucket
from secure_network_segmentation_lab.models import Observation, utc_now
from secure_network_segmentation_lab.wireless import bucket_from_rssi


def normalize_observation(
    raw: dict[str, Any],
    *,
    default_provenance: Provenance | None = None,
) -> Observation:
    """Normalize a raw observation dict into an Observation model."""
    data = dict(raw)
    data.setdefault("observation_id", data.get("id") or f"obs-{uuid4().hex[:12]}")
    if "device_id" not in data:
        raise ValueError("observation requires device_id")

    # Accept alternate timestamp keys from other generators
    if "observed_at_utc" not in data:
        if "observed_at" in data:
            data["observed_at_utc"] = data.pop("observed_at")
        else:
            data["observed_at_utc"] = utc_now()

    prov = data.get("provenance") or default_provenance or Provenance.SYNTHETIC
    if isinstance(prov, str):
        prov = Provenance(prov)
    data["provenance"] = prov

    if data.get("rssi") is not None and not data.get("signal_bucket"):
        data["signal_bucket"] = bucket_from_rssi(int(data["rssi"]))

    if data.get("connection_type") and isinstance(data["connection_type"], str):
        data["connection_type"] = ConnectionType(data["connection_type"])

    if data.get("signal_bucket") and isinstance(data["signal_bucket"], str):
        data["signal_bucket"] = SignalBucket(data["signal_bucket"])

    data.setdefault(
        "source",
        data.pop("source_label", None)
        or ("synthetic" if prov == Provenance.SYNTHETIC else str(prov.value)),
    )
    data.setdefault("tags", [])
    data.setdefault("services", [])

    # Drop fields from alternate schemas that are not on Observation
    for drop in ("observation_type", "payload", "source_label", "observed_at"):
        data.pop(drop, None)

    # Flatten payload if present
    payload = raw.get("payload")
    if isinstance(payload, dict):
        for key in (
            "ipv4",
            "ipv6",
            "mac",
            "hostname",
            "vendor_hint",
            "dhcp_fingerprint",
            "reported_os",
            "ssid",
            "ap_id",
            "switch_id",
            "port_id",
            "rssi",
            "signal_bucket",
            "connection_type",
            "tags",
            "services",
        ):
            if key in payload and key not in data:
                data[key] = payload[key]

    return Observation.model_validate(data)


def normalize_observations(
    items: list[dict[str, Any]],
    *,
    default_provenance: Provenance = Provenance.SYNTHETIC,
) -> list[Observation]:
    return [normalize_observation(item, default_provenance=default_provenance) for item in items]


def normalize_many(raw_items: list[dict[str, Any]]) -> list[Observation]:
    return normalize_observations(raw_items)
