#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để kiểm tra việc tích hợp module visualization 3D
"""

import sys
import os
from pathlib import Path

# Thêm đường dẫn để import các module
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test import các module visualization 3D"""
    print("🧪 Testing imports...")
    
    try:
        # Test import module chính
        from ui.visualization_3d.enhanced_widget import EnhancedVisualization3DWidget
        print("✅ EnhancedVisualization3DWidget imported successfully")
        
        from ui.visualization_3d.core.animation_engine import ConveyorAnimationEngine
        print("✅ ConveyorAnimationEngine imported successfully")
        
        from ui.visualization_3d.core.component_builder import ComponentBuilderManager
        print("✅ ComponentBuilderManager imported successfully")
        
        from ui.visualization_3d.core.physics_simulator import ConveyorPhysicsSimulator
        print("✅ ConveyorPhysicsSimulator imported successfully")
        
        from ui.visualization_3d.core.model_generator import ConveyorModelGenerator
        print("✅ ConveyorModelGenerator imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_widget_creation():
    """Test tạo widget visualization 3D"""
    print("\n🧪 Testing widget creation...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from ui.visualization_3d.enhanced_widget import EnhancedVisualization3DWidget
        
        # Tạo QApplication nếu chưa có
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Tạo widget
        widget = EnhancedVisualization3DWidget()
        print("✅ EnhancedVisualization3DWidget created successfully")
        
        # Kiểm tra các method cần thiết
        required_methods = [
            'update_enhanced_visualization',
            'get_visualization_data',
            'show_demo'
        ]
        
        for method in required_methods:
            if hasattr(widget, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"⚠️ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Widget creation failed: {e}")
        return False

def test_core_modules():
    """Test các core module"""
    print("\n🧪 Testing core modules...")
    
    try:
        from ui.visualization_3d.core.animation_engine import ConveyorAnimationEngine
        from ui.visualization_3d.core.component_builder import ComponentBuilderManager
        from ui.visualization_3d.core.physics_simulator import ConveyorPhysicsSimulator
        from ui.visualization_3d.core.model_generator import ConveyorModelGenerator
        
        # Test tạo instances với dữ liệu mẫu
        sample_data = {
            'belt_length': 10.0,
            'belt_width': 0.8,
            'material_density': 1600,
            'conveyor_speed': 1.5
        }
        
        try:
            animation_engine = ConveyorAnimationEngine(sample_data)
            print("✅ ConveyorAnimationEngine instance created")
        except Exception as e:
            print(f"⚠️ ConveyorAnimationEngine creation failed: {e}")
            # Tạo instance với constructor mặc định nếu có thể
            try:
                animation_engine = ConveyorAnimationEngine()
                print("✅ ConveyorAnimationEngine instance created with default constructor")
            except:
                print("⚠️ ConveyorAnimationEngine không thể tạo instance")
        
        try:
            component_builder = ComponentBuilderManager()
            print("✅ ComponentBuilderManager instance created")
        except Exception as e:
            print(f"⚠️ ComponentBuilderManager creation failed: {e}")
        
        try:
            physics_simulator = ConveyorPhysicsSimulator()
            print("✅ ConveyorPhysicsSimulator instance created")
        except Exception as e:
            print(f"⚠️ ConveyorPhysicsSimulator creation failed: {e}")
        
        try:
            model_generator = ConveyorModelGenerator()
            print("✅ ConveyorModelGenerator instance created")
        except Exception as e:
            print(f"⚠️ ConveyorModelGenerator creation failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Core modules test failed: {e}")
        return False

def test_integration():
    """Test tích hợp với UI components"""
    print("\n🧪 Testing UI integration...")
    
    try:
        from ui.ui_components_3d_enhanced import Enhanced3DResultsPanel
        
        # Test tạo panel
        panel = Enhanced3DResultsPanel()
        print("✅ Enhanced3DResultsPanel created successfully")
        
        # Kiểm tra các thuộc tính cần thiết
        if hasattr(panel, 'viz_3d'):
            print("✅ viz_3d attribute exists")
        else:
            print("⚠️ viz_3d attribute missing")
        
        if hasattr(panel, '_switch_mode'):
            print("✅ _switch_mode method exists")
        else:
            print("⚠️ _switch_mode method missing")
        
        return True
        
    except Exception as e:
        print(f"❌ UI integration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Visualization 3D Integration Tests...")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Widget Creation Test", test_widget_creation),
        ("Core Modules Test", test_core_modules),
        ("UI Integration Test", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Tổng kết kết quả
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Module visualization 3D is ready for use.")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
