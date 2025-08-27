#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test để kiểm tra từng group function của InputsPanel
"""

import sys
import os
import traceback
from pathlib import Path

# Thêm đường dẫn hiện tại vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_inputs_panel_groups():
    """Test tạo InputsPanel với từng group function"""
    print("🧪 Testing InputsPanel groups...")
    
    try:
        from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
        from ui.ui_components_3d_enhanced import InputsPanel
        
        # Tạo QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            print("✅ QApplication created")
        else:
            print("✅ QApplication already exists")
        
        print("Step 1: Create InputsPanel...")
        inputs = InputsPanel()
        print("✅ InputsPanel created successfully")
        
        print("Step 2: Test panel properties...")
        print(f"   Panel size: {inputs.size()}")
        print(f"   Panel layout count: {inputs.layout().count()}")
        print("✅ Panel properties OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        traceback.print_exc()
        return False

def test_group_functions_individually():
    """Test từng group function một cách riêng biệt"""
    print("\n🔍 Testing group functions individually...")
    
    try:
        from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFormLayout, QGroupBox, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QCheckBox, QScrollArea
        from PySide6.QtSvgWidgets import QSvgWidget
        
        # Tạo QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            print("✅ QApplication created")
        else:
            print("✅ QApplication already exists")
        
        print("Step 1: Create basic structure...")
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        v = QVBoxLayout(container)
        print("✅ Basic structure created")
        
        print("Step 2: Create form widgets...")
        # Project
        edt_project_name = QLineEdit("Thiết kế băng tải nhà máy ABC")
        edt_designer = QLineEdit("Kỹ sư thiết kế")
        edt_client = QLineEdit("Khách hàng")
        edt_location = QLineEdit("Công trình")
        
        # Material
        cbo_material = QComboBox()
        spn_density = QDoubleSpinBox()
        spn_density.setRange(0.1, 10.0)
        spn_density.setDecimals(3)
        spn_density.setValue(1.6)
        spn_density.setSuffix(" tấn/m³")
        print("✅ Form widgets created")
        
        print("Step 3: Create project group...")
        g_project = QGroupBox("Thông tin dự án")
        f_project = QFormLayout(g_project)
        f_project.addRow("Tên dự án:", edt_project_name)
        f_project.addRow("Người thiết kế:", edt_designer)
        f_project.addRow("Khách hàng:", edt_client)
        f_project.addRow("Công trình:", edt_location)
        print("✅ Project group created")
        
        print("Step 4: Create material group...")
        g_material = QGroupBox("Lựa chọn vật liệu & đặc tính")
        f_material = QFormLayout(g_material)
        f_material.addRow("Loại vật liệu:", cbo_material)
        f_material.addRow("Khối lượng riêng:", spn_density)
        print("✅ Material group created")
        
        print("Step 5: Add groups to layout...")
        v.addWidget(g_project)
        v.addWidget(g_material)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        print("✅ Layout completed")
        
        print("Step 6: Test final widget...")
        print(f"   Widget size: {widget.size()}")
        print(f"   Layout count: {main_layout.count()}")
        print("✅ Final widget OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("🚀 Starting UI Groups Test")
    print("=" * 60)
    
    success = True
    
    # Test InputsPanel với groups
    success &= test_inputs_panel_groups()
    
    # Test group functions individually
    success &= test_group_functions_individually()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Tất cả tests đều PASSED!")
        print("✅ UI groups có thể được tạo thành công")
        print("🔍 Vấn đề có thể nằm ở nơi khác")
    else:
        print("❌ Test failed")
        print("🔧 Cần kiểm tra lỗi cụ thể")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

