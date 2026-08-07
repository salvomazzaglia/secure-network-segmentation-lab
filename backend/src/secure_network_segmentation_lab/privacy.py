"""Privacy masking and hashing helpers. Salt is never persisted."""

from __future__ import annotations

import hashlib
import os
import re
from typing import Any

from secure_network_segmentation_lab.enums import PrivacyMode

_IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_IPV6_RE = re.compile(r"\b(?:[0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}\b")
_MAC_RE = re.compile(r"\b(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b")


class PrivacyError(ValueError):
    pass


def _salt() -> str:
    salt = os.environ.get("SNSL_HASH_SALT")
    if not salt:
        raise PrivacyError(
            "SNSL_HASH_SALT environment variable required for hashed privacy mode. "
            "Salt is never stored by this application."
        )
    return salt


def stable_hash(value: str, *, length: int = 12) -> str:
    """SHA-256 hex digest truncated; salt from env only, never stored."""
    digest = hashlib.sha256(f"{_salt()}:{value}".encode()).hexdigest()
    return digest[:length]


def mask_mac(mac: str | None) -> str | None:
    if not mac:
        return mac
    parts = re.split(r"[:-]", mac.strip())
    if len(parts) != 6:
        return "02:xx:xx:xx:xx:xx"
    return f"{parts[0]}:{parts[1]}:xx:xx:xx:{parts[5]}"


def mask_ip(ip: str | None) -> str | None:
    if not ip:
        return ip
    if ":" in ip:
        # Keep documentation prefix style
        return "2001:db8::xxxx"
    parts = ip.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.{parts[2]}.x"
    return "x.x.x.x"


def mask_ssid(ssid: str | None) -> str | None:
    if not ssid:
        return ssid
    if ssid.startswith("SYNTHETIC-"):
        return ssid  # already synthetic demo label
    return f"SSID-{ssid[:2]}***"


def mask_label(label: str | None) -> str | None:
    if not label:
        return label
    if label.startswith("SYNTHETIC-"):
        return label
    if len(label) <= 4:
        return "***"
    return f"{label[:3]}***"


def hash_value(value: str | None, prefix: str = "H") -> str | None:
    if value is None:
        return None
    return f"{prefix}-{stable_hash(value)}"


def apply_privacy_to_string(text: str, mode: PrivacyMode) -> str:
    if mode == PrivacyMode.FULL:
        return text

    def _mac(m: re.Match[str]) -> str:
        raw = m.group(0)
        if mode == PrivacyMode.HASHED:
            return hash_value(raw, "MAC") or "MAC-****"
        return mask_mac(raw) or "02:xx:xx:xx:xx:xx"

    def _ip(m: re.Match[str]) -> str:
        raw = m.group(0)
        if mode == PrivacyMode.HASHED:
            return hash_value(raw, "IP") or "IP-****"
        return mask_ip(raw) or "x.x.x.x"

    out = _MAC_RE.sub(_mac, text)
    out = _IPV4_RE.sub(_ip, out)
    out = _IPV6_RE.sub(_ip, out)
    return out


def redact_mapping(data: dict[str, Any], mode: PrivacyMode) -> dict[str, Any]:
    """Return a shallow-copied mapping with sensitive fields transformed."""
    if mode == PrivacyMode.FULL:
        result = dict(data)
        result["_privacy_warning"] = (
            "FULL privacy mode — local authorized operation only; never print secrets."
        )
        return result

    sensitive_ip = {"ipv4", "ipv6", "ip", "address"}
    sensitive_mac = {"mac", "calling_station", "station_mac"}
    sensitive_ssid = {"ssid"}
    sensitive_label = {
        "alias",
        "hostname",
        "label",
        "switch_id",
        "ap_id",
        "ownership_label",
        "operator_label",
    }

    out: dict[str, Any] = {}
    for key, value in data.items():
        if value is None:
            out[key] = None
            continue
        if isinstance(value, dict):
            out[key] = redact_mapping(value, mode)
            continue
        if isinstance(value, list):
            out[key] = [redact_mapping(v, mode) if isinstance(v, dict) else v for v in value]
            continue
        if not isinstance(value, str):
            out[key] = value
            continue
        if key in sensitive_mac:
            out[key] = hash_value(value, "MAC") if mode == PrivacyMode.HASHED else mask_mac(value)
        elif key in sensitive_ip:
            out[key] = hash_value(value, "IP") if mode == PrivacyMode.HASHED else mask_ip(value)
        elif key in sensitive_ssid:
            out[key] = hash_value(value, "SSID") if mode == PrivacyMode.HASHED else mask_ssid(value)
        elif key in sensitive_label:
            out[key] = hash_value(value, "LBL") if mode == PrivacyMode.HASHED else mask_label(value)
        else:
            if isinstance(value, str) and mode in {PrivacyMode.MASKED, PrivacyMode.HASHED}:
                out[key] = apply_privacy_to_string(value, mode)
            else:
                out[key] = value
    if mode == PrivacyMode.HASHED:
        out["_privacy_note"] = (
            "Hashed pseudonyms use SHA-256 with SNSL_HASH_SALT; "
            "pseudonymization is not anonymization. Salt is never stored."
        )
    return out
