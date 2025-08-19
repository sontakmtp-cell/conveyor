# ui/login_dialog.py
# -*- coding: utf-8 -*-
"""
Module định nghĩa cửa sổ đăng nhập cho ứng dụng.
Giao diện được tùy chỉnh để khớp với hình ảnh thiết kế bằng tọa độ tuyệt đối.
"""

import sys
import os
import json
import hashlib
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QDialogButtonBox
)
from PySide6.QtGui import QPixmap, QPalette, QBrush
from PySide6.QtCore import Qt, QSize

class CreateAccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tạo tài khoản mới")
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Tên đăng nhập mới")
        layout.addWidget(QLabel("Tên đăng nhập:"))
        layout.addWidget(self.username_input)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mật khẩu mới")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Mật khẩu:"))
        layout.addWidget(self.password_input)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QLabel {
                font-weight: bold;
            }
        """)

def get_resource_path(relative_path: str) -> str:
    """Lấy đường dẫn tuyệt đối đến tài nguyên."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.users_db_path = get_resource_path("users.json")
        self.users = self._load_users()

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        """
        --- [THAY ĐỔI] Xây dựng giao diện bằng tọa độ tuyệt đối ---
        Bỏ sử dụng layout và đặt widget vào vị trí chính xác.
        """
        self.setWindowTitle("Đăng nhập - Conveyor Calculator 3D")
        # --- Kích thước cửa sổ mới ---
        self.setFixedSize(1024, 1024)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Đặt hình nền
        image_path = get_resource_path("ui/images/login.png")
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            palette = self.palette()
            palette.setBrush(QPalette.Window, QBrush(pixmap.scaled(
                self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
            self.setPalette(palette)
            self.setAutoFillBackground(True)
        
        # --- Bỏ layout, đặt widget trực tiếp lên dialog ---
        
        # Ô nhập liệu Username
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Username")
        self.username_input.setText("Admin")
        # Tọa độ: x=330, y=480, width=348, height=45
        self.username_input.setGeometry(330, 476, 680 - 330, 530 - 476)

        # Ô nhập liệu Password
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        # Tọa độ: x=330, y=560, width=348, height=45
        self.password_input.setGeometry(330, 558, 680 - 330, 610 - 558)

        # Nút Login
        self.login_button = QPushButton("Login", self)
        # Tọa độ: x=330, y=670, width=85, height=35
        self.login_button.setGeometry(330, 670, 418 - 330, 715 - 670)

        # Nút Create Account
        self.create_account_button = QPushButton("Create Account", self)
        # Tọa độ: x=430, y=670, width=160, height=35
        self.create_account_button.setGeometry(430, 670, 595 - 430, 715 - 670)

        # Nút Exit
        self.exit_button = QPushButton("Exit", self)
        # Tọa độ: x=605, y=670, width=75, height=35
        self.exit_button.setGeometry(605, 670, 683 - 605, 715 - 670)
        
        # Kết nối tín hiệu
        self.login_button.clicked.connect(self.handle_login)
        self.create_account_button.clicked.connect(self.handle_create_account)
        self.exit_button.clicked.connect(self.reject)
        self.password_input.returnPressed.connect(self.handle_login)

    def _apply_styles(self):
        """
        --- [THAY ĐỔI] Tinh chỉnh style cho phù hợp với kích thước mới ---
        - Bỏ các style cho label và widget không còn tồn tại.
        - Điều chỉnh font và padding của nút cho vừa với kích thước mới.
        """
        self.setStyleSheet("""
            QLineEdit {
                background-color: #F5EFE1; /* Màu giấy cũ */
                border: 2px solid #D3C5B3;
                border-radius: 8px;
                padding: 10px;
                font-size: 18px; /* Giảm cỡ chữ một chút */
                font-family: 'Courier New', monospace;
                color: #5D4037;
            }
            QPushButton {
                background-color: #EAE0C8;
                color: #5D4037;
                border: 2px solid #C8BBA7;
                border-radius: 8px;
                padding: 5px; /* Giảm padding để vừa kích thước nút */
                font-size: 14px; /* Giảm cỡ chữ nút */
                font-weight: bold;
                font-family: 'Times New Roman', serif;
            }
            QPushButton:hover {
                background-color: #D3C5B3;
                border-color: #B2A491;
            }
        """)

    def _hash_password(self, password):
        """Mã hóa mật khẩu bằng SHA256."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def _load_users(self):
        """Tải danh sách người dùng từ file JSON, nếu không có thì tạo mới."""
        if not os.path.exists(self.users_db_path):
            default_users = {
                "Admin": self._hash_password("123567")
            }
            self._save_users(default_users)
            return default_users
        try:
            with open(self.users_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return self._load_users()

    def _save_users(self, users_data):
        """Lưu danh sách người dùng vào file JSON."""
        with open(self.users_db_path, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=4)

    def handle_login(self):
        """Xử lý sự kiện nhấn nút Đăng nhập."""
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tên đăng nhập và mật khẩu.")
            return

        hashed_password = self._hash_password(password)
        
        if self.users.get(username) == hashed_password:
            self.accept()
        else:
            QMessageBox.critical(self, "Đăng nhập thất bại", "Tên đăng nhập hoặc mật khẩu không đúng.")

    def handle_create_account(self):
        """Xử lý sự kiện nhấn nút Tạo tài khoản."""
        username = self.username_input.text()
        password = self.password_input.text()

        # Kiểm tra xem có phải là Admin và mật khẩu đúng không
        if username != "Admin" or self._hash_password(password) != self.users.get("Admin"):
            QMessageBox.warning(self, "Không có quyền", "Chỉ Admin với mật khẩu chính xác mới có thể tạo tài khoản mới.")
            return

        # Hiển thị dialog tạo tài khoản mới
        new_account = CreateAccountDialog(self)
        if new_account.exec_() == QDialog.Accepted:
            new_username = new_account.username_input.text()
            new_password = new_account.password_input.text()

            if not new_username or not new_password:
                QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tên đăng nhập và mật khẩu mới.")
                return

            if new_username in self.users:
                QMessageBox.warning(self, "Tài khoản đã tồn tại", f"Tên đăng nhập '{new_username}' đã được sử dụng.")
                return
            
            if len(new_password) < 6:
                QMessageBox.warning(self, "Mật khẩu yếu", "Mật khẩu phải có ít nhất 6 ký tự.")
                return
                
            # Thêm tài khoản mới
            self.users[new_username] = self._hash_password(new_password)
            self._save_users(self.users)
            
            QMessageBox.information(self, "Tạo tài khoản thành công", 
                                  f"Đã tạo tài khoản cho '{new_username}'.")

        self.users[username] = self._hash_password(password)
        self._save_users(self.users)
        
        QMessageBox.information(self, "Tạo tài khoản thành công", 
                                f"Đã tạo tài khoản cho '{username}'.\nBây giờ bạn có thể đăng nhập.")
        self.password_input.clear()
