# ui/styles.py

# -*- coding: utf-8 -*-

# --- Giao diện SÁNG ---
LIGHT = """
/* Nền chính và các thành phần cơ bản */
QMainWindow { background: #f8fafc; color: #0f172a; }
QStatusBar { background:#f8fafc; border-top:1px solid #e2e8f0; color:#64748b; font-size:12px; }

/* Header */
QFrame#headerFrame { background:#ffffff; border-bottom:1px solid #e2e8f0; }
QLabel#headerTitle { color:#1e293b; font-size:22px; font-weight:bold; padding:8px 0; }
QLabel#headerSubtitle { color:#475569; font-size:12px; padding-bottom:8px; }

/* Nút bấm */
QPushButton { background:#ffffff; color:#334155; border:1px solid #cbd5e1; border-radius:8px; padding:10px 16px; font-weight:600; }
QPushButton:hover { background:#f1f5f9; }
QPushButton#primary { background:#3b82f6; color:white; border:none; font-weight:700; }
QPushButton#primary:hover { background:#2563eb; }

/* GroupBox */
QGroupBox { font-weight:600; font-size:13px; color:#374151; background:#ffffff; border:1px solid #d1d5db; border-radius:10px; margin:12px 0; padding-top:20px; }
QGroupBox::title { subcontrol-origin: margin; left:12px; top:8px; padding:0 8px; background:white; }

/* Ô nhập liệu */
QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox { background:#ffffff; color: #0f172a; border:2px solid #e5e7eb; border-radius:6px; padding:8px 12px; }
QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus { border-color: #3b82f6; }

/* Trạng thái cảnh báo cho ô nhập liệu */
QLineEdit[state="warning"], QDoubleSpinBox[state="warning"], QSpinBox[state="warning"], QComboBox[state="warning"] { border-color: #f59e0b; }
QLineEdit[state="error"], QDoubleSpinBox[state="error"], QSpinBox[state="error"], QComboBox[state="error"] { border-color: #ef4444; }

/* Tabs và Bảng */
QTabWidget::pane { border:1px solid #d1d5db; background:#ffffff; border-radius:8px; }
QTabBar::tab { background: #f1f5f9; color: #475569; padding: 10px; border-top-left-radius: 6px; border-top-right-radius: 6px; border: 1px solid #d1d5db; border-bottom: none; margin-right: 2px;}
QTabBar::tab:selected { background: #ffffff; color: #1e293b; font-weight: bold; border-bottom: 1px solid #ffffff;}
QTableWidget { background:#ffffff; border:1px solid #e5e7eb; border-radius:8px; }

/* Thẻ thống kê */
QFrame#card { background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:12px; }
QFrame#card[status="success"] { border-left:4px solid #10b981; }
QFrame#card[status="warning"] { border-left:4px solid #f59e0b; }
QFrame#card[status="danger"]  { border-left:4px solid #ef4444; }
QLabel#cardTitle { color:#475569; font-size:11px; font-weight:600; }
QLabel#cardValue { color:#1e293b; font-size:24px; font-weight:bold; }
QLabel#cardSubtitle { color:#64748b; font-size:11px; }

/* Tooltip */
QToolTip { background-color: #1e293b; color: white; padding: 5px; border: 1px solid #334155; border-radius: 4px; }
"""

# --- Giao diện TỐI ---
DARK = """
/* Nền chính và các thành phần cơ bản */
QMainWindow { background: #0f172a; color: #e2e8f0; }
QStatusBar { background:#0f172a; border-top:1px solid #1e293b; color:#94a3b8; font-size:12px; }

/* Header */
QFrame#headerFrame { background:#1e293b; border-bottom:1px solid #334155; }
QLabel#headerTitle { color:#f8fafc; font-size:22px; font-weight:bold; padding:8px 0; }
QLabel#headerSubtitle { color:#94a3b8; font-size:12px; padding-bottom:8px; }

/* Nút bấm */
QPushButton { background:#1e293b; color:#e2e8f0; border:1px solid #334155; border-radius:8px; padding:10px 16px; font-weight:600; }
QPushButton:hover { background:#334155; }
QPushButton#primary { background:#3b82f6; color:white; border:none; font-weight:700; }
QPushButton#primary:hover { background:#2563eb; }

/* GroupBox */
QGroupBox { font-weight:600; font-size:13px; color:#cbd5e1; background:#1e293b; border:1px solid #334155; border-radius:10px; margin:12px 0; padding-top:20px; }
QGroupBox::title { subcontrol-origin: margin; left:12px; top:8px; padding:0 8px; background:#1e293b; }

/* Ô nhập liệu */
QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox { background:#0f172a; color: #e2e8f0; border:2px solid #334155; border-radius:6px; padding:8px 12px; }
QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus { border-color: #3b82f6; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background-color: #1e293b; color: #e2e8f0; selection-background-color: #3b82f6; }

/* Trạng thái cảnh báo cho ô nhập liệu */
QLineEdit[state="warning"], QDoubleSpinBox[state="warning"], QSpinBox[state="warning"], QComboBox[state="warning"] { border-color: #f59e0b; }
QLineEdit[state="error"], QDoubleSpinBox[state="error"], QSpinBox[state="error"], QComboBox[state="error"] { border-color: #ef4444; }

/* Tabs và Bảng */
QTabWidget::pane { border:1px solid #334155; background:#1e293b; border-radius:8px; }
QTabBar::tab { background: #0f172a; color: #94a3b8; padding: 10px; border-top-left-radius: 6px; border-top-right-radius: 6px; border: 1px solid #334155; border-bottom: none; margin-right: 2px;}
QTabBar::tab:selected { background: #1e293b; color: #f8fafc; font-weight: bold; border-bottom: 1px solid #1e293b;}
QTableWidget { background:#1e293b; border:1px solid #334155; border-radius:8px; gridline-color: #334155; }
QHeaderView::section { background-color: #1e293b; color: #e2e8f0; padding: 4px; border: 1px solid #334155; }

/* Thẻ thống kê */
QFrame#card { background:#1e293b; border:1px solid #334155; border-radius:12px; padding:12px; }
QFrame#card[status="success"] { border-left:4px solid #10b981; }
QFrame#card[status="warning"] { border-left:4px solid #f59e0b; }
QFrame#card[status="danger"]  { border-left:4px solid #ef4444; }
QLabel#cardTitle { color:#94a3b8; font-size:11px; font-weight:600; }
QLabel#cardValue { color:#f8fafc; font-size:24px; font-weight:bold; }
QLabel#cardSubtitle { color:#94a3b8; font-size:11px; }

/* Tooltip */
QToolTip { background-color: #f8fafc; color: #1e293b; padding: 5px; border: 1px solid #cbd5e1; border-radius: 4px; }
"""
