"""Standalone JSON/CSV/HTML reports — no CDN, HTML-escaped."""

from __future__ import annotations

import csv
import html
import io
import json
from pathlib import Path
from typing import Any

from secure_network_segmentation_lab.enums import PrivacyMode
from secure_network_segmentation_lab.privacy import redact_mapping


def _maybe_redact(rows: list[dict[str, Any]], mode: PrivacyMode) -> list[dict[str, Any]]:
    return [redact_mapping(r, mode) for r in rows]


def write_json_report(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def write_csv_report(
    path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = fieldnames or sorted({k for row in rows for k in row})
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        flat = {k: row.get(k) for k in fields}
        writer.writerow(flat)
    path.write_text(buf.getvalue(), encoding="utf-8")


def write_html_report(path: Path, title: str, sections: dict[str, list[dict[str, Any]]]) -> None:
    """Standalone HTML with escaped content — no external CDN."""
    path.parent.mkdir(parents=True, exist_ok=True)
    parts: list[str] = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8"/>',
        f"<title>{html.escape(title)}</title>",
        "<style>",
        "body{font-family:Georgia,serif;margin:2rem;background:#f7f7f5;color:#1a1a1a}",
        "h1,h2{font-family:system-ui,sans-serif}",
        "table{border-collapse:collapse;width:100%;margin-bottom:2rem;background:#fff}",
        "th,td{border:1px solid #ccc;padding:.4rem .6rem;text-align:left;font-size:.9rem}",
        "th{background:#eee}",
        ".banner{background:#fff3cd;border:1px solid #e0c36a;padding:.75rem;margin-bottom:1rem}",
        "</style>",
        "</head>",
        "<body>",
        f"<h1>{html.escape(title)}</h1>",
        '<div class="banner">SYNTHETIC DEMONSTRATION DATA — '
        "PROPOSED / SIMULATED — NOT APPLIED</div>",
    ]
    for section_title, rows in sections.items():
        parts.append(f"<h2>{html.escape(section_title)}</h2>")
        if not rows:
            parts.append("<p>No rows.</p>")
            continue
        keys = sorted({k for r in rows for k in r})
        parts.append("<table><thead><tr>")
        for k in keys:
            parts.append(f"<th>{html.escape(str(k))}</th>")
        parts.append("</tr></thead><tbody>")
        for row in rows:
            parts.append("<tr>")
            for k in keys:
                val = row.get(k, "")
                if isinstance(val, (dict, list)):
                    val = json.dumps(val, default=str)
                parts.append(f"<td>{html.escape(str(val))}</td>")
            parts.append("</tr>")
        parts.append("</tbody></table>")
    parts.extend(["</body>", "</html>"])
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def export_reports(
    out_dir: Path,
    *,
    devices: list[dict[str, Any]],
    classifications: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    reachability: list[dict[str, Any]],
    drift: list[dict[str, Any]],
    audit: list[dict[str, Any]],
    privacy_mode: PrivacyMode = PrivacyMode.MASKED,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    bundles = {
        "inventory": _maybe_redact(devices, privacy_mode),
        "classification": _maybe_redact(classifications, privacy_mode),
        "segmentation-policy": _maybe_redact(decisions, privacy_mode),
        "reachability": reachability,
        "drift": drift,
        "audit": _maybe_redact(audit, privacy_mode),
        "quarantine": _maybe_redact(
            [d for d in devices if d.get("current_segment") == "quarantine"],
            privacy_mode,
        ),
    }
    for name, rows in bundles.items():
        jp = out_dir / f"{name}-report.json"
        write_json_report(jp, {"report": name, "rows": rows, "privacy_mode": privacy_mode.value})
        written.append(jp)
        cp = out_dir / f"{name}-report.csv"
        write_csv_report(cp, rows)
        written.append(cp)

    hp = out_dir / "lab-report.html"
    write_html_report(hp, "Secure Network Segmentation Lab Report", bundles)
    written.append(hp)
    return written
