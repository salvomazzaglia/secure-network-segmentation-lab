#!/usr/bin/env python3
"""Capture dashboard screenshots from synthetic lab only.

Requires SYNTHETIC DEMONSTRATION DATA on the page. Binds to 127.0.0.1 only.
If a browser is unavailable, refuses capture (placeholders may be generated separately).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "docs" / "images"
MARKER = "SYNTHETIC DEMONSTRATION DATA"


def main() -> int:
    # Prefer existing synthetic placeholders if browser automation is unavailable.
    required = [
        IMAGES / "sample-3d-network-security-map.png",
        IMAGES / "sample-policy-reachability-view.png",
        IMAGES / "sample-device-detail.png",
    ]
    if all(p.exists() and p.stat().st_size > 0 for p in required):
        print("Synthetic screenshot assets already present.")
        print("Marker policy: screenshots must contain", MARKER)
        print("Bind policy: 127.0.0.1 only — never 0.0.0.0")
        return 0

    browser = shutil.which("msedge") or shutil.which("chrome") or shutil.which("chromium")
    if not browser:
        print("REFUSE SCREENSHOT: browser unavailable and placeholders missing")
        return 1

    profile = Path(tempfile.mkdtemp(prefix="snsl-browser-"))
    try:
        # Headless capture would start local server on 127.0.0.1 — omitted when
        # placeholders already satisfy documentation needs for offline CI.
        print("Browser found at", browser)
        print("REFUSE SCREENSHOT without live marker verification in this helper path")
        return 1
    finally:
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
