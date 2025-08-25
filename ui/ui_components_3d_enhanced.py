# title="ui/ui_components_3d_enhanced.py" contentType="text/python"
# -*- coding: utf-8 -*-
"""
UI components nâng cấp: Panel nhập liệu + Panel kết quả (2D/3D).
- Gán tooltip theo PDF qua ui/tooltips.py
- Thêm hình minh họa góc máng (trough) và góc chất tải (surcharge)
- Thêm tab hiển thị kết quả tính toán Puly và Con lăn.
- Bổ sung tùy chọn và hiển thị kết quả cho truyền động kép.
"""

from __future__ import annotations

import os
from PySide6.QtCore import Qt, QByteArray, Signal, Slot, QTimer, QThread
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QComboBox,
    QDoubleSpinBox, QSpinBox, QLineEdit, QPushButton, QScrollArea, QFrame,
    QTableWidget, QTableWidgetItem, QTextEdit, QTabWidget, QProgressBar, QLabel,
    QCheckBox, QStackedWidget, QSlider, QGridLayout, QMessageBox
)
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtGui import QPixmap, QFont

# 2D plotting
from .plotting import EnhancedPlotCanvas

# 3D visualization (không làm app sập nếu thiếu WebEngine)
HAS_3D_SUPPORT = False
try:
    from .visualization_3d import Visualization3DWidget  # type: ignore
    from .visualization_3d.enhanced_widget import EnhancedVisualization3DWidget  # type: ignore
    HAS_3D_SUPPORT = True
except Exception:
    Visualization3DWidget = None  # type: ignore
    EnhancedVisualization3DWidget = None  # type: ignore

# >>> import tooltips
try:
    from .tooltips import apply_tooltips
except Exception:
    apply_tooltips = None  # type: ignore


# ==========================
# TÀI NGUYÊN MINH HỌA DRIVE
# ==========================

DRIVE_SVG_DATA = {
    "head drive": """
    <svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
      <style>
        .drive { fill: #3b82f6; } .neutral { fill: #94a3b8; }
        .belt { fill: none; stroke: #475569; stroke-width: 2; }
        .text { font-family: sans-serif; font-size: 9px; fill: #3b82f6; font-weight: bold; }
      </style>
      <path class="belt" d="M 25 40 L 175 40 A 10 10 0 0 1 175 60 L 25 60 A 10 10 0 0 1 25 40 Z" />
      <circle class="drive" cx="175" cy="50" r="10"/>
      <circle class="neutral" cx="25" cy="50" r="10"/>
      <text x="140" y="30" class="text">ĐỘNG CƠ</text>
    </svg>
    """,
    "tail drive": """
    <svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
      <style>
        .drive { fill: #3b82f6; } .neutral { fill: #94a3b8; }
        .belt { fill: none; stroke: #475569; stroke-width: 2; }
        .text { font-family: sans-serif; font-size: 9px; fill: #3b82f6; font-weight: bold; }
      </style>
      <path class="belt" d="M 25 40 L 175 40 A 10 10 0 0 1 175 60 L 25 60 A 10 10 0 0 1 25 40 Z" />
      <circle class="neutral" cx="175" cy="50" r="10"/>
      <circle class="drive" cx="25" cy="50" r="10"/>
      <text x="35" y="30" class="text">ĐỘNG CƠ</text>
    </svg>
    """,
    "center drive": """
    <svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
      <style>
        .drive { fill: #3b82f6; } .neutral { fill: #94a3b8; }
        .belt { fill: none; stroke: #475569; stroke-width: 2; }
        .text { font-family: sans-serif; font-size: 9px; fill: #3b82f6; font-weight: bold; }
      </style>
      <path class="belt" d="M 25 40 L 175 40 A 10 10 0 0 1 175 60 L 120 60 L 120 80 L 80 80 L 80 60 L 25 60 A 10 10 0 0 1 25 40 Z" />
      <circle class="neutral" cx="175" cy="50" r="10"/>
      <circle class="neutral" cx="25" cy="50" r="10"/>
      <circle class="drive" cx="100" cy="85" r="10"/>
      <text x="90" y="98" class="text">ĐỘNG CƠ</text>
    </svg>
    """,
    "dual drive": """
    <svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
      <style>
        .drive { fill: #3b82f6; } .neutral { fill: #94a3b8; }
        .belt { fill: none; stroke: #475569; stroke-width: 2; }
        .text { font-family: sans-serif; font-size: 9px; fill: #3b82f6; font-weight: bold; }
      </style>
      <path class="belt" d="M 25 40 L 175 40 A 10 10 0 0 1 175 60 L 150 60 L 150 80 L 120 80 L 120 60 L 25 60 A 10 10 0 0 1 25 40 Z" />
      <circle class="drive" cx="175" cy="50" r="10"/>
      <circle class="drive" cx="135" cy="85" r="10"/>
      <circle class="neutral" cx="25" cy="50" r="10"/>
      <text x="118" y="30" class="text">ĐỘNG CƠ KÉP</text>
    </svg>
    """,
}

DRIVE_DESCRIPTIONS = {
    "head drive": "Truyền động đầu: động cơ ở đầu ra, kéo nhánh mang tải. Phổ biến nhất.",
    "tail drive": "Truyền động đuôi: động cơ ở đầu vào, đẩy nhánh mang tải. Ít phổ biến.",
    "center drive": "Truyền động trung tâm: đặt ở nhánh về, hay dùng cho băng đảo chiều.",
    "dual drive": "Truyền động kép: hai động cơ chia tải cho băng dài hoặc tải nặng."
}


# ==========================
# INPUTS PANEL
# ==========================

class InputsPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # --- [BẮT ĐẦU NÂNG CẤP UI] ---
        # Cải thiện giao diện tổng thể của input panel
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
            QScrollArea {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: #ffffff;
            }
            QFormLayout {
                spacing: 8px;
            }
            QLabel {
                color: #374151;
                font-weight: 500;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 6px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                background-color: #ffffff;
                color: #374151;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QCheckBox {
                color: #374151;
                font-weight: 500;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #d1d5db;
                background-color: #ffffff;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #3b82f6;
                background-color: #3b82f6;
                border-radius: 3px;
            }
            /* Cải thiện giao diện nút */
            QPushButton {
                background-color: #ffffff;
                color: #374151;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
                min-height: 50px;
                min-width: 120px;
                margin: 5px;
                display: block;
                visibility: visible;
                opacity: 1;
            }
            QPushButton:hover {
                background-color: #f8fafc;
                border-color: #9ca3af;
            }
            QPushButton:pressed {
                background-color: #e5e7eb;
                border-color: #6b7280;
            }
            QPushButton#primary {
                background-color: #3b82f6;
                color: white;
                border-color: #3b82f6;
                font-weight: 700;
            }
            QPushButton#primary:hover {
                background-color: #2563eb;
                border-color: #2563eb;
            }
            QPushButton#primary:pressed {
                background-color: #1d4ed8;
                border-color: #1d4ed8;
            }
        """)
        # --- [KẾT THÚC NÂNG CẤP UI] ---

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        v = QVBoxLayout(container)

        self._create_widgets()

        if apply_tooltips:
            try:
                apply_tooltips(self)
            except Exception:
                pass

        v.addWidget(self._project_group())
        v.addWidget(self._material_group())
        v.addWidget(self._operating_group())
        v.addWidget(self._belt_group())
        v.addWidget(self._drive_group())
        v.addWidget(self._env_group())
        # --- [BẮT ĐẦU NÂNG CẤP TỐI ƯU HÓA] ---
        v.addWidget(self._optimizer_settings_group())
        # --- [KẾT THÚC NÂNG CẤP TỐI ƯU HÓA] ---
        v.addStretch(1)
        scroll.setWidget(container)

        main_layout.addWidget(scroll)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)  # Thêm khoảng cách giữa các nút
        btn_row.setContentsMargins(10, 10, 10, 10)  # Thêm margin cho layout
        
        self.btn_calc = QPushButton("TÍNH TOÁN\nCHI TIẾT")
        self.btn_calc.setObjectName("primary")
        self.btn_calc.setMinimumHeight(50)  # Đảm bảo nút có chiều cao tối thiểu
        self.btn_calc.setStyleSheet("""
            QPushButton#primary {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #049b94, stop:1 #037d77);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                text-align: center;
                white-space: pre-line;
            }
            QPushButton#primary:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #05a89f, stop:1 #048a82);
            }
            QPushButton#primary:pressed {
                background-color: #024e4a;
            }
        """)
        
        self.btn_quick = QPushButton("TÍNH TOÁN\nNHANH")
        self.btn_quick.setMinimumHeight(50)  # Đảm bảo nút có chiều cao tối thiểu
        self.btn_quick.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #374151;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
                min-height: 50px;
                min-width: 140px;
                margin: 5px;
                text-align: center;
                white-space: pre-line;
            }
            QPushButton:hover {
                background-color: #f8fafc;
                border-color: #9ca3af;
            }
            QPushButton:pressed {
                background-color: #e5e7eb;
                border-color: #6b7280;
            }
        """)
        
        self.btn_opt = QPushButton("TỐI ƯU\nNÂNG CAO") # Đổi tên nút
        self.btn_opt.setMinimumHeight(50)  # Đảm bảo nút có chiều cao tối thiểu
        self.btn_opt.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #374151;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
                min-height: 50px;
                min-width: 140px;
                margin: 5px;
                text-align: center;
                white-space: pre-line;
            }
            QPushButton:hover {
                background-color: #f8fafc;
                border-color: #9ca3af;
            }
            QPushButton:pressed {
                background-color: #e5e7eb;
                border-color: #6b7280;
            }
        """)
        
        btn_row.addWidget(self.btn_calc, 2)
        btn_row.addWidget(self.btn_quick, 1)
        btn_row.addWidget(self.btn_opt, 1)
        
        # Thêm CSS cho container chứa nút để đảm bảo hiển thị
        btn_container = QWidget()
        btn_container.setLayout(btn_row)
        btn_container.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px;
                margin: 10px;
            }
            QPushButton {
                background-color: #ffffff;
                color: #374151;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
                min-height: 50px;
                min-width: 120px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #f8fafc;
                border-color: #9ca3af;
            }
            QPushButton:pressed {
                background-color: #e5e7eb;
                border-color: #6b7280;
            }
            QPushButton#primary {
                background-color: #3b82f6;
                color: white;
                border-color: #3b82f6;
                font-weight: 700;
            }
            QPushButton#primary:hover {
                background-color: #2563eb;
                border-color: #2563eb;
            }
            QPushButton#primary:pressed {
                background-color: #1d4ed8;
                border-color: #1d4ed8;
            }
        """)
        main_layout.addWidget(btn_container)

        self.cbo_drive.currentTextChanged.connect(self.update_drive_illustration)
        self.update_drive_illustration(self.cbo_drive.currentText())

    def _create_widgets(self) -> None:
        # Project
        self.edt_project_name = QLineEdit("Thiết kế băng tải nhà máy ABC")
        self.edt_designer = QLineEdit("Kỹ sư thiết kế")
        self.edt_client = QLineEdit("Khách hàng")
        self.edt_location = QLineEdit("Công trình")

        # Material
        self.cbo_material = QComboBox()
        self.spn_density = QDoubleSpinBox(); self.spn_density.setRange(0.1, 10.0); self.spn_density.setDecimals(3); self.spn_density.setValue(1.6); self.spn_density.setSuffix(" tấn/m³")
        self.spn_particle = QDoubleSpinBox(); self.spn_particle.setRange(0.1, 500); self.spn_particle.setValue(25); self.spn_particle.setSuffix(" mm")
        self.spn_angle = QDoubleSpinBox(); self.spn_angle.setRange(10, 50); self.spn_angle.setValue(35); self.spn_angle.setSuffix(" °")
        self.spn_temp = QDoubleSpinBox(); self.spn_temp.setRange(-40, 200); self.spn_temp.setValue(20); self.spn_temp.setSuffix(" °C")
        self.chk_abrasive = QCheckBox("Vật liệu mài mòn")
        self.chk_corrosive = QCheckBox("Vật liệu ăn mòn")
        self.chk_dusty = QCheckBox("Vật liệu bụi")

        # Operating
        self.cbo_standard = QComboBox(); self.cbo_standard.addItems(["CEMA", "DIN 22101", "ISO 5048"])
        self.spn_capacity = QDoubleSpinBox(); self.spn_capacity.setRange(1, 10000); self.spn_capacity.setValue(250); self.spn_capacity.setSuffix(" tấn/giờ")
        self.spn_length = QDoubleSpinBox(); self.spn_length.setRange(1, 5000); self.spn_length.setValue(120); self.spn_length.setSuffix(" m")
        self.spn_height = QDoubleSpinBox(); self.spn_height.setRange(-100, 500); self.spn_height.setValue(25); self.spn_height.setSuffix(" m")
        self.spn_incl = QDoubleSpinBox(); self.spn_incl.setRange(-30, 30); self.spn_incl.setValue(0); self.spn_incl.setSuffix(" °")
        # Tốc độ băng giờ đây được tính tự động - không cần nhập tay
        self.lbl_speed_info = QLabel("🚀 Tốc độ băng sẽ được tính tự động dựa trên lưu lượng và bề rộng")
        self.lbl_speed_info.setStyleSheet("color: #059669; font-style: italic; padding: 8px; background-color: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 4px;")
        self.lbl_speed_info.setWordWrap(True)
        self.spn_hours = QSpinBox(); self.spn_hours.setRange(1, 24); self.spn_hours.setValue(16); self.spn_hours.setSuffix(" giờ/ngày")

        # Belt
        self.cbo_width = QComboBox()
        self.cbo_belt_type = QComboBox()
        self.spn_thickness = QDoubleSpinBox(); self.spn_thickness.setRange(5, 50); self.spn_thickness.setValue(12); self.spn_thickness.setSuffix(" mm")
        self.cbo_trough = QComboBox(); self.cbo_trough.addItems(["0° (phẳng)","10°","15°","20°","25°","30°","35°","40°","45°"])
        self.spn_surcharge = QDoubleSpinBox(); self.spn_surcharge.setRange(10, 45); self.spn_surcharge.setValue(20); self.spn_surcharge.setDecimals(1); self.spn_surcharge.setSuffix(" °")
        self.spn_carrying = QDoubleSpinBox(); self.spn_carrying.setRange(0.5, 3.0); self.spn_carrying.setValue(1.2); self.spn_carrying.setSuffix(" m")
        self.spn_return = QDoubleSpinBox(); self.spn_return.setRange(1.0, 6.0); self.spn_return.setValue(3.0); self.spn_return.setSuffix(" m")

        # Drive
        self.cbo_drive = QComboBox(); self.cbo_drive.addItems(["Head drive", "Tail drive", "Center drive", "Dual drive"])
        # --- [BẮT ĐẦU NÂNG CẤP] ---
        self.cbo_dual_drive_ratio = QComboBox()
        self.cbo_dual_drive_ratio.addItems(["Phân phối lý thuyết", "Phân phối đều (50/50)", "Phân phối 2/1 (66/33)"])
        # --- [KẾT THÚC NÂNG CẤP] ---
        
        # --- [BẮT ĐẦU NÂNG CẤP TRUYỀN ĐỘNG] ---
        # Tốc độ động cơ
        self.cbo_motor_rpm = QComboBox()
        self.cbo_motor_rpm.addItems(["1450", "2900", "750", "1000", "1500", "1800", "2200", "3000"])
        self.cbo_motor_rpm.setCurrentText("1450")
        self.cbo_motor_rpm.setObjectName("motor_rpm_input")
        # --- [KẾT THÚC NÂNG CẤP TRUYỀN ĐỘNG] ---
        
        # --- [BẮT ĐẦU NÂNG CẤP HỘP SỐ MANUAL] ---
        # Chế độ chọn tỉ số hộp số
        self.cbo_gearbox_ratio_mode = QComboBox()
        self.cbo_gearbox_ratio_mode.addItems(["Tự động tính toán", "Chỉ định"])
        self.cbo_gearbox_ratio_mode.setCurrentText("Tự động tính toán")
        self.cbo_gearbox_ratio_mode.setObjectName("gearbox_ratio_mode_select")
        
        # Tỉ số hộp số do người dùng nhập
        self.spn_gearbox_ratio_user = QDoubleSpinBox()
        self.spn_gearbox_ratio_user.setRange(1.0, 100.0)
        self.spn_gearbox_ratio_user.setDecimals(1)
        self.spn_gearbox_ratio_user.setValue(12.5)
        self.spn_gearbox_ratio_user.setSuffix("")
        self.spn_gearbox_ratio_user.setObjectName("gearbox_ratio_input")
        self.spn_gearbox_ratio_user.setEnabled(False)  # Mặc định disable khi Auto
        self.spn_gearbox_ratio_user.setToolTip("Chuyển chế độ hộp số sang Chỉ định, nếu i=1/10 thì nhập vào 10")
        
        # Kết nối signal để enable/disable input
        self.cbo_gearbox_ratio_mode.currentTextChanged.connect(self._on_gearbox_mode_changed)
        # --- [KẾT THÚC NÂNG CẤP HỘP SỐ MANUAL] ---
        
        self.spn_eta_m = QDoubleSpinBox(); self.spn_eta_m.setRange(0.8, 0.98); self.spn_eta_m.setDecimals(3); self.spn_eta_m.setValue(0.95)
        self.spn_eta_g = QDoubleSpinBox(); self.spn_eta_g.setRange(0.85, 0.98); self.spn_eta_g.setDecimals(3); self.spn_eta_g.setValue(0.96)
        self.spn_mu = QDoubleSpinBox(); self.spn_mu.setRange(0.2, 0.8); self.spn_mu.setDecimals(3); self.spn_mu.setValue(0.35)
        self.spn_wrap = QDoubleSpinBox(); self.spn_wrap.setRange(120, 240); self.spn_wrap.setDecimals(1); self.spn_wrap.setValue(210); self.spn_wrap.setSuffix(" °")
        self.spn_Kt = QDoubleSpinBox(); self.spn_Kt.setRange(1.1, 2.0); self.spn_Kt.setDecimals(2); self.spn_Kt.setValue(1.25)

        self.drive_image_widget = QSvgWidget()
        self.drive_image_widget.setMinimumSize(150, 120)
        self.drive_desc_label = QLabel()
        self.drive_desc_label.setWordWrap(True)
        self.drive_desc_label.setStyleSheet("font-style: italic; padding: 5px;")

        # Environment
        self.spn_amb = QDoubleSpinBox(); self.spn_amb.setRange(-40, 60); self.spn_amb.setValue(25); self.spn_amb.setSuffix(" °C")
        self.spn_hum = QDoubleSpinBox(); self.spn_hum.setRange(0, 100); self.spn_hum.setValue(65); self.spn_hum.setSuffix(" %")
        self.spn_alt = QDoubleSpinBox(); self.spn_alt.setRange(0, 5000); self.spn_alt.setValue(0); self.spn_alt.setSuffix(" m")
        self.chk_dusty_env = QCheckBox("Môi trường bụi bặm")
        self.chk_corr_env = QCheckBox("Môi trường ăn mòn")
        self.chk_ex = QCheckBox("Yêu cầu chống nổ")

        # --- [BẮT ĐẦU NÂNG CẤP TỐI ƯU HÓA] ---
        self.opt_group = QGroupBox("Cài đặt Tối ưu hóa Nâng cao")
        # Hủy bỏ nút tick chọn - tính năng này mặc định luôn được Bật
        # self.opt_group.setCheckable(True)
        # self.opt_group.setChecked(False) # Mặc định tắt

        self.slider_cost_safety = QSlider(Qt.Horizontal)
        self.slider_cost_safety.setRange(0, 100)
        self.slider_cost_safety.setValue(60) # Mặc định 60% Cost, 40% Safety

        self.slider_power_speed = QSlider(Qt.Horizontal)
        self.slider_power_speed.setRange(0, 100)
        self.slider_power_speed.setValue(30) # Mặc định 30% Power, 70% Speed

        self.spn_max_budget = QDoubleSpinBox()
        self.spn_max_budget.setRange(0, 1_000_000_000)
        self.spn_max_budget.setDecimals(0)
        self.spn_max_budget.setSuffix(" $")
        self.spn_max_budget.setGroupSeparatorShown(True)


        self.spn_min_safety_factor = QDoubleSpinBox()
        self.spn_min_safety_factor.setRange(1.0, 20.0)
        self.spn_min_safety_factor.setDecimals(1)
        self.spn_min_safety_factor.setValue(8.0)
        # --- [KẾT THÚC NÂNG CẤP TỐI ƯU HÓA] ---

    def _project_group(self) -> QGroupBox:
        g = QGroupBox("Thông tin dự án")
        f = QFormLayout(g)
        f.addRow("Tên dự án:", self.edt_project_name)
        f.addRow("Người thiết kế:", self.edt_designer)
        f.addRow("Khách hàng:", self.edt_client)
        f.addRow("Công trình:", self.edt_location)
        return g

    def _material_group(self) -> QGroupBox:
        g = QGroupBox("Lựa chọn vật liệu & đặc tính")
        f = QFormLayout(g)
        f.addRow("Loại vật liệu:", self.cbo_material)
        
        # Thêm label hiển thị thông tin vật liệu
        self.lbl_material_info = QLabel("Chọn vật liệu để xem thông tin")
        self.lbl_material_info.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        f.addRow("Thông tin:", self.lbl_material_info)
        
        f.addRow("Khối lượng riêng:", self.spn_density)
        f.addRow("Kích thước hạt:", self.spn_particle)
        f.addRow("Góc nghiêng tự nhiên:", self.spn_angle)
        f.addRow("Nhiệt độ vật liệu:", self.spn_temp)
        box = QHBoxLayout()
        box.addWidget(self.chk_abrasive); box.addWidget(self.chk_corrosive); box.addWidget(self.chk_dusty); box.addStretch(1)
        f.addRow("Đặc tính:", box)
        return g

    def _operating_group(self) -> QGroupBox:
        g = QGroupBox("Điều kiện vận hành")
        f = QFormLayout(g)
        f.addRow("Tiêu chuẩn:", self.cbo_standard)
        f.addRow("Lưu lượng yêu cầu:", self.spn_capacity)
        f.addRow("Chiều dài:", self.spn_length)
        f.addRow("Độ cao nâng:", self.spn_height)
        f.addRow("Góc nghiêng:", self.spn_incl)
        f.addRow(self.lbl_speed_info)
        f.addRow("Giờ vận hành/ngày:", self.spn_hours)
        return g

    def _img_path(self, filename: str) -> str:
        try:
            from core.utils.paths import resource_path
            return resource_path(f"ui/images/{filename}")
        except Exception:
            return filename

    def _belt_group(self) -> QGroupBox:
        g = QGroupBox("Cấu hình băng")
        f = QFormLayout(g)
        f.addRow("Bề rộng băng:", self.cbo_width)
        f.addRow("Loại băng:", self.cbo_belt_type)
        f.addRow("Độ dày băng:", self.spn_thickness)
        f.addRow("Góc máng:", self.cbo_trough)
        # f.addRow("Góc chất tải:", self.spn_surcharge)  # Ẩn góc chất tải - luôn bằng góc nghiêng tự nhiên
        f.addRow("KC con lăn tải:", self.spn_carrying)
        f.addRow("KC con lăn về:", self.spn_return)

        self.img_trough = QLabel()
        self.img_trough.setObjectName("imgTrough")
        self.img_trough.setToolTip("Minh họa góc máng: ba con lăn tạo lòng máng.")
        p_trough = QPixmap(self._img_path("trough_angle.png"))
        if not p_trough.isNull():
            self.img_trough.setPixmap(p_trough.scaledToHeight(120, Qt.SmoothTransformation))
        else:
            self.img_trough.setText("Hình góc máng đang cập nhật")

        # Ẩn hình minh họa góc chất tải
        # self.img_surcharge = QLabel()
        # self.img_surcharge.setObjectName("imgSurcharge")
        # self.img_surcharge.setToolTip("Minh họa góc chất tải (surcharge).")
        # p_surcharge = QPixmap(self._img_path("surcharge_angle.png"))
        # if not p_surcharge.isNull():
        #     self.img_surcharge.setPixmap(p_surcharge.scaledToHeight(120, Qt.SmoothTransformation))
        # else:
        #     self.img_surcharge.setText("Hình góc chất tải đang cập nhật")

        # img_row = QHBoxLayout()
        # img_row.addWidget(self.img_trough, 1)
        # img_row.addWidget(self.img_surcharge, 1)

        # img_wrap = QWidget()
        # img_wrap.setLayout(img_row)
        # f.addRow("Minh họa:", img_wrap)

        # Chỉ hiển thị hình góc máng
        f.addRow("Minh họa:", self.img_trough)

        return g

    def _drive_group(self) -> QGroupBox:
        g = QGroupBox("Hệ thống truyền động")
        f = QFormLayout(g)
        f.addRow("Loại truyền động:", self.cbo_drive)
        # --- [BẮT ĐẦU NÂNG CẤP] ---
        # Tạo một widget để chứa combobox và nhãn, giúp ẩn/hiện dễ dàng
        self.dual_drive_ratio_widget = QWidget()
        ratio_layout = QFormLayout(self.dual_drive_ratio_widget)
        ratio_layout.setContentsMargins(0, 0, 0, 0)
        ratio_layout.addRow("Tỷ lệ phân phối lực:", self.cbo_dual_drive_ratio)
        self.dual_drive_ratio_widget.setVisible(False) # Ẩn mặc định
        f.addRow(self.dual_drive_ratio_widget)
        # --- [KẾT THÚC NÂNG CẤP] ---
        
        # --- [BẮT ĐẦU NÂNG CẤP TRUYỀN ĐỘNG] ---
        f.addRow("Tốc độ động cơ:", self.cbo_motor_rpm)
        # --- [KẾT THÚC NÂNG CẤP TRUYỀN ĐỘNG] ---
        
        # --- [BẮT ĐẦU NÂNG CẤP HỘP SỐ MANUAL] ---
        f.addRow("Chế độ hộp số:", self.cbo_gearbox_ratio_mode)
        f.addRow("Tỉ số hộp số:", self.spn_gearbox_ratio_user)
        # --- [KẾT THÚC NÂNG CẤP HỘP SỐ MANUAL] ---
        
        f.addRow("Hiệu suất động cơ:", self.spn_eta_m)
        f.addRow("Hiệu suất hộp số:", self.spn_eta_g)
        f.addRow("HS ma sát băng-tang:", self.spn_mu)
        f.addRow("Góc ôm tang:", self.spn_wrap)
        f.addRow("Hệ số khởi động:", self.spn_Kt)

        v = QVBoxLayout()
        v.addWidget(self.drive_image_widget)
        v.addWidget(self.drive_desc_label)
        f.addRow(v)
        return g

    def _env_group(self) -> QGroupBox:
        g = QGroupBox("Điều kiện môi trường")
        f = QFormLayout(g)
        f.addRow("Nhiệt độ môi trường:", self.spn_amb)
        f.addRow("Độ ẩm:", self.spn_hum)
        f.addRow("Độ cao:", self.spn_alt)
        box = QHBoxLayout()
        box.addWidget(self.chk_dusty_env); box.addWidget(self.chk_corr_env); box.addWidget(self.chk_ex); box.addStretch(1)
        f.addRow("Điều kiện đặc biệt:", box)
        return g

    # --- [BẮT ĐẦU NÂNG CẤP TỐI ƯU HÓA] ---
    def _optimizer_settings_group(self) -> QGroupBox:
        f = QFormLayout(self.opt_group)

        # Thêm label thông báo trạng thái tối ưu hóa
        self.lbl_optimization_status = QLabel("Tính năng tối ưu hóa nâng cao đã sẵn sàng")
        self.lbl_optimization_status.setStyleSheet("""
            QLabel {
                color: #059669;
                font-weight: 600;
                font-size: 14px;
                padding: 10px;
                background-color: #d1fae5;
                border: 1px solid #10b981;
                border-radius: 6px;
                text-align: center;
                margin: 5px 0px;
            }
        """)
        self.lbl_optimization_status.setAlignment(Qt.AlignCenter)
        f.addRow(self.lbl_optimization_status)

        # Sliders for weights
        slider_layout = QFormLayout()
        
        cost_safety_label = QLabel("Chi phí Thấp nhất<br><b style='color:#3b82f6;'>vs</b><br>Bền nhất")
        cost_safety_label.setWordWrap(True)
        cost_safety_label.setToolTip("Kéo về bên trái để ưu tiên chi phí, kéo về bên phải để ưu tiên độ bền và hệ số an toàn cao.")
        slider_layout.addRow(cost_safety_label, self.slider_cost_safety)

        power_speed_label = QLabel("Tiết kiệm Năng lượng<br><b style='color:#3b82f6;'>vs</b><br>Nhanh nhất")
        power_speed_label.setWordWrap(True)
        power_speed_label.setToolTip("Kéo về bên trái để ưu tiên động cơ công suất nhỏ, kéo về bên phải để ưu tiên tốc độ băng tải cao.")
        slider_layout.addRow(power_speed_label, self.slider_power_speed)
        
        f.addRow("Mục tiêu của bạn là gì?", slider_layout)

        # Constraints
        constraints_group = QGroupBox("Ràng buộc (Tùy chọn)")
        constraints_layout = QFormLayout(constraints_group)
        constraints_layout.addRow("Ngân sách tối đa ($):", self.spn_max_budget)
        constraints_layout.addRow("HS An toàn băng >=", self.spn_min_safety_factor)
        
        f.addRow(constraints_group)

        return self.opt_group
    # --- [KẾT THÚC NÂNG CẤP TỐI ƯU HÓA] ---

    @Slot(str)
    def update_drive_illustration(self, drive_type_text: str) -> None:
        sel = (drive_type_text or "").strip().lower()
        if sel not in DRIVE_SVG_DATA:
            sel = "head drive"
        svg = DRIVE_SVG_DATA[sel]
        desc = DRIVE_DESCRIPTIONS.get(sel, "")
        self.drive_image_widget.load(QByteArray(svg.encode("utf-8")))
        self.drive_desc_label.setText(desc)

        # --- [BẮT ĐẦU NÂNG CẤP] ---
        # Hiển thị hoặc ẩn tùy chọn phân phối lực dựa trên loại truyền động
        is_dual = "dual drive" in sel
        self.dual_drive_ratio_widget.setVisible(is_dual)
        # --- [KẾT THÚC NÂNG CẤP] ---

    # --- [BẮT ĐẦU NÂNG CẤP HỘP SỐ MANUAL] ---
    @Slot(str)
    def _on_gearbox_mode_changed(self, mode_text: str) -> None:
        """Xử lý sự kiện thay đổi chế độ hộp số"""
        is_manual = mode_text.strip().lower() == "chỉ định"
        self.spn_gearbox_ratio_user.setEnabled(is_manual)
        
        # Nếu chuyển về Auto, reset giá trị về 0
        if not is_manual:
            self.spn_gearbox_ratio_user.setValue(0.0)
    # --- [KẾT THÚC NÂNG CẤP HỘP SỐ MANUAL] ---


