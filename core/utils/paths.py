"""Utility functions for resolving application data, log, and temp paths.

Cross-platform behavior:
- Windows: %LOCALAPPDATA%/ConveyorCalculator
- macOS: ~/Library/Application Support/ConveyorCalculator
- Linux/Unix: ~/.local/share/ConveyorCalculator

All returned directories are created if they do not already exist.
"""

from __future__ import annotations

import os
import sys
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

def resource_path(relative_path):
    """
    Lấy đường dẫn tuyệt đối đến tài nguyên.
    Hoạt động cho cả development và PyInstaller bundle.
    
    Args:
        relative_path (str): Đường dẫn tương đối từ thư mục gốc của dự án
        
    Returns:
        str: Đường dẫn tuyệt đối đến tài nguyên
    """
    try:
        # PyInstaller tạo thư mục temp và lưu đường dẫn trong _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            # Nếu không phải PyInstaller, sử dụng thư mục hiện tại
            base_path = os.path.abspath(".")
        
        # Kết hợp đường dẫn cơ sở với đường dẫn tương đối
        full_path = os.path.join(base_path, relative_path)
        
        # Kiểm tra xem file có tồn tại không
        if os.path.exists(full_path):
            return full_path
        
        # Nếu không tìm thấy trong PyInstaller, thử tìm trong thư mục gốc
        if hasattr(sys, '_MEIPASS') and base_path != os.path.abspath("."):
            alt_path = os.path.join(os.path.abspath("."), relative_path)
            if os.path.exists(alt_path):
                return alt_path
        
        # Thử tìm trong thư mục của script hiện tại
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, "..", "..", relative_path)
        if os.path.exists(script_path):
            return script_path
        
        # Thử tìm trong thư mục làm việc hiện tại
        cwd_path = os.path.join(os.getcwd(), relative_path)
        if os.path.exists(cwd_path):
            return cwd_path
        
        # Nếu vẫn không tìm thấy, trả về đường dẫn gốc
        return full_path
        
    except Exception as e:
        print(f"Warning: Error in resource_path for {relative_path}: {e}")
        # Fallback: trả về đường dẫn tương đối
        return relative_path

def get_data_dir():
    """Lấy đường dẫn đến thư mục dữ liệu"""
    return resource_path("data")

def get_images_dir():
    """Lấy đường dẫn đến thư mục hình ảnh"""
    return resource_path("ui/images")

def get_fonts_dir():
    """Lấy đường dẫn đến thư mục font"""
    return resource_path("reports/fonts")

def get_models_dir():
    """Lấy đường dẫn đến thư mục 3D models"""
    return resource_path("ui/models")

def get_js_dir():
    """Lấy đường dẫn đến thư mục JavaScript"""
    return resource_path("ui/js")

def get_templates_dir():
    """Lấy đường dẫn đến thư mục templates"""
    return resource_path("reports")

def ensure_dir(path):
    """Đảm bảo thư mục tồn tại, tạo mới nếu cần"""
    os.makedirs(path, exist_ok=True)
    return path

def get_app_root():
    """Lấy đường dẫn gốc của ứng dụng"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller bundle
        return sys._MEIPASS
    else:
        # Development mode
        return os.path.abspath(".")

def get_user_data_dir():
    """Lấy thư mục dữ liệu người dùng"""
    if sys.platform == "win32":
        appdata = os.environ.get('APPDATA')
        if appdata:
            return os.path.join(appdata, "ConveyorCalculatorAI")
        else:
            return os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "ConveyorCalculatorAI")
    elif sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", "ConveyorCalculatorAI")
    else:
        return os.path.join(os.path.expanduser("~"), ".conveyor_calculator_ai")

def get_logs_dir():
    """Lấy thư mục logs"""
    logs_dir = os.path.join(get_user_data_dir(), "logs")
    ensure_dir(logs_dir)
    return logs_dir

def get_config_dir():
    """Lấy thư mục cấu hình"""
    config_dir = os.path.join(get_user_data_dir(), "config")
    ensure_dir(config_dir)
    return config_dir


__all__ = [
    "get_app_data_dir",
    "get_log_path",
    "get_temp_path",
]


