"""
Enhanced 3D Visualization Widget
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QCheckBox, QComboBox, QLabel, QPushButton, 
                             QSlider, QSpinBox, QDoubleSpinBox, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from .core.model_generator import ConveyorModelGenerator
from .core.animation_engine import ConveyorAnimationEngine
from .templates.html_templates import ENHANCED_HTML_TEMPLATE, SIMPLE_HTML_TEMPLATE
from .templates.js_templates import ENHANCED_JS_TEMPLATE, BASIC_JS_TEMPLATE


class EnhancedVisualization3DWidget(QWidget):
    """Widget visualization 3D nâng cấp"""
    
    # Signals
    visualization_updated = pyqtSignal(dict)
    component_selected = pyqtSignal(str)
    animation_state_changed = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model_generator = None
        self.animation_engine = None
        self.current_data = {}
        self.visualization_mode = 'enhanced'
        
        self._setup_ui()
        self._setup_enhanced_features()
        self._setup_connections()
        
        # Timer cho performance monitoring
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self._update_performance_info)
        self.performance_timer.start(1000)  # Cập nhật mỗi giây
    
    def _setup_ui(self):
        """Thiết lập giao diện cơ bản"""
        self.main_layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("🎯 Băng tải 3D nâng cao")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Mode selector
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Nâng cao", "Đơn giản", "Phân tích"])
        self.mode_combo.setCurrentText("Nâng cao")
        header_layout.addWidget(QLabel("Chế độ:"))
        header_layout.addWidget(self.mode_combo)
        
        self.main_layout.addLayout(header_layout)
        
        # Main content area
        self.content_layout = QHBoxLayout()
        
        # Left panel - Controls
        self.left_panel = self._create_left_panel()
        self.content_layout.addWidget(self.left_panel, 1)
        
        # Center - Visualization area
        self.visualization_area = self._create_visualization_area()
        self.content_layout.addWidget(self.visualization_area, 4)
        
        # Right panel - Info
        self.right_panel = self._create_right_panel()
        self.content_layout.addWidget(self.right_panel, 1)
        
        self.main_layout.addLayout(self.content_layout)
        
        # Bottom panel - Animation controls
        self.bottom_panel = self._create_bottom_panel()
        self.main_layout.addWidget(self.bottom_panel)
    
    def _create_left_panel(self):
        """Tạo panel bên trái với các controls"""
        panel = QGroupBox("🎛️ Điều khiển")
        layout = QVBoxLayout(panel)
        
        # Component visibility controls
        component_group = QGroupBox("Thành phần hiển thị")
        component_layout = QVBoxLayout(component_group)
        
        self.chk_belt_system = QCheckBox("Băng tải")
        self.chk_belt_system.setChecked(True)
        component_layout.addWidget(self.chk_belt_system)
        
        self.chk_drive_system = QCheckBox("Hệ truyền động")
        self.chk_drive_system.setChecked(True)
        component_layout.addWidget(self.chk_drive_system)
        
        self.chk_support_structure = QCheckBox("Khung đỡ")
        self.chk_support_structure.setChecked(True)
        component_layout.addWidget(self.chk_support_structure)
        
        self.chk_material_flow = QCheckBox("Dòng vật liệu")
        self.chk_material_flow.setChecked(True)
        component_layout.addWidget(self.chk_material_flow)
        
        layout.addWidget(component_group)
        
        # Material controls
        material_group = QGroupBox("🎨 Chế độ hiển thị")
        material_layout = QVBoxLayout(material_group)
        
        self.material_combo = QComboBox()
        self.material_combo.addItems(["Thực tế", "Wireframe", "Phân tích nhiệt"])
        material_layout.addWidget(QLabel("Chế độ:"))
        material_layout.addWidget(self.material_combo)
        
        layout.addWidget(material_group)
        
        # Camera controls
        camera_group = QGroupBox("📷 Góc nhìn")
        camera_layout = QVBoxLayout(camera_group)
        
        self.camera_preset_combo = QComboBox()
        self.camera_preset_combo.addItems([
            "Tổng quan", "Hệ truyền động", "Con lăn", "Băng tải", "Tùy chỉnh"
        ])
        camera_layout.addWidget(QLabel("Góc nhìn:"))
        camera_layout.addWidget(self.camera_preset_combo)
        
        self.reset_camera_btn = QPushButton("🔄 Reset camera")
        camera_layout.addWidget(self.reset_camera_btn)
        
        layout.addWidget(camera_group)
        
        # Performance controls
        performance_group = QGroupBox("⚡ Hiệu suất")
        performance_layout = QVBoxLayout(performance_group)
        
        self.chk_shadows = QCheckBox("Bóng đổ")
        self.chk_shadows.setChecked(True)
        performance_layout.addWidget(self.chk_shadows)
        
        self.chk_antialiasing = QCheckBox("Khử răng cưa")
        self.chk_antialiasing.setChecked(True)
        performance_layout.addWidget(self.chk_antialiasing)
        
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 5)
        self.quality_slider.setValue(3)
        self.quality_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.quality_slider.setTickInterval(1)
        performance_layout.addWidget(QLabel("Chất lượng:"))
        performance_layout.addWidget(self.quality_slider)
        
        layout.addWidget(performance_group)
        
        layout.addStretch()
        return panel
    
    def _create_visualization_area(self):
        """Tạo khu vực visualization chính"""
        area = QGroupBox("🎮 Khu vực 3D")
        layout = QVBoxLayout(area)
        
        # Placeholder cho WebEngine
        self.visualization_placeholder = QLabel("Khu vực visualization 3D\n(WebEngine sẽ được tích hợp ở đây)")
        self.visualization_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.visualization_placeholder.setStyleSheet("""
            QLabel {
                background-color: #2c3e50;
                color: white;
                border: 2px dashed #34495e;
                border-radius: 8px;
                padding: 40px;
                font-size: 16px;
            }
        """)
        layout.addWidget(self.visualization_placeholder)
        
        return area
    
    def _create_right_panel(self):
        """Tạo panel bên phải với thông tin"""
        panel = QGroupBox("📊 Thông tin")
        layout = QVBoxLayout(panel)
        
        # System info
        system_group = QGroupBox("Hệ thống")
        system_layout = QVBoxLayout(system_group)
        
        self.lbl_length = QLabel("Chiều dài: --")
        self.lbl_width = QLabel("Chiều rộng: --")
        self.lbl_height = QLabel("Chiều cao: --")
        self.lbl_speed = QLabel("Tốc độ: --")
        self.lbl_power = QLabel("Công suất: --")
        
        system_layout.addWidget(self.lbl_length)
        system_layout.addWidget(self.lbl_width)
        system_layout.addWidget(self.lbl_height)
        system_layout.addWidget(self.lbl_speed)
        system_layout.addWidget(self.lbl_power)
        
        layout.addWidget(system_group)
        
        # Component info
        component_info_group = QGroupBox("Thành phần")
        component_info_layout = QVBoxLayout(component_info_group)
        
        self.lbl_belt_type = QLabel("Băng tải: --")
        self.lbl_motor_info = QLabel("Động cơ: --")
        self.lbl_gearbox_info = QLabel("Hộp số: --")
        self.lbl_idler_count = QLabel("Con lăn: --")
        
        component_info_layout.addWidget(self.lbl_belt_type)
        component_info_layout.addWidget(self.lbl_motor_info)
        component_info_layout.addWidget(self.lbl_gearbox_info)
        component_info_layout.addWidget(self.lbl_idler_count)
        
        layout.addWidget(component_info_group)
        
        # Performance info
        performance_info_group = QGroupBox("Hiệu suất")
        performance_info_layout = QVBoxLayout(performance_info_group)
        
        self.lbl_fps = QLabel("FPS: --")
        self.lbl_triangles = QLabel("Triangles: --")
        self.lbl_memory = QLabel("Memory: -- MB")
        
        performance_info_layout.addWidget(self.lbl_fps)
        performance_info_layout.addWidget(self.lbl_triangles)
        performance_info_layout.addWidget(self.lbl_memory)
        
        layout.addWidget(performance_info_group)
        
        layout.addStretch()
        return panel
    
    def _create_bottom_panel(self):
        """Tạo panel dưới với animation controls"""
        panel = QGroupBox("🎬 Điều khiển animation")
        layout = QHBoxLayout(panel)
        
        # Animation controls
        self.play_pause_btn = QPushButton("⏸️ Tạm dừng")
        self.play_pause_btn.setCheckable(True)
        self.play_pause_btn.setChecked(True)
        layout.addWidget(self.play_pause_btn)
        
        self.reset_btn = QPushButton("🔄 Reset")
        layout.addWidget(self.reset_btn)
        
        layout.addWidget(QLabel("Tốc độ:"))
        
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(10, 300)
        self.speed_slider.setValue(100)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(50)
        layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("100%")
        layout.addWidget(self.speed_label)
        
        # Additional controls
        self.wireframe_btn = QPushButton("📐 Wireframe")
        self.wireframe_btn.setCheckable(True)
        layout.addWidget(self.wireframe_btn)
        
        self.fullscreen_btn = QPushButton("⛶ Fullscreen")
        layout.addWidget(self.fullscreen_btn)
        
        self.export_btn = QPushButton("💾 Xuất")
        layout.addWidget(self.export_btn)
        
        layout.addStretch()
        return panel
    
    def _setup_enhanced_features(self):
        """Thiết lập tính năng nâng cao"""
        # Khởi tạo các thành phần
        self._initialize_components()
        
        # Thiết lập default values
        self._setup_default_values()
    
    def _initialize_components(self):
        """Khởi tạo các thành phần"""
        # Component builders sẽ được khởi tạo khi có dữ liệu
        pass
    
    def _setup_default_values(self):
        """Thiết lập giá trị mặc định"""
        # Camera preset
        self.camera_preset_combo.setCurrentText("Tổng quan")
        
        # Material mode
        self.material_combo.setCurrentText("Thực tế")
        
        # Performance settings
        self.quality_slider.setValue(3)
        self.chk_shadows.setChecked(True)
        self.chk_antialiasing.setChecked(True)
    
    def _setup_connections(self):
        """Thiết lập các kết nối signal-slot"""
        # Mode change
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        
        # Component visibility
        self.chk_belt_system.toggled.connect(self._on_component_visibility_changed)
        self.chk_drive_system.toggled.connect(self._on_component_visibility_changed)
        self.chk_support_structure.toggled.connect(self._on_component_visibility_changed)
        self.chk_material_flow.toggled.connect(self._on_component_visibility_changed)
        
        # Material mode
        self.material_combo.currentTextChanged.connect(self._on_material_mode_changed)
        
        # Camera controls
        self.camera_preset_combo.currentTextChanged.connect(self._on_camera_preset_changed)
        self.reset_camera_btn.clicked.connect(self._on_reset_camera)
        
        # Performance controls
        self.chk_shadows.toggled.connect(self._on_shadows_toggled)
        self.chk_antialiasing.toggled.connect(self._on_antialiasing_toggled)
        self.quality_slider.valueChanged.connect(self._on_quality_changed)
        
        # Animation controls
        self.play_pause_btn.toggled.connect(self._on_play_pause_toggled)
        self.reset_btn.clicked.connect(self._on_reset_animation)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        self.wireframe_btn.toggled.connect(self._on_wireframe_toggled)
        self.fullscreen_btn.clicked.connect(self._on_fullscreen)
        self.export_btn.clicked.connect(self._on_export)
    
    def _on_mode_changed(self, mode):
        """Xử lý khi thay đổi chế độ"""
        if mode == "Nâng cao":
            self.visualization_mode = 'enhanced'
        elif mode == "Đơn giản":
            self.visualization_mode = 'simple'
        elif mode == "Phân tích":
            self.visualization_mode = 'analysis'
        
        self._update_visualization_mode()
    
    def _on_component_visibility_changed(self, checked):
        """Xử lý khi thay đổi hiển thị thành phần"""
        # Cập nhật visibility của các thành phần
        self._update_component_visibility()
    
    def _on_material_mode_changed(self, mode):
        """Xử lý khi thay đổi chế độ material"""
        # Cập nhật material mode
        self._update_material_mode(mode)
    
    def _on_camera_preset_changed(self, preset):
        """Xử lý khi thay đổi camera preset"""
        # Cập nhật camera position
        self._update_camera_preset(preset)
    
    def _on_reset_camera(self):
        """Reset camera về vị trí ban đầu"""
        # Reset camera
        self._reset_camera()
    
    def _on_shadows_toggled(self, enabled):
        """Xử lý khi toggle shadows"""
        # Cập nhật shadow settings
        self._update_shadow_settings(enabled)
    
    def _on_antialiasing_toggled(self, enabled):
        """Xử lý khi toggle antialiasing"""
        # Cập nhật antialiasing settings
        self._update_antialiasing_settings(enabled)
    
    def _on_quality_changed(self, quality):
        """Xử lý khi thay đổi chất lượng"""
        # Cập nhật quality settings
        self._update_quality_settings(quality)
    
    def _on_play_pause_toggled(self, playing):
        """Xử lý khi toggle play/pause"""
        if playing:
            self.play_pause_btn.setText("⏸️ Tạm dừng")
            self.animation_state_changed.emit(True)
        else:
            self.play_pause_btn.setText("▶️ Phát")
            self.animation_state_changed.emit(False)
    
    def _on_reset_animation(self):
        """Reset animation"""
        # Reset tất cả animation
        self._reset_animation()
    
    def _on_speed_changed(self, speed):
        """Xử lý khi thay đổi tốc độ"""
        self.speed_label.setText(f"{speed}%")
        # Cập nhật animation speed
        self._update_animation_speed(speed / 100.0)
    
    def _on_wireframe_toggled(self, enabled):
        """Xử lý khi toggle wireframe"""
        # Cập nhật wireframe mode
        self._update_wireframe_mode(enabled)
    
    def _on_fullscreen(self):
        """Xử lý khi click fullscreen"""
        # Toggle fullscreen
        self._toggle_fullscreen()
    
    def _on_export(self):
        """Xử lý khi export"""
        # Export visualization
        self._export_visualization()
    
    def update_enhanced_visualization(self, params, result):
        """Cập nhật visualization nâng cao"""
        try:
            # Tạo mô hình 3D từ tham số
            self.model_generator = ConveyorModelGenerator(params, result)
            model_data = self.model_generator.generate_complete_model()
            
            # Tạo animation engine
            self.animation_engine = ConveyorAnimationEngine(model_data)
            
            # Lưu dữ liệu hiện tại
            self.current_data = model_data
            
            # Cập nhật visualization
            self._load_enhanced_scene(model_data)
            
            # Cập nhật thông tin hiển thị
            self._update_display_info(model_data)
            
            # Emit signal
            self.visualization_updated.emit(model_data)
            
        except Exception as e:
            print(f"Lỗi khi cập nhật visualization: {e}")
            # Fallback về chế độ đơn giản
            self._fallback_to_simple_mode(params, result)
    
    def _load_enhanced_scene(self, model_data):
        """Tải scene nâng cao"""
        try:
            # Chọn template dựa trên mode
            if self.visualization_mode == 'enhanced':
                html_template = ENHANCED_HTML_TEMPLATE
                js_template = ENHANCED_JS_TEMPLATE
            elif self.visualization_mode == 'simple':
                html_template = SIMPLE_HTML_TEMPLATE
                js_template = BASIC_JS_TEMPLATE
            else:
                html_template = ENHANCED_HTML_TEMPLATE
                js_template = ENHANCED_JS_TEMPLATE
            
            # Format template với dữ liệu
            html_content = self._format_html_template(html_template, model_data)
            js_content = self._format_js_template(js_template, model_data)
            
            # Tạo HTML hoàn chỉnh
            complete_html = html_content.replace('{enhanced_js}', js_content)
            
            # Load vào WebEngine (placeholder)
            self._load_html_content(complete_html)
            
        except Exception as e:
            print(f"Lỗi khi tải scene: {e}")
    
    def _format_html_template(self, template, data):
        """Format HTML template với dữ liệu"""
        try:
            # Extract data từ model_data
            belt_data = data.get('belt_system', {})
            drive_data = data.get('drive_system', {})
            support_data = data.get('support_structure', {})
            
            # Format template
            formatted = template.format(
                length=belt_data.get('properties', {}).get('length_m', 10.0),
                width=belt_data.get('properties', {}).get('width_m', 0.5),
                height=belt_data.get('properties', {}).get('height_m', 1.0),
                inclination=data.get('inclination_deg', 0.0),
                speed=data.get('belt_speed_mps', 2.0),
                power=drive_data.get('motor', {}).get('power_kw', 5.5),
                ratio=drive_data.get('gearbox', {}).get('ratio', 20.0),
                libs=self._get_threejs_libraries()
            )
            
            return formatted
            
        except Exception as e:
            print(f"Lỗi khi format HTML template: {e}")
            return template
    
    def _format_js_template(self, template, data):
        """Format JavaScript template với dữ liệu"""
        try:
            # Format template với dữ liệu
            formatted = template.replace('{data}', str(data))
            return formatted
            
        except Exception as e:
            print(f"Lỗi khi format JS template: {e}")
            return template
    
    def _get_threejs_libraries(self):
        """Lấy thư viện Three.js"""
        return """
        <script src="ui/js/three.min.js"></script>
        <script src="ui/js/GLTFLoader.js"></script>
        """
    
    def _load_html_content(self, html_content):
        """Load HTML content vào WebEngine"""
        # Placeholder - sẽ được tích hợp với WebEngine
        print("Loading HTML content into WebEngine...")
        print(f"Content length: {len(html_content)} characters")
    
    def _update_display_info(self, model_data):
        """Cập nhật thông tin hiển thị"""
        try:
            belt_data = model_data.get('belt_system', {})
            drive_data = model_data.get('drive_system', {})
            support_data = model_data.get('support_structure', {})
            
            # Cập nhật thông tin hệ thống
            self.lbl_length.setText(f"Chiều dài: {belt_data.get('properties', {}).get('length_m', 0):.1f} m")
            self.lbl_width.setText(f"Chiều rộng: {belt_data.get('properties', {}).get('width_m', 0):.2f} m")
            self.lbl_height.setText(f"Chiều cao: {belt_data.get('properties', {}).get('height_m', 0):.1f} m")
            self.lbl_speed.setText(f"Tốc độ: {model_data.get('belt_speed_mps', 0):.2f} m/s")
            self.lbl_power.setText(f"Công suất: {drive_data.get('motor', {}).get('power_kw', 0):.1f} kW")
            
            # Cập nhật thông tin thành phần
            self.lbl_belt_type.setText(f"Băng tải: {belt_data.get('properties', {}).get('belt_type', 'EP')}")
            self.lbl_motor_info.setText(f"Động cơ: {drive_data.get('motor', {}).get('power_kw', 0):.1f} kW")
            self.lbl_gearbox_info.setText(f"Hộp số: {drive_data.get('gearbox', {}).get('ratio', 0):.1f}")
            self.lbl_idler_count.setText(f"Con lăn: {support_data.get('properties', {}).get('total_carrying_idlers', 0)}")
            
        except Exception as e:
            print(f"Lỗi khi cập nhật thông tin hiển thị: {e}")
    
    def _fallback_to_simple_mode(self, params, result):
        """Fallback về chế độ đơn giản"""
        print("Fallback về chế độ đơn giản...")
        # Implement fallback logic
    
    def _update_visualization_mode(self):
        """Cập nhật chế độ visualization"""
        if hasattr(self, 'current_data') and self.current_data:
            self._load_enhanced_scene(self.current_data)
    
    def _update_component_visibility(self):
        """Cập nhật visibility của các thành phần"""
        # Implement component visibility update
        pass
    
    def _update_material_mode(self, mode):
        """Cập nhật material mode"""
        # Implement material mode update
        pass
    
    def _update_camera_preset(self, preset):
        """Cập nhật camera preset"""
        # Implement camera preset update
        pass
    
    def _reset_camera(self):
        """Reset camera"""
        # Implement camera reset
        pass
    
    def _update_shadow_settings(self, enabled):
        """Cập nhật shadow settings"""
        # Implement shadow settings update
        pass
    
    def _update_antialiasing_settings(self, enabled):
        """Cập nhật antialiasing settings"""
        # Implement antialiasing settings update
        pass
    
    def _update_quality_settings(self, quality):
        """Cập nhật quality settings"""
        # Implement quality settings update
        pass
    
    def _reset_animation(self):
        """Reset animation"""
        # Implement animation reset
        pass
    
    def _update_animation_speed(self, speed):
        """Cập nhật animation speed"""
        # Implement animation speed update
        pass
    
    def _update_wireframe_mode(self, enabled):
        """Cập nhật wireframe mode"""
        # Implement wireframe mode update
        pass
    
    def _toggle_fullscreen(self):
        """Toggle fullscreen"""
        # Implement fullscreen toggle
        pass
    
    def _export_visualization(self):
        """Export visualization"""
        # Implement export functionality
        pass
    
    def _update_performance_info(self):
        """Cập nhật thông tin hiệu suất"""
        # Placeholder - sẽ được cập nhật từ WebEngine
        self.lbl_fps.setText("FPS: 60")
        self.lbl_triangles.setText("Triangles: 1,234")
        self.lbl_memory.setText("Memory: 45 MB")
    
    def get_visualization_data(self):
        """Lấy dữ liệu visualization hiện tại"""
        return self.current_data
    
    def set_visualization_mode(self, mode):
        """Thiết lập chế độ visualization"""
        self.mode_combo.setCurrentText(mode)
    
    def toggle_animation(self, playing):
        """Toggle animation"""
        self.play_pause_btn.setChecked(playing)
    
    def set_animation_speed(self, speed):
        """Thiết lập tốc độ animation (0.1 - 3.0)"""
        speed_percent = int(speed * 100)
        self.speed_slider.setValue(speed_percent)
    
    def highlight_component(self, component_type):
        """Highlight thành phần được chọn"""
        self.component_selected.emit(component_type)
    
    def refresh_visualization(self):
        """Refresh visualization"""
        if hasattr(self, 'current_data') and self.current_data:
            self._load_enhanced_scene(self.current_data)