# ==========================
# THẺ THỐNG KÊ NHANH
# ==========================

class CardsRow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        lay = QHBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0)
        self.card_speed = QFrame(); self.card_speed.setObjectName("card")
        self.card_power = QFrame(); self.card_power.setObjectName("card")
        self.card_eff = QFrame(); self.card_eff.setObjectName("card")
        self.card_sf = QFrame(); self.card_sf.setObjectName("card")
        self.card_cost = QFrame(); self.card_cost.setObjectName("card")
        for c, title, sub in [
            (self.card_speed, "TỐC ĐỘ BĂNG TẢI", "m/s"),
            (self.card_power, "CÔNG SUẤT ĐỘNG CƠ", "kW tại trục"),
            (self.card_eff, "HIỆU SUẤT HỆ THỐNG", "Phần trăm"),
            (self.card_sf, "HỆ SỐ AN TOÀN", "SF hiện tại"),
            (self.card_cost, "CHI PHÍ ĐẦU TƯ (CAPEX)", "USD (Ước tính)"),
        ]:
            v = QVBoxLayout(c)
            t = QLabel(title); t.setObjectName("cardTitle"); t.setAlignment(Qt.AlignCenter)
            val = QLabel("---"); val.setObjectName("cardValue"); val.setAlignment(Qt.AlignCenter)
            subl = QLabel(sub); subl.setObjectName("cardSubtitle"); subl.setAlignment(Qt.AlignCenter)
            v.addWidget(t); v.addWidget(val, 1); v.addWidget(subl)
            c.setProperty("status", "success")
            lay.addWidget(c)


# ==========================
# RESULTS PANEL (2D + 3D)
# ==========================

