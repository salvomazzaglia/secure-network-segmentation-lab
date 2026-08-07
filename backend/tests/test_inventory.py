from __future__ import annotations

from datetime import UTC, datetime, timedelta

from secure_network_segmentation_lab.enums import ConnectionType, Provenance
from secure_network_segmentation_lab.inventory import (
    device_from_dict,
    mark_stale,
    merge_observation_into_device,
)
from secure_network_segmentation_lab.models import Observation


def test_add_synthetic(sample_printer):
    assert sample_printer.mac.startswith("02:")
    assert sample_printer.device_id.startswith("SYNTHETIC-")


def test_merge_observation(sample_printer):
    later = datetime.now(UTC) + timedelta(hours=1)
    obs = Observation(
        observation_id="obs-1",
        device_id=sample_printer.device_id,
        observed_at_utc=later,
        provenance=Provenance.SYNTHETIC,
        ipv4="203.0.113.88",
    )
    updated = merge_observation_into_device(sample_printer, obs)
    assert updated.ipv4 == "203.0.113.88"


def test_first_seen(sample_printer):
    earlier = datetime.now(UTC) - timedelta(days=5)
    obs = Observation(
        observation_id="obs-2",
        device_id=sample_printer.device_id,
        observed_at_utc=earlier,
        provenance=Provenance.SYNTHETIC,
    )
    updated = merge_observation_into_device(sample_printer, obs)
    assert updated.first_seen_utc <= sample_printer.first_seen_utc


def test_connection_wireless(sample_printer):
    obs = Observation(
        observation_id="obs-3",
        device_id=sample_printer.device_id,
        observed_at_utc=datetime.now(UTC) + timedelta(minutes=1),
        provenance=Provenance.SYNTHETIC,
        ap_id="SYNTHETIC-AP-01",
        connection_type=ConnectionType.WIRELESS,
    )
    updated = merge_observation_into_device(sample_printer, obs)
    assert updated.connection_type == ConnectionType.WIRELESS


def test_stale(sample_printer):
    old = sample_printer.model_copy(
        update={"last_seen_utc": datetime.now(UTC) - timedelta(days=10)}
    )
    marked = mark_stale([old], stale_after_seconds=86400)[0]  
    assert marked.stale is True


def test_roundtrip(sample_printer):
    again = device_from_dict(sample_printer.model_dump(mode="json"))
    assert again.device_id == sample_printer.device_id
