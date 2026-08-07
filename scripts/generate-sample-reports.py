#!/usr/bin/env python3
"""Generate sample JSON/HTML reports from synthetic lab."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    from secure_network_segmentation_lab.lab_bootstrap import bootstrap_lab
    from secure_network_segmentation_lab.reports import export_reports

    db = bootstrap_lab()
    out = ROOT / "examples"
    out.mkdir(parents=True, exist_ok=True)
    export_reports(db, out)
    print("Sample reports written under examples/")


if __name__ == "__main__":
    main()
