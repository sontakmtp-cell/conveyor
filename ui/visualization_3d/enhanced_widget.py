"""
Enhanced Visualization 3D Widget
Widget PyQt6 với các panel điều khiển và hiển thị thông tin nâng cao
"""

import json
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QCheckBox, QComboBox, QPushButton, QSlider, QSpinBox,
    QDoubleSpinBox, QTabWidget, QTextEdit, QProgressBar,
    QSplitter, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, Signal as pyqtSignal
from PySide6.QtGui import QFont, QPalette, QColor

from .core.animation_engine import ConveyorAnimationEngine
from .core.component_builder import ComponentBuilderManager
from .core.physics_simulator import ConveyorPhysicsSimulator
from .core.model_generator import ConveyorModelGenerator


class AnimationControlPanel(QWidget):
    """Panel điều khiển animation"""
    
    animation_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation_engine = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Thiết lập giao diện"""
        layout = QVBoxLayout(self)
        
        # Nhóm điều khiển chính
        main_group = QGroupBox("Điều khiển Animation")
        main_layout = QVBoxLayout(main_group)
        
        # Nút Play/Pause
        self.play_pause_btn = QPushButton("⏸️ Tạm dừng")
        self.play_pause_btn.setCheckable(True)
        self.play_pause_btn.setChecked(True)
        self.play_pause_btn.clicked.connect(self._toggle_play_pause)
        main_layout.addWidget(self.play_pause_btn)
        
        # Nút Reset
        self.reset_btn = QPushButton("🔄 Đặt lại")
        self.reset_btn.clicked.connect(self._reset_animation)
        main_layout.addWidget(self.reset_btn)
        
        # Điều khiển tốc độ
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Tốc độ:"))
        
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(10, 500)
        self.speed_slider.setValue(100)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(50)
        self.speed_slider.valueChanged.connect(self._speed_changed)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("1.0x")
        speed_layout.addWidget(self.speed_label)
        main_layout.addLayout(speed_layout)
        
        layout.addWidget(main_group)
        
        # Nhóm điều khiển thành phần
        component_group = QGroupBox("Hiển thị thành phần")
        component_layout = QVBoxLayout(component_group)
        
        self.chk_belt_system = QCheckBox("Hệ thống băng tải")
        self.chk_belt_system.setChecked(True)
        self.chk_belt_system.toggled.connect(self._component_toggled)
        component_layout.addWidget(self.chk_belt_system)
        
        self.chk_drive_system = QCheckBox("Hệ truyền động")
        self.chk_drive_system.setChecked(True)
        self.chk_drive_system.toggled.connect(self._component_toggled)
        component_layout.addWidget(self.chk_drive_system)
        
        self.chk_support_structure = QCheckBox("Khung đỡ")
        self.chk_support_structure.setChecked(True)
        self.chk_support_structure.toggled.connect(self._component_toggled)
        component_layout.addWidget(self.chk_support_structure)
        
        self.chk_material_flow = QCheckBox("Dòng vật liệu")
        self.chk_material_flow.setChecked(True)
        self.chk_material_flow.toggled.connect(self._component_toggled)
        component_layout.addWidget(self.chk_material_flow)
        
        layout.addWidget(component_group)
        
        # Nhóm điều khiển camera
        camera_group = QGroupBox("Điều khiển camera")
        camera_layout = QVBoxLayout(camera_group)
        
        self.camera_preset_combo = QComboBox()
        self.camera_preset_combo.addItems([
            "Tổng quan", "Hệ truyền động", "Con lăn", "Băng tải", "Tùy chỉnh"
        ])
        self.camera_preset_combo.currentTextChanged.connect(self._camera_preset_changed)
        camera_layout.addWidget(self.camera_preset_combo)
        
        # Nút camera
        camera_btn_layout = QHBoxLayout()
        self.front_btn = QPushButton("Trước")
        self.front_btn.clicked.connect(lambda: self._set_camera_view("front"))
        camera_btn_layout.addWidget(self.front_btn)
        
        self.side_btn = QPushButton("Bên")
        self.side_btn.clicked.connect(lambda: self._set_camera_view("side"))
        camera_btn_layout.addWidget(self.side_btn)
        
        self.top_btn = QPushButton("Trên")
        self.top_btn.clicked.connect(lambda: self._set_camera_view("top"))
        camera_btn_layout.addWidget(self.top_btn)
        
        camera_layout.addLayout(camera_btn_layout)
        layout.addWidget(camera_group)
        
        # Nhóm điều khiển chất liệu
        material_group = QGroupBox("Chế độ hiển thị")
        material_layout = QVBoxLayout(material_group)
        
        self.material_combo = QComboBox()
        self.material_combo.addItems(["Thực tế", "Wireframe", "Phân tích nhiệt", "Phân tích ứng suất"])
        self.material_combo.currentTextChanged.connect(self._material_mode_changed)
        material_layout.addWidget(self.material_combo)
        
        # Điều khiển độ trong suốt
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Độ trong suốt:"))
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self._opacity_changed)
        opacity_layout.addWidget(self.opacity_slider)
        
        self.opacity_label = QLabel("100%")
        opacity_layout.addWidget(self.opacity_label)
        material_layout.addLayout(opacity_layout)
        
        layout.addWidget(material_group)
        
        # Nhóm điều khiển nâng cao
        advanced_group = QGroupBox("Tính năng nâng cao")
        advanced_layout = QVBoxLayout(advanced_group)
        
        self.chk_physics_simulation = QCheckBox("Mô phỏng vật lý")
        self.chk_physics_simulation.setChecked(False)
        self.chk_physics_simulation.toggled.connect(self._physics_simulation_toggled)
        advanced_layout.addWidget(self.chk_physics_simulation)
        
        self.chk_particle_system = QCheckBox("Hệ thống hạt")
        self.chk_particle_system.setChecked(True)
        self.chk_particle_system.toggled.connect(self._particle_system_toggled)
        advanced_layout.addWidget(self.chk_particle_system)
        
        self.chk_shadows = QCheckBox("Bóng đổ")
        self.chk_shadows.setChecked(True)
        self.chk_shadows.toggled.connect(self._shadows_toggled)
        advanced_layout.addWidget(self.chk_shadows)
        
        self.chk_antialiasing = QCheckBox("Khử răng cưa")
        self.chk_antialiasing.setChecked(True)
        self.chk_antialiasing.toggled.connect(self._antialiasing_toggled)
        advanced_layout.addWidget(self.chk_antialiasing)
        
        layout.addWidget(advanced_group)
        
        # Thêm stretch để đẩy các widget lên trên
        layout.addStretch()
    
    def set_animation_engine(self, engine: ConveyorAnimationEngine):
        """Thiết lập animation engine"""
        self.animation_engine = engine
    
    def _toggle_play_pause(self):
        """Chuyển đổi play/pause"""
        if self.animation_engine:
            if self.play_pause_btn.isChecked():
                self.animation_engine.play()
                self.play_pause_btn.setText("⏸️ Tạm dừng")
            else:
                self.animation_engine.pause()
                self.play_pause_btn.setText("▶️ Phát")
            
            self.animation_changed.emit({
                'action': 'play_pause',
                'is_playing': self.play_pause_btn.isChecked()
            })
    
    def _reset_animation(self):
        """Đặt lại animation"""
        if self.animation_engine:
            self.animation_engine.reset()
            self.animation_changed.emit({'action': 'reset'})
    
    def _speed_changed(self, value):
        """Tốc độ thay đổi"""
        speed = value / 100.0
        self.speed_label.setText(f"{speed:.1f}x")
        
        if self.animation_engine:
            self.animation_engine.set_speed(speed)
        
        self.animation_changed.emit({
            'action': 'speed_change',
            'speed': speed
        })
    
    def _component_toggled(self):
        """Thành phần được bật/tắt"""
        components = {
            'belt_system': self.chk_belt_system.isChecked(),
            'drive_system': self.chk_drive_system.isChecked(),
            'support_structure': self.chk_support_structure.isChecked(),
            'material_flow': self.chk_material_flow.isChecked()
        }
        
        self.animation_changed.emit({
            'action': 'component_toggle',
            'components': components
        })
    
    def _camera_preset_changed(self, preset: str):
        """Camera preset thay đổi"""
        self.animation_changed.emit({
            'action': 'camera_preset',
            'preset': preset
        })
    
    def _set_camera_view(self, view: str):
        """Thiết lập góc nhìn camera"""
        self.animation_changed.emit({
            'action': 'camera_view',
            'view': view
        })
    
    def _material_mode_changed(self, mode: str):
        """Chế độ chất liệu thay đổi"""
        self.animation_changed.emit({
            'action': 'material_mode',
            'mode': mode
        })
    
    def _opacity_changed(self, value):
        """Độ trong suốt thay đổi"""
        opacity = value / 100.0
        self.opacity_label.setText(f"{value}%")
        
        self.animation_changed.emit({
            'action': 'opacity_change',
            'opacity': opacity
        })
    
    def _physics_simulation_toggled(self, checked: bool):
        """Mô phỏng vật lý được bật/tắt"""
        self.animation_changed.emit({
            'action': 'physics_simulation',
            'enabled': checked
        })
    
    def _particle_system_toggled(self, checked: bool):
        """Hệ thống hạt được bật/tắt"""
        self.animation_changed.emit({
            'action': 'particle_system',
            'enabled': checked
        })
    
    def _shadows_toggled(self, checked: bool):
        """Bóng đổ được bật/tắt"""
        self.animation_changed.emit({
            'action': 'shadows',
            'enabled': checked
        })
    
    def _antialiasing_toggled(self, checked: bool):
        """Khử răng cưa được bật/tắt"""
        self.animation_changed.emit({
            'action': 'antialiasing',
            'enabled': checked
        })


class InformationPanel(QWidget):
    """Panel hiển thị thông tin"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Thiết lập giao diện"""
        layout = QVBoxLayout(self)
        
        # Tab widget cho các loại thông tin khác nhau
        self.tab_widget = QTabWidget()
        
        # Tab thông số kỹ thuật
        self.technical_tab = self._create_technical_tab()
        self.tab_widget.addTab(self.technical_tab, "Thông số kỹ thuật")
        
        # Tab thành phần
        self.components_tab = self._create_components_tab()
        self.tab_widget.addTab(self.components_tab, "Thành phần")
        
        # Tab vật lý
        self.physics_tab = self._create_physics_tab()
        self.tab_widget.addTab(self.physics_tab, "Vật lý")
        
        # Tab animation
        self.animation_tab = self._create_animation_tab()
        self.tab_widget.addTab(self.animation_tab, "Animation")
        
        layout.addWidget(self.tab_widget)
    
    def _create_technical_tab(self) -> QWidget:
        """Tạo tab thông số kỹ thuật"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Thông số chính
        main_group = QGroupBox("Thông số chính")
        main_layout = QVBoxLayout(main_group)
        
        self.length_label = QLabel("Chiều dài: -- m")
        main_layout.addWidget(self.length_label)
        
        self.width_label = QLabel("Chiều rộng: -- m")
        main_layout.addWidget(self.width_label)
        
        self.height_label = QLabel("Chiều cao: -- m")
        main_layout.addWidget(self.height_label)
        
        self.speed_label = QLabel("Tốc độ: -- m/s")
        main_layout.addWidget(self.speed_label)
        
        self.power_label = QLabel("Công suất: -- kW")
        main_layout.addWidget(self.power_label)
        
        layout.addWidget(main_group)
        
        # Thông số vật liệu
        material_group = QGroupBox("Vật liệu")
        material_layout = QVBoxLayout(material_group)
        
        self.material_type_label = QLabel("Loại vật liệu: --")
        material_layout.addWidget(self.material_type_label)
        
        self.flow_rate_label = QLabel("Lưu lượng: -- TPH")
        material_layout.addWidget(self.flow_rate_label)
        
        self.density_label = QLabel("Mật độ: -- kg/m³")
        material_layout.addWidget(self.density_label)
        
        layout.addWidget(material_group)
        
        layout.addStretch()
        return widget
    
    def _create_components_tab(self) -> QWidget:
        """Tạo tab thành phần"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Danh sách thành phần
        self.components_text = QTextEdit()
        self.components_text.setReadOnly(True)
        self.components_text.setMaximumHeight(200)
        layout.addWidget(QLabel("Danh sách thành phần:"))
        layout.addWidget(self.components_text)
        
        # Thống kê
        stats_group = QGroupBox("Thống kê")
        stats_layout = QVBoxLayout(stats_group)
        
        self.total_components_label = QLabel("Tổng số thành phần: --")
        stats_layout.addWidget(self.total_components_label)
        
        self.belt_components_label = QLabel("Thành phần băng tải: --")
        stats_layout.addWidget(self.belt_components_label)
        
        self.drive_components_label = QLabel("Thành phần truyền động: --")
        stats_layout.addWidget(self.drive_components_label)
        
        self.support_components_label = QLabel("Thành phần khung đỡ: --")
        stats_layout.addWidget(self.support_components_label)
        
        layout.addWidget(stats_group)
        
        layout.addStretch()
        return widget
    
    def _create_physics_tab(self) -> QWidget:
        """Tạo tab vật lý"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Lực và mô-men
        forces_group = QGroupBox("Lực và mô-men")
        forces_layout = QVBoxLayout(forces_group)
        
        self.belt_tension_label = QLabel("Lực căng băng tải: -- N")
        forces_layout.addWidget(self.belt_tension_label)
        
        self.motor_torque_label = QLabel("Mô-men động cơ: -- Nm")
        forces_layout.addWidget(self.motor_torque_label)
        
        self.output_torque_label = QLabel("Mô-men đầu ra: -- Nm")
        forces_layout.addWidget(self.output_torque_label)
        
        layout.addWidget(forces_group)
        
        # Hiệu suất
        efficiency_group = QGroupBox("Hiệu suất")
        efficiency_layout = QVBoxLayout(efficiency_group)
        
        self.motor_efficiency_label = QLabel("Hiệu suất động cơ: -- %")
        efficiency_layout.addWidget(self.motor_efficiency_label)
        
        self.gearbox_efficiency_label = QLabel("Hiệu suất hộp số: -- %")
        efficiency_layout.addWidget(self.gearbox_efficiency_label)
        
        self.overall_efficiency_label = QLabel("Hiệu suất tổng thể: -- %")
        efficiency_layout.addWidget(self.overall_efficiency_label)
        
        layout.addWidget(efficiency_group)
        
        # Hệ số an toàn
        safety_group = QGroupBox("An toàn")
        safety_layout = QVBoxLayout(safety_group)
        
        self.safety_factor_label = QLabel("Hệ số an toàn: --")
        safety_layout.addWidget(self.safety_factor_label)
        
        self.safety_status_label = QLabel("Trạng thái: --")
        safety_layout.addWidget(self.safety_status_label)
        
        layout.addWidget(safety_group)
        
        layout.addStretch()
        return widget
    
    def _create_animation_tab(self) -> QWidget:
        """Tạo tab animation"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Trạng thái animation
        status_group = QGroupBox("Trạng thái")
        status_layout = QVBoxLayout(status_group)
        
        self.animation_status_label = QLabel("Trạng thái: --")
        status_layout.addWidget(self.animation_status_label)
        
        self.animation_time_label = QLabel("Thời gian: -- s")
        status_layout.addWidget(self.animation_time_label)
        
        self.animation_speed_label = QLabel("Tốc độ: -- x")
        status_layout.addWidget(self.animation_speed_label)
        
        layout.addWidget(status_group)
        
        # Thông số animation
        params_group = QGroupBox("Thông số")
        params_layout = QVBoxLayout(params_group)
        
        self.belt_animation_label = QLabel("Animation băng tải: --")
        params_layout.addWidget(self.belt_animation_label)
        
        self.drive_animation_label = QLabel("Animation truyền động: --")
        params_layout.addWidget(self.drive_animation_label)
        
        self.idler_animation_label = QLabel("Animation con lăn: --")
        params_layout.addWidget(self.idler_animation_label)
        
        self.material_animation_label = QLabel("Animation vật liệu: --")
        params_layout.addWidget(self.material_animation_label)
        
        layout.addWidget(params_group)
        
        layout.addStretch()
        return widget
    
    def update_technical_info(self, data: Dict[str, Any]):
        """Cập nhật thông tin kỹ thuật"""
        if 'belt_system' in data:
            belt_data = data['belt_system']
            geometry = belt_data.get('geometry', {})
            
            self.length_label.setText(f"Chiều dài: {geometry.get('length', 0):.1f} m")
            self.width_label.setText(f"Chiều rộng: {geometry.get('width', 0):.2f} m")
            self.height_label.setText(f"Chiều cao: {geometry.get('thickness', 0):.3f} m")
        
        if 'drive_system' in data:
            drive_data = data['drive_system']
            motor_data = drive_data.get('motor', {})
            
            self.power_label.setText(f"Công suất: {motor_data.get('power_kw', 0):.1f} kW")
        
        if 'material_properties' in data:
            material_data = data['material_properties']
            
            self.material_type_label.setText(f"Loại vật liệu: {material_data.get('name', '--')}")
            self.flow_rate_label.setText(f"Lưu lượng: {material_data.get('flow_rate_tph', 0):.0f} TPH")
            self.density_label.setText(f"Mật độ: {material_data.get('density_kg_m3', 0):.0f} kg/m³")
    
    def update_components_info(self, components_data: Dict[str, Any]):
        """Cập nhật thông tin thành phần"""
        # Cập nhật danh sách thành phần
        components_text = ""
        for comp in components_data.get('components', []):
            components_text += f"• {comp['name']} ({comp['type']})\n"
        
        self.components_text.setPlainText(components_text)
        
        # Cập nhật thống kê
        self.total_components_label.setText(f"Tổng số thành phần: {components_data.get('total_count', 0)}")
        
        systems = components_data.get('systems', {})
        self.belt_components_label.setText(f"Thành phần băng tải: {systems.get('belt_system', {}).get('component_count', 0)}")
        self.drive_components_label.setText(f"Thành phần truyền động: {systems.get('drive_system', {}).get('component_count', 0)}")
        self.support_components_label.setText(f"Thành phần khung đỡ: {systems.get('support_structure', {}).get('component_count', 0)}")
    
    def update_physics_info(self, physics_data: Dict[str, Any]):
        """Cập nhật thông tin vật lý"""
        if 'simulation' in physics_data:
            sim_data = physics_data['simulation']
            
            if 'belt' in sim_data:
                self.belt_tension_label.setText(f"Lực căng băng tải: {sim_data['belt'].get('tension_n', 0):.0f} N")
            
            if 'drive' in sim_data:
                self.motor_torque_label.setText(f"Mô-men động cơ: {sim_data['drive'].get('output_torque_nm', 0):.1f} Nm")
                self.output_torque_label.setText(f"Mô-men đầu ra: {sim_data['drive'].get('output_torque_nm', 0):.1f} Nm")
        
        if 'summary' in physics_data:
            summary = physics_data['summary']
            
            self.overall_efficiency_label.setText(f"Hiệu suất tổng thể: {summary.get('efficiency', 0) * 100:.1f} %")
            self.safety_factor_label.setText(f"Hệ số an toàn: {summary.get('safety_factor', 0):.2f}")
            
            safety_factor = summary.get('safety_factor', 0)
            if safety_factor > 2.0:
                status = "An toàn"
                color = "green"
            elif safety_factor > 1.5:
                status = "Chấp nhận được"
                color = "orange"
            else:
                status = "Không an toàn"
                color = "red"
            
            self.safety_status_label.setText(f"Trạng thái: {status}")
            self.safety_status_label.setStyleSheet(f"color: {color}")
    
    def update_animation_info(self, animation_data: Dict[str, Any]):
        """Cập nhật thông tin animation"""
        if 'state' in animation_data:
            state = animation_data['state']
            
            status = "Đang phát" if state.get('is_playing', False) else "Đã tạm dừng"
            self.animation_status_label.setText(f"Trạng thái: {status}")
            
            self.animation_time_label.setText(f"Thời gian: {state.get('time', 0):.1f} s")
            self.animation_speed_label.setText(f"Tốc độ: {state.get('speed', 1.0):.1f}x")
        
        if 'animations' in animation_data:
            animations = animation_data['animations']
            
            if 'belt' in animations:
                belt_anim = animations['belt']
                self.belt_animation_label.setText(f"Animation băng tải: {belt_anim.get('speed', 0):.2f} m/s")
            
            if 'drive' in animations:
                drive_anim = animations['drive']
                self.drive_animation_label.setText(f"Animation truyền động: {drive_anim.get('output_rpm', 0):.0f} RPM")
            
            if 'idler' in animations:
                idler_anim = animations['idler']
                self.idler_animation_label.setText(f"Animation con lăn: {idler_anim.get('rotation_speed', 0):.2f} rad/s")
            
            if 'material_flow' in animations:
                material_anim = animations['material_flow']
                self.material_animation_label.setText(f"Animation vật liệu: {material_anim.get('flow_rate', 0):.0f} TPH")


