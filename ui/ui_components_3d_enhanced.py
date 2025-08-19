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
from PySide6.QtCore import Qt, QByteArray, Signal, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QComboBox,
    QDoubleSpinBox, QSpinBox, QLineEdit, QPushButton, QScrollArea, QFrame,
    QTableWidget, QTableWidgetItem, QTextEdit, QTabWidget, QProgressBar, QLabel,
    QCheckBox, QStackedWidget
)
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtGui import QPixmap, QFont

# 2D plotting
from .plotting import EnhancedPlotCanvas

# 3D visualization (không làm app sập nếu thiếu WebEngine)
HAS_3D_SUPPORT = False
try:
    from .visualization_3d import Visualization3DWidget  # type: ignore
    HAS_3D_SUPPORT = True
except Exception:
    Visualization3DWidget = None  # type: ignore

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
        v.addStretch(1)
        scroll.setWidget(container)

        main_layout.addWidget(scroll)

        btn_row = QHBoxLayout()
        self.btn_calc = QPushButton("TÍNH TOÁN CHI TIẾT")
        self.btn_calc.setObjectName("primary")
        self.btn_quick = QPushButton("TÍNH TOÁN NHANH")
        self.btn_opt = QPushButton("TỐI ƯU TỰ ĐỘNG")
        btn_row.addWidget(self.btn_calc, 2)
        btn_row.addWidget(self.btn_quick, 1)
        btn_row.addWidget(self.btn_opt, 1)
        main_layout.addLayout(btn_row)

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
        self.spn_speed = QDoubleSpinBox(); self.spn_speed.setRange(0.1, 15.0); self.spn_speed.setDecimals(2); self.spn_speed.setValue(2.5); self.spn_speed.setSuffix(" m/s")
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
        f.addRow("Tốc độ băng:", self.spn_speed)
        f.addRow("Giờ vận hành/ngày:", self.spn_hours)
        return g

    def _img_path(self, filename: str) -> str:
        try:
            here = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(here, "images", filename)
        except Exception:
            return filename

    def _belt_group(self) -> QGroupBox:
        g = QGroupBox("Cấu hình băng")
        f = QFormLayout(g)
        f.addRow("Bề rộng băng:", self.cbo_width)
        f.addRow("Loại băng:", self.cbo_belt_type)
        f.addRow("Độ dày băng:", self.spn_thickness)
        f.addRow("Góc máng:", self.cbo_trough)
        f.addRow("Góc chất tải:", self.spn_surcharge)
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

        self.img_surcharge = QLabel()
        self.img_surcharge.setObjectName("imgSurcharge")
        self.img_surcharge.setToolTip("Minh họa góc chất tải (surcharge).")
        p_surcharge = QPixmap(self._img_path("surcharge_angle.png"))
        if not p_surcharge.isNull():
            self.img_surcharge.setPixmap(p_surcharge.scaledToHeight(120, Qt.SmoothTransformation))
        else:
            self.img_surcharge.setText("Hình góc chất tải đang cập nhật")

        img_row = QHBoxLayout()
        img_row.addWidget(self.img_trough, 1)
        img_row.addWidget(self.img_surcharge, 1)

        img_wrap = QWidget()
        img_wrap.setLayout(img_row)
        f.addRow("Minh họa:", img_wrap)

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


# ==========================
# THẺ THỐNG KÊ NHANH
# ==========================

