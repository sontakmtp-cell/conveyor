# cloud.py
# -*- coding: utf-8 -*-
"""
Điểm vào ứng dụng (main).
File này khởi tạo và hiển thị màn hình đăng nhập trước khi vào cửa sổ chính.
"""
import sys
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog
from pathlib import Path
from dotenv import load_dotenv
import os
# Import các cửa sổ cần thiết
from ui.main_window_3d_enhanced import Enhanced3DConveyorWindow
from ui.login_dialog import LoginDialog  # <<< THÊM DÒNG NÀY
from core.licensing import is_activated
from ui.activation_dialog import ActivationDialog
from core.specs import VERSION
import logging
from core.utils.paths import get_log_path
import os.path

def main():
    # Load environment variables from .env file
    root_dir = Path(__file__).parent.absolute()
    dotenv_path = root_dir / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)
    
    # Set default INDEX_DIR if not provided - Sửa đường dẫn để sử dụng đường dẫn tuyệt đối
    if not os.getenv('INDEX_DIR'):
        index_dir = root_dir / 'data' / 'index'
        os.environ['INDEX_DIR'] = str(index_dir)
        print(f"Using default INDEX_DIR: {os.environ['INDEX_DIR']}")
        
        # Kiểm tra và tạo thư mục index nếu chưa tồn tại
        if not index_dir.exists():
            print(f"Creating index directory: {index_dir}")
            index_dir.mkdir(parents=True, exist_ok=True)
        else:
            print(f"Index directory exists: {index_dir}")
        
        # Kiểm tra xem file chunks.faiss có tồn tại không
        faiss_file = index_dir / 'chunks.faiss'
        if not faiss_file.exists():
            print(f"Warning: chunks.faiss file not found in: {index_dir}")
            print("You may need to rebuild the index using: python scripts/rebuild_index.py")
        else:
            print(f"Found chunks.faiss at: {faiss_file}")
        
    app = QApplication(sys.argv)
    app.setApplicationName("Conveyor Calculator Professional")
    app.setApplicationVersion(VERSION)
    app.setOrganizationName("haingocson@gmail.com")

    # --- [BẮT ĐẦU THAY ĐỔI] ---
    # Bước 1: Kiểm tra kích hoạt offline
    ok, _state = is_activated()
    if not ok:
        act_dialog = ActivationDialog()
        if act_dialog.exec() != QDialog.Accepted:
            return 0

    # Bước 2: Hiển thị màn hình đăng nhập trước khi vào app chính
    login_dialog = LoginDialog()
    result = login_dialog.exec()
    if result == QDialog.Accepted:
        # Setup logging in user's AppData directory
        log_file = os.path.join(get_log_path(), 'conveyor_calculator.log')
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8", mode="a"),
                logging.StreamHandler()  # Also log to console
            ]
        )

        try:
            # Tạo và hiển thị cửa sổ chính của ứng dụng
            main_window = Enhanced3DConveyorWindow()
            main_window.show()
            return app.exec()
        except Exception as e:
            QMessageBox.critical(None, "Lỗi khởi động", f"Không thể khởi động ứng dụng chính:\n{e}")
            logging.error(f"Lỗi khởi động cửa sổ chính: {e}", exc_info=True)
            return 1
    else:
        # Nếu người dùng đóng cửa sổ đăng nhập hoặc đăng nhập thất bại, thoát.
        return 0
    # --- [KẾT THÚC THAY ĐỔI] ---

if __name__ == "__main__":
    sys.exit(main())
