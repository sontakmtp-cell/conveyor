#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test tạo instance
"""
import sys
import traceback

def test_instance_creation():
    print("=== Testing instance creation ===")
    
    try:
        print("Step 1: Import QApplication")
        from PySide6.QtWidgets import QApplication
        print("   ✓ QApplication imported")
        
        print("Step 2: Create QApplication")
        app = QApplication(sys.argv)
        print("   ✓ QApplication created")
        
        print("Step 3: Import Enhanced3DConveyorWindow")
        from ui.main_window_3d_enhanced import Enhanced3DConveyorWindow
        print("   ✓ Enhanced3DConveyorWindow imported")
        
        print("Step 4: Create instance")
        print("   Creating Enhanced3DConveyorWindow()...")
        main_window = Enhanced3DConveyorWindow()
        print("   ✓ Instance created successfully")
        
        print("Step 5: Check instance attributes")
        print(f"   Window title: {main_window.windowTitle()}")
        print(f"   Window size: {main_window.size()}")
        print(f"   Is visible: {main_window.isVisible()}")
        
        print("Step 6: Call show()")
        main_window.show()
        print("   ✓ show() called successfully")
        
        print("Step 7: Check visibility after show")
        print(f"   Is visible after show: {main_window.isVisible()}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_instance_creation()
    if success:
        print("\n=== Instance creation test completed successfully! ===")
    else:
        print("\n=== Instance creation test failed! ===")
        sys.exit(1)
