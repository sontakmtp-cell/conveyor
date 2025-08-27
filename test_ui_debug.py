#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script debug để kiểm tra vấn đề UI không hiển thị
"""

import sys
import os
import traceback
from pathlib import Path

# Thêm đường dẫn hiện tại vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test import các module cần thiết"""
    print("🧪 Testing imports...")
    
    try:
        print("1. Testing PySide6...")
        from PySide6.QtWidgets import QApplication
        print("✅ PySide6.QtWidgets imported successfully")
        
        print("2. Testing core modules...")
        from core.models import ConveyorParameters, CalculationResult
        print("✅ core.models imported successfully")
        
        print("3. Testing UI components...")
        from ui.ui_components_3d_enhanced import InputsPanel, Enhanced3DResultsPanel
        print("✅ UI components imported successfully")
        
        print("4. Testing main window...")
        from ui.main_window_3d_enhanced import Enhanced3DConveyorWindow
        print("✅ Main window imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_ui_creation():
    """Test tạo UI components"""
    print("\n🔧 Testing UI creation...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from ui.main_window_3d_enhanced import Enhanced3DConveyorWindow
        
        # Tạo QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            print("✅ QApplication created")
        else:
            print("✅ QApplication already exists")
        
        # Test tạo main window
        print("Creating main window...")
        main_window = Enhanced3DConveyorWindow()
        print("✅ Main window created successfully")
        
        # Test hiển thị (không show thực sự)
        print("Testing window properties...")
        print(f"   Window title: {main_window.windowTitle()}")
        print(f"   Window size: {main_window.size()}")
        print(f"   Is visible: {main_window.isVisible()}")
        
        return True
        
    except Exception as e:
        print(f"❌ UI creation failed: {e}")
        traceback.print_exc()
        return False

def test_file_structure():
    """Test cấu trúc file"""
    print("\n📁 Testing file structure...")
    
    current_dir = Path(__file__).parent
    print(f"Current directory: {current_dir}")
    
    # Kiểm tra các file quan trọng
    important_files = [
        "ui/main_window_3d_enhanced.py",
        "ui/ui_components_3d_enhanced.py",
        "core/models.py",
        "core/specs.py"
    ]
    
    for file_path in important_files:
        full_path = current_dir / file_path
        exists = full_path.exists()
        print(f"   {file_path}: {'✅ exists' if exists else '❌ not found'}")
        
        if exists:
            try:
                size = full_path.stat().st_size
                print(f"      Size: {size} bytes")
            except:
                print(f"      Could not get size")
    
    return True

def main():
    print("🚀 Starting UI Debug Test")
    print("=" * 60)
    
    success = True
    
    # Test cấu trúc file
    success &= test_file_structure()
    
    # Test imports
    success &= test_imports()
    
    # Test UI creation
    success &= test_ui_creation()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Tất cả tests đều PASSED!")
        print("✅ UI components có thể được tạo thành công")
        print("🔍 Vấn đề có thể nằm ở nơi khác")
    else:
        print("❌ Một số tests đã FAILED")
        print("🔧 Cần sửa lỗi trước khi tiếp tục")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

