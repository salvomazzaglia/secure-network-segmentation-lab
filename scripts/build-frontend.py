#!/usr/bin/env python3
"""Build frontend production bundle."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"


def main() -> int:
    subprocess.run(["npm", "ci"], cwd=FRONTEND, check=True)
    subprocess.run(["npm", "run", "build"], cwd=FRONTEND, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
