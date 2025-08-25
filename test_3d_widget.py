#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để kiểm tra EnhancedVisualization3DWidget
"""

import sys
import os
from pathlib import Path

# Thêm đường dẫn để import
sys.path.insert(0, str(Path(__file__).parent))

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
    from PySide6.QtCore import Qt
    
    from ui.visualization_3d.enhanced_widget import EnhancedVisualization3DWidget
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Test Enhanced 3D Widget")
            self.setGeometry(100, 100, 1200, 800)
            
            # Widget chính
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Nút test
            test_btn = QPushButton("Test Widget 3D")
            test_btn.clicked.connect(self.test_widget)
            layout.addWidget(test_btn)
            
            # Widget 3D
            self.widget_3d = EnhancedVisualization3DWidget()
            layout.addWidget(self.widget_3d)
            
        def test_widget(self):
            print("Testing 3D Widget...")
            print(f"Widget type: {type(self.widget_3d)}")
            print(f"Has update_enhanced_visualization: {hasattr(self.widget_3d, 'update_enhanced_visualization')}")
            
            # Test với dữ liệu mẫu
            try:
                from core.models import ConveyorParameters, CalculationResult
                
                # Tạo params mẫu
                params = ConveyorParameters(
                    L_m=50.0,
                    B_mm=800,
                    Q_tph=200.0,
                    H_m=10.0,
                    material_type="Than đá",
                    belt_type="fabric_ep",
                    trough_angle_label="35°",
                    motor_rpm=1450,
                    motor_efficiency=0.9,
                    gearbox_efficiency=0.95
                )
                
                # Tạo result mẫu
                result = CalculationResult(
                    belt_speed_mps=2.5,
                    motor_power_kw=15.5,
                    safety_factor=8.2,
                    belt_strength_utilization=75.5,
                    cost_capital_total=45000.0
                )
                
                print("Testing update_enhanced_visualization...")
                self.widget_3d.update_enhanced_visualization(params, result)
                print("✅ Test thành công!")
                
            except Exception as e:
                print(f"❌ Test thất bại: {e}")
                import traceback
                traceback.print_exc()
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = TestWindow()
        window.show()
        sys.exit(app.exec())
        
except ImportError as e:
    print(f"❌ Không thể import: {e}")
    print("Hãy đảm bảo đã cài đặt PySide6 và các dependencies cần thiết")
except Exception as e:
    print(f"❌ Lỗi khác: {e}")
    import traceback
    traceback.print_exc()
