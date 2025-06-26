from __future__ import annotations

"""Utility helpers for determining important filesystem paths.

These helpers provide a single source of truth for the location of
persistent data (encrypted API keys, local SQLite DBs, text lists, …)
so that every component of the application refers to the **exact same
folder** regardless of the current working directory or the execution
environment (local development, unit-tests, Docker image, etc.).
"""

import os
from pathlib import Path
from typing import Optional

__all__ = [
    "get_project_root",
    "get_data_dir",
]


def _find_repo_root(start_dir: Path) -> Optional[Path]:
    """Walk upwards from *start_dir* looking for the project‐level *pyproject.toml*.

    The file must contain the package name ``email-validator-tool``.  If no
    such directory is found, *None* is returned.
    """

    for directory in [start_dir, *start_dir.parents]:
        pyproject = directory / "pyproject.toml"
        if not pyproject.exists():
            continue
        try:
            # A very cheap check – we do not parse TOML to avoid an extra
            # dependency here.
            if 'name = "email-validator-tool"' in pyproject.read_text(encoding="utf-8"):
                return directory
        except Exception:
            # If the file cannot be read for some reason, keep searching.
            continue
    return None


def get_project_root() -> Path:
    """Return the absolute path to the project root directory.

    Precedence:
    1. ``EMAIL_VALIDATOR_PROJECT_ROOT`` environment variable – allows full
       manual control (e.g. inside containers).
    2. First parent directory (starting from the current file) that contains
       a *pyproject.toml* whose ``name`` is ``email-validator-tool``.
    3. Fallback to :pyfunc:`Path.cwd` if nothing was found.
    """

    env_override = os.getenv("EMAIL_VALIDATOR_PROJECT_ROOT")
    if env_override:
        return Path(env_override).expanduser().resolve()

    located_root = _find_repo_root(Path(__file__).resolve())
    if located_root:
        return located_root

    # Last resort: current working directory – may be inside a Docker image
    # where the *pyproject.toml* was not copied.
    return Path.cwd().resolve()


def get_data_dir() -> Path:
    """Return the *data* directory path, creating it if required.

    Precedence:
    1. ``EMAIL_VALIDATOR_DATA_DIR`` environment variable (absolute or
       relative).
    2. ``<project_root>/data`` (where *project_root* is determined by
       :pyfunc:`get_project_root`).
    """

    env_override = os.getenv("EMAIL_VALIDATOR_DATA_DIR")
    # Also accept the shorter alias "DATA_DIR" for convenience / backwards compat
    if not env_override:
        env_override = os.getenv("DATA_DIR")
    if env_override:
        data_dir = Path(env_override).expanduser().resolve()
    else:
        data_dir = get_project_root() / "data"

    # Always make sure the directory exists to avoid race conditions where
    # different components attempt to create it concurrently.
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir 