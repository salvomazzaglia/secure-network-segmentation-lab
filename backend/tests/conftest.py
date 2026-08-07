"""Shared fixtures for SNSL backend tests."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from secure_network_segmentation_lab.classification import classify_device
from secure_network_segmentation_lab.inventory import device_from_dict
from secure_network_segmentation_lab.lab_bootstrap import bootstrap_lab
from secure_network_segmentation_lab.models import Classification
from secure_network_segmentation_lab.paths import repo_root, synthetic_dir


@pytest.fixture(scope="session")
def root() -> Path:
    return repo_root()


@pytest.fixture(scope="session")
def bootstrapped_db(tmp_path_factory: pytest.TempPathFactory):
    db_dir = tmp_path_factory.mktemp("snsl-db")
    from secure_network_segmentation_lab.database import open_database

    db = open_database(db_dir / "test.sqlite3")
    return bootstrap_lab(db)


@pytest.fixture(scope="session")
def synthetic_devices():
    path = synthetic_dir() / "devices.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return [device_from_dict(d) for d in data["devices"]]


@pytest.fixture
def sample_printer():
    return device_from_dict(
        {
            "device_id": "SYNTHETIC-PRINTER-99",
            "alias": "SYNTHETIC-PRINTER-99",
            "mac": "02:00:00:00:99:01",
            "ipv4": "203.0.113.99",
            "device_class": "printer",
            "current_segment": "trusted",
            "connection_type": "wired",
            "security_state": "restricted",
            "online": True,
            "first_seen": datetime.now(UTC).isoformat(),
            "last_seen": datetime.now(UTC).isoformat(),
            "vendor_hint": "Fictional Print Works",
            "hostname": "printer-99.lab.example.invalid",
            "provenance": "synthetic",
        }
    )


@pytest.fixture
def sample_unknown():
    return device_from_dict(
        {
            "device_id": "SYNTHETIC-UNKNOWN-99",
            "alias": "SYNTHETIC-UNKNOWN-99",
            "mac": "02:00:00:00:99:02",
            "ipv4": "192.0.2.99",
            "device_class": "unknown",
            "current_segment": "quarantine",
            "connection_type": "wired",
            "security_state": "quarantined",
            "online": True,
            "first_seen": datetime.now(UTC).isoformat(),
            "last_seen": datetime.now(UTC).isoformat(),
            "provenance": "synthetic",
        }
    )


@pytest.fixture
def printer_classification(sample_printer) -> Classification:
    return classify_device(
        sample_printer,
        observations=[
            {
                "device_id": sample_printer.device_id,
                "dhcp_fingerprint": "synth-print",
                "reported_os": "synth-os-printer",
                "services": ["printing"],
            }
        ],
    )
