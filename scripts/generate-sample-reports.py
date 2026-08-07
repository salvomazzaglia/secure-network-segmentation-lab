#!/usr/bin/env python3
"""Generate sample JSON/HTML reports from synthetic lab."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    from secure_network_segmentation_lab.lab_bootstrap import bootstrap_lab
    from secure_network_segmentation_lab.privacy import PrivacyMode
    from secure_network_segmentation_lab.reachability import (
        evaluate_matrix,
        load_reachability_policy,
    )
    from secure_network_segmentation_lab.reports import export_reports

    db = bootstrap_lab()
    segments = [str(s.get("segment_id")) for s in db.list_segments()]
    reachability = [
        r.model_dump(mode="json")
        for r in evaluate_matrix(segments, segments, ["any"], policy=load_reachability_policy())
    ]
    out = ROOT / "examples"
    written = export_reports(
        out,
        devices=db.list_devices(),
        classifications=db.list_classifications(),
        decisions=db.list_policy_decisions(),
        reachability=reachability,
        drift=[],
        audit=db.list_audit(),
        privacy_mode=PrivacyMode.MASKED,
    )
    print(f"Sample reports written under examples/ ({len(written)} files)")


if __name__ == "__main__":
    main()
