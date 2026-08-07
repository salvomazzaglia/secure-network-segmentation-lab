from __future__ import annotations

import json
import re

from secure_network_segmentation_lab.paths import repo_root, synthetic_dir

RFC1918 = [
    re.compile(r"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
    re.compile(r"\b192\.168\.\d{1,3}\.\d{1,3}\b"),
    re.compile(r"\b172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}\b"),
]


def test_no_rfc1918_in_synthetic():
    for path in synthetic_dir().rglob("*"):
        if path.is_file() and path.suffix in {".json", ".jsonl", ".md"}:
            text = path.read_text(encoding="utf-8")
            for pattern in RFC1918:
                assert not pattern.search(text), f"RFC1918 in {path}"


def test_synthetic_mac_policy():
    text = (synthetic_dir() / "devices.json").read_text(encoding="utf-8")
    macs = re.findall(r"02:[0-9a-fA-F:]{14}", text)
    assert macs


def test_no_nmap_in_src():
    root = repo_root() / "backend" / "src"
    for path in root.rglob("*.py"):
        # Skip the policy scanner that lists forbidden markers as data.
        if path.name in {"config.py", "policy_validation.py"}:
            continue
        lines = [
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if not line.strip().startswith("#")
        ]
        text = "\n".join(lines).lower()
        assert "nmap" not in text
        assert "masscan" not in text
        assert "shell=true" not in text.replace(" ", "")
        # Flag live eval usage, not string markers
        assert not re.search(r"(?<![\"'])\beval\(", text)


def test_ci_no_self_hosted():
    ci = repo_root() / ".github" / "workflows" / "ci.yml"
    text = ci.read_text(encoding="utf-8")
    assert "pull_request_target" not in text
    assert "self-hosted" not in text


def test_synthetic_node_count():
    data = json.loads((synthetic_dir() / "devices.json").read_text(encoding="utf-8"))
    count = data.get("device_count") or data.get("count") or len(data.get("devices", []))
    assert 35 <= count <= 45


def test_documentation_ips():
    text = (synthetic_dir() / "devices.json").read_text(encoding="utf-8")
    assert "192.168." not in text
    assert any(x in text for x in ("192.0.2.", "198.51.100.", "203.0.113."))
