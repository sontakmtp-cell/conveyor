import os
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPaintEvent, QPixmap, QPalette, QBrush, QPainter

from core.licensing import assigned_account_id, verify_input, write_activation


def get_resource_path(relative_path: str) -> str:
    """Lấy đường dẫn tuyệt đối đến tài nguyên, hỗ trợ cả development và PyInstaller exe."""
    # Normalize path separators for cross-platform compatibility
    relative_path = relative_path.replace("\\", "/")
    
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        resource_path = os.path.join(base_path, relative_path)
    except AttributeError:
        # Running in development mode
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        resource_path = os.path.join(base_path, relative_path)
    
    # Convert to proper path separators for current OS
    resource_path = os.path.normpath(resource_path)
    return resource_path


class ActivationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Software Activate - Conveyor Calculator AI")
        self.setFixedSize(672, 960)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.account_id = assigned_account_id()
        
        # Initialize background pixmap
        self.background_pixmap = None
        
        self._setup_ui()
        self._setup_background()
        
        self.btn_activate.clicked.connect(self._do_activate)
        self.password.returnPressed.connect(self._do_activate)
    
    def paintEvent(self, event: QPaintEvent):
        """Custom paint event to draw background image"""
        painter = QPainter(self)
        
        if self.background_pixmap and not self.background_pixmap.isNull():
            # Draw the background image
            painter.drawPixmap(0, 0, self.background_pixmap)
        else:
            # Draw fallback gradient background
            painter.fillRect(self.rect(), Qt.black)
        
        # Call parent paintEvent to draw widgets
        super().paintEvent(event)
    
    def _setup_background(self):
        """Thiết lập hình nền từ file Whisk_zkxmgy.png"""
        # Direct path to the image file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "images", "Whisk_zkxmgy.png")
        
        # Debug: Print paths being tried
        print(f"Current dir: {current_dir}")
        print(f"Looking for image at: {image_path}")
        print(f"Image exists: {os.path.exists(image_path)}")
        
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            print(f"Pixmap loaded: {not pixmap.isNull()}")
            print(f"Pixmap size: {pixmap.size().width()}x{pixmap.size().height()}")
            
            if not pixmap.isNull():
                # Scale image to fit dialog size
                self.background_pixmap = pixmap.scaled(
                    self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
                )
                print(f"Scaled pixmap size: {self.background_pixmap.size().width()}x{self.background_pixmap.size().height()}")
                print("Background pixmap stored for paintEvent")
            else:
                print(f"Error: Could not load pixmap from {image_path}")
                self.background_pixmap = None
        else:
            print(f"Error: Image file not found at {image_path}")
            self.background_pixmap = None
    
    def _setup_ui(self):
        """Thiết lập UI với tọa độ tuyệt đối theo yêu cầu"""
        # Không sử dụng layout, đặt widget trực tiếp bằng tọa độ
        
        # Account ID label - tọa độ 160x295 đến 515x375
        self.account_label = QLabel(self.account_id, self)
        self.account_label.setGeometry(160, 295, 355, 80)  # width=515-160=355, height=375-295=80
        self.account_label.setAlignment(Qt.AlignCenter)
        self.account_label.setObjectName("accountLabel")
        
        # Username field - tọa độ 160x460 đến 515x515
        self.username = QLineEdit(self.account_id, self)
        self.username.setGeometry(160, 460, 355, 55)  # width=515-160=355, height=515-460=55
        self.username.setReadOnly(True)
        self.username.setObjectName("usernameField")
        
        # Password field - tọa độ 160x560 đến 515x610
        self.password = QLineEdit(self)
        self.password.setGeometry(160, 560, 355, 50)  # width=515-160=355, height=610-560=50
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Enter activation password...")
        self.password.setObjectName("passwordField")
        
        # Activate button - tọa độ 205x740 đến 470x795
        self.btn_activate = QPushButton("ACTIVATE", self)
        self.btn_activate.setGeometry(205, 740, 265, 55)  # width=470-205=265, height=795-740=55
        self.btn_activate.setObjectName("activateButton")
        
        # Apply styles for widgets (background will be set separately)
        self._apply_widget_styles()
    
    def _apply_widget_styles(self):
        """Apply styles to widgets only, not the dialog background"""
        widget_styles = """
            #accountLabel {
                background-color: rgba(255, 255, 255, 180);
                border: 2px solid #3b82f6;
                border-radius: 10px;
                font-size: 24px;
                font-weight: bold;
                color: #1e293b;
                padding: 10px;
            }
            
            #usernameField {
                background-color: rgba(255, 255, 255, 200);
                border: 2px solid #cbd5e1;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-family: 'Courier New', monospace;
                color: #64748b;
            }
            
            #passwordField {
                background-color: rgba(255, 255, 255, 220);
                border: 2px solid #cbd5e1;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-family: 'Courier New', monospace;
                color: #1e293b;
            }
            
            #passwordField:focus {
                border-color: #3b82f6;
                background-color: rgba(255, 255, 255, 240);
            }
            
            #activateButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 18px;
                padding: 15px;
            }
            
            #activateButton:hover {
                background-color: #2563eb;
            }
            
            #activateButton:pressed {
                background-color: #1d4ed8;
            }
        """
        
        # Apply widget styles first
        self.setStyleSheet(widget_styles)

    def _do_activate(self):
        if verify_input(self.username.text().strip(), self.password.text().strip()):
            write_activation(self.account_id)
            QMessageBox.information(self, "Thành công", "Đã kích hoạt.")
            self.accept()
        else:
            QMessageBox.warning(self, "Sai mật khẩu", "Password không khớp. Vui lòng kiểm tra lại thẻ kích hoạt.")


