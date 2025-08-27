#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test tối thiểu để kiểm tra từng import một
"""

import sys
import os
import traceback
from pathlib import Path

# Thêm đường dẫn hiện tại vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports_one_by_one():
    """Test từng import một"""
    print("🧪 Testing imports one by one...")
    
    try:
        print("1. Testing PySide6.QtWidgets...")
        from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QGroupBox, QFormLayout
        print("✅ PySide6.QtWidgets OK")
        
        print("2. Testing PySide6.QtSvgWidgets...")
        from PySide6.QtSvgWidgets import QSvgWidget
        print("✅ PySide6.QtSvgWidgets OK")
        
        print("3. Testing core.models...")
        from core.models import ConveyorParameters
        print("✅ core.models OK")
        
        print("4. Testing core.specs...")
        from core.specs import VERSION
        print("✅ core.specs OK")
        
        print("5. Testing ui.plotting...")
        from ui.plotting import EnhancedPlotCanvas
        print("✅ ui.plotting OK")
        
        print("6. Testing ui.tooltips...")
        from ui.tooltips import apply_tooltips
        print("✅ ui.tooltips OK")
        
        print("7. Testing ui.visualization_3d...")
        try:
            from ui.visualization_3d import Visualization3DWidget
            print("✅ ui.visualization_3d OK")
        except Exception as e:
            print(f"⚠️ ui.visualization_3d failed (expected): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_ui_components():
    """Test tạo UI components"""
    print("\n🔧 Testing UI components...")
    
    try:
        from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
        from PySide6.QtSvgWidgets import QSvgWidget
        
        # Tạo QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            print("✅ QApplication created")
        else:
            print("✅ QApplication already exists")
        
        print("1. Testing QSvgWidget...")
        svg_widget = QSvgWidget()
        print("✅ QSvgWidget created")
        
        print("2. Testing basic widget creation...")
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Test")
        layout.addWidget(label)
        print("✅ Basic widget created")
        
        print("3. Testing InputsPanel import...")
        from ui.ui_components_3d_enhanced import InputsPanel
        print("✅ InputsPanel imported")
        
        print("4. Testing InputsPanel creation...")
        inputs = InputsPanel()
        print("✅ InputsPanel created")
        
        return True
        
    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("🚀 Starting Minimal UI Debug Test")
    print("=" * 60)
    
    success = True
    
    # Test imports
    success &= test_imports_one_by_one()
    
    # Test UI components
    success &= test_ui_components()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Tất cả tests đều PASSED!")
        print("✅ UI components có thể được tạo thành công")
    else:
        print("❌ Test failed")
        print("🔧 Cần kiểm tra lỗi cụ thể")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

