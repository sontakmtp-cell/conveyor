#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test đơn giản
"""
import sys
import traceback

def test_step_by_step():
    print("=== Testing step by step ===")
    
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
        
        print("Step 4: Create Enhanced3DConveyorWindow")
        main_window = Enhanced3DConveyorWindow()
        print("   ✓ Enhanced3DConveyorWindow created")
        
        print("Step 5: Call show()")
        main_window.show()
        print("   ✓ show() called")
        
        print("Step 6: Check visibility")
        print(f"   Main window visible: {main_window.isVisible()}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error at step: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_step_by_step()
    if success:
        print("\n=== All steps completed successfully! ===")
    else:
        print("\n=== Test failed! ===")
        sys.exit(1)
