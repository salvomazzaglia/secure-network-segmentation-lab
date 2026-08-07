#!/usr/bin/env python3
"""Capture real dashboard screenshots from the synthetic lab only.

Requires SYNTHETIC DEMONSTRATION DATA in the live DOM. Binds to 127.0.0.1 only.
Uses a temporary browser profile via system Chrome/Edge + puppeteer-core
(installed under .capture-node/, not a permanent project dependency).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "docs" / "images"
MARKER = "SYNTHETIC DEMONSTRATION DATA"
CAPTURE_JS = ROOT / "scripts" / "capture-dashboard.mjs"
BACKEND = "http://127.0.0.1:8765/api/v1/health"
FRONTEND = "http://127.0.0.1:5173/"


def _http_ok(url: str, timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 — localhost only
            return 200 <= resp.status < 300
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def _wait(url: str, seconds: float = 90.0) -> None:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if _http_ok(url):
            return
        time.sleep(0.5)
    raise RuntimeError(f"Timed out waiting for {url}")


def _validate_png(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    if len(data) < 8 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"{path.name}: not a valid PNG")
    if len(data) < 50_000:
        raise RuntimeError(f"{path.name}: file too small ({len(data)} bytes) — likely placeholder")
    # IHDR width/height
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if width < 1000 or height < 700:
        raise RuntimeError(f"{path.name}: unexpected dimensions {width}x{height}")
    # crude non-monochrome check via sampled bytes variance
    sample = data[1000 : 1000 + 4000]
    if len(set(sample)) < 40:
        raise RuntimeError(f"{path.name}: appears near-monochrome / placeholder")
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "bytes": len(data), "width": width, "height": height}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--start-servers",
        action="store_true",
        help="Start backend (8765) and frontend (5173) on 127.0.0.1 if not already up",
    )
    args = parser.parse_args()

    procs: list[subprocess.Popen[bytes]] = []
    try:
        if args.start_servers:
            if not _http_ok(BACKEND):
                procs.append(
                    subprocess.Popen(
                        [
                            sys.executable,
                            "-m",
                            "secure_network_segmentation_lab",
                            "serve",
                            "--host",
                            "127.0.0.1",
                            "--port",
                            "8765",
                        ],
                        cwd=str(ROOT),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                )
            if not _http_ok(FRONTEND):
                npm = shutil.which("npm")
                if not npm:
                    print("REFUSE SCREENSHOT: npm not found to start frontend")
                    return 1
                procs.append(
                    subprocess.Popen(
                        [npm, "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"],
                        cwd=str(ROOT / "frontend"),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                )

        if not _http_ok(BACKEND):
            print("REFUSE SCREENSHOT: backend not reachable at", BACKEND)
            print("Start with: python -m secure_network_segmentation_lab serve --host 127.0.0.1 --port 8765")
            return 1
        if not _http_ok(FRONTEND):
            print("REFUSE SCREENSHOT: frontend not reachable at", FRONTEND)
            print("Start with: npm run dev -- --host 127.0.0.1 --port 5173")
            return 1

        _wait(BACKEND)
        _wait(FRONTEND)

        node = shutil.which("node")
        if not node:
            print("REFUSE SCREENSHOT: node not found")
            return 1
        if not CAPTURE_JS.is_file():
            print("REFUSE SCREENSHOT: missing", CAPTURE_JS)
            return 1

        print("Capturing live synthetic dashboard on 127.0.0.1 …")
        print("Marker policy:", MARKER)
        result = subprocess.run([node, str(CAPTURE_JS)], cwd=str(ROOT), check=False)
        if result.returncode != 0:
            print("REFUSE SCREENSHOT: capture process failed")
            return result.returncode

        required = [
            IMAGES / "sample-3d-network-security-map.png",
            IMAGES / "sample-policy-reachability-view.png",
            IMAGES / "sample-device-detail.png",
        ]
        report = []
        for path in required:
            if not path.is_file():
                print("REFUSE SCREENSHOT: missing", path.name)
                return 1
            meta = _validate_png(path)
            report.append(meta)
            print("OK", meta)

        (ROOT / "capture-node-deps").mkdir(exist_ok=True)
        (ROOT / "capture-node-deps" / "screenshot-capture-report.json").write_text(
            json.dumps({"marker": MARKER, "bind": "127.0.0.1", "screenshots": report}, indent=2) + "\n",
            encoding="utf-8",
        )
        return 0
    finally:
        for proc in procs:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
