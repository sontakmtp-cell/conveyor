#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script debug đơn giản để kiểm tra từng phần của InputsPanel
"""

import sys
import os
import traceback
from pathlib import Path

# Thêm đường dẫn hiện tại vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_inputs_panel_step_by_step():
    """Test tạo InputsPanel từng bước một"""
    print("🧪 Testing InputsPanel step by step...")
    
    try:
        from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QGroupBox, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QCheckBox, QScrollArea
        from PySide6.QtSvgWidgets import QSvgWidget
        
        # Tạo QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            print("✅ QApplication created")
        else:
            print("✅ QApplication already exists")
        
        print("Step 1: Create basic widget...")
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        print("✅ Basic widget created")
        
        print("Step 2: Create scroll area...")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        v = QVBoxLayout(container)
        print("✅ Scroll area created")
        
        print("Step 3: Create form widgets...")
        # Project
        edt_project_name = QLineEdit("Thiết kế băng tải nhà máy ABC")
        edt_designer = QLineEdit("Kỹ sư thiết kế")
        edt_client = QLineEdit("Khách hàng")
        edt_location = QLineEdit("Công trình")
        print("✅ Form widgets created")
        
        print("Step 4: Create project group...")
        g = QGroupBox("Thông tin dự án")
        f = QFormLayout(g)
        f.addRow("Tên dự án:", edt_project_name)
        f.addRow("Người thiết kế:", edt_designer)
        f.addRow("Khách hàng:", edt_client)
        f.addRow("Công trình:", edt_location)
        print("✅ Project group created")
        
        print("Step 5: Add to layout...")
        v.addWidget(g)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        print("✅ Layout completed")
        
        print("Step 6: Test window properties...")
        print(f"   Widget size: {widget.size()}")
        print(f"   Layout count: {main_layout.count()}")
        print("✅ Window properties OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed at step: {e}")
        traceback.print_exc()
        return False

def test_import_issues():
    """Test các import có thể gây vấn đề"""
    print("\n🔍 Testing potential import issues...")
    
    try:
        print("1. Testing core.specs import...")
        from core.specs import ACTIVE_BELT_SPECS, STANDARD_WIDTHS
        print("✅ core.specs imports OK")
        
        print("2. Testing core.db import...")
        from core.db import load_database
        print("✅ core.db import OK")
        
        print("3. Testing core.thread_worker import...")
        from core.thread_worker import CalculationThread
        print("✅ core.thread_worker import OK")
        
        print("4. Testing core.optimizer_worker import...")
        from core.optimizer_worker import OptimizerWorker
        print("✅ core.optimizer_worker import OK")
        
        print("5. Testing reports imports...")
        from reports.exporter_pdf import export_pdf_report
        from reports.exporter_excel import export_excel_report
        print("✅ reports imports OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Import issue found: {e}")
        traceback.print_exc()
        return False

def main():
    print("🚀 Starting UI Debug Simple Test")
    print("=" * 60)
    
    success = True
    
    # Test InputsPanel step by step
    success &= test_inputs_panel_step_by_step()
    
    # Test import issues
    success &= test_import_issues()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Tất cả tests đều PASSED!")
        print("✅ UI components có thể được tạo thành công")
        print("🔍 Vấn đề có thể nằm ở nơi khác")
    else:
        print("❌ Test failed")
        print("🔧 Cần kiểm tra lỗi cụ thể")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