class EnhancedVisualization3DWidget(QWidget):
    """Widget visualization 3D nâng cấp"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Khởi tạo các thành phần
        self.animation_engine = None
        self.component_builder = None
        self.physics_simulator = None
        
        # Thiết lập giao diện
        self._setup_ui()
        self._setup_connections()
        
        # Timer để cập nhật thông tin
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_info)
        self.update_timer.start(100)  # Cập nhật mỗi 100ms
    
    def _setup_ui(self):
        """Thiết lập giao diện"""
        # Layout chính
        main_layout = QHBoxLayout(self)
        
        # Splitter để chia màn hình
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel điều khiển bên trái
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Panel điều khiển animation
        self.animation_panel = AnimationControlPanel()
        left_layout.addWidget(self.animation_panel)
        
        # Panel thông tin
        self.info_panel = InformationPanel()
        left_layout.addWidget(self.info_panel)
        
        left_panel.setMaximumWidth(350)
        left_panel.setMinimumWidth(300)
        
        # Panel visualization chính với WebEngine
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
            from PySide6.QtWebEngineCore import QWebEnginePage
            
            self.web_view = QWebEngineView()
            self.web_page = QWebEnginePage()
            self.web_view.setPage(self.web_page)
            
            # Thiết lập HTML mặc định
            default_html = self._generate_default_html()
            self.web_view.setHtml(default_html)
            
            self.visualization_panel = self.web_view
            
        except ImportError:
            # Fallback nếu không có WebEngine
            self.visualization_panel = QWidget()
            self.visualization_panel.setStyleSheet("background-color: #2b2b2b;")
            
            temp_label = QLabel("Panel Visualization 3D\n(Cần PySide6-WebEngine để hiển thị 3D)")
            temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            temp_label.setStyleSheet("color: white; font-size: 16px;")
            
            temp_layout = QVBoxLayout(self.visualization_panel)
            temp_layout.addWidget(temp_label)
        
        # Thêm vào splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(self.visualization_panel)
        
        # Thiết lập tỷ lệ splitter
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter)
    
    def _setup_connections(self):
        """Thiết lập kết nối tín hiệu"""
        self.animation_panel.animation_changed.connect(self._handle_animation_change)
    
    def update_enhanced_visualization(self, params, result):
        """Cập nhật visualization nâng cao"""
        try:
            # Sử dụng ConveyorModelGenerator để tạo mô hình hoàn chỉnh
            self.model_generator = ConveyorModelGenerator(params, result)
            model_data = self.model_generator.generate_complete_model()
            
            # Khởi tạo animation engine
            self.animation_engine = ConveyorAnimationEngine(model_data)
            self.animation_panel.set_animation_engine(self.animation_engine)
            
            # Khởi tạo component builder
            self.component_builder = ComponentBuilderManager(model_data)
            
            # Khởi tạo physics simulator
            self.physics_simulator = ConveyorPhysicsSimulator(model_data)
            
            # Cập nhật thông tin
            self._update_all_info(model_data)
            
            # Cập nhật visualization 3D
            self._update_3d_visualization(model_data)
            
        except Exception as e:
            print(f"Lỗi trong update_enhanced_visualization: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_model_data(self, params, result) -> Dict[str, Any]:
        """Tạo dữ liệu mô hình từ params và result"""
        model_data = {
            'belt_system': {
                'geometry': {
                    'width': params.B_mm / 1000.0,
                    'length': params.L_m,
                    'thickness': getattr(params, 'belt_thickness_mm', 10) / 1000.0,
                    'trough_angle': self._parse_trough_angle(params.trough_angle_label),
                    'inclination': getattr(params, 'inclination_degrees', 0)
                },
                'material': {
                    'type': getattr(params, 'belt_type', 'fabric_ep'),
                    'texture': 'belt_texture'
                }
            },
            'drive_system': {
                'motor': {
                    'power_kw': getattr(result, 'motor_power_kw', 5.5),
                    'rpm': getattr(params, 'motor_rpm', 1450),
                    'efficiency': getattr(params, 'motor_efficiency', 0.9)
                },
                'gearbox': {
                    'ratio': getattr(result, 'transmission_solution', {}).get('gearbox_ratio', 20.0),
                    'efficiency': getattr(params, 'gearbox_efficiency', 0.95)
                },
                'chain_drive': getattr(result, 'transmission_solution', {}),
                'pulleys': {
                    'drive_diameter': 0.4,
                    'tail_diameter': 0.4
                }
            },
            'support_structure': {
                'carrying_idlers': {
                    'count': max(2, int(params.L_m / getattr(params, 'carrying_idler_spacing_m', 2.0))),
                    'spacing': getattr(params, 'carrying_idler_spacing_m', 2.0),
                    'diameter': 0.15,
                    'trough_angle': self._parse_trough_angle(params.trough_angle_label)
                },
                'return_idlers': {
                    'count': max(2, int(params.L_m / getattr(params, 'return_idler_spacing_m', 3.0))),
                    'spacing': getattr(params, 'return_idler_spacing_m', 3.0),
                    'diameter': 0.12
                }
            },
            'material_properties': {
                'name': getattr(params, 'material_type', 'Than đá'),
                'density_kg_m3': getattr(params, 'material_density_kg_m3', 1600),
                'flow_rate_tph': getattr(params, 'Q_tph', 100),
                'particle_size_mm': getattr(params, 'particle_size_mm', 25.0)
            },
            'belt_speed_mps': getattr(params, 'belt_speed_mps', 2.0)
        }
        
        return model_data
    
    def _parse_trough_angle(self, angle_label: str) -> float:
        """Phân tích góc máng từ label"""
        try:
            if '20°' in angle_label:
                return 20.0
            elif '35°' in angle_label:
                return 35.0
            elif '45°' in angle_label:
                return 45.0
            else:
                return 0.0
        except:
            return 0.0
    
    def _update_all_info(self, model_data: Dict[str, Any]):
        """Cập nhật tất cả thông tin"""
        # Cập nhật thông tin kỹ thuật
        self.info_panel.update_technical_info(model_data)
        
        # Cập nhật thông tin thành phần
        if self.component_builder:
            components_data = self.component_builder.export_components_data()
            self.info_panel.update_components_info(components_data)
        
        # Cập nhật thông tin vật lý
        if self.physics_simulator:
            physics_data = self.physics_simulator.export_physics_data()
            try:
                physics_dict = json.loads(physics_data)
                self.info_panel.update_physics_info(physics_dict)
            except:
                pass
    
    def _update_info(self):
        """Cập nhật thông tin theo timer"""
        if self.animation_engine:
            animation_data = self.animation_engine.get_animation_data()
            self.info_panel.update_animation_info(animation_data)
    
    def _handle_animation_change(self, data: Dict[str, Any]):
        """Xử lý thay đổi animation"""
        action = data.get('action', '')
        
        if action == 'play_pause':
            # Xử lý play/pause
            pass
        elif action == 'reset':
            # Xử lý reset
            pass
        elif action == 'speed_change':
            # Xử lý thay đổi tốc độ
            pass
        elif action == 'component_toggle':
            # Xử lý bật/tắt thành phần
            pass
        elif action == 'camera_preset':
            # Xử lý thay đổi camera preset
            pass
        elif action == 'material_mode':
            # Xử lý thay đổi chế độ chất liệu
            pass
        
        # Gửi tín hiệu đến WebEngine (sẽ được implement sau)
        print(f"Animation change: {action}")
    
    def get_visualization_data(self) -> Dict[str, Any]:
        """Lấy dữ liệu visualization để truyền vào WebEngine"""
        data = {}
        
        if self.animation_engine:
            data['animation'] = self.animation_engine.get_animation_data()
        
        if self.component_builder:
            data['components'] = self.component_builder.export_components_data()
        
        if self.physics_simulator:
            data['physics'] = self.physics_simulator.export_physics_data()
        
        return data
    
    def _generate_default_html(self) -> str:
        """Tạo HTML mặc định cho visualization"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Conveyor 3D Visualization</title>
            <style>
                body { margin: 0; padding: 0; background: #2b2b2b; color: white; font-family: Arial, sans-serif; }
                #container { width: 100%; height: 100vh; display: flex; align-items: center; justify-content: center; }
                .loading { text-align: center; }
                .loading h2 { color: #3b82f6; margin-bottom: 20px; }
                .loading p { color: #9ca3af; }
            </style>
        </head>
        <body>
            <div id="container">
                <div class="loading">
                    <h2>🚀 Conveyor 3D Visualization</h2>
                    <p>Đang tải mô hình 3D...</p>
                    <p>Vui lòng chờ trong giây lát</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _update_3d_visualization(self, model_data: Dict[str, Any]):
        """Cập nhật visualization 3D với dữ liệu mới"""
        if hasattr(self, 'web_view') and self.web_view:
            try:
                # Tạo HTML với dữ liệu mới
                html_content = self._generate_3d_html(model_data)
                self.web_view.setHtml(html_content)
            except Exception as e:
                print(f"Lỗi cập nhật 3D visualization: {e}")
    
    def _generate_3d_html(self, model_data: Dict[str, Any]) -> str:
        """Tạo HTML cho visualization 3D với dữ liệu thực"""
        # Lấy thông tin từ model_data
        belt_info = model_data.get('belt_system', {})
        drive_info = model_data.get('drive_system', {})
        support_info = model_data.get('support_structure', {})
        
        # Tạo HTML với Three.js
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Conveyor 3D - Enhanced</title>
            <style>
                body {{ margin: 0; padding: 0; background: #1a1a1a; color: white; font-family: 'Segoe UI', sans-serif; }}
                #container {{ width: 100%; height: 100vh; }}
                #info-panel {{ 
                    position: absolute; top: 20px; left: 20px; 
                    background: rgba(0,0,0,0.8); padding: 20px; border-radius: 10px;
                    max-width: 300px; z-index: 100;
                }}
                .info-item {{ margin: 10px 0; }}
                .info-label {{ color: #9ca3af; font-size: 12px; }}
                .info-value {{ color: #3b82f6; font-weight: bold; font-size: 14px; }}
                #controls {{ 
                    position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
                    background: rgba(0,0,0,0.8); padding: 15px; border-radius: 20px;
                    z-index: 100;
                }}
                .control-btn {{ 
                    background: #3b82f6; color: white; border: none; padding: 8px 16px;
                    border-radius: 20px; margin: 0 5px; cursor: pointer;
                }}
                .control-btn:hover {{ background: #2563eb; }}
            </style>
        </head>
        <body>
            <div id="container">
                <div id="info-panel">
                    <h3>📊 Thông tin Băng tải</h3>
                    <div class="info-item">
                        <div class="info-label">Chiều dài:</div>
                        <div class="info-value">{belt_info.get('geometry', {}).get('length', 0):.1f} m</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Chiều rộng:</div>
                        <div class="info-value">{belt_info.get('geometry', {}).get('width', 0):.2f} m</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Góc máng:</div>
                        <div class="info-value">{belt_info.get('geometry', {}).get('trough_angle', 0):.0f}°</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Tốc độ:</div>
                        <div class="info-value">{model_data.get('belt_speed_mps', 0):.2f} m/s</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Công suất:</div>
                        <div class="info-value">{drive_info.get('motor', {}).get('power_kw', 0):.1f} kW</div>
                    </div>
                </div>
                
                <div id="controls">
                    <button class="control-btn" onclick="toggleAnimation()">⏸️ Tạm dừng</button>
                    <button class="control-btn" onclick="resetView()">🔄 Đặt lại</button>
                    <button class="control-btn" onclick="toggleWireframe()">🔲 Wireframe</button>
                </div>
            </div>
            
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script>
                // Three.js visualization code sẽ được thêm ở đây
                let scene, camera, renderer, conveyor;
                let isAnimating = true;
                
                function init() {{
                    // Thiết lập scene
                    scene = new THREE.Scene();
                    scene.background = new THREE.Color(0x1a1a1a);
                    
                    // Thiết lập camera
                    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
                    camera.position.set(10, 5, 10);
                    camera.lookAt(0, 0, 0);
                    
                    // Thiết lập renderer
                    renderer = new THREE.WebGLRenderer({{ antialias: true }});
                    renderer.setSize(window.innerWidth, window.innerHeight);
                    renderer.shadowMap.enabled = true;
                    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                    
                    document.getElementById('container').appendChild(renderer.domElement);
                    
                    // Tạo băng tải
                    createConveyor();
                    
                    // Thiết lập lighting
                    setupLighting();
                    
                    // Animation loop
                    animate();
                    
                    // Xử lý resize
                    window.addEventListener('resize', onWindowResize, false);
                }}
                
                function createConveyor() {{
                    // Tạo băng tải chính
                    const beltGeometry = new THREE.BoxGeometry(
                        {belt_info.get('geometry', {}).get('length', 10)}, 
                        {belt_info.get('geometry', {}).get('thickness', 0.01)}, 
                        {belt_info.get('geometry', {}).get('width', 0.8)}
                    );
                    const beltMaterial = new THREE.MeshLambertMaterial({{ color: 0x2563eb }});
                    conveyor = new THREE.Mesh(beltGeometry, beltMaterial);
                    conveyor.position.y = 0.5;
                    scene.add(conveyor);
                    
                    // Tạo con lăn
                    createIdlers();
                    
                    // Tạo khung đỡ
                    createSupportStructure();
                }}
                
                function createIdlers() {{
                    const idlerCount = {support_info.get('carrying_idlers', {}).get('count', 5)};
                    const spacing = {support_info.get('carrying_idlers', {}).get('spacing', 2.0)};
                    const diameter = {support_info.get('carrying_idlers', {}).get('diameter', 0.15)};
                    
                    for (let i = 0; i < idlerCount; i++) {{
                        const idlerGeometry = new THREE.CylinderGeometry(diameter/2, diameter/2, {belt_info.get('geometry', {}).get('width', 0.8)}, 8);
                        const idlerMaterial = new THREE.MeshLambertMaterial({{ color: 0x6b7280 }});
                        const idler = new THREE.Mesh(idlerGeometry, idlerMaterial);
                        
                        idler.rotation.z = Math.PI / 2;
                        idler.position.x = (i - idlerCount/2) * spacing;
                        idler.position.y = diameter/2;
                        
                        scene.add(idler);
                    }}
                }}
                
                function createSupportStructure() {{
                    const length = {belt_info.get('geometry', {}).get('length', 10)};
                    const width = {belt_info.get('geometry', {}).get('width', 0.8)};
                    
                    // Tạo khung đỡ
                    const frameGeometry = new THREE.BoxGeometry(length, 0.1, 0.1);
                    const frameMaterial = new THREE.MeshLambertMaterial({{ color: 0x374151 }});
                    
                    // Khung dọc
                    const leftFrame = new THREE.Mesh(frameGeometry, frameMaterial);
                    leftFrame.position.set(0, 0.05, -width/2 - 0.05);
                    scene.add(leftFrame);
                    
                    const rightFrame = new THREE.Mesh(frameGeometry, frameMaterial);
                    rightFrame.position.set(0, 0.05, width/2 + 0.05);
                    scene.add(rightFrame);
                    
                    // Khung ngang
                    const crossFrameGeometry = new THREE.BoxGeometry(0.1, 0.1, width + 0.2);
                    const crossFrame = new THREE.Mesh(crossFrameGeometry, frameMaterial);
                    crossFrame.position.set(0, 0.05, 0);
                    scene.add(crossFrame);
                }}
                
                function setupLighting() {{
                    // Ambient light
                    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
                    scene.add(ambientLight);
                    
                    // Directional light
                    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                    directionalLight.position.set(10, 10, 5);
                    directionalLight.castShadow = true;
                    directionalLight.shadow.mapSize.width = 2048;
                    directionalLight.shadow.mapSize.height = 2048;
                    scene.add(directionalLight);
                }}
                
                function animate() {{
                    requestAnimationFrame(animate);
                    
                    if (isAnimating) {{
                        // Animation cho băng tải
                        if (conveyor) {{
                            conveyor.rotation.y += 0.01;
                        }}
                    }}
                    
                    renderer.render(scene, camera);
                }}
                
                function toggleAnimation() {{
                    isAnimating = !isAnimating;
                    const btn = event.target;
                    btn.textContent = isAnimating ? '⏸️ Tạm dừng' : '▶️ Phát';
                }}
                
                function resetView() {{
                    camera.position.set(10, 5, 10);
                    camera.lookAt(0, 0, 0);
                }}
                
                function toggleWireframe() {{
                    if (conveyor) {{
                        conveyor.material.wireframe = !conveyor.material.wireframe;
                    }}
                }}
                
                function onWindowResize() {{
                    camera.aspect = window.innerWidth / window.innerHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(window.innerWidth, window.innerHeight);
                }}
                
                // Khởi tạo khi trang load xong
                window.addEventListener('load', init);
            </script>
        </body>
        </html>
        """
        
        return html
