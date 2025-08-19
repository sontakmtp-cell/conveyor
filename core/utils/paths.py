"""Utility functions for resolving application data, log, and temp paths.

Cross-platform behavior:
- Windows: %LOCALAPPDATA%/ConveyorCalculator
- macOS: ~/Library/Application Support/ConveyorCalculator
- Linux/Unix: ~/.local/share/ConveyorCalculator

All returned directories are created if they do not already exist.
"""

from __future__ import annotations

import os
import platform
from pathlib import Path


APP_DIR_NAME = "ConveyorCalculator"


def _ensure_directory_exists(path: Path) -> str:
    """Create the directory if it does not exist and return its string path."""
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def get_app_data_dir() -> str:
    """Return the base application data directory (platform specific)."""
    system_name = platform.system().lower()

    if system_name == "windows":
        # Prefer LOCALAPPDATA; fall back to APPDATA; then to user home
        base = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
        if base:
            return _ensure_directory_exists(Path(base) / APP_DIR_NAME)
        return _ensure_directory_exists(Path.home() / "AppData" / "Local" / APP_DIR_NAME)

    if system_name == "darwin":  # macOS
        return _ensure_directory_exists(Path.home() / "Library" / "Application Support" / APP_DIR_NAME)

    # Linux and other Unix-like systems
    xdg_data_home = os.getenv("XDG_DATA_HOME")
    if xdg_data_home:
        return _ensure_directory_exists(Path(xdg_data_home) / APP_DIR_NAME)
    return _ensure_directory_exists(Path.home() / ".local" / "share" / APP_DIR_NAME)


def get_log_path() -> str:
    """Return the directory for log files under the app data directory."""
    return _ensure_directory_exists(Path(get_app_data_dir()) / "logs")


def get_temp_path() -> str:
    """Return the directory for temporary files under the app data directory."""
    return _ensure_directory_exists(Path(get_app_data_dir()) / "temp")


__all__ = [
    "get_app_data_dir",
    "get_log_path",
    "get_temp_path",
]


