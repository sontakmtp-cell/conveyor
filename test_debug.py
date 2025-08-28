#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script debug để kiểm tra từng bước
"""
import sys
import traceback

def test_imports():
    print("=== Testing imports ===")
    
    try:
        print("1. Importing PySide6...")
        from PySide6.QtWidgets import QApplication
        print("   ✓ PySide6 imported successfully")
    except Exception as e:
        print(f"   ✗ PySide6 import failed: {e}")
        return False
    
    try:
        print("2. Importing InputsPanel...")
        from ui.ui_components_3d_enhanced import InputsPanel
        print("   ✓ InputsPanel imported successfully")
    except Exception as e:
        print(f"   ✗ InputsPanel import failed: {e}")
        return False
    
    try:
        print("3. Importing ConveyorParameters...")
        from core.models import ConveyorParameters
        print("   ✓ ConveyorParameters imported successfully")
    except Exception as e:
        print(f"   ✗ ConveyorParameters import failed: {e}")
        return False
    
    try:
        print("4. Importing Enhanced3DConveyorWindow...")
        from ui.main_window_3d_enhanced import Enhanced3DConveyorWindow
        print("   ✓ Enhanced3DConveyorWindow imported successfully")
    except Exception as e:
        print(f"   ✗ Enhanced3DConveyorWindow import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_main_window_creation():
    print("\n=== Testing main window creation ===")
    
    try:
        print("1. Creating QApplication...")
        from PySide6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        print("   ✓ QApplication created successfully")
        
        print("2. Creating Enhanced3DConveyorWindow...")
        from ui.main_window_3d_enhanced import Enhanced3DConveyorWindow
        main_window = Enhanced3DConveyorWindow()
        print("   ✓ Enhanced3DConveyorWindow created successfully")
        
        print("3. Calling show() method...")
        main_window.show()
        print("   ✓ show() method called successfully")
        
        print("4. Main window is visible:", main_window.isVisible())
        print("5. Main window geometry:", main_window.geometry())
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        traceback.print_exc()
        return False

def main():
    print("Starting debug test...")
    
    if not test_imports():
        print("Import test failed!")
        return 1
    
    if not test_main_window_creation():
        print("Main window creation test failed!")
        return 1
    
    print("\n=== All tests passed! ===")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
