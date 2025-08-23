# ui/main_window_3d_enhanced.py
# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QFrame, QHBoxLayout, QVBoxLayout, 
    QLabel, QFileDialog, QMessageBox, QTableWidgetItem, QDialog, QTextBrowser,
    QDockWidget
)
from PySide6.QtGui import QAction, QIcon, QActionGroup
from PySide6.QtCore import Qt, QTimer, QThread

# --- [BẮT ĐẦU NÂNG CẤP TỐI ƯU HÓA] ---
from .ui_components_3d_enhanced import InputsPanel, Enhanced3DResultsPanel
from .chat.chat_panel import ChatPanel
from .styles import LIGHT, DARK
from core.models import ConveyorParameters, CalculationResult
from core.optimizer.models import OptimizerSettings
from core.thread_worker import CalculationThread
from core.optimizer_worker import OptimizerWorker # Import the new worker
from core.specs import VERSION, COPYRIGHT, STANDARD_WIDTHS, ACTIVE_MATERIAL_DB, ACTIVE_BELT_SPECS
from reports.exporter_pdf import export_pdf_report
from reports.exporter_excel import export_excel_report
from core.db import load_database
from .ad_banner_widget import AdBannerWidget
import traceback
import os
from pathlib import Path
from dotenv import load_dotenv
from core.licensing import assigned_account_id
# --- [KẾT THÚC NÂNG CẤP TỐI ƯU HÓA] ---

