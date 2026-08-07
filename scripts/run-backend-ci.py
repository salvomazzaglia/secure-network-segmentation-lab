#!/usr/bin/env python3
"""Backend CI helper."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"


def main() -> int:
    py = sys.executable
    cmds = [
        [py, "-m", "ruff", "check", "src", "tests"],
        [py, "-m", "ruff", "format", "--check", "src", "tests"],
        [py, "-m", "mypy", "src"],
        [py, "-m", "pytest"],
        [py, "-m", "build"],
    ]
    for cmd in cmds:
        print("+", " ".join(cmd))
        subprocess.run(cmd, cwd=BACKEND, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
