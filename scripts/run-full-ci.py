#!/usr/bin/env python3
"""Run local CI-equivalent checks (synthetic only, no host network discovery)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], cwd: Path) -> None:
    print("+", " ".join(cmd), f"(cwd={cwd})")
    subprocess.run(cmd, cwd=cwd, check=True)


def resolve_npm() -> str:
    # Prefer npm.cmd on Windows — CreateProcess cannot launch the extensionless shim.
    for name in ("npm.cmd", "npm"):
        found = shutil.which(name)
        if found:
            return found
    raise RuntimeError("npm not found on PATH")


def main() -> int:
    py = sys.executable
    npm = resolve_npm()
    backend = ROOT / "backend"
    frontend = ROOT / "frontend"

    run([py, str(ROOT / "scripts" / "generate-synthetic-lab.py")], ROOT)
    run([py, "-m", "pip", "install", "-e", ".[dev]"], backend)
    run([py, "-m", "ruff", "check", "src", "tests"], backend)
    run([py, "-m", "ruff", "format", "--check", "src", "tests"], backend)
    run([py, "-m", "mypy", "src"], backend)
    run([py, "-m", "pytest"], backend)
    run([py, "-m", "build"], backend)
    run([py, str(ROOT / "scripts" / "validate-repository.py")], ROOT)

    run([npm, "ci"], frontend)
    run([npm, "run", "typecheck"], frontend)
    run([npm, "run", "lint"], frontend)
    run([npm, "run", "format:check"], frontend)
    run([npm, "test"], frontend)
    run([npm, "run", "build"], frontend)
    print("FULL LOCAL CI PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
