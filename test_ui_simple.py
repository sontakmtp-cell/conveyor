#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script debug đơn giản để kiểm tra vấn đề UI
"""

import sys
import os
import traceback
from pathlib import Path

# Thêm đường dẫn hiện tại vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_step_by_step():
    """Test từng bước một"""
    print("🧪 Testing step by step...")
    
    try:
        print("Step 1: Import PySide6...")
        from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
        print("✅ PySide6 imported")
        
        print("Step 2: Create QApplication...")
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            print("✅ QApplication created")
        else:
            print("✅ QApplication already exists")
        
        print("Step 3: Create simple widget...")
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Test Label")
        layout.addWidget(label)
        print("✅ Simple widget created")
        
        print("Step 4: Test widget properties...")
        print(f"   Widget size: {widget.size()}")
        print(f"   Layout count: {layout.count()}")
        print("✅ Widget properties OK")
        
        print("Step 5: Import core modules...")
        from core.models import ConveyorParameters
        print("✅ Core models imported")
        
        print("Step 6: Import UI components...")
        from ui.ui_components_3d_enhanced import InputsPanel
        print("✅ InputsPanel imported")
        
        print("Step 7: Create InputsPanel...")
        inputs = InputsPanel()
        print("✅ InputsPanel created")
        
        print("Step 8: Import main window...")
        from ui.main_window_3d_enhanced import Enhanced3DConveyorWindow
        print("✅ Main window imported")
        
        print("Step 9: Create main window...")
        main_window = Enhanced3DConveyorWindow()
        print("✅ Main window created")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed at step: {e}")
        traceback.print_exc()
        return False

def main():
    print("🚀 Starting Simple UI Debug Test")
    print("=" * 60)
    
    success = test_step_by_step()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Tất cả steps đều PASSED!")
        print("✅ UI có thể được tạo thành công")
    else:
        print("❌ Test failed")
        print("🔧 Cần kiểm tra lỗi cụ thể")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

