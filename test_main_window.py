#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để kiểm tra main window
"""
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window_3d_enhanced import Enhanced3DConveyorWindow

def test_main_window():
    print("Khởi tạo QApplication...")
    app = QApplication(sys.argv)
    
    print("Tạo main window...")
    try:
        main_window = Enhanced3DConveyorWindow()
        print("Main window được tạo thành công")
        
        print("Hiển thị main window...")
        main_window.show()
        print("Main window đã được hiển thị")
        
        print("Chạy event loop...")
        return app.exec()
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = test_main_window()
    sys.exit(exit_code)
