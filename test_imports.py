#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test import từng module
"""
import sys
import traceback

def test_import(module_name, import_statement):
    try:
        print(f"Testing import: {module_name}")
        exec(import_statement)
        print(f"   ✓ {module_name} imported successfully")
        return True
    except Exception as e:
        print(f"   ✗ {module_name} import failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("=== Testing module imports ===")
    
    imports_to_test = [
        ("PySide6.QtWidgets", "from PySide6.QtWidgets import QApplication"),
        ("ui.ui_components_3d_enhanced", "from ui.ui_components_3d_enhanced import InputsPanel"),
        ("core.models", "from core.models import ConveyorParameters"),
        ("ui.main_window_3d_enhanced", "from ui.main_window_3d_enhanced import Enhanced3DConveyorWindow"),
    ]
    
    success_count = 0
    for module_name, import_statement in imports_to_test:
        if test_import(module_name, import_statement):
            success_count += 1
        print()
    
    print(f"=== Results: {success_count}/{len(imports_to_test)} imports successful ===")
    
    if success_count == len(imports_to_test):
        print("All imports successful!")
        return 0
    else:
        print("Some imports failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