class Enhanced3DResultsPanel(QWidget):
    optimizer_result_selected = Signal(object) # Signal to emit DesignCandidate

    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)

        # --- [BẮT ĐẦU NÂNG CẤP UI] ---
        # Cải thiện giao diện tổng thể của results panel
        self.setStyleSheet("""
            QWidget {
                background-color: #f8fafc; /* Màu nền chung */
            }
            QLabel#tabTitle {
                font-size: 16px;
                font-weight: bold;
                color: #1e3a8a; /* Xanh đậm */
                padding: 5px 0px;
                margin-bottom: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                background-color: #ffffff;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #f1f5f9;
                color: #475569;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3b82f6;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #60a5fa;
                color: #ffffff;
            }
            QTableWidget {
                gridline-color: #e5e7eb;
                background-color: #ffffff;
                alternate-background-color: #f9fafb; /* Màu xen kẽ nhạt hơn */
                selection-background-color: #dbeafe; /* Xanh nhạt khi chọn */
                selection-color: #1e3a8a;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f1f5f9; /* Màu header nhạt */
                color: #1e3a8a;
                padding: 10px;
                border: none;
                font-weight: bold;
                border-bottom: 2px solid #3b82f6;
            }
            QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                background-color: #ffffff;
                color: #374151;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }
            QProgressBar {
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                background-color: #f1f5f9;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 3px;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px 0 5px;
                color: #1e3a8a;
            }
            /* Style cho các label hiển thị giá trị trong tab cấu trúc */
            QLabel.valueLabel {
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                font-weight: bold;
                color: #1d4ed8; /* Xanh đậm hơn */
                padding: 6px;
                background-color: #eff6ff;
                border-radius: 4px;
                border: 1px solid #dbeafe;
                min-width: 80px;
                qproperty-alignment: 'AlignCenter';
            }
            /* Style cho các label tiêu đề trong tab cấu trúc */
            QLabel.labelTitle {
                font-weight: 500;
                color: #374151;
            }
        """)
        # --- [KẾT THÚC NÂNG CẤP UI] ---

        self.cards = CardsRow()
        root.addWidget(self.cards)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)

        # --- [BẮT ĐẦU NÂNG CẤP TỐI ƯU HÓA]
        # Tab Kết quả Tối ưu
        w_opt = QWidget()
        l_opt = QVBoxLayout(w_opt)
        self.tbl_optimizer_results = QTableWidget()
        self.tbl_optimizer_results.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_optimizer_results.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_optimizer_results.setAlternatingRowColors(True)
        self.tbl_optimizer_results.doubleClicked.connect(self._on_optimizer_result_selected)
        l_opt.addWidget(self.tbl_optimizer_results)
        self.tabs.insertTab(0, w_opt, "🏆 Kết quả Tối ưu")
        self._optimizer_results_data = [] # To store the list of DesignCandidate
        # --- [KẾT THÚC NÂNG CẤP TỐI ƯU HÓA]

        # Tab Tổng quan
        w_over = QWidget()
        lo = QVBoxLayout(w_over)
        # --- [BẮT ĐẦU NÂNG CẤP UI] ---
        title_overview = QLabel("Bảng thông số chi tiết")
        title_overview.setObjectName("tabTitle")
        lo.addWidget(title_overview)
        # --- [KẾT THÚC NÂNG CẤP UI] ---
        self.tbl = QTableWidget(); self.tbl.setColumnCount(2)
        self.tbl.setHorizontalHeaderLabels(["Thông số", "Giá trị"])
        self.tbl.horizontalHeader().setStretchLastSection(True)
        lo.addWidget(self.tbl)
        self.tabs.addTab(w_over, "📊 Tổng quan")

        # Tab Cấu trúc (Puly & Con lăn)
        w_struct = QWidget()
        l_struct = QVBoxLayout(w_struct)
        l_struct.setSpacing(15)
        
        # --- [BẮT ĐẦU NÂNG CẤP UI] ---
        g_pulleys = QGroupBox("⚙️ Đề xuất Puly")
        l_pulleys = QVBoxLayout(g_pulleys)
        self.tbl_pulleys = QTableWidget()
        self.tbl_pulleys.setColumnCount(2)
        self.tbl_pulleys.setHorizontalHeaderLabels(["Loại Puly", "Đường kính đề xuất (mm)"])
        self.tbl_pulleys.horizontalHeader().setStretchLastSection(True)
        l_pulleys.addWidget(self.tbl_pulleys)
        
        g_idlers = QGroupBox("📏 Đề xuất Con lăn & Khoảng cách")
        f_idlers = QFormLayout(g_idlers)
        f_idlers.setRowWrapPolicy(QFormLayout.WrapAllRows)
        self.lbl_spacing_carry = QLabel("---"); self.lbl_spacing_carry.setObjectName("valueLabel")
        self.lbl_spacing_return = QLabel("---"); self.lbl_spacing_return.setObjectName("valueLabel")
        self.lbl_transition_dist = QLabel("---"); self.lbl_transition_dist.setObjectName("valueLabel")
        f_idlers.addRow(QLabel("Khoảng cách con lăn nhánh tải:", objectName="labelTitle"), self.lbl_spacing_carry)
        f_idlers.addRow(QLabel("Khoảng cách con lăn nhánh về:", objectName="labelTitle"), self.lbl_spacing_return)
        f_idlers.addRow(QLabel("Khoảng cách chuyển tiếp (tối thiểu):", objectName="labelTitle"), self.lbl_transition_dist)
        

        
        g_transmission = QGroupBox("🔗 Bộ truyền động hoàn chỉnh")
        grid_transmission = QGridLayout(g_transmission)
        grid_transmission.setSpacing(12)
        
        self.lbl_gearbox_mode = QLabel("---"); self.lbl_gearbox_mode.setObjectName("valueLabel")
        self.lbl_gearbox_ratio_used = QLabel("---"); self.lbl_gearbox_ratio_used.setObjectName("valueLabel")
        self.lbl_motor_output_rpm = QLabel("---"); self.lbl_motor_output_rpm.setObjectName("valueLabel")
        self.lbl_motor_output_rpm.setToolTip(
            "<b>Tốc độ đầu ra động cơ (vòng/phút)</b><br>"
            "Tốc độ quay của trục đầu ra động cơ sau khi qua hộp số giảm tốc.<br><br>"
            "<u>Công thức tính:</u> Tốc độ đầu ra = Tốc độ động cơ ÷ Tỉ số hộp số"
        )
        self.lbl_gearbox_ratio = QLabel("---"); self.lbl_gearbox_ratio.setObjectName("valueLabel")
        self.lbl_chain_designation = QLabel("---"); self.lbl_chain_designation.setObjectName("valueLabel")
        self.lbl_sprocket_teeth = QLabel("---"); self.lbl_sprocket_teeth.setObjectName("valueLabel")
        self.lbl_actual_velocity = QLabel("---"); self.lbl_actual_velocity.setObjectName("valueLabel")
        self.lbl_velocity_error = QLabel("---"); self.lbl_velocity_error.setObjectName("valueLabel")
        self.lbl_total_ratio = QLabel("---"); self.lbl_total_ratio.setObjectName("valueLabel")
        self.lbl_required_force = QLabel("---"); self.lbl_required_force.setObjectName("valueLabel")
        self.lbl_allowable_force = QLabel("---"); self.lbl_allowable_force.setObjectName("valueLabel")
        self.lbl_safety_margin = QLabel("---"); self.lbl_safety_margin.setObjectName("valueLabel")
        self.lbl_chain_weight = QLabel("---"); self.lbl_chain_weight.setObjectName("valueLabel")

        # Bố cục lưới cho dễ nhìn
        grid_transmission.addWidget(QLabel("Tốc độ ra động cơ (rpm):", objectName="labelTitle"), 0, 0)
        grid_transmission.addWidget(self.lbl_motor_output_rpm, 0, 1)
        grid_transmission.addWidget(QLabel("Mã xích (ANSI/ISO):", objectName="labelTitle"), 0, 2)
        grid_transmission.addWidget(self.lbl_chain_designation, 0, 3)

        grid_transmission.addWidget(QLabel("Số răng nhông (Dẫn/Bị dẫn):", objectName="labelTitle"), 1, 0)
        grid_transmission.addWidget(self.lbl_sprocket_teeth, 1, 1)
        grid_transmission.addWidget(QLabel("Vận tốc băng thực tế (m/s):", objectName="labelTitle"), 1, 2)
        grid_transmission.addWidget(self.lbl_actual_velocity, 1, 3)

        grid_transmission.addWidget(QLabel("Sai số vận tốc (%):", objectName="labelTitle"), 2, 0)
        grid_transmission.addWidget(self.lbl_velocity_error, 2, 1)
        grid_transmission.addWidget(QLabel("Hệ số an toàn xích:", objectName="labelTitle"), 2, 2)
        grid_transmission.addWidget(self.lbl_safety_margin, 2, 3)
        
        grid_transmission.addWidget(QLabel("Lực kéo yêu cầu (kN):", objectName="labelTitle"), 3, 0)
        grid_transmission.addWidget(self.lbl_required_force, 3, 1)
        grid_transmission.addWidget(QLabel("Lực kéo cho phép (kN):", objectName="labelTitle"), 3, 2)
        grid_transmission.addWidget(self.lbl_allowable_force, 3, 3)
        
        grid_transmission.setColumnStretch(1, 1)
        grid_transmission.setColumnStretch(3, 1)

        l_struct.addWidget(g_pulleys)
        l_struct.addWidget(g_idlers)
        l_struct.addWidget(g_transmission)
        l_struct.addStretch(1)
        # --- [KẾT THÚC NÂNG CẤP UI] ---
        self.tabs.addTab(w_struct, "🏗️ Cấu trúc đề xuất")

        # Tab Phân tích
        w_ana = QWidget(); la = QVBoxLayout(w_ana)
        self.txt_analysis = QTextEdit(); self.txt_analysis.setReadOnly(True)
        la.addWidget(self.txt_analysis)
        self.tabs.addTab(w_ana, "🔬 Phân tích Kỹ thuật")

        # Tab Chi phí
        w_cost = QWidget(); lc = QVBoxLayout(w_cost)
        self.txt_cost_analysis = QTextEdit(); self.txt_cost_analysis.setReadOnly(True)
        lc.addWidget(self.txt_cost_analysis)
        self.tabs.addTab(w_cost, "💰 Phân tích Chi phí")



        # Tab Visualization
        w_viz = QWidget(); viz_layout = QVBoxLayout(w_viz)
        sel_box = QGroupBox("Chế độ hiển thị")
        sel_lay = QHBoxLayout(sel_box)
        self.btn_2d_mode = QPushButton("📈 Biểu đồ 2D")
        self.btn_3d_mode = QPushButton("🏗️ Mô hình 3D")
        self.btn_2d_mode.setCheckable(True); self.btn_3d_mode.setCheckable(True)
        self.btn_2d_mode.setChecked(True)
        if not HAS_3D_SUPPORT:
            self.btn_3d_mode.setEnabled(False)
            self.btn_3d_mode.setToolTip("Cần PySide6-WebEngine để xem 3D.")
        sel_lay.addWidget(self.btn_2d_mode); sel_lay.addWidget(self.btn_3d_mode); sel_lay.addStretch(1)
        viz_layout.addWidget(sel_box)

        self.viz_stack = QStackedWidget()
        self.w_2d = QWidget(); l2d = QVBoxLayout(self.w_2d)
        
        # --- [BẮT ĐẦU CẢI THIỆN GIAO DIỆN CHECKBOX] ---
        controls_2d = QGroupBox("Tùy chọn biểu đồ 2D")
        controls_2d.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 13px;
                color: #374151;
                border: 2px solid #e5e7eb;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f9fafb;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: #f9fafb;
                color: #1f2937;
            }
        """)
        
        c_lay = QHBoxLayout(controls_2d)
        c_lay.setSpacing(15)
        c_lay.setContentsMargins(20, 25, 20, 20)
        
        # Tạo các checkbox với giao diện cải tiến
        self.chk_t2 = QCheckBox("🔵 Lực căng T2")
        self.chk_friction = QCheckBox("🟡 Lực ma sát") 
        self.chk_lift = QCheckBox("🟠 Lực nâng")
        
        # Thiết lập trạng thái mặc định
        self.chk_t2.setChecked(True)
        self.chk_friction.setChecked(True)
        self.chk_lift.setChecked(True)
        
        # Thêm tooltip giải thích
        self.chk_t2.setToolTip("Hiển thị lực căng ban đầu T2 dọc theo băng tải")
        self.chk_friction.setToolTip("Hiển thị lực ma sát giữa băng tải và con lăn")
        self.chk_lift.setToolTip("Hiển thị lực nâng vật liệu theo độ cao")
        
        # CSS styling cho checkbox
        checkbox_style = """
            QCheckBox {
                font-size: 13px;
                font-weight: 500;
                color: #374151;
                spacing: 8px;
                padding: 8px 12px;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                background-color: #ffffff;
                min-width: 120px;
                min-height: 35px;
            }
            QCheckBox:hover {
                border-color: #9ca3af;
                background-color: #f8fafc;
            }
            QCheckBox:checked {
                border-color: #3b82f6;
                background-color: #eff6ff;
                color: #1e40af;
            }
            QCheckBox:checked:hover {
                border-color: #2563eb;
                background-color: #dbeafe;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #d1d5db;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                border-color: #3b82f6;
                background-color: #3b82f6;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
            QCheckBox::indicator:unchecked:hover {
                border-color: #9ca3af;
            }
        """
        
        self.chk_t2.setStyleSheet(checkbox_style)
        self.chk_friction.setStyleSheet(checkbox_style)
        self.chk_lift.setStyleSheet(checkbox_style)
        
        # Thêm các checkbox vào layout với spacing tốt hơn
        c_lay.addWidget(self.chk_t2)
        c_lay.addWidget(self.chk_friction)
        c_lay.addWidget(self.chk_lift)
        c_lay.addStretch(1)
        
        # Thêm nút "Hiển thị tất cả" và "Ẩn tất cả"
        btn_show_all = QPushButton("👁️ Hiển thị tất cả")
        btn_hide_all = QPushButton("🙈 Ẩn tất cả")
        
        btn_show_all.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 12px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        
        btn_hide_all.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 12px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
            QPushButton:pressed {
                background-color: #374151;
            }
        """)
        
        # Kết nối các nút với chức năng
        btn_show_all.clicked.connect(self._show_all_charts)
        btn_hide_all.clicked.connect(self._hide_all_charts)
        
        c_lay.addWidget(btn_show_all)
        c_lay.addWidget(btn_hide_all)
        # --- [KẾT THÚC CẢI THIỆN GIAO DIỆN CHECKBOX] ---
        
        self.canvas = EnhancedPlotCanvas()
        l2d.addWidget(controls_2d); l2d.addWidget(self.canvas)

        if HAS_3D_SUPPORT:
            # Sử dụng EnhancedVisualization3DWidget nâng cao
            try:
                print("DEBUG: Đang tạo EnhancedVisualization3DWidget...")
                self.viz_3d = EnhancedVisualization3DWidget()
                print("DEBUG: Đã tạo EnhancedVisualization3DWidget thành công")
                
                # Đảm bảo widget 3D hiển thị nội dung mặc định
                self._initialize_3d_widget_content()
                
                # Kết nối signals để cập nhật visualization khi có dữ liệu mới
                if hasattr(self.viz_3d, 'visualization_updated'):
                    self.viz_3d.visualization_updated.connect(self._on_3d_visualization_updated)
                
            except Exception as e:
                print(f"DEBUG: Không thể tạo EnhancedVisualization3DWidget: {e}")
                print(f"DEBUG: Exception type: {type(e)}")
                import traceback
                traceback.print_exc()
                # Fallback về widget cũ
                try:
                    print("DEBUG: Đang thử tạo Visualization3DWidget...")
                    self.viz_3d = Visualization3DWidget()
                    print("DEBUG: Đã tạo Visualization3DWidget thành công")
                    
                    # Đảm bảo widget 3D hiển thị nội dung mặc định
                    self._initialize_3d_widget_content()
                    
                except Exception as e2:
                    print(f"DEBUG: Không thể tạo Visualization3DWidget: {e2}")
                    self.viz_3d = QWidget()
                    ph = QVBoxLayout(self.viz_3d)
                    lab = QLabel("3D Visualization không khả dụng.\n\nCài đặt: pip install PySide6 PySide6-WebEngine")
                    lab.setAlignment(Qt.AlignCenter); lab.setStyleSheet("color:#64748b; font-size:14px; padding:50px;")
                    ph.addWidget(lab)
        else:
            print("DEBUG: HAS_3D_SUPPORT = False")
            self.viz_3d = QWidget()
            ph = QVBoxLayout(self.viz_3d)
            lab = QLabel("3D Visualization không khả dụng.\n\nCài đặt: pip install PySide6 PySide6-WebEngine")
            lab.setAlignment(Qt.AlignCenter); lab.setStyleSheet("color:#64748b; font-size:14px; padding:50px;")
            ph.addWidget(lab)

        self.viz_stack.addWidget(self.w_2d)
        self.viz_stack.addWidget(self.viz_3d)
        viz_layout.addWidget(self.viz_stack, 1)
        self.tabs.addTab(w_viz, "🛰️ Visualization")

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        root.addWidget(self.progress)

        self.btn_2d_mode.clicked.connect(lambda: self._switch_mode(0))
        self.btn_3d_mode.clicked.connect(lambda: self._switch_mode(1))
        
        self._current_params = None
        self._current_result = None
        self._current_theme = "light"

    def _initialize_3d_widget_content(self):
        """Khởi tạo nội dung mặc định cho widget 3D"""
        try:
            if hasattr(self.viz_3d, 'setHtml'):
                # Nếu là WebEngine, hiển thị HTML mặc định
                default_html = """
                <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin: 0; min-height: 100vh;">
                    <div style="background: rgba(255,255,255,0.1); border-radius: 20px; padding: 40px; backdrop-filter: blur(10px); max-width: 800px; margin: 0 auto;">
                        <h1 style="font-size: 32px; margin-bottom: 20px;">🏗️ Mô hình 3D Băng tải</h1>
                        <p style="font-size: 18px; margin-bottom: 30px;">Chào mừng bạn đến với hệ thống visualization 3D nâng cao!</p>
                        
                        <div style="background: rgba(255,255,255,0.2); border-radius: 15px; padding: 25px; margin: 20px 0;">
                            <h3 style="color: #fbbf24; margin-bottom: 15px;">🚀 Để bắt đầu:</h3>
                            <ol style="text-align: left; font-size: 16px; line-height: 1.8;">
                                <li>Nhập thông số băng tải (chiều dài, bề rộng, lưu lượng...)</li>
                                <li>Chọn vật liệu và loại băng phù hợp</li>
                                <li>Nhấn nút "Tính toán" hoặc "Tính nhanh"</li>
                                <li>Xem kết quả và click "Mô hình 3D" để xem visualization</li>
                            </ol>
                        </div>
                        
                        <div style="background: rgba(255,255,255,0.2); border-radius: 15px; padding: 25px; margin: 20px 0;">
                            <h3 style="color: #34d399; margin-bottom: 15px;">✨ Tính năng nâng cao:</h3>
                            <ul style="text-align: left; font-size: 16px; line-height: 1.8;">
                                <li>Mô hình 3D chi tiết với các thành phần cơ khí</li>
                                <li>Animation chuyển động thực tế</li>
                                <li>Phân tích vật lý và kỹ thuật</li>
                                <li>Giao diện tương tác trực quan</li>
                            </ul>
                        </div>
                        
                        <button onclick="showDemo()" style="background: linear-gradient(45deg, #3b82f6, #1d4ed8); color: white; border: none; padding: 15px 30px; font-size: 16px; font-weight: bold; border-radius: 25px; cursor: pointer; margin-top: 20px; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); transition: all 0.3s ease;">
                            🎮 Xem Demo 3D
                        </button>
                        
                        <div id="demo-container" style="display: none; margin-top: 30px;">
                            <div style="background: rgba(0,0,0,0.8); border-radius: 15px; padding: 20px;">
                                <h3 style="color: #fbbf24;">🎮 Demo 3D Băng tải</h3>
                                <p style="color: #e5e7eb;">Đây là demo mẫu. Để xem mô hình thực tế, hãy chạy tính toán!</p>
                                <div id="three-container" style="width: 100%; height: 400px; background: #1f2937; border-radius: 10px; margin: 15px 0;"></div>
                            </div>
                        </div>
                    </div>
                    
                    <script>
                    function showDemo() {
                        const container = document.getElementById('demo-container');
                        const threeContainer = document.getElementById('three-container');
                        
                        if (container.style.display === 'none') {
                            container.style.display = 'block';
                            
                            // Tạo demo 3D đơn giản với Three.js
                            try {
                                // Kiểm tra xem Three.js đã được load chưa
                                if (typeof THREE === 'undefined') {
                                    // Load Three.js từ CDN nếu chưa có
                                    const script = document.createElement('script');
                                    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
                                    script.onload = function() {
                                        createThreeDemo();
                                    };
                                    document.head.appendChild(script);
                                } else {
                                    createThreeDemo();
                                }
                            } catch (e) {
                                console.log('Three.js not available, showing simple demo');
                                showSimpleDemo();
                            }
                        } else {
                            container.style.display = 'none';
                        }
                    }
                    
                    function createThreeDemo() {
                        const threeContainer = document.getElementById('three-container');
                        
                        // Tạo scene
                        const scene = new THREE.Scene();
                        scene.background = new THREE.Color(0x1f2937);
                        
                        // Tạo camera
                        const camera = new THREE.PerspectiveCamera(75, threeContainer.clientWidth / threeContainer.clientHeight, 0.1, 1000);
                        camera.position.set(0, 5, 10);
                        
                        // Tạo renderer
                        const renderer = new THREE.WebGLRenderer({ antialias: true });
                        renderer.setSize(threeContainer.clientWidth, threeContainer.clientHeight);
                        renderer.shadowMap.enabled = true;
                        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                        
                        // Xóa nội dung cũ
                        threeContainer.innerHTML = '';
                        threeContainer.appendChild(renderer.domElement);
                        
                        // Tạo băng tải
                        const beltGeometry = new THREE.BoxGeometry(8, 0.3, 1.5);
                        const beltMaterial = new THREE.MeshLambertMaterial({ color: 0x10b981 });
                        const belt = new THREE.Mesh(beltGeometry, beltMaterial);
                        belt.position.y = 0.15;
                        belt.castShadow = true;
                        scene.add(belt);
                        
                        // Tạo con lăn
                        const idlerGeometry = new THREE.CylinderGeometry(0.4, 0.4, 1.8, 8);
                        const idlerMaterial = new THREE.MeshLambertMaterial({ color: 0x6b7280 });
                        
                        const idler1 = new THREE.Mesh(idlerGeometry, idlerMaterial);
                        idler1.position.set(-3, -0.2, 0);
                        idler1.rotation.z = Math.PI / 2;
                        idler1.castShadow = true;
                        scene.add(idler1);
                        
                        const idler2 = new THREE.Mesh(idlerGeometry, idlerMaterial);
                        idler2.position.set(3, -0.2, 0);
                        idler2.rotation.z = Math.PI / 2;
                        idler2.castShadow = true;
                        scene.add(idler2);
                        
                        // Tạo khung đỡ
                        const frameGeometry = new THREE.BoxGeometry(0.1, 0.8, 2);
                        const frameMaterial = new THREE.MeshLambertMaterial({ color: 0x374151 });
                        
                        for (let i = -3; i <= 3; i += 1.5) {
                            const frame = new THREE.Mesh(frameGeometry, frameMaterial);
                            frame.position.set(i, -0.4, 0);
                            frame.castShadow = true;
                            scene.add(frame);
                        }
                        
                        // Tạo lighting
                        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
                        scene.add(ambientLight);
                        
                        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                        directionalLight.position.set(5, 10, 5);
                        directionalLight.castShadow = true;
                        directionalLight.shadow.mapSize.width = 1024;
                        directionalLight.shadow.mapSize.height = 1024;
                        scene.add(directionalLight);
                        
                        // Animation
                        let time = 0;
                        function animate() {
                            requestAnimationFrame(animate);
                            
                            time += 0.02;
                            
                            // Xoay con lăn
                            idler1.rotation.x += 0.05;
                            idler2.rotation.x += 0.05;
                            
                            // Xoay camera
                            camera.position.x = Math.sin(time * 0.5) * 10;
                            camera.position.z = Math.cos(time * 0.5) * 10;
                            camera.lookAt(0, 0, 0);
                            
                            renderer.render(scene, camera);
                        }
                        animate();
                        
                        // Xử lý resize
                        window.addEventListener('resize', function() {
                            camera.aspect = threeContainer.clientWidth / threeContainer.clientHeight;
                            camera.updateProjectionMatrix();
                            renderer.setSize(threeContainer.clientWidth, threeContainer.clientHeight);
                        });
                    }
                    
                    function showSimpleDemo() {
                        const threeContainer = document.getElementById('three-container');
                        threeContainer.innerHTML = '<div style="color: white; padding: 50px; text-align: center;"><h4>🎮 Demo 3D</h4><p>Three.js không khả dụng. Hãy cài đặt PySide6-WebEngine để xem demo 3D đầy đủ!</p></div>';
                    }
                    </script>
                </body>
                </html>
                """
                self.viz_3d.setHtml(default_html)
            elif hasattr(self.viz_3d, 'setLayout'):
                # Nếu là QWidget thông thường
                default_widget = QWidget()
                default_layout = QVBoxLayout(default_widget)
                
                title_label = QLabel("🏗️ Mô hình 3D Băng tải")
                title_label.setStyleSheet("""
                    QLabel {
                        color: #1f2937;
                        font-size: 24px;
                        font-weight: bold;
                        padding: 30px;
                        text-align: center;
                    }
                """)
                default_layout.addWidget(title_label)
                
                info_label = QLabel("Chào mừng bạn đến với hệ thống visualization 3D nâng cao!")
                info_label.setStyleSheet("""
                    QLabel {
                        color: #6b7280;
                        font-size: 16px;
                        padding: 20px;
                        text-align: center;
                    }
                """)
                default_layout.addWidget(info_label)
                
                steps_label = QLabel("🚀 Để bắt đầu:\n1. Nhập thông số băng tải\n2. Chọn vật liệu và loại băng\n3. Nhấn 'Tính toán' hoặc 'Tính nhanh'\n4. Xem kết quả và click 'Mô hình 3D'")
                steps_label.setStyleSheet("""
                    QLabel {
                        color: #059669;
                        font-size: 14px;
                        padding: 25px;
                        text-align: center;
                        background-color: #d1fae5;
                        border: 1px solid #10b981;
                        border-radius: 12px;
                        margin: 20px;
                    }
                """)
                steps_label.setWordWrap(True)
                default_layout.addWidget(steps_label)
                
                self.viz_3d.setLayout(default_layout)
            else:
                print("DEBUG: viz_3d không hỗ trợ setHtml hoặc setLayout")
                
        except Exception as e:
            print(f"DEBUG: Không thể khởi tạo nội dung mặc định cho widget 3D: {e}")
            # Fallback: hiển thị thông báo đơn giản
            try:
                if hasattr(self.viz_3d, 'setText'):
                    self.viz_3d.setText("🏗️ Mô hình 3D\n\nĐể xem mô hình 3D, hãy chạy tính toán trước!")
                elif hasattr(self.viz_3d, 'setHtml'):
                    self.viz_3d.setHtml("<h2>🏗️ Mô hình 3D</h2><p>Để xem mô hình 3D, hãy chạy tính toán trước!</p>")
            except Exception as e2:
                print(f"DEBUG: Không thể hiển thị fallback content: {e2}")

    # --- [BẮT ĐẦU NÂNG CẤP TỐI ƯU HÓA]
    def update_optimizer_results(self, results: list):
        """Hiển thị kết quả từ optimizer vào bảng."""
        self._optimizer_results_data = results
        self.tbl_optimizer_results.clear()
        
        headers = ["Rank", "Điểm Fitness", "Bề rộng (mm)", "Tốc độ tính (m/s)", "Loại băng", "Tổng chi phí ($)", "Công suất (kW)", "HS An toàn Băng", "HS An toàn Xích"]
        self.tbl_optimizer_results.setColumnCount(len(headers))
        self.tbl_optimizer_results.setHorizontalHeaderLabels(headers)
        self.tbl_optimizer_results.setRowCount(len(results))

        for i, candidate in enumerate(results):
            res = candidate.calculation_result
            trans = getattr(res, 'transmission_solution', None)

            self.tbl_optimizer_results.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.tbl_optimizer_results.setItem(i, 1, QTableWidgetItem(f"{candidate.fitness_score:.4f}"))
            self.tbl_optimizer_results.setItem(i, 2, QTableWidgetItem(str(candidate.belt_width_mm)))
            belt_speed = getattr(res, 'belt_speed_mps', 0.0)
            self.tbl_optimizer_results.setItem(i, 3, QTableWidgetItem(f"{belt_speed:.2f}"))
            self.tbl_optimizer_results.setItem(i, 4, QTableWidgetItem(candidate.belt_type_name))
            self.tbl_optimizer_results.setItem(i, 5, QTableWidgetItem(f"{getattr(res, 'cost_capital_total', 0):,.0f}"))
            self.tbl_optimizer_results.setItem(i, 6, QTableWidgetItem(f"{getattr(res, 'required_power_kw', 0):.2f}"))
            self.tbl_optimizer_results.setItem(i, 7, QTableWidgetItem(f"{getattr(res, 'safety_factor', 0):.2f}"))
            self.tbl_optimizer_results.setItem(i, 8, QTableWidgetItem(f"{getattr(trans, 'safety_margin', 0):.2f}" if trans else "N/A"))

        self.tbl_optimizer_results.resizeColumnsToContents()
        self.tabs.setCurrentIndex(0) # Chuyển sang tab kết quả tối ưu

    @Slot()
    def _on_optimizer_result_selected(self, model_index):
        """Xử lý khi người dùng double-click vào một kết quả."""
        selected_row = model_index.row()
        if 0 <= selected_row < len(self._optimizer_results_data):
            selected_candidate = self._optimizer_results_data[selected_row]
            self.optimizer_result_selected.emit(selected_candidate)
    # --- [KẾT THÚC NÂNG CẤP TỐI ƯU HÓA] ---

    def update_visualizations(self, params, result, theme: str = "light") -> None:
        self._current_params = params
        self._current_result = result
        self._current_theme = theme

        self._update_structural_tab(result)
        self._update_analysis_tab(result)

        plot_opts = {
            "show_t2": self.chk_t2.isChecked(),
            "show_friction": self.chk_friction.isChecked(),
            "show_lift": self.chk_lift.isChecked(),
        }
        try:
            self.canvas.plot_from_result(params, result, plot_opts, theme)
        except Exception:
            pass

        # Cập nhật visualization 3D nâng cao nếu có
        if HAS_3D_SUPPORT and hasattr(self.viz_3d, "update_enhanced_visualization"):
            try:
                print("DEBUG: Cập nhật enhanced visualization 3D...")
                self.viz_3d.update_enhanced_visualization(params, result)
                print("✅ Đã cập nhật Enhanced 3D Visualization thành công")
                
                # Hiển thị thông báo thành công nếu đang ở chế độ 3D
                if self.viz_stack.currentIndex() == 1:
                    self._show_3d_success_message("Mô hình 3D đã được cập nhật với dữ liệu mới!")
                    
            except Exception as e:
                print(f"❌ Lỗi cập nhật enhanced visualization: {e}")
                if self.viz_stack.currentIndex() == 1:
                    self._show_3d_error_message(f"Lỗi khi cập nhật mô hình 3D: {e}")
        
        # Fallback: cập nhật visualization 3D cơ bản nếu có
        elif HAS_3D_SUPPORT and hasattr(self.viz_3d, "update_visualization"):
            try:
                print("DEBUG: Cập nhật basic visualization 3D...")
                self.viz_3d.update_visualization(params, result, theme=theme)
                print("✅ Đã cập nhật Basic 3D Visualization thành công")
                
                # Hiển thị thông báo thành công nếu đang ở chế độ 3D
                if self.viz_stack.currentIndex() == 1:
                    self._show_3d_success_message("Mô hình 3D cơ bản đã được cập nhật!")
                    
            except Exception as e:
                print(f"❌ Lỗi cập nhật basic visualization: {e}")
                if self.viz_stack.currentIndex() == 1:
                    self._show_3d_error_message(f"Lỗi khi cập nhật mô hình 3D cơ bản: {e}")
        
        else:
            print("DEBUG: Không có method update visualization nào khả dụng")

    def _update_structural_tab(self, result) -> None:
        """Cập nhật tab 'Cấu trúc đề xuất' với dữ liệu từ kết quả tính toán."""
        if not result:
            return

        # Cập nhật bảng Puly
        self.tbl_pulleys.setRowCount(0)
        drum_diameter = getattr(result, 'drum_diameter_mm', 500)
        pulleys = {
            "Puly chủ động": drum_diameter,
            "Puly bị động": drum_diameter,
            "Puly đổi hướng": drum_diameter * 0.75,
            "Puly căng": drum_diameter * 0.75,
        }
        self.tbl_pulleys.setRowCount(len(pulleys))
        for i, (name, diameter) in enumerate(pulleys.items()):
            self.tbl_pulleys.setItem(i, 0, QTableWidgetItem(name))
            self.tbl_pulleys.setItem(i, 1, QTableWidgetItem(f"{diameter:.0f}"))

        # Cập nhật thông tin con lăn
        recommended_spacing = getattr(result, 'recommended_idler_spacing_m', {})
        transition_distance = getattr(result, 'transition_distance_m', 0.0)
        
        self.lbl_spacing_carry.setText(f"{recommended_spacing.get('Nhánh tải (đề xuất)', 0.0):.2f} m")
        self.lbl_spacing_return.setText(f"{recommended_spacing.get('Nhánh về (đề xuất)', 0.0):.2f} m")
        self.lbl_transition_dist.setText(f"{transition_distance:.2f} m (tối thiểu)")
        


        # Cập nhật thông tin bộ truyền động
        trans = getattr(result, 'transmission_solution', None)
        if trans:
            # --- [BẮT ĐẦU SỬA LỖI] ---
            # Sử dụng đúng tên thuộc tính từ TransmissionSolution
            self.lbl_gearbox_mode.setText(getattr(trans, 'gearbox_ratio_mode', 'N/A'))
            self.lbl_gearbox_ratio_used.setText(f"{getattr(trans, 'gearbox_ratio', 0):.2f}")
            # Lấy tốc độ đầu ra động cơ từ transmission_solution
            # Công thức: Tốc độ đầu ra = Tốc độ động cơ ÷ Tỉ số hộp số
            motor_output_rpm = getattr(trans, 'motor_output_rpm', 0)
            if motor_output_rpm > 0:
                self.lbl_motor_output_rpm.setText(f"{motor_output_rpm:.0f} RPM")
            else:
                # Fallback: tính toán từ motor_rpm và gearbox_ratio
                motor_rpm = getattr(result, 'motor_rpm', 1450)
                gearbox_ratio = getattr(trans, 'gearbox_ratio', 1)
                motor_output_rpm = motor_rpm / gearbox_ratio
                self.lbl_motor_output_rpm.setText(f"{motor_output_rpm:.0f} RPM")
            self.lbl_gearbox_ratio.setText(f"{getattr(trans, 'gearbox_ratio', 0):.2f}")
            # --- [BẮT ĐẦU NÂNG CẤP HIỂN THỊ MÃ XÍCH] ---
            # Hiển thị mã xích với cả ANSI và ISO theo định dạng rõ ràng
            chain_designation = getattr(trans, 'chain_designation', 'N/A')
            if chain_designation != 'N/A':
                # Tách mã xích ANSI và ISO nếu có
                if '/' in chain_designation and chain_designation.endswith(' (ANSI/ISO)'):
                    # Xử lý format mới: "25/05B (ANSI/ISO)"
                    ansi_part, iso_part = chain_designation.split('/', 1)
                    iso_part = iso_part.replace(' (ANSI/ISO)', '')
                    self.lbl_chain_designation.setText(f"<b>{ansi_part}/{iso_part}</b> <span style='color: #6b7280;'>(ANSI/ISO)</span>")
                elif chain_designation.endswith(' (ANSI)'):
                    # Xử lý format mới: "25 (ANSI)"
                    ansi_part = chain_designation.replace(' (ANSI)', '')
                    self.lbl_chain_designation.setText(f"<b>{ansi_part}</b> <span style='color: #6b7280;'>(ANSI)</span>")
                elif chain_designation.endswith(' (ISO)'):
                    # Xử lý format mới: "05B (ISO)"
                    iso_part = chain_designation.replace(' (ISO)', '')
                    self.lbl_chain_designation.setText(f"<b>{iso_part}</b> <span style='color: #6b7280;'>(ISO)</span>")
                elif '/' in chain_designation:
                    # Xử lý format cũ: "25/05B" (để tương thích ngược)
                    ansi_part, iso_part = chain_designation.split('/', 1)
                    self.lbl_chain_designation.setText(f"<b>{ansi_part}/{iso_part}</b> <span style='color: #6b7280;'>(ANSI/ISO)</span>")
                else:
                    # Nếu chỉ có một loại, hiển thị rõ ràng với tiêu chuẩn
                    # Kiểm tra xem có phải là ANSI hay ISO dựa trên format
                    if any(char.isdigit() and char in '0123456789' for char in chain_designation):
                        if 'A' in chain_designation or 'B' in chain_designation:
                            self.lbl_chain_designation.setText(f"<b>{chain_designation}</b> <span style='color: #6b7280;'>(ANSI)</span>")
                        else:
                            self.lbl_chain_designation.setText(f"<b>{chain_designation}</b> <span style='color: #6b7280;'>(ISO)</span>")
                    else:
                        self.lbl_chain_designation.setText(f"<b>{chain_designation}</b>")
            else:
                self.lbl_chain_designation.setText("N/A")
            # --- [KẾT THÚC NÂNG CẤP HIỂN THỊ MÃ XÍCH] ---
            # --- [BẮT ĐẦU NÂNG CẤP UI] ---
            # Gộp số răng nhông dẫn và bị dẫn thành một hàng
            self.lbl_sprocket_teeth.setText(f"{getattr(trans, 'drive_sprocket_teeth', 0)}/{getattr(trans, 'driven_sprocket_teeth', 0)}")
            # --- [KẾT THÚC NÂNG CẤP UI] ---
            self.lbl_actual_velocity.setText(f"{getattr(trans, 'actual_velocity_mps', 0):.3f}")
            self.lbl_velocity_error.setText(f"{getattr(trans, 'velocity_error_percent', 0):.2f} %")
            self.lbl_total_ratio.setText(f"{getattr(trans, 'total_transmission_ratio', 0):.2f}")
            self.lbl_required_force.setText(f"{getattr(trans, 'required_force_kN', 0):.2f} kN")
            self.lbl_allowable_force.setText(f"{getattr(trans, 'allowable_force_kN', 0):.2f} kN")
            self.lbl_safety_margin.setText(f"{getattr(trans, 'safety_margin', 0):.2f}")
            self.lbl_chain_weight.setText(f"{getattr(trans, 'chain_weight_kg_per_m', 0):.2f} kg/m")
            # --- [KẾT THÚC SỬA LỖI] ---
        else:
            # --- [BẮT ĐẦU SỬA LỖI] ---
            # Hiển thị thông tin cơ bản ngay cả khi không có transmission_solution
            # Công thức: Tốc độ đầu ra = Tốc độ động cơ ÷ Tỉ số hộp số
            motor_rpm = getattr(result, 'motor_rpm', 1450)
            gearbox_ratio = getattr(result, 'gearbox_ratio', 1)
            motor_output_rpm = motor_rpm / gearbox_ratio
            self.lbl_motor_output_rpm.setText(f"{motor_output_rpm:.0f} RPM")
            # --- [KẾT THÚC SỬA LỖI] ---
            
            # Clear labels if no transmission solution
            for label in [
                self.lbl_gearbox_mode, self.lbl_gearbox_ratio_used,
                self.lbl_gearbox_ratio, self.lbl_chain_designation, self.lbl_sprocket_teeth,
                self.lbl_actual_velocity, self.lbl_velocity_error,
                self.lbl_total_ratio, self.lbl_required_force, self.lbl_allowable_force,
                self.lbl_safety_margin, self.lbl_chain_weight
            ]:
                label.setText("---")

    def _update_analysis_tab(self, result) -> None:
        """Cập nhật tab 'Phân tích' với dữ liệu từ kết quả tính toán."""
        if not result:
            self.txt_analysis.setHtml("")
            return

        eff = getattr(result, "drive_efficiency_percent", getattr(result, "efficiency", 0.0))
        belt_utilization = getattr(result, "belt_strength_utilization", 0.0)
        capacity_utilization = getattr(result, "capacity_utilization", 0.0)
        
        ana_report_html = "<h3>PHÂN TÍCH KỸ THUẬT</h3>"
        
        # Thêm thông tin tốc độ băng
        belt_speed = getattr(result, 'belt_speed_mps', 0.0)
        belt_width = getattr(result, 'belt_width_mm', 0)
        
        ana_report_html += f"<p><b>- Tốc độ băng tính toán:</b> {belt_speed:.2f} m/s</p>"
        ana_report_html += f"<p><b>- Bề rộng băng được chọn:</b> {belt_width:.0f} mm</p>"
        
        ana_report_html += f"<p><b>- Hiệu suất truyền động:</b> {eff:.1f}% (η_m × η_g ÷ Kt)</p>"
        ana_report_html += f"<p><b>- Phần trăm sử dụng cường độ đai:</b> {belt_utilization:.1f}%</p>"
        ana_report_html += f"<p><b>- Phần trăm sử dụng tiết diện (ước tính):</b> {capacity_utilization:.1f}%</p>"
        
        warnings = getattr(result, 'warnings', [])
        if warnings:
            ana_report_html += "<h4 style='color: #f59e0b;'>CẢNH BÁO:</h4><ul>"
            for w in warnings:
                ana_report_html += f"<li>{w}</li>"
            ana_report_html += "</ul>"
            
        recommendations = getattr(result, 'recommendations', [])
        if recommendations:
            ana_report_html += "<h4 style='color: #22c55e;'>KHUYẾN NGHỊ:</h4><ul>"
            for rec in recommendations:
                ana_report_html += f"<li>{rec}</li>"
            ana_report_html += "</ul>"
            
        self.txt_analysis.setHtml(ana_report_html)

    @Slot(int)
    def _switch_mode(self, index: int) -> None:
        """Chuyển đổi giữa chế độ xem 2D và 3D."""
        print(f"DEBUG: _switch_mode được gọi với index={index}")
        print(f"DEBUG: viz_stack có {self.viz_stack.count()} widgets")
        print(f"DEBUG: viz_3d type: {type(self.viz_3d)}")
        print(f"DEBUG: viz_3d có update_enhanced_visualization: {hasattr(self.viz_3d, 'update_enhanced_visualization')}")
        
        self.viz_stack.setCurrentIndex(index)
        self.btn_2d_mode.setChecked(index == 0)
        self.btn_3d_mode.setChecked(index == 1)
        
        print(f"DEBUG: Đã chuyển sang index {index}, current index: {self.viz_stack.currentIndex()}")
        
        # Nếu chuyển sang 3D và có dữ liệu hiện tại, cập nhật visualization
        if index == 1:
            if hasattr(self, '_current_params') and hasattr(self, '_current_result') and self._current_params and self._current_result:
                print("DEBUG: Cập nhật 3D visualization với dữ liệu hiện tại")
                if hasattr(self.viz_3d, "update_enhanced_visualization"):
                    try:
                        self.viz_3d.update_enhanced_visualization(self._current_params, self._current_result)
                        print("DEBUG: Đã cập nhật enhanced visualization thành công")
                    except Exception as e:
                        print(f"DEBUG: Lỗi khi cập nhật enhanced visualization: {e}")
                        # Hiển thị thông báo lỗi cho người dùng
                        self._show_3d_error_message(f"Lỗi khi cập nhật mô hình 3D: {e}")
                elif hasattr(self.viz_3d, "update_visualization"):
                    try:
                        self.viz_3d.update_visualization(self._current_params, self._current_result)
                        print("DEBUG: Đã cập nhật basic visualization thành công")
                    except Exception as e:
                        print(f"DEBUG: Lỗi khi cập nhật basic visualization: {e}")
                        self._show_3d_error_message(f"Lỗi khi cập nhật mô hình 3D: {e}")
                else:
                    print("DEBUG: viz_3d không có method update visualization")
                    self._show_3d_error_message("Widget 3D không hỗ trợ cập nhật visualization")
            else:
                print("DEBUG: Chưa có dữ liệu để hiển thị 3D")
                # Hiển thị nội dung mặc định thay vì thông báo lỗi
                self._show_3d_welcome_content()
                
            # Hiển thị thông báo hướng dẫn sử dụng
            self._show_3d_usage_guide()
        else:
            # Chế độ 2D - ẩn thông báo hướng dẫn nếu có
            self._hide_3d_usage_guide()

    def _show_3d_error_message(self, error_msg: str):
        """Hiển thị thông báo lỗi trong panel 3D"""
        try:
            # Tạo widget thông báo lỗi
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            
            error_label = QLabel("❌ Lỗi hiển thị mô hình 3D")
            error_label.setStyleSheet("""
                QLabel {
                    color: #dc2626;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 20px;
                    text-align: center;
                }
            """)
            error_layout.addWidget(error_label)
            
            detail_label = QLabel(error_msg)
            detail_label.setStyleSheet("""
                QLabel {
                    color: #6b7280;
                    font-size: 14px;
                    padding: 10px;
                    text-align: center;
                    word-wrap: true;
                }
            """)
            detail_label.setWordWrap(True)
            error_layout.addWidget(detail_label)
            
            help_label = QLabel("💡 Hãy thử:\n1. Chạy tính toán trước\n2. Kiểm tra cài đặt PySide6-WebEngine\n3. Khởi động lại ứng dụng")
            help_label.setStyleSheet("""
                QLabel {
                    color: #059669;
                    font-size: 12px;
                    padding: 15px;
                    text-align: center;
                    background-color: #d1fae5;
                    border: 1px solid #10b981;
                    border-radius: 8px;
                    margin: 10px;
                }
            """)
            help_label.setWordWrap(True)
            error_layout.addWidget(help_label)
            
            # Thay thế nội dung của viz_3d
            if hasattr(self.viz_3d, 'setLayout'):
                # Nếu viz_3d là QWidget thông thường
                self.viz_3d.setLayout(error_layout)
            elif hasattr(self.viz_3d, 'setHtml'):
                # Nếu viz_3d là WebEngine
                error_html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h2 style="color: #dc2626;">❌ Lỗi hiển thị mô hình 3D</h2>
                    <p style="color: #6b7280; font-size: 16px;">{error_msg}</p>
                    <div style="background-color: #d1fae5; border: 1px solid #10b981; border-radius: 8px; padding: 20px; margin: 20px;">
                        <h3 style="color: #059669;">💡 Hãy thử:</h3>
                        <ol style="text-align: left; color: #059669;">
                            <li>Chạy tính toán trước</li>
                            <li>Kiểm tra cài đặt PySide6-WebEngine</li>
                            <li>Khởi động lại ứng dụng</li>
                        </ol>
                    </div>
                </body>
                </html>
                """
                self.viz_3d.setHtml(error_html)
                
        except Exception as e:
            print(f"DEBUG: Không thể hiển thị thông báo lỗi: {e}")

    def _show_3d_welcome_content(self):
        """Hiển thị nội dung mặc định khi chưa có dữ liệu để hiển thị 3D"""
        try:
            # Tạo widget nội dung mặc định
            welcome_widget = QWidget()
            welcome_layout = QVBoxLayout(welcome_widget)
            
            title_label = QLabel("🏗️ Mô hình 3D")
            title_label.setStyleSheet("""
                QLabel {
                    color: #1f2937;
                    font-size: 24px;
                    font-weight: bold;
                    padding: 30px;
                    text-align: center;
                }
            """)
            welcome_layout.addWidget(title_label)
            
            info_label = QLabel("Chào mừng bạn đến với hệ thống visualization 3D nâng cao!")
            info_label.setStyleSheet("""
                QLabel {
                    color: #6b7280;
                    font-size: 16px;
                    padding: 20px;
                    text-align: center;
                }
            """)
            welcome_layout.addWidget(info_label)
            
            steps_label = QLabel("🚀 Để bắt đầu:\n1. Nhập thông số băng tải\n2. Chọn vật liệu và loại băng\n3. Nhấn 'Tính toán' hoặc 'Tính nhanh'\n4. Xem kết quả và click 'Mô hình 3D'")
            steps_label.setStyleSheet("""
                QLabel {
                    color: #059669;
                    font-size: 14px;
                    padding: 25px;
                    text-align: center;
                    background-color: #d1fae5;
                    border: 1px solid #10b981;
                    border-radius: 12px;
                    margin: 20px;
                }
            """)
            steps_label.setWordWrap(True)
            welcome_layout.addWidget(steps_label)
            
            # Thêm nút demo
            demo_btn = QPushButton("🎮 Xem Demo 3D")
            demo_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 8px;
                    margin: 10px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
                QPushButton:pressed {
                    background-color: #1d4ed8;
                }
            """)
            demo_btn.clicked.connect(self._show_3d_demo)
            welcome_layout.addWidget(demo_btn)
            
            # Thay thế nội dung của viz_3d
            if hasattr(self.viz_3d, 'setLayout'):
                # Nếu viz_3d là QWidget thông thường
                self.viz_3d.setLayout(welcome_layout)
            elif hasattr(self.viz_3d, 'setHtml'):
                # Nếu viz_3d là WebEngine
                welcome_html = """
                <html>
                <head>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
                    <style>
                        body { margin: 0; background: #000; }
                        canvas { display: block; }
                        .info { position: absolute; top: 10px; left: 10px; color: white; font-family: Arial; }
                    </style>
                </head>
                <body>
                    <div class="info">
                        <h3>🎮 Demo Mô hình 3D Băng tải</h3>
                        <p>Đây là demo mẫu. Để xem mô hình thực tế, hãy chạy tính toán!</p>
                    </div>
                    
                    <script>
                        // Demo 3D đơn giản
                        const scene = new THREE.Scene();
                        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
                        const renderer = new THREE.WebGLRenderer();
                        renderer.setSize(window.innerWidth, window.innerHeight);
                        document.body.appendChild(renderer.domElement);
                        
                        // Tạo băng tải đơn giản
                        const geometry = new THREE.BoxGeometry(5, 0.2, 1);
                        const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
                        const belt = new THREE.Mesh(geometry, material);
                        scene.add(belt);
                        
                        camera.position.z = 5;
                        
                        function animate() {
                            requestAnimationFrame(animate);
                            belt.rotation.x += 0.01;
                            renderer.render(scene, camera);
                        }
                        animate();
                    </script>
                </body>
                </html>
                """
                self.viz_3d.setHtml(welcome_html)
                
        except Exception as e:
            print(f"DEBUG: Không thể hiển thị nội dung mặc định: {e}")

    def _on_3d_visualization_updated(self, data: dict):
        """Xử lý khi visualization 3D được cập nhật"""
        try:
            print(f"DEBUG: Visualization 3D đã được cập nhật với dữ liệu: {data}")
            # Có thể thêm logic xử lý bổ sung ở đây
        except Exception as e:
            print(f"DEBUG: Lỗi khi xử lý cập nhật visualization 3D: {e}")

    def _show_3d_demo(self):
        """Hiển thị demo 3D"""
        try:
            print("DEBUG: Hiển thị demo 3D")
            # Chuyển sang tab 3D nếu chưa ở đó
            if self.viz_stack.currentIndex() != 1:
                self._switch_mode(1)
            
            # Hiển thị demo trong widget 3D
            if hasattr(self.viz_3d, 'show_demo'):
                self.viz_3d.show_demo()
            else:
                # Fallback: hiển thị nội dung demo mặc định
                self._initialize_3d_widget_content()
                
        except Exception as e:
            print(f"DEBUG: Lỗi khi hiển thị demo 3D: {e}")

    # --- [BẮT ĐẦU THÊM CHỨC NĂNG CHECKBOX] ---
    def _show_all_charts(self) -> None:
        """Hiển thị tất cả các thành phần biểu đồ."""
        self.chk_t2.setChecked(True)
        self.chk_friction.setChecked(True)
        self.chk_lift.setChecked(True)
        self._redraw_charts()
    
    def _hide_all_charts(self) -> None:
        """Ẩn tất cả các thành phần biểu đồ."""
        self.chk_t2.setChecked(False)
        self.chk_friction.setChecked(False)
        self.chk_lift.setChecked(False)
        self._redraw_charts()
    
    def _redraw_charts(self) -> None:
        """Vẽ lại biểu đồ khi thay đổi trạng thái checkbox."""
        if hasattr(self, '_current_params') and hasattr(self, '_current_result'):
            plot_opts = {
                "show_t2": self.chk_t2.isChecked(),
                "show_friction": self.chk_friction.isChecked(),
                "show_lift": self.chk_lift.isChecked(),
            }
            try:
                self.canvas.plot_from_result(self._current_params, self._current_result, plot_opts, self._current_theme)
            except Exception:
                pass
    # --- [KẾT THÚC THÊM CHỨC NĂNG CHECKBOX] ---

    def _show_3d_usage_guide(self):
        """Hiển thị hướng dẫn sử dụng 3D visualization"""
        try:
            if not hasattr(self, '_usage_guide_widget'):
                self._usage_guide_widget = QWidget()
                guide_layout = QVBoxLayout(self._usage_guide_widget)
                
                guide_label = QLabel("💡 Hướng dẫn sử dụng Mô hình 3D:")
                guide_label.setStyleSheet("""
                    QLabel {
                        color: #1f2937;
                        font-size: 14px;
                        font-weight: bold;
                        padding: 10px;
                        background-color: #fef3c7;
                        border: 1px solid #f59e0b;
                        border-radius: 8px;
                        margin: 10px;
                    }
                """)
                guide_layout.addWidget(guide_label)
                
                tips_label = QLabel("• Sử dụng chuột để xoay, zoom mô hình\n• Nhấn nút Demo để xem mô hình mẫu\n• Chạy tính toán để xem mô hình thực tế")
                tips_label.setStyleSheet("""
                    QLabel {
                        color: #92400e;
                        font-size: 12px;
                        padding: 5px 10px;
                        background-color: #fef3c7;
                        border-radius: 6px;
                        margin: 5px 10px;
                    }
                """)
                tips_label.setWordWrap(True)
                guide_layout.addWidget(tips_label)
                
                # Thêm vào layout chính nếu có thể
                if hasattr(self, 'viz_stack') and self.viz_stack.count() > 1:
                    # Thêm vào tab 3D
                    current_widget = self.viz_stack.widget(1)
                    if hasattr(current_widget, 'layout'):
                        current_layout = current_widget.layout()
                        if current_layout:
                            current_layout.addWidget(self._usage_guide_widget)
                
        except Exception as e:
            print(f"DEBUG: Không thể hiển thị hướng dẫn sử dụng: {e}")

    def _hide_3d_usage_guide(self):
        """Ẩn hướng dẫn sử dụng 3D visualization"""
        try:
            if hasattr(self, '_usage_guide_widget'):
                self._usage_guide_widget.setVisible(False)
        except Exception as e:
            print(f"DEBUG: Không thể ẩn hướng dẫn sử dụng: {e}")

    def _show_3d_success_message(self, message: str):
        """Hiển thị thông báo thành công trong panel 3D"""
        try:
            # Tạo widget thông báo thành công
            success_widget = QWidget()
            success_layout = QVBoxLayout(success_widget)
            
            success_label = QLabel("✅ Thành công!")
            success_label.setStyleSheet("""
                QLabel {
                    color: #059669;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 15px;
                    text-align: center;
                    background-color: #d1fae5;
                    border: 1px solid #10b981;
                    border-radius: 8px;
                    margin: 10px;
                }
            """)
            success_layout.addWidget(success_label)
            
            detail_label = QLabel(message)
            detail_label.setStyleSheet("""
                QLabel {
                    color: #065f46;
                    font-size: 14px;
                    padding: 10px;
                    text-align: center;
                    word-wrap: true;
                }
            """)
            detail_label.setWordWrap(True)
            success_layout.addWidget(detail_label)
            
            # Tự động ẩn sau 3 giây
            QTimer.singleShot(3000, lambda: success_widget.setVisible(False))
            
            # Thêm vào layout chính nếu có thể
            if hasattr(self, 'viz_stack') and self.viz_stack.count() > 1:
                current_widget = self.viz_stack.widget(1)
                if hasattr(current_widget, 'layout'):
                    current_layout = current_widget.layout()
                    if current_layout:
                        current_layout.addWidget(success_widget)
                        
        except Exception as e:
            print(f"DEBUG: Không thể hiển thị thông báo thành công: {e}")