class CardsRow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        lay = QHBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0)
        self.card_power = QFrame(); self.card_power.setObjectName("card")
        self.card_eff = QFrame(); self.card_eff.setObjectName("card")
        self.card_sf = QFrame(); self.card_sf.setObjectName("card")
        self.card_cost = QFrame(); self.card_cost.setObjectName("card")
        for c, title, sub in [
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
    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)

        self.cards = CardsRow()
        root.addWidget(self.cards)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)

        # Tab Tổng quan
        w_over = QWidget(); lo = QVBoxLayout(w_over)
        self.tbl = QTableWidget(); self.tbl.setColumnCount(2)
        self.tbl.setHorizontalHeaderLabels(["Thông số", "Giá trị"])
        self.tbl.horizontalHeader().setStretchLastSection(True)
        lo.addWidget(self.tbl)
        self.tabs.addTab(w_over, "📊 Tổng quan")

        # Tab Cấu trúc (Puly & Con lăn)
        w_struct = QWidget()
        l_struct = QVBoxLayout(w_struct)
        g_pulleys = QGroupBox("Đề xuất Puly")
        l_pulleys = QVBoxLayout(g_pulleys)
        self.tbl_pulleys = QTableWidget()
        self.tbl_pulleys.setColumnCount(2)
        self.tbl_pulleys.setHorizontalHeaderLabels(["Loại Puly (theo Bảng 21)", "Đường kính đề xuất (mm)"])
        self.tbl_pulleys.horizontalHeader().setStretchLastSection(True)
        l_pulleys.addWidget(self.tbl_pulleys)
        g_idlers = QGroupBox("Đề xuất Con lăn & Khoảng cách")
        f_idlers = QFormLayout(g_idlers)
        self.lbl_spacing_carry = QLabel("---"); self.lbl_spacing_carry.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.lbl_spacing_return = QLabel("---"); self.lbl_spacing_return.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.lbl_transition_dist = QLabel("---"); self.lbl_transition_dist.setFont(QFont("Segoe UI", 11, QFont.Bold))
        f_idlers.addRow("Khoảng cách con lăn nhánh tải:", self.lbl_spacing_carry)
        f_idlers.addRow("Khoảng cách con lăn nhánh về:", self.lbl_spacing_return)
        f_idlers.addRow("Khoảng cách chuyển tiếp (tối thiểu):", self.lbl_transition_dist)
        l_struct.addWidget(g_pulleys)
        l_struct.addWidget(g_idlers)
        l_struct.addStretch(1)
        self.tabs.addTab(w_struct, "🏗️ Cấu trúc (Puly & Con lăn)")

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

        # Tab Tóm tắt
        w_sum = QWidget(); ls = QVBoxLayout(w_sum)
        self.txt_report = QTextEdit(); self.txt_report.setReadOnly(True)
        ls.addWidget(self.txt_report)
        self.tabs.addTab(w_sum, "📝 Tóm tắt")

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
        controls_2d = QGroupBox("Tùy chọn biểu đồ 2D"); c_lay = QHBoxLayout(controls_2d)
        self.chk_t2 = QCheckBox("Lực căng T2"); self.chk_t2.setChecked(True)
        self.chk_friction = QCheckBox("Lực ma sát"); self.chk_friction.setChecked(True)
        self.chk_lift = QCheckBox("Lực nâng"); self.chk_lift.setChecked(True)
        c_lay.addWidget(self.chk_t2); c_lay.addWidget(self.chk_friction); c_lay.addWidget(self.chk_lift); c_lay.addStretch(1)
        self.canvas = EnhancedPlotCanvas()
        l2d.addWidget(controls_2d); l2d.addWidget(self.canvas)

        if HAS_3D_SUPPORT:
            self.viz_3d = Visualization3DWidget()
        else:
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

    def update_visualizations(self, params, result, theme: str = "light") -> None:
        self._current_params = params
        self._current_result = result
        self._current_theme = theme

        self._update_structural_tab(result)
        # --- [BẮT ĐẦU NÂNG CẤP] ---
        self._update_analysis_tab(result)
        # --- [KẾT THÚC NÂNG CẤP] ---

        plot_opts = {
            "show_t2": self.chk_t2.isChecked(),
            "show_friction": self.chk_friction.isChecked(),
            "show_lift": self.chk_lift.isChecked(),
        }
        try:
            self.canvas.plot_from_result(params, result, plot_opts, theme)
        except Exception:
            pass

        if HAS_3D_SUPPORT and hasattr(self.viz_3d, "update_visualization"):
            try:
                self.viz_3d.update_visualization(params, result, theme=theme)
            except Exception:
                pass
    
    def _update_structural_tab(self, r):
        """Cập nhật dữ liệu cho tab Cấu trúc (Puly & Con lăn)."""
        pulleys_data = getattr(r, 'recommended_pulley_diameters_mm', {})
        self.tbl_pulleys.setRowCount(len(pulleys_data))
        for i, (name, dia) in enumerate(pulleys_data.items()):
            self.tbl_pulleys.setItem(i, 0, QTableWidgetItem(str(name)))
            self.tbl_pulleys.setItem(i, 1, QTableWidgetItem(f"{dia:.0f} mm"))
        self.tbl_pulleys.resizeColumnsToContents()

        idlers_data = getattr(r, 'recommended_idler_spacing_m', {})
        self.lbl_spacing_carry.setText(f"{idlers_data.get('Nhánh tải (đề xuất)', 0):.2f} m")
        self.lbl_spacing_return.setText(f"{idlers_data.get('Nhánh về (đề xuất)', 0):.2f} m")
        
        transition_dist = getattr(r, 'transition_distance_m', 0.0)
        self.lbl_transition_dist.setText(f"{transition_dist:.3f} m")

    # --- [BẮT ĐẦU NÂNG CẤP] ---
    def _update_analysis_tab(self, r):
        """Tạo báo cáo HTML cho tab Phân tích Kỹ thuật."""
        ana_report_html = "<h3>PHÂN TÍCH KỸ THUẬT</h3>"
        eff = getattr(r, "drive_efficiency_percent", getattr(r, "efficiency", 0.0))
        ana_report_html += f"<p><b>- Hiệu suất truyền động:</b> {eff:.1f}% (η_m × η_g ÷ Kt)</p>"
        ana_report_html += f"<p><b>- Phần trăm sử dụng cường độ đai:</b> {r.belt_strength_utilization:.1f}%</p>"
        ana_report_html += f"<p><b>- Phần trăm sử dụng tiết diện (ước tính):</b> {r.capacity_utilization:.1f}%</p>"

        # Logic mới để hiển thị kết quả truyền động kép
        if r.drive_distribution_method:
            ana_report_html += "<h4 style='color: #3b82f6;'>PHÂN TÍCH TRUYỀN ĐỘNG KÉP</h4>"
            ana_report_html += f"<p><b>Phương pháp phân phối:</b> {r.drive_distribution_method}</p>"
            ana_report_html += "<ul>"
            ana_report_html += f"<li><b>Puly 1 (Chính):</b> Lực vòng Fp1 = <b>{r.Fp1:,.1f} kgf</b> | Lực căng T1 = <b>{r.F11:,.0f} N</b></li>"
            ana_report_html += f"<li><b>Puly 2 (Phụ):</b> Lực vòng Fp2 = <b>{r.Fp2:,.1f} kgf</b> | Lực căng T2 = <b>{r.F12:,.0f} N</b></li>"
            ana_report_html += "</ul>"
            ana_report_html += f"<p><b>=> Lực căng lớn nhất toàn hệ thống (Max Tension): {r.max_tension:,.0f} N</b></p>"

        if r.warnings:
            ana_report_html += "<h4 style='color: #f59e0b;'>CẢNH BÁO:</h4><ul>"
            for w in r.warnings:
                ana_report_html += f"<li>{w}</li>"
            ana_report_html += "</ul>"

        if r.recommendations:
            ana_report_html += "<h4 style='color: #22c55e;'>KHUYẾN NGHỊ:</h4><ul>"
            for rec in r.recommendations:
                ana_report_html += f"<li>{rec}</li>"
            ana_report_html += "</ul>"

        self.txt_analysis.setHtml(ana_report_html)
    # --- [KẾT THÚC NÂNG CẤP] ---

    def _switch_mode(self, idx: int) -> None:
        idx = 0 if idx not in (0, 1) else idx
        self.btn_2d_mode.setChecked(idx == 0)
        self.btn_3d_mode.setChecked(idx == 1)
        self.viz_stack.setCurrentIndex(idx)
        if idx == 1 and HAS_3D_SUPPORT and self._current_params and self._current_result:
            try:
                self.viz_3d.update_visualization(self._current_params, self._current_result, theme=self._current_theme)
            except Exception:
                pass
