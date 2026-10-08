"""Resolve plugin assets and the host repository without changing the FS."""

import os
from pathlib import Path

from .schemas import fail


def skill_root():
    """Source layout: <skill>/scripts/factum_lib/paths.py."""
    return Path(__file__).resolve().parents[2]


def assets_root():
    """Support both a cloned skill and a built Python package."""
    cloned = skill_root() / "assets"
    if cloned.is_dir():
        return cloned

    packaged = Path(__file__).resolve().parent / "assets"
    if packaged.is_dir():
        return packaged

    fail(
        "ASSETS_MISSING",
        "Factum assets are missing. Install the complete skill directory.",
    )


def is_repository(path):
    """Support ordinary repositories and Git worktrees."""
    marker = Path(path) / ".git"
    return marker.is_dir() or marker.is_file()


def enclosing_repository(start, excluded=None):
    excluded = {
        Path(path).resolve() for path in (excluded or [])
    }
    current = Path(start).resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if candidate not in excluded and is_repository(candidate):
            return candidate

    return None


def resolve_repository(explicit=None):
    """
    Resolution order:
    1. --repo
    2. FACTUM_REPO
    3. Repository enclosing the installed plugin
    4. Repository enclosing the working directory

    The plugin's own checkout is never an implicit corpus target.
    """
    plugin = skill_root()

    configured = explicit if explicit is not None else os.environ.get(
        "FACTUM_REPO"
    )
    if configured is not None:
        path = Path(configured).expanduser().resolve()
        if not path.is_dir():
            fail("REPOSITORY_MISSING", str(path))
        if not is_repository(path):
            fail(
                "NOT_A_REPOSITORY",
                f"Expected a Git repository root: {path}",
            )
        return path

    host = enclosing_repository(plugin.parent, excluded={plugin})
    if host is not None:
        return host

    host = enclosing_repository(Path.cwd(), excluded={plugin})
    if host is not None:
        return host

    fail(
        "HOST_REPOSITORY_NOT_FOUND",
        "No host repository was found. Run from the target repository "
        "or pass --repo <repository-root>.",
    )