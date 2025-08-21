# ui/ad_banner_widget.py
# -*- coding: utf-8 -*-
import os
import sys
from PySide6.QtCore import QUrl, QTimer, Qt
from PySide6.QtWebEngineWidgets import QWebEngineView

def _resource_path(relative_path: str) -> str:
    # For source and one-folder build, the file is relative to this script
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # For one-file build, _MEIPASS is the root, and our UI files are in a 'ui' subdir
    if hasattr(sys, '_MEIPASS'):
        base_path = os.path.join(sys._MEIPASS, 'ui')

    return os.path.join(base_path, relative_path)

class AdBannerWidget(QWebEngineView):
    """
    Widget hiển thị banner quảng cáo bằng cách load một file HTML cục bộ
    (trong file HTML có đoạn JS của Adsterra/Ads networks).
    """

    def __init__(
        self,
        parent=None,
        html_filename: str = "ads_banner.html",
        width: int = 728,
        height: int = 90,
        reload_interval_sec: int = 0,
    ) -> None:
        super().__init__(parent)

        # Kích thước banner
        self.setFixedSize(width, height)
        self.setContextMenuPolicy(Qt.NoContextMenu)

        self._html_filename = html_filename
        self._timer: QTimer | None = None

        # Nạp banner ban đầu
        self._load_banner()

        # Hẹn giờ reload nếu cần
        if reload_interval_sec and reload_interval_sec > 0:
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._load_banner)
            self._timer.start(int(reload_interval_sec * 1000))

    # ---------- API phụ ----------
    def set_banner_file(self, html_filename: str) -> None:
        """Đổi file HTML chứa quảng cáo và nạp lại."""
        self._html_filename = html_filename
        self._load_banner()

    def stop_auto_reload(self) -> None:
        if self._timer:
            self._timer.stop()
            self._timer = None

    # ---------- Nội bộ ----------
    def _load_banner(self) -> None:
        # Resolve đường dẫn tới HTML
        if os.path.isabs(self._html_filename):
            html_path = self._html_filename
        else:
            html_path = _resource_path(self._html_filename)

        try:
            with open(html_path, "r", encoding="utf-8") as f:
                html = f.read()
        except Exception as e:
            # Placeholder khi không đọc được file
            html = (
                "<html><body style='display:flex;align-items:center;"
                "justify-content:center;background:#eef2ff;color:#3a63ff;"
                "font-family:Segoe UI, sans-serif;font-size:13px;'>"
                f"Lỗi đọc <b>{self._html_filename}</b>: {e}"
                "</body></html>"
            )

        # QUAN TRỌNG: Cho trang 1 origin HTTPS để JS Adsterra chạy
        self.setHtml(html, baseUrl=QUrl("https://ad.local/"))
