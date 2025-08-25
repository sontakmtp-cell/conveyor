#!/usr/bin/env python3
"""
Test script cho Giai đoạn 2: Thành phần cơ bản
"""

import sys
import os

# Thêm đường dẫn để import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'ui', 'visualization_3d'))

def test_belt_system_builder():
    """Test BeltSystemBuilder"""
    print("🧪 Testing BeltSystemBuilder...")
    
    try:
        from components.belt_system import BeltSystemBuilder
        
        # Test data
        test_data = {
            'geometry': {
                'width': 0.6,
                'length': 15.0,
                'thickness': 0.012,
                'trough_angle': 20
            },
            'material': {
                'type': 'EP'
            }
        }
        
        builder = BeltSystemBuilder(test_data)
        result = builder.build_complete_belt_system()
        
        print(f"✅ BeltSystemBuilder test passed")
        print(f"   - Belt width: {result['properties']['width_m']} m")
        print(f"   - Belt length: {result['properties']['length_m']} m")
        print(f"   - Belt type: {result['properties']['belt_type']}")
        
        return True
        
    except Exception as e:
        print(f"❌ BeltSystemBuilder test failed: {e}")
        return False

def test_drive_system_builder():
    """Test DriveSystemBuilder"""
    print("\n🧪 Testing DriveSystemBuilder...")
    
    try:
        from components.drive_system import DriveSystemBuilder
        
        # Test data
        test_data = {
            'motor': {
                'power_kw': 7.5,
                'rpm': 1450
            },
            'gearbox': {
                'ratio': 25.0,
                'efficiency': 0.95
            },
            'chain_drive': {
                'chain_type': '16B',
                'sprocket_teeth': {
                    'drive': 17,
                    'driven': 85
                },
                'chain_pitch_mm': 25.4
            },
            'belt_system': {
                'geometry': {
                    'width': 0.6
                }
            }
        }
        
        builder = DriveSystemBuilder(test_data)
        result = builder.build_complete_drive_system()
        
        print(f"✅ DriveSystemBuilder test passed")
        print(f"   - Motor power: {result['motor']['properties']['power_kw']} kW")
        print(f"   - Gearbox ratio: {result['gearbox']['properties']['ratio']}")
        print(f"   - Chain type: {result['chain_drive']['properties']['chain_type']}")
        
        return True
        
    except Exception as e:
        print(f"❌ DriveSystemBuilder test failed: {e}")
        return False

def test_support_structure_builder():
    """Test SupportStructureBuilder"""
    print("\n🧪 Testing SupportStructureBuilder...")
    
    try:
        from components.support_structure import SupportStructureBuilder
        
        # Test data
        test_data = {
            'carrying_idlers': {
                'count': 12,
                'spacing': 1.2,
                'diameter': 0.133,
                'trough_angle': 20
            },
            'return_idlers': {
                'count': 8,
                'spacing': 3.0,
                'diameter': 0.133
            },
            'belt_system': {
                'geometry': {
                    'length': 15.0,
                    'width': 0.6
                }
            }
        }
        
        builder = SupportStructureBuilder(test_data)
        result = builder.build_complete_support_structure()
        
        print(f"✅ SupportStructureBuilder test passed")
        print(f"   - Carrying idlers: {result['properties']['total_carrying_idlers']}")
        print(f"   - Return idlers: {result['properties']['total_return_idlers']}")
        print(f"   - Frame material: {result['properties']['frame_material']}")
        
        return True
        
    except Exception as e:
        print(f"❌ SupportStructureBuilder test failed: {e}")
        return False

def test_html_templates():
    """Test HTML templates"""
    print("\n🧪 Testing HTML templates...")
    
    try:
        from templates.html_templates import (
            ENHANCED_HTML_TEMPLATE, 
            SIMPLE_HTML_TEMPLATE, 
            ANALYSIS_HTML_TEMPLATE
        )
        
        # Test template loading
        assert len(ENHANCED_HTML_TEMPLATE) > 1000
        assert len(SIMPLE_HTML_TEMPLATE) > 500
        assert len(ANALYSIS_HTML_TEMPLATE) > 1000
        
        # Test template content
        assert "Băng tải 3D nâng cao" in ENHANCED_HTML_TEMPLATE
        assert "Băng tải 3D đơn giản" in SIMPLE_HTML_TEMPLATE
        assert "Phân tích băng tải 3D" in ANALYSIS_HTML_TEMPLATE
        
        print(f"✅ HTML templates test passed")
        print(f"   - Enhanced template: {len(ENHANCED_HTML_TEMPLATE)} chars")
        print(f"   - Simple template: {len(SIMPLE_HTML_TEMPLATE)} chars")
        print(f"   - Analysis template: {len(ANALYSIS_HTML_TEMPLATE)} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ HTML templates test failed: {e}")
        return False

def test_js_templates():
    """Test JavaScript templates"""
    print("\n🧪 Testing JavaScript templates...")
    
    try:
        from templates.js_templates import (
            ENHANCED_JS_TEMPLATE, 
            BASIC_JS_TEMPLATE, 
            SIMPLE_JS_TEMPLATE
        )
        
        # Test template loading
        assert len(ENHANCED_JS_TEMPLATE) > 500
        assert len(BASIC_JS_TEMPLATE) > 200
        assert len(SIMPLE_JS_TEMPLATE) > 200
        
        # Test template content
        assert "EnhancedConveyorVisualization" in ENHANCED_JS_TEMPLATE
        assert "BasicConveyorVisualization" in BASIC_JS_TEMPLATE
        assert "SimpleConveyorVisualization" in SIMPLE_JS_TEMPLATE
        
        print(f"✅ JavaScript templates test passed")
        print(f"   - Enhanced template: {len(ENHANCED_JS_TEMPLATE)} chars")
        print(f"   - Basic template: {len(BASIC_JS_TEMPLATE)} chars")
        print(f"   - Simple template: {len(SIMPLE_JS_TEMPLATE)} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ JavaScript templates test failed: {e}")
        return False

def test_enhanced_widget():
    """Test Enhanced Widget"""
    print("\n🧪 Testing Enhanced Widget...")
    
    try:
        from enhanced_widget import EnhancedVisualization3DWidget
        
        # Test widget creation
        widget = EnhancedVisualization3DWidget()
        
        # Test basic properties
        assert widget.visualization_mode == 'enhanced'
        assert hasattr(widget, 'model_generator')
        assert hasattr(widget, 'animation_engine')
        
        # Test UI components
        assert hasattr(widget, 'mode_combo')
        assert hasattr(widget, 'play_pause_btn')
        assert hasattr(widget, 'speed_slider')
        
        print(f"✅ Enhanced Widget test passed")
        print(f"   - Widget created successfully")
        print(f"   - Visualization mode: {widget.visualization_mode}")
        print(f"   - UI components initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Widget test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Bắt đầu kiểm thử Giai đoạn 2: Thành phần cơ bản")
    print("=" * 60)
    
    tests = [
        test_belt_system_builder,
        test_drive_system_builder,
        test_support_structure_builder,
        test_html_templates,
        test_js_templates,
        test_enhanced_widget
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Kết quả kiểm thử: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Tất cả tests đã pass! Giai đoạn 2 hoàn thành thành công!")
        return True
    else:
        print("⚠️ Một số tests đã fail. Cần kiểm tra lại.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
