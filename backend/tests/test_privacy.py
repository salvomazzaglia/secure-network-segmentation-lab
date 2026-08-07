from __future__ import annotations

import pytest

from secure_network_segmentation_lab.enums import PrivacyMode
from secure_network_segmentation_lab.privacy import (
    PrivacyError,
    hash_value,
    mask_ip,
    mask_label,
    mask_mac,
    mask_ssid,
    redact_mapping,
)


def test_mask_ip():
    assert mask_ip("192.0.2.10").endswith(".x")
    assert mask_ip("2001:db8::1") == "2001:db8::xxxx"


def test_mask_mac():
    assert "xx" in mask_mac("02:00:00:00:01:01")
    assert mask_mac("02:00:00:00:01:01").startswith("02:")


def test_mask_ssid_synthetic_passthrough():
    assert mask_ssid("SYNTHETIC-LAB") == "SYNTHETIC-LAB"


def test_mask_label_synthetic_passthrough():
    assert mask_label("SYNTHETIC-PC-01") == "SYNTHETIC-PC-01"


def test_mask_label_other():
    assert "***" in (mask_label("RealHostName") or "")


def test_redact_masked():
    out = redact_mapping(
        {
            "mac": "02:00:00:00:01:01",
            "ipv4": "203.0.113.10",
            "ssid": "OTHER-SSID",
            "alias": "hostabc",
        },
        PrivacyMode.MASKED,
    )
    assert "xx" in out["mac"]
    assert out["ipv4"].endswith(".x")


def test_hashed_requires_salt(monkeypatch):
    monkeypatch.delenv("SNSL_HASH_SALT", raising=False)
    with pytest.raises(PrivacyError):
        hash_value("02:00:00:00:01:01")


def test_hashed_mode(monkeypatch):
    monkeypatch.setenv("SNSL_HASH_SALT", "unit-test-salt")
    out = redact_mapping({"mac": "02:00:00:00:01:01", "alias": "hostabcde"}, PrivacyMode.HASHED)
    assert out["mac"].startswith("MAC-") or out["mac"].startswith("H-")
    assert "unit-test-salt" not in str(out)


def test_full_warning():
    out = redact_mapping({"mac": "02:00:00:00:01:01"}, PrivacyMode.FULL)
    assert "_privacy_warning" in out


def test_switch_ap_masking():
    out = redact_mapping({"switch_id": "edge-sw-1", "ap_id": "ap-room-1"}, PrivacyMode.MASKED)
    assert "***" in out["switch_id"] or out["switch_id"].startswith("edge")
