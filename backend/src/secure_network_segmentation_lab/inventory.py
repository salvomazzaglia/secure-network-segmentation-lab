"""Inventory merge: devices, observations, online/offline/stale."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Any

from secure_network_segmentation_lab.enums import ConnectionType, SecurityState, SourceMode
from secure_network_segmentation_lab.models import Device, Observation, utc_now


def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return utc_now()


def device_from_dict(raw: dict[str, Any]) -> Device:
    """Build a Device from a dict, accepting first_seen / first_seen_utc aliases."""
    data = dict(raw)
    if "first_seen_utc" not in data and "first_seen" in data:
        data["first_seen_utc"] = data.pop("first_seen")
    if "last_seen_utc" not in data and "last_seen" in data:
        data["last_seen_utc"] = data.pop("last_seen")
    if "device_class_hint" not in data and "device_class" in data:
        data["device_class_hint"] = data.get("device_class")
    if "vendor" not in data and data.get("vendor_hint"):
        data["vendor"] = data["vendor_hint"]
    return Device.model_validate(data)


def merge_observation_into_device(
    device: Device,
    observation: Observation | dict[str, Any],
    *,
    stale_after_seconds: int = 86400,
    now: datetime | None = None,
) -> Device:
    now = now or utc_now()
    if isinstance(observation, dict):
        observation = Observation.model_validate(observation)

    data = device.model_dump()
    observed_at = observation.observed_at_utc
    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(tzinfo=UTC)

    first_seen = _parse_dt(data["first_seen_utc"])
    last_seen = _parse_dt(data["last_seen_utc"])

    if observed_at < first_seen:
        first_seen = observed_at
    if observed_at > last_seen:
        last_seen = observed_at
        if observation.ipv4:
            data["ipv4"] = observation.ipv4
        if observation.ipv6:
            data["ipv6"] = observation.ipv6
        if observation.mac:
            data["mac"] = observation.mac
        if observation.hostname:
            data["hostname"] = observation.hostname
        if observation.vendor_hint:
            data["vendor"] = observation.vendor_hint
        if observation.ssid:
            data["ssid"] = observation.ssid
        if observation.ap_id:
            data["ap_id"] = observation.ap_id
        if observation.switch_id:
            data["switch_id"] = observation.switch_id
        if observation.port_id:
            data["port_id"] = observation.port_id
        if observation.rssi is not None:
            data["rssi"] = observation.rssi
        if observation.signal_bucket:
            data["signal_bucket"] = observation.signal_bucket
        if observation.connection_type:
            data["connection_type"] = observation.connection_type
        if observation.tags:
            tags = list(dict.fromkeys([*data.get("tags", []), *observation.tags]))
            data["tags"] = tags

    data["first_seen_utc"] = first_seen
    data["last_seen_utc"] = last_seen
    age = now - last_seen
    data["stale"] = age > timedelta(seconds=stale_after_seconds)
    data["online"] = age <= timedelta(seconds=min(stale_after_seconds, 3600 * 6))
    if not data["online"]:
        data["security_state"] = SecurityState.OFFLINE
    return Device.model_validate(data)


def merge_devices(
    devices: Sequence[Device | dict[str, Any]],
    observations: Sequence[Observation | dict[str, Any]],
    *,
    stale_after_seconds: int = 86400,
    now: datetime | None = None,
) -> list[Device]:
    now = now or utc_now()
    by_id: dict[str, Device] = {}
    for raw in devices:
        device = device_from_dict(raw) if isinstance(raw, dict) else raw
        by_id[device.device_id] = device

    for item in observations:
        obs: Observation = Observation.model_validate(item) if isinstance(item, dict) else item
        if obs.device_id not in by_id:
            by_id[obs.device_id] = Device(
                device_id=obs.device_id,
                alias=obs.hostname or obs.device_id,
                mac=obs.mac or "02:00:00:00:00:00",
                ipv4=obs.ipv4,
                ipv6=obs.ipv6,
                hostname=obs.hostname,
                vendor=obs.vendor_hint,
                connection_type=obs.connection_type or ConnectionType.UNKNOWN,
                first_seen_utc=obs.observed_at_utc,
                last_seen_utc=obs.observed_at_utc,
                provenance=obs.provenance,
                source_mode=SourceMode.SYNTHETIC,
            )
        by_id[obs.device_id] = merge_observation_into_device(
            by_id[obs.device_id],
            obs,
            stale_after_seconds=stale_after_seconds,
            now=now,
        )

    return sorted(by_id.values(), key=lambda d: d.device_id)


def mark_stale(
    devices: list[Device],
    *,
    stale_after_seconds: int = 86400,
    now: datetime | None = None,
) -> list[Device]:
    now = now or utc_now()
    updated: list[Device] = []
    for device in devices:
        age = now - (
            device.last_seen_utc
            if device.last_seen_utc.tzinfo
            else device.last_seen_utc.replace(tzinfo=UTC)
        )
        stale = age > timedelta(seconds=stale_after_seconds)
        online = age <= timedelta(seconds=min(stale_after_seconds, 3600 * 6))
        data = device.model_dump()
        data["stale"] = stale
        data["online"] = online
        if not online:
            data["security_state"] = SecurityState.OFFLINE
        updated.append(Device.model_validate(data))
    return updated
