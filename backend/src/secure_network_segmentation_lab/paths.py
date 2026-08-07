"""Repository path resolution for config/, synthetic/, and runtime/."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def repo_root() -> Path:
    """Locate repository root by walking up from this package file."""
    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / "config" / "default.config.json").is_file() and (
            candidate / "backend"
        ).is_dir():
            return candidate
    # Fallback: backend/src/pkg → parents[3] = repo
    return here.parents[3]


def config_dir() -> Path:
    return repo_root() / "config"


def synthetic_dir() -> Path:
    return repo_root() / "synthetic"


def runtime_dir() -> Path:
    path = repo_root() / "runtime"
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_under_repo(relative: str | Path) -> Path:
    """Resolve a path relative to repo root; reject absolute escapes."""
    root = repo_root().resolve()
    target = (root / relative).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Path escapes repository root: {relative}") from exc
    return target


def database_path(configured: str | None = None) -> Path:
    rel = configured or "runtime/lab.sqlite3"
    path = resolve_under_repo(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
