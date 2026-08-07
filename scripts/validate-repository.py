#!/usr/bin/env python3
"""Repository privacy and safety guards for tracked content."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RFC1918 = [
    re.compile(r"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
    re.compile(r"\b192\.168\.\d{1,3}\.\d{1,3}\b"),
    re.compile(r"\b172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}\b"),
]

SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "runtime",
    "dist",
    "build",
    ".ruff_cache",
    ".mypy_cache",
    ".pytest_cache",
    "htmlcov",
    "coverage",
}


def main() -> int:
    errors: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in {
            ".png",
            ".jpg",
            ".pyc",
            ".sqlite3",
            ".db",
            ".whl",
            ".js",
        }:
            continue
        if path.name == "package-lock.json":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = str(path.relative_to(ROOT))
        if any(part in {"synthetic", "examples"} for part in path.parts) or (
            "config" in path.parts and path.suffix in {".json", ".yml", ".yaml"}
        ):
            for pattern in RFC1918:
                if pattern.search(text):
                    errors.append(f"RFC1918 in {rel}")
        # Executable danger in source only
        if path.suffix == ".py" and "src" in path.parts:
            code_lines = [
                line for line in text.splitlines() if not line.strip().startswith("#")
            ]
            code = "\n".join(code_lines)
            if "shell=True" in code.replace(" ", ""):
                errors.append(f"shell=True in {rel}")
            if re.search(r"(?<![\"'])\beval\(", code):
                errors.append(f"eval( in {rel}")
            if "yaml.load(" in code and "safe_load" not in code:
                errors.append(f"unsafe yaml.load in {rel}")

    # CI must not use self-hosted or pull_request_target
    ci = ROOT / ".github" / "workflows" / "ci.yml"
    if ci.exists():
        ci_text = ci.read_text(encoding="utf-8")
        if "self-hosted" in ci_text:
            errors.append("self-hosted runner in ci.yml")
        if "pull_request_target" in ci_text:
            errors.append("pull_request_target in ci.yml")

    if errors:
        print("PRIVACY/REPO GUARD FAILURES:")
        for err in sorted(set(errors)):
            print(" -", err)
        return 1
    print("Repository privacy guards PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
