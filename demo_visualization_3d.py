#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script để kiểm tra module visualization 3D trong ứng dụng chính
"""

import sys
import os
from pathlib import Path

# Thêm đường dẫn để import các module
sys.path.insert(0, str(Path(__file__).parent))

def demo_visualization_3d():
    """Demo module visualization 3D"""
    print("🚀 Demo Module Visualization 3D")
    print("=" * 50)
    
    try:
        # Import module chính
        from ui.visualization_3d.enhanced_widget import EnhancedVisualization3DWidget
        print("✅ Module visualization 3D imported successfully")
        
        # Tạo dữ liệu mẫu
        sample_params = {
            'belt_length_m': 15.0,
            'belt_width_m': 0.8,
            'conveyor_speed_ms': 1.5,
            'material_density_kgm3': 1600,
            'lift_height_m': 3.0,
            'friction_coefficient': 0.35
        }
        
        sample_result = {
            'belt_tension_n': 2500,
            'motor_power_kw': 5.5,
            'drum_diameter_mm': 500,
            'idler_spacing_m': 1.2,
            'total_mass_kg': 12000
        }
        
        print("📊 Sample data created:")
        print(f"   - Belt length: {sample_params['belt_length_m']} m")
        print(f"   - Belt width: {sample_params['belt_width_m']} m")
        print(f"   - Conveyor speed: {sample_params['conveyor_speed_ms']} m/s")
        print(f"   - Material density: {sample_params['material_density_kgm3']} kg/m³")
        
        # Tạo QApplication
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Tạo widget visualization 3D
        print("\n🏗️ Creating EnhancedVisualization3DWidget...")
        viz_widget = EnhancedVisualization3DWidget()
        print("✅ Widget created successfully")
        
        # Kiểm tra các method
        print("\n🔍 Checking widget methods...")
        methods_to_check = [
            'update_enhanced_visualization',
            'get_visualization_data',
            'setHtml',
            'setLayout'
        ]
        
        for method in methods_to_check:
            if hasattr(viz_widget, method):
                print(f"   ✅ {method} method exists")
            else:
                print(f"   ⚠️ {method} method missing")
        
        # Test cập nhật visualization
        print("\n🔄 Testing visualization update...")
        try:
            viz_widget.update_enhanced_visualization(sample_params, sample_result)
            print("✅ Visualization updated successfully")
        except Exception as e:
            print(f"⚠️ Visualization update failed: {e}")
        
        # Test lấy dữ liệu visualization
        print("\n📊 Testing data retrieval...")
        try:
            viz_data = viz_widget.get_visualization_data()
            print(f"✅ Visualization data retrieved: {len(viz_data)} items")
            for key, value in viz_data.items():
                print(f"   - {key}: {value}")
        except Exception as e:
            print(f"⚠️ Data retrieval failed: {e}")
        
        # Test hiển thị HTML mặc định
        print("\n🌐 Testing HTML display...")
        try:
            if hasattr(viz_widget, 'setHtml'):
                default_html = """
                <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                    <h1>🏗️ Demo Mô hình 3D Băng tải</h1>
                    <p>Module visualization 3D đã hoạt động thành công!</p>
                    <div style="background: rgba(255,255,255,0.2); border-radius: 15px; padding: 25px; margin: 20px;">
                        <h3>📊 Dữ liệu mẫu:</h3>
                        <ul style="text-align: left;">
                            <li>Chiều dài băng tải: 15.0 m</li>
                            <li>Bề rộng băng tải: 0.8 m</li>
                            <li>Tốc độ: 1.5 m/s</li>
                            <li>Mật độ vật liệu: 1600 kg/m³</li>
                        </ul>
                    </div>
                </body>
                </html>
                """
                viz_widget.setHtml(default_html)
                print("✅ HTML content displayed successfully")
            else:
                print("⚠️ Widget không hỗ trợ setHtml")
        except Exception as e:
            print(f"⚠️ HTML display failed: {e}")
        
        # Hiển thị widget
        print("\n🖥️ Displaying widget...")
        viz_widget.resize(800, 600)
        viz_widget.show()
        
        print("\n🎉 Demo completed successfully!")
        print("Widget đang hiển thị. Đóng cửa sổ để kết thúc demo.")
        
        # Chạy event loop
        return app.exec()
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("Hãy kiểm tra cài đặt dependencies:")
        print("pip install PySide6 PySide6-WebEngine")
        return 1
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Main function"""
    print("🚀 Starting Visualization 3D Demo...")
    print("=" * 50)
    
    try:
        exit_code = demo_visualization_3d()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
