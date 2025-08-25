# ui/visualization_3d/__init__.py
# -*- coding: utf-8 -*-

"""
Module visualization 3D nâng cao cho băng tải
Tự động tạo mô hình 3D từ tham số tính toán
"""

from .core.model_generator import ConveyorModelGenerator
from .core.animation_engine import ConveyorAnimationEngine

__version__ = "1.0.0"
__all__ = [
    "ConveyorModelGenerator", 
    "ConveyorAnimationEngine"
]
