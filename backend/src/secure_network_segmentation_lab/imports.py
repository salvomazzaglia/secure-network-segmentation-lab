"""Safe offline import with path traversal / symlink / NUL / size guards."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from secure_network_segmentation_lab.paths import repo_root

MAX_IMPORT_BYTES = 5 * 1024 * 1024  # 5 MiB


class ImportError_(ValueError):
    """Import validation error (named to avoid shadowing builtins.ImportError)."""


def _assert_safe_path(path: Path, *, base: Path | None = None) -> Path:
    base = (base or repo_root()).resolve()
    if "\x00" in str(path):
        raise ImportError_("NUL byte in path rejected")
    # Reject before resolve if symlink
    if path.exists() and path.is_symlink():
        raise ImportError_("Symlink imports rejected")
    resolved = path.resolve()
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        # Allow absolute paths under an explicit allowed parent when base contains path
        # Still reject path traversal components
        raise ImportError_(f"Path traversal / escape rejected: {path}") from exc
    if resolved.exists() and resolved.is_symlink():
        raise ImportError_("Symlink imports rejected")
    return resolved


def _read_limited(path: Path) -> bytes:
    size = path.stat().st_size
    if size > MAX_IMPORT_BYTES:
        raise ImportError_(f"Import oversized (>{MAX_IMPORT_BYTES} bytes)")
    data = path.read_bytes()
    if b"\x00" in data:
        raise ImportError_("NUL byte in file content rejected")
    return data


def load_import_json(path: Path, *, base: Path | None = None) -> Any:
    safe = _assert_safe_path(path, base=base)
    raw = _read_limited(safe)
    return json.loads(raw.decode("utf-8"))


def load_import_jsonl(path: Path, *, base: Path | None = None) -> list[dict[str, Any]]:
    safe = _assert_safe_path(path, base=base)
    raw = _read_limited(safe)
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(raw.decode("utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if not isinstance(obj, dict):
            raise ImportError_(f"JSONL line {line_no} must be an object")
        rows.append(obj)
    return rows


def load_import_csv(path: Path, *, base: Path | None = None) -> list[dict[str, str]]:
    safe = _assert_safe_path(path, base=base)
    raw = _read_limited(safe)
    text = raw.decode("utf-8")
    reader = csv.DictReader(text.splitlines())
    return [dict(row) for row in reader]


def validate_import_path(path: str | Path, *, base: Path | None = None) -> Path:
    """Validate import path for CLI ``snsl validate --import``."""
    p = Path(path)
    return _assert_safe_path(p, base=base)


def summarize_import(path: Path) -> dict[str, Any]:
    """Offline-only import summary. No remote enrichment / DNS / OUI lookup."""
    safe = validate_import_path(path)
    suffix = safe.suffix.lower()
    if suffix == ".json":
        data = load_import_json(safe)
        count = len(data) if isinstance(data, list) else 1
        kind = "json"
    elif suffix == ".jsonl":
        data = load_import_jsonl(safe)
        count = len(data)
        kind = "jsonl"
    elif suffix == ".csv":
        data = load_import_csv(safe)
        count = len(data)
        kind = "csv"
    else:
        raise ImportError_(f"Unsupported import format: {suffix}")
    return {
        "path": str(safe),
        "kind": kind,
        "record_count": count,
        "enrichment": False,
        "note": "Offline import only — no remote enrichment",
    }
