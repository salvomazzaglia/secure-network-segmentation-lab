from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from secure_network_segmentation_lab.adapters import get_adapter_plan
from secure_network_segmentation_lab.api import create_app
from secure_network_segmentation_lab.imports import ImportError_ as SafeImportError
from secure_network_segmentation_lab.imports import load_import_json, validate_import_path


@pytest.fixture(scope="module")
def client():
    app = create_app(bootstrap=True)
    with TestClient(app) as c:
        yield c


def test_adapter_plans():
    for name in ["radius", "lldp", "snmp", "firewall", "dhcp", "arp", "fdb", "wlan"]:
        plan = get_adapter_plan(name)
        assert plan.connects is False
        assert plan.mutates is False
        assert plan.steps


def test_import_json(tmp_path: Path):
    path = tmp_path / "inv.json"
    path.write_text(
        json.dumps({"devices": [{"device_id": "SYNTHETIC-A", "mac": "02:00:00:00:00:01"}]}),
        encoding="utf-8",
    )
    payload = load_import_json(path, base=tmp_path)
    assert "devices" in payload


def test_import_path_traversal(tmp_path: Path):
    base = tmp_path / "base"
    base.mkdir()
    with pytest.raises(SafeImportError):
        validate_import_path(tmp_path / "outside.json", base=base)


def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_lab(client):
    r = client.get("/api/v1/lab")
    assert r.status_code == 200
    assert r.json()["device_count"] >= 35


def test_devices(client):
    r = client.get("/api/v1/devices")
    assert r.status_code == 200
    body = r.json()
    devices = body["devices"] if isinstance(body, dict) else body
    assert len(devices) >= 35


def test_topology(client):
    assert client.get("/api/v1/topology").status_code == 200


def test_classifications(client):
    assert client.get("/api/v1/classifications").status_code == 200


def test_decisions(client):
    assert client.get("/api/v1/policy/decisions").status_code == 200


def test_reachability(client):
    r = client.get(
        "/api/v1/reachability",
        params={"source": "guest", "destination": "management", "service": "ssh"},
    )
    assert r.status_code == 200


def test_drift(client):
    assert client.get("/api/v1/drift").status_code == 200


def test_events(client):
    assert client.get("/api/v1/events").status_code == 200


def test_adapters(client):
    assert client.get("/api/v1/adapters").status_code == 200


def test_simulation_step(client):
    r = client.post("/api/v1/simulation/step", params={"scenario": "mixed"})
    assert r.status_code == 200


def test_approval_synthetic(client):
    devices = client.get("/api/v1/devices").json()
    devices = devices["devices"] if isinstance(devices, dict) else devices
    unknown = next(d for d in devices if "UNK" in str(d.get("device_id", "")))
    r = client.post(
        "/api/v1/approvals",
        json={
            "device_id": unknown["device_id"],
            "decision": "keep_quarantined",
            "justification": "still reviewing",
            "synthetic": True,
            "recommended_segment": "quarantine",
        },
    )
    assert r.status_code == 200
    assert "NO NETWORK CHANGE" in r.json().get("note", "")


def test_approval_requires_synthetic(client):
    devices = client.get("/api/v1/devices").json()
    devices = devices["devices"] if isinstance(devices, dict) else devices
    r = client.post(
        "/api/v1/approvals",
        json={
            "device_id": devices[0]["device_id"],
            "decision": "approve",
            "justification": "x",
            "synthetic": False,
        },
    )
    assert r.status_code in {400, 422}
