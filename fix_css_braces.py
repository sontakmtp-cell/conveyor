#!/usr/bin/env python3
"""
Script để sửa tất cả các dấu ngoặc nhọn trong CSS templates
"""

import re

def fix_css_braces(file_path):
    """Sửa tất cả các dấu ngoặc nhọn trong CSS"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tìm và thay thế tất cả các CSS rules
    # Pattern: selector { ... }
    pattern = r'(\s*[.#]?\w+(?:[.#]\w+)*\s*)\{([^}]*)\}'
    
    def replace_braces(match):
        selector = match.group(1)
        rules = match.group(2)
        return selector + "{{" + rules + "}}"
    
    # Thay thế tất cả các CSS rules
    content = re.sub(pattern, replace_braces, content)
    
    # Ghi lại file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Đã sửa CSS braces trong {file_path}")

if __name__ == "__main__":
    file_path = "ui/visualization_3d/templates/html_templates.py"
    fix_css_braces(file_path)