class Enhanced3DConveyorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load environment variables from .env file
        root_dir = Path(__file__).parent.parent.absolute()
        
        # Try multiple possible locations for .env file
        possible_env_paths = [
            root_dir / '.env',  # Same directory as exe
            root_dir / '_internal' / '.env',  # _internal subdirectory
            root_dir / '..' / '.env',  # Parent directory
        ]
        
        env_loaded = False
        for env_path in possible_env_paths:
            if env_path.exists():
                print(f"Loading .env from: {env_path}")
                load_dotenv(dotenv_path=env_path)
                env_loaded = True
                break
        
        if not env_loaded:
            print("Warning: No .env file found in any expected location")
            print("Available paths checked:")
            for env_path in possible_env_paths:
                print(f"  - {env_path}: {'exists' if env_path.exists() else 'not found'}")
        
        # Set default INDEX_DIR if not provided - Try multiple possible locations
        if not os.getenv('INDEX_DIR'):
            possible_index_paths = [
                root_dir / 'data' / 'index',  # Same directory as exe
                root_dir / '_internal' / 'data' / 'index',  # _internal subdirectory
                root_dir / '..' / 'data' / 'index',  # Parent directory
            ]
            
            index_dir = None
            for idx_path in possible_index_paths:
                if idx_path.exists():
                    index_dir = idx_path
                    break
            
            if index_dir is None:
                # Create default index directory
                index_dir = root_dir / 'data' / 'index'
                print(f"Creating default index directory: {index_dir}")
                index_dir.mkdir(parents=True, exist_ok=True)
            
            os.environ['INDEX_DIR'] = str(index_dir)
            print(f"Using INDEX_DIR: {os.environ['INDEX_DIR']}")
            
        self.setWindowTitle(f"Convayor Calculator AI v{VERSION}")
        self.resize(1600, 1000)
        self.current_theme = "light"
        self.setStyleSheet(LIGHT)
        
        # --- [BẮT ĐẦU NÂNG CẤP UI] ---
        # Cải thiện giao diện tổng thể
        self.setStyleSheet(LIGHT + """
            QMainWindow {
                background-color: #f8fafc;
            }
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                background-color: #ffffff;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #f1f5f9;
                color: #475569;
                padding: 8px 16px;
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
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #374151;
            }
            /* Loại bỏ CSS cho QPushButton để tránh xung đột với UI components */
            /* QPushButton {
                background-color: #3b82f6;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
            QPushButton#primary {
                background-color: #059669;
                font-size: 14px;
                padding: 12px 24px;
            }
            QPushButton#primary:hover {
                background-color: #047857;
            } */
        """)
        # --- [KẾT THÚC NÂNG CẤP UI] ---
        
        # Thiết lập icon cho cửa sổ
        try:
            from core.utils.paths import resource_path
            icon_path = resource_path("icon.ico")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            print(f"Không thể tải icon: {e}")
        
        self.params: ConveyorParameters | None = None
        self.current_result: CalculationResult | None = None
        self.db_path = ""

        self._setup_ui()
        self._setup_menu()
        self._connect()
        self._setup_chat_panel()  # Add chat panel

        self.statusBar().showMessage(f"Sẵn sàng | {COPYRIGHT}")
        self._populate_defaults()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self._header())

        splitter = QSplitter(Qt.Horizontal)
        self.inputs = InputsPanel()
        self.results = Enhanced3DResultsPanel()
        splitter.addWidget(self.inputs)
        splitter.addWidget(self.results)
        splitter.setSizes([520, 1080])
        main_layout.addWidget(splitter)

    def _header(self) -> QWidget:
        h = QFrame()
        h.setObjectName("headerFrame")
        lay = QHBoxLayout(h)
        lay.setContentsMargins(15, 5, 15, 5)
        t1 = QLabel("Convayor Calculator AI")
        t1.setObjectName("headerTitle")
        t2 = QLabel(f"Phiên bản {VERSION} | DIN 22101, CEMA, ISO 5048")
        t2.setObjectName("headerSubtitle")
        title_box = QWidget()
        title_layout = QVBoxLayout(title_box)
        title_layout.setContentsMargins(0,0,0,0)
        title_layout.setSpacing(0)
        title_layout.addWidget(t1)
        title_layout.addWidget(t2)
        lay.addWidget(title_box)
        lay.addStretch(1)
        self.ad_banner = AdBannerWidget(
            parent=self,
            html_filename="ads_banner.html",  # file HTML bạn đã dán JS Adsterra vào
            width=728,
            height=90,
            reload_interval_sec=0            # =0: không tự reload (bạn đổi nếu muốn)
        )
        lay.addWidget(self.ad_banner)

        return h

    def _setup_menu(self):
        menubar = self.menuBar()
        m_file = menubar.addMenu("📁 Tệp")
        act_open_db = QAction("🗃️ Chọn cơ sở dữ liệu...", self)
        act_open_db.triggered.connect(self.choose_database)
        act_export_pdf = QAction("📑 Xuất PDF", self)
        act_export_pdf.triggered.connect(self.export_pdf)
        act_export_excel = QAction("📊 Xuất Excel", self)
        act_export_excel.triggered.connect(self.export_excel)
        m_file.addAction(act_open_db)
        m_file.addSeparator()
        m_file.addAction(act_export_pdf)
        m_file.addAction(act_export_excel)

        m_tools = menubar.addMenu("🔧 Công cụ")
        act_validate = QAction("✅ Kiểm định thiết kế", self)
        act_validate.triggered.connect(self.validate_design)
        m_tools.addAction(act_validate)
        
        # Add Chat Assistant action
        self.act_chat = QAction("💬 Trợ lý kỹ thuật", self)
        self.act_chat.setCheckable(True)
        self.act_chat.setChecked(True)  # Initially checked since chat is visible
        self.act_chat.triggered.connect(self._toggle_chat_panel)
        m_tools.addAction(self.act_chat)

        # License menu
        m_license = menubar.addMenu("🔒 Giấy phép")
        act_show_acc = QAction("👤 Tài khoản được gán", self)
        act_show_acc.triggered.connect(self._show_assigned_account)
        m_license.addAction(act_show_acc)

        m_appearance = menubar.addMenu("🎨 Giao diện")
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)
        act_light_theme = QAction("Sáng", self, checkable=True)
        act_light_theme.setChecked(True)
        act_light_theme.triggered.connect(lambda: self._set_theme("light"))
        act_dark_theme = QAction("Tối", self, checkable=True)
        act_dark_theme.triggered.connect(lambda: self._set_theme("dark"))
        theme_group.addAction(act_light_theme)
        theme_group.addAction(act_dark_theme)
        m_appearance.addAction(act_light_theme)
        m_appearance.addAction(act_dark_theme)

        m_help = menubar.addMenu("❓ Trợ giúp")
        act_about = QAction("ℹ️ Giới thiệu", self)
        act_about.triggered.connect(self._show_about_dialog)
        
        # --- [BẮT ĐẦU THÊM MỚI] ---
        act_manual = QAction("📖 Hướng dẫn sử dụng", self)
        act_manual.triggered.connect(self._show_user_manual)
        # --- [KẾT THÚC THÊM MỚI] ---
        
        m_help.addAction(act_about)
        m_help.addAction(act_manual) # Thêm mục mới vào menu

    # --- [BẮT ĐẦU THÊM MỚI] ---
    def _show_user_manual(self):
        """Hiển thị cửa sổ Hướng dẫn sử dụng."""
        manual_dialog = QDialog(self)
        manual_dialog.setWindowTitle("Hướng dẫn sử dụng")
        manual_dialog.resize(800, 700)
        manual_dialog.setWindowFlags(self.windowFlags() | Qt.Window)

        layout = QVBoxLayout(manual_dialog)
        text_browser = QTextBrowser(manual_dialog)
        
        # Nội dung được lấy từ bản nháp đã duyệt
        manual_html = """
        <html><body style='font-family: Segoe UI, sans-serif; font-size: 15px; line-height: 1.6;'>
        <h1>Hướng dẫn sử dụng Convayor Calculator AI</h1>
        <p>Chào mừng bạn đến với Convayor Calculator AI. Tài liệu này sẽ hướng dẫn bạn từng bước sử dụng phần mềm để thiết kế, phân tích và tối ưu hóa hệ thống băng tải một cách hiệu quả.</p>
        <hr>
        <h3>1. Bắt đầu: Đăng nhập và Quản lý tài khoản</h3>
        <p>Khi khởi động, bạn sẽ thấy màn hình đăng nhập.</p>
        <ul>
            <li><b>Đăng nhập:</b>
                <ul>
                    <li>Nếu bạn đã có tài khoản, hãy nhập <b>Username</b> và <b>Password</b>, sau đó nhấn nút <b>Login</b>.</li>
                    <li>Tài khoản quản trị mặc định là: Username: <code>Admin</code>, Password: <code>123567</code></li>
                </ul>
            </li>
            <li><b>Tạo tài khoản mới:</b>
                <ul>
                    <li>Nhập tên người dùng và mật khẩu bạn muốn tạo vào hai ô tương ứng.</li>
                    <li>Nhấn nút <b>Create Account</b>. Một thông báo sẽ xác nhận khi tài khoản được tạo thành công.</li>
                </ul>
            </li>
            <li><b>Thoát:</b> Nhấn nút <b>Exit</b> để đóng ứng dụng.</li>
        </ul>
        <h3>2. Giao diện chính</h3>
        <p>Sau khi đăng nhập thành công, giao diện chính sẽ hiện ra, được chia thành hai khu vực:</p>
        <ul>
            <li><b>Bên trái (Panel Nhập liệu):</b> Nơi bạn cung cấp tất cả các thông số kỹ thuật cho dự án băng tải của mình.</li>
            <li><b>Bên phải (Panel Kết quả):</b> Nơi hiển thị tất cả kết quả tính toán, phân tích và biểu đồ sau khi bạn nhấn nút tính toán.</li>
        </ul>
        <h3>3. Hướng dẫn tính toán từng bước</h3>
        <p>Bạn cần điền thông tin vào các mục trong <b>Panel Nhập liệu</b> từ trên xuống dưới.</p>
        <h4>Bước 1: Nhập thông tin dự án</h4>
        <p>Điền các thông tin cơ bản để quản lý và nhận dạng bản tính của bạn (Tên dự án, Người thiết kế, Khách hàng, Công trình).</p>
        <h4>Bước 2: Lựa chọn vật liệu và đặc tính</h4>
        <p>Đây là bước quan trọng, quyết định đến tải trọng và công suất. Chọn <b>Loại vật liệu</b> từ danh sách, các thông số liên quan sẽ tự động cập nhật.</p>
        <p style='border-left: 3px solid #0078d4; padding-left: 10px; color: #555;'><i><b>Mẹo:</b> Di chuột qua từng ô nhập liệu để xem giải thích chi tiết (tooltip) về ý nghĩa của thông số đó.</i></p>
        <h4>Bước 3: Cấu hình điều kiện vận hành</h4>
        <p>Xác định các yêu cầu về hiệu suất của băng tải như <b>Tiêu chuẩn</b> tính toán (<b>khuyến nghị DIN</b>), <b>Lưu lượng yêu cầu</b>, <b>Chiều dài (L)</b> và <b>Độ cao nâng (H)</b>.</p>
        <h4>Bước 4: Cấu hình băng tải</h4>
        <p>Lựa chọn các thành phần cơ khí của hệ thống như <b>Bề rộng băng (B)</b>, <b>Loại băng</b>, và <b>Góc máng</b>.</p>
        <h4>Bước 5: Cấu hình hệ thống truyền động</h4>
        <p>Thiết lập các thông số liên quan đến động cơ và puly. Nếu chọn <b>Dual drive</b> (truyền động kép), một tùy chọn về <b>Tỷ lệ phân phối lực</b> sẽ xuất hiện.</p>
        <hr>
        <h3>4. Thực hiện tính toán</h3>
        <p>Sau khi đã nhập đầy đủ thông tin, bạn có 3 lựa chọn:</p>
        <ol>
            <li><b>TÍNH TOÁN CHI TIẾT:</b> Chạy phân tích đầy đủ và chính xác nhất.</li>
            <li><b>TÍNH TOÁN NHANH:</b> Thực hiện tính toán nhanh cho kết quả sơ bộ.</li>
            <li><b>TỐI ƯU NÂNG CAO:</b> Phần mềm sẽ tự động tìm kiếm các giải pháp thiết kế tốt nhất dựa trên mục tiêu bạn đã chọn.</li>
        </ol>
        <h3>5. Đọc và phân tích kết quả</h3>
        <p>Kết quả sẽ được hiển thị ở <b>Panel Kết quả</b> bên phải, bao gồm các chỉ số KPIs và các Tab chi tiết (Tổng quan, Cấu trúc, Phân tích kỹ thuật, Chi phí, Tóm tắt, Biểu đồ 2D).</p>
        <p><b>Lưu ý quan trọng:</b> Hệ số an toàn (SF) nên lớn hơn 8 để đảm bảo an toàn vận hành.</p>
        <h3>6. Các tính năng khác</h3>
        <p>Sử dụng thanh menu ở góc trên bên trái để truy cập các tính năng nâng cao như <b>Chọn cơ sở dữ liệu</b>, <b>Xuất PDF/Excel</b>, và thay đổi <b>Giao diện</b>.</p>
        </body></html>
        """
        text_browser.setHtml(manual_html)
        text_browser.setOpenExternalLinks(True)
        layout.addWidget(text_browser)
        manual_dialog.exec()
    # --- [KẾT THÚC THÊM MỚI] ---

    def _show_assigned_account(self):
        try:
            acc = assigned_account_id()
            QMessageBox.information(self, "Tài khoản", f"Máy này được gán: {acc}")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không xác định được tài khoản: {e}")



    def _setup_chat_panel(self):
        """Setup the chat panel as a floating dock widget."""
        self.chat_dock = QDockWidget("", self)  # Empty title as we have title in panel
        self.chat_dock.setWidget(ChatPanel())
        
        # Make it floating by default
        self.chat_dock.setFloating(True)
        
        # Allow docking on both sides
        self.chat_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.chat_dock)
        
        # Set size and position
        self.chat_dock.setMinimumWidth(350)
        self.chat_dock.resize(400, 600)
        
        # Style the dock widget
        self.chat_dock.setStyleSheet("""
            QDockWidget {
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                background-color: #f8fafc;
            }
            QDockWidget::title {
                background: transparent;
            }
        """)
        
        # Position it on the right side of the main window
        main_rect = self.geometry()
        chat_rect = self.chat_dock.geometry()
        self.chat_dock.move(
            main_rect.right() - chat_rect.width() - 20,
            main_rect.top() + 50
        )
        
        # Show by default
        self.chat_dock.show()

    def _set_theme(self, theme_name: str):
        if theme_name == "light":
            self.setStyleSheet(LIGHT)
            self.current_theme = "light"
        elif theme_name == "dark":
            self.setStyleSheet(DARK)
            self.current_theme = "dark"
        self._redraw_all_visualizations()

    def _populate_defaults(self):
        self.inputs.cbo_material.addItems(list(ACTIVE_MATERIAL_DB.keys()))
        self.inputs.cbo_width.addItems([str(w) for w in STANDARD_WIDTHS])
        self.inputs.cbo_width.setCurrentText("800")
        self.inputs.cbo_belt_type.addItems(list(ACTIVE_BELT_SPECS.keys()))
        # Thiết lập giá trị mặc định cho calculation_standard
        self.inputs.cbo_standard.setCurrentText("CEMA")
        self.inputs.update_drive_illustration(self.inputs.cbo_drive.currentText())
        
        # Cập nhật thông tin vật liệu mặc định
        if self.inputs.cbo_material.count() > 0:
            self._on_material_changed()

    def _connect(self):
        self.inputs.btn_calc.clicked.connect(self._full_calculate)
        self.inputs.btn_quick.clicked.connect(self._quick_calculate)
        self.inputs.btn_opt.clicked.connect(self._run_advanced_optimization) # Changed
        self.inputs.cbo_material.currentTextChanged.connect(self._on_material_changed)
        self.inputs.cbo_drive.currentTextChanged.connect(self.inputs.update_drive_illustration)
        self.results.chk_t2.stateChanged.connect(self._redraw_all_visualizations)
        self.results.chk_friction.stateChanged.connect(self._redraw_all_visualizations)
        self.results.chk_lift.stateChanged.connect(self._redraw_all_visualizations)
        # --- [BẮT ĐẦU NÂNG CẤP TỐI ƯU HÓA] ---
        self.results.optimizer_result_selected.connect(self._apply_optimizer_solution)
        # --- [KẾT THÚC NÂNG CẤP TỐI ƯU HÓA] ---

    def _collect(self) -> ConveyorParameters:
        i = self.inputs
        self.params = ConveyorParameters(
            calculation_standard=i.cbo_standard.currentText(),
            project_name=i.edt_project_name.text(),
            designer=i.edt_designer.text(),
            client=i.edt_client.text(),
            location=i.edt_location.text(),
            material=i.cbo_material.currentText(),
            density_tpm3=i.spn_density.value(),
            particle_size_mm=i.spn_particle.value(),
            angle_repose_deg=i.spn_angle.value(),
            material_temp_c=i.spn_temp.value(),
            is_abrasive=i.chk_abrasive.isChecked(),
            is_corrosive=i.chk_corrosive.isChecked(),
            is_dusty=i.chk_dusty.isChecked(),
            Qt_tph=i.spn_capacity.value(),
            L_m=i.spn_length.value(),
            H_m=i.spn_height.value(),
            inclination_deg=i.spn_incl.value(),
            V_mps=i.spn_speed.value(),
            operating_hours=i.spn_hours.value(),
            B_mm=int(i.cbo_width.currentText() or 0),
            belt_type=i.cbo_belt_type.currentText(),
            belt_thickness_mm=i.spn_thickness.value(),
            trough_angle_label=i.cbo_trough.currentText(),
            surcharge_angle_deg=i.spn_angle.value(),  # Luôn bằng góc nghiêng tự nhiên
            carrying_idler_spacing_m=i.spn_carrying.value(),
            return_idler_spacing_m=i.spn_return.value(),
            drive_type=i.cbo_drive.currentText(),
            motor_efficiency=i.spn_eta_m.value(),
            gearbox_efficiency=i.spn_eta_g.value(),
            mu_pulley=i.spn_mu.value(),
            wrap_deg=i.spn_wrap.value(),
            Kt_start=i.spn_Kt.value(),
            ambient_temp_c=i.spn_amb.value(),
            humidity_percent=i.spn_hum.value(),
            altitude_m=i.spn_alt.value(),
            dusty_environment=i.chk_dusty_env.isChecked(),
            corrosive_environment=i.chk_corr_env.isChecked(),
            explosion_proof=i.chk_ex.isChecked(),
            dual_drive_ratio=i.cbo_dual_drive_ratio.currentText(),
            # --- [BẮT ĐẦU NÂNG CẤP TRUYỀN ĐỘNG] ---
            motor_rpm=int(i.cbo_motor_rpm.currentText()),
            # --- [KẾT THÚC NÂNG CẤP TRUYỀN ĐỘNG] ---
            
            # --- [BẮT ĐẦU NÂNG CẤP HỘP SỐ MANUAL] ---
            gearbox_ratio_mode="manual" if i.cbo_gearbox_ratio_mode.currentText().lower() == "chỉ định" else "auto",
            gearbox_ratio_user=i.spn_gearbox_ratio_user.value() if i.cbo_gearbox_ratio_mode.currentText().lower() == "chỉ định" else 0.0,
            # --- [KẾT THÚC NÂNG CẤP HỘP SỐ MANUAL] ---
            db_path=self.db_path
        )
        return self.params

    def _start_thread(self, params: ConveyorParameters):
        self.th = CalculationThread(params)
        self.th.progress_updated.connect(self.results.progress.setValue)
        self.th.status_updated.connect(self.statusBar().showMessage)
        self.th.calculation_finished.connect(self._on_finished)
        self.results.progress.setVisible(True)
        self.results.progress.setValue(0)
        self._set_buttons(False)
        self.th.start()

    def _set_buttons(self, enabled: bool):
        self.inputs.btn_calc.setEnabled(enabled)
        self.inputs.btn_quick.setEnabled(enabled)
        self.inputs.btn_opt.setEnabled(enabled)

    def _full_calculate(self):
        self.statusBar().showMessage("🔄 Đang tính toán...")
        self._start_thread(self._collect())

    def _quick_calculate(self):
        i = self.inputs
        mat = i.cbo_material.currentText()
        vmax = ACTIVE_MATERIAL_DB.get(mat, {}).get("v_max", 4.0)
        if i.spn_speed.value() > vmax:
            i.spn_speed.setValue(round(0.8 * vmax, 2))
            self.statusBar().showMessage("Đã hạ tốc độ về mức khuyến cáo theo vật liệu.")
        self._start_thread(self._collect())

    # --- [BẮT ĐẦU NÂNG CẤP TỐI ƯU HÓA] ---
    def _run_advanced_optimization(self):
        # Tính năng tối ưu hóa nâng cao giờ đây luôn được bật mặc định
        # Không cần kiểm tra opt_group.isChecked() nữa

        # Hiển thị thông báo "Đang quét vô hạn kết quả, hãy kiên nhẫn chờ đợi !!" trong label trạng thái
        self.inputs.lbl_optimization_status.setText("🔄 Đang quét vô hạn kết quả, hãy kiên nhẫn chờ đợi !!")
        self.inputs.lbl_optimization_status.setStyleSheet("""
            QLabel {
                color: #dc2626;
                font-weight: 600;
                font-size: 14px;
                padding: 10px;
                background-color: #fee2e2;
                border: 1px solid #ef4444;
                border-radius: 6px;
                text-align: center;
                margin: 5px 0px;
            }
        """)
        
        # Cũng hiển thị thông báo trong status bar
        self.statusBar().showMessage("🔄 Đang quét vô hạn kết quả, hãy kiên nhẫn chờ đợi !!")

        i = self.inputs
        # Lấy giá trị từ slider (0-100) và chuẩn hóa về (0-1)
        cost_vs_safety = i.slider_cost_safety.value() / 100.0

        # Tạo đối tượng cài đặt
        opt_settings = OptimizerSettings(
            w_cost = 1.0 - cost_vs_safety, # Kéo sang trái (0) là ưu tiên cost
            w_safety = cost_vs_safety,      # Kéo sang phải (1) là ưu tiên safety
            w_power = 0.3, # Giữ giá trị mặc định hoặc có thể thêm slider khác
            max_budget_usd=i.spn_max_budget.value() if i.spn_max_budget.value() > 0 else None,
            min_belt_safety_factor=i.spn_min_safety_factor.value()
        )

        base_params = self._collect()

        # Setup and run the worker thread
        self.opt_thread = QThread()
        self.opt_worker = OptimizerWorker(base_params, opt_settings)
        self.opt_worker.moveToThread(self.opt_thread)

        self.opt_thread.started.connect(self.opt_worker.run)
        self.opt_worker.finished.connect(self._on_optimizer_finished)
        self.opt_worker.status.connect(self.statusBar().showMessage)
        # self.opt_worker.progress.connect(self.results.progress.setValue) # Can be implemented later
        
        self.opt_thread.start()
        self._set_buttons(False)
        self.results.progress.setVisible(True)
        self.results.progress.setRange(0, 0) # Indeterminate progress bar

    def _on_optimizer_finished(self, results):
        self.results.progress.setVisible(False)
        self.results.progress.setRange(0, 100)
        self._set_buttons(True)
        
        # Reset thông báo trạng thái về trạng thái ban đầu
        self.inputs.lbl_optimization_status.setText("✅ Tối ưu hóa hoàn tất!")
        self.inputs.lbl_optimization_status.setStyleSheet("""
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
        
        if not results:
            QMessageBox.warning(self, "Không có giải pháp", "Không tìm thấy giải pháp tối ưu nào phù hợp với điều kiện của bạn.")
            # Cập nhật thông báo nếu không có kết quả
            self.inputs.lbl_optimization_status.setText("❌ Không tìm thấy giải pháp phù hợp")
            self.inputs.lbl_optimization_status.setStyleSheet("""
                QLabel {
                    color: #dc2626;
                    font-weight: 600;
                    font-size: 14px;
                    padding: 10px;
                    background-color: #fee2e2;
                    border: 1px solid #ef4444;
                    border-radius: 6px;
                    text-align: center;
                    margin: 5px 0px;
                }
            """)
        else:
            self.results.update_optimizer_results(results)

        # Tự động reset thông báo về trạng thái ban đầu sau 5 giây
        QTimer.singleShot(5000, self._reset_optimization_status)

        # Clean up the thread properly
        if hasattr(self, 'opt_thread'):
            self.opt_thread.quit()
            self.opt_thread.wait(5000)  # Wait max 5 seconds
            if self.opt_thread.isRunning():
                self.opt_thread.terminate()
                self.opt_thread.wait()
            delattr(self, 'opt_thread')
            delattr(self, 'opt_worker')

    def _reset_optimization_status(self):
        """Reset thông báo trạng thái tối ưu hóa về trạng thái ban đầu"""
        self.inputs.lbl_optimization_status.setText("Tính năng tối ưu hóa nâng cao đã sẵn sàng")
        self.inputs.lbl_optimization_status.setStyleSheet("""
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
    # --- [KẾT THÚC NÂNG CẤP TỐI ƯU HÓA] ---

    def _apply_optimizer_solution(self, candidate):
        """Cập nhật lại input panel với giải pháp được chọn và chạy tính toán chi tiết."""
        i = self.inputs
        i.cbo_width.setCurrentText(str(candidate.belt_width_mm))
        i.spn_speed.setValue(candidate.belt_speed_mps)
        i.cbo_belt_type.setCurrentText(candidate.belt_type_name)
        i.cbo_gearbox_ratio_mode.setCurrentText("Chỉ định")
        i.spn_gearbox_ratio_user.setValue(candidate.gearbox_ratio)

        # Chạy lại tính toán chi tiết để hiển thị đầy đủ kết quả cho giải pháp đã chọn
        QTimer.singleShot(100, self._full_calculate)
        self.statusBar().showMessage(f"Đã áp dụng giải pháp tối ưu. Đang chạy tính toán chi tiết...")
    # --- [KẾT THÚC NÂNG CẤP TỐI ƯU HÓA] ---

    def _on_material_changed(self):
        mat = self.inputs.cbo_material.currentText()
        d = ACTIVE_MATERIAL_DB.get(mat, {})
        if d:
            # Cập nhật thông tin vật liệu
            density = d.get("density", 1.6)
            angle_repose = d.get("angle_repose", 30)
            v_max = d.get("v_max", 4.0)
            abrasive = d.get("abrasive", "medium")
            temperature_max = d.get("temperature_max", 60)
            moisture = d.get("moisture", "low")
            
            # Cập nhật UI
            self.inputs.spn_density.setValue(density)
            self.inputs.spn_angle.setValue(angle_repose)
            # Góc chất tải luôn bằng góc nghiêng tự nhiên, không cần cập nhật spn_surcharge
            
            # Cập nhật label thông tin vật liệu
            info_text = f"Khối lượng riêng: {density} tấn/m³ | Góc mái: {angle_repose}° | Tốc độ tối đa: {v_max} m/s <br> Mài mòn: {abrasive} | Nhiệt độ tối đa: {temperature_max}°C | Độ ẩm: {moisture}"
            self.inputs.lbl_material_info.setText(info_text)
            self.inputs.lbl_material_info.setWordWrap(True)
            self.inputs.lbl_material_info.setStyleSheet("color: #2563eb; font-style: normal; padding: 5px; background-color: #eff6ff; border: 1px solid #dbeafe; border-radius: 4px;")
            
            # Kiểm tra và điều chỉnh tốc độ nếu cần
            if self.inputs.spn_speed.value() > v_max:
                self.inputs.spn_speed.setValue(round(0.8 * v_max, 2))
                self.statusBar().showMessage(f"Tốc độ đã được chỉnh theo {mat}.")
            
            # Tự động tính toán lại khi vật liệu thay đổi
            if hasattr(self, 'current_result') and self.current_result is not None:
                self.statusBar().showMessage(f"🔄 Đang tính toán lại với vật liệu {mat}...")
                self._start_thread(self._collect())
        else:
            # Reset label khi không có thông tin vật liệu
            self.inputs.lbl_material_info.setText("Vật liệu không xác định")
            self.inputs.lbl_material_info.setStyleSheet("color: #dc2626; font-style: italic; padding: 5px; background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 4px;")

    def _on_finished(self, result: CalculationResult):
        self.current_result = result
        # Đảm bảo self.params được cập nhật với dữ liệu mới nhất
        if not hasattr(self, 'params') or self.params is None:
            self.params = self._collect()
        self._set_buttons(True)
        self.results.progress.setVisible(False)
        self._update_ui(result)

        if result.warnings:
            self.statusBar().showMessage(f"✅ Hoàn tất! {len(result.warnings)} cảnh báo.")
        else:
            self.statusBar().showMessage("🎉 Tính toán hoàn tất!")

    def _update_validation_styles(self, warnings: list[str]):
        i = self.inputs
        warning_map = {
            "Tốc độ băng": i.spn_speed,
            "Góc nghiêng lớn": i.spn_incl,
            "Lưu lượng": i.spn_capacity,
            "Chiều dài băng": i.spn_length,
            "Nhiệt độ vật liệu": i.spn_temp,
            "Vật liệu/MT ăn mòn": i.cbo_belt_type
        }

        all_widgets = [i.spn_speed, i.spn_incl, i.spn_capacity, i.spn_length, i.spn_temp, i.cbo_belt_type]
        for widget in all_widgets:
            widget.setProperty("state", "default")
            widget.style().unpolish(widget)
            widget.style().polish(widget)

        for warning_text in warnings:
            for keyword, widget in warning_map.items():
                if keyword in warning_text:
                    widget.setProperty("state", "warning")
                    widget.style().unpolish(widget)
                    widget.style().polish(widget)
                    break

    def _update_ui(self, r: CalculationResult):
        try:
            self._update_validation_styles(r.warnings)

            def set_card(card: QFrame, text: str, status: str):
                if not card: return
                value_label = card.findChild(QLabel, "cardValue")
                if value_label: value_label.setText(text)
                card.setProperty("status", status)
                card.style().unpolish(card)
                card.style().polish(card)

            cards = self.results.cards
            set_card(cards.card_power, f"{r.motor_power_kw:.1f} kW", "success" if r.motor_power_kw < 50 else "warning" if r.motor_power_kw < 100 else "danger")
            eff = getattr(r, "drive_efficiency_percent", getattr(r, "efficiency", 0.0))
            set_card(cards.card_eff, f"{eff:.1f} %", "success" if eff > 80 else "warning" if eff > 60 else "danger")
            set_card(cards.card_sf, f"{r.safety_factor:.2f}", "success" if r.safety_factor > 8 else "warning" if r.safety_factor > 5 else "danger")
            set_card(cards.card_cost, f"${r.cost_capital_total:,.0f}", "success")

            vals = [
                f"{r.mass_flow_rate:.3f}", f"{r.material_load_kgpm:.2f}", f"{r.belt_weight_kgpm:.2f}",
                f"{r.moving_parts_weight_kgpm:.2f}", f"{r.total_load_kgpm:.2f}", f"{r.friction_force:,.0f}",
                f"{r.lift_force:,.0f}", f"{r.effective_tension:,.0f}",
                f"{r.T1:,.0f}", f"{r.T2:,.0f}", f"{r.safety_factor:.2f}",
                f"{r.belt_strength_utilization:.1f} %", f"{r.required_power_kw:.1f}",
                f"{r.motor_power_kw:.1f}", f"{r.drum_diameter_mm:.0f}"
            ]
            labels = [
                "Lưu lượng khối (kg/s)", "Tải trọng vật liệu (kg/m)", "Khối lượng băng (kg/m)",
                "KL bộ phận chuyển động (kg/m)", "Tổng tải (kg/m)", "Tổng lực ma sát (N)",
                "Lực nâng (N)", "Lực căng hiệu dụng (N)",
                "T1 (N)", "T2 (N)", "Hệ số an toàn (SF)", "% dùng cường độ đai",
                "Công suất cần (kW)", "Công suất động cơ (kW)", "ĐK tang khuyến cáo (mm)"
            ]
            self.results.tbl.setRowCount(len(labels))
            for i, label in enumerate(labels):
                self.results.tbl.setItem(i, 0, QTableWidgetItem(label))
                self.results.tbl.setItem(i, 1, QTableWidgetItem(vals[i] if i < len(vals) else "---"))

            ana_report_html = "<h3>PHÂN TÍCH KỸ THUẬT</h3>"
            ana_report_html += f"<p><b>- Hiệu suất truyền động:</b> {eff:.1f}% (η_m × η_g ÷ Kt)</p>"
            ana_report_html += f"<p><b>- Phần trăm sử dụng cường độ đai:</b> {r.belt_strength_utilization:.1f}%</p>"
            ana_report_html += f"<p><b>- Phần trăm sử dụng tiết diện (ước tính):</b> {r.capacity_utilization:.1f}%</p>"
            if r.warnings:
                ana_report_html += "<h4 style='color: #f59e0b;'>CẢNH BÁO:</h4><ul>"
                for w in r.warnings: ana_report_html += f"<li>{w}</li>"
                ana_report_html += "</ul>"
            if r.recommendations:
                ana_report_html += "<h4 style='color: #22c55e;'>KHUYẾN NGHỊ:</h4><ul>"
                for rec in r.recommendations: ana_report_html += f"<li>{rec}</li>"
                ana_report_html += "</ul>"
            self.results.txt_analysis.setHtml(ana_report_html)

            cost_report = (f"PHÂN TÍCH CHI PHÍ (ƯỚC TÍNH)\n{'-'*40}\n1. CHI PHÍ ĐẦU TƯ BAN ĐẦU (CAPEX)\n"
                           f"   - Chi phí băng tải: ${r.cost_belt:,.2f}\n"
                           f"   - Chi phí con lăn: ${r.cost_idlers:,.2f}\n"
                           f"   - Chi phí kết cấu: ${r.cost_structure:,.2f}\n"
                           f"   - Chi phí truyền động: ${r.cost_drive:,.2f}\n"
                           f"   - Chi phí khác (lắp đặt...): ${r.cost_others:,.2f}\n"
                           f"{'-'*40}\n"
                           f"   => TỔNG CHI PHÍ ĐẦU TƯ: ${r.cost_capital_total:,.2f}\n"
                           f"{'-'*40}\n2. CHI PHÍ VẬN HÀNH/NĂM (OPEX)\n"
                           f"   - Chi phí năng lượng/năm: ${r.op_cost_energy_per_year:,.2f}\n"
                           f"   - Chi phí bảo trì/năm: ${r.op_cost_maintenance_per_year:,.2f}\n"
                           f"   => TỔNG CHI PHÍ VẬN HÀNH/NĂM: ${r.op_cost_total_per_year:,.2f}\n")
            self.results.txt_cost_analysis.setPlainText(cost_report)

            summary_report = (f"BÁO CÁO TÓM TẮT\n{'-'*40}\n"
                              f"• Công suất động cơ khuyến cáo: {r.motor_power_kw:.1f} kW\n"
                              f"• Hiệu suất truyền động: {eff:.1f}%\n"
                              f"• Hệ số an toàn của băng: {r.safety_factor:.2f}\n"
                              f"• Đường kính tang khuyến cáo: {r.drum_diameter_mm:.0f} mm\n"
                              f"• Ước tính chi phí đầu tư (CAPEX): ${r.cost_capital_total:,.2f}\n"
                              f"• Ước tính chi phí vận hành/năm (OPEX): ${r.op_cost_total_per_year:,.2f}\n")
            self.results.txt_report.setPlainText(summary_report)
            
            # Cập nhật thông tin truyền động
            self._redraw_all_visualizations()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi cập nhật Giao diện", f"Đã xảy ra lỗi khi hiển thị kết quả:\n{e}")
            traceback.print_exc()

    def choose_database(self):
        path, _ = QFileDialog.getOpenFileName(self, "Chọn cơ sở dữ liệu", "", "Excel/CSV (*.xlsx *.xls *.csv)")
        if path:
            try:
                self.statusBar().showMessage(f"Đang nạp CSDL từ {path}...")
                _, _, report = load_database(path)
                self.db_path = path
                self.inputs.cbo_material.clear()
                self.inputs.cbo_material.addItems(list(ACTIVE_MATERIAL_DB.keys()))
                self.inputs.cbo_belt_type.clear()
                self.inputs.cbo_belt_type.addItems(list(ACTIVE_BELT_SPECS.keys()))
                self.statusBar().showMessage(report)
            except Exception as e:
                QMessageBox.critical(self, "Lỗi CSDL", f"Không thể nạp CSDL:\n{e}")

    def export_pdf(self):
        if not self.current_result or not self.params:
            QMessageBox.warning(self, "Chưa có kết quả", "Hãy tính toán trước khi xuất PDF.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Xuất PDF", "bao_cao_bang_tai.pdf", "PDF (*.pdf)")
        if path:
            try:
                export_pdf_report(path, self.params, self.current_result)
                self.statusBar().showMessage(f"Đã xuất PDF: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi PDF", f"Không thể xuất PDF:\n{e}")

    def export_excel(self):
        if not self.current_result or not self.params:
            QMessageBox.warning(self, "Chưa có kết quả", "Hãy tính toán trước khi xuất Excel.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Xuất Excel", "bao_cao_bang_tai.xlsx", "Excel (*.xlsx)")
        if path:
            try:
                export_excel_report(path, self.params, self.current_result)
                self.statusBar().showMessage(f"Đã xuất Excel: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi Excel", f"Không thể xuất Excel:\n{e}")

    def validate_design(self):
        if not self.current_result:
            QMessageBox.warning(self, "Chưa có kết quả", "Tính toán trước đã.")
            return
        r = self.current_result
        eff = getattr(r, "drive_efficiency_percent", getattr(r, "efficiency", 0.0))
        msgs = [
            "<h3>KIỂM ĐỊNH THIẾT KẾ</h3>",
            f"- SF: {r.safety_factor:.2f} {'(Đạt ≥ 6.0)' if r.safety_factor >= 6.0 else '(THIẾU)'}",
            f"- Hiệu suất truyền động: {eff:.1f} %",
            f"- % dùng cường độ đai: {r.belt_strength_utilization:.1f} %"
        ]
        QMessageBox.information(self, "Kiểm định", "\n".join(msgs))

    def _redraw_all_visualizations(self):
        if not hasattr(self, 'params') or not self.params or not self.current_result:
            return
        if hasattr(self.results, 'update_visualizations'):
            try:
                self.results.update_visualizations(self.params, self.current_result, self.current_theme)
            except Exception as e:
                print(f"Error in update_visualizations: {e}")
                import traceback
                traceback.print_exc()

    def _toggle_chat_panel(self):
        """Toggle the chat panel visibility and sync menu item state."""
        is_visible = self.chat_dock.isVisible()
        self.chat_dock.setVisible(not is_visible)
        self.act_chat.setChecked(not is_visible)

    def _show_about_dialog(self):
        about_text = f"""
            <h3>Convayor Calculator AI</h3>
            <p><b>Phiên bản:</b> {VERSION}<br>
            <b>Ngày phát hành:</b> 2025</p>
            
            <h4>Tính năng chính:</h4>
            <ul>
                <li>✔️ Tính toán theo tiêu chuẩn DIN 22101, CEMA, ISO 5048</li>
                <li>✔️ Tích hợp Trợ lý kỹ thuật trí tuệ nhân tạo</li>
                <li>✔️ Tự động lựa chọn và tối ưu thiết bị</li>
                <li>✔️ Phân tích chi tiết các điều kiện vận hành</li>
                <li>✔️ Báo cáo kỹ thuật và chi phí hoàn chỉnh</li>
                <li>✔️ Kiểm tra tuân thủ hệ số an toàn</li>
                <li>✔️ Giao diện chuyên Nghiệp, thân thiện</li>
            </ul>

            <h4>Tài liệu tham khảo:</h4>
            <ul>
                <li>Bridgestone, Conveyor Belt Design Manual</li>
                <li>Funner Dunlop, Conveyor Handbook</li>
                <li>Funner Dunlop, Selecting the Proper Conveyor Belt</li>
                <li>CSMA, Belt Conveyors for Bulk Materials</li>
            </ul>
            
            <hr>
            <p><b>{COPYRIGHT}</b></p>
            <p><i>Phần mềm được phát triển với mục đích hỗ trợ sinh viên và người không chuyên thiết kế băng tải.
            Vui lòng tham khảo ý kiến chuyên gia trước khi áp dụng trong thực tế.</i></p>
            Nếu thấy phần mềm hữu ích hãy mời tác giả 1 li cà phê nhé 019704070025850 HDBank</i></p>
        """
        QMessageBox.about(self, "Giới thiệu", about_text)

